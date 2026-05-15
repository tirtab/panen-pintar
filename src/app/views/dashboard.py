"""Dashboard / home view for PanenPintar."""

from __future__ import annotations

import flet as ft

from app.data import CROPS, format_currency
from app.store import AppState
from app.theme import PALETTE, RADIUS, SPACING
from app.ui import card, pill, primary_button, section_title, soft_shadow


def view(state: AppState) -> ft.Control:
    history_count = len(state.history)
    last = state.history[0] if state.history else None

    hero = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(
                                    f"Selamat datang, {state.farmer_name}",
                                    size=13,
                                    color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                                ),
                                ft.Text(
                                    "Mau buat keputusan apa hari ini?",
                                    size=20,
                                    weight=ft.FontWeight.W_700,
                                    color=ft.Colors.WHITE,
                                ),
                            ],
                            spacing=4,
                            expand=True,
                        ),
                        ft.Container(
                            content=ft.Text("🌱", size=22),
                            width=44,
                            height=44,
                            alignment=ft.Alignment.CENTER,
                            bgcolor=ft.Colors.with_opacity(0.18, ft.Colors.WHITE),
                            border_radius=RADIUS["pill"],
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(height=SPACING["md"]),
                ft.Row(
                    [
                        pill(
                            f"{history_count} keputusan",
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.with_opacity(0.18, ft.Colors.WHITE),
                            icon=ft.Icons.HISTORY_ROUNDED,
                        ),
                        pill(
                            "Mode offline",
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.with_opacity(0.18, ft.Colors.WHITE),
                            icon=ft.Icons.WIFI_OFF_ROUNDED,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Container(height=SPACING["lg"]),
                primary_button(
                    "Buat keputusan baru",
                    on_click=lambda _: state.navigate("form"),
                    icon=ft.Icons.AUTO_AWESOME_ROUNDED,
                    expand=True,
                ),
            ],
            spacing=0,
        ),
        padding=SPACING["lg"],
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[PALETTE.primary_dark, PALETTE.primary],
        ),
        border_radius=RADIUS["xl"],
        shadow=soft_shadow(opacity=0.12, offset_y=10, blur=24),
    )

    crop_cards = [
        ft.Container(
            content=ft.Column(
                [
                    ft.Text(crop.emoji, size=26),
                    ft.Text(
                        crop.name,
                        size=13,
                        weight=ft.FontWeight.W_700,
                        color=PALETTE.text_strong,
                    ),
                    ft.Text(
                        f"{format_currency(crop.base_price_per_kg)}/kg",
                        size=11,
                        color=PALETTE.text_muted,
                    ),
                ],
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
            padding=SPACING["md"],
            bgcolor=PALETTE.surface,
            border_radius=RADIUS["md"],
            border=ft.Border.all(1, PALETTE.border),
            width=120,
            on_click=lambda _e, key=crop.key: state.navigate("form", crop=key),
            ink=True,
        )
        for crop in CROPS
    ]

    crops_row = ft.Row(
        controls=crop_cards,
        spacing=SPACING["sm"],
        scroll=ft.ScrollMode.HIDDEN,
    )

    last_result_card: ft.Control
    if last is None:
        last_result_card = card(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.LIGHTBULB_OUTLINE_ROUNDED,
                            color=PALETTE.accent,
                            size=22,
                        ),
                        padding=10,
                        bgcolor=PALETTE.accent_soft,
                        border_radius=RADIUS["pill"],
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                "Belum ada keputusan",
                                size=14,
                                weight=ft.FontWeight.W_700,
                                color=PALETTE.text_strong,
                            ),
                            ft.Text(
                                "Buat analisis pertama untuk melihat saran terbaik.",
                                size=12,
                                color=PALETTE.text_muted,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
    else:
        profit_color = PALETTE.primary if last.recommended_profit >= 0 else PALETTE.danger
        last_result_card = card(
            on_click=lambda _: state.navigate("history"),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                last.crop_name,
                                size=15,
                                weight=ft.FontWeight.W_700,
                                color=PALETTE.text_strong,
                            ),
                            pill(
                                last.recommended_title,
                                color=PALETTE.primary,
                                bgcolor=PALETTE.primary_soft,
                                icon=ft.Icons.CHECK_CIRCLE_ROUNDED,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(last.summary, size=12, color=PALETTE.text_muted, max_lines=2),
                    ft.Row(
                        [
                            ft.Text(
                                "Estimasi profit",
                                size=11,
                                color=PALETTE.text_muted,
                            ),
                            ft.Text(
                                format_currency(last.recommended_profit),
                                size=16,
                                weight=ft.FontWeight.W_800,
                                color=profit_color,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                spacing=8,
            ),
        )

    tip_card = card(
        bgcolor=PALETTE.accent_soft,
        border_color=PALETTE.accent_soft,
        content=ft.Row(
            [
                ft.Text("💡", size=22),
                ft.Column(
                    [
                        ft.Text(
                            "Tahukah Anda?",
                            size=13,
                            weight=ft.FontWeight.W_700,
                            color=PALETTE.text_strong,
                        ),
                        ft.Text(
                            "Menurut FAO, hama dan penyakit dapat menyebabkan "
                            "kehilangan hasil hingga 40% per musim. Tindakan "
                            "cepat dalam 3 hari pertama mampu menyelamatkan "
                            "sebagian besar panen.",
                            size=12,
                            color=PALETTE.text,
                        ),
                    ],
                    spacing=4,
                    expand=True,
                ),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
    )

    disclaimer_card = ft.Container(
        content=ft.Row(
            [
                ft.Icon(
                    ft.Icons.INFO_OUTLINE_ROUNDED,
                    color=PALETTE.text_muted,
                    size=16,
                ),
                ft.Text(
                    "Rekomendasi bersifat estimasi cepat berbasis aturan. "
                    "Konsultasikan keputusan besar dengan penyuluh pertanian.",
                    size=11,
                    color=PALETTE.text_muted,
                    expand=True,
                ),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
        padding=12,
    )

    return ft.Column(
        controls=[
            hero,
            section_title("Pilih komoditas Anda"),
            crops_row,
            section_title(
                "Keputusan terakhir",
                action=ft.TextButton(
                    content="Lihat semua",
                    on_click=lambda _: state.navigate("history"),
                    style=ft.ButtonStyle(color=PALETTE.primary),
                ),
            ),
            last_result_card,
            section_title("Tips hari ini"),
            tip_card,
            disclaimer_card,
            ft.Container(height=SPACING["xl"]),
        ],
        spacing=SPACING["md"],
    )
