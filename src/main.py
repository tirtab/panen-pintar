"""PanenPintar entry point.

Run with ``uv run flet run`` (desktop) or ``uv run flet run --web``.
"""

import flet as ft

from app import bootstrap


ft.run(bootstrap)
