"""Input form for crop condition assessment."""

from __future__ import annotations

import flet as ft

from app.data import (
    CROPS,
    SYMPTOMS,
    WEATHER_OPTIONS,
    DecisionInput,
    analyze,
    format_currency,
    get_crop,
)
from app.store import AppState
from app.theme import PALETTE, RADIUS, SPACING
from app.ui import (
    back_header,
    card,
    chip_select,
    pill,
    primary_button,
    section_title,
)


def view(state: AppState) -> ft.Control:
    # Restore previous draft so user does not lose input when navigating back.
    form_state = state.form_draft

    # Honor explicit crop selection coming from dashboard quick-tap.
    crop_override = state.route_params.get("crop")
    if crop_override:
        form_state["crop"] = crop_override

    container = ft.Container()

    def rebuild():
        container.content = build_body()
        container.update()

    def on_crop(key: str):
        form_state["crop"] = key
        rebuild()

    def on_weather(key: str):
        form_state["weather"] = key
        rebuild()

    def toggle_symptom(key: str):
        if key in form_state["symptoms"]:
            form_state["symptoms"].remove(key)
        else:
            form_state["symptoms"].add(key)
        rebuild()

    def submit(_):
        crop = get_crop(form_state["crop"])
        if crop is None:
            return
        decision_input = DecisionInput(
            crop_key=form_state["crop"],
            age_days=int(form_state["age"]),
            symptoms=list(form_state["symptoms"]),
            weather=form_state["weather"],
            area_m2=float(form_state["area"]),
            care_budget=int(form_state["budget"]),
        )
        result = analyze(decision_input)
        state.commit_result(decision_input, result)
        state.navigate("analysis")

    def reset_form(_):
        state.reset_form_draft()
        nonlocal form_state
        form_state = state.form_draft
        rebuild()

    def build_crop_grid() -> ft.Control:
        items: list[ft.Control] = []
        for crop in CROPS:
            active = crop.key == form_state["crop"]
            items.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(crop.emoji, size=22),
                            ft.Text(
                                crop.name,
                                size=12,
                                weight=ft.FontWeight.W_600,
                                color=ft.Colors.WHITE if active else PALETTE.text_strong,
                            ),
                        ],
                        spacing=4,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding.symmetric(horizontal=14, vertical=12),
                    bgcolor=PALETTE.primary if active else PALETTE.surface,
                    border_radius=RADIUS["md"],
                    border=ft.Border.all(
                        1,
                        PALETTE.primary if active else PALETTE.border,
                    ),
                    ink=True,
                    on_click=lambda _e, k=crop.key: on_crop(k),
                    animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
                )
            )
        return ft.Row(controls=items, wrap=True, spacing=8, run_spacing=8)

    def build_weather_chips() -> ft.Control:
        return chip_select(
            options=WEATHER_OPTIONS,
            selected={form_state["weather"]},
            on_toggle=on_weather,
        )

    def build_symptom_chips() -> ft.Control:
        return chip_select(
            options=[(s.key, f"{s.icon} {s.label}") for s in SYMPTOMS],
            selected=form_state["symptoms"],
            on_toggle=toggle_symptom,
        )

    def slider_field(
        label: str,
        value: float,
        min_v: float,
        max_v: float,
        divisions: int,
        on_change: callable,
        formatter: callable,
    ) -> ft.Control:
        value_text = ft.Text(
            formatter(value),
            size=13,
            weight=ft.FontWeight.W_700,
            color=PALETTE.primary,
        )

        def handler(e):
            value_text.value = formatter(e.control.value)
            on_change(e.control.value)
            value_text.update()

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(label, size=13, color=PALETTE.text),
                        value_text,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Slider(
                    value=value,
                    min=min_v,
                    max=max_v,
                    divisions=divisions,
                    active_color=PALETTE.primary,
                    inactive_color=PALETTE.surface_muted,
                    on_change=handler,
                ),
            ],
            spacing=4,
        )

    def set_age(v: float):
        form_state["age"] = v

    def set_area(v: float):
        form_state["area"] = v

    def set_budget(v: float):
        form_state["budget"] = v

    def section_header(step: int, total: int, title: str) -> ft.Control:
        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(
                        str(step),
                        size=12,
                        weight=ft.FontWeight.W_700,
                        color=ft.Colors.WHITE,
                    ),
                    width=24,
                    height=24,
                    bgcolor=PALETTE.primary,
                    border_radius=RADIUS["pill"],
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Text(
                    title,
                    size=15,
                    weight=ft.FontWeight.W_700,
                    color=PALETTE.text_strong,
                ),
                ft.Container(expand=True),
                ft.Text(
                    f"Langkah {step}/{total}",
                    size=11,
                    color=PALETTE.text_muted,
                ),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def build_body() -> ft.Control:
        crop = get_crop(form_state["crop"])
        cycle = crop.cycle_days if crop else 100
        age_ratio = min(form_state["age"] / cycle, 1.0)
        total_steps = 5

        pills_row = ft.Row(
            controls=[
                pill(
                    "5 langkah singkat",
                    color=PALETTE.primary,
                    bgcolor=PALETTE.primary_soft,
                    icon=ft.Icons.CHECKLIST_ROUNDED,
                ),
                pill(
                    f"Komoditas: {crop.name if crop else '-'}",
                    color=PALETTE.text,
                    bgcolor=PALETTE.surface,
                    icon=ft.Icons.AGRICULTURE_ROUNDED,
                ),
            ],
            spacing=8,
            wrap=True,
            run_spacing=8,
            expand=True,
        )

        intro = ft.Row(
            controls=[
                pills_row,
                ft.TextButton(
                    content="Reset",
                    icon=ft.Icons.REFRESH_ROUNDED,
                    on_click=reset_form,
                    style=ft.ButtonStyle(color=PALETTE.text_muted),
                ),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        progress_card = card(
            bgcolor=PALETTE.primary_soft,
            border_color=PALETTE.primary_soft,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("📈", size=18),
                            ft.Text(
                                f"Umur tanam: {int(form_state['age'])} hari "
                                f"({int(age_ratio * 100)}% dari siklus)",
                                size=12,
                                weight=ft.FontWeight.W_600,
                                color=PALETTE.text_strong,
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.ProgressBar(
                        value=age_ratio,
                        color=PALETTE.primary,
                        bgcolor=ft.Colors.with_opacity(0.4, ft.Colors.WHITE),
                        bar_height=8,
                    ),
                ],
                spacing=8,
            ),
        )

        return ft.Column(
            controls=[
                back_header(
                    title="Buat keputusan",
                    subtitle="Isi data singkat tentang tanaman Anda",
                    on_back=lambda _: state.navigate("dashboard"),
                ),
                intro,
                section_header(1, total_steps, "Komoditas"),
                build_crop_grid(),
                section_header(2, total_steps, "Umur tanam"),
                card(
                    content=slider_field(
                        label="Hari setelah tanam",
                        value=form_state["age"],
                        min_v=1,
                        max_v=cycle,
                        divisions=max(cycle - 1, 10),
                        on_change=set_age,
                        formatter=lambda v: f"{int(v)} hari",
                    )
                ),
                progress_card,
                section_header(3, total_steps, "Gejala yang terlihat"),
                ft.Text(
                    "Pilih semua yang sesuai. Lewati jika tanaman sehat.",
                    size=12,
                    color=PALETTE.text_muted,
                ),
                build_symptom_chips(),
                section_header(4, total_steps, "Cuaca beberapa hari terakhir"),
                build_weather_chips(),
                section_header(5, total_steps, "Lahan & anggaran perawatan"),
                card(
                    content=ft.Column(
                        [
                            slider_field(
                                label="Luas lahan",
                                value=form_state["area"],
                                min_v=10,
                                max_v=2000,
                                divisions=199,
                                on_change=set_area,
                                formatter=lambda v: f"{int(v)} m²",
                            ),
                            ft.Divider(color=PALETTE.border, height=1),
                            slider_field(
                                label="Anggaran perawatan",
                                value=form_state["budget"],
                                min_v=20000,
                                max_v=1500000,
                                divisions=148,
                                on_change=set_budget,
                                formatter=lambda v: format_currency(int(v)),
                            ),
                        ],
                        spacing=8,
                    )
                ),
                ft.Container(height=SPACING["md"]),
                primary_button(
                    "Analisis sekarang",
                    on_click=submit,
                    icon=ft.Icons.ANALYTICS_ROUNDED,
                    expand=True,
                ),
                ft.Container(height=SPACING["xl"]),
            ],
            spacing=SPACING["md"],
        )

    container.content = build_body()
    return container
