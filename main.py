import sys
from time import sleep
from functools import partial

from PyQt5.QtCore import QSize, Qt, QPoint, QRect
from PyQt5.QtGui import QIcon, QIntValidator, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QComboBox,
                            QLabel, QDialog, QDialogButtonBox, QPushButton,
                            QSystemTrayIcon, QLineEdit, QMainWindow, QMenu,
                            QHBoxLayout, QVBoxLayout, QGridLayout
                            )

from utils import SnippingTool, BoardWidget, square_extended_fen_position, extend_fen, compress_fen, flip_fen
from fen2png import DrawBoard, PIECES_DICT, INV_PIECES_DICT
from help_messages import *


class FenSettingsWindow(QDialog):
    def __init__(self, fen):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowState(Qt.WindowState.WindowActive)

        self.setWindowTitle('FEN Settings')
        self.mainLayout = QVBoxLayout()

        self.origFen = fen
        self.fen = fen
        self.fenSpecs = ['' if i % 2 != 0 else ' ' for i in range(10)]
        self.fenSpecs[1] = 'w'
        self.fenSpecs[3] = 'KQkq'
        self.fenSpecs[5] = '-'
        self.fenSpecs[7] = '0'
        self.fenSpecs[9] = '20'
        self.boardSquareSize = 40

        self.addHowPlays()
        self.addPerspective()
        self.addSettings()
        self.addBoard(fen)
        self.addFenLineEdit()
        self.addButtons()
        self.addToolTips()

        self.halfMoveText.setText('0')
        self.fullMoveText.setText('20')

        self.whoPlaysComboBox.currentIndexChanged.connect(self.configChanged)
        self.whoPlaysComboBox.currentIndexChanged.connect(self.changeEnPassant)
        self.perspectiveComboBox.currentIndexChanged.connect(self.perspectiveChanged)
        self.whiteOO.stateChanged.connect(self.configChanged)
        self.whiteOOO.stateChanged.connect(self.configChanged)
        self.blackOO.stateChanged.connect(self.configChanged)
        self.blackOOO.stateChanged.connect(self.configChanged)
        self.halfMoveText.textChanged.connect(self.configChanged)
        self.fullMoveText.textChanged.connect(self.configChanged)
        self.enPassantComboBox.currentIndexChanged.connect(self.configChanged)

        self.configChanged()
        self.fenLineEdit.setText(self.origFen + ''.join(self.fenSpecs))

        self.buttonBox.accepted.connect(self.okPressed)
        self.buttonBox.rejected.connect(self.reject)

        self.addRightClickMenu()
        for key, value in self.contextActions.items():
            value.triggered.connect(partial(self.imageClicked, key))

        self.boardImage.setMouseTracking(True)
        self.boardImage.rightClick.connect(self.rightMoueseClick)

        self.setLayout(self.mainLayout)

    def changeEnPassant(self):
        if self.whoPlaysComboBox.currentIndex() == 0:
            self.enPassantComboBox.clear()
            self.enPassantComboBox.addItem('-')
            for file in 'abcdefgh':
                self.enPassantComboBox.addItem(file + '6')
        else:
            self.enPassantComboBox.clear()
            self.enPassantComboBox.addItem('-')
            for file in 'abcdefgh':
                self.enPassantComboBox.addItem(file + '3')
        self.updateFenAndBoard()
        
    def imageClicked(self, piece):
        file, rank = square_extended_fen_position(self.boardSquareSize, *self.clickCoordinates)
        splitted_fen = self.fen.split(' ')
        extended_fen = extend_fen(splitted_fen[0].split('/'))
        extended_fen[rank] = extended_fen[rank][:file] + INV_PIECES_DICT[piece] + extended_fen[rank][file + 1:]
        new_fen = ' '.join([compress_fen('/'.join(extended_fen)), *splitted_fen[1:]])
        self.fenLineEdit.setText(new_fen)
        self.updateFenAndBoard()

    def rightMoueseClick(self, x, y, e):
        self.clickCoordinates = [x, y]
        self.rightClickMenu.exec_(e.globalPos())

    def okPressed(self):
        self.accept()
        
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(self.fen, mode=cb.Clipboard)

        self.close()        

    def perspectiveChanged(self):
        tmp_fen = self.fen.split()
        fen_position = tmp_fen[0].split('/')[::-1]
        self.fenLineEdit.setText(' '.join(['/'.join(fen_position), *tmp_fen[1:]]))
        self.updateFenAndBoard()

    def configChanged(self):
        if self.whoPlaysComboBox.currentIndex() == 0:
            self.fenSpecs[1] = 'w'
        else:
            self.fenSpecs[1] = 'b'
        
        castlingPart = []
        if all([not self.whiteOO.isChecked(),
                not self.whiteOOO.isChecked(),
                not self.blackOO.isChecked(),
                not self.blackOOO.isChecked()]):
            self.fenSpecs[3] = '-'
        else:
            if self.whiteOO.isChecked():
                castlingPart.append('K')
            if self.whiteOOO.isChecked():
                castlingPart.append('Q')
            if self.blackOO.isChecked():
                castlingPart.append('k')
            if self.blackOOO.isChecked():
                castlingPart.append('q')
            self.fenSpecs[3] = ''.join(castlingPart)

        self.fenSpecs[5] = self.enPassantComboBox.currentText()
        self.fenSpecs[7] = self.halfMoveText.text()
        self.fenSpecs[9] = self.fullMoveText.text()
        
        if self.perspectiveComboBox.currentIndex() == 0:
            self.fen = self.origFen + ''.join(self.fenSpecs)
        else:
            self.fen = flip_fen(self.origFen) + ''.join(self.fenSpecs)
        self.fenLineEdit.setText(self.fen)

    def updateFenAndBoard(self):
        self.fen = self.fenLineEdit.text()
        board = DrawBoard(self.fen)
        self.boardImage.setPixmap(board.boardQPixmap())

    def addHowPlays(self):
        self.colorsLayout = QHBoxLayout()

        self.whoPlaysComboBox = QComboBox()
        self.whoPlaysComboBox.addItem('White to play')
        self.whoPlaysComboBox.addItem('Black to play')

        self.colorsLayout.addWidget(self.whoPlaysComboBox)
        self.mainLayout.addLayout(self.colorsLayout)

    def addPerspective(self):
        self.perspectiveComboBox = QComboBox() 
        self.perspectiveComboBox.addItem("White's perspective")
        self.perspectiveComboBox.addItem("Black's perspective")

        self.colorsLayout.addWidget(self.perspectiveComboBox)

    def addSettings(self):
        settingsLayout = QVBoxLayout()

        castelingLayout = QHBoxLayout()
        whiteLayout = QVBoxLayout()
        blackLayout = QVBoxLayout()

        self.whiteOO = QCheckBox('O-O')
        self.whiteOOO = QCheckBox('O-O-O')
        self.blackOO = QCheckBox('O-O')
        self.blackOOO = QCheckBox('O-O-O')
        
        self.whiteOO.setChecked(True)
        self.whiteOOO.setChecked(True)
        self.blackOO.setChecked(True)
        self.blackOOO.setChecked(True)

        whiteLayout.addWidget(QLabel('White'))
        whiteLayout.addWidget(self.whiteOO)
        whiteLayout.addWidget(self.whiteOOO)
        blackLayout.addWidget(QLabel('Black'))
        blackLayout.addWidget(self.blackOO)
        blackLayout.addWidget(self.blackOOO)

        castelingLayout.addLayout(whiteLayout)
        castelingLayout.addLayout(blackLayout)
        castelingLayout.setAlignment(Qt.AlignHCenter)
        settingsLayout.addLayout(castelingLayout)

        enPassantLayout = QHBoxLayout()
        self.enPassantComboBox = QComboBox()
        self.enPassantLabel = QLabel('En passant square:')
        enPassantLayout.addWidget(self.enPassantLabel)
        enPassantLayout.addWidget(self.enPassantComboBox)
        enPassantLayout.setAlignment(Qt.AlignHCenter)
        self.enPassantComboBox.addItem('-')
        for file in 'abcdefgh':
            self.enPassantComboBox.addItem(file + '6')

        halfMoveLayout = QHBoxLayout()
        self.halfMoveText = QLineEdit()
        self.halfMoveLabel = QLabel('Halfmove count:')
        self.halfMoveText.setValidator(QIntValidator())
        self.halfMoveText.setFixedWidth(self.halfMoveText.width() // 10)
        halfMoveLayout.addWidget(QLabel(''))
        halfMoveLayout.addWidget(self.halfMoveLabel)
        halfMoveLayout.addWidget(self.halfMoveText)
        halfMoveLayout.addWidget(QLabel(''))
        halfMoveLayout.setAlignment(Qt.AlignHCenter)

        fullMoveLayout = QHBoxLayout()
        self.fullMoveText = QLineEdit()
        self.fullMoveLabel = QLabel('Fullmove count:')
        self.fullMoveText.setValidator(QIntValidator())
        self.fullMoveText.setFixedWidth(self.fullMoveText.width() // 10)
        fullMoveLayout.addWidget(QLabel(''))
        fullMoveLayout.addWidget(self.fullMoveLabel)
        fullMoveLayout.addWidget(self.fullMoveText)
        fullMoveLayout.addWidget(QLabel(''))
        fullMoveLayout.setAlignment(Qt.AlignHCenter)

        settingsLayout.addLayout(enPassantLayout)
        settingsLayout.addLayout(halfMoveLayout)
        settingsLayout.addLayout(fullMoveLayout)

        settingsLayout.setAlignment(Qt.AlignHCenter)
        self.mainLayout.addLayout(settingsLayout)

    def addBoard(self, currentFen):
        self.boardImage = BoardWidget(currentFen, self.boardSquareSize)
        self.mainLayout.addWidget(self.boardImage)

    def addFenLineEdit(self):
        fenLineEditLayout = QHBoxLayout()
        fenLabel = QLabel('FEN: ')
        self.fenLineEdit = QLineEdit()
        self.fenLineEdit.setReadOnly(True)

        fenLineEditLayout.addWidget(fenLabel)
        fenLineEditLayout.addWidget(self.fenLineEdit)
        fenLineEditLayout.setAlignment(Qt.AlignHCenter)

        self.mainLayout.addLayout(fenLineEditLayout)

    def addButtons(self):
        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttons)
        self.mainLayout.addWidget(self.buttonBox)

    def addRightClickMenu(self):
        self.rightClickMenu = QMenu(self)
        self.contextActions = {}
        for piece in PIECES_DICT.values():
            icon = QIcon('resources/pieces/' + piece + '.png')
            self.contextActions[piece]= QAction(icon, '', self)
            self.rightClickMenu.addAction(self.contextActions[piece])
        self.contextActions['e'] = QAction('empty', self)
        self.rightClickMenu.addAction(self.contextActions['e'])

    def addToolTips(self):
        self.perspectiveComboBox.setToolTip(perspectiveHelp)
        self.whiteOO.setToolTip(castelingHelp)
        self.whiteOOO.setToolTip(castelingHelp)
        self.blackOO.setToolTip(castelingHelp)
        self.blackOOO.setToolTip(castelingHelp)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SnipChess")

        self.createActions()
        self.createTrayIcon()
        self.trayIcon.show()

        self.messageDialog = QDialog()
        
    def createActions(self):
        self.snipAction = QAction("Snip", self, triggered=self.snip)
        self.quitAction = QAction('&Quit', self, triggered=QApplication.instance().quit)

    def createTrayIcon(self):
        self.trayIconMenu = QMenu(self)

        self.trayIconMenu.addAction(self.snipAction)
        self.trayIconMenu.addAction(self.quitAction)

        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)

        self.icon = QIcon('resources/icons/wk.png')
        self.trayIcon.setIcon(self.icon)

    def snip(self):
        snipping_tool = SnippingTool()
        snipping_tool.show()
        snipping_tool.exec_()

        self.optsWindow = FenSettingsWindow(snipping_tool.fen)
        self.optsWindow.show()

        if self.optsWindow.exec_():
            self.trayIcon.showMessage('', 'FEN has been successfuly copied to clipboard!',  self.icon, 50 * 1000)


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()
    window.hide()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
