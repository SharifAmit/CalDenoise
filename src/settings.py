import os
class Settings:

  def __new__(cls):

    cls.DEFAULT_OUTPUT_DIR_NAME = 'output'
    cls.PROCESSING_DIR_NAME ='img_process'

    if not hasattr(cls, 'instance'):
      cls.instance = super(Settings, cls).__new__(cls)
    return cls.instance

  def output_suffix(self):
    return f'LM{self.large_median}_SM{self.small_median}_enh{self.enhance}_SOL{self.SOL}_TSOL{self.threshold_SOL}_gradfilter{self.gradient_filter}'

  def process_output_dir(self):
    return f'{self.outout_dir}/{self.PROCESSING_DIR_NAME}_{self.output_suffix()}/'

  def init(self, dir, large_median, small_median, enhance, SOL, threshold_SOL, gradient_filter, plot_signals, interm, median_w_SOL, print_exec_time):
    self.dir=dir
    if(os.path.isfile(dir)):
      self.dir = os.path.dirname(dir)
    self.outout_dir = f'{self.dir}/{self.DEFAULT_OUTPUT_DIR_NAME}/'
    self.large_median = large_median
    self.small_median = small_median
    self.enhance = enhance
    self.SOL = SOL
    self.threshold_SOL = threshold_SOL
    self.gradient_filter = gradient_filter
    self.plot_signals = plot_signals
    self.interm = interm
    self.median_w_SOL = median_w_SOL
    self.print_exec_time = print_exec_time


