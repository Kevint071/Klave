"""
Utilidades para manejo de temas
"""
import flet as ft


def apply_system_overlay(page):
    """
    Configura el overlay del sistema (barra de estado) para integrarse
    visualmente con el fondo de la app.

    - status_bar_color=TRANSPARENT: la barra de estado hereda el bgcolor de la
      vista, por lo que no aparece como una franja extra de color diferente.
    - status_bar_icon_brightness: DARK (iconos oscuros) cuando el fondo es
      claro; LIGHT (iconos blancos) cuando el fondo es oscuro. Flet aplica
      automáticamente el tema correcto según page.theme_mode.
    """
    light_overlay = ft.SystemOverlayStyle(
        status_bar_color=ft.Colors.TRANSPARENT,
        status_bar_icon_brightness=ft.Brightness.DARK,
    )
    dark_overlay = ft.SystemOverlayStyle(
        status_bar_color=ft.Colors.TRANSPARENT,
        status_bar_icon_brightness=ft.Brightness.LIGHT,
    )
    page.theme = ft.Theme(system_overlay_style=light_overlay)
    page.dark_theme = ft.Theme(system_overlay_style=dark_overlay)


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
