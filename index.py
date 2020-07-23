import sys
import urllib.request

from PyQt5.QtWidgets import QApplication,QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import QRect, QPropertyAnimation
from PyQt5.uic import loadUiType

import pafy
import humanize
import os

ui, _ = loadUiType('main.ui')

class MainApp(QMainWindow, ui):
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.setFixedSize(self.geometry().width(), self.geometry().height())
        self.initUi()
        self.connectButtons()

    def initUi(self):
        self.tabWidget.tabBar().setVisible(False)
        self.animateBoxes()

    def connectButtons(self):
        self.btnDownload.clicked.connect(self.startDownload)
        self.btnBrowseTb1.clicked.connect(self.browse)
        self.btnCheckVdo.clicked.connect(self.getVideoData)
        self.btnBrowseVdoTb2.clicked.connect(self.saveBrowse)
        self.btnOneVdoDownload.clicked.connect(self.downloadSingleYoutubeVideo)
        self.btnPlaylistDownload.clicked.connect(self.downloadPlaylist)
        self.btnPlaylistSaveBrowse.clicked.connect(self.playlistBrowse)
        self.btnHome.clicked.connect(self.homeTab)
        self.btnDownload2.clicked.connect(self.downloadTab)
        self.btnSettings.clicked.connect(self.settingsTab)
        self.btnYoutube.clicked.connect(self.youtubeTab)
        self.btnDarkGray.clicked.connect(self.applyDarkGray)
        self.btnDarkBlue.clicked.connect(self.applyDarkBlue)
        self.btnClassic.clicked.connect(self.applyClassic)


    def handleProgress(self, noOfBlocks, blockSize, totalSize):
        """ Calculate download progress """
        totalDataRead = noOfBlocks * blockSize
        if totalSize > 0:
            percentDownloaded = int(totalDataRead * 100 / totalSize)
            self.progressBarTb1.setValue(percentDownloaded)
            QApplication.processEvents()

    def browse(self):
        saveLocation = QFileDialog.getSaveFileName(self, caption='Save As', directory='.', filter='All Files(*.*)')[0]
        self.lnEdtSvLocationTb1.setText(saveLocation)

    # Download any kind of file
    def startDownload(self):
        print("Download started")

        # pick download url
        downloadUrl = self.lnEdtUrlTb1.text()
        # pick save location
        saveLocation = self.lnEdtSvLocationTb1.text()

        if downloadUrl == '' or saveLocation == '':
            QMessageBox.warning(self, 'Data Error', 'Please provide valid url or save location')
        else:
            try:
                urllib.request.urlretrieve(downloadUrl, saveLocation, self.handleProgress)
            except Exception:
                QMessageBox.warning(self, 'Download Error', 'Bad url or save location')
        QMessageBox(self, 'Success', 'The download completed successfully')
        # reset lineEdits to empty and progress bar to 0
        self.lnEdtSvLocationTb1.setText('')
        self.lnEdtUrlTb1.setText('')
        self.progressBarTb1.setValue(0)

    # Download a single youtube video
    def saveBrowse(self):
        saveLocation = QFileDialog.getSaveFileName(self, caption='Save As', directory='.', filter='All Files(*.*)')[0]
        self.lnEdtVdoSvLocationTb2.setText(saveLocation)

    def getVideoData(self):
        videoUrl = self.lnEdtVdoUrlTb2.text()
        if videoUrl == '':
            QMessageBox(self, 'Data Error', 'Please provide a valid video url')
        else:
            videoDetails = pafy.new(videoUrl)
            print(videoDetails.title)
            print(videoDetails.duration)
            print(videoDetails.author)
            print(videoDetails.length)
            print(videoDetails.viewcount)
            print(videoDetails.likes)
            print(videoDetails.dislikes)

            videoStreams = videoDetails.videostreams
            for stream in videoStreams:
                print(f"size {stream.get_filesize()}")
                size = humanize.naturalsize(stream.get_filesize())
                data = f"{stream.mediatype} {stream.extension} {stream.quality} {size}"
                self.comboBoxTb1.addItem(data)

    def downloadSingleYoutubeVideo(self):
        videoUrl = self.lnEdtVdoUrlTb2.text()
        saveLocation = self.lnEdtVdoSvLocationTb2.text()

        if videoUrl == '' or saveLocation == '':
            QMessageBox(self, 'Data Error', 'Please enter a valid url or save location')
        else:
            video = pafy.new(videoUrl)
            videoStream = video.videostreams
            videoQuality = self.comboBoxTb1.currentIndex()
            download = videoStream[videoQuality].download(filepath=saveLocation, callback=self.youtubeVideoProgress)

    def youtubeVideoProgress(self, totalBytes, receivedBytes, ratioDownloaded, downloadRate, eta):
        if totalBytes > 0:
            percentDownloaded = receivedBytes * 100 / totalBytes;
            self.progressBarVdoTb1.setValue(percentDownloaded)
            remainingTime = round(eta / 60, 2)
            self.lblSingleVdoTimeRemaining.setText(f"{remainingTime} minutes remaining")
            QApplication.processEvents()

    # Playlist Download
    def downloadPlaylist(self):
        playlistUrl = self.lnEdtPlaylistTb2.text()
        saveLocation = self.lnEdtSvPlaylistTb2.text()

        if playlistUrl == '' or saveLocation == '':
            QMessageBox(self, 'Data Error', 'Please provide valid url or save location')
        else:
            playlist = pafy.get_playlist(playlistUrl)
            print(playlist)
            playlistVideos = playlist['items']
            self.playlistLcdNumber.display(len(playlistVideos))

        os.chdir(saveLocation)
        if os.path.exists(str(playlist['title'])):
            os.chdir(str(playlist['title']))
        else:
            os.mkdir(str(playlist['title']))
            os.chdir(str(playlist['title']))

        quality = self.comboBoxPlaylist.currentIndex()
        currentVideoInDownload = 1
        QApplication.processEvents()
        for video in playlistVideos:
            # if video['playlist_meta']['privacy'] == 'public':
            self.currentLcdNumber.display(currentVideoInDownload)
            currentVideo = video['pafy']
            print(currentVideo)
            currentVideoStreams= currentVideo.videostreams
            download = currentVideoStreams[quality].download(callback=self.playlistProgress)
            QApplication.processEvents()
            currentVideoInDownload += 1


    def playlistProgress(self, totalBytes, receivedBytes, ratioDownloaded, downloadRate, eta):
        if totalBytes > 0:
            percentDownloaded = receivedBytes * 100 / totalBytes;
            self.progressBarPlaylist.setValue(int(percentDownloaded))
            remainingTime = round(eta / 60, 2)
            self.lblPlaylistTimeRemaining.setText(f"{remainingTime} minutes remaining")
            QApplication.processEvents()

    def playlistBrowse(self):
        saveLocation = QFileDialog.getExistingDirectory(self, 'Select download directory')
        self.lnEdtSvPlaylistTb2.setText(saveLocation)

    def homeTab(self):
        self.tabWidget.setCurrentIndex(0)

    def settingsTab(self):
        self.tabWidget.setCurrentIndex(3)

    def youtubeTab(self):
        self.tabWidget.setCurrentIndex(2)

    def downloadTab(self):
        self.tabWidget.setCurrentIndex(1)

    def applyDarkGray(self):
        style = open('themes/qdarkgraystyle.css', 'r')
        style = style.read()
        self.setStyleSheet(style)

    def applyDarkBlue(self):
        style = open('themes/qdarkbluestyle.css', 'r')
        style = style.read()
        self.setStyleSheet(style)

    def applyClassic(self):
        self.setStyleSheet('')



    def animateBoxes(self):
        boxAnimation1 = QPropertyAnimation(self.groupBox, b"geometry")
        boxAnimation1.setDuration(1000)
        boxAnimation1.setStartValue(QRect(0,0,0,0))
        boxAnimation1.setEndValue(QRect(29, 40, 261, 111))
        boxAnimation1.start()
        self.boxAnimation1 = boxAnimation1

        boxAnimation2 = QPropertyAnimation(self.groupBox_1, b"geometry")
        boxAnimation2.setDuration(1000)
        boxAnimation2.setStartValue(QRect(0, 0, 0, 0))
        boxAnimation2.setEndValue(QRect(319, 40, 261, 111))
        boxAnimation2.start()
        self.boxAnimation2 = boxAnimation2

        boxAnimation3 = QPropertyAnimation(self.groupBox_2, b"geometry")
        boxAnimation3.setDuration(1000)
        boxAnimation3.setStartValue(QRect(0, 0, 0, 0))
        boxAnimation3.setEndValue(QRect(30, 180, 261, 111))
        boxAnimation3.start()
        self.boxAnimation3 = boxAnimation3

        boxAnimation4 = QPropertyAnimation(self.groupBox_3, b"geometry")
        boxAnimation4.setDuration(1000)
        boxAnimation4.setStartValue(QRect(0, 0, 0, 0))
        boxAnimation4.setEndValue(QRect(320, 180, 261, 111))
        boxAnimation4.start()
        self.boxAnimation4 = boxAnimation4

def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

