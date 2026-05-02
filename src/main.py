"""
Punto de entrada de la aplicación.
"""
import asyncio
import flet as ft
from models import SongApp
from views import CharacterSettingsView, SettingsView, SongFormView, EditView, MainView
from views.theme_utils import apply_system_overlay


def main(page: ft.Page):
    """Función principal de la aplicación"""
    page.title = "Gestor de Canciones"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    app = SongApp()

    # Cargar tema guardado desde JSON
    saved_theme = app.get_theme()
    page.session.store.set("theme_mode", saved_theme)
    page.theme_mode = ft.ThemeMode.LIGHT if saved_theme == "light" else ft.ThemeMode.DARK
    page.bgcolor = "#f5f6fa" if saved_theme == "light" else "#0a0e27"
    # apply_system_overlay se llama UNA sola vez al inicio.
    # NO en route_change: cada llamada serializa dos objetos Theme en page.update(),
    # anadiendo trabajo innecesario en cada navegacion.
    apply_system_overlay(page)

    main_view = MainView(page, app)
    page.session.store.set("main_view", main_view)

    add_view = SongFormView(page, app, "/add", "Agregar Cancion", ["#00b894", "#55efc4"])
    edit_view = EditView(page, app)
    settings_view = SettingsView(page, app)
    character_settings_view = CharacterSettingsView(page, app)

    def apply_theme():
        """Aplica colores de pagina segun el tema guardado. Sin tocar page.theme."""
        mode = page.session.store.get("theme_mode") or "dark"
        page.theme_mode = ft.ThemeMode.LIGHT if mode == "light" else ft.ThemeMode.DARK
        page.bgcolor = "#f5f6fa" if mode == "light" else "#0a0e27"

    async def route_change():
        """
        Two-phase render para eliminar el indicador 'working' de Flutter.

        Fase 1: construye el skeleton (sin song cards) y llama page.update().
                Flutter recibe el patch y oculta 'working' mostrando el skeleton.
        Fase 2: await asyncio.sleep(0) cede al event loop para que send_loop
                envie el mensaje antes de continuar. Luego search_handler()
                puebla los song cards con una actualizacion dirigida al Column
                (mucho mas ligera que un page.update() completo sobre toda la pagina).
        """
        route = page.route
        apply_theme()
        page.views.clear()

        # main_view.build() es rapido: refresh_theme() ya no reconstruye song cards.
        page.views.append(main_view.build())

        if route == "/add":
            add_view.clear_form()
            add_view.refresh_character_options()
            page.views.append(add_view.build(main_view))

        elif route == "/edit":
            editing_song = page.session.store.get("editing_song")
            if editing_song:
                edit_view.load_song_data(editing_song)
                edit_view.refresh_character_options()
            page.views.append(edit_view.build(main_view))

        elif route == "/settings":
            page.views.append(settings_view.build(main_view))

        elif route == "/settings/characters":
            character_settings_view.refresh_characters_list()
            page.views.append(settings_view.build(main_view))
            page.views.append(character_settings_view.build(main_view))

        # Fase 1: skeleton → Flutter. Pone el mensaje en la send_queue.
        page.update()

        # Cede al event loop: send_loop lee la queue y envia el mensaje al socket.
        # Flutter recibe el skeleton y oculta el indicador 'working'.
        await asyncio.sleep(0)

        # Fase 2: poblar song cards solo para la vista principal.
        # search_handler → update_results → results_column.update() (patch dirigido).
        if route == "/":
            try:
                main_view.search_handler(None)
            except RuntimeError:
                # La sesión pudo cerrarse mientras se procesaba el cambio de ruta.
                return

    async def view_pop(e: ft.ViewPopEvent):
        if e.view is not None:
            page.views.remove(e.view)
            top_view = page.views[-1]
            await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Llamada inicial como tarea async dentro del event loop de Flet.
    asyncio.get_running_loop().create_task(route_change())


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
