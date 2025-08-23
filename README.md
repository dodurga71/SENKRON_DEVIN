# SENKRON – Devin AI Başlangıç Paketi

Bu depo, **SENKRON**'u *Devin AI* içinde uçtan uca derlemek, test etmek ve ürünleştirmek için
hazırlanmış **bootstrapping** (başlangıç) iskeletidir. Kod, CI ve görev planı Devin'in
otonom çalışmasına uygun şekilde düzenlenmiştir.

## 🚀 Neler Var?
- **FastAPI** tabanlı minimal API (`/version`, `/healthz/details`)
- **Modül iskeletleri**: `ephemeris_engine.py`, `timeline_engine.py`, `ai_learner.py`,
  `prediction_backtester.py`, `sentiment_collector.py`, `historical_event_importer.py`,
  `unified_predictor.py`, `quantum_predictor.py`, `financial_predictor.py`
- **Devin için görev seti**: `devin/plan.md`, `devin/prompts.md`, `devin/checklist.md`
- **Docker**, **Makefile**, **pytest** ve **GitHub Actions CI**

## 🧭 Hızlı Başlangıç (Yerel)
```bash
# 1) Sanal ortam
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Kurulum
pip install -U pip
pip install -r requirements.txt

# 3) Çalıştır
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 4) Test
pytest -q
```

## 🐳 Docker
```bash
docker build -t senkronx_plus:dev .
docker run --rm -p 8000:8000 senkronx_plus:dev
```

## 🧪 Uç Noktalar
- `GET /version` – sürüm ve çalışma zamanı
- `GET /healthz/details` – temel sağlık kontrolü

## 📁 Klasör Yapısı
```
.
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── modules/
│       ├── ephemeris_engine.py
│       ├── timeline_engine.py
│       ├── ai_learner.py
│       ├── prediction_backtester.py
│       ├── sentiment_collector.py
│       ├── historical_event_importer.py
│       ├── unified_predictor.py
│       ├── quantum_predictor.py
│       └── financial_predictor.py
├── data/
│   ├── historical_events.csv
│   └── README.md
├── devin/
│   ├── plan.md
│   ├── prompts.md
│   └── checklist.md
├── tests/
│   └── test_version.py
├── .github/workflows/ci.yml
├── .devcontainer/devcontainer.json
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── requirements.txt
├── .env.example
└── README.md
```

## ⭐ SBZET v2025.9 Entegrasyonu

SENKRON artık **SBZET (Sevt×Sbzet) v2025.9** çerçevesi ile quantum temporal mechanics ve astrolojik analizi birleştiren unified prediction sistemi sunuyor.

### 🔮 Unified Predictor API

```bash
# POST /predict - Unified prediction skoru
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2024-01-01",
    "end_date": "2024-01-31", 
    "E": 5.0,
    "delta_g": 0.1,
    "D": 2.0,
    "weights": [0.7, 0.3]
  }'

# GET /patterns - Timeline pattern discovery
curl "http://localhost:8000/patterns?start=2024-01-01&end=2024-02-29"
```

### 🧮 SBZET Formülü

```
p = σ(k*(E-E0-α*D+β*Δg)) * exp(-γ*D)
σ(x) = 1/(1+exp(-x))
```

**Parametreler:**
- E: Enerji seviyesi
- D: Mesafe/gecikme faktörü  
- Δg: Gravitasyonel değişim
- E0=3.0, k=1.25, α=0.9, β=8.0, γ=0.8

### 🐍 Python Kullanımı

```python
from datetime import datetime, timezone, date
from app.modules.unified_predictor import unified_score
from app.modules.quantum_predictor import success_prob, QuantumParams
from app.modules.timeline_engine import build_window, discover_triggers

# Unified prediction
result = unified_score(
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 31),
    E=5.0, delta_g=0.1, D=2.0,
    weights=(0.7, 0.3)
)
print(f"Final Score: {result['final']:.3f}")
print(f"Astro: {result['astro']:.3f}, Quantum: {result['quant']:.3f}")

# SBZET quantum calculation
prob = success_prob(E=5.0, delta_g=0.1, D=2.0)
print(f"SBZET Probability: {prob:.3f}")

# Timeline pattern discovery
events_a = build_window(date(2024, 1, 1), date(2024, 1, 15))
events_b = build_window(date(2024, 1, 16), date(2024, 1, 31))
patterns = discover_triggers(events_a, events_b)
print(f"Discovered {len(patterns)} patterns")
```

## ⭐ Ephemeris Engine Örneği

```python
from datetime import datetime, timezone
from app.modules.ephemeris_engine import compute_positions, deg_to_sign, aspect_clusters

# Gezegen pozisyonlarını hesapla
dt = datetime(2024, 3, 21, 12, 0, 0, tzinfo=timezone.utc)  # İlkbahar ekinoksu
positions = compute_positions(dt)

# Güneş'in pozisyonu
sun = positions["positions"]["sun"]
print(f"Güneş: {sun['longitude']:.1f}° - {sun['zodiac']['sign']}")

# deg_to_sign fonksiyonu kullanımı
sign_index, sign_name, deg_in_sign, dms = deg_to_sign(sun['longitude'])
print(f"Güneş: {deg_in_sign:.1f}° {sign_name}")

# Aspect cluster analizi
aspects = aspect_clusters(date(2024, 3, 1), date(2024, 3, 31))
print(f"Aspect Density: {aspects['aspect_density']:.2f}")
```

## 📊 Modül Durumu

Tüm modüller şu anda "iskelet" durumundadır ve Devin AI tarafından genişletilmeyi beklemektedir:

- ✅ **FastAPI Bootstrap**: Temel uygulama yapısı hazır
- ✅ **ephemeris_engine**: Skyfield tabanlı gezegen hesaplamaları (tamamlandı)
- 🔄 **unified_predictor**: Fusion Core (iskelet)
- 🔄 **financial_predictor**: TA + Astro + Gann (iskelet)
- 🔄 **quantum_predictor**: Retrocausality + 3B zaman (iskelet)
- 🔄 **ai_learner**: PPO/Self-Play (iskelet)
- 🔄 **prediction_backtester**: F1, MAPE, Sharpe (iskelet)
- 🔄 **timeline_engine**: Retrokausal Zaman Tüneli (iskelet)
- 🔄 **sentiment_collector**: Twitter/Reddit/Telegram (iskelet)
- 🔄 **historical_event_importer**: Event data ingestion (iskelet)

## 🧩 Notlar
- DİL KİLİDİ: Tüm açıklamalar **Türkçe** tutulmuştur.
- Devin görev akışı için `devin/prompts.md` dosyasındaki **kopyala–yapıştır** komutlarını kullan.
- Varlık dosyaları (zip'ler, pdf'ler) `data/` dizinine atılıp görevlerde içe aldırılacaktır.

— Oluşturulma: 2025-08-21T18:03:49.393382
