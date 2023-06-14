from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QHBoxLayout, QSpinBox, \
  QCheckBox, QComboBox, QPushButton

from src.settings import Settings


class ImagePipelineSettingsDialog(QDialog):

  def __init__(self, parent=None,apply_flag=False,process=False,progress_bar=None):
    super().__init__(parent)
    self.grid_layout = QGridLayout()
    self.progress_bar=progress_bar
    self.process=process
    self.apply_flag = apply_flag
    self.setLayout(self.grid_layout)
    self.setWindowTitle("Image Processing")
    self.label_2 = QLabel("Image Processing")
    self.label_2.setFont(QFont('Times', 10))
    self.grid_layout.addWidget(self.label_2, 1, 0)

    self.hbox_large_median = QHBoxLayout()
    self.Label_large_median = QLabel("Large Median")
    self.QSpinBox_large_median = QSpinBox()
    self.QSpinBox_large_median.setMinimum(1)
    self.QSpinBox_large_median.setMaximum(100)
    self.QSpinBox_large_median.setValue(self.parent().large_median)
    self.grid_layout.addWidget(self.Label_large_median, 2, 0)
    self.grid_layout.addWidget(self.QSpinBox_large_median,2, 1)

    self.hbox_small_median = QHBoxLayout()
    self.Label_small_median = QLabel("Small Median")
    self.QSpinBox_small_median = QSpinBox()
    self.QSpinBox_small_median.setMinimum(1)
    self.QSpinBox_small_median.setMaximum(100)
    self.QSpinBox_small_median.setValue(self.parent().small_median)
    self.grid_layout.addWidget(self.Label_small_median, 3, 0)
    self.grid_layout.addWidget(self.QSpinBox_small_median, 3, 1)

    self.hbox_enhance = QHBoxLayout()
    self.Label_enhance = QLabel("Enhance")
    self.QSpinBox_enhance = QSpinBox()
    self.QSpinBox_enhance.setMinimum(1)
    self.QSpinBox_enhance.setMaximum(100)
    self.QSpinBox_enhance.setValue(self.parent().enhance)
    self.grid_layout.addWidget(self.Label_enhance, 4, 0)
    self.grid_layout.addWidget(self.QSpinBox_enhance, 4, 1)

    self.hbox_SOL = QHBoxLayout()
    self.Label_SOL = QLabel("SOL")
    self.QSpinBox_SOL = QCheckBox()
    self.QSpinBox_SOL.setChecked(self.parent().SOL)
    self.grid_layout.addWidget(self.Label_SOL, 5, 0)
    self.grid_layout.addWidget(self.QSpinBox_SOL, 5, 1)

    self.hbox_threshold_SOL = QHBoxLayout()
    self.Label_threshold_SOL = QLabel("Threshold SOL")
    self.QSpinBox_threshold_SOL = QSpinBox()
    self.QSpinBox_threshold_SOL.setMinimum(1)
    self.QSpinBox_threshold_SOL.setMaximum(100)
    self.QSpinBox_threshold_SOL.setValue(self.parent().threshold_SOL)
    self.grid_layout.addWidget(self.Label_threshold_SOL, 6, 0)
    self.grid_layout.addWidget(self.QSpinBox_threshold_SOL, 6, 1)

    self.hbox_gradient_filter = QHBoxLayout()
    self.Label_gradient_filter = QLabel("Gradient Filter")
    self.QComboBox_gradient_filter = QComboBox()
    self.QComboBox_gradient_filter.addItems([self.parent().gradient_filter])
    self.grid_layout.addWidget(self.Label_gradient_filter, 7, 0)
    self.grid_layout.addWidget(self.QComboBox_gradient_filter, 7, 1)

    self.hbox_plot_signals = QHBoxLayout()
    self.Label_plot_signals = QLabel("Plot Signals")
    self.QCheckBox_plot_signals = QCheckBox()
    self.QCheckBox_plot_signals.setChecked(self.parent().plot_signals)
    self.grid_layout.addWidget(self.Label_plot_signals, 8, 0)
    self.grid_layout.addWidget(self.QCheckBox_plot_signals, 8, 1)

    self.hbox_interm = QHBoxLayout()
    self.Label_interm = QLabel("Intermediate")
    self.QCheckBox_interm = QCheckBox()
    self.QCheckBox_interm.setChecked(self.parent().interm)
    self.grid_layout.addWidget(self.Label_interm, 9, 0)
    self.grid_layout.addWidget(self.QCheckBox_interm, 9, 1)

    self.hbox_median_w_SOL = QHBoxLayout()
    self.Label_median_w_SOL = QLabel("Median with SOL")
    self.QCheckBox_median_w_SOL = QCheckBox()
    self.QCheckBox_median_w_SOL.setChecked(self.parent().median_w_SOL)
    self.grid_layout.addWidget(self.Label_median_w_SOL, 10, 0)
    self.grid_layout.addWidget(self.QCheckBox_median_w_SOL, 10, 1)

    self.hbox_print_exec_time = QHBoxLayout()
    self.Label_print_exec_time = QLabel("Print Execution Time")
    self.QCheckBox_print_exec_time = QCheckBox()
    self.QCheckBox_print_exec_time.setChecked(self.parent().print_exec_time)
    self.grid_layout.addWidget(self.Label_print_exec_time, 11, 0)
    self.grid_layout.addWidget(self.QCheckBox_print_exec_time, 11, 1)
    if(self.apply_flag):
      self.ApplyButton = QPushButton("Apply")
      self.SaveButton = QPushButton("Save and Apply")
      self.grid_layout.addWidget(self.ApplyButton, 12, 0)
      self.ApplyButton.clicked.connect(self.apply_clicked)
      self.SaveButton.clicked.connect(self.save_settings)
      self.grid_layout.addWidget(self.SaveButton, 12, 1)
    else:
      self.SaveButton = QPushButton("Save")
      self.grid_layout.addWidget(self.SaveButton, 12, 0, 1, 2)
      self.SaveButton.clicked.connect(self.save_settings)

  def apply_clicked(self):
    image_filepath = self.parent().select_path
    settings = Settings()
    settings.init(image_filepath, self.QSpinBox_large_median.value(), self.QSpinBox_small_median.value(),
                  self.QSpinBox_enhance.value(), self.QSpinBox_SOL.isChecked(), self.QSpinBox_threshold_SOL.value(),
                  self.QComboBox_gradient_filter.currentText(), self.QCheckBox_plot_signals.isChecked(),
                  self.QCheckBox_interm.isChecked(), self.QCheckBox_median_w_SOL.isChecked(),
                  self.QCheckBox_print_exec_time.isChecked())
    self.close()


  def save_settings(self):
    self.parent().large_median = self.QSpinBox_large_median.value()
    self.parent().small_median = self.QSpinBox_small_median.value()
    self.parent().enhance = self.QSpinBox_enhance.value()
    self.parent().SOL = self.QSpinBox_SOL.isChecked()
    self.parent().threshold_SOL = self.QSpinBox_threshold_SOL.value()
    self.parent().gradient_filter = self.QComboBox_gradient_filter.currentText()
    self.parent().plot_signals = self.QCheckBox_plot_signals.isChecked()
    self.parent().interm = self.QCheckBox_interm.isChecked()
    self.parent().median_w_SOL = self.QCheckBox_median_w_SOL.isChecked()
    self.parent().print_exec_time = self.QCheckBox_print_exec_time.isChecked()


    self.parent().PARAMS["image_processing"]["large_median"] = self.parent().large_median
    self.parent().PARAMS["image_processing"]["small_median"] = self.parent().small_median
    self.parent().PARAMS["image_processing"]["enhance"] = self.parent().enhance
    self.parent().PARAMS["image_processing"]["SOL"] = self.parent().SOL
    self.parent().PARAMS["image_processing"]["threshold_SOL"] = self.parent().threshold_SOL
    self.parent().PARAMS["image_processing"]["gradient_filter"] = self.parent().gradient_filter
    self.parent().PARAMS["image_processing"]["plot_signals"] = self.parent().plot_signals
    self.parent().PARAMS["image_processing"]["interm"] = self.parent().interm
    self.parent().PARAMS["image_processing"]["median_w_SOL"] = self.parent().median_w_SOL
    self.parent().PARAMS["image_processing"]["print_exec_time"] = self.parent().print_exec_time
    self.parent().JH.write_json(self.parent().PARAMS)
    if(self.process):
      image_filepath = self.parent().select_path
      settings = Settings()
      settings.init(image_filepath, self.QSpinBox_large_median.value(), self.QSpinBox_small_median.value(),
                    self.QSpinBox_enhance.value(), self.QSpinBox_SOL.isChecked(), self.QSpinBox_threshold_SOL.value(),
                    self.QComboBox_gradient_filter.currentText(), self.QCheckBox_plot_signals.isChecked(),
                    self.QCheckBox_interm.isChecked(), self.QCheckBox_median_w_SOL.isChecked(),
                    self.QCheckBox_print_exec_time.isChecked())
    self.close()
