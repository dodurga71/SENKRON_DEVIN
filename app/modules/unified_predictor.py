"""Unified Predictor (Fusion Core)

Bu modül SENKRON'un fusion core bileşenidir. Astrolojik ve quantum
skorları birleştirerek unified prediction skoru üretir.

Fusion Formülü:
final = sigmoid(w_astro * astro_score + w_quant * quant_score)

Bileşenler:
- astro_score: Normalize edilmiş aspect yoğunluğu [0,1]
- quant_score: SBZET quantum başarı olasılığı [0,1]
- weights: (w_astro, w_quant) ağırlık çifti
"""

import logging
import math
from datetime import date
from typing import Any, Dict, Tuple

from .quantum_predictor import success_prob
from .timeline_engine import build_window

logger = logging.getLogger(__name__)

def unified_score(
    start_date: date,
    end_date: date,
    E: float,
    delta_g: float,
    D: float,
    weights: Tuple[float, float] = (0.7, 0.3)
) -> Dict[str, Any]:
    """Unified prediction skoru hesaplar

    Args:
        start_date: Başlangıç tarihi
        end_date: Bitiş tarihi
        E: Quantum enerji seviyesi
        delta_g: Gravitasyonel değişim
        D: Mesafe/gecikme faktörü
        weights: (astro_weight, quantum_weight) ağırlık çifti

    Returns:
        Dict: {"astro": float, "quant": float, "final": float}
    """
    try:
        w_astro, w_quant = weights

        if not (0.0 <= w_astro <= 1.0 and 0.0 <= w_quant <= 1.0):
            raise ValueError("Ağırlıklar [0,1] aralığında olmalıdır")

        if start_date >= end_date:
            raise ValueError("Başlangıç tarihi bitiş tarihinden önce olmalıdır")

        astro_score = _calculate_astro_score(start_date, end_date)

        quant_score = success_prob(E, delta_g, D)

        combined = w_astro * astro_score + w_quant * quant_score

        final_score = _sigmoid(combined)

        result = {
            "astro": astro_score,
            "quant": quant_score,
            "final": final_score,
            "weights": weights,
            "metadata": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "quantum_params": {"E": E, "delta_g": delta_g, "D": D}
            }
        }

        logger.info(f"Unified score: astro={astro_score:.3f}, quant={quant_score:.3f}, final={final_score:.3f}")

        return result

    except Exception as e:
        logger.error(f"Unified score hesaplama hatası: {e}")
        return {
            "error": str(e),
            "astro": 0.0,
            "quant": 0.0,
            "final": 0.0
        }

def _calculate_astro_score(start_date: date, end_date: date) -> float:
    """Astrolojik aspect yoğunluğu skorunu hesaplar

    Args:
        start_date: Başlangıç tarihi
        end_date: Bitiş tarihi

    Returns:
        float: Normalize edilmiş astro skoru [0,1]
    """
    try:
        events = build_window(start_date, end_date)

        if not events:
            return 0.0

        total_aspects = 0
        total_events = len(events)

        for event in events:
            if event.astro_signature:
                aspect_count = len(event.astro_signature)
                total_aspects += aspect_count

        max_possible = total_events * 10

        if max_possible > 0:
            normalized_score = min(1.0, total_aspects / max_possible)
        else:
            normalized_score = 0.0

        return normalized_score

    except Exception as e:
        logger.warning(f"Astro skor hesaplama hatası: {e}")
        return 0.0

def _sigmoid(x: float) -> float:
    """Sigmoid aktivasyon fonksiyonu

    Args:
        x: Giriş değeri

    Returns:
        float: Sigmoid çıkışı [0,1]
    """
    try:
        if x > 500:
            return 1.0
        elif x < -500:
            return 0.0
        else:
            return 1.0 / (1.0 + math.exp(-x))
    except Exception:
        return 0.5  # Güvenli varsayılan

def ready() -> bool:
    """Modülün hazır olup olmadığını döndürür"""
    try:
        test_date = date(2024, 1, 1)
        result = unified_score(test_date, test_date, 5.0, 0.1, 2.0)

        return (
            isinstance(result, dict) and
            "final" in result and
            isinstance(result["final"], float) and
            0.0 <= result["final"] <= 1.0
        )
    except Exception:
        return False

def describe() -> Dict[str, Any]:
    """Unified predictor modül özeti"""
    return {
        "name": "unified_predictor",
        "version": "Fusion Core v1.0",
        "ready": ready(),
        "formula": "final = sigmoid(w_astro * astro_score + w_quant * quant_score)",
        "default_weights": {"astro": 0.7, "quantum": 0.3},
        "components": ["astro_score", "quant_score", "sigmoid_fusion"],
        "notes": "Astrolojik ve quantum skorları birleştiren fusion core"
    }
