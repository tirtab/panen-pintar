"""Analysis result view showing 3 decision options."""

from __future__ import annotations

import flet as ft

from app.data import DecisionOption, format_currency
from app.store import AppState
from app.theme import PALETTE, RADIUS, RISK_COLORS, RISK_LABELS, SPACING
from app.ui import (
    back_header,
    card,
    ghost_button,
    pill,
    primary_button,
    risk_pill,
    section_title,
    stat_tile,
)


def view(state: AppState) -> ft.Control:
    result = state.last_result
    if result is None:
        return ft.Column(
            [
                back_header(
                    title="Belum ada analisis",
                    subtitle="Kembali dan isi data terlebih dulu",
                    on_back=lambda _: state.navigate("dashboard"),
                ),
                ft.Text(
                    "Buat analisis baru untuk melihat keputusan terbaik.",
                    color=PALETTE.text_muted,
                ),
            ]
        )

    summary_card = card(
        bgcolor=PALETTE.primary_soft,
        border_color=PALETTE.primary_soft,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            f"Hasil analisis · {result.crop_name}",
                            size=14,
                            weight=ft.FontWeight.W_700,
                            color=PALETTE.text_strong,
                        ),
                        risk_pill(result.risk_level),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(result.summary, size=13, color=PALETTE.text),
                ft.Row(
                    [
                        stat_tile(
                            label="Skor risiko",
                            value=f"{int(result.risk_score * 100)}%",
                            icon=ft.Icons.SHIELD_OUTLINED,
                            accent=RISK_COLORS[result.risk_level][0],
                        ),
                        stat_tile(
                            label="Rekomendasi",
                            value=result.recommended.title,
                            icon=ft.Icons.AUTO_AWESOME_ROUNDED,
                            accent=PALETTE.primary,
                        ),
                    ],
                    spacing=SPACING["sm"],
                ),
            ],
            spacing=SPACING["md"],
        ),
    )

    option_cards = [_option_card(state, opt) for opt in result.options]

    return ft.Column(
        controls=[
            back_header(
                title="Pilihan keputusan",
                subtitle="Bandingkan 3 opsi tindakan untuk Anda",
                on_back=lambda _: state.navigate("form"),
            ),
            summary_card,
            section_title("3 opsi tindakan"),
            *option_cards,
            ft.Container(height=SPACING["md"]),
            primary_button(
                "Lihat rencana 7 hari",
                on_click=lambda _: state.navigate("plan"),
                icon=ft.Icons.EVENT_NOTE_ROUNDED,
                expand=True,
            ),
            ghost_button(
                "Simpan & kembali ke beranda",
                on_click=lambda _: (state.show_snack("Keputusan disimpan ke riwayat"), state.navigate("dashboard")),
                icon=ft.Icons.BOOKMARK_OUTLINE_ROUNDED,
            ),
            ft.Container(height=SPACING["xl"]),
        ],
        spacing=SPACING["md"],
    )


def _option_card(state: AppState, option: DecisionOption) -> ft.Control:
    available = option.confidence > 0

    accent = option.accent_color
    badge: ft.Control
    if option.recommended:
        badge = pill(
            "Rekomendasi terbaik",
            color=PALETTE.primary,
            bgcolor=PALETTE.primary_soft,
            icon=ft.Icons.STAR_ROUNDED,
        )
    else:
        badge = ft.Container()

    if not available:
        body = ft.Column(
            [
                ft.Text(
                    "Opsi ini belum tersedia untuk kondisi saat ini.",
                    size=12,
                    color=PALETTE.text_muted,
                ),
                *[
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.INFO_OUTLINE_ROUNDED,
                                color=PALETTE.text_muted,
                                size=14,
                            ),
                            ft.Text(reason, size=12, color=PALETTE.text_muted, expand=True),
                        ],
                        spacing=8,
                    )
                    for reason in option.reasons
                ],
            ],
            spacing=6,
        )
    else:
        profit_color = PALETTE.primary if option.profit >= 0 else PALETTE.danger
        body = ft.Column(
            [
                ft.Row(
                    [
                        stat_tile(
                            label="Estimasi profit",
                            value=format_currency(option.profit),
                            icon=ft.Icons.TRENDING_UP_ROUNDED,
                            accent=profit_color,
                        ),
                        stat_tile(
                            label="Hasil panen",
                            value=f"{option.expected_yield_kg} kg",
                            icon=ft.Icons.AGRICULTURE_ROUNDED,
                            accent=accent,
                        ),
                    ],
                    spacing=SPACING["sm"],
                ),
                ft.Row(
                    [
                        stat_tile(
                            label="Biaya tindakan",
                            value=format_currency(option.cost),
                            icon=ft.Icons.PAYMENTS_ROUNDED,
                            accent=PALETTE.info,
                        ),
                        stat_tile(
                            label="Keyakinan",
                            value=f"{option.confidence}%",
                            icon=ft.Icons.BOLT_ROUNDED,
                            accent=PALETTE.accent,
                        ),
                    ],
                    spacing=SPACING["sm"],
                ),
                ft.Divider(color=PALETTE.border, height=1),
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED,
                                    color=accent,
                                    size=14,
                                ),
                                ft.Text(reason, size=12, color=PALETTE.text, expand=True),
                            ],
                            spacing=8,
                        )
                        for reason in option.reasons
                    ],
                    spacing=4,
                ),
            ],
            spacing=SPACING["md"],
        )

    header = ft.Row(
        [
            ft.Container(
                content=ft.Text(option.icon, size=20),
                width=44,
                height=44,
                bgcolor=ft.Colors.with_opacity(0.12, accent),
                border_radius=RADIUS["pill"],
                alignment=ft.Alignment.CENTER,
            ),
            ft.Column(
                [
                    ft.Text(
                        option.title,
                        size=15,
                        weight=ft.FontWeight.W_700,
                        color=PALETTE.text_strong,
                    ),
                    ft.Text(option.subtitle, size=12, color=PALETTE.text_muted),
                ],
                spacing=2,
                expand=True,
            ),
            badge,
        ],
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    border_color = accent if option.recommended else PALETTE.border
    return card(
        border_color=border_color,
        content=ft.Column(
            [
                header,
                ft.Row(
                    [
                        pill(
                            RISK_LABELS[option.risk],
                            color=RISK_COLORS[option.risk][0],
                            bgcolor=RISK_COLORS[option.risk][1],
                            icon=ft.Icons.SHIELD_OUTLINED,
                        ),
                    ],
                    spacing=8,
                ),
                body,
            ],
            spacing=SPACING["md"],
        ),
    )
