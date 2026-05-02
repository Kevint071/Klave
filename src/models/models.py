import asyncio
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
        """Guarda datos del usuario en el archivo JSON (síncrono, solo para inicio)"""
        try:
            temp_file = f"{self.data_file}.tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self.user_data, f, ensure_ascii=False, indent=2)
            os.replace(temp_file, self.data_file)
        except Exception as e:
            print(f"Error guardando datos: {e}")

    async def save_async(self):
        """Guarda datos en disco en un thread separado para no bloquear el event loop"""
        await asyncio.to_thread(self.save_user_data)

    # ===== GESTIÓN DE TEMA =====

    def get_theme(self):
        """Obtiene el tema guardado"""
        return self.user_data.get("theme", "dark")

    def save_theme(self, mode):
        """Muta el tema en memoria (llamar save_async() para persistir)"""
        self.user_data["theme"] = mode

    # ===== GESTIÓN DE CARACTERES =====
    
    def get_characters(self):
        """Obtiene la lista de caracteres disponibles"""
        return self.user_data.get("characters", DEFAULT_CHARACTERS.copy())

    def add_character(self, character):
        """Agrega un carácter en memoria (llamar save_async() para persistir)"""
        if character and character not in self.user_data["characters"]:
            self.user_data["characters"].append(character)
            return True
        return False

    def remove_character(self, character):
        """Elimina un carácter en memoria (llamar save_async() para persistir)"""
        if character in self.user_data["characters"]:
            self.user_data["characters"].remove(character)
            return True
        return False

    # ===== GESTIÓN DE CANCIONES =====
    
    def get_all_songs(self):
        """Obtiene todas las canciones"""
        return self.user_data.get("songs", [])

    def add_song(self, title, key, character, tempo):
        """Agrega una canción en memoria (llamar save_async() para persistir)"""
        new_id = max([s["id"] for s in self.user_data["songs"]], default=0) + 1
        new_song = {
            "id": new_id,
            "title": title,
            "key": key,
            "character": character,  # String con comas: "Adoración,Alabanza"
            "tempo": tempo
        }
        self.user_data["songs"].append(new_song)
        return new_song

    def update_song(self, song_id, title=None, key=None, character=None, tempo=None):
        """Actualiza una canción en memoria (llamar save_async() para persistir)"""
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
                return True
        return False

    def delete_song(self, song_id):
        """Elimina una canción en memoria (llamar save_async() para persistir)"""
        self.user_data["songs"] = [s for s in self.user_data["songs"] if s["id"] != song_id]

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
