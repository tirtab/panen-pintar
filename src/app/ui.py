"""Reusable UI primitives for PanenPintar.

Each helper returns a Flet Control configured with the palette defined in
``app.theme``. Keep these small and composable so views remain readable.
"""

from __future__ import annotations

from typing import Callable, Iterable, Optional

import flet as ft

from app.theme import PALETTE, RADIUS, RISK_COLORS, RISK_LABELS, SPACING


def soft_shadow(opacity: float = 0.06, offset_y: int = 6, blur: int = 16) -> ft.BoxShadow:
    return ft.BoxShadow(
        spread_radius=0,
        blur_radius=blur,
        color=ft.Colors.with_opacity(opacity, ft.Colors.BLACK),
        offset=ft.Offset(0, offset_y),
    )


def section_title(text: str, *, action: Optional[ft.Control] = None) -> ft.Control:
    children: list[ft.Control] = [
        ft.Text(text, size=16, weight=ft.FontWeight.W_700, color=PALETTE.text_strong)
    ]
    if action is not None:
        children.append(action)
    return ft.Row(
        controls=children,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


def card(
    *,
    content: ft.Control,
    padding: int = SPACING["lg"],
    bgcolor: str = PALETTE.surface,
    on_click: Optional[Callable] = None,
    border_color: Optional[str] = None,
) -> ft.Container:
    return ft.Container(
        content=content,
        padding=padding,
        bgcolor=bgcolor,
        border_radius=RADIUS["lg"],
        border=ft.Border.all(1, border_color or PALETTE.border),
        shadow=soft_shadow(),
        ink=on_click is not None,
        on_click=on_click,
        animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
    )


def pill(text: str, *, color: str, bgcolor: str, icon: Optional[str] = None) -> ft.Container:
    children: list[ft.Control] = []
    if icon is not None:
        children.append(ft.Icon(icon, color=color, size=14))
    children.append(ft.Text(text, size=12, weight=ft.FontWeight.W_600, color=color))
    return ft.Container(
        content=ft.Row(controls=children, spacing=6, tight=True),
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        bgcolor=bgcolor,
        border_radius=RADIUS["pill"],
    )


def risk_pill(level: str) -> ft.Container:
    color, bg = RISK_COLORS[level]
    label = RISK_LABELS[level]
    return pill(label, color=color, bgcolor=bg, icon=ft.Icons.SHIELD_OUTLINED)


def stat_tile(*, label: str, value: str, icon: str, accent: str) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(icon, color=accent, size=16),
                            padding=6,
                            bgcolor=ft.Colors.with_opacity(0.12, accent),
                            border_radius=RADIUS["pill"],
                        ),
                        ft.Text(
                            label,
                            size=11,
                            color=PALETTE.text_muted,
                            no_wrap=False,
                            expand=True,
                        ),
                    ],
                    spacing=6,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Text(
                    value,
                    size=15,
                    weight=ft.FontWeight.W_700,
                    color=PALETTE.text_strong,
                    no_wrap=False,
                ),
            ],
            spacing=6,
        ),
        padding=10,
        bgcolor=PALETTE.surface,
        border_radius=RADIUS["md"],
        border=ft.Border.all(1, PALETTE.border),
        expand=True,
    )


def primary_button(
    text: str,
    *,
    on_click: Callable,
    icon: Optional[str] = None,
    expand: bool = False,
) -> ft.Control:
    return ft.FilledButton(
        content=text,
        icon=icon,
        on_click=on_click,
        expand=expand,
        style=ft.ButtonStyle(
            bgcolor=PALETTE.primary,
            color=ft.Colors.WHITE,
            padding=ft.Padding.symmetric(horizontal=20, vertical=18),
            shape=ft.RoundedRectangleBorder(radius=RADIUS["md"]),
            text_style=ft.TextStyle(weight=ft.FontWeight.W_600, size=14),
        ),
    )


def ghost_button(
    text: str,
    *,
    on_click: Callable,
    icon: Optional[str] = None,
    color: Optional[str] = None,
) -> ft.Control:
    return ft.TextButton(
        content=text,
        icon=icon,
        on_click=on_click,
        style=ft.ButtonStyle(
            color=color or PALETTE.primary,
            padding=ft.Padding.symmetric(horizontal=12, vertical=12),
            text_style=ft.TextStyle(weight=ft.FontWeight.W_600, size=14),
        ),
    )


def back_header(*, title: str, subtitle: Optional[str], on_back: Callable) -> ft.Container:
    column_children: list[ft.Control] = [
        ft.Text(title, size=20, weight=ft.FontWeight.W_700, color=PALETTE.text_strong)
    ]
    if subtitle:
        column_children.append(
            ft.Text(subtitle, size=13, color=PALETTE.text_muted)
        )
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK_ROUNDED,
                    on_click=on_back,
                    icon_color=PALETTE.text_strong,
                    style=ft.ButtonStyle(
                        bgcolor=PALETTE.surface,
                        shape=ft.CircleBorder(),
                        padding=10,
                        side=ft.BorderSide(1, PALETTE.border),
                    ),
                ),
                ft.Column(controls=column_children, spacing=2, expand=True),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.only(top=SPACING["md"], bottom=SPACING["md"]),
    )


def empty_state(*, icon: str, title: str, body: str) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [
                ft.Icon(icon, size=40, color=PALETTE.text_muted),
                ft.Text(title, size=15, weight=ft.FontWeight.W_700, color=PALETTE.text_strong),
                ft.Text(
                    body,
                    size=12,
                    color=PALETTE.text_muted,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        padding=SPACING["xl"],
        alignment=ft.Alignment.CENTER,
    )


def chip_select(
    *,
    options: Iterable[tuple[str, str]],
    selected: set[str],
    on_toggle: Callable[[str], None],
) -> ft.Control:
    chips: list[ft.Control] = []
    for key, label in options:
        is_active = key in selected
        chips.append(
            ft.Container(
                content=ft.Text(
                    label,
                    size=12,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.WHITE if is_active else PALETTE.text_strong,
                ),
                padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                bgcolor=PALETTE.primary if is_active else PALETTE.surface,
                border_radius=RADIUS["pill"],
                border=ft.Border.all(
                    1,
                    PALETTE.primary if is_active else PALETTE.border,
                ),
                ink=True,
                on_click=lambda _e, k=key: on_toggle(k),
                animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            )
        )
    return ft.Row(controls=chips, wrap=True, spacing=8, run_spacing=8)
