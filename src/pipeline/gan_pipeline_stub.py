import ntpath
import os
import warnings
from src import utils
from src.gan_settings import GanSettings
from src.methods import Methods

warnings.filterwarnings("ignore")



def load_models(method):

  settings = GanSettings()
  cell_type = settings.type

  if method==Methods.METHOD_GAN_IMG_PROC.value and cell_type=='rhythmic':
    print('A')

  if method==Methods.METHOD_GAN_IMG_PROC.value and cell_type=='stochastic':
    print('B')

  if method==Methods.METHOD_GAN_4SM.value and cell_type=='rhythmic':
    print('C')

  if method==Methods.METHOD_GAN_4SM.value and cell_type=='stochastic':
    print('D')

  if method==Methods.METHOD_GAN_SEGMENTATION.value and cell_type=='rhythmic':
    print('E')

  if method==Methods.METHOD_GAN_SEGMENTATION.value and cell_type=='stochastic':
    print('F')

  return ['A','B']




def process(image_path, image_name, output_dir, stride, crop_size, thresh,
    alpha, g_local_model, g_global_model):
  print(
    f'{image_path}{image_name}{output_dir}, {stride},{crop_size}{thresh}{alpha}')
  # utils.save_image(im_np_img, output_dir + 'denoised/', img_name, 'png')
  return 0


def gan_process_single_image(image_filepath, local_model, global_model):
  settings = GanSettings()
  print(settings.process_output_dir())
  file = 'weight_file/4sm/rhythmic/global_model_000034.h5'

  #
  # process(image_filepath, img_name, settings.process_output_dir(),
  #         settings.stride,
  #         settings.crop_size, settings.thresh, settings.alpha, local_model,
  #         global_model)
