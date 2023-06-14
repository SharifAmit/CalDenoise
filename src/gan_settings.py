import os

from src.methods import Methods


class GanSettings:

  def __new__(cls):
    cls.DEFAULT_OUTPUT_DIR_NAME = 'output'
    cls.GAN_PROCESSING_DIR_NAME = 'gan'
    cls.SM4_PROCESSING_DIR_NAME = '4sm'
    cls.SEG_PROCESSING_DIR_NAME = 'seg'

    if not hasattr(cls, 'instance'):
      cls.instance = super(GanSettings, cls).__new__(cls)
    return cls.instance

  def output_suffix(self):
    return f'stride{self.stride}_crop{self.crop_size}_tresh{self.thresh}_alpha{self.alpha}_type{self.type}_method{self.method}'

  def process_output_dir(self):
    if (self.method ==Methods.METHOD_GAN_IMG_PROC.value):
        return f'{self.outout_dir}/{self.GAN_PROCESSING_DIR_NAME}_{self.output_suffix()}/'

    if (self.method ==Methods.METHOD_GAN_4SM.value):
      return f'{self.outout_dir}/{self.SM4_PROCESSING_DIR_NAME}_{self.output_suffix()}/'

    if (self.method ==Methods.METHOD_GAN_SEGMENTATION.value):
      return f'{self.outout_dir}/{self.SEG_PROCESSING_DIR_NAME}_{self.output_suffix()}/'


  def init(self, dir, stride, crop_size, thresh, alpha, type, method):
    self.dir = dir
    if (os.path.isfile(dir)):
      self.dir = os.path.dirname(dir)
    self.outout_dir = f'{self.dir}/{self.DEFAULT_OUTPUT_DIR_NAME}/'
    self.stride = stride
    self.crop_size = crop_size
    self.thresh = thresh
    self.alpha = alpha
    self.type = type
    self.method = method
