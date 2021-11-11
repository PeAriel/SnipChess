import PyQt5
import numpy as np
import cv2

from PyQt5.QtCore import QRect, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QCursor, QIcon, QMouseEvent, QPainter, QPainterPath, QPixmap
from PyQt5.QtWidgets import QApplication, QDialog, QLabel

from png2fen import evaluate
from fen2png import DrawBoard, is_int


def pixmap2array(pixmap):
    channels = 4
    image = pixmap.toImage()
    height = pixmap.size().height()
    width = pixmap.size().width()
    s = image.bits().asstring(width * height * channels)
    arr = np.fromstring(s, dtype=np.uint8).reshape((height, width, channels)) 

    return arr

def extend_fen(fen):
    """
    extends a fen name to be 8 characters long for each row, for easy counting.
    :param fen_list: list of strings where each string represents a rank position
    """
    for i in range(8):
        jdx = 0
        for _ in range(len(fen[i])):
            if is_int(fen[i][jdx]):
                nempty = int(fen[i][jdx])
                fen[i] = fen[i][:jdx] + 'e' * nempty + fen[i][jdx + 1:]
                jdx += nempty
                continue
            jdx += 1
    return fen

def compress_fen(extended_fen):
    compressed_fen = []
    fen_ranks = extended_fen.split('/')
    for rank in fen_ranks:
        compressed_rank = ''
        ecount = 0
        for j, square in enumerate(rank):
            if square != 'e':
                if ecount != 0:
                    compressed_rank += str(ecount)
                    ecount = 0
                compressed_rank += square                    
                continue
            ecount += 1
            if j == 7:
                compressed_rank += str(ecount)
        compressed_fen.append(compressed_rank)

    return '/'.join(list(filter(None, compressed_fen)))

def flip_fen(fen):
    tmp_fen = fen.split()
    fen_position = tmp_fen[0].split('/')[::-1]
    return ' '.join(['/'.join(fen_position), *tmp_fen[1:]])

def square_extended_fen_position(square_size, x, y):
    file = None
    rank = None
    for i in range(8):
        if x in range(square_size * i, square_size * (i + 1)):
            file = i
        if y in range(square_size * i, square_size * (i + 1)):
            rank = i
        if file and rank:
            break
    return (file, rank)


class SnippingTool(QDialog):
    def __init__(self):
        super().__init__()
        
        self.setCursor(Qt.CrossCursor)
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


class BoardWidget(QLabel):
    rightClick = pyqtSignal(float, float, QMouseEvent)

    def __init__(self, currentFen, squareSize=40):
        self.squareSize = squareSize
        super().__init__()

        board = DrawBoard(currentFen, square_size=self.squareSize)
        self.boardPixmap = board.boardQPixmap()
        self.setPixmap(self.boardPixmap)
        self.setAlignment(Qt.AlignHCenter)

        

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            heightMargin = (self.rect().height() - self.pixmap().rect().height()) // 2
            widthMargin = (self.rect().width() - self.pixmap().rect().width()) // 2
            self.rightClick.emit(event.x() - widthMargin, event.y() - heightMargin, event)
        super().mousePressEvent(event)
