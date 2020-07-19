import sys
import urllib.request

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.uic import loadUiType


ui, _ = loadUiType('main.ui')
class MainApp(QMainWindow, ui):
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.initUi();
        self.connectButtons()

    def initUi(self):
        pass

    def connectButtons(self):
        self.btnDownload.clicked.connect(self.startDownload)
        self.btnBrowseTb1.clicked.connect(self.browse)

    def handleProgress(self, noOfBlocks, blockSize, totalSize):
        """ Calculate download progress"""
        totalDataRead = noOfBlocks * blockSize
        if totalSize > 0:
            percentDownloaded = int(totalDataRead * 100 / totalSize)
            self.progressBarTb1.setValue(percentDownloaded)
            QApplication.processEvents()

    def browse(self):
        save_location = QFileDialog.getSaveFileName(self, caption='Save As', directory='.', filter='All Files(*.*)')[0]
        self.lnEdtSvLocationTb1.setText(save_location)

    def startDownload(self):
        print("Download started")

        # pick download url
        download_url = self.lnEdtUrlTb1.text()
        # pick save location
        save_location = self.lnEdtSvLocationTb1.text()

        if download_url == '' or save_location =='':
            QMessageBox.warning(self, 'Data Error', 'Please provide valid url or save location')
        else:
            try:
                urllib.request.urlretrieve(download_url, save_location, self.handleProgress)
            except Exception:
                QMessageBox.warning(self, 'Download Error', 'Bad url or save location')
        QMessageBox(self, 'Success', 'The download completed successfully')
        # reset lineEdits to empty and progress bar to 0
        self.lnEdtSvLocationTb1.setText('')
        self.lnEdtUrlTb1.setText('')
        self.progressBarTb1.setValue(0)

    def save_browse(self):
        pass

def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
