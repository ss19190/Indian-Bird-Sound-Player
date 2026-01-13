from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout,
    QStackedWidget, QHBoxLayout
)
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor
from PySide6.QtCore import Qt, QUrl, Signal, QObject
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from src.detection import BirdDetector
from src.audio_manager import AudioManager

# ---------- GLOBAL BUTTON COLORS ----------
BTN_BG = "#007AFF"
BTN_HOVER = "#0063CC"
BTN_PRESSED = "#004EA2"
BTN_TEXT = "white"

class DropArea(QLabel):
    # Sygnał wysyłany po upuszczeniu pliku: ścieżka do pliku
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
        # Emitujemy sygnał do MainPage, żeby obsłużył detekcję
        self.file_dropped.emit(file_path)

    def display_image_with_box(self, pixmap, bbox=None):
        """
        Rysuje bounding box na obrazku jeśli bbox jest podany.
        bbox format: [x1, y1, x2, y2]
        """
        final_pixmap = pixmap.copy()
        
        if bbox is not None:
            painter = QPainter(final_pixmap)
            pen = QPen(QColor("red"))
            pen.setWidth(3)
            painter.setPen(pen)
            
            # Konwersja bbox (który jest względem oryginalnego obrazka) na skalę Pixmapy
            # Musimy wiedzieć jaka była skala. Dla uproszczenia tutaj
            # rysujemy na przeskalowanym w MainPage, albo rysujemy na oryginale i skalujemy.
            # Zrobimy rysowanie na oryginale, potem skalowanie do wyświetlenia.
            pass # Rysowanie odbywa się w MainPage przed displayem
            
        self.setPixmap(final_pixmap)


class MainPage(QWidget):
    def __init__(self, detector, on_evaluate):
        super().__init__()
        self.detector = detector
        self.on_evaluate = on_evaluate
        self.current_bbox = None # Przechowujemy wykryty bbox

        self.drop_area = DropArea()
        # Połączenie sygnału z drop area z funkcją detekcji
        self.drop_area.file_dropped.connect(self.handle_image_drop)

        self.evaluate_btn = QPushButton("Evaluate Species")
        self.evaluate_btn.clicked.connect(self.trigger_evaluation)
        self.evaluate_btn.setEnabled(False) # Nieaktywny dopóki nie ma zdjęcia

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
            QPushButton:disabled {{
                background-color: #cccccc;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.addWidget(self.drop_area)
        layout.addWidget(self.evaluate_btn)

    def handle_image_drop(self, file_path):
        # 1. Wczytaj obrazek do Pixmapy
        original_pixmap = QPixmap(file_path)
        
        # 2. Użyj YOLO do znalezienia bboxa
        bbox = self.detector.detect_bbox(file_path)
        self.current_bbox = bbox # Zapisz do późniejszej klasyfikacji

        # 3. Rysuj BBox jeśli znaleziono
        if bbox is not None:
            x1, y1, x2, y2 = bbox
            painter = QPainter(original_pixmap)
            pen = QPen(QColor("#00FF00")) # Zielony kolor
            pen.setWidth(5)
            painter.setPen(pen)
            # Rysuj prostokąt (x, y, w, h)
            painter.drawRect(int(x1), int(y1), int(x2-x1), int(y2-y1))
            painter.end()
            print(f"Bird detected at: {bbox}")
        else:
            print("No bird detected by YOLO.")

        # 4. Przeskaluj do wyświetlenia i pokaż
        scaled_pixmap = original_pixmap.scaled(
            400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.drop_area.setPixmap(scaled_pixmap)
        
        # Odblokuj przycisk evaluate
        self.evaluate_btn.setEnabled(True)

    def trigger_evaluation(self):
        if self.drop_area.image_path:
            self.on_evaluate(self.drop_area.image_path, self.current_bbox)


class ResultPage(QWidget):
    def __init__(self, on_back):
        super().__init__()

        # ---------- BACK BUTTON ----------
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

        # ---------- TOP BAR ----------
        top_bar = QHBoxLayout()
        top_bar.addWidget(self.back_btn)
        top_bar.addStretch()
        top_bar.setContentsMargins(12, 12, 0, 0)

        # ---------- CONTENT ----------
        self.image_label = QLabel(alignment=Qt.AlignCenter)

        self.result_label = QLabel("Result: ---", alignment=Qt.AlignCenter)
        self.result_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #111827;
        """)

        # ---------- AUDIO ----------
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        self.play_btn = QPushButton("▶ Play Sound")
        self.play_btn.setFixedSize(200, 56)
        self.play_btn.clicked.connect(self.player.play)
        self.play_btn.setEnabled(False) # Domyślnie wyłączony
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
        # Pokazujemy to samo zdjęcie co na input (z bboxem jeśli zrobiliśmy save, 
        # ale tutaj ładujemy czyste - można zmienić logikę by przekazywać pixmapę)
        pixmap = QPixmap(image_path).scaled(
            300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.image_label.setPixmap(pixmap)
        
        self.result_label.setText(f"It's a {result_text}!")
        
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

        # Inicjalizacja logiki backendowej
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

        # 1. Klasyfikacja (z użyciem wykrytego wcześniej bboxa)
        species_name = self.detector.classify_species(image_path, bbox)
        
        # 2. Pobranie dźwięku
        audio_path = self.audio_manager.get_audio_path(species_name)

        # 3. Wyświetlenie wyników
        self.result_page.set_result(image_path, species_name, audio_path)
        self.stack.setCurrentWidget(self.result_page)

    def go_back(self):
        self.stack.setCurrentWidget(self.main_page)
        # Opcjonalnie: resetowanie playera
        self.result_page.player.stop()
