import sys

sys.path.append(".")
import io
import json
import os
import shutil
import sys
import time
from pathlib import Path

from PIL import Image, ImageEnhance
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from src.UI.gan_pipeline_settings import GanPipelineSettingsDialog
from src.UI.image_pipeline_settings import ImagePipelineSettingsDialog
import src.pipeline.denoising_pipeline as denoise_pipeline


if os.getenv('RUN_MODE') == 'STUB':
  import src.pipeline.gan_pipeline_stub as gan_pipeline
else:
  import src.pipeline.gan_pipeline as gan_pipeline
  import keras.backend.tensorflow_backend as tb
  tb._SYMBOLIC_SCOPE.value = True


from src.methods import Methods


class CustomTreeView(QTreeView):

  def __init__(self, exclude=[], include=[]):
    super(CustomTreeView, self).__init__()

    self.BaseModel = QFileSystemModel()
    self.exclude = exclude
    self.include = include

    # self.baseModel.setReadOnly(True)

    self.proxy = ShowFileTypesProxy(exclude=self.exclude, include=self.include,
                                    parent=self)
    self.proxy.setDynamicSortFilter(True)
    self.proxy.setSourceModel(self.BaseModel)

    self.setModel(self.proxy)

    # idx = self.BaseModel.setRootPath("/")
    # self.setRootIndex(self.proxy.mapFromSource(idx))

  def getModel(self):
    return self.proxy


class ShowFileTypesProxy(QSortFilterProxyModel):
  def __init__(self, exclude, include, *args, **kwargs):
    super(ShowFileTypesProxy, self).__init__(*args, **kwargs)
    self._include = include
    self._folderExclude = exclude

  def filterAcceptsRow(self, srcRow, srcParent):
    idx = self.sourceModel().index(srcRow, 0, srcParent)
    absolutePath = self.sourceModel().filePath(idx)
    name = idx.data()
    if (os.path.isdir(absolutePath)):
      if (name in self._folderExclude):
        return False
      return True

    for inc in self._include:
      if name.endswith(inc):
        return True

    return False

  def ChangeModelPath(self, path):
    self.sourceModel().setRootPath(path)
    self.parent().setRootIndex(
        self.mapFromSource(self.sourceModel().index(path)))

  def GetAbsoluteSelectedPath(self):
    path = self.sourceModel().filePath(
        self.mapToSource(self.parent().currentIndex()))
    return path

  def GetRootAbsolutePath(self):
    path = self.sourceModel().rootPath()
    return path

  def FilterOutFiles(self):
    self.sourceModel().setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)

  def RevertFilter(self):
    self.sourceModel().setFilter(
        QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)

  def FilterOutFolders(self):
    self.sourceModel().setFilter(QDir.NoDotAndDotDot | QDir.Files)


class JsonHandler():
  def __init__(self, file_path):
    self.file_path = file_path

  def getData(self):
    with open(self.file_path) as f:
      data = json.load(f)
    f.close()
    return data

  def write_json(self, data):
    with open(self.file_path, 'w') as f:
      json.dump(data, f, indent=4)
    f.close()


def pil2pixmap(im):
  if im.mode == "RGB":
    r, g, b = im.split()
    im = Image.merge("RGB", (b, g, r))
  elif im.mode == "RGBA":
    r, g, b, a = im.split()
    im = Image.merge("RGBA", (b, g, r, a))
  elif im.mode == "L":
    im = im.convert("RGBA")
  # Bild in RGBA konvertieren, falls nicht bereits passiert
  im2 = im.convert("RGBA")
  data = im2.tobytes("raw", "RGBA")
  qim = QImage(data, im.size[0], im.size[1], QImage.Format_ARGB32)
  pixmap = QPixmap.fromImage(qim)
  return pixmap


def qimage2pil(qimage):
  buffer = QBuffer()
  buffer.open(QBuffer.ReadWrite)
  qimage.save(buffer, "PNG")
  pil_im = Image.open(io.BytesIO(buffer.data()))
  return pil_im


def last_pixmap_in_dock(dock_widget):
  array_labels = []
  res_containers = dock_widget.findChildren(ResultContainer)
  for x in res_containers:
    array_labels.append(x.QLabel1)
  return array_labels[-1].pixmap().copy()


class ResultContainer(QDockWidget):
  def __init__(self, parent_window, image, chk=False, title=""):
    super(QDockWidget, self).__init__()
    self.qwidget = QWidget()
    self.parent_window = parent_window
    self.image = image
    self.vlayout1 = QVBoxLayout()
    self.QLabel1 = QLabel()
    self.QLabel1.setPixmap(pil2pixmap(image))
    self.QLabel1.setAlignment(Qt.AlignCenter)
    self.pixmap = self.QLabel1.pixmap()
    self.btn_save = QPushButton("Save")
    self.btn_save.clicked.connect(self.save_image)
    self.btn_info = QPushButton("Info")
    self.btn_info.clicked.connect(self.show_info)

    self.hbox_buttons = QHBoxLayout()
    self.hbox_buttons.addWidget(self.btn_save)
    self.hbox_buttons.addWidget(self.btn_info)

    # if(chk):
    #     self.chk_box = QCheckBox("Select")
    #     self.vlayout1.addWidget(self.chk_box)
    # else:
    #     self.chk_box = None
    self.vlayout1.addLayout(self.hbox_buttons)
    self.vlayout1.addWidget(self.QLabel1)

    self.qwidget.setLayout(self.vlayout1)
    self.setWindowTitle(title)
    self.setWidget(self.qwidget)
    self.closeEvent = self.close_event
    self.setSizePolicy(QSizePolicy.MinimumExpanding,
                       QSizePolicy.MinimumExpanding)
    self.setFixedSize(self.vlayout1.sizeHint())

  def close_event(self, event):
    width = self.width()
    self.parent_window.setFixedWidth(self.parent_window.width() - width)
    self.parent_window.parent().parent().setFixedWidth(
        self.parent_window.parent().parent().width() - width)
    self.setParent(QWidget())

  def save_image(self):
    im = self.QLabel1.pixmap().copy()
    name = QFileDialog.getSaveFileName(
        self, 'Save Image', ".", "Image files (*.jpg)")
    im.save(name[0])

  def show_info(self):
    QMessageBox.information(self, "Image Info",
                            "Image Resolution :" + str(self.image.size) + "\n"
                            + "Image Format : " + str(self.image.format) + "\n"
                            + "Image Info : " + str(self.image.info) + "\n"
                            + "Image Filename : " + str(self.image.filename)
                            )


class LeftSidebar(QMainWindow):
  def __init__(self):
    super(QMainWindow, self).__init__()
    self.v_top_layout = QVBoxLayout()
    self.label_top = QLabel("Image Processing")
    self.h_separator = QFrame()
    self.h_separator.setFrameShape(QFrame.HLine)
    self.h_separator.setFrameShadow(QFrame.Sunken)
    self.v_top_layout.addWidget(self.label_top)
    self.v_top_layout.addWidget(self.h_separator)
    self.v_append_layout = QVBoxLayout()
    self.main_layout = QVBoxLayout()
    self.main_layout.addLayout(self.v_top_layout)
    self.main_layout.addLayout(self.v_append_layout)
    self.qwidget = QWidget()
    self.qwidget.setLayout(self.main_layout)
    self.setCentralWidget(self.qwidget)
    self.main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
    self.v_top_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
    self.v_append_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
    self.setFixedWidth(300)
    self.setStyleSheet("background-color: rgb(255, 255, 255);")


class ContrastWidget(QDockWidget):
  def __init__(self, parent_window):
    super(QDockWidget, self).__init__()
    self.setWindowTitle("Contrast Adjustement")
    self.closeEvent = self.contrast_close
    self.parent_window = parent_window
    vlayout = QVBoxLayout()
    contrast_label = QLabel("Contrast Adjustement")
    min_val = 0.5
    max_val = 1.5
    info_label_min = QLabel("Minimum Value: " + str(min_val))
    info_label_max = QLabel("Maximum Value: " + str(max_val))
    QHBoxLayout_slider = QHBoxLayout()
    self.contrast_slider = QSlider(Qt.Horizontal)
    self.contrast_slider.setMinimum(5)
    self.contrast_slider.setMaximum(15)
    self.contrast_slider.setValue(10)
    self.contrast_slider.valueChanged.connect(self.updateLabel)
    self.slider_label = QLabel(str(self.contrast_slider.value() / 10))
    QHBoxLayout_slider.addWidget(self.contrast_slider)
    QHBoxLayout_slider.addSpacing(15)
    QHBoxLayout_slider.addWidget(self.slider_label)
    apply_button = QPushButton("Apply")
    apply_button.clicked.connect(lambda: self.apply_contrast(
        float(self.contrast_slider.value()) / 10))
    vlayout.addWidget(contrast_label)
    vlayout.addWidget(info_label_min)
    vlayout.addWidget(info_label_max)
    vlayout.addLayout(QHBoxLayout_slider)
    vlayout.addWidget(apply_button)
    vlayout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
    new_widget = QWidget()
    new_widget.setLayout(vlayout)
    self.setWidget(new_widget)
    self.contrast_opened = 1
    self.setStyleSheet("background-color: rgb(200, 200, 200);")
    self.setFixedHeight(200)

  def updateLabel(self, value):
    self.slider_label.setText(str(float(value) / 10))

  def apply_contrast(self, value):
    obj = self.parent_window.findChildren(
        ResultContainer, options=Qt.FindDirectChildrenOnly)
    for res_cont in obj:
      if (res_cont.chk_box.isChecked()):
        result = res_cont.QLabel1.pixmap().copy()
        Q_image = QPixmap.toImage(result)
        pil_im = qimage2pil(Q_image)
        contrast_image = ImageEnhance.Contrast(pil_im)
        contrast_image = contrast_image.enhance(value)
        im = qimage2pil(contrast_image)
        new_res_container = ResultContainer(
            self.parent_window, im, chk=True,
            title="Contrast adjustement: " + str(value))
        self.parent_window.addDockWidget(
            Qt.LeftDockWidgetArea, new_res_container, Qt.Horizontal)
        self.parent_window.setFixedWidth(
            self.parent_window.width() + new_res_container.sizeHint().width())
        self.parent_window.parent().parent().setFixedWidth(
            self.parent_window.parent().parent().width() + new_res_container.sizeHint().width())

  def contrast_close(self, event):
    self.parent_window.parent().parent().contrast_opened = 0
    self.setParent(None)


class SettingsGlobal(QDialog):
  def __init__(self, parent=None):
    super().__init__(parent)
    self.grid_layout = QGridLayout()
    self.setWindowTitle("Global")
    self.setLayout(self.grid_layout)
    self.dir_name = ""

    self.Hline = QFrame()
    self.Hline.setFrameShape(QFrame.HLine)
    self.Hline.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
    self.Hline.setLineWidth(2)

    self.label_1 = QLabel("Application")
    self.label_1.setFont(QFont('Times', 10))
    self.grid_layout.addWidget(self.label_1, 0, 0)

    self.basePath = QLabel("Base Path")
    self.dirButton = QPushButton("Browse")
    self.pathEditText = QLineEdit()
    self.pathEditText.setText(self.parent().base_dir)
    self.pathEditText.setReadOnly(True)

    self.setAsDefaultBtn = QPushButton("Set as Default")
    self.setAsDefaultBtn.clicked.connect(self.setPathAsDefault)
    self.dirButton.clicked.connect(self.browse_dir)

    self.grid_layout.addWidget(self.basePath, 1, 0)
    self.grid_layout.addWidget(self.pathEditText, 1, 1)
    self.grid_layout.addWidget(self.dirButton, 2, 0)
    self.grid_layout.addWidget(self.setAsDefaultBtn, 2, 1)

  def browse_dir(self):
    selectedDIR = QFileDialog.getExistingDirectory(self, "Select Directory")
    if (selectedDIR):
      self.pathEditText.setText(selectedDIR)
      self.dir_name = selectedDIR

  def setPathAsDefault(self):
    pwrite = self.parent().PARAMS
    pwrite["app"]["base_dir"] = self.dir_name
    self.parent().JH.write_json(pwrite)


class UIForm(object):
  def setupUI(self, Form):
    Form.setObjectName("Form")
    Form.resize(550, 140)
    self.grid_layout = QGridLayout(Form)

    self.label_title = QLabel()
    font = QFont()
    font.setPointSize(14)
    font.setBold(True)
    font.setWeight(75)
    self.grid_layout.addWidget(self.label_title, 0, 0, 1, 2)
    self.label_title.setFont(font)
    self.label_title.setText("Processing...")
    self.label_title.setGeometry(QRect(30, 10, 500, 31))

    self.label_progress_1 = QLabel()
    self.label_progress_1.setText("0/100")
    self.label_progress_1.setAlignment(Qt.AlignRight)
    self.grid_layout.addWidget(self.label_progress_1, 3, 0)

    self.progressBar = QProgressBar()
    # self.progressBar.setGeometry(QRect(30, 60, 500, 35))
    sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(
        self.progressBar.sizePolicy().hasHeightForWidth())
    self.progressBar.setSizePolicy(sizePolicy)
    self.progressBar.setMinimumSize(QSize(500, 35))
    self.progressBar.setMaximumSize(QSize(500, 35))
    self.progressBar.setProperty("value", 0)
    self.progressBar.setObjectName("progressBar")
    self.grid_layout.addWidget(self.progressBar, 2, 0, 1, 2)
    self.label_progress_2 = QLabel()
    # self.label_progress_2.setGeometry(QRect(30, 100, 500, 16))
    self.label_progress_2.setText("0/4")
    self.label_progress_2.setAlignment(Qt.AlignRight)
    self.grid_layout.addWidget(self.label_progress_2, 1, 0)
    self.progressBar_Global = QProgressBar(Form)
    # self.progressBar_Global.setGeometry(QRect(30, 120, 500, 35))
    self.progressBar_Global.setSizePolicy(sizePolicy)
    self.progressBar_Global.setMinimumSize(QSize(500, 35))
    self.progressBar_Global.setMaximumSize(QSize(500, 35))
    self.progressBar_Global.setProperty("value", 0)
    self.progressBar_Global.setObjectName("progressBar_Global")
    self.grid_layout.addWidget(self.progressBar_Global, 4, 0, 1, 2)
    self.retranslateUI(Form)
    QMetaObject.connectSlotsByName(Form)

  def retranslateUI(self, Form):
    _translate = QCoreApplication.translate
    Form.setWindowTitle(_translate("Form", "Progress bar"))


class ProgressBar(QDialog, UIForm):
  def __init__(self, desc=None, parent=None):
    super(ProgressBar, self).__init__(parent)
    self.p1 = parent
    self.setupUI(self)

    if desc != None:
      self.setDescription(desc)

  def setValueP1(self, val):  # Sets value
    self.progressBar.setProperty("value", val)

  def setValueP2(self, val):  # Sets value
    self.progressBar_Global.setProperty("value", val)

  def setValueP1Text(self, val):
    self.label_progress_1.setText(val)

  def setValueP2Text(self, val):
    self.label_progress_2.setText(val)

  def setDescription(self, desc):  # Sets Pbar window title
    self.setWindowTitle(desc)

  def closeEvent(self, a0: QCloseEvent) -> None:
    self.p1.setEnabled(True)
    if os.path.isdir(self.p1.select_path):
      pathFolder = self.p1.select_path + "/output"
    else:
      pathFolder = str(Path(self.p1.select_path).parent) + "/output"

    # self.p1.dirModel_right.ChangeModelPath(pathFolder)
    # self.p1.label_current_dir_right.setText(pathFolder)
    return super().closeEvent(a0)


class CellCAD(QMainWindow):

  def __init__(self):
    super().__init__()
    self.initUI()

  def initUI(self):
    self.mainwindow = self
    self.contrast_opened = 0
    self.JH = JsonHandler("my_settings.json")
    self.PARAMS = self.JH.getData()
    self.select_path = None
    self.setWindowIcon(QIcon('logo.png'))
    # -----------------------------------------------------------------
    # PARAMETERS
    # -----------------------------------------------------------------
    # APP PARAMS
    self.base_dir = self.PARAMS["app"]["base_dir"]
    # IMAGE PROCESSING PARAMS
    self.large_median = self.PARAMS["image_processing"]["large_median"]
    self.small_median = self.PARAMS["image_processing"]["small_median"]
    self.enhance = self.PARAMS["image_processing"]["enhance"]
    self.SOL = self.PARAMS["image_processing"]["SOL"]
    self.threshold_SOL = self.PARAMS["image_processing"]["threshold_SOL"]
    self.gradient_filter = self.PARAMS["image_processing"]["gradient_filter"]
    self.plot_signals = self.PARAMS["image_processing"]["plot_signals"]
    self.interm = self.PARAMS["image_processing"]["interm"]
    self.median_w_SOL = self.PARAMS["image_processing"]["median_w_SOL"]
    self.print_exec_time = self.PARAMS["image_processing"]["print_exec_time"]
    # -----------------------------------------------------------------

    # GAN PROCESSING PARAMS
    self.stride = self.PARAMS["gan_processing"]["stride"]
    self.crop_size = self.PARAMS["gan_processing"]["crop_size"]
    self.thresh = self.PARAMS["gan_processing"]["thresh"]
    self.alpha = self.PARAMS["gan_processing"]["alpha"]
    self.type = self.PARAMS["gan_processing"]["type"]
    self.method = self.PARAMS["gan_processing"]["method"]
    # -----------------------------------------------------------------

    self.prog_bar = ProgressBar("Processing...", self)
    self.tot_images_prog_bar = 0

    menubar = self.menuBar()
    menubar.setNativeMenuBar(False)
    fileMenu = menubar.addMenu('File')
    models_menu = menubar.addMenu('Settings')

    exitAction = QAction('Exit', self)
    exitAction.triggered.connect(self.exitMethod)
    GlobalSettings = QAction("Global Settings", self)
    fileMenu.addAction(GlobalSettings)
    fileMenu.addAction(exitAction)
    GlobalSettings.triggered.connect(self.settingsPopup)

    sm1 = QAction("Image Pipeline Settings", self)
    sm2 = QAction("GAN Pipeline Settings", self)

    models_menu.addAction(sm1)
    models_menu.addAction(sm2)
    sm1.triggered.connect(self.settings_popup_image_pipeline)
    sm2.triggered.connect(self.settings_popup_gan_pipeline)
    self.vbox_top = QVBoxLayout()
    self.hbox = QHBoxLayout()
    self.window_right = QMainWindow()

    # ------------ LEFT DIRECTORY TREE VIEW -----------
    self.treeview = CustomTreeView(
        include=[".jpg", ".png", ".jpeg", ".bmp", ".tif", ".tiff"],
        exclude=[""])

    self.dirModel = self.treeview.getModel()
    # self.dirModel.FilterOutFiles()
    path = str(Path.home())
    if (self.base_dir != None):
      path = self.base_dir

    self.dirModel.ChangeModelPath(path)
    self.treeview.setContextMenuPolicy(Qt.CustomContextMenu)
    self.treeview.doubleClicked.connect(self.treeview_doubleClicked)
    default_act = QAction("Set As Default", self.treeview)
    self.treeview.addAction(default_act)
    self.treeview.customContextMenuRequested.connect(self.menuContextTree)
    self.treeview.clicked.connect(self.dirview_clicked)
    self.treeview.header().resizeSection(0, self.treeview.width() / 3)
    # ----------------------------------------

    # ------------ RIGHT DIRECTORY TREE VIEW -----------
    # self.treeview_right = CustomTreeView(
    #     include=[".jpg", ".png", ".jpeg", ".bmp", ".tif", ".tiff"])
    # self.dirModel_right = self.treeview_right.getModel()
    # self.treeview_right.doubleClicked.connect(self.treeview_right_doubleClicked)
    # # self.dirModel_right.ChangeModelPath(None)
    # self.treeview_right.header().resizeSection(0,
    #                                            self.treeview_right.width() / 3)
    # ----------------------------------------

    self.button_home = QPushButton("User Directory")
    self.button_default = QPushButton("Default Directory")
    self.button_back = QPushButton("Back")
    self.button_home.clicked.connect(self.return_home)
    self.button_back.clicked.connect(self.return_back)
    self.button_default.clicked.connect(self.return_default)
    self.hbox_buttons_tree = QHBoxLayout()
    self.hbox_buttons_tree.addWidget(self.button_back)
    self.hbox_buttons_tree.addWidget(self.button_default)
    self.hbox_buttons_tree.addWidget(self.button_home)
    self.label_current_dir = QLabel()
    self.label_current_dir.setText(path)

    # ------------ DROP DOWN + APPLY BUTTON -----------
    self.combo = QComboBox()
    self.combo.addItem(Methods.METHOD_IMG_PROC.value)
    self.combo.addItem(Methods.METHOD_GAN_IMG_PROC.value)
    self.combo.addItem(Methods.METHOD_GAN_4SM.value)
    self.combo.addItem(Methods.METHOD_GAN_SEGMENTATION.value)
    self.button_process = QPushButton("Apply")
    self.button_process.clicked.connect(self.process_path)
    self.hbox_buttons = QHBoxLayout()
    self.hbox_buttons.addWidget(self.combo)
    self.hbox_buttons.addWidget(self.button_process)
    # -----------------------------------------------

    self.vbox_up = QVBoxLayout()
    self.hbox_top_left = QHBoxLayout()
    self.vbox_up.addLayout(self.hbox_buttons)
    self.vbox_up.addWidget(self.label_current_dir)
    self.vbox_up.addLayout(self.hbox_buttons_tree)
    self.hbox_top_left.addLayout(self.vbox_up)
    self.empty_hbox = QHBoxLayout()
    # self.label_current_dir_right = QLabel()
    # self.label_current_dir_right.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
    # self.empty_hbox.addWidget(self.label_current_dir_right)
    self.hbox_top_left.addLayout(self.empty_hbox)
    self.vbox_top.addLayout(self.hbox_top_left)
    hbox_trees = QHBoxLayout()
    hbox_trees.addWidget(self.treeview)
    # hbox_trees.addWidget(self.treeview_right)
    self.vbox_top.addLayout(hbox_trees)
    self.hbox.addLayout(self.vbox_top)
    self.hbox.addWidget(self.window_right)
    self.window_right.setMinimumWidth(0)
    self.window_right.resize(self.window_right.sizeHint())
    self.window_right.setFixedWidth(0)
    widget = QWidget()
    widget.setLayout(self.hbox)
    self.setCentralWidget(widget)
    self.setGeometry(100, 100, screen_width / 3, screen_height / 1.5)
    self.setWindowTitle('Cal Denoise: Subcellular Calcium Analysis and Denoising')
    self.show()

  def treeview_right_doubleClicked(self):
    index = self.treeview_right.currentIndex()
    path = self.dirModel_right.GetAbsoluteSelectedPath()
    arr_ext = (".jpg", ".jpeg", ".png", ".tif", ".tiff")
    if (path.endswith(arr_ext)):
      self.image_open_action(path)

  def exitMethod(self):
    self.close()

  def treeview_doubleClicked(self):
    index = self.treeview.currentIndex()
    path = self.dirModel.GetAbsoluteSelectedPath()

    if (os.path.isdir(path)):
      self.update_selected_folder(path)
    else:
      arr_ext = (".jpg", ".jpeg", ".png", ".tif", ".tiff")
      if (path.endswith(arr_ext)):
        self.image_open_action(path)

  def update_selected_folder(self, input_folder_path):
    output_path = input_folder_path + "/output"
    self.dirModel.ChangeModelPath(input_folder_path)
    self.label_current_dir.setText(input_folder_path)
    # if os.path.isdir(output_path):
      # self.dirModel_right.ChangeModelPath(output_path)
      # self.label_current_dir_right.setText(output_path)
    # else:
    # self.treeview_right = QTreeView()

  def return_default(self):
    self.dirModel.ChangeModelPath(self.base_dir)
    self.label_current_dir.setText(self.base_dir)

  def return_home(self):
    self.dirModel.ChangeModelPath(str(Path.home()))
    self.label_current_dir.setText(str(Path.home()))

  def return_back(self):
    path = self.dirModel.GetRootAbsolutePath()
    path_up = os.path.dirname(path)
    self.dirModel.ChangeModelPath(path_up)
    self.label_current_dir.setText(path_up)

  def menuContextTree(self, point):
    index = self.treeview.indexAt(point)
    if not index.isValid():
      return

    self.selected_path = self.dirModel.GetAbsoluteSelectedPath()

    menu = QMenu()
    action_open_in_dock = None
    action_default = None
    menu.addSeparator()
    delete_action = menu.addAction("Delete")
    arr_ext = (".jpg", ".jpeg", ".png", ".tif", ".tiff")
    if (self.selected_path.endswith(arr_ext)):
      action_open_in_dock = menu.addAction("Open Image")
      action_model1 = QAction("Image Pipeline Settings")
      action_model2 = QAction("GAN Pipeline Settings")
    elif (os.path.isdir(self.selected_path)):
      action_default = QAction("Set Directory As Default")
      action_batch = QAction("Batch Image Processing")
      action_batch.triggered.connect(self.batch_image_processing)

    if (action_default != None):
      action_default.triggered.connect(self.CustomContextDefault)
      menu.addAction(action_default)
      menu.addSeparator()
      menu.addAction(delete_action)
    if (action_open_in_dock != None):
      action_open_in_dock.triggered.connect(self.CustomContextOpenInDock)
      menu.addAction(action_open_in_dock)

      menu.addAction(delete_action)

    delete_action.triggered.connect(self.CustomContextDelete)

    menu.exec_(self.treeview.mapToGlobal(point))

  def CustomContextDelete(self):
    # confirmation dialog
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("Are you sure you want to delete?")
    msg.setWindowTitle("Warning")
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    msg.buttonClicked.connect(self.deleteSelected)
    msg.exec_()

  def deleteSelected(self, i):
    if (i.text() == "OK"):
      if (os.path.isdir(self.selected_path)):
        # treeview_right_path = self.dirModel_right.GetRootAbsolutePath()
        # if (self.selected_path == treeview_right_path):
        #   self.dirModel_right.ChangeModelPath(None)
        #   self.label_current_dir_right.setText("")
        shutil.rmtree(self.selected_path)
      else:
        os.remove(self.selected_path)
      self.select_path = os.path.dirname(self.select_path)
      self.treeview.setRootIndex(self.treeview.rootIndex())
      # self.treeview_right.setRootIndex(self.treeview_right.rootIndex())

  def batch_image_processing(self):
    index = self.treeview.currentIndex()
    path = self.dirModel.filePath(index)
    pb = ProgressBar(parent=self)
    settings = ImagePipelineSettingsDialog(self, True, process=True,
                                           progress_bar=pb)
    settings.show()
    pb.close()
    self.setEnabled(True)

  def CustomContextImageProcessing(self):
    # METHOD 1 TRIGGERS HERE
    index = self.treeview.currentIndex()
    path = self.dirModel.filePath(index)
    pb = ProgressBar(parent=self)
    self.setEnabled(False)
    settings = ImagePipelineSettingsDialog(self, True, process=True,
                                           progress_bar=pb)
    settings.show()
    pb.close()
    self.setEnabled(True)

  def CustomContextMLModel(self):
    # METHOD 2 TRIGGERS HERE
    index = self.treeview.currentIndex()
    path = self.dirModel.filePath(index)
    self.setEnabled(False)
    pb = ProgressBar(parent=self)
    to_range1 = 100
    to_range2 = 4
    for j in range(0, to_range2):
      for i in range(0, to_range1):
        time.sleep(0.05)
        pb.setValueP1(((i + 1) / to_range1) * 100)
        pb.setValueP1Text(str(i) + "/" + str(to_range1))
        QApplication.processEvents()

      pb.setValueP2(((j + 1) / to_range2) * 100)
      pb.setValueP2Text(str(j + 1) + "/" + str(to_range2))

    pb.close()
    self.setEnabled(True)

  def CustomContextDefault(self):
    if (os.path.isdir(self.selected_path)):
      self.base_dir = self.selected_path
      pwrite = self.PARAMS
      pwrite["app"]["base_dir"] = self.selected_path
      self.JH.write_json(pwrite)

    else:
      self.selected_path = None

  def CustomContextOpenInDock(self):
    self.image_open_action(self.selected_path)

  def settingsPopup(self):
    exPopup = SettingsGlobal(self)
    exPopup.resize(QSize(self.width() / 1.8, exPopup.height()))
    exPopup.show()

  def settings_popup_image_pipeline(self):
    exPopup1 = ImagePipelineSettingsDialog(self)
    exPopup1.show()

  def settings_popup_gan_pipeline(self):
    exPopup1 = GanPipelineSettingsDialog(self)
    exPopup1.show()

  def setdirviewpath(self):
    path = QFileDialog.getExistingDirectory(self, "Select Directory")
    self.treeview.setRootIndex(self.dirModel.index(path))

  def dirview_clicked(self, index):
    path = self.dirModel.GetAbsoluteSelectedPath()
    self.select_path = path

  def apply_contrast_sidebar(self):
    if (self.contrast_opened == 0):
      self.left_sidebar.v_append_layout.addWidget(
          ContrastWidget(self.window_right))
      self.contrast_opened += 1

  def resizeMainWindow(self):
    obj = self.window_right.findChildren(
        ResultContainer, options=Qt.FindDirectChildrenOnly)
    width = 0
    for res_cont in obj:
      width += res_cont.pixmap.width() + int(res_cont.pixmap.width() / 10)
    if (width == 0):
      width = 300

  def image_open_action(self, im_path):
    if (im_path != ""):
      rescontainer = ResultContainer(self.window_right, Image.open(
          im_path), chk=True, title=im_path)
      self.window_right.addDockWidget(
          Qt.LeftDockWidgetArea, rescontainer, Qt.Horizontal)
      self.window_right.setFixedWidth(
          self.window_right.width() + rescontainer.sizeHint().width())
      self.mainwindow.setFixedWidth(
          self.mainwindow.width() + rescontainer.sizeHint().width())

  def BatchImageProcessing(self, method):
    self.setEnabled(False)
    count_images = 0
    for file in os.listdir(self.select_path):
      arr_ext = (".jpg", ".jpeg", ".png", ".tif", ".tiff")
      if (file.endswith(arr_ext)):
        count_images += 1
    self.tot_images_prog_bar = count_images
    if method == Methods.METHOD_IMG_PROC.value:
      settings = ImagePipelineSettingsDialog(self, True, process=True,
                                             progress_bar=self.prog_bar)
    else:
      settings = GanPipelineSettingsDialog(self, True, process=True,
                                           progress_bar=self.prog_bar,
                                           method=method)
    settings.exec_()
    self.prog_bar.show()
    self.thread = MyThread(self.select_path, method)
    self.thread.change_value.connect(self.setProgressVal)
    self.thread.end_value.connect(self.endProgressBar)
    self.thread.start()

  def SingleImageProcessing(self, method):
    self.setEnabled(False)
    self.tot_images_prog_bar = 1
    if method == Methods.METHOD_IMG_PROC.value:
      settings = ImagePipelineSettingsDialog(self, True, process=True,
                                             progress_bar=self.prog_bar)
    else:
      settings = GanPipelineSettingsDialog(self, True, process=True,
                                           progress_bar=self.prog_bar)
    settings.exec_()
    self.prog_bar.show()
    self.thread = MyThread(self.select_path, method)
    self.thread.change_value.connect(self.setProgressVal)
    self.thread.end_value.connect(self.endProgressBar)
    self.thread.start()

  def endProgressBar(self):
    self.setEnabled(True)
    self.prog_bar.close()

  def setProgressVal(self, val):
    self.prog_bar.setValueP2(100)
    self.prog_bar.setValueP1Text("1/1")
    self.prog_bar.setValueP1(val / self.tot_images_prog_bar * 100)
    self.prog_bar.setValueP2Text(str(val) + "/" + str(self.tot_images_prog_bar))
    self.prog_bar.setValueP2(0)
    self.prog_bar.setValueP1Text("0/1")

  def process_path(self):
    combo_value = self.combo.currentText()
    index = self.treeview.currentIndex()
    path = self.dirModel.GetAbsoluteSelectedPath()
    if (self.select_path != None):
      if (os.path.isdir(path)):

        if (combo_value == Methods.METHOD_IMG_PROC.value):
          self.BatchImageProcessing(Methods.METHOD_IMG_PROC.value)

        if (combo_value == Methods.METHOD_GAN_IMG_PROC.value):
          self.BatchImageProcessing(Methods.METHOD_GAN_IMG_PROC.value)

        if (combo_value == Methods.METHOD_GAN_4SM.value):
          self.BatchImageProcessing(Methods.METHOD_GAN_4SM.value)

        if (combo_value == Methods.METHOD_GAN_SEGMENTATION.value):
          self.BatchImageProcessing(Methods.METHOD_GAN_SEGMENTATION.value)
      else:
        if (combo_value == Methods.METHOD_IMG_PROC.value):
          self.SingleImageProcessing(Methods.METHOD_IMG_PROC.value)
        if (combo_value == Methods.METHOD_GAN_IMG_PROC.value):
          self.SingleImageProcessing(Methods.METHOD_GAN_IMG_PROC.value)
        if (combo_value == Methods.METHOD_GAN_4SM.value):
          self.SingleImageProcessing(Methods.METHOD_GAN_4SM.value)
        if (combo_value == Methods.METHOD_GAN_SEGMENTATION.value):
          self.SingleImageProcessing(Methods.METHOD_GAN_SEGMENTATION.value)
    else:
      QMessageBox.warning(self, 'Warning', "Please select a file or directory")


class MyThread(QThread):
  # Create a counter thread
  change_value = pyqtSignal(int)
  end_value = pyqtSignal(int)

  # init
  def __init__(self, folder=None, method=Methods.METHOD_IMG_PROC.value):
    super(MyThread, self).__init__()
    self.folder = folder
    self.method = method

  def run(self):
    if os.getenv('RUN_MODE') != 'STUB':
      import keras.backend.tensorflow_backend as tb
      tb._SYMBOLIC_SCOPE.value = True

    if (os.path.isdir(self.folder)):
      files = os.listdir(self.folder)
      count_images = 0
      for file in files:
        arr_ext = (".jpg", ".jpeg", ".png", ".tif", ".tiff")
        if (file.endswith(arr_ext)):
          count_images += 1
      count = 0
      for x in os.listdir(self.folder):
        if (x.endswith(arr_ext)):
          if (self.method == Methods.METHOD_IMG_PROC.value):
            denoise_pipeline.process_single_image(self.folder + "/" + x)
          else:
            [local_model, global_model] = gan_pipeline.load_models(self.method)
            gan_pipeline.gan_process_single_image(self.folder + "/" + x,
                                                  local_model, global_model)
          self.change_value.emit(count)
          count += 1

      self.end_value.emit(1)
    else:
      if (self.method == Methods.METHOD_IMG_PROC.value):
        filePath = Path(self.folder);
        denoise_pipeline.process_single_image(str(filePath.parent) + "/" + filePath.name)
      else:
        [local_model, global_model] = gan_pipeline.load_models(self.method)
        gan_pipeline.gan_process_single_image(self.folder, local_model, global_model)
      self.change_value.emit(1)
      time.sleep(0.5)
      self.end_value.emit(1)


def main():
  QApplication.setStyle('Fusion')
  app = QApplication(sys.argv)
  screen = app.primaryScreen()
  rect = screen.availableGeometry()
  global screen_width
  screen_width = rect.width()
  global screen_height
  screen_height = rect.height()
  ex = CellCAD()
  sys.exit(app.exec_())


if __name__ == '__main__':
  main()
