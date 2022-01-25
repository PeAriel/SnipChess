import os

from PIL import Image
import numpy as np
import cv2
from PyQt5.QtGui import QImage, QPixmap

PIECES = "RBNQKPrbnqkp"
PIECES_DICT = {i: ("b" if i.islower() else "w") + i.lower() for i in PIECES}
INV_PIECES_DICT = {vals: keys for keys, vals in PIECES_DICT.items()}
INV_PIECES_DICT['e'] = 'e'
ICONS = "resources/pieces/"


def is_int(val):
    """
    checks if a string represents an integer
    :param val: single str charachter, e.g. 's'.
    """
    try:
        val = int(val)
        return True
    except ValueError:
        return False


class DrawBoard:
    def __init__(self, fen, boardtype ='w', square_size=40):
        self.dir = os.getcwd() + '/'
        self.fen = fen.split()[0]
        self.square_size = square_size
        self.piece_size = (square_size, square_size)
        self.board_size = (square_size * 8, square_size * 8)
        self.output = Image.open(self.dir + ICONS + '/board%s.png' % boardtype).resize(self.board_size)

    def _get_piece_positions(self):
        board = [["" for _ in range(8)] for _ in range(8)]
        positions = self.fen.split('/')
        for i, rank in enumerate(positions):
            j = 0
            for square in rank:
                if is_int(square):
                    j += int(square)
                    continue
                board[i][j] = square
                j += 1

        return board

    def _insert_piece(self, coordinate, piece):
        piece_img = Image.open(self.dir + ICONS + '/' + PIECES_DICT.get(piece) + '.png')
        piece_img = piece_img.resize(self.piece_size)
        X = coordinate[1] * self.square_size
        Y = coordinate[0] * self.square_size
        self.output.paste(piece_img, (X, Y), piece_img)

    def _add_pieces(self):
        positions = self._get_piece_positions()
        for i in range(8):
            for j in range(8):
                if positions[i][j]:
                    self._insert_piece((i, j), positions[i][j])

    def boardQPixmap(self, dark=True):
        self._add_pieces()
        pil_image = self.output.convert('RGB') 
        cv_image = np.array(pil_image)
        if not dark:
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        # Convert RGB to BGR 
        cvImg = cv_image[:, :, ::-1].copy()

        height, width, channel = cvImg.shape
        bytesPerLine = 3 * width
        qImg = QImage(cvImg.data, width, height, bytesPerLine, QImage.Format_RGB888)
        qPixmap = QPixmap.fromImage(qImg)
        return qPixmap
        
