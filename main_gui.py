import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PIL import Image
import io
from PIL.ImageQt import ImageQt
from PIL import Image, ImageEnhance


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
    res_containers = dock_widget.findChildren(Result_Container)
    for x in res_containers:
        array_labels.append(x.QLabel1)
    return array_labels[-1].pixmap().copy()


class Result_Container(QDockWidget):
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
        if(chk):
            self.chk_box = QCheckBox("Select")
            self.vlayout1.addWidget(self.chk_box)
        else:
            self.chk_box = None
        self.vlayout1.addWidget(self.QLabel1)
        self.vlayout1.addWidget(self.btn_save)
        self.qwidget.setLayout(self.vlayout1)
        self.setWindowTitle(title)
        self.setWidget(self.qwidget)
        self.closeEvent = self.close_event
        self.setSizePolicy(QSizePolicy.MinimumExpanding,
                           QSizePolicy.MinimumExpanding)
        self.setFixedSize(self.vlayout1.sizeHint())

    def close_event(self, event):
        width = self.width()
        self.parent_window.setFixedWidth(self.parent_window.width()-width)
        self.parent_window.parent().parent().setFixedWidth(
            self.parent_window.parent().parent().width()-width)      
        self.setParent(QWidget())

    def save_image(self):
        im = self.QLabel1.pixmap().copy()
        name = QFileDialog.getSaveFileName(
            self, 'Save Image', ".", "Image files (*.jpg)")
        im.save(name[0])


class left_sidebar(QMainWindow):
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


class Contrast_Widget(QDockWidget):
    def __init__(self, parent_window):
        super(QDockWidget, self).__init__()
        self.setWindowTitle("Contrast Adjustement")
        self.closeEvent = self.contrast_close
        self.parent_window = parent_window
        vlayout = QVBoxLayout()
        contrast_label = QLabel("Contrast Adjustement")
        min_val = 0.5
        max_val = 1.5
        info_label_min = QLabel("Minimum Value: "+str(min_val))
        info_label_max = QLabel("Maximum Value: "+str(max_val))
        QHBoxLayout_slider = QHBoxLayout()
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setMinimum(5)
        self.contrast_slider.setMaximum(15)
        self.contrast_slider.setValue(10)
        self.contrast_slider.valueChanged.connect(self.updateLabel)
        self.slider_label = QLabel(str(self.contrast_slider.value()/10))
        QHBoxLayout_slider.addWidget(self.contrast_slider)
        QHBoxLayout_slider.addSpacing(15)
        QHBoxLayout_slider.addWidget(self.slider_label)
        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(lambda: self.apply_contrast(
            float(self.contrast_slider.value())/10))
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
        self.slider_label.setText(str(float(value)/10))

    def apply_contrast(self, value):
        obj = self.parent_window.findChildren(
            Result_Container, options=Qt.FindDirectChildrenOnly)
        for res_cont in obj:
            if(res_cont.chk_box.isChecked()):
                result = res_cont.QLabel1.pixmap().copy()
                Q_image = QPixmap.toImage(result)
                pil_im = qimage2pil(Q_image)
                contrast_image = ImageEnhance.Contrast(pil_im)
                contrast_image = contrast_image.enhance(value)
                im = qimage2pil(contrast_image)
                new_res_container = Result_Container(
                    self.parent_window, im, chk=True, title="Contrast adjustement: "+str(value))
                self.parent_window.addDockWidget(
                    Qt.LeftDockWidgetArea, new_res_container, Qt.Horizontal)
                self.parent_window.setFixedWidth(
                    self.parent_window.width()+new_res_container.sizeHint().width())
                self.parent_window.parent().parent().setFixedWidth(
                    self.parent_window.parent().parent().width()+new_res_container.sizeHint().width())

    def contrast_close(self, event):
        self.parent_window.parent().parent().contrast_opened = 0
        self.setParent(None)


class BakerImage(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.mainwindow = self
        self.contrast_opened = 0
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        fileMenu = menubar.addMenu('Open')
        newAct = QAction('File', self)
        newAct.triggered.connect(self.image_open_action)
        fileMenu.addAction(newAct)
        processingMenu = menubar.addMenu('Image Processing')
        grayscale_action = QAction('Grayscale', self)
        grayscale_action.triggered.connect(self.apply_grayscale)
        processingMenu.addAction(grayscale_action)
        contrast_sidebar_action = QAction('Contrast', self)
        contrast_sidebar_action.triggered.connect(self.apply_contrast_sidebar)
        processingMenu.addAction(contrast_sidebar_action)
        vbox1 = QVBoxLayout()
        self.hbox = QHBoxLayout()
        self.window_right = QMainWindow()
        self.left_sidebar = left_sidebar()
        self.hbox.addWidget(self.left_sidebar)
        self.hbox.addLayout(vbox1)
        self.hbox.addWidget(self.window_right)
        self.window_right.setMinimumWidth(0)
        widget = QWidget()
        widget.setLayout(self.hbox)
        self.setCentralWidget(widget)
        self.setGeometry(100, 100, 300, 900)
        self.setWindowTitle('baker-image')
        self.show()

    def apply_contrast_sidebar(self):
        if(self.contrast_opened == 0):
            self.left_sidebar.v_append_layout.addWidget(
                Contrast_Widget(self.window_right))
            self.contrast_opened += 1

    def resizeMainWindow(self):
        obj = self.window_right.findChildren(
            Result_Container, options=Qt.FindDirectChildrenOnly)
        width = 0
        for res_cont in obj:
            width += res_cont.pixmap.width()+int(res_cont.pixmap.width()/10)
        if(width == 0):
            width = 300

    def apply_grayscale(self):
        obj = self.window_right.findChildren(
            Result_Container, options=Qt.FindDirectChildrenOnly)
        for res_cont in obj:
            if(res_cont.chk_box.isChecked()):
                pix = res_cont.QLabel1.pixmap().copy()
                Q_image = QPixmap.toImage(pix)
                grayscale = Q_image.convertToFormat(QImage.Format_Grayscale8)
                pixmap_grayscale = QPixmap.fromImage(grayscale)
                im = qimage2pil(pixmap_grayscale)
                new_res_container = Result_Container(
                    self.window_right, im, chk=True, title="Grayscale")
                self.window_right.addDockWidget(
                    Qt.LeftDockWidgetArea, new_res_container, Qt.Horizontal)
                self.window_right.setFixedWidth(
                    self.window_right.width()+new_res_container.sizeHint().width())
                self.mainwindow.setFixedWidth(
                    self.mainwindow.width()+new_res_container.sizeHint().width())

    def image_open_action(self):
        im_path = QFileDialog.getOpenFileName(
            self, 'Open file', "c:/", "Image files (*.jpg *.png *.tiff)")
        if(im_path[0] != ""):
            rescontainer = Result_Container(self.window_right, Image.open(
                im_path[0]), chk=True, title=im_path[0])
            self.window_right.addDockWidget(
                Qt.LeftDockWidgetArea, rescontainer, Qt.Horizontal)
            self.window_right.setFixedWidth(
                self.window_right.width()+rescontainer.sizeHint().width())
            self.mainwindow.setFixedWidth(
                self.mainwindow.width()+rescontainer.sizeHint().width())


def main():
    app = QApplication(sys.argv)
    ex = BakerImage()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
