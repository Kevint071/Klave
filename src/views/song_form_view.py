import asyncio
import flet as ft
from components import create_header, show_snackbar
from .theme_utils import get_theme_colors

BASE_NOTES = ["Do", "Re", "Mi", "Fa", "Sol", "La", "Si"]

_ACCENT_GRAD = ["#6c5ce7", "#a29bfe"]   # gradient stays fixed
_WHITE       = "#ffffff"


class SongFormView:
    """Vista base para agregar/editar canciones"""

    def __init__(self, page, app, route, title, header_colors):
        self.page = page
        self.app = app
        self.route = route
        self.title = title
        self.header_colors = header_colors

        # Key state
        self.selected_note = None
        self.sostenido = False
        self.menor = False

        # Character state
        self.selected_characters = set()

        # Tempo state
        self.tempo_value = None  # "Lenta" | "Rápida"

        # Persistent controls
        self.title_field = self._create_title_field()
        self._note_buttons_row = ft.Row(
            [],
            spacing=6,
            run_spacing=6,
            wrap=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self._char_column = ft.Column([], spacing=4)
        self._sostenido_cb = None
        self._menor_cb = None
        self._tempo_radio = None

    # ── Theme color helper ────────────────────────────────────────────────────

    @property
    def _c(self):
        return get_theme_colors(self.page)

    # ── Title field ───────────────────────────────────────────────────────────

    def _create_title_field(self):
        c = self._c
        return ft.TextField(
            hint_text="Ingresa el nombre de la canción",
            hint_style=ft.TextStyle(color=c["text_secondary"], size=13),
            border_color=c["border_color"],
            focused_border_color=c["border_focused"],
            bgcolor=c["bg_secondary"],
            color=c["text_primary"],
            text_size=14,
            border_radius=10,
            content_padding=ft.Padding(left=14, right=14, top=14, bottom=14),
            expand=True,
            cursor_color=c["border_focused"],
        )

    # ── Key helpers ───────────────────────────────────────────────────────────

    def _get_key_value(self):
        if not self.selected_note:
            return ""
        key = self.selected_note
        if self.sostenido:
            key += "#"
        if self.menor:
            key += " Menor"
        return key

    def _parse_key(self, key_str):
        if not key_str:
            return None, False, False
        menor = key_str.endswith(" Menor")
        clean = key_str.replace(" Menor", "")
        sostenido = clean.endswith("#")
        note = clean.rstrip("#")
        if note not in BASE_NOTES:
            return None, False, False
        return note, sostenido, menor

    # ── Note buttons ──────────────────────────────────────────────────────────

    def _build_note_btn(self, note):
        c = self._c
        selected = self.selected_note == note
        width = 46 if len(note) == 3 else 40
        return ft.Container(
            content=ft.Text(
                note,
                style=ft.TextStyle(
                    size=13,
                    height=1,
                    weight=ft.FontWeight.W_700,
                    color=_WHITE if selected else c["text_primary"],
                ),
            ),
            width=width,
            height=34,
            alignment=ft.Alignment.CENTER,
            bgcolor=c["border_focused"] if selected else c["bg_secondary"],
            border_radius=20,
            padding=ft.Padding(left=4, right=4, top=2, bottom=2),
            border=ft.Border.all(
                1.5 if selected else 1,
                c["border_focused"] if selected else c["border_color"],
            ),
            on_click=lambda e, n=note: self._on_note_click(n),
            animate=ft.Animation(curve=ft.AnimationCurve.EASE_IN_OUT, duration=200),
            ink=True,
        )

    def _on_note_click(self, note):
        self.selected_note = None if self.selected_note == note else note
        self._refresh_note_row()

    def _refresh_note_row(self):
        self._note_buttons_row.controls = [self._build_note_btn(n) for n in BASE_NOTES]
        try:
            if self._note_buttons_row.page:
                self._note_buttons_row.update()
        except Exception:
            pass

    # ── Modifier checkboxes ───────────────────────────────────────────────────

    def _build_modifier_row(self):
        c = self._c
        self._sostenido_cb = ft.Checkbox(
            label="Sostenido (#)",
            value=self.sostenido,
            active_color=c["border_focused"],
            check_color=_WHITE,
            label_style=ft.TextStyle(color=c["text_primary"], size=13),
            on_change=lambda e: self._on_modifier("sostenido", e.control.value),
        )
        self._menor_cb = ft.Checkbox(
            label="Menor",
            value=self.menor,
            active_color=c["border_focused"],
            check_color=_WHITE,
            label_style=ft.TextStyle(color=c["text_primary"], size=13),
            on_change=lambda e: self._on_modifier("menor", e.control.value),
        )
        return ft.Row([self._sostenido_cb, self._menor_cb], spacing=20)

    def _on_modifier(self, mod, value):
        if mod == "sostenido":
            self.sostenido = value
        else:
            self.menor = value

    # ── Character checkboxes ──────────────────────────────────────────────────

    def _build_character_section(self):
        c = self._c
        characters = self.app.get_characters()
        if not characters:
            self._char_column.controls = [
                ft.Text(
                    "No hay caracteres configurados",
                    size=13,
                    color=c["text_secondary"],
                    italic=True,
                )
            ]
            return self._char_column

        checkboxes = [
            ft.Checkbox(
                label=ch,
                value=ch in self.selected_characters,
                active_color=c["border_focused"],
                check_color=_WHITE,
                label_style=ft.TextStyle(color=c["text_primary"], size=13),
                on_change=lambda e, ch=ch: self._on_char_toggle(ch, e.control.value),
            )
            for ch in characters
        ]
        # 2-column grid matching the screenshot
        rows = [
            ft.Row(
                [ft.Container(content=cb, expand=True) for cb in checkboxes[i : i + 2]],
                spacing=4,
            )
            for i in range(0, len(checkboxes), 2)
        ]
        self._char_column.controls = list[ft.Control](rows)
        return self._char_column

    def _on_char_toggle(self, char, value):
        if value:
            self.selected_characters.add(char)
        else:
            self.selected_characters.discard(char)

    def refresh_character_options(self):
        self._build_character_section()
        try:
            if self._char_column.page:
                self._char_column.update()
        except Exception:
            pass

    # ── Tempo radio ───────────────────────────────────────────────────────────

    def _build_tempo_row(self):
        c = self._c
        self._tempo_radio = ft.RadioGroup(
            content=ft.Row(
                [
                    ft.Radio(
                        value="Lenta",
                        label="Lenta",
                        label_style=ft.TextStyle(color=c["text_primary"], size=14),
                        fill_color=ft.Colors.with_opacity(1, c["border_focused"]),
                    ),
                    ft.Radio(
                        value="Rápida",
                        label="Rápida",
                        label_style=ft.TextStyle(color=c["text_primary"], size=14),
                        fill_color=ft.Colors.with_opacity(1, c["border_focused"]),
                    ),
                ],
                spacing=24,
            ),
            value=self.tempo_value,
            on_change=lambda e: setattr(self, "tempo_value", e.control.value),
        )
        return self._tempo_radio

    # ── Section block (left purple bar + label) ───────────────────────────────

    def _section_block(self, label, content):
        c = self._c
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                width=3, height=18,
                                bgcolor=c["border_focused"],
                                border_radius=2,
                            ),
                            ft.Text(
                                label,
                                size=13,
                                weight=ft.FontWeight.W_700,
                                color=c["text_primary"],
                            ),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    content,
                ],
                spacing=10,
            ),
            padding=ft.Padding.symmetric(vertical=10),
        )

    def _section_divider(self):
        return ft.Divider(
            height=1,
            thickness=0.8,
            color=ft.Colors.with_opacity(0.4, self._c["border_color"]),
        )

    # ── Theme refresh ─────────────────────────────────────────────────────────

    def refresh_theme(self):
        c = self._c
        self.title_field.border_color = c["border_color"]
        self.title_field.focused_border_color = c["border_focused"]
        self.title_field.bgcolor = c["bg_secondary"]
        self.title_field.color = c["text_primary"]
        self._refresh_note_row()

    # ── State management ──────────────────────────────────────────────────────

    def clear_form(self):
        self.title_field.value = ""
        self.selected_note = None
        self.sostenido = False
        self.menor = False
        self.selected_characters = set()
        self.tempo_value = None
        try:
            self.title_field.update()
        except Exception:
            pass

    def load_song_data(self, song):
        self.title_field.value = str(song["title"])
        note, sostenido, menor = self._parse_key(song.get("key", ""))
        self.selected_note = note
        self.sostenido = sostenido
        self.menor = menor

        chars = song.get("character", "")
        if isinstance(chars, list):
            self.selected_characters = {str(c) for c in chars}
        elif chars:
            self.selected_characters = {c.strip() for c in str(chars).split(",") if c.strip()}
        else:
            self.selected_characters = set()

        tempo = song.get("tempo", "")
        self.tempo_value = tempo if tempo in ("Lenta", "Rápida") else None

    # ── Save handler ──────────────────────────────────────────────────────────

    async def save_song_handler(self, main_view):
        if not self.title_field.value or not self.title_field.value.strip():
            show_snackbar(self.page, "El nombre de la canción es obligatorio", "#ff7675")
            return

        editing_song = self.page.session.store.get("editing_song")
        key_value = self._get_key_value()
        tempo_value = self.tempo_value or ""
        characters_str = (
            ",".join(sorted(self.selected_characters)) if self.selected_characters else ""
        )

        if not key_value and not characters_str and not tempo_value:
            show_snackbar(
                self.page,
                "Selecciona al menos un Tono, Carácter o Tempo",
                "#ff7675",
            )
            return

        if editing_song:
            self.app.update_song(
                editing_song["id"],
                title=self.title_field.value.strip(),
                key=key_value,
                character=characters_str,
                tempo=tempo_value,
            )
            self.page.session.store.set("editing_song", None)
            show_snackbar(self.page, "Canción actualizada exitosamente", "#00b894")
        else:
            self.app.add_song(
                self.title_field.value.strip(),
                key=key_value,
                character=characters_str,
                tempo=tempo_value,
            )
            show_snackbar(self.page, "Canción agregada exitosamente", "#00b894")

        self.clear_form()
        # No llamar search_handler aquí: route_change() lo hace en la Fase 2
        # después de navegar, evitando un page.update() redundante antes de push_route.
        await self.page.push_route("/")
        # Guardar en disco en thread separado para no bloquear el event loop
        await self.app.save_async()

    # ── Build ─────────────────────────────────────────────────────────────────

    def build(self, main_view, extra_buttons=None):
        c = self._c
        self.refresh_theme()

        # Rebuild note row with current state
        self._note_buttons_row.controls = [self._build_note_btn(n) for n in BASE_NOTES]

        right_buttons = list(extra_buttons) if extra_buttons else []
        editing_song = self.page.session.store.get("editing_song")

        header = create_header(
            self.page,
            self.title,
            self.header_colors,
            left_button=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=c["text_primary"],
                icon_size=24,
                on_click=lambda e: asyncio.create_task(self.page.push_route("/")),
                tooltip="Volver",
            ),
            right_buttons=right_buttons,
        )

        # ── Save button ──────────────────────────────────────────────────────
        save_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        ft.Icons.SAVE_ROUNDED if editing_song else ft.Icons.ADD_ROUNDED,
                        color=_WHITE,
                        size=18,
                    ),
                    ft.Text(
                        "Guardar cambios" if editing_song else "Añadir canción",
                        color=_WHITE,
                        size=14,
                        weight=ft.FontWeight.W_600,
                    ),
                ],
                spacing=8,
                tight=True,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            gradient=ft.LinearGradient(
                colors=_ACCENT_GRAD,
                begin=ft.Alignment.CENTER_LEFT,
                end=ft.Alignment.CENTER_RIGHT,
            ),
            border_radius=14,
            padding=ft.Padding.symmetric(vertical=16),
            shadow=ft.BoxShadow(
                blur_radius=20,
                spread_radius=0,
                color=ft.Colors.with_opacity(0.40, c["border_focused"]),
                offset=ft.Offset(0, 4),
            ),
            on_click=lambda e: asyncio.create_task(self.save_song_handler(main_view)),
            expand=True,
            alignment=ft.Alignment.CENTER,
        )

        # ── Form layout matching screenshot ──────────────────────────────────
        form_content = ft.Column(
            [
                # ─ Song title ─────────────────────────────────────────────
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Nombre de la canción:",
                                size=13,
                                weight=ft.FontWeight.W_700,
                                color=c["text_primary"],
                            ),
                            ft.Container(height=8),
                            ft.Row([self.title_field], expand=True),
                        ],
                        spacing=0,
                    ),
                    padding=ft.Padding.symmetric(vertical=10),
                ),

                self._section_divider(),

                # ─ Tono ───────────────────────────────────────────────────
                self._section_block(
                    "Tono:",
                    ft.Column(
                        [
                            self._note_buttons_row,
                            ft.Container(height=4),
                            ft.Text(
                                "Modificadores:",
                                size=12,
                                weight=ft.FontWeight.W_500,
                                color=c["text_secondary"],
                            ),
                            self._build_modifier_row(),
                        ],
                        spacing=8,
                    ),
                ),

                self._section_divider(),

                # ─ Caracteres ─────────────────────────────────────────────
                self._section_block(
                    "Seleccionar caracteres:",
                    self._build_character_section(),
                ),

                self._section_divider(),

                # ─ Tempo ──────────────────────────────────────────────────
                self._section_block(
                    "Tempo:",
                    self._build_tempo_row(),
                ),

                ft.Container(height=20),

                # ─ Save button ────────────────────────────────────────────
                ft.Row([save_btn]),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        )

        return ft.View(
            route=self.route,
            controls=[
                header,
                ft.Container(
                    content=form_content,
                    padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                    expand=True,
                ),
            ],
            bgcolor=c["bg_primary"],
            padding=0,
        )