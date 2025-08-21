# SENKRON Makefile
# Devin AI için optimize edilmiş görevler

.PHONY: help install test lint format coverage clean dev docker-build docker-run

# Varsayılan hedef
help:
	@echo "SENKRON - Kullanılabilir komutlar:"
	@echo ""
	@echo "  install     - Bağımlılıkları yükle"
	@echo "  test        - Testleri çalıştır"
	@echo "  lint        - Kod kalitesi kontrolü (ruff check)"
	@echo "  format      - Kod formatla (ruff format)"
	@echo "  coverage    - Test coverage raporu (≥%75)"
	@echo "  dev         - Geliştirme sunucusunu başlat"
	@echo "  clean       - Geçici dosyaları temizle"
	@echo "  docker-build - Docker image oluştur"
	@echo "  docker-run  - Docker container çalıştır"

# Bağımlılık yükleme
install:
	pip install -U pip
	pip install -r requirements.txt

# Test çalıştırma
test:
	pytest -q

# Lint kontrolü
lint:
	ruff check .

# Kod formatlama
format:
	ruff format .

# Coverage raporu (≥%75 hedefi)
coverage:
	pytest --maxfail=1 --disable-warnings -q --cov=app --cov-branch --cov-report=term-missing

# Geliştirme sunucusu
dev:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Temizlik
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete

# Docker işlemleri
docker-build:
	docker build -t senkronx_plus:dev .

docker-run:
	docker run --rm -p 8000:8000 senkronx_plus:dev

# CI için birleşik komut
ci: install lint test coverage
	@echo "✅ CI pipeline tamamlandı!"