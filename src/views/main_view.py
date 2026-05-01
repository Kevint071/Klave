import asyncio
import flet as ft
from components import create_song_card, create_header, create_empty_state
from .theme_utils import get_theme_colors

BASE_NOTES = ["Do", "Re", "Mi", "Fa", "Sol", "La", "Si"]


class MainView:
    """Vista principal con listado de canciones"""

    def __init__(self, page, app):
        self.page = page
        self.app = app
        self.results_column = ft.Column(
            [], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True
        )
        self.search_field = self._create_search_field()

        # Filter state
        self._filter_note = None
        self._filter_sostenido = False
        self._filter_menor = False
        self._filter_character = ""
        self._filter_ritmo = ""

    def _create_search_field(self):
        colors = get_theme_colors(self.page)
        return ft.TextField(
            hint_text="Buscar canción...",
            prefix_icon=ft.Icons.SEARCH,
            border_color=colors["border_color"],
            focused_border_color=colors["border_focused"],
            bgcolor=colors["bg_secondary"],
            color=colors["text_primary"],
            on_change=lambda e: self.search_handler(e),
            text_size=14,
            border_radius=12,
            expand=True,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=16),
        )

    def _build_filter_key(self):
        if not self._filter_note:
            return ""
        key = self._filter_note
        if self._filter_sostenido:
            key += "#"
        if self._filter_menor:
            key += " Menor"
        return key

    def _has_active_filters(self):
        return bool(
            self._filter_note or self._filter_character or self._filter_ritmo
        )

    def _open_filter_dialog(self, e):
        colors = get_theme_colors(self.page)

        # Working copy of filter state for the dialog
        state = {
            "note": self._filter_note,
            "sostenido": self._filter_sostenido,
            "menor": self._filter_menor,
            "character": self._filter_character,
            "ritmo": {
                "Lenta": "Lento",
                "Moderada": "Moderado",
                "Rápida": "Rápido",
            }.get(self._filter_ritmo, self._filter_ritmo),
        }

        # Notes that don't support sostenido
        NO_SOSTENIDO = {"Mi", "Si"}

        def _sostenido_disabled():
            return state["note"] in NO_SOSTENIDO

        def build_note_btn(note):
            is_sel = state["note"] == note
            return ft.Container(
                content=ft.Text(
                    note, size=13, weight=ft.FontWeight.W_600,
                    color="#ffffff" if is_sel else colors["text_primary"],
                    text_align=ft.TextAlign.CENTER,
                ),
                bgcolor="#6c5ce7" if is_sel else colors["bg_tertiary"],
                border_radius=20,
                width=48,
                height=36,
                border=ft.Border.all(
                    1.5 if is_sel else 1,
                    "#6c5ce7" if is_sel else colors["border_color"],
                ),
                on_click=lambda e, n=note: on_note_click(n),
                animate=ft.Animation(120, ft.AnimationCurve.EASE_IN_OUT),
                alignment=ft.Alignment.CENTER,
            )

        note_row = ft.Row(
            [build_note_btn(n) for n in BASE_NOTES],
            spacing=6,
            wrap=True,
        )

        sos_cb = ft.Checkbox(
            label="Sostenido (#)",
            value=state["sostenido"],
            active_color="#6c5ce7",
            check_color="#ffffff",
            disabled=_sostenido_disabled(),
            label_style=ft.TextStyle(color=colors["text_primary"], size=14),
            on_change=lambda e: state.update({"sostenido": e.control.value}),
        )
        menor_cb = ft.Checkbox(
            label="Menor",
            value=state["menor"],
            active_color="#6c5ce7",
            check_color="#ffffff",
            label_style=ft.TextStyle(color=colors["text_primary"], size=14),
            on_change=lambda e: state.update({"menor": e.control.value}),
        )

        def on_note_click(note):
            state["note"] = None if state["note"] == note else note
            # Disable sostenido for Mi and Si; clear its value if needed
            disabled = state["note"] in NO_SOSTENIDO
            if disabled:
                state["sostenido"] = False
                sos_cb.value = False
            sos_cb.disabled = disabled
            note_row.controls = [build_note_btn(n) for n in BASE_NOTES]
            note_row.update()
            sos_cb.update()

        characters = self.app.get_characters()
        char_dd = ft.Dropdown(
            value=state["character"] or "Todos los caracteres",
            options=[ft.dropdown.Option("Todos los caracteres")]
            + [ft.dropdown.Option(c) for c in characters],
            bgcolor=colors["bg_secondary"],
            color=colors["text_primary"],
            border_color=colors["border_color"],
            focused_border_color=colors["border_focused"],
            border_radius=10,
            text_size=14,
            expand=True,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            on_select=lambda e: state.update(
                {"character": "" if e.control.value == "Todos los caracteres" else e.control.value}
            ),
        )

        ritmo_dd = ft.Dropdown(
            value=state["ritmo"] or "Todos los ritmos",
            options=[
                ft.dropdown.Option("Todos los ritmos"),
                ft.dropdown.Option("Lento"),
                ft.dropdown.Option("Moderado"),
                ft.dropdown.Option("Rápido"),
            ],
            bgcolor=colors["bg_secondary"],
            color=colors["text_primary"],
            border_color=colors["border_color"],
            focused_border_color=colors["border_focused"],
            border_radius=10,
            text_size=14,
            expand=True,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            on_select=lambda e: state.update(
                {"ritmo": "" if e.control.value == "Todos los ritmos" else e.control.value}
            ),
        )

        def _label(text):
            return ft.Text(
                text, size=10, weight=ft.FontWeight.W_700,
                color=colors["text_secondary"],
            )

        def on_clear(e):
            state.update({"note": None, "sostenido": False, "menor": False, "character": "", "ritmo": ""})
            note_row.controls = [build_note_btn(n) for n in BASE_NOTES]
            sos_cb.value = False
            sos_cb.disabled = False
            menor_cb.value = False
            char_dd.value = "Todos los caracteres"
            ritmo_dd.value = "Todos los ritmos"
            self.page.update()

        def on_apply(e):
            self._filter_note = state["note"]
            self._filter_sostenido = state["sostenido"]
            self._filter_menor = state["menor"]
            self._filter_character = state["character"]
            self._filter_ritmo = state["ritmo"]
            dialog.open = False
            self.page.update()
            self.search_handler(None)

        def on_cancel(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.TUNE_ROUNDED, color="#6c5ce7", size=18),
                        width=32,
                        height=32,
                        bgcolor=ft.Colors.with_opacity(0.12, "#6c5ce7"),
                        border_radius=8,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Text(
                        "Filtros de búsqueda", size=16,
                        weight=ft.FontWeight.BOLD, color=colors["text_primary"],
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=colors["bg_secondary"],
            title_padding=ft.Padding.only(left=20, top=18, right=20, bottom=12),
            content_padding=ft.Padding.only(left=20, right=20, top=0, bottom=20),
            actions_padding=ft.Padding.all(0),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Divider(height=1, color=colors["border_color"], thickness=0.5),
                        ft.Container(height=14),
                        _label("TONO MUSICAL"),
                        ft.Container(height=8),
                        note_row,
                        ft.Container(height=14),
                        _label("MODIFICADORES"),
                        ft.Container(height=6),
                        ft.Row(
                            [
                                ft.Container(content=sos_cb, expand=True),
                                ft.Container(content=menor_cb, expand=True),
                            ],
                            spacing=0,
                        ),
                        ft.Container(height=12),
                        _label("CARÁCTER"),
                        ft.Container(height=6),
                        char_dd,
                        ft.Container(height=10),
                        _label("TEMPO"),
                        ft.Container(height=6),
                        ritmo_dd,
                        ft.Container(height=16),
                        ft.Row(
                            [
                                ft.OutlinedButton(
                                    content=ft.Row(
                                        [
                                            ft.Icon(
                                                ft.Icons.FILTER_ALT_OFF_ROUNDED,
                                                size=15,
                                                color="#ff7675",
                                            ),
                                            ft.Text(
                                                "Limpiar filtros",
                                                color="#ff7675",
                                                size=13,
                                                weight=ft.FontWeight.W_600,
                                            ),
                                        ],
                                        spacing=8,
                                        tight=True,
                                        alignment=ft.MainAxisAlignment.CENTER,
                                    ),
                                    style=ft.ButtonStyle(
                                        side=ft.BorderSide(1.5, "#ff7675"),
                                        shape=ft.RoundedRectangleBorder(radius=10),
                                        padding=ft.Padding.symmetric(vertical=11),
                                        overlay_color=ft.Colors.with_opacity(0.08, "#ff7675"),
                                    ),
                                    expand=True,
                                    on_click=on_clear,
                                ),
                            ],
                            expand=True,
                        ),
                        ft.Container(height=10),
                        ft.Divider(height=1, color=colors["border_color"], thickness=0.5),
                        ft.Container(height=10),
                        ft.Row(
                            [
                                ft.TextButton(
                                    content=ft.Text(
                                        "Cancelar",
                                        size=14,
                                        weight=ft.FontWeight.W_500,
                                        color=colors["text_secondary"],
                                    ),
                                    on_click=on_cancel,
                                    expand=True,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                        padding=ft.Padding.symmetric(vertical=11),
                                        overlay_color=ft.Colors.with_opacity(0.06, colors["text_secondary"]),
                                    ),
                                ),
                                ft.FilledButton(
                                    content=ft.Row(
                                        [
                                            ft.Text("Aplicar", color="#ffffff", size=14, weight=ft.FontWeight.W_600),
                                            ft.Icon(ft.Icons.CHECK_ROUNDED, color="#ffffff", size=16),
                                        ],
                                        spacing=6,
                                        tight=True,
                                        alignment=ft.MainAxisAlignment.CENTER,
                                    ),
                                    on_click=on_apply,
                                    expand=True,
                                    style=ft.ButtonStyle(
                                        bgcolor="#6c5ce7",
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                        padding=ft.Padding.symmetric(vertical=11),
                                        overlay_color=ft.Colors.with_opacity(0.15, "#ffffff"),
                                    ),
                                ),
                            ],
                            spacing=8,
                            expand=True,
                        ),
                        ft.Container(height=2),
                    ],
                    spacing=0,
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=320,
            ),
            actions=[],
        )

        if dialog not in self.page.overlay:
            self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def update_results(self, songs):
        self.results_column.controls.clear()
        if not songs:
            self.results_column.controls.append(
                create_empty_state(self.page, "No hay canciones")
            )
        else:
            for song in songs:
                self.results_column.controls.append(
                    create_song_card(
                        self.page,
                        song,
                        lambda s=song: asyncio.create_task(self.go_to_edit(s)),
                    )
                )
        self.page.update()

    def search_handler(self, e):
        query = self.search_field.value.strip() if self.search_field.value else ""
        key = self._build_filter_key()
        songs = self.app.search_songs(query, key, self._filter_character, self._filter_ritmo)
        self.update_results(songs)

    def clear_filters_handler(self, e):
        self.search_field.value = ""
        self._filter_note = None
        self._filter_sostenido = False
        self._filter_menor = False
        self._filter_character = ""
        self._filter_ritmo = ""
        self.search_handler(None)

    async def go_to_edit(self, song):
        self.page.session.store.set("editing_song", song)
        await self.page.push_route("/edit")

    def refresh_character_options(self):
        # Characters are fetched fresh each time the dialog opens — no-op here
        pass

    def refresh_theme(self):
        colors = get_theme_colors(self.page)
        self.search_field.border_color = colors["border_color"]
        self.search_field.bgcolor = colors["bg_secondary"]
        self.search_field.color = colors["text_primary"]
        self.update_results(
            self.app.search_songs(
                self.search_field.value.strip() if self.search_field.value else "",
                self._build_filter_key(),
                self._filter_character,
                self._filter_ritmo,
            )
        )

    def build(self):
        colors = get_theme_colors(self.page)
        self.refresh_theme()

        has_filters = self._has_active_filters()

        filter_btn = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.FILTER_ALT_ROUNDED,
                icon_color="#6c5ce7" if has_filters else colors["text_secondary"],
                icon_size=19,
                on_click=self._open_filter_dialog,
                tooltip="Filtros",
            ),
            bgcolor=colors["bg_secondary"],
            border_radius=10,
            border=ft.Border.all(
                1.5 if has_filters else 1,
                "#6c5ce7" if has_filters else colors["border_color"],
            ),
            width=42,
            height=42,
            alignment=ft.Alignment.CENTER,
        )

        header = create_header(
            self.page,
            "Canciones",
            ["#6c5ce7", "#a29bfe"],
            right_buttons=[
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.Icons.TUNE_ROUNDED,
                        icon_color=colors["text_secondary"],
                        icon_size=19,
                        on_click=lambda e: asyncio.create_task(
                            self.page.push_route("/settings")
                        ),
                        tooltip="Configuración",
                        style=ft.ButtonStyle(
                            overlay_color=ft.Colors.with_opacity(0.08, "#6c5ce7"),
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                    ),
                    width=38,
                    height=38,
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(0.06, "#6c5ce7"),
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.ADD_ROUNDED, color="#ffffff", size=16),
                            ft.Text("Agregar", color="#ffffff", size=12,
                                    weight=ft.FontWeight.W_600),
                        ],
                        spacing=6,
                        tight=True,
                    ),
                    height=36,
                    alignment=ft.Alignment.CENTER,
                    gradient=ft.LinearGradient(
                        colors=["#00b894", "#00cec9"],
                        begin=ft.Alignment.TOP_LEFT,
                        end=ft.Alignment.BOTTOM_RIGHT,
                    ),
                    border_radius=14,
                    padding=ft.Padding.symmetric(horizontal=14),
                    shadow=ft.BoxShadow(
                        blur_radius=14,
                        spread_radius=0,
                        color=ft.Colors.with_opacity(0.35, "#00b894"),
                        offset=ft.Offset(0, 4),
                    ),
                    on_click=lambda e: asyncio.create_task(self.page.push_route("/add")),
                    ink=True,
                ),
            ],
        )

        search_row = ft.Container(
            content=ft.Row(
                [self.search_field, filter_btn],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        )

        results = ft.Container(
            content=self.results_column,
            padding=ft.Padding.only(left=16, right=16, bottom=16),
            expand=True,
        )

        return ft.View(
            route="/",
            controls=[
                ft.SafeArea(
                    content=ft.Column(
                        controls=[header, search_row, results],
                        spacing=0,
                        expand=True,
                    ),
                    expand=True,
                )
            ],
            bgcolor=colors["bg_primary"],
            padding=0,
        )