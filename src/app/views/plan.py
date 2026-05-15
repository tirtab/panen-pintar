"""7-day plan view for the recommended decision option."""

from __future__ import annotations

import flet as ft

from app.data import format_currency
from app.store import AppState
from app.theme import PALETTE, RADIUS, SPACING
from app.ui import back_header, card, ghost_button, pill, primary_button, section_title


def view(state: AppState) -> ft.Control:
    result = state.last_result
    if result is None:
        return ft.Column(
            [
                back_header(
                    title="Belum ada rencana",
                    subtitle="Buat analisis lebih dulu",
                    on_back=lambda _: state.navigate("dashboard"),
                ),
            ]
        )

    option = result.recommended

    header_card = card(
        bgcolor=PALETTE.primary_soft,
        border_color=PALETTE.primary_soft,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Text(option.icon, size=20),
                            width=44,
                            height=44,
                            bgcolor=ft.Colors.WHITE,
                            border_radius=RADIUS["pill"],
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    option.title,
                                    size=16,
                                    weight=ft.FontWeight.W_700,
                                    color=PALETTE.text_strong,
                                ),
                                ft.Text(
                                    option.subtitle,
                                    size=12,
                                    color=PALETTE.text,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        pill(
                            "7 Hari",
                            color=PALETTE.primary,
                            bgcolor=ft.Colors.WHITE,
                            icon=ft.Icons.CALENDAR_TODAY_ROUNDED,
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        _mini_stat("Profit", format_currency(option.profit), PALETTE.primary),
                        _mini_stat("Biaya", format_currency(option.cost), PALETTE.info),
                        _mini_stat("Hasil", f"{option.expected_yield_kg} kg", PALETTE.accent),
                    ],
                    spacing=SPACING["sm"],
                ),
            ],
            spacing=SPACING["md"],
        ),
    )

    timeline_items: list[ft.Control] = []
    steps = option.plan_steps or ["Belum ada langkah untuk opsi ini."]
    for index, step in enumerate(steps, start=1):
        timeline_items.append(_timeline_row(index, step, last=index == len(steps)))

    timeline_card = card(content=ft.Column(timeline_items, spacing=0))

    pitch_card = card(
        bgcolor=PALETTE.accent_soft,
        border_color=PALETTE.accent_soft,
        content=ft.Column(
            [
                ft.Text(
                    "Tunjukkan ke penyuluh",
                    size=13,
                    weight=ft.FontWeight.W_700,
                    color=PALETTE.text_strong,
                ),
                ft.Text(
                    "Anda dapat menunjukkan ringkasan ini kepada penyuluh "
                    "atau toko pertanian untuk konfirmasi dan pembelian "
                    "kebutuhan yang sesuai.",
                    size=12,
                    color=PALETTE.text,
                ),
            ],
            spacing=4,
        ),
    )

    return ft.Column(
        controls=[
            back_header(
                title="Rencana 7 Hari",
                subtitle="Langkah harian sesuai keputusan terbaik",
                on_back=lambda _: state.navigate("analysis"),
            ),
            header_card,
            section_title("Linimasa tindakan"),
            timeline_card,
            pitch_card,
            primary_button(
                "Selesai, simpan ke riwayat",
                on_click=lambda _: (state.show_snack("Rencana disimpan"), state.navigate("dashboard")),
                icon=ft.Icons.CHECK_ROUNDED,
                expand=True,
            ),
            ghost_button(
                "Ubah keputusan",
                on_click=lambda _: state.navigate("analysis"),
                icon=ft.Icons.SWAP_HORIZ_ROUNDED,
            ),
            ft.Container(height=SPACING["xl"]),
        ],
        spacing=SPACING["md"],
    )


def _mini_stat(label: str, value: str, accent: str) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(label, size=11, color=PALETTE.text_muted),
                ft.Text(
                    value,
                    size=14,
                    weight=ft.FontWeight.W_700,
                    color=accent,
                ),
            ],
            spacing=2,
        ),
        expand=True,
        padding=ft.Padding.symmetric(horizontal=12, vertical=10),
        bgcolor=ft.Colors.WHITE,
        border_radius=RADIUS["md"],
    )


def _timeline_row(index: int, text: str, *, last: bool) -> ft.Control:
    dot = ft.Container(
        content=ft.Text(
            str(index),
            size=12,
            weight=ft.FontWeight.W_700,
            color=ft.Colors.WHITE,
        ),
        width=28,
        height=28,
        bgcolor=PALETTE.primary,
        border_radius=RADIUS["pill"],
        alignment=ft.Alignment.CENTER,
    )

    line = ft.Container(
        width=2,
        height=24 if not last else 0,
        bgcolor=PALETTE.primary_soft,
    )

    return ft.Row(
        [
            ft.Column(
                [dot, line],
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(
                content=ft.Text(text, size=13, color=PALETTE.text),
                expand=True,
                padding=ft.Padding.only(top=4, bottom=12, left=4),
            ),
        ],
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )
