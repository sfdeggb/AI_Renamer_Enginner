import sys
import os
import concurrent.futures
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal, QThread
from collections import Counter
import pandas as pd

from text_processor import process_text_file
from vedio_processor import process_video_file
from image_processor import process_image


class MainLogicThread(QThread):
    output_text_signal = pyqtSignal(str)

    def __init__(self, config, parent=None):
        super(MainLogicThread, self).__init__(parent)
        self.config = config
        self.stop_event = False
        self.success_counter = Counter()
        self.failure_counter = Counter()
        self.num_counter = Counter()
        self.active_counter = Counter()

    def run(self):
        self.process_files_concurrently()

    def process_files_concurrently(self):
        source_folder = self.config["Source_folder"]
        text_suffixes = ('.txt', '.docx', '.xls', '.xlsx', '.pdf', '.md')
        video_suffixes = ('.mp4', '.mov', '.avi', '.flv', '.mkv')
        image_suffixes = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.heif', '.heic', '.svg')
        file_paths = []
        max_workers = 5

        for root, dirs, files in os.walk(source_folder):
            dirs[:] = [d for d in dirs if d != '.airenametmp']
            for filename in files:
                if filename.lower().endswith(text_suffixes + video_suffixes+image_suffixes):
                    file_path = os.path.join(root, filename)
                    file_paths.append(file_path)

        self.output_text_signal.emit(f"开始处理{len(file_paths)}个文件，线程:{max_workers}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for file_path in file_paths:
                if file_path.lower().endswith(text_suffixes):
                    future = executor.submit(process_text_file, file_path)
                elif file_path.lower().endswith(video_suffixes):
                    future = executor.submit(process_video_file, file_path)
                elif file_path.lower().endswith(image_suffixes):
                    future = executor.submit(process_image_file, file_path)
                else:
                    continue
                futures.append(future)
            for future in concurrent.futures.as_completed(futures):
                if self.stop_event:
                    break
                try:
                    future.result()
                except Exception as exc:
                    self.output_text_signal.emit(f'生成异常: {exc}')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('AI_RENAME_TOOL')
        self.setGeometry(100, 100, 800, 600)

        self.textEdit = QTextEdit(self)
        self.startButton = QPushButton('开始处理', self)
        self.startButton.clicked.connect(self.start_processing)

        layout = QVBoxLayout()
        layout.addWidget(self.textEdit)
        layout.addWidget(self.startButton)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_processing(self):
        config = {"Source_folder": "path/to/your/source_folder"}
        self.thread = MainLogicThread(config)
        self.thread.output_text_signal.connect(self.update_text)
        self.thread.start()

    def update_text(self, text):
        self.textEdit.append(text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())