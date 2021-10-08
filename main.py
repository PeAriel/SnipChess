import sys
from PyQt5.QtCore import QRect

from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QComboBox,
                            QLabel, QDialog, QDialogButtonBox, QPushButton,
                            QSystemTrayIcon, QLineEdit, QMainWindow, QMenu,
                            QHBoxLayout, QVBoxLayout, QGridLayout
                            )

from utils import SnippingTool
from fen2png import DrawBoard


class FenOptionsWindow(QDialog):
    def __init__(self, fen):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowState(Qt.WindowState.WindowActive)

        self.setWindowTitle('Additional Options')
        # self.setModal(True)
        self.mainLayout = QVBoxLayout()

        self.origFen = fen
        self.fen = fen
        self.fenSpecs = ['' if i % 2 != 0 else ' ' for i in range(10)]
        self.fenSpecs[1] = 'w'
        self.fenSpecs[3] = 'KQkq'

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
        self.fenUpdateButton.clicked.connect(self.updateFenAndBoard)

        self.buttonBox.accepted.connect(self.okPressed)
        self.buttonBox.rejected.connect(self.reject)

        self.setLayout(self.mainLayout)

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
        self.boardLabel.setPixmap(board.boardQPixmap())

    def addFenLineEdit(self):
        fenLineEditLayout = QHBoxLayout()
        fenLabel = QLabel('FEN: ')
        self.fenLineEdit = QLineEdit()
        self.fenUpdateButton = QPushButton('Update FEN')
        fenLineEditLayout.addWidget(fenLabel)
        fenLineEditLayout.addWidget(self.fenLineEdit)
        fenLineEditLayout.addWidget(self.fenUpdateButton)
        self.mainLayout.addLayout(fenLineEditLayout)

    def addHowPlays(self):
        self.whoPlaysComboBox = QComboBox()
        self.whoPlaysComboBox.addItem('White to play')
        self.whoPlaysComboBox.addItem('Black to play')
        self.mainLayout.addWidget(self.whoPlaysComboBox)
        
    def addButtons(self):
        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttons)
        self.mainLayout.addWidget(self.buttonBox)

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

        self.mainLayout.addLayout(castelingLayout)

    def addBoard(self, currentFen):
        self.boardLabel = QLabel()
        board = DrawBoard(currentFen)
        self.boardLabel.setPixmap(board.boardQPixmap())
        self.mainLayout.addWidget(self.boardLabel)


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

        self.optsWindow = FenOptionsWindow(snipping_tool.fen)
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


