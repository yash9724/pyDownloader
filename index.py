import sys
import urllib.request

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
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
        self.initUi();
        self.connectButtons()

    def initUi(self):
        pass

    def connectButtons(self):
        self.btnDownload.clicked.connect(self.startDownload)
        self.btnBrowseTb1.clicked.connect(self.browse)
        self.btnCheckVdo.clicked.connect(self.getVideoData)
        self.btnBrowseVdoTb2.clicked.connect(self.saveBrowse)
        self.btnOneVdoDownload.clicked.connect(self.downloadSingleYoutubeVideo)
        self.btnPlaylistDownload.clicked.connect(self.downloadPlaylist)
        self.btnPlaylistSaveBrowse.clicked.connect(self.playlistBrowse)

    def handleProgress(self, noOfBlocks, blockSize, totalSize):
        """ Calculate download progress"""
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




def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

# {'playlist_id': 'PLZoTAELRMXVNxYFq_9MuiUdn2YnlFqmMK', 'likes': None, 'title': 'Pytorch', 'author': 'Krish Naik',
#  'dislikes': None, 'description': '',
#  'items': [{'pafy': Pafy object: U0i7 - c3Vrgc[Pytorch Tutorial 1 - Pytorch Installation For D..],
#  'playlist_meta': {'added': '12/07/2020', 'is_cc': False, 'is_hd': True, 'likes': 271,
#                    'title': 'Pytorch Tutorial 1-Pytorch Installation For Deep Learning', 'views': '5,256',
#                    'rating': 4.0, 'author': 'Krish Naik', 'user_id': 'NU_lfiiWBdtULKOw6X0Dig', 'privacy': 'public',
#                    'start': 0.0, 'dislikes': 2, 'duration': '15:02', 'comments': '42',
#                    'keywords': '"pytorch tutorial pdf" "pytorch tutorial for beginners" "pytorch examples" "tensorflow tutorial" "pytorch computer vision tutorial" "deep learning with pytorch" "pytorch documentation" "pytorch projects for beginners"',
#                    'thumbnail': 'https://i.ytimg.com/vi/U0i7-c3Vrgc/default.jpg', 'cc_license': False,
#                    'category_id': 27,
#                    'description': "PyTorch is an open source machine learning library based on the Torch library,used for applications such as computer vision and natural language processing,primarily developed by Facebook's AI Research lab (FAIR).It is free and open-source software released under the Modified BSD license. Although the Python interface is more polished and the primary focus of development, PyTorch also has a C++ interface.\n\nA number of pieces of Deep Learning software are built on top of PyTorch, including Tesla, Uber's Pyro, HuggingFace's Transformers, PyTorch Lightning, and Catalyst.\n\nPyTorch provides two high-level features:\n\nTensor computing (like NumPy) with strong acceleration via graphics processing units (GPU)\nDeep neural networks built on a tape-based automatic differentiation system\ngithub: https://github.com/krishnaik06/Pytorch-Tutorial",
#                    'encrypted_id': 'U0i7-c3Vrgc', 'time_created': 1594559943, 'time_updated': None,
#                    'length_seconds': 902, 'end': 902}}, {'pafy': Pafy object: 3XA4ojhq44Q[Pytorch Tutorial
#                                                          2 - Understanding Of Tensors U..], 'playlist_meta': {
#     'added': '14/07/2020', 'is_cc': False, 'is_hd': True, 'likes': 127,
#     'title': 'Pytorch Tutorial 2-Understanding Of Tensors Using Pytorch', 'views': '2,572', 'rating': 4.0,
#     'author': 'Krish Naik', 'user_id': 'NU_lfiiWBdtULKOw6X0Dig', 'privacy': 'public', 'start': 0.0, 'dislikes': 3,
#     'duration': '16:17', 'comments': '24',
#     'keywords': '"pytorch tutorial pdf" "pytorch tutorial for beginners" "pytorch examples" "tensorflow tutorial" "pytorch computer vision tutorial" "deep learning with pytorch" "pytorch documentation" "pytorch projects for beginners"',
#     'thumbnail': 'https://i.ytimg.com/vi/3XA4ojhq44Q/default.jpg', 'cc_license': False, 'category_id': 27,
#     'description': "PyTorch is an open source machine learning library based on the Torch library,used for applications such as computer vision and natural language processing,primarily developed by Facebook's AI Research lab (FAIR).It is free and open-source software released under the Modified BSD license. Although the Python interface is more polished and the primary focus of development, PyTorch also has a C++ interface.\ngithub: https://github.com/krishnaik06/Pytorch-Tutorial\nPytorch Playlist: https://www.youtube.com/playlist?list=PLZoTAELRMXVNxYFq_9MuiUdn2YnlFqmMK\ngithub: https://github.com/krishnaik06/Pytorch-Tutorial\n\nDL Playlist: https://www.youtube.com/watch?v=DKSZHN7jftI&list=PLZoTAELRMXVPGU70ZGsckrMdr0FteeRUi\n\nA number of pieces of Deep Learning software are built on top of PyTorch, including Tesla, Uber's Pyro, HuggingFace's Transformers, PyTorch Lightning, and Catalyst.\n\nPyTorch provides two high-level features:\n\nTensor computing (like NumPy) with strong acceleration via graphics processing units (GPU)\nDeep neural networks built on a tape-based automatic differentiation system\ngithub: https://github.com/krishnaik06/Pytorch-Tutorial",
#     'encrypted_id': '3XA4ojhq44Q', 'time_created': 1594717241, 'time_updated': None, 'length_seconds': 977,
#     'end': 977}}, {'pafy': Pafy object: igypbt686zI[Pytorch TutoriaL 3 - How To Perform
#                    BackPropoga..], 'playlist_meta': {'added': '17/07/2020', 'is_cc': False, 'is_hd': True, 'likes': 52,
#                                                      'title': 'Pytorch TutoriaL 3-How To Perform BackPropogation Using Pytorch',
#                                                      'views': '1,065', 'rating': 4.0, 'author': 'Krish Naik',
#                                                      'user_id': 'NU_lfiiWBdtULKOw6X0Dig', 'privacy': 'public',
#                                                      'start': 0.0, 'dislikes': 1, 'duration': '15:51', 'comments': '13',
#                                                      'keywords': '"pytorch tutorial pdf" "pytorch tutorial for beginners" "pytorch examples" "tensorflow tutorial" "pytorch computer vision tutorial" "deep learning with pytorch" "pytorch documentation" "pytorch projects for beginners"',
#                                                      'thumbnail': 'https://i.ytimg.com/vi/igypbt686zI/default.jpg',
#                                                      'cc_license': False, 'category_id': 27,
#                                                      'description': "Reuploaded in HD format\nPyTorch is an open source machine learning library based on the Torch library,used for applications such as computer vision and natural language processing,primarily developed by Facebook's AI Research lab (FAIR).It is free and open-source software released under the Modified BSD license. Although the Python interface is more polished and the primary focus of development, PyTorch also has a C++ interface.\nPytorch Playlist: https://www.youtube.com/playlist?list=PLZoTAELRMXVNxYFq_9MuiUdn2YnlFqmMK\ngithub: https://github.com/krishnaik06/Pytorch-Tutorial\n\nA number of pieces of Deep Learning software are built on top of PyTorch, including Tesla, Uber's Pyro, HuggingFace's Transformers, PyTorch Lightning, and Catalyst.\n\nPyTorch provides two high-level features:\n\nTensor computing (like NumPy) with strong acceleration via graphics processing units (GPU)\nDeep neural networks built on a tape-based automatic differentiation system\ngithub: https://github.com/krishnaik06/Pytorch-Tutorial",
#                                                      'encrypted_id': 'igypbt686zI', 'time_created': 1594971699,
#                                                      'time_updated': None, 'length_seconds': 951, 'end': 951}}, {
#     'pafy': Pafy object: oSHwZG4X3Zo[Tutorial 4 - Solving Kaggle Pima Diabetes Pred..], 'playlist_meta': {
#     'added': '19/07/2020', 'is_cc': False, 'is_hd': True, 'likes': 16,
#     'title': 'Tutorial 4- Solving Kaggle Pima Diabetes Prediction Using ANN With PyTorch Library', 'views': '1',
#     'rating': 5.0, 'author': 'Krish Naik', 'user_id': 'NU_lfiiWBdtULKOw6X0Dig', 'privacy': 'public', 'start': 0.0,
#     'dislikes': 0, 'duration': '40:58', 'comments': '1',
#     'keywords': '"pytorch tutorial pdf" "pytorch tutorial for beginners" "pytorch examples" "tensorflow tutorial" "pytorch computer vision tutorial" "deep learning with pytorch" "pytorch documentation" "pytorch projects for beginners"',
#     'thumbnail': 'https://i.ytimg.com/vi/oSHwZG4X3Zo/default.jpg', 'cc_license': False, 'category_id': 27,
#     'description': "PyTorch is an open source machine learning library based on the Torch library,used for applications such as computer vision and natural language processing,primarily developed by Facebook's AI Research lab (FAIR).It is free and open-source software released under the Modified BSD license. Although the Python interface is more polished and the primary focus of development, PyTorch also has a C++ interface.\ngithub: https://github.com/krishnaik06/Pytorch-Tutorial\nPytorch Playlist: https://www.youtube.com/playlist?list=PLZoTAELRMXVNxYFq_9MuiUdn2YnlFqmMK\n\n\nA number of pieces of Deep Learning software are built on top of PyTorch, including Tesla, Uber's Pyro, HuggingFace's Transformers, PyTorch Lightning, and Catalyst.\n\nPyTorch provides two high-level features:\n\nTensor computing (like NumPy) with strong acceleration via graphics processing units (GPU)\nDeep neural networks built on a tape-based automatic differentiation system\ngithub: https://github.com/krishnaik06/Pytorch-Tutorial",
#     'encrypted_id': 'oSHwZG4X3Zo', 'time_created': 1594972553, 'time_updated': None, 'length_seconds': 2458,
#     'end': 2458}}]}
