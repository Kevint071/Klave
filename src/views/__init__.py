"""
Módulo de vistas de la aplicación
"""
from .main_view import MainView
from .song_form_view import SongFormView
from .edit_view import EditView
from .settings_view import SettingsView
from .character_settings_view import CharacterSettingsView

__all__ = [
    'MainView',
    'SongFormView', 
    'EditView',
    'SettingsView',
    'CharacterSettingsView'
]
