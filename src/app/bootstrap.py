"""Application bootstrap: configures the Flet page and mounts the shell."""

from __future__ import annotations

import flet as ft

from app.shell import build_shell
from app.store import AppState
from app.theme import PALETTE


def _loading_screen() -> ft.Control:
    return ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Text("🌱", size=36),
                    width=72,
                    height=72,
                    bgcolor=PALETTE.primary_soft,
                    border_radius=36,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.ProgressRing(color=PALETTE.primary, width=28, height=28),
                ft.Text(
                    "Memuat PanenPintar...",
                    size=18,
                    weight=ft.FontWeight.W_700,
                    color=PALETTE.text_strong,
                ),
                ft.Text(
                    "Menyiapkan engine keputusan dan tampilan aplikasi",
                    size=12,
                    color=PALETTE.text_muted,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        expand=True,
        alignment=ft.Alignment.CENTER,
        padding=24,
        bgcolor=PALETTE.surface_alt,
    )


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

    root = ft.Container(content=_loading_screen(), expand=True)
    page.add(root)
    page.update()

    state = AppState(page=page)
    shell = build_shell(state)

    root.content = ft.SafeArea(content=shell, expand=True)
    page.update()
