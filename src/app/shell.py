"""Root navigation shell with responsive desktop/mobile layouts."""

from __future__ import annotations

import flet as ft

from app.store import AppState
from app.theme import PALETTE, RADIUS, SPACING
from app.views import dashboard, form, analysis, history, onboarding, plan


PRIMARY_TABS = [
    ("dashboard", "Beranda", ft.Icons.HOME_OUTLINED, ft.Icons.HOME_ROUNDED),
    ("history", "Riwayat", ft.Icons.HISTORY_OUTLINED, ft.Icons.HISTORY_ROUNDED),
]


VIEW_BUILDERS = {
    "onboarding": onboarding.view,
    "dashboard": dashboard.view,
    "form": form.view,
    "analysis": analysis.view,
    "plan": plan.view,
    "history": history.view,
}


# Breakpoints (logical pixels)
DESKTOP_BREAKPOINT = 900
TABLET_BREAKPOINT = 700
DESKTOP_CONTENT_MAX_WIDTH = 760


def build_shell(state: AppState) -> ft.Control:
    body_holder = ft.AnimatedSwitcher(
        content=_build_view(state),
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=200,
        reverse_duration=200,
        switch_in_curve=ft.AnimationCurve.EASE_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN,
    )

    body_scroll = ft.Column(
        controls=[body_holder],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    body_area = ft.Container(
        content=body_scroll,
        expand=True,
    )

    layout = ft.Container(expand=True, bgcolor=PALETTE.surface_alt)

    def _on_nav_change(index: int):
        route = PRIMARY_TABS[index][0]
        if state.route != route:
            state.navigate(route)

    def _layout_mode() -> str:
        width = state.page.width or 0
        if width >= DESKTOP_BREAKPOINT:
            return "desktop"
        if width >= TABLET_BREAKPOINT:
            return "tablet"
        return "mobile"

    def apply_layout():
        mode = _layout_mode()
        selected = _tab_index(state.route)
        nav_visible = state.route in {"dashboard", "history"}

        if mode == "desktop":
            body_area.padding = ft.Padding.symmetric(horizontal=SPACING["xl"], vertical=SPACING["md"])
            constrained_body = ft.Container(
                content=body_area,
                width=DESKTOP_CONTENT_MAX_WIDTH,
            )
            content_column = ft.Row(
                controls=[
                    ft.Container(expand=True),
                    constrained_body,
                    ft.Container(expand=True),
                ],
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                spacing=0,
            )

            rail = ft.NavigationRail(
                selected_index=selected,
                label_type=ft.NavigationRailLabelType.ALL,
                bgcolor=PALETTE.surface,
                indicator_color=PALETTE.primary_soft,
                min_width=88,
                leading=_brand_badge(),
                group_alignment=-0.9,
                destinations=[
                    ft.NavigationRailDestination(
                        icon=outlined,
                        selected_icon=filled,
                        label=label,
                    )
                    for _, label, outlined, filled in PRIMARY_TABS
                ],
                on_change=lambda e: _on_nav_change(e.control.selected_index),
            )

            layout.content = ft.Row(
                controls=[
                    rail,
                    ft.VerticalDivider(width=1, color=PALETTE.border),
                    ft.Container(content=content_column, expand=True),
                ],
                spacing=0,
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            )
        else:
            horizontal_padding = SPACING["lg"] if mode == "mobile" else SPACING["xl"]
            body_area.padding = ft.Padding.symmetric(
                horizontal=horizontal_padding,
                vertical=SPACING["sm"],
            )

            inner_body: ft.Control = body_area
            if mode == "tablet":
                inner_body = ft.Row(
                    controls=[
                        ft.Container(expand=True),
                        ft.Container(content=body_area, width=DESKTOP_CONTENT_MAX_WIDTH),
                        ft.Container(expand=True),
                    ],
                    spacing=0,
                    expand=True,
                    vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                )

            nav_bar = ft.NavigationBar(
                destinations=[
                    ft.NavigationBarDestination(
                        icon=outlined,
                        selected_icon=filled,
                        label=label,
                    )
                    for _, label, outlined, filled in PRIMARY_TABS
                ],
                selected_index=selected,
                bgcolor=PALETTE.surface,
                indicator_color=PALETTE.primary_soft,
                label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
                on_change=lambda e: _on_nav_change(e.control.selected_index),
                height=68,
            )

            layout.content = ft.Column(
                controls=[
                    ft.Container(content=inner_body, expand=True),
                    ft.Container(content=nav_bar, visible=nav_visible),
                ],
                expand=True,
                spacing=0,
            )

    def rerender():
        body_holder.content = _build_view(state)
        apply_layout()
        layout.update()

    state.on_change = rerender

    def on_resize(_event):
        apply_layout()
        try:
            layout.update()
        except RuntimeError:
            pass

    state.page.on_resize = on_resize

    apply_layout()
    return layout


def _build_view(state: AppState) -> ft.Control:
    builder = VIEW_BUILDERS.get(state.route, dashboard.view)
    content = builder(state)
    return ft.Container(
        key=state.route,
        content=content,
        padding=ft.Padding.only(top=SPACING["md"]),
    )


def _tab_index(route: str) -> int:
    for index, (key, *_rest) in enumerate(PRIMARY_TABS):
        if key == route:
            return index
    return 0


def _brand_badge() -> ft.Control:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text("🌱", size=22),
                    width=44,
                    height=44,
                    bgcolor=PALETTE.primary_soft,
                    border_radius=RADIUS["pill"],
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Text(
                    "PanenPintar",
                    size=11,
                    weight=ft.FontWeight.W_700,
                    color=PALETTE.primary_dark,
                ),
            ],
            spacing=6,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=12, vertical=18),
    )
