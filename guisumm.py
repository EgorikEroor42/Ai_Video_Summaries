from faster_whisper import WhisperModel
import glob
import os
from pathlib import Path
from PySide6.QtCore import QObject,Qt,QThread,Signal,Slot
from PySide6.QtWidgets import QApplication,QComboBox,QHBoxLayout,QLabel,QLineEdit,QPushButton,QSizePolicy,QVBoxLayout,QWidget
import sys
import yt_dlp

models = {'1':'tiny','2':'base','3':'small','4':'medium','5':'large-v3'}
class Signals(QObject):
    progress = Signal(str)
    result = Signal(str)
    finished = Signal()

    def __init__(self,url,quality):
        super().__init__()
        self.url = url
        self.quality = quality

    @Slot()
    def summ(self):
        self.progress.emit('Installing the selected AI-model...')
        model = WhisperModel(self.quality)
        self.progress.emit('Loading video from URL...')
        try:
            yt_dlp.YoutubeDL({'format': 'bestaudio/best', 'outtmpl': f'downvid/vid.%(ext)s', 'verbose': True}).download([self.url])
        except yt_dlp.utils.DownloadError:
            self.progress.emit('Enter a valid URL.')
            self.finished.emit()
            return
        foundvideo = list(Path('downvid').glob('vid.*'))[0]
        if not foundvideo:
            self.progress.emit('File not found.')
            self.finished.emit()
            return
        self.progress.emit('Video transcription...')
        parts_text, info = model.transcribe(foundvideo)
        text = ''.join(part_text.text for part_text in parts_text)
        self.progress.emit('Cleaning temporary files...')
        foundvideo.unlink()
        self.progress.emit('Creating a summary...')
        self.progress.emit('')
        self.result.emit('')
        self.finished.emit()

class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("A brief summary of the video.")
        self.resize(500,400)

        self.lineedit = QLineEdit()
        self.slidingwindow = QComboBox()
        self.descript = QLabel('1 - Highest speed with low accuracy.\n2 - High speed with medium accuracy.\n3 - Average speed with good accuracy.\n4 - Slow speed with highest accuracy.\n5 - Lowest speed with maximum accuracy.\nThe speed of AI summation depends on the components of your computer.')
        self.summbutt = QPushButton('Summarize')
        self.infosumm = QLabel('')
        self.briefsumm = QLabel('')

        self.lineedit.setFixedSize(480,20)
        self.slidingwindow.setFixedSize(200,20)
        self.slidingwindow.addItem('Select transcription quality')
        self.slidingwindow.addItems(['1', '2', '3', '4', '5'])
        self.slidingwindow.model().item(0).setEnabled(False)
        self.summbutt.setFixedSize(100,20)
        self.summbutt.clicked.connect(self.track_summbutt)
        self.briefsumm.setWordWrap(True)
        self.briefsumm.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        y = QVBoxLayout()
        x1 = QHBoxLayout()
        x2 = QHBoxLayout()

        y.addWidget(self.lineedit)
        x1.addWidget(self.slidingwindow,alignment=Qt.AlignTop)
        x1.addWidget(self.descript,alignment=Qt.AlignTop)
        y.addLayout(x1)
        x2.addWidget(self.summbutt)
        x2.addWidget(self.infosumm)
        y.addLayout(x2)
        y.addWidget(self.briefsumm)
        y.addStretch()

        self.setLayout(y)

    def track_summbutt(self):
        url = self.lineedit.text()
        modqua = self.slidingwindow.currentText()
        if not url and modqua not in models:
            self.infosumm.setText('Enter URL.\nSelect AI-model.')
            return
        if not url:
            self.infosumm.setText('Enter URL.')
            return
        if modqua not in models:
            self.infosumm.setText('Select AI-model.')
            return

        self.summbutt.setEnabled(False)
        self.slidingwindow.setEnabled(False)
        self.lineedit.setEnabled(False)
        self.briefsumm.setText('')
        self.infosumm.setText('Deleting the contents of a folder...')
        videos = glob.glob('downvid/*')
        for video in videos:
            os.remove(video)

        self.thread = QThread()
        self.signal = Signals(url,models[modqua])
        self.signal.moveToThread(self.thread)

        self.thread.started.connect(self.signal.summ)
        self.signal.progress.connect(self.infosumm.setText)
        self.signal.result.connect(self.briefsumm.setText)

        self.signal.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.signal.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.cleanup)

        self.thread.start()

    def cleanup(self):
        self.summbutt.setEnabled(True)
        self.slidingwindow.setEnabled(True)
        self.lineedit.setEnabled(True)
        self.thread = None
        self.signal = None

app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())