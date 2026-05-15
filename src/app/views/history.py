"""History view of past decisions."""

from __future__ import annotations

import flet as ft

from app.data import format_currency
from app.store import AppState
from app.theme import PALETTE, RADIUS, RISK_COLORS, RISK_LABELS, SPACING
from app.ui import card, empty_state, pill, primary_button, section_title


def view(state: AppState) -> ft.Control:
    if not state.history:
        return ft.Column(
            [
                ft.Container(height=SPACING["md"]),
                ft.Text(
                    "Riwayat keputusan",
                    size=22,
                    weight=ft.FontWeight.W_800,
                    color=PALETTE.text_strong,
                ),
                ft.Text(
                    "Setiap analisis tersimpan otomatis di sini.",
                    size=13,
                    color=PALETTE.text_muted,
                ),
                ft.Container(height=SPACING["xl"]),
                empty_state(
                    icon=ft.Icons.HISTORY_ROUNDED,
                    title="Belum ada riwayat",
                    body="Mulai analisis pertama untuk menyimpan keputusan Anda.",
                ),
                primary_button(
                    "Buat keputusan baru",
                    on_click=lambda _: state.navigate("form"),
                    icon=ft.Icons.ADD_ROUNDED,
                    expand=True,
                ),
            ],
            spacing=SPACING["sm"],
        )

    rows: list[ft.Control] = []
    for entry in state.history:
        color, bg = RISK_COLORS[entry.risk_level]
        profit_color = PALETTE.primary if entry.recommended_profit >= 0 else PALETTE.danger
        rows.append(
            card(
                on_click=lambda _e, eid=entry.id: state.open_history_entry(eid),
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    entry.crop_name,
                                    size=15,
                                    weight=ft.FontWeight.W_700,
                                    color=PALETTE.text_strong,
                                ),
                                pill(
                                    RISK_LABELS[entry.risk_level],
                                    color=color,
                                    bgcolor=bg,
                                    icon=ft.Icons.SHIELD_OUTLINED,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Text(
                            entry.summary,
                            size=12,
                            color=PALETTE.text_muted,
                            max_lines=2,
                        ),
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(
                                            "Rekomendasi",
                                            size=11,
                                            color=PALETTE.text_muted,
                                        ),
                                        ft.Text(
                                            entry.recommended_title,
                                            size=13,
                                            weight=ft.FontWeight.W_700,
                                            color=PALETTE.text_strong,
                                        ),
                                    ],
                                    spacing=2,
                                ),
                                ft.Column(
                                    [
                                        ft.Text(
                                            "Profit",
                                            size=11,
                                            color=PALETTE.text_muted,
                                        ),
                                        ft.Text(
                                            format_currency(entry.recommended_profit),
                                            size=14,
                                            weight=ft.FontWeight.W_800,
                                            color=profit_color,
                                        ),
                                    ],
                                    spacing=2,
                                    horizontal_alignment=ft.CrossAxisAlignment.END,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Row(
                            [
                                ft.Text(
                                    entry.created_at.strftime("%d %b %Y · %H:%M"),
                                    size=11,
                                    color=PALETTE.text_muted,
                                ),
                                ft.Row(
                                    [
                                        ft.Text(
                                            "Lihat detail",
                                            size=11,
                                            weight=ft.FontWeight.W_600,
                                            color=PALETTE.primary,
                                        ),
                                        ft.Icon(
                                            ft.Icons.ARROW_FORWARD_ROUNDED,
                                            size=12,
                                            color=PALETTE.primary,
                                        ),
                                    ],
                                    spacing=4,
                                    tight=True,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                    spacing=8,
                ),
            )
        )

    return ft.Column(
        controls=[
            ft.Container(height=SPACING["sm"]),
            ft.Text(
                "Riwayat keputusan",
                size=22,
                weight=ft.FontWeight.W_800,
                color=PALETTE.text_strong,
            ),
            ft.Text(
                f"{len(state.history)} keputusan tersimpan",
                size=13,
                color=PALETTE.text_muted,
            ),
            section_title("Terbaru lebih dulu"),
            *rows,
            ft.Container(height=SPACING["xl"]),
        ],
        spacing=SPACING["md"],
    )
