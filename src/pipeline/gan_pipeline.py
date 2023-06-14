import ntpath

from keras.optimizers import Adam
import keras.backend as K
import gc
import warnings

from src.gan import predict

warnings.filterwarnings('ignore')

from src.gan.model import fine_generator, coarse_generator
from src.gan_settings import GanSettings
from src.methods import Methods

warnings.filterwarnings("ignore")

import keras.backend.tensorflow_backend as tb
tb._SYMBOLIC_SCOPE.value = True

def load_models(method):

  settings = GanSettings()
  cell_type = settings.type
  weight_name = 'todo'
  K.clear_session()
  gc.collect()

  img_shape = (64,64,1)
  label_shape = (64,64,1)
  x_global = (32,32,64)
  opt = Adam()

  if method==Methods.METHOD_GAN_IMG_PROC.value and cell_type=='rhythmic':
    local_model_file = 'weight_file/img_proc/rhythmic/local_model_000037.h5'
    global_model_file = 'weight_file/img_proc/rhythmic/global_model_000037.h5'

  if method==Methods.METHOD_GAN_IMG_PROC.value and cell_type=='stochastic':
    local_model_file = 'weight_file/img_proc/stochastic/local_model_000090.h5'
    global_model_file = 'weight_file/img_proc/stochastic/global_model_000090.h5'


  if method==Methods.METHOD_GAN_4SM.value and cell_type=='rhythmic':
    local_model_file = 'weight_file/4sm/rhythmic/local_model_000034.h5'
    global_model_file = 'weight_file/4sm/rhythmic/global_model_000034.h5'

  if method==Methods.METHOD_GAN_4SM.value and cell_type=='stochastic':
    local_model_file = 'weight_file/4sm/stochastic/local_model_000001.h5'
    global_model_file = 'weight_file/4sm/stochastic/global_model_000001.h5'

  if method==Methods.METHOD_GAN_SEGMENTATION.value and cell_type=='rhythmic':
    local_model_file = 'weight_file/seg/rhythmic/local_model_000025.h5'
    global_model_file = 'weight_file/seg/rhythmic/global_model_000025.h5'

  if method==Methods.METHOD_GAN_SEGMENTATION.value and cell_type=='stochastic':
    local_model_file = 'weight_file/seg/stochastic/local_model_000071.h5'
    global_model_file = 'weight_file/seg/stochastic/global_model_000071.h5'

  g_local_model = fine_generator(x_global,img_shape)
  g_local_model.load_weights(local_model_file)
  g_local_model.compile(loss='mse', optimizer=opt)

  img_shape_g = (32,32,1)
  g_global_model = coarse_generator(img_shape_g,n_downsampling=2, n_blocks=6, n_channels=1)
  g_global_model.load_weights(global_model_file)
  g_global_model.compile(loss='mse',optimizer=opt)

  return [g_local_model, g_global_model]

def gan_process_single_image(image_filepath, local_model, global_model):
  settings = GanSettings()
  img_name = ntpath.basename(image_filepath)

  predict.process(image_filepath, img_name, settings.process_output_dir(),
          settings.stride, settings.crop_size, settings.thresh, settings.alpha, local_model,
          global_model)