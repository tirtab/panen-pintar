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

    recommended = result.recommended
    profit_color = PALETTE.primary if recommended.profit >= 0 else PALETTE.danger

    summary_card = card(
        bgcolor=PALETTE.primary_soft,
        border_color=PALETTE.primary_soft,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            f"Keputusan utama · {result.crop_name}",
                            size=14,
                            weight=ft.FontWeight.W_700,
                            color=PALETTE.text_strong,
                        ),
                        risk_pill(result.risk_level),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(
                    f"Sebaiknya: {recommended.title}",
                    size=22,
                    weight=ft.FontWeight.W_700,
                    color=PALETTE.text_strong,
                ),
                ft.Text(_recommendation_story(result), size=13, color=PALETTE.text),
                ft.Row(
                    [
                        stat_tile(
                            label="Estimasi untung",
                            value=format_currency(recommended.profit),
                            icon=ft.Icons.TRENDING_UP_ROUNDED,
                            accent=profit_color,
                        ),
                        stat_tile(
                            label="Biaya tindakan",
                            value=format_currency(recommended.cost),
                            icon=ft.Icons.PAYMENTS_ROUNDED,
                            accent=PALETTE.info,
                        ),
                    ],
                    spacing=SPACING["sm"],
                ),
                ft.Row(
                    [
                        stat_tile(
                            label="Hasil terselamatkan",
                            value=f"{recommended.expected_yield_kg} kg",
                            icon=ft.Icons.AGRICULTURE_ROUNDED,
                            accent=recommended.accent_color,
                        ),
                        stat_tile(
                            label="Risiko kehilangan hasil",
                            value=f"{RISK_LABELS[result.risk_level]} ({int(result.risk_score * 100)}%)",
                            icon=ft.Icons.SHIELD_OUTLINED,
                            accent=RISK_COLORS[result.risk_level][0],
                        ),
                    ],
                    spacing=SPACING["sm"],
                ),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.INFO_OUTLINE_ROUNDED,
                                color=PALETTE.text_muted,
                                size=16,
                            ),
                            ft.Text(
                                "Angka utama di atas adalah cerita keputusan: untung-rugi, biaya, hasil terselamatkan, "
                                "risiko kehilangan hasil, dan kecocokan tindakan. Kecocokan ikut menjadi faktor pendukung "
                                "saat selisih untung-rugi antar opsi berdekatan.",
                                size=12,
                                color=PALETTE.text_muted,
                                expand=True,
                            ),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    padding=ft.Padding.all(10),
                    bgcolor=ft.Colors.with_opacity(0.45, ft.Colors.WHITE),
                    border_radius=RADIUS["md"],
                ),
            ],
            spacing=SPACING["md"],
        ),
    )

    option_cards = [_option_card(state, opt) for opt in result.options]
    alternatives_card = _alternatives_card(result.options, recommended)

    return ft.Column(
        controls=[
            back_header(
                title="Hasil keputusan",
                subtitle="Ringkasan tindakan paling masuk akal untuk kondisi ini",
                on_back=lambda _: state.navigate("form"),
            ),
            summary_card,
            alternatives_card,
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


def _recommendation_story(result) -> str:
    option = result.recommended
    risk_label = RISK_LABELS[result.risk_level].lower()

    if option.key == "rawat":
        return (
            f"Risiko kehilangan hasil saat ini {risk_label}, tetapi tanaman masih layak diselamatkan. "
            "Perawatan dipilih karena estimasi hasil yang terselamatkan masih sebanding dengan biaya."
        )
    if option.key == "panen_awal":
        if option.title == "Panen Sekarang":
            return (
                f"Tanaman sudah siap dipanen dan risiko kehilangan hasil {risk_label}. "
                "Memanen sekarang membantu mengunci hasil tanpa menambah biaya perawatan."
            )
        return (
            f"Risiko kehilangan hasil {risk_label} dan umur tanaman sudah cukup untuk panen dini. "
            "Panen lebih awal dipilih untuk mengunci hasil sebelum kondisi memburuk."
        )
    return (
        f"Kondisi tanaman masih relatif aman dengan risiko kehilangan hasil {risk_label}. "
        "Menunggu sambil memantau dipilih karena biaya rendah dan estimasi untungnya paling baik."
    )


def _alternatives_card(options: list[DecisionOption], recommended: DecisionOption) -> ft.Control:
    rows: list[ft.Control] = []
    for option in options:
        if option.key == recommended.key:
            continue
        rows.append(
            ft.Row(
                [
                    ft.Icon(
                        ft.Icons.INFO_OUTLINE_ROUNDED,
                        size=15,
                        color=option.accent_color,
                    ),
                    ft.Text(
                        f"{option.title}: {_alternative_reason(option, recommended)}",
                        size=12,
                        color=PALETTE.text,
                        expand=True,
                    ),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        )

    return card(
        content=ft.Column(
            [
                ft.Text(
                    "Kenapa opsi lain tidak dipilih?",
                    size=14,
                    weight=ft.FontWeight.W_700,
                    color=PALETTE.text_strong,
                ),
                *rows,
            ],
            spacing=8,
        )
    )


def _alternative_reason(option: DecisionOption, recommended: DecisionOption) -> str:
    if option.confidence == 0:
        return "belum tersedia karena umur tanaman belum cukup untuk opsi ini."
    if option.profit < 0:
        return (
            f"secara tindakan bisa dipertimbangkan, tetapi estimasi profitnya negatif "
            f"({format_currency(option.profit)})."
        )
    if option.profit < recommended.profit:
        return (
            f"estimasi untungnya lebih rendah ({format_currency(option.profit)}) dibanding "
            f"opsi utama ({format_currency(recommended.profit)})."
        )
    if option.risk == "high":
        return "potensi untung ada, tetapi risiko kehilangan hasil masih terlalu besar."
    if option.confidence > recommended.confidence:
        return "kecocokan tindakannya tinggi, tetapi secara untung-rugi belum menjadi pilihan paling kuat."
    return "masih layak sebagai alternatif, tetapi skor akhir untung-rugi dan risikonya kalah dari opsi utama."


def _option_card(state: AppState, option: DecisionOption) -> ft.Control:
    available = option.confidence > 0

    accent = option.accent_color

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
                            label="Kecocokan tindakan",
                            value=f"{option.confidence}%",
                            icon=ft.Icons.TASK_ALT_ROUNDED,
                            accent=PALETTE.accent,
                        ),
                    ],
                    spacing=SPACING["sm"],
                ),
                ft.Text(
                    "Kecocokan menilai kesesuaian tindakan dengan umur, gejala, dan cuaca. "
                    "Angka ini ikut mendukung rekomendasi, tetapi tidak mengalahkan selisih profit yang besar.",
                    color=PALETTE.text_muted,
                    style=ft.TextStyle(
                        size=11,
                        height=1.45,
                    ),
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

    icon_circle = ft.Container(
        content=ft.Text(option.icon, size=20),
        width=44,
        height=44,
        bgcolor=ft.Colors.with_opacity(0.12, accent),
        border_radius=RADIUS["pill"],
        alignment=ft.Alignment.CENTER,
    )
    title_block = ft.Column(
        [
            ft.Text(
                option.title,
                size=15,
                weight=ft.FontWeight.W_700,
                color=PALETTE.text_strong,
                expand=True,
                no_wrap=False,
            ),
            ft.Text(
                option.subtitle,
                size=12,
                color=PALETTE.text_muted,
                expand=True,
                no_wrap=False,
            ),
        ],
        spacing=2,
        expand=True,
    )
    chips: list[ft.Control] = [
        pill(
            RISK_LABELS[option.risk],
            color=RISK_COLORS[option.risk][0],
            bgcolor=RISK_COLORS[option.risk][1],
            icon=ft.Icons.SHIELD_OUTLINED,
        ),
    ]
    if option.recommended:
        chips.append(
            pill(
                "Terbaik secara untung-rugi",
                color=PALETTE.primary,
                bgcolor=PALETTE.primary_soft,
                icon=ft.Icons.STAR_ROUNDED,
            )
        )
    header = ft.Column(
        [
            ft.Row(
                [icon_circle, title_block],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            ft.Row(
                controls=chips,
                spacing=SPACING["sm"],
                run_spacing=SPACING["sm"],
                wrap=True,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ],
        spacing=SPACING["sm"],
    )

    border_color = accent if option.recommended else PALETTE.border
    return card(
        border_color=border_color,
        content=ft.Column(
            [
                header,
                body,
            ],
            spacing=SPACING["md"],
        ),
    )
