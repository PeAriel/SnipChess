import sys
from time import sleep
from PyQt5.QtCore import QRect

from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QComboBox,
                            QLabel, QDialog, QDialogButtonBox, QPushButton,
                            QSystemTrayIcon, QLineEdit, QMainWindow, QMenu,
                            QHBoxLayout, QVBoxLayout, QGridLayout
                            )
from numpy import array

from utils import SnippingTool, BoardWidget
from fen2png import DrawBoard


class FenSettingsWindow(QDialog):
    def __init__(self, fen):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowState(Qt.WindowState.WindowActive)
        # self.setFixedSize(QSize(735, 557))

        self.setWindowTitle('FEN Settings')
        # self.setModal(True)
        self.mainLayout = QVBoxLayout()

        self.origFen = fen
        self.fen = fen
        self.fenSpecs = ['' if i % 2 != 0 else ' ' for i in range(10)]
        self.fenSpecs[1] = 'w'
        self.fenSpecs[3] = 'KQkq'
        self.boardSquareSize = 40

        self.addHowPlays()
        self.addCasteling()
        self.addBoard(fen)
        self.addFenLineEdit()
        self.addButtons()

        self.whoPlaysComboBox.currentIndexChanged.connect(self.configChanged)
        self.whiteOO.stateChanged.connect(self.configChanged)
        self.whiteOOO.stateChanged.connect(self.configChanged)
        self.blackOO.stateChanged.connect(self.configChanged)
        self.blackOOO.stateChanged.connect(self.configChanged)

        self.configChanged()
        self.fenLineEdit.setText(self.origFen + ''.join(self.fenSpecs))

        self.buttonBox.accepted.connect(self.okPressed)
        self.buttonBox.rejected.connect(self.reject)

        self.testLabel0 = QLabel()
        self.testLabel1 = QLabel()
        self.testLabel2 = QLabel()
        self.boardImage.setMouseTracking(True)
        self.mainLayout.addWidget(self.testLabel0)
        self.boardImage.moved.connect(self.testCoords)
        self.boardImage.leftClick.connect(self.testLeftClick)

        self.setLayout(self.mainLayout)

    def testLeftClick(self, lclickx, lclicky):
        print('left click coordinates:', lclickx, lclicky)

    def testCoords(self, x0, y0):
        self.testLabel0.setText('event: %.2f, %.2f' % (x0, y0))

    def okPressed(self):
        self.accept()
        
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(self.fen, mode=cb.Clipboard)

        self.close()

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
            
        self.fen = self.origFen + ''.join(self.fenSpecs)
        self.fenLineEdit.setText(self.fen)

    def updateFenAndBoard(self):
        self.fen = self.fenLineEdit.text()
        board = DrawBoard(self.fen)
        self.boardImage.setPixmap(board.boardQPixmap())

    def addHowPlays(self):
        self.whoPlaysComboBox = QComboBox()
        self.whoPlaysComboBox.addItem('White to play')
        self.whoPlaysComboBox.addItem('Black to play')
        self.mainLayout.addWidget(self.whoPlaysComboBox)

    def addCasteling(self):
        castelingLayout = QHBoxLayout()
        whiteLayout = QVBoxLayout()
        blackLayout = QVBoxLayout()
        questionLayout = QVBoxLayout()

        questionWidget = QLabel('?')
        questionWidget.setToolTip('These buttons specifies if casteling is still a possibility.\n'
                                   'Uncheck both if O-O and O-O-O if a player has already casteled.')

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
        questionLayout.addWidget(questionWidget)
        questionLayout.addWidget(QLabel(''))
        questionLayout.addWidget(QLabel(''))

        castelingLayout.addLayout(whiteLayout)
        castelingLayout.addLayout(blackLayout)
        castelingLayout.addLayout(questionLayout)
        castelingLayout.setAlignment(Qt.AlignHCenter)

        self.mainLayout.addLayout(castelingLayout)

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


