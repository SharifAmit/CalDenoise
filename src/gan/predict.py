'''
4SM/model.py Copyright (C) 2021 Sharif Amit Kamran, Hussein Moghnieh

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
'''

import os
import warnings

import cv2
import numpy as np
import tensorflow as tf
from PIL import Image
from src.gan.model import fine_generator, coarse_generator

from src import utils

warnings.filterwarnings('ignore')


import keras.backend.tensorflow_backend as tb
tb._SYMBOLIC_SCOPE.value = True

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
  try:
    # Currently, memory growth needs to be the same across GPUs
    for gpu in gpus:
      tf.config.experimental.set_memory_growth(gpu, True)
    logical_gpus = tf.config.experimental.list_logical_devices('GPU')
    print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
  except RuntimeError as e:
    # Memory growth must be set before GPUs have been initialized
    print(e)

dirname = os.path.dirname(__file__)

def normalize_pred(img, g_global_model, g_local_model):
  img = np.reshape(img, [1, 64, 64, 1])
  img_coarse = tf.image.resize(img, (32, 32),
                               method=tf.image.ResizeMethod.LANCZOS3)
  img_coarse = (img_coarse - 127.5) / 127.5
  img_coarse = np.array(img_coarse)

  X_fakeB_coarse, x_global = g_global_model.predict(img_coarse)
  X_fakeB_coarse = (X_fakeB_coarse + 1) / 2.0
  pred_img_coarse = X_fakeB_coarse[:, :, :, 0]

  img = (img - 127.5) / 127.5
  X_fakeB = g_local_model.predict([img, x_global])
  X_fakeB = (X_fakeB + 1) / 2.0
  pred_img = X_fakeB[:, :, :, 0]
  return [np.asarray(pred_img, dtype=np.float32),
          np.asarray(pred_img_coarse, dtype=np.float32)]


def strided_crop(img, img_h, img_w, height, width, g_global_model,
    g_local_model, stride=1):

  print(height)
  print(width)
  full_prob = np.zeros((img_h, img_w), dtype=np.float32)
  full_sum = np.ones((img_h, img_w), dtype=np.float32)

  max_x = int(((img.shape[0] - height) / stride) + 1)
  max_y = int(((img.shape[1] - width) / stride) + 1)
  max_crops = (max_x) * (max_y)
  i = 0
  for h in range(max_x):
    for w in range(max_y):
      crop_img_arr = img[h * stride:(h * stride) + height,
                     w * stride:(w * stride) + width]
      print(crop_img_arr.shape)
      [pred, pred_256] = normalize_pred(crop_img_arr, g_global_model,
                                        g_local_model)
      full_prob[h * stride:(h * stride) + height,
      w * stride:(w * stride) + width] += pred[0]
      full_sum[h * stride:(h * stride) + height,
      w * stride:(w * stride) + width] += 1
      i = i + 1
      # print(i)
  out_img = full_prob / full_sum
  return out_img


def threshold(img, thresh):
  binary_map = (img > thresh).astype(np.uint8)
  binary_map[binary_map == 1] = 255
  return binary_map


def overlay(img, mask, alpha=0.7):
  overlay = np.zeros((mask.shape[0], mask.shape[1], 3))
  overlay[mask == 255] = 255
  overlay[:, :, 1] = 0
  overlay[:, :, 2] = 0
  image = np.zeros((img.shape[0], img.shape[1], 3))
  image[:, :, 0] = img
  image[:, :, 1] = img
  image[:, :, 2] = img
  overlay = overlay.astype(np.uint8)
  image = image.astype(np.uint8)
  print(image.shape, overlay.shape)
  print(type(image), type(overlay))
  overlay_bgr = cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR)
  dst = cv2.addWeighted(image, alpha, overlay_bgr, 1 - alpha, 0)
  dst = cv2.cvtColor(dst, cv2.COLOR_BGR2RGB)
  return dst


def load_local_model(weight_name, opt):
  img_shape = (64, 64, 1)
  label_shape = (64, 64, 1)
  x_global = (32, 32, 64)

  weight_files_dir = os.path.join(dirname, 'weight_file/')
  local_weight_filename = weight_files_dir + 'local_model_' + weight_name + '.h5';

  g_local_model = fine_generator(x_global, img_shape)
  g_local_model.load_weights(local_weight_filename)
  g_local_model.compile(loss='mse', optimizer=opt)

  return g_local_model


def load_global_model(weight_name, opt):
  img_shape_g = (32, 32, 1)
  weight_files_dir = os.path.join(dirname, 'weight_file/')
  global_weight_filename = weight_files_dir + 'global_model_' + weight_name + '.h5';
  g_global_model = coarse_generator(img_shape_g, n_downsampling=2, n_blocks=9,
                                    n_channels=1)
  g_global_model.load_weights(global_weight_filename)
  g_global_model.compile(loss='mse', optimizer=opt)

  return g_global_model


def process(image_path, img_name, output_dir, stride, crop_size, thresh, alpha, g_local_model, g_global_model):

  crop_size_h = crop_size
  crop_size_w = crop_size

  img = Image.open(image_path)
  img_arr = np.asarray(img, dtype=np.float32)
  img_arr = img_arr[:, :, 0]
  print(img_arr.shape)
  out_img = strided_crop(img_arr, img_arr.shape[0], img_arr.shape[1],
                         crop_size_h, crop_size_w, g_global_model,
                         g_local_model, stride)
  out_img_sv = out_img.copy()
  out_img_sv = ((out_img_sv) * 255.0).astype('uint8')

  out_img_sv = out_img_sv.astype(np.uint8)
  out_im = Image.fromarray(out_img_sv)

  utils.save_image(out_im, output_dir + 'denoised/', img_name, 'png')


  out_img_thresh = out_img_sv.copy()
  thresh_img = threshold(out_img_thresh, thresh)
  thresh_im = Image.fromarray(thresh_img)
  utils.save_image(thresh_im, output_dir + 'threshold/', img_name, 'png')

  cc_img = thresh_img.copy()

  ovleray_img = overlay(img_arr.copy(), thresh_img.copy(), alpha)
  ovleray_im = Image.fromarray(ovleray_img)
  utils.save_image(ovleray_im, output_dir + 'overlay/', img_name, 'png')

