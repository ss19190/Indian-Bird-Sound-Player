import os

class AudioManager:
    def __init__(self, assets_dir="assets/sounds"):
        self.assets_dir = assets_dir
        # Mapa: Nazwa klasy (z CLASS_NAMES) -> nazwa pliku
        self.sound_map = {
            "Indian Peacock": "Indian_Peacock.mp3",
	    "Asian_Green_Bee_eater": "Asian_Green_Bee_eater.mp3",
	    "Cattle_Egret": "Cattle_Egret.mp3",
            "Common_Kingfisher": "Common_Kingfisher.mp3",
            " Common_Myna": " Common_Myna.mp3",
            "Common_Rosefinch": "Common_Rosefinch.mp3",
            "Common_Tailorbird": "Common_Tailorbird.mp3",
            "Coppersmith_Barbet": "Coppersmith_Barbet.mp3",
            "Forest_Wagtail": "Forest_Wagtail.mp3",
            "Gray_Wagtail": "Gray_Wagtail.mp3",        
            "Hoopoe": "Hoopoe.mp3",     
            "House_Crow": "House_Crow.mp3",     
            "Indian_Grey_Hornbill": "Indian_Grey_Hornbill.mp3",     
            "Indian_Pitta": "Indian_Pitta.mp3",     
            "Indian_Roller": "Indian_Roller.mp3",     
            "Jungle_Babbler": "Jungle_Babbler.mp3",     
            "Northern_Lapwing": "Northern_Lapwing.mp3",     
            "Red_Wattled_Lapwing": "Red_Wattled_Lapwing.mp3",     
            "Ruddy_Shelduck": "Ruddy_Shelduck.mp3",     
            "Rufous_Treepie": "Rufous_Treepie.mp3",     
            "Sarus_Crane": "Sarus_Crane.mp3",     
            "White_Breasted_Kingfisher": "White_Breasted_Kingfisher.mp3",   
            "White_Breasted_Waterhen": "White_Breasted_Waterhen.mp3",   
            "White_Wagtail": "White_Wagtail.mp3",   
}

    def get_audio_path(self, species_name):
        filename = self.sound_map.get(species_name)
        if filename:
            path = os.path.join(self.assets_dir, filename)
            if os.path.exists(path):
                return path
        return None