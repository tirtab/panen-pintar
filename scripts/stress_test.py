"""Standalone stress test for the decision engine. Run from project root.

Usage:
    .venv\\Scripts\\python.exe scripts\\stress_test.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from app.data import DecisionInput, analyze  # noqa: E402


def case(label: str, **kw) -> None:
    inp = DecisionInput(**kw)
    r = analyze(inp)
    print(f"\n=== {label} ===")
    print(
        f"  Input: {kw['crop_key']}, umur {kw['age_days']}h, "
        f"gejala={kw.get('symptoms', [])}, cuaca={kw.get('weather','cerah')}, "
        f"lahan {kw.get('area_m2',100)}m2, anggaran={kw.get('care_budget',150000)}"
    )
    print(f"  Risk: {r.risk_level} ({r.risk_score})")
    for o in r.options:
        rec = " <-- REKOMENDASI" if o.recommended else ""
        print(
            f"  [{o.key:10}] risk={o.risk:6} "
            f"profit={o.profit:>10} cost={o.cost:>8} "
            f"yield={o.expected_yield_kg:>6}kg conf={o.confidence:>3}%{rec}"
        )


SCENARIOS = [
    ("Tanaman sehat sempurna (cabai 60h, cerah, no symptoms)",
     dict(crop_key='cabai', age_days=60, symptoms=[], weather='cerah', area_m2=120, care_budget=150000)),
    ("Risiko rendah (cabai 60h, daun_kuning, cerah)",
     dict(crop_key='cabai', age_days=60, symptoms=['daun_kuning'], weather='cerah', area_m2=120, care_budget=150000)),
    ("Risiko sedang (cabai 70h, daun_kuning+bercak_daun, hujan)",
     dict(crop_key='cabai', age_days=70, symptoms=['daun_kuning','bercak_daun'], weather='hujan', area_m2=120, care_budget=200000)),
    ("Risiko tinggi (cabai 50h, busuk+layu+hama, hujan_lebat)",
     dict(crop_key='cabai', age_days=50, symptoms=['busuk_buah','layu','hama_serangga'], weather='hujan_lebat', area_m2=120, care_budget=200000)),
    ("Umur muda terkunci (cabai 20h, 1 gejala)",
     dict(crop_key='cabai', age_days=20, symptoms=['daun_kuning'], weather='cerah', area_m2=120, care_budget=150000)),
    ("Sudah matang penuh (cabai 90h, 1 gejala ringan)",
     dict(crop_key='cabai', age_days=90, symptoms=['daun_kuning'], weather='cerah', area_m2=120, care_budget=150000)),
    ("Lewat siklus (cabai 100h, no symptoms)",
     dict(crop_key='cabai', age_days=100, symptoms=[], weather='cerah', area_m2=120, care_budget=150000)),
    ("Lahan mini (cabai 60h, 10 m2)",
     dict(crop_key='cabai', age_days=60, symptoms=['bercak_daun'], weather='berawan', area_m2=10, care_budget=50000)),
    ("Lahan besar (cabai 70h, 2000m2)",
     dict(crop_key='cabai', age_days=70, symptoms=['bercak_daun'], weather='hujan', area_m2=2000, care_budget=1500000)),
    ("Padi 100h banyak gejala parah",
     dict(crop_key='padi', age_days=100, symptoms=['busuk_buah','layu','jamur','hama_serangga'], weather='hujan_lebat', area_m2=500, care_budget=300000)),
]


if __name__ == "__main__":
    for label, kw in SCENARIOS:
        case(label, **kw)
