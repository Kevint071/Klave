import json
import os

# Constantes
MUSICAL_KEYS = [
    "Do", "Do Menor",
    "Do#", "Do# Menor",
    "Re", "Re Menor",
    "Re#", "Re# Menor",
    "Mi", "Mi Menor",
    "Fa", "Fa Menor",
    "Fa#", "Fa# Menor",
    "Sol", "Sol Menor",
    "Sol#", "Sol# Menor",
    "La", "La Menor",
    "La#", "La# Menor",
    "Si", "Si Menor"
]
DEFAULT_CHARACTERS = ["Misionero", "Oración", "Evangelístico", "Alabanza", "Adoración"]


def _normalize_tempo(tempo):
    return {
        "Lenta": "Lento",
        "Moderada": "Moderado",
        "Rápida": "Rápido",
    }.get(tempo, tempo)


class SongApp:
    """Gestiona la lógica de negocio de canciones y caracteres"""
    
    def __init__(self):
        assets_dir = os.environ.get("FLET_ASSETS_DIR", os.path.join(os.path.dirname(__file__), "..", "assets"))
        self.data_file = os.path.join(assets_dir, "user_data.json")
        self.user_data = self.load_user_data()

    def load_user_data(self):
        """Carga datos del usuario desde el archivo JSON"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "characters" not in data:
                        data["characters"] = DEFAULT_CHARACTERS.copy()
                    if "songs" not in data:
                        data["songs"] = []
                    if "theme" not in data:
                        data["theme"] = "dark"
                    return data
        except Exception as e:
            print(f"Error cargando datos: {e}")
        
        # Fallback a datos por defecto
        return {"songs": [], "characters": DEFAULT_CHARACTERS.copy(), "theme": "dark"}

    def save_user_data(self):
        """Guarda datos del usuario en el archivo JSON"""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.user_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando datos: {e}")

    # ===== GESTIÓN DE TEMA =====

    def get_theme(self):
        """Obtiene el tema guardado"""
        return self.user_data.get("theme", "dark")

    def save_theme(self, mode):
        """Guarda el tema en el archivo JSON"""
        self.user_data["theme"] = mode
        self.save_user_data()

    # ===== GESTIÓN DE CARACTERES =====
    
    def get_characters(self):
        """Obtiene la lista de caracteres disponibles"""
        self.user_data = self.load_user_data()
        return self.user_data.get("characters", DEFAULT_CHARACTERS.copy())

    def add_character(self, character):
        """Agrega un nuevo carácter"""
        if character and character not in self.user_data["characters"]:
            self.user_data["characters"].append(character)
            self.save_user_data()
            self.user_data = self.load_user_data()
            return True
        return False

    def remove_character(self, character):
        """Elimina un carácter"""
        if character in self.user_data["characters"]:
            self.user_data["characters"].remove(character)
            self.save_user_data()
            self.user_data = self.load_user_data()
            return True
        return False

    # ===== GESTIÓN DE CANCIONES =====
    
    def get_all_songs(self):
        """Obtiene todas las canciones"""
        return self.user_data.get("songs", [])

    def add_song(self, title, key, character, tempo):
        """Agrega una nueva canción"""
        new_id = max([s["id"] for s in self.user_data["songs"]], default=0) + 1
        new_song = {
            "id": new_id,
            "title": title,
            "key": key,
            "character": character,  # String con comas: "Adoración,Alabanza"
            "tempo": tempo
        }
        self.user_data["songs"].append(new_song)
        self.save_user_data()
        return new_song

    def update_song(self, song_id, title=None, key=None, character=None, tempo=None):
        """Actualiza una canción existente"""
        for song in self.user_data["songs"]:
            if song["id"] == song_id:
                if title is not None:
                    song["title"] = title
                if key is not None:
                    song["key"] = key
                if character is not None:
                    song["character"] = character
                if tempo is not None:
                    song["tempo"] = tempo
                self.save_user_data()
                return True
        return False

    def delete_song(self, song_id):
        """Elimina una canción"""
        self.user_data["songs"] = [s for s in self.user_data["songs"] if s["id"] != song_id]
        self.save_user_data()

    def search_songs(self, query="", key="", character="", tempo=""):
        """
        Busca canciones con filtros.
        ✅ Soporta múltiples caracteres por canción.
        """
        songs = self.get_all_songs()

        # Filtro de texto (búsqueda por título)
        if query:
            query_lower = query.lower()
            songs = [s for s in songs if query_lower in s["title"].lower()]

        # Filtro de tono
        if key:
            songs = [s for s in songs if s.get("key") == key]

        # ✅ Filtro de carácter (verifica si el carácter está en la lista)
        if character:
            filtered_songs = []
            for song in songs:
                song_characters = song.get("character", "")
                # Convertir string separado por comas en lista
                char_list = [c.strip() for c in song_characters.split(",") if c.strip()]
                # Si el carácter buscado está en la lista, incluir la canción
                if character in char_list:
                    filtered_songs.append(song)
            songs = filtered_songs

        # Filtro de tempo
        if tempo:
            normalized_tempo = _normalize_tempo(tempo)
            songs = [s for s in songs if _normalize_tempo(s.get("tempo")) == normalized_tempo]

        return songs
