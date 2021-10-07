import numpy as np
import cv2

from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QPixmap
from PyQt5.QtWidgets import QApplication, QDialog

from png2fen import evaluate, visualize_regions


def pixmap2array(pixmap):
    channels = 4
    image = pixmap.toImage()
    height = pixmap.size().height()
    width = pixmap.size().width()
    s = image.bits().asstring(width * height * channels)
    arr = np.fromstring(s, dtype=np.uint8).reshape((height, width, channels)) 

    return arr


class SnippingTool(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowState(Qt.WindowState.WindowActive)
        self.setGeometry(QApplication.desktop().geometry())

        self.dekstopPixmap = self.grabScreenshot()
        self.selectedRect = QRect()

        self.fen = None

    def mousePressEvent(self, event):
        self.selectedRect.setTopLeft(event.globalPos())

    def mouseMoveEvent(self, event):
        self.selectedRect.setBottomRight(event.globalPos())
        self.update()

    def mouseReleaseEvent(self, event):
        self.selectedPixmap = self.dekstopPixmap.copy(self.selectedRect.normalized())
        self.accept()

        self.fen = evaluate(pixmap2array(self.selectedPixmap), resizing=450)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.dekstopPixmap)

        path = QPainterPath()
        path.addRect(*self.selectedRect.getRect())
        painter.fillPath(path, QColor.fromRgb(0, 0, 0, 200))

        painter.setPen(Qt.red)
        painter.drawRect(self.selectedRect)


    @staticmethod
    def grabScreenshot():
        desktopPixmap = QPixmap(QApplication.desktop().geometry().size())
        painter = QPainter(desktopPixmap)
        for screen in QApplication.screens():
            painter.drawPixmap(screen.geometry().topLeft(), screen.grabWindow(0))

        return desktopPixmap


