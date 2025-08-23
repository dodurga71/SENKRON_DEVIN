"""Timeline Engine (Retrokausal Zaman Tüneli)

Bu modül SENKRON'un timeline engine bileşenidir. Retrokausal zaman tüneli
kavramını kullanarak tarihsel olaylar arasındaki nedensel bağlantıları
ve meta-pattern'leri keşfeder.

Temel Kavramlar:
- EventNode: Tarihsel olay düğümü (astrolojik imza ile)
- CausalLink: Olaylar arası nedensel bağlantı
- MetaPattern: Keşfedilen üst-düzey pattern'ler
"""

import csv
import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

@dataclass
class EventNode:
    """Tarihsel olay düğümü"""
    id: str
    date: date
    label: str
    astro_signature: Dict[str, Any] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CausalLink:
    """Olaylar arası nedensel bağlantı"""
    src_id: str
    dst_id: str
    weight: float
    delay_days: int
    evidence: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetaPattern:
    """Keşfedilen meta-pattern"""
    name: str
    score: float
    description: str
    nodes: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)

def build_window(start_date: date, end_date: date, events_csv: str = "data/historical_events.csv") -> List[EventNode]:
    """Belirtilen tarih aralığındaki olayları yükler

    Args:
        start_date: Başlangıç tarihi
        end_date: Bitiş tarihi
        events_csv: CSV dosya yolu

    Returns:
        List[EventNode]: Tarih aralığındaki olaylar
    """
    try:
        events = []
        csv_path = Path(events_csv)

        if not csv_path.exists():
            logger.warning(f"CSV dosyası bulunamadı: {events_csv}")
            return []

        with open(csv_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    event_date = datetime.strptime(row['date'], '%Y-%m-%d').date()

                    if start_date <= event_date <= end_date:
                        astro_sig = {}
                        if 'astro_signature' in row and row['astro_signature']:
                            try:
                                pairs = row['astro_signature'].split(',')
                                for pair in pairs:
                                    if ':' in pair:
                                        planet, lon_str = pair.split(':')
                                        astro_sig[planet.strip()] = float(lon_str.strip())
                            except Exception as e:
                                logger.warning(f"Astro signature parse hatası: {e}")

                        meta = {
                            'category': row.get('category', ''),
                            'description': row.get('description', '')
                        }

                        event = EventNode(
                            id=row['id'],
                            date=event_date,
                            label=row['label'],
                            astro_signature=astro_sig,
                            meta=meta
                        )
                        events.append(event)

                except Exception as e:
                    logger.warning(f"Olay parse hatası: {e}, satır: {row}")
                    continue

        logger.info(f"Yüklenen olay sayısı: {len(events)} ({start_date} - {end_date})")
        return events

    except Exception as e:
        logger.error(f"CSV yükleme hatası: {e}")
        return []

def discover_triggers(window_a: List[EventNode], window_b: List[EventNode]) -> List[MetaPattern]:
    """İki pencere arasındaki tetikleyici pattern'leri keşfeder

    Args:
        window_a: İlk pencere olayları
        window_b: İkinci pencere olayları

    Returns:
        List[MetaPattern]: Keşfedilen pattern'ler
    """
    try:
        patterns = []

        if not window_a or not window_b:
            return patterns

        for event_a in window_a:
            for event_b in window_b:
                try:
                    delay = (event_b.date - event_a.date).days

                    if delay <= 0:  # Sadece ileriye dönük bağlantılar
                        continue

                    similarity_score = _calculate_astro_similarity(
                        event_a.astro_signature,
                        event_b.astro_signature
                    )

                    if similarity_score > 0.3:  # Eşik değeri
                        pattern_name = f"trigger_{event_a.id}_to_{event_b.id}"

                        pattern = MetaPattern(
                            name=pattern_name,
                            score=similarity_score,
                            description=f"Astrolojik tetikleyici: {event_a.label} → {event_b.label} ({delay} gün)",
                            nodes=[event_a.id, event_b.id],
                            links=[f"{event_a.id}->{event_b.id}"]
                        )
                        patterns.append(pattern)

                except Exception as e:
                    logger.warning(f"Pattern analiz hatası: {e}")
                    continue

        patterns.sort(key=lambda p: p.score, reverse=True)

        logger.info(f"Keşfedilen pattern sayısı: {len(patterns)}")
        return patterns[:10]  # En iyi 10 pattern

    except Exception as e:
        logger.error(f"Pattern keşif hatası: {e}")
        return []

def _calculate_astro_similarity(sig_a: Dict[str, float], sig_b: Dict[str, float]) -> float:
    """İki astrolojik imza arasındaki benzerlik skorunu hesaplar"""
    try:
        if not sig_a or not sig_b:
            return 0.0

        common_planets = set(sig_a.keys()) & set(sig_b.keys())

        if not common_planets:
            return 0.0

        total_similarity = 0.0

        for planet in common_planets:
            lon_a = sig_a[planet]
            lon_b = sig_b[planet]

            diff = abs(lon_a - lon_b)
            if diff > 180:
                diff = 360 - diff

            similarity = 1.0 - (diff / 180.0)
            total_similarity += similarity

        avg_similarity = total_similarity / len(common_planets)

        return avg_similarity

    except Exception as e:
        logger.warning(f"Astro benzerlik hesaplama hatası: {e}")
        return 0.0

def ready() -> bool:
    """Modülün hazır olup olmadığını döndürür"""
    try:
        empty_patterns = discover_triggers([], [])
        return isinstance(empty_patterns, list)
    except Exception:
        return False

def describe() -> Dict[str, Any]:
    """Timeline engine modül özeti"""
    return {
        "name": "timeline_engine",
        "version": "Retrokausal Zaman Tüneli v1.0",
        "ready": ready(),
        "components": ["EventNode", "CausalLink", "MetaPattern"],
        "functions": ["build_window", "discover_triggers"],
        "data_source": "data/historical_events.csv",
        "notes": "Tarihsel olaylar arası nedensel pattern keşfi"
    }
