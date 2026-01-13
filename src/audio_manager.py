import os

class AudioManager:
    def __init__(self, assets_dir="assets"):
        self.assets_dir = assets_dir
        # Mapa: Nazwa klasy (z CLASS_NAMES) -> nazwa pliku
        self.sound_map = {
            "Indian Peacock": "peacock.mp3",
        }

    def get_audio_path(self, species_name):
        filename = self.sound_map.get(species_name)
        if filename:
            path = os.path.join(self.assets_dir, filename)
            if os.path.exists(path):
                return path
        return None