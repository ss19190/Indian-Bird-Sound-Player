# 🦚 Indian Bird Species Detector & Player

**A desktop application that uses Computer Vision to detect Indian birds in images and plays their corresponding calls.**

## 📖 Overview

This project is a Python-based desktop application designed to identify various species of birds found in India. When a user uploads an image, the system performs two main tasks:

1. **Object Detection:** Localizes the bird within the image.
2. **Species Classification:** Identifies the specific species.
3. **Audio Feedback:** Automatically plays the unique call/song of the identified bird.

It combines deep learning (CNNs) for visual recognition with an interactive audio experience.

## ✨ Key Features

* **GUI Interface:** User-friendly desktop interface for uploading images.
* **Bird Localization:** Draws bounding boxes around the detected bird.
* **Species Identification:** accurately classifies Indian bird species (e.g., Indian Peafowl, Kingfisher, Myna).
* **Audio Playback:** Instantly plays the bird's sound upon detection.

## 🛠️ Tech Stack

This project was built using the following technologies:

* **Language:** Python 3.x
* **GUI:** [Tkinter / PyQt5 / CustomTkinter] TBA
* **Machine Learning:** [TensorFlow/ PyTorch] TBA
* **Image Processing:** OpenCV
* **Audio Handling:** [PyGame / Playsound] TBA

## 🚀 Installation & Setup

Follow these steps to run the project locally.

### 1. Clone the repository

```bash
git clone https://github.com/ss19190/Indian-Bird-Sound-Player#
cd Indian-Bird-Sound-Player

```

### 2. Create a Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

```

### 3. Install Dependencies

```bash
pip install -r requirements.txt

```

### 4. Run the Application

```bash
python main.py

```

## 📂 Project Structure

```text
Indian-Bird-Sound-Player/
│
├── assets/             # Audio files (.wav/.mp3) and UI icons
│   ├── peacock.mp3
│   ├── kingfisher.mp3
│   └── ...
├── data/               # Sample images for testing
├── models/             # Trained ML models
├── src/                # Source code
│   ├── gui.py          # GUI implementation
│   ├── detection.py    # Object detection & classification logic
│   └── audio_manager.py # Audio playback logic
├── main.py             # Entry point of the application
├── requirements.txt    # Python dependencies
└── README.md

```

## 🧠 Model Information

The model was trained on a dataset of Indian Bird species.

* **Architecture:** [e.g., ResNet50, MobileNetV2, Custom CNN] TBA
* **Accuracy:** ~[XX]%
* **Classes:** The model currently recognizes 25 species, including House Crow or Indian Peacock 

---

**Created by:**
- Sara Sobstyl
- Bartosz Szkodny
- Szymon Poterejko
- Filip Bucher
- Alicja Banaszewska
- Yassine Bendimerad
