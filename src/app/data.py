"""Domain data for PanenPintar: crop catalog, symptom catalog,
and a deterministic decision engine for the "untung-rugi" analysis.

The engine is intentionally simple and rule-based so the demo behaves
predictably during the competition.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


# --- Crop catalog ---------------------------------------------------------

@dataclass(frozen=True)
class Crop:
    key: str
    name: str
    emoji: str
    cycle_days: int
    base_yield_kg_per_m2: float
    base_price_per_kg: int  # Indonesian Rupiah


CROPS: list[Crop] = [
    # cycle_days mengikuti referensi umum budidaya Indonesia
    # (dataran rendah/varietas cepat). Sumber: Agropedia, Liputan6, PTT Kementan.
    Crop("cabai", "Cabai Merah", "🌶️", cycle_days=90, base_yield_kg_per_m2=0.8, base_price_per_kg=35000),
    Crop("padi", "Padi", "🌾", cycle_days=110, base_yield_kg_per_m2=0.6, base_price_per_kg=7000),
    Crop("jagung", "Jagung", "🌽", cycle_days=100, base_yield_kg_per_m2=0.9, base_price_per_kg=6000),
    Crop("tomat", "Tomat", "🍅", cycle_days=70, base_yield_kg_per_m2=2.5, base_price_per_kg=12000),
    Crop("kentang", "Kentang", "🥔", cycle_days=110, base_yield_kg_per_m2=2.0, base_price_per_kg=14000),
    Crop("bawang", "Bawang Merah", "🧅", cycle_days=65, base_yield_kg_per_m2=1.2, base_price_per_kg=28000),
]


def get_crop(key: str) -> Crop | None:
    for crop in CROPS:
        if crop.key == key:
            return crop
    return None


# --- Symptom catalog ------------------------------------------------------

@dataclass(frozen=True)
class Symptom:
    key: str
    label: str
    icon: str
    weight: float  # 0..1 contribution to risk score


SYMPTOMS: list[Symptom] = [
    Symptom("daun_kuning", "Daun menguning", "🍂", 0.20),
    Symptom("bercak_daun", "Bercak pada daun", "🟤", 0.25),
    Symptom("layu", "Tanaman layu", "🥀", 0.30),
    Symptom("busuk_buah", "Busuk buah / umbi", "🤢", 0.35),
    Symptom("hama_serangga", "Serangan hama", "🐛", 0.30),
    Symptom("kekurangan_air", "Tanah kering", "💧", 0.15),
    Symptom("kerdil", "Tumbuh kerdil", "📉", 0.20),
    Symptom("jamur", "Jamur / lumut", "🍄", 0.25),
]


WEATHER_OPTIONS = [
    ("cerah", "Cerah"),
    ("berawan", "Berawan"),
    ("hujan", "Hujan"),
    ("hujan_lebat", "Hujan Lebat"),
]


WEATHER_RISK = {
    "cerah": 0.0,
    "berawan": 0.05,
    "hujan": 0.10,
    "hujan_lebat": 0.20,
}


# --- Decision engine ------------------------------------------------------

RiskLevel = Literal["low", "medium", "high"]


@dataclass
class DecisionInput:
    crop_key: str
    age_days: int
    symptoms: list[str] = field(default_factory=list)
    weather: str = "cerah"
    area_m2: float = 100.0
    care_budget: int = 150000  # Rp budget per cycle for routine care
    market_price_per_kg: int | None = None  # override base price


@dataclass
class DecisionOption:
    key: str
    title: str
    subtitle: str
    icon: str
    accent_color: str
    cost: int
    expected_yield_kg: float
    revenue: int
    profit: int
    risk: RiskLevel
    confidence: int  # 0..100
    reasons: list[str]
    plan_steps: list[str]
    recommended: bool = False


@dataclass
class DecisionResult:
    crop_name: str
    risk_score: float
    risk_level: RiskLevel
    summary: str
    options: list[DecisionOption]

    @property
    def recommended(self) -> DecisionOption:
        for opt in self.options:
            if opt.recommended:
                return opt
        return self.options[0]


def _risk_level(score: float) -> RiskLevel:
    if score < 0.25:
        return "low"
    if score < 0.55:
        return "medium"
    return "high"


def _symptom_weights(keys: list[str]) -> float:
    score = 0.0
    for key in keys:
        for s in SYMPTOMS:
            if s.key == key:
                score += s.weight
                break
    return min(score, 1.0)


def _format_rp(value: int | float) -> str:
    value = int(round(value))
    return "Rp" + f"{value:,}".replace(",", ".")


def analyze(input: DecisionInput) -> DecisionResult:
    crop = get_crop(input.crop_key)
    if crop is None:
        raise ValueError(f"Unknown crop: {input.crop_key}")

    price = input.market_price_per_kg or crop.base_price_per_kg
    normal_yield = crop.base_yield_kg_per_m2 * input.area_m2
    age_ratio = min(max(input.age_days / crop.cycle_days, 0.0), 1.0)

    symptom_score = _symptom_weights(input.symptoms)
    weather_penalty = WEATHER_RISK.get(input.weather, 0.0)
    raw_risk = symptom_score * 0.75 + weather_penalty
    risk_score = min(raw_risk, 1.0)
    risk_level = _risk_level(risk_score)

    # Biaya panen adalah biaya tetap yang dikenakan ke SEMUA opsi karena
    # petani pasti akan memanen di akhir siklus, terlepas dari pilihan
    # tindakan saat ini. Tanpa ini, opsi Tunggu terlihat tidak adil-untung
    # karena seolah-olah tidak ada biaya panen sama sekali.
    harvest_cost = int(input.area_m2 * 400)

    # Option A: Rawat sekarang -- spend on care, retain most yield.
    # care_factor naik saat risiko sudah > 0.6 supaya engine tidak terlalu
    # optimis ketika tanaman sudah parah (perawatan sulit menyelamatkan
    # banyak kalau gejala sudah berat).
    care_cost = int(input.care_budget + input.area_m2 * 250) + harvest_cost
    care_factor = 0.30 + max(0.0, risk_score - 0.6) * 0.5
    retained_a = max(0.30, 1.0 - risk_score * care_factor)
    yield_a = normal_yield * retained_a
    revenue_a = int(yield_a * price)
    profit_a = revenue_a - care_cost
    rescue_pct = int(round(retained_a * 100))
    reasons_a = [
        f"Tindakan ini menyelamatkan ~{rescue_pct}% potensi panen",
        f"Cocok karena risiko saat ini {risk_level.upper()}",
        "Biaya jelas dan terkontrol",
    ]
    plan_a = [
        "Hari 1: Bersihkan gulma dan daun terinfeksi",
        "Hari 2: Aplikasikan pupuk dasar + cek drainase",
        "Hari 3: Semprot pestisida nabati di sore hari",
        "Hari 4: Penyiraman teratur sesuai cuaca",
        "Hari 5: Pemeriksaan ulang gejala daun",
        "Hari 6: Pemupukan susulan ringan",
        "Hari 7: Evaluasi & dokumentasi kondisi",
    ]

    # Option B: Panen lebih awal (only sensible past 60% cycle).
    # Diskon hasil berkurang linear dari 25% (umur 60% siklus) sampai 0%
    # (umur >= 100% siklus, artinya panen normal tanpa penalti).
    can_early = age_ratio >= 0.6
    discount = max(0.0, min(0.25, (1.0 - age_ratio) * 0.625))
    early_cost = harvest_cost
    # Hasil = bagian umur yang sudah terbentuk, dikurangi penalti kematangan.
    # Jika umur >= 100%, retained = 1.0 (panen normal sepenuhnya).
    retained_b = min(1.0, age_ratio) * (1.0 - discount)
    yield_b = normal_yield * retained_b
    revenue_b = int(yield_b * price * (1.0 - discount * 0.4))
    profit_b = revenue_b - early_cost
    if discount > 0:
        maturity_reason = f"Hasil dipotong ~{int(round(discount * 100))}% karena belum matang penuh"
    else:
        maturity_reason = "Tanaman sudah matang penuh, panen tanpa penalti kualitas"
    reasons_b = [
        f"Umur tanam sudah {int(age_ratio * 100)}% dari siklus",
        "Mengunci hasil sebelum risiko membesar",
        maturity_reason,
    ]
    plan_b = [
        "Hari 1: Hitung area panen prioritas",
        "Hari 2: Siapkan keranjang & tenaga panen",
        "Hari 3-4: Panen bertahap area paling sehat",
        "Hari 5: Sortir hasil panen Grade A / B",
        "Hari 6: Hubungi pengepul / pasar terdekat",
        "Hari 7: Bersihkan lahan & evaluasi untung",
    ]

    # Option C: Tunggu / biarkan. Tetap dikenakan harvest_cost karena
    # tanaman tetap dipanen di akhir siklus.
    wait_cost = harvest_cost
    retained_c = 1.0 - (risk_score * 0.70)
    yield_c = normal_yield * retained_c
    revenue_c = int(yield_c * price)
    profit_c = revenue_c - wait_cost
    potential_loss_pct = int(round(risk_score * 70))
    if risk_score < 0.20:
        wait_subtitle = "Pantau rutin tanpa intervensi tambahan"
        wait_reasons = [
            "Tanpa biaya perawatan tambahan",
            "Tanaman cukup sehat untuk dipantau saja",
            "Lakukan pemeriksaan harian sebagai pencegahan",
        ]
    elif risk_score < 0.55:
        wait_subtitle = "Tanpa intervensi, namun risiko tetap berjalan"
        wait_reasons = [
            "Tanpa biaya perawatan tambahan",
            f"Estimasi kerugian ~{potential_loss_pct}% jika gejala memburuk",
            "Hanya disarankan jika gejala benar-benar ringan",
        ]
    else:
        wait_subtitle = "Berbahaya: risiko ditanggung penuh oleh petani"
        wait_reasons = [
            "Tanpa biaya perawatan, namun tanpa upaya pencegahan",
            f"Estimasi kerugian ~{potential_loss_pct}% jika dibiarkan",
            "Sangat berisiko untuk kondisi yang sudah berat",
        ]
    reasons_c = wait_reasons
    plan_c = [
        "Hari 1-7: Pantau gejala tiap pagi",
        "Catat perubahan warna daun & batang",
        "Siapkan rencana darurat jika memburuk",
    ]

    # Confidence = seberapa yakin engine bahwa opsi ini adalah tindakan
    # paling tepat untuk kondisi saat ini (bukan "seberapa berisiko opsi").
    # Rawat paling masuk akal ketika ada gejala (risk medium-tinggi) tapi
    # tidak ekstrem; kurang masuk akal ketika sehat (overkill) atau parah
    # (sulit diselamatkan).
    rawat_fit = 1.0 - abs(risk_score - 0.5) * 1.4
    rawat_confidence = int(max(45, min(95, 60 + rawat_fit * 35)))

    # Tunggu paling masuk akal saat risiko rendah; sangat tidak yakin saat
    # risiko sudah tinggi.
    tunggu_confidence = int(max(20, min(95, 90 - risk_score * 80)))

    # Panen awal: yakin kalau umur tanam sudah dekat/melewati 100%, kurang
    # yakin saat baru menyentuh 60%.
    panen_confidence = int(min(95, 50 + age_ratio * 45)) if can_early else 0

    options = [
        DecisionOption(
            key="rawat",
            title="Rawat Sekarang",
            subtitle="Intervensi terjadwal 7 hari",
            icon="🛠️",
            accent_color="#2E7D32",
            cost=care_cost,
            expected_yield_kg=round(yield_a, 1),
            revenue=revenue_a,
            profit=profit_a,
            risk=risk_level if risk_level != "high" else "medium",
            confidence=rawat_confidence,
            reasons=reasons_a,
            plan_steps=plan_a,
        ),
        DecisionOption(
            key="panen_awal",
            title="Panen Sekarang" if discount == 0 and can_early else "Panen Lebih Awal",
            subtitle=(
                "Tanaman sudah siap dipanen"
                if discount == 0 and can_early
                else "Kunci hasil panen sebelum risiko naik"
            ),
            icon="🧺",
            accent_color="#F9A825",
            cost=early_cost,
            expected_yield_kg=round(yield_b, 1) if can_early else 0.0,
            revenue=revenue_b if can_early else 0,
            profit=profit_b if can_early else -1,
            risk="low" if discount == 0 and can_early else "medium",
            confidence=panen_confidence,
            reasons=reasons_b if can_early else [
                "Tanaman belum cukup umur untuk panen dini",
                "Pilihan ini terkunci sampai umur >= 60% siklus",
            ],
            plan_steps=plan_b if can_early else [],
        ),
        DecisionOption(
            key="tunggu",
            title="Tunggu & Pantau",
            subtitle=wait_subtitle,
            icon="⏳",
            accent_color="#1565C0",
            cost=wait_cost,
            expected_yield_kg=round(yield_c, 1),
            revenue=revenue_c,
            profit=profit_c,
            risk="high" if risk_score >= 0.4 else risk_level,
            confidence=tunggu_confidence,
            reasons=reasons_c,
            plan_steps=plan_c,
        ),
    ]

    # Pick recommended option using a risk-adjusted economic score.
    # Profit remains the main signal, risk reduces unsafe choices, and
    # confidence adds a small area-scaled bonus so agronomic fit can decide
    # close calls without overwhelming meaningful profit differences.
    def score(opt: DecisionOption) -> float:
        risk_penalty = {"low": 0.0, "medium": -50_000, "high": -200_000}[opt.risk]
        confidence_bonus = opt.confidence * input.area_m2 * 20
        availability_penalty = -10_000_000 if opt.confidence == 0 else 0
        return opt.profit + confidence_bonus + risk_penalty + availability_penalty

    best = max(options, key=score)
    for opt in options:
        opt.recommended = opt.key == best.key

    if risk_level == "low":
        summary = (
            f"Kondisi {crop.name} terpantau aman. Lanjutkan perawatan rutin "
            "untuk menjaga hasil panen tetap optimal."
        )
    elif risk_level == "medium":
        summary = (
            f"{crop.name} menunjukkan gejala yang perlu diwaspadai. "
            "Tindakan cepat dapat menyelamatkan sebagian besar hasil."
        )
    else:
        summary = (
            f"Risiko gagal panen {crop.name} tinggi. Pertimbangkan langkah "
            "penyelamatan dan kunci hasil yang masih bisa diraih."
        )

    return DecisionResult(
        crop_name=crop.name,
        risk_score=round(risk_score, 2),
        risk_level=risk_level,
        summary=summary,
        options=options,
    )


def format_currency(value: int | float) -> str:
    return _format_rp(value)
