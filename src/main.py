"""
Punto de entrada de la aplicación.
Actualizado a la nueva API de Flet:
- route_change sin parámetro e
- on_view_pop registrado (manejo del botón Atrás)
- push_route con await
- Stack de vistas declarativo (acumulativo por ruta)
"""
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
    apply_system_overlay(page)

    main_view = MainView(page, app)
    page.session.store.set("main_view", main_view)

    add_view = SongFormView(page, app, "/add", "Agregar Canción", ["#00b894", "#55efc4"])
    edit_view = EditView(page, app)
    settings_view = SettingsView(page, app)
    character_settings_view = CharacterSettingsView(page, app)

    def apply_theme():
        mode = page.session.store.get("theme_mode") or "dark"
        page.theme_mode = ft.ThemeMode.LIGHT if mode == "light" else ft.ThemeMode.DARK
        page.bgcolor = "#f5f6fa" if mode == "light" else "#0a0e27"
        apply_system_overlay(page)

    # ✅ CAMBIO 1: sin parámetro `e` — la nueva API llama route_change()
    #    sin argumento cuando se asigna a page.on_route_change.
    def route_change():
        apply_theme()
        page.views.clear()

        # ✅ CAMBIO 2: el stack es ACUMULATIVO.
        # La vista "/" siempre se añade primero como base.
        # Las rutas hijas se apilan encima, para que el botón
        # Atrás funcione correctamente en Android/iOS/web.
        page.views.append(main_view.build())

        if page.route == "/add":
            add_view.clear_form()
            add_view.refresh_character_options()
            page.views.append(add_view.build(main_view))

        elif page.route == "/edit":
            editing_song = page.session.store.get("editing_song")
            if editing_song:
                edit_view.load_song_data(editing_song)
                edit_view.refresh_character_options()
            page.views.append(edit_view.build(main_view))

        elif page.route == "/settings":
            page.views.append(settings_view.build(main_view))

        elif page.route == "/settings/characters":
            # ✅ CAMBIO 3: apilamos /settings Y /settings/characters,
            # porque /settings/characters es hija de /settings.
            # Así el Atrás desde /settings/characters va a /settings,
            # no directo a /.
            character_settings_view.refresh_characters_list()
            page.views.append(settings_view.build(main_view))
            page.views.append(character_settings_view.build(main_view))

        page.update()

    # ✅ CAMBIO 4: on_view_pop — FALTABA COMPLETAMENTE en el código original.
    # Sin esto el botón Atrás del sistema (Android, browser) no funciona:
    # Flet dispara este evento, espera que saquemos la vista del stack y
    # naveguemos a la nueva top view.
    async def view_pop(e: ft.ViewPopEvent):
        if e.view is not None:
            page.views.remove(e.view)
            top_view = page.views[-1]
            await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop  # ✅ registrado

    # ✅ CAMBIO 5: llamada inicial sin argumento (consistente con la firma)
    route_change()

    main_view.search_handler(None)
    page.update()


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
