import asyncio
import flet as ft
from components import show_confirmation_dialog, show_snackbar
from .song_form_view import SongFormView
from .theme_utils import get_theme_colors


class EditView(SongFormView):
    """Vista de edición de canciones"""

    def __init__(self, page, app):
        super().__init__(page, app, "/edit", "Editar Canción", ["#74b9ff", "#a29bfe"])

    async def _delete_song_and_return(self, song_id):
        self.app.delete_song(song_id)
        self.page.session.store.set("editing_song", None)
        self.clear_form()
        await self.page.push_route("/")
        show_snackbar(self.page, "Canción eliminada exitosamente", "#ff7675")
        asyncio.create_task(self.app.save_async())

    async def delete_from_edit(self, main_view):
        editing_song = self.page.session.store.get("editing_song")
        if not editing_song:
            return

        def on_confirm():
            try:
                asyncio.create_task(self._delete_song_and_return(editing_song["id"]))
            except Exception as ex:
                print("ERROR al eliminar canción:", ex)
                show_snackbar(self.page, "Error al eliminar la canción", "#ff7675")

        show_confirmation_dialog(
            self.page,
            "Confirmar eliminación",
            "¿Estás seguro de que deseas eliminar esta canción?",
            on_confirm,
        )

    def build(self, main_view, extra_buttons=None):
        editing_song = self.page.session.store.get("editing_song")
        if editing_song:
            self.load_song_data({
                "id": editing_song["id"],
                "title": editing_song["title"],
                "key": editing_song.get("key", ""),
                "character": editing_song.get("character", ""),
                "tempo": editing_song.get("tempo", ""),
            })

        colors = get_theme_colors(self.page)

        delete_menu = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.DELETE_OUTLINE_ROUNDED, color="#ff7675", size=18),
                            ft.Text("Eliminar canción", color="#ff7675", size=14),
                        ],
                        spacing=8,
                    ),
                    on_click=lambda e: asyncio.create_task(self.delete_from_edit(main_view)),
                )
            ],
            icon=ft.Icons.MORE_VERT_ROUNDED,
            icon_color=colors["text_secondary"],
            tooltip="Más opciones",
        )

        return super().build(main_view, extra_buttons=[delete_menu])