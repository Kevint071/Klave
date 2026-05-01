import asyncio
import flet as ft
from components import create_header
from .theme_utils import get_theme_colors, apply_system_overlay


class SettingsView:
    """Vista de configuración principal"""

    def __init__(self, page, app):
        self.page = page
        self.app = app

    def _get_theme_mode(self):
        return self.page.session.store.get("theme_mode") or "dark"

    async def _set_theme_mode(self, mode, main_view):
        self.page.session.store.set("theme_mode", mode)
        self.page.theme_mode = ft.ThemeMode.LIGHT if mode == "light" else ft.ThemeMode.DARK
        self.page.bgcolor = "#f5f6fa" if mode == "light" else "#0a0e27"
        apply_system_overlay(self.page)
        self.app.save_theme(mode)
        # Reconstruir las vistas en-lugar para aplicar el cambio inmediatamente
        self.page.views.clear()
        self.page.views.append(main_view.build())
        self.page.views.append(self.build(main_view))
        self.page.update()

    def build(self, main_view):
        colors = get_theme_colors(self.page)
        is_light = self._get_theme_mode() == "light"

        header = create_header(
            self.page,
            "Configuración",
            ["#fd79a8", "#fdcb6e"],
            left_button=ft.IconButton(
                icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
                icon_color=colors["icon_color"],
                icon_size=18,
                on_click=lambda e: asyncio.create_task(self.page.push_route("/")),
                tooltip="Volver",
                style=ft.ButtonStyle(
                    padding=ft.Padding.only(left=8, right=4, top=8, bottom=8),
                ),
            ),
        )

        def _setting_row(icon, icon_color, label, trailing):
            return ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(icon, size=20, color=icon_color),
                            bgcolor=ft.Colors.with_opacity(0.12, icon_color),
                            border_radius=10,
                            width=38, height=38,
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Text(
                            label, size=15, weight=ft.FontWeight.W_500,
                            color=colors["text_primary"], expand=True,
                        ),
                        trailing,
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=colors["bg_secondary"],
                border_radius=14,
                padding=ft.Padding.symmetric(horizontal=16, vertical=14),
                border=ft.Border.all(1, colors["border_color"]),
            )

        theme_switch = ft.Switch(
            value=is_light,
            on_change=lambda e: asyncio.create_task(
                self._set_theme_mode("light" if e.control.value else "dark", main_view)
            ),
            active_color="#00b894",
            inactive_thumb_color="#636e72",
            inactive_track_color=ft.Colors.with_opacity(0.3, "#636e72"),
        )

        theme_row = _setting_row(
            ft.Icons.LIGHT_MODE if is_light else ft.Icons.DARK_MODE,
            "#fdcb6e" if is_light else "#74b9ff",
            "Modo Claro" if is_light else "Modo Oscuro",
            theme_switch,
        )

        chars_row = ft.Container(
            content=_setting_row(
                ft.Icons.CATEGORY_ROUNDED,
                "#74b9ff",
                "Personalizar Caracteres",
                ft.Icon(ft.Icons.CHEVRON_RIGHT_ROUNDED, color=colors["text_secondary"], size=20),
            ),
            on_click=lambda e: asyncio.create_task(
                self.page.push_route("/settings/characters")
            ),
            ink=True,
            border_radius=14,
        )

        content = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Preferencias",
                        size=18, weight=ft.FontWeight.BOLD,
                        color=colors["text_primary"],
                    ),
                    ft.Container(height=14),
                    theme_row,
                    ft.Container(height=12),
                    chars_row,
                ],
                spacing=0,
            ),
            padding=16,
            expand=True,
        )

        return ft.View(
            route="/settings",
            controls=[
                ft.SafeArea(
                    content=ft.Column(
                        controls=[header, content],
                        spacing=0,
                        expand=True,
                    ),
                    expand=True,
                )
            ],
            bgcolor=colors["bg_primary"],
            padding=0,
        )