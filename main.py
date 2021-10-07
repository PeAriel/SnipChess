import sys
from PyQt5.QtCore import QRect

from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QComboBox,
                            QLabel, QDialog, QDialogButtonBox,
                            QSystemTrayIcon, QLineEdit, QMainWindow, QMenu,
                            QHBoxLayout, QVBoxLayout, QGridLayout
                            )

from utils import SnippingTool


class FenOptionsWindow(QDialog):
    def __init__(self, fen):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowState(Qt.WindowState.WindowActive)

        self.fen = fen

        self.setWindowTitle('Additional Options')
        self.setModal(True)
        self.mainLayout = QVBoxLayout()

        self.addHowPlays()
        self.addCasteling()
        self.addFenLineEdit()
        self.addButtons()

        self.fenLineEdit.setText(self.fen)

        self.buttonBox.accepted.connect(self.okPressed)
        self.buttonBox.rejected.connect(self.reject)

        self.setLayout(self.mainLayout)

    def okPressed(self):
        self.accept()
        if self.whoPlaysComboBox.currentIndex() == 0:
            self.fen += ' w'
        else:
            self.fen += ' b'
        
        castlingFen = []
        if all([self.whiteOO.isChecked(),
                self.whiteOOO.isChecked(),
                self.blackOO.isChecked(),
                self.blackOOO.isChecked()]):
            self.fen += ' -'
        else:
            castlingFen.append(' ')
            if self.whiteOO.isChecked():
                castlingFen.append('K')
            if self.whiteOOO.isChecked():
                castlingFen.append('Q')
            if self.blackOO.isChecked():
                castlingFen.append('k')
            if self.blackOOO.isChecked():
                castlingFen.append('q')
            self.fen += ''.join(castlingFen)
        
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(self.fen, mode=cb.Clipboard)

        self.close()

    def addFenLineEdit(self):
        fenLineEditLayout = QHBoxLayout()
        fenLabel = QLabel('FEN: ')
        self.fenLineEdit = QLineEdit()
        fenLineEditLayout.addWidget(fenLabel)
        fenLineEditLayout.addWidget(self.fenLineEdit)
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
        whiteLayout = QGridLayout()
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

        whiteLayout.addWidget(QLabel('White'), 0, 0)
        whiteLayout.addWidget(self.whiteOO, 1, 0)
        whiteLayout.addWidget(self.whiteOOO, 2, 0)
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


