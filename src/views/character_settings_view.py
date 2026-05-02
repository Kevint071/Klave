import asyncio
import flet as ft
from components import create_header, create_character_item, show_snackbar
from .theme_utils import get_theme_colors


class CharacterSettingsView:
    """Vista para editar caracteres"""

    def __init__(self, page, app):
        self.page = page
        self.app = app
        self.characters_list = ft.Column(
            [], spacing=8, scroll=ft.ScrollMode.AUTO, expand=True
        )
        self.new_character_field = self._create_new_character_field()

    def _create_new_character_field(self):
        colors = get_theme_colors(self.page)
        return ft.TextField(
            hint_text="Nuevo carácter...",
            border_color=colors["border_color"],
            focused_border_color=colors["border_focused"],
            bgcolor=colors["bg_secondary"],
            color=colors["text_primary"],
            height=55,
            text_size=14,
            border_radius=12,
            on_submit=lambda e: asyncio.create_task(
                self._add_character_from_field()
            ),
        )

    def refresh_theme(self):
        """Actualiza los estilos según el tema"""
        colors = get_theme_colors(self.page)
        self.new_character_field.border_color = colors["border_color"]
        self.new_character_field.bgcolor = colors["bg_secondary"]
        self.new_character_field.color = colors["text_primary"]

    def refresh_characters_list(self):
        """Actualiza la lista de caracteres"""
        self.characters_list.controls.clear()
        for char in self.app.get_characters():
            self.characters_list.controls.append(
                create_character_item(
                    self.page,
                    char,
                    lambda c=char: asyncio.create_task(
                        self.remove_character_handler(c)
                    ),
                )
            )
        # ✅ Solo llamar update() si el control ya está montado en la página
        try:
            if self.characters_list.page:
                self.characters_list.update()
            else:
                self.page.update()
        except Exception:
            self.page.update()

    async def _add_character_from_field(self):
        """Lógica interna de agregar carácter desde el campo de texto"""
        value = self.new_character_field.value
        if value and value.strip():
            if self.app.add_character(value.strip()):
                self.new_character_field.value = ""
                self.new_character_field.update()
                self.refresh_characters_list()

                # Refrescar opciones en el main_view almacenado en sesión
                main_view = self.page.session.store.get("main_view")
                if main_view:
                    main_view.refresh_character_options()

                show_snackbar(self.page, "Carácter agregado exitosamente", "#00b894")
                await self.app.save_async()
            else:
                show_snackbar(self.page, "El carácter ya existe", "#ff7675")

    async def add_character_handler(self, main_view=None):
        """Agrega un nuevo carácter"""
        value = self.new_character_field.value
        if value and value.strip():
            if self.app.add_character(value.strip()):
                self.new_character_field.value = ""
                self.new_character_field.update()
                self.refresh_characters_list()

                # Preferir main_view de sesión si no se pasa como argumento
                mv = main_view or self.page.session.store.get("main_view")
                if mv:
                    mv.refresh_character_options()

                show_snackbar(self.page, "Carácter agregado exitosamente", "#00b894")
                await self.app.save_async()
            else:
                show_snackbar(self.page, "El carácter ya existe", "#ff7675")

    async def remove_character_handler(self, character):
        """Elimina un carácter"""
        if self.app.remove_character(character):
            self.refresh_characters_list()

            main_view = self.page.session.store.get("main_view")
            if main_view:
                main_view.refresh_character_options()

            show_snackbar(self.page, "Carácter eliminado exitosamente", "#ff7675")
            await self.app.save_async()

    def build(self, main_view):
        """Construye la vista de edición de caracteres"""
        colors = get_theme_colors(self.page)
        self.refresh_theme()

        header = create_header(
            self.page,
            "Editar Caracteres",
            ["#fd79a8", "#fdcb6e"],
            # ✅ CAMBIO: push_route("/settings") en lugar de page.go("/settings")
            # El stack acumulativo de main.py ya tiene /settings debajo, así que
            # push_route dispara on_view_pop correctamente en Android/iOS/web
            left_button=ft.IconButton(
                icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
                icon_color=colors["icon_color"],
                icon_size=18,
                on_click=lambda e: asyncio.create_task(
                    self.page.push_route("/settings")
                ),
                tooltip="Volver",
                style=ft.ButtonStyle(
                    padding=ft.Padding.only(left=8, right=4, top=8, bottom=8),
                ),
            ),
        )

        content = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.CATEGORY, size=22, color="#74b9ff"),
                            ft.Text(
                                "Gestión de Caracteres",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=colors["text_primary"],
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Container(height=8),
                    ft.Row(
                        [
                            ft.Container(
                                content=self.new_character_field, expand=True
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ADD_CIRCLE,
                                icon_color="#00b894",
                                icon_size=32,
                                # ✅ asyncio.create_task envuelve la coroutine
                                # add_character_handler en un lambda sincrónico
                                on_click=lambda e: asyncio.create_task(
                                    self.add_character_handler(main_view)
                                ),
                                tooltip="Agregar carácter",
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Container(
                        content=ft.Container(
                            height=1, bgcolor=colors["border_color"]
                        ),
                        margin=ft.Margin.symmetric(vertical=16),
                    ),
                    ft.Text(
                        "Caracteres disponibles:",
                        size=14,
                        color=colors["text_secondary"],
                        weight=ft.FontWeight.W_500,
                    ),
                    ft.Container(height=8),
                    self.characters_list,
                ],
                spacing=12,
                expand=True,
            ),
            padding=16,
            expand=True,
        )

        return ft.View(
            route="/settings/characters",
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
