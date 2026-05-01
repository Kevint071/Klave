"""
Componentes reutilizables de la interfaz con sistema de temas
"""
import flet as ft


def get_theme_colors(page):
    """Retorna los colores según el tema activo"""
    is_light = page.session.store.get("theme_mode") == "light"
    
    return {
        "bg_primary": "#f5f6fa" if is_light else "#0a0e27",
        "bg_secondary": "#ffffff" if is_light else "#1e2347",
        "bg_tertiary": "#e8eaf0" if is_light else "#2d3561",
        "text_primary": "#2d3436" if is_light else "#ffffff",
        "text_secondary": "#636e72" if is_light else "#b2bec3",
        "border_color": "#dfe6e9" if is_light else "#2d3561",
        "border_focused": "#6c5ce7",
        "card_shadow": "#00000030" if is_light else "#00000015",
        "icon_color": "#6c5ce7",
        "icon_bg": "#e8eaf0" if is_light else "#2d3561",
        "empty_icon": "#b2bec3" if is_light else "#2d3561",
    }


def create_song_card(page, song, on_click_callback):
    colors = get_theme_colors(page)

    key_badge = ft.Container(
        content=ft.Text(
            song.get("key") or "Sin nota",
            size=11,
            color="#2d3436",
            weight=ft.FontWeight.BOLD
        ),
        bgcolor="#ffeaa7",
        padding=ft.Padding.symmetric(horizontal=8, vertical=4),  # antes: 10/6
        border_radius=10,
    )

    return ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Icon(ft.Icons.MUSIC_NOTE, color="#6c5ce7", size=18),  # antes: 22
                bgcolor=colors["icon_bg"],
                padding=6,          # antes: 8
                border_radius=8,
            ),
            ft.Text(
                song["title"],
                size=14,            # antes: 15
                weight=ft.FontWeight.BOLD,
                color=colors["text_primary"],
                expand=True
            ),
            key_badge,
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.Padding.symmetric(horizontal=12, vertical=10),  # antes: 14 flat
        bgcolor=colors["bg_secondary"],
        border_radius=12,           # antes: 16
        border=ft.Border.all(1, colors["border_color"]),
        margin=ft.Margin.only(bottom=6),   # antes: 10
        shadow=ft.BoxShadow(
            spread_radius=0,        # antes: 1
            blur_radius=6,          # antes: 10
            color=colors["card_shadow"],
            offset=ft.Offset(0, 2), # antes: 4
        ),
        on_click=lambda e: on_click_callback(song),
        ink=True,
    )


def create_character_item(page, character, on_delete_callback):
    """Crea un item de carácter en la lista de configuración"""
    colors = get_theme_colors(page)
    
    return ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.LABEL, color="#a29bfe", size=20),
            ft.Text(character, size=15, color=colors["text_primary"], weight=ft.FontWeight.W_500),
            ft.Container(expand=True),
            ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_color="#ff7675",
                icon_size=20,
                on_click=lambda e: on_delete_callback(character),
                tooltip="Eliminar"
            ),
        ], spacing=12),
        bgcolor=colors["bg_secondary"],
        padding=14,
        border_radius=12,
        border=ft.Border.all(1, colors["border_color"]),
    )


def create_header(page, title, gradient_colors=None, left_button=None, right_buttons=None):
    """Header moderno con acento de color y separación visual clara"""
    colors = get_theme_colors(page)

    title_group = ft.Row(
        [
            ft.Text(
                title,
                size=19,
                weight=ft.FontWeight.W_700,
                color=colors["text_primary"],
            ),
        ],
        spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    controls = []
    if left_button:
        controls.append(left_button)
    controls.append(title_group)
    controls.append(ft.Container(expand=True))
    if right_buttons:
        controls.extend(right_buttons)

    left_padding = 4 if left_button else 16

    return ft.Container(
        content=ft.Row(
            controls,
            spacing=6,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.only(left=left_padding, right=12, top=12, bottom=12),
        bgcolor=colors["bg_primary"],
    )


def create_empty_state(page, message):
    """Crea un estado vacío para cuando no hay resultados"""
    colors = get_theme_colors(page)
    
    return ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.MUSIC_OFF, size=64, color=colors["empty_icon"]),
            ft.Container(height=12),
            ft.Text(
                message,
                size=16,
                color=colors["text_secondary"],
                weight=ft.FontWeight.W_500
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
        padding=60,
        alignment=ft.Alignment.CENTER,
    )


def show_confirmation_dialog(page, title, message, on_confirm):
    """Muestra un diálogo de confirmación"""
    def close_dialog(e):
        dialog.open = False
        page.update()

    def confirm_and_close(e):
        on_confirm()
        close_dialog(e)

    dialog = ft.AlertDialog(
        title=ft.Text(title),
        content=ft.Text(message),
        actions=[
            ft.TextButton("Cancelar", on_click=close_dialog),
            ft.TextButton("Eliminar", on_click=confirm_and_close),
        ],
    )
    page.overlay.append(dialog)
    dialog.open = True
    page.update()


def show_snackbar(page, message, bgcolor="#00b894"):
    """Muestra un snackbar con un mensaje"""
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message, color="#ffffff"),
        bgcolor=bgcolor,
    )
    page.snack_bar.open = True
    page.update()
