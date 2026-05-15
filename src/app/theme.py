"""Centralized design tokens for PanenPintar.

Colors are tuned for a calm, agronomy-friendly palette with strong contrast
on small screens, which is where most petani will use the app.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    primary: str = "#2E7D32"
    primary_dark: str = "#1B5E20"
    primary_soft: str = "#E8F5E9"

    accent: str = "#F9A825"
    accent_soft: str = "#FFF8E1"

    danger: str = "#C62828"
    danger_soft: str = "#FFEBEE"

    info: str = "#1565C0"
    info_soft: str = "#E3F2FD"

    surface: str = "#FFFFFF"
    surface_alt: str = "#F4F7F4"
    surface_muted: str = "#ECEFEA"

    text_strong: str = "#1B2A1B"
    text: str = "#2E3A2E"
    text_muted: str = "#6B7A6B"

    border: str = "#DCE3DC"


PALETTE = Palette()


RISK_COLORS: dict[str, tuple[str, str]] = {
    "low": (PALETTE.primary, PALETTE.primary_soft),
    "medium": (PALETTE.accent, PALETTE.accent_soft),
    "high": (PALETTE.danger, PALETTE.danger_soft),
}


RISK_LABELS: dict[str, str] = {
    "low": "Risiko Rendah",
    "medium": "Risiko Sedang",
    "high": "Risiko Tinggi",
}


SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
    "xxl": 32,
}


RADIUS = {
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
    "pill": 999,
}
