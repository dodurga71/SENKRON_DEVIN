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

## 🧩 Notlar
- DİL KİLİDİ: Tüm açıklamalar **Türkçe** tutulmuştur.
- Devin görev akışı için `devin/prompts.md` dosyasındaki **kopyala–yapıştır** komutlarını kullan.
- Varlık dosyaları (zip’ler, pdf’ler) `data/` dizinine atılıp görevlerde içe aldırılacaktır.

— Oluşturulma: 2025-08-21T18:03:49.393382
