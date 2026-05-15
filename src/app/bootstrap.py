"""Application bootstrap: configures the Flet page and mounts the shell."""

from __future__ import annotations

import flet as ft

from app.shell import build_shell
from app.store import AppState
from app.theme import PALETTE


def bootstrap(page: ft.Page) -> None:
    page.title = "PanenPintar"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = PALETTE.surface_alt
    page.padding = 0
    page.spacing = 0
    page.theme = ft.Theme(
        color_scheme_seed=PALETTE.primary,
        use_material3=True,
    )

    # Start at a comfortable desktop size; the layout adapts to mobile widths
    # automatically when the window is resized smaller.
    page.window.width = 1100
    page.window.height = 780
    page.window.min_width = 360
    page.window.min_height = 600

    state = AppState(page=page)
    shell = build_shell(state)

    page.add(ft.SafeArea(content=shell, expand=True))
