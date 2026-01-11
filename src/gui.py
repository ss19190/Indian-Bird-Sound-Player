from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout,
    QStackedWidget, QHBoxLayout
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput


# ---------- GLOBAL BUTTON COLORS ----------
BTN_BG = "#007AFF"
BTN_HOVER = "#0063CC"
BTN_PRESSED = "#004EA2"
BTN_TEXT = "white"


class DropArea(QLabel):
    def __init__(self):
        super().__init__("Drop image here")
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 12px;
                color: #666;
                font-size: 16px;
                padding: 40px;
                background: #fafafa;
            }
        """)
        self.image_path = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        url = event.mimeData().urls()[0]
        self.image_path = url.toLocalFile()
        pixmap = QPixmap(self.image_path).scaled(
            300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.setPixmap(pixmap)


class MainPage(QWidget):
    def __init__(self, on_evaluate):
        super().__init__()
        self.drop_area = DropArea()

        self.evaluate_btn = QPushButton("Evaluate")
        self.evaluate_btn.clicked.connect(
            lambda: on_evaluate(self.drop_area.image_path)
        )
        self.evaluate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BTN_BG};
                color: {BTN_TEXT};
                padding: 14px;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {BTN_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {BTN_PRESSED};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.addWidget(self.drop_area)
        layout.addWidget(self.evaluate_btn)


class ResultPage(QWidget):
    def __init__(self, on_back):
        super().__init__()

        # ---------- BACK BUTTON ----------
        self.back_btn = QPushButton("←")
        self.back_btn.setFixedSize(38, 38)
        self.back_btn.clicked.connect(on_back)
        self.back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #004a99;
                color: {BTN_TEXT};
                font-size: 18px;
                border-radius: 12px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {BTN_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {BTN_PRESSED};
            }}
        """)

        # ---------- TOP BAR ----------
        top_bar = QHBoxLayout()
        top_bar.addWidget(self.back_btn)
        top_bar.addStretch()
        top_bar.setContentsMargins(12, 12, 0, 0)

        # ---------- CONTENT ----------
        self.image_label = QLabel(alignment=Qt.AlignCenter)

        self.result_label = QLabel("Result: ---", alignment=Qt.AlignCenter)
        self.result_label.setStyleSheet("""
            font-size: 18px;
            color: #111827;
        """)

        # ---------- AUDIO ----------
        self.player = QMediaPlayer()
        self.audio = QAudioOutput()
        self.player.setAudioOutput(self.audio)

        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(56, 56)
        self.play_btn.clicked.connect(self.player.play)
        self.play_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BTN_BG};
                color: {BTN_TEXT};
                font-size: 22px;
                border-radius: 14px;
            }}
            QPushButton:hover {{
                background-color: {BTN_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {BTN_PRESSED};
            }}
        """)

        # ---------- MAIN LAYOUT ----------
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(top_bar)
        main_layout.addSpacing(8)
        main_layout.addWidget(self.image_label)
        main_layout.addSpacing(12)
        main_layout.addWidget(self.result_label)
        main_layout.addSpacing(24)
        main_layout.addWidget(self.play_btn, alignment=Qt.AlignCenter)
        main_layout.addStretch()

    def set_result(self, image_path, result_text, audio_path):
        pixmap = QPixmap(image_path).scaled(
            300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.image_label.setPixmap(pixmap)
        self.result_label.setText(result_text)
        self.player.setSource(QUrl.fromLocalFile(audio_path))


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Evaluation App")
        self.resize(420, 600)

        self.stack = QStackedWidget()

        self.main_page = MainPage(self.evaluate)
        self.result_page = ResultPage(self.go_back)

        self.stack.addWidget(self.main_page)
        self.stack.addWidget(self.result_page)

        layout = QVBoxLayout(self)
        layout.addWidget(self.stack)

    def evaluate(self, image_path):
        if not image_path:
            return

        result_text = "Evaluation: OK"
        audio_path = "example.wav"

        self.result_page.set_result(image_path, result_text, audio_path)
        self.stack.setCurrentWidget(self.result_page)

    def go_back(self):
        self.stack.setCurrentWidget(self.main_page)
