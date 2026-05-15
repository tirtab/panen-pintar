"""In-memory app state + navigation for PanenPintar."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional

import flet as ft

from app.data import DecisionInput, DecisionResult


def _default_form_draft() -> dict[str, Any]:
    return {
        "crop": "cabai",
        "age": 45,
        "symptoms": set(),
        "weather": "berawan",
        "area": 100,
        "budget": 500000,
    }


@dataclass
class HistoryEntry:
    id: str
    created_at: datetime
    crop_key: str
    crop_name: str
    risk_level: str
    summary: str
    recommended_title: str
    recommended_profit: int
    snapshot_input: DecisionInput
    snapshot_result: DecisionResult


@dataclass
class AppState:
    page: ft.Page
    on_change: Callable[[], None] = field(default=lambda: None)

    route: str = "onboarding"
    route_params: dict = field(default_factory=dict)

    last_input: Optional[DecisionInput] = None
    last_result: Optional[DecisionResult] = None
    history: list[HistoryEntry] = field(default_factory=list)
    farmer_name: str = "Petani"

    # Persists user-entered form values across navigations.
    form_draft: dict[str, Any] = field(default_factory=_default_form_draft)

    def navigate(self, route: str, **params) -> None:
        self.route = route
        self.route_params = params
        self.on_change()

    def commit_result(self, decision_input: DecisionInput, result: DecisionResult) -> None:
        self.last_input = decision_input
        self.last_result = result
        rec = result.recommended
        entry = HistoryEntry(
            id=str(uuid.uuid4())[:8],
            created_at=datetime.now(),
            crop_key=decision_input.crop_key,
            crop_name=result.crop_name,
            risk_level=result.risk_level,
            summary=result.summary,
            recommended_title=rec.title,
            recommended_profit=rec.profit,
            snapshot_input=decision_input,
            snapshot_result=result,
        )
        self.history.insert(0, entry)

    def open_history_entry(self, entry_id: str) -> None:
        """Restore a saved decision and open the analysis view."""
        for entry in self.history:
            if entry.id == entry_id:
                self.last_input = entry.snapshot_input
                self.last_result = entry.snapshot_result
                self.navigate("analysis")
                return

    def reset_form_draft(self) -> None:
        self.form_draft = _default_form_draft()

    def show_snack(self, message: str) -> None:
        self.page.show_dialog(
            ft.SnackBar(
                content=ft.Text(message, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.GREEN_700,
                duration=2500,
            )
        )
