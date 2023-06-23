from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QHBoxLayout, QSpinBox, \
  QCheckBox, QComboBox, QPushButton

from src.gan_settings import GanSettings


class GanPipelineSettingsDialog(QDialog):

  def __init__(self, parent=None,apply_flag=False,process=False,progress_bar=None, method=None):
    super().__init__(parent)
    self.grid_layout = QGridLayout()
    self.progress_bar=progress_bar
    self.process=process
    self.apply_flag = apply_flag
    self.setLayout(self.grid_layout)
    self.setWindowTitle("GAN Processing")
    self.label_2 = QLabel("GAN Processing")
    self.label_2.setFont(QFont('Times', 10))
    self.grid_layout.addWidget(self.label_2, 1, 0)
    self.method = method

    self.hbox_stride = QHBoxLayout()
    self.Label_stride = QLabel("Stride")
    self.QSpinBox_stride = QSpinBox()
    self.QSpinBox_stride.setMinimum(3)
    self.QSpinBox_stride.setMaximum(48)
    self.QSpinBox_stride.setValue(self.parent().stride)
    self.grid_layout.addWidget(self.Label_stride, 2, 0)
    self.grid_layout.addWidget(self.QSpinBox_stride,2, 1)

    self.hbox_crop_size = QHBoxLayout()
    self.Label_crop_size = QLabel("Crop Size")
    self.QSpinBox_crop_size = QSpinBox()
    self.QSpinBox_crop_size.setEnabled(False)
    self.QSpinBox_crop_size.setMinimum(1)
    self.QSpinBox_crop_size.setMaximum(100)
    self.QSpinBox_crop_size.setValue(self.parent().crop_size)
    self.grid_layout.addWidget(self.Label_crop_size, 3, 0)
    self.grid_layout.addWidget(self.QSpinBox_crop_size, 3, 1)

    self.hbox_thresh = QHBoxLayout()
    self.Label_thresh = QLabel("Threshold")
    self.QSpinBox_thresh = QSpinBox()
    self.QSpinBox_thresh.setMinimum(1)
    self.QSpinBox_thresh.setMaximum(254)
    self.QSpinBox_thresh.setValue(self.parent().thresh)
    self.grid_layout.addWidget(self.Label_thresh, 4, 0)
    self.grid_layout.addWidget(self.QSpinBox_thresh, 4, 1)

    self.hbox_alpha = QHBoxLayout()
    self.Label_alpha = QLabel("Alpha")
    self.QSpinBox_alpha = QSpinBox()
    self.QSpinBox_alpha.setMinimum(0.1)
    self.QSpinBox_alpha.setMaximum(1)
    self.QSpinBox_alpha.setSingleStep(0.1)
    self.QSpinBox_alpha.setValue(self.parent().alpha)
    self.grid_layout.addWidget(self.Label_alpha, 5, 0)
    self.grid_layout.addWidget(self.QSpinBox_alpha, 5, 1)

    self.hbox_type = QHBoxLayout()
    self.Label_type = QLabel("Type")
    self.QComboBox_type = QComboBox()
    self.QComboBox_type.addItems(['rhythmic','stochastic'])
    self.grid_layout.addWidget(self.Label_type, 6, 0)
    self.grid_layout.addWidget(self.QComboBox_type, 6, 1)

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
    settings = GanSettings()
    settings.init(image_filepath, self.QSpinBox_stride.value(), self.QSpinBox_crop_size.value(),
                  self.QSpinBox_thresh.value(), self.QSpinBox_alpha.value(),
                  self.QComboBox_type.currentText(), self.method)
    self.accept()


  def save_settings(self):
    self.parent().stride = self.QSpinBox_stride.value()
    self.parent().crop_size = self.QSpinBox_crop_size.value()
    self.parent().thresh = self.QSpinBox_thresh.value()
    self.parent().alpha = self.QSpinBox_alpha.value()
    self.parent().type = self.QComboBox_type.currentText()

    self.parent().PARAMS["gan_processing"]["stride"] = self.parent().stride
    self.parent().PARAMS["gan_processing"]["crop_size"] = self.parent().crop_size
    self.parent().PARAMS["gan_processing"]["thresh"] = self.parent().thresh
    self.parent().PARAMS["gan_processing"]["alpha"] = self.parent().alpha
    self.parent().PARAMS["gan_processing"]["type"] = self.parent().type
    self.parent().JH.write_json(self.parent().PARAMS)
    if(self.process):
      image_filepath = self.parent().select_path
      settings = GanSettings()
      settings.init(image_filepath, self.QSpinBox_stride.value(), self.QSpinBox_crop_size.value(),
                    self.QSpinBox_thresh.value(), self.QSpinBox_alpha.value(),
                    self.QComboBox_type.currentText())
    self.accept()
