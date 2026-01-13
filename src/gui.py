from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout,
    QStackedWidget, QHBoxLayout
)
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor
from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from src.detection import BirdDetector
from src.audio_manager import AudioManager

# ---------- GLOBAL STYLES ----------
BTN_BG = "#007AFF"
BTN_HOVER = "#0063CC"
BTN_PRESSED = "#004EA2"
BTN_TEXT = "white"

class DropArea(QLabel):
    file_dropped = Signal(str)

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
        file_path = url.toLocalFile()
        self.image_path = file_path
        self.file_dropped.emit(file_path)

class MainPage(QWidget):
    def __init__(self, detector, on_evaluate):
        super().__init__()
        self.detector = detector
        self.on_evaluate = on_evaluate
        self.current_bbox = None 

        self.drop_area = DropArea()
        self.drop_area.file_dropped.connect(self.handle_image_drop)

        # Label do wyświetlania dokładności detekcji (YOLO)
        self.detection_info = QLabel("")
        self.detection_info.setAlignment(Qt.AlignCenter)
        self.detection_info.setStyleSheet("color: #555; font-size: 14px; margin-top: 5px;")

        self.evaluate_btn = QPushButton("Evaluate Species")
        self.evaluate_btn.clicked.connect(self.trigger_evaluation)
        self.evaluate_btn.setEnabled(False) 

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
            QPushButton:disabled {{
                background-color: #cccccc;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.addWidget(self.drop_area)
        layout.addWidget(self.detection_info) # Dodajemy label pod zdjęciem
        layout.addWidget(self.evaluate_btn)

    def handle_image_drop(self, file_path):
        original_pixmap = QPixmap(file_path)
        
        # Detekcja (zwraca teraz też confidence)
        bbox, conf = self.detector.detect_bbox(file_path)
        self.current_bbox = bbox

        # Rysowanie ramki
        if bbox is not None:
            x1, y1, x2, y2 = bbox
            painter = QPainter(original_pixmap)
            pen = QPen(QColor("#00FF00")) # Zielony
            pen.setWidth(5)
            painter.setPen(pen)
            painter.drawRect(int(x1), int(y1), int(x2-x1), int(y2-y1))
            painter.end()
            
            # Wyświetlamy accuracy detekcji
            self.detection_info.setText(f"Bird detected! (Confidence: {conf:.2%})")
            self.detection_info.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.detection_info.setText("No bird detected (Manual mode)")
            self.detection_info.setStyleSheet("color: orange;")

        scaled_pixmap = original_pixmap.scaled(
            400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.drop_area.setPixmap(scaled_pixmap)
        self.evaluate_btn.setEnabled(True)

    def trigger_evaluation(self):
        if self.drop_area.image_path:
            self.on_evaluate(self.drop_area.image_path, self.current_bbox)


class ResultPage(QWidget):
    def __init__(self, on_back):
        super().__init__()

        self.back_btn = QPushButton("← Back")
        self.back_btn.setFixedSize(80, 38)
        self.back_btn.clicked.connect(on_back)
        self.back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #004a99;
                color: {BTN_TEXT};
                font-size: 14px;
                border-radius: 12px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {BTN_HOVER};
            }}
        """)

        top_bar = QHBoxLayout()
        top_bar.addWidget(self.back_btn)
        top_bar.addStretch()
        top_bar.setContentsMargins(12, 12, 0, 0)

        self.image_label = QLabel(alignment=Qt.AlignCenter)

        self.result_label = QLabel("Result: ---", alignment=Qt.AlignCenter)
        self.result_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #111827;
        """)

        # Label dla accuracy klasyfikacji
        self.accuracy_label = QLabel("", alignment=Qt.AlignCenter)
        self.accuracy_label.setStyleSheet("color: #666; font-size: 16px;")

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        self.play_btn = QPushButton("▶ Play Sound")
        self.play_btn.setFixedSize(200, 56)
        self.play_btn.clicked.connect(self.player.play)
        self.play_btn.setEnabled(False)
        self.play_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BTN_BG};
                color: {BTN_TEXT};
                font-size: 18px;
                border-radius: 14px;
            }}
            QPushButton:hover {{
                background-color: {BTN_HOVER};
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(top_bar)
        main_layout.addSpacing(8)
        main_layout.addWidget(self.image_label)
        main_layout.addSpacing(12)
        main_layout.addWidget(self.result_label)
        main_layout.addWidget(self.accuracy_label) # Dodane accuracy pod nazwą
        main_layout.addSpacing(24)
        main_layout.addWidget(self.play_btn, alignment=Qt.AlignCenter)
        main_layout.addStretch()

    def set_result(self, image_path, result_text, confidence, audio_path):
        pixmap = QPixmap(image_path).scaled(
            300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.image_label.setPixmap(pixmap)
        
        self.result_label.setText(f"{result_text}")
        
        # Wyświetlamy accuracy klasyfikacji
        self.accuracy_label.setText(f"Model Confidence: {confidence:.2%}")
        
        if audio_path:
            self.player.setSource(QUrl.fromLocalFile(audio_path))
            self.audio_output.setVolume(1.0)
            self.play_btn.setEnabled(True)
            self.play_btn.setText("▶ Play Sound")
        else:
            self.play_btn.setEnabled(False)
            self.play_btn.setText("No Audio Available")


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Indian Bird Species Detector")
        self.resize(450, 650)

        self.detector = BirdDetector()
        self.audio_manager = AudioManager()

        self.stack = QStackedWidget()

        self.main_page = MainPage(self.detector, self.evaluate_logic)
        self.result_page = ResultPage(self.go_back)

        self.stack.addWidget(self.main_page)
        self.stack.addWidget(self.result_page)

        layout = QVBoxLayout(self)
        layout.addWidget(self.stack)

    def evaluate_logic(self, image_path, bbox):
        if not image_path:
            return

        # 1. Klasyfikacja (zwraca teraz też confidence)
        species_name, conf = self.detector.classify_species(image_path, bbox)
        
        # 2. Audio
        audio_path = self.audio_manager.get_audio_path(species_name)

        # 3. Wyświetlenie
        self.result_page.set_result(image_path, species_name, conf, audio_path)
        self.stack.setCurrentWidget(self.result_page)

    def go_back(self):
        self.stack.setCurrentWidget(self.main_page)
        self.result_page.player.stop()
