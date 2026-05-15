"""Onboarding hero view shown on first launch."""

from __future__ import annotations

import flet as ft

from app.store import AppState
from app.theme import PALETTE, RADIUS, SPACING
from app.ui import primary_button


def view(state: AppState) -> ft.Control:
    def start(_):
        state.navigate("dashboard")

    feature_rows = [
        ("📊", "Asisten Untung-Rugi", "Bandingkan 3 keputusan dalam satu layar"),
        ("📅", "Rencana 7 Hari", "Langkah harian yang siap dijalankan"),
        ("🧾", "Catatan Konsultasi", "Riwayat keputusan tersimpan rapi"),
    ]

    feature_list = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(emoji, size=20),
                        width=40,
                        height=40,
                        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
                        border_radius=RADIUS["pill"],
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Column(
                        [
                            ft.Text(title, size=14, weight=ft.FontWeight.W_700, color=ft.Colors.WHITE),
                            ft.Text(subtitle, size=12, color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE)),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
            for emoji, title, subtitle in feature_rows
        ],
        spacing=14,
    )

    hero = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("🌱", size=22),
                            ft.Text(
                                "PanenPintar",
                                size=14,
                                weight=ft.FontWeight.W_700,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                    bgcolor=ft.Colors.with_opacity(0.18, ft.Colors.WHITE),
                    border_radius=RADIUS["pill"],
                ),
                ft.Container(height=SPACING["xl"]),
                ft.Text(
                    "Keputusan tani\nyang lebih untung.",
                    size=30,
                    weight=ft.FontWeight.W_800,
                    color=ft.Colors.WHITE,
                ),
                ft.Container(height=SPACING["sm"]),
                ft.Text(
                    "Asisten ringan untuk petani kecil: cek kondisi tanaman, "
                    "bandingkan tindakan, dan jalankan rencana 7 hari yang "
                    "paling menguntungkan.",
                    size=14,
                    color=ft.Colors.with_opacity(0.92, ft.Colors.WHITE),
                ),
                ft.Container(height=SPACING["xl"]),
                feature_list,
            ],
        ),
        padding=SPACING["xl"],
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[PALETTE.primary_dark, PALETTE.primary, "#4CAF50"],
        ),
        border_radius=RADIUS["xl"],
        expand=True,
    )

    return ft.Column(
        controls=[
            ft.Container(content=hero, expand=True, padding=SPACING["lg"]),
            ft.Container(
                content=ft.Column(
                    [
                        primary_button(
                            "Mulai gunakan PanenPintar",
                            on_click=start,
                            icon=ft.Icons.ARROW_FORWARD_ROUNDED,
                            expand=True,
                        ),
                        ft.Text(
                            "Tanpa registrasi. Cukup isi kondisi tanaman Anda.",
                            size=11,
                            color=PALETTE.text_muted,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding.only(
                    left=SPACING["lg"],
                    right=SPACING["lg"],
                    bottom=SPACING["lg"],
                    top=SPACING["sm"],
                ),
            ),
        ],
        expand=True,
        spacing=0,
    )
