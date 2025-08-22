"""SENKRON Timeline Engine (Retrokausal Zaman Tüneli)

Bu modül tarihsel olaylar arasındaki nedensel bağlantıları ve kalıpları analiz eder.
Astrolojik imzalar ve zaman gecikmeleri kullanarak olaylar arası ilişkileri keşfeder.

Özellikler:
- EventNode: Tarihsel olayları astrolojik imzalarla birlikte saklar
- CausalLink: Olaylar arası nedensel bağlantıları modeller
- MetaPattern: Tekrar eden kalıpları ve tetikleyicileri tanımlar
- Zaman penceresi analizi ve pattern keşfi

Skorlama Sistemi:
- Ortak gezegen açı kümeleri sayısı
- Gecikme uyumu (zaman tutarlılığı)
- Astrolojik imza benzerliği
"""

import csv
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List

# Logging konfigürasyonu
logger = logging.getLogger(__name__)


@dataclass
class EventNode:
    """Tarihsel olay düğümü.

    Attributes:
        id: Benzersiz olay kimliği
        date: Olay tarihi
        label: Olay etiketi/başlığı
        astro_signature: Astrolojik imza (gezegen pozisyonları)
        meta: Ek metadata (kategori, açıklama vb.)
    """
    id: str
    date: datetime
    label: str
    astro_signature: Dict[str, float]
    meta: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Veri doğrulama ve normalizasyon."""
        if not self.id:
            raise ValueError("EventNode id boş olamaz")
        if not self.label:
            raise ValueError("EventNode label boş olamaz")
        if not isinstance(self.astro_signature, dict):
            raise ValueError("astro_signature dict olmalı")


@dataclass
class CausalLink:
    """İki olay arasındaki nedensel bağlantı.

    Attributes:
        src_id: Kaynak olay kimliği
        dst_id: Hedef olay kimliği
        weight: Bağlantı ağırlığı (0.0-1.0)
        delay_days: Gecikme süresi (gün)
        evidence: Kanıt ve skorlama detayları
    """
    src_id: str
    dst_id: str
    weight: float
    delay_days: int
    evidence: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Veri doğrulama."""
        if not (0.0 <= self.weight <= 1.0):
            raise ValueError("Weight 0.0-1.0 aralığında olmalı")
        if self.delay_days < 0:
            raise ValueError("delay_days negatif olamaz")


@dataclass
class MetaPattern:
    """Meta kalıp - tekrar eden olay dizileri.

    Attributes:
        name: Kalıp adı
        score: Kalıp güvenilirlik skoru (0.0-1.0)
        description: Kalıp açıklaması
        nodes: İlgili olay kimliklerinin listesi
        links: İlgili bağlantı çiftlerinin listesi
    """
    name: str
    score: float
    description: str
    nodes: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Veri doğrulama."""
        if not (0.0 <= self.score <= 1.0):
            raise ValueError("Score 0.0-1.0 aralığında olmalı")


def ready() -> bool:
    """Modülün hazır olup olmadığını döndürür."""
    try:
        # Temel veri sınıflarının çalışıp çalışmadığını test et
        EventNode(
            id="test",
            date=datetime.now(),
            label="Test Event",
            astro_signature={"sun": 0.0}
        )
        CausalLink(
            src_id="test1",
            dst_id="test2",
            weight=0.5,
            delay_days=10
        )
        MetaPattern(
            name="Test Pattern",
            score=0.8,
            description="Test açıklaması"
        )
        return True
    except Exception as e:
        logger.error(f"Timeline engine hazır değil: {e}")
        return False


def describe() -> Dict[str, Any]:
    """Modül özeti ve durumu."""
    return {
        "name": "timeline_engine",
        "ready": ready(),
        "features": [
            "EventNode veri sınıfı",
            "CausalLink nedensel bağlantılar",
            "MetaPattern kalıp keşfi",
            "Zaman penceresi analizi"
        ],
        "data_sources": ["CSV dosyaları", "Astrolojik imzalar"],
        "notes": "Retrokausal zaman tüneli analizi",
    }


def parse_astro_signature(signature_str: str) -> Dict[str, float]:
    """Astrolojik imza string'ini dict'e çevirir.

    Args:
        signature_str: "sun:295.5,moon:120.3,mercury:280.1" formatında string

    Returns:
        Dict[str, float]: Gezegen adı -> derece mapping'i

    Example:
        >>> parse_astro_signature("sun:295.5,moon:120.3")
        {'sun': 295.5, 'moon': 120.3}
    """
    try:
        signature = {}
        if not signature_str or signature_str.strip() == "":
            return signature

        pairs = signature_str.split(",")
        for pair in pairs:
            if ":" in pair:
                planet, degree_str = pair.strip().split(":", 1)
                signature[planet.strip()] = float(degree_str.strip())

        return signature
    except (ValueError, AttributeError) as e:
        logger.error(f"Astrolojik imza parse hatası: {e}")
        return {}


def build_window(
    start_date: datetime,
    end_date: datetime,
    events_csv: str = "data/historical_events.csv"
) -> List[EventNode]:
    """Belirtilen tarih aralığındaki olayları yükler.

    Args:
        start_date: Başlangıç tarihi
        end_date: Bitiş tarihi
        events_csv: CSV dosya yolu

    Returns:
        List[EventNode]: Tarih aralığındaki olaylar

    CSV Format:
        id,date,label,category,description,astro_signature

    Example:
        >>> from datetime import datetime
        >>> start = datetime(2024, 1, 1)
        >>> end = datetime(2024, 6, 30)
        >>> events = build_window(start, end)
        >>> len(events)  # İlk 6 aydaki olay sayısı
    """
    try:
        events = []

        # Dosya varlığını kontrol et
        if not os.path.exists(events_csv):
            logger.warning(f"CSV dosyası bulunamadı: {events_csv}")
            return events

        with open(events_csv, encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    # Tarihi parse et
                    event_date = datetime.strptime(row['date'], '%Y-%m-%d')

                    # Tarih aralığını kontrol et
                    if not (start_date <= event_date <= end_date):
                        continue

                    # Astrolojik imzayı parse et
                    astro_sig = parse_astro_signature(row.get('astro_signature', ''))

                    # Meta bilgileri topla
                    meta = {
                        'category': row.get('category', ''),
                        'description': row.get('description', ''),
                        'source_file': events_csv
                    }

                    # EventNode oluştur
                    event = EventNode(
                        id=row['id'],
                        date=event_date,
                        label=row['label'],
                        astro_signature=astro_sig,
                        meta=meta
                    )

                    events.append(event)

                except (ValueError, KeyError) as e:
                    logger.error(f"Olay parse hatası (satır {reader.line_num}): {e}")
                    continue

        logger.info(f"{len(events)} olay yüklendi ({start_date} - {end_date})")
        return events

    except Exception as e:
        logger.error(f"Window build hatası: {e}")
        return []


def calculate_astro_similarity(sig1: Dict[str, float], sig2: Dict[str, float]) -> float:
    """İki astrolojik imza arasındaki benzerliği hesaplar.

    Args:
        sig1: İlk astrolojik imza
        sig2: İkinci astrolojik imza

    Returns:
        float: Benzerlik skoru (0.0-1.0)

    Algoritma:
        - Ortak gezegenler için açı farkları hesaplanır
        - 0°-30° fark: yüksek benzerlik
        - 30°-60° fark: orta benzerlik
        - 60°+ fark: düşük benzerlik
    """
    try:
        if not sig1 or not sig2:
            return 0.0

        common_planets = set(sig1.keys()) & set(sig2.keys())
        if not common_planets:
            return 0.0

        total_similarity = 0.0

        for planet in common_planets:
            angle1 = sig1[planet] % 360
            angle2 = sig2[planet] % 360

            # Açı farkını hesapla (0-180 aralığında)
            diff = abs(angle1 - angle2)
            if diff > 180:
                diff = 360 - diff

            # Benzerlik skoru (0-30° = 1.0, 30-60° = 0.5, 60-180° = 0.0)
            if diff <= 30:
                similarity = 1.0 - (diff / 30) * 0.5  # 1.0 -> 0.5
            elif diff <= 60:
                similarity = 0.5 - ((diff - 30) / 30) * 0.5  # 0.5 -> 0.0
            else:
                similarity = 0.0

            total_similarity += similarity

        # Ortalama benzerlik
        return total_similarity / len(common_planets)

    except Exception as e:
        logger.error(f"Astrolojik benzerlik hesaplama hatası: {e}")
        return 0.0


def discover_triggers(
    window_a: List[EventNode],
    window_b: List[EventNode],
    min_score: float = 0.3
) -> List[MetaPattern]:
    """İki zaman penceresi arasındaki tetikleyici kalıpları keşfeder.

    Args:
        window_a: İlk zaman penceresi olayları
        window_b: İkinci zaman penceresi olayları
        min_score: Minimum kalıp skoru eşiği

    Returns:
        List[MetaPattern]: Keşfedilen kalıplar

    Algoritma:
        1. Her A olayı için B olaylarıyla benzerlik hesapla
        2. Zaman gecikmesi tutarlılığını kontrol et
        3. Ortak gezegen açı kümelerini say
        4. Skorlama: astro_similarity * delay_consistency * common_patterns

    Example:
        >>> events_jan = build_window(datetime(2024,1,1), datetime(2024,1,31))
        >>> events_feb = build_window(datetime(2024,2,1), datetime(2024,2,28))
        >>> patterns = discover_triggers(events_jan, events_feb)
    """
    try:
        patterns = []

        if not window_a or not window_b:
            logger.warning("Boş pencere(ler) - pattern keşfi yapılamıyor")
            return patterns

        # Her A olayı için B olaylarıyla karşılaştır
        for event_a in window_a:
            for event_b in window_b:
                # Zaman gecikmesi hesapla
                delay = (event_b.date - event_a.date).days
                if delay <= 0:  # B olayı A'dan önce olamaz
                    continue

                # Astrolojik benzerlik hesapla
                astro_sim = calculate_astro_similarity(
                    event_a.astro_signature,
                    event_b.astro_signature
                )

                if astro_sim < 0.1:  # Çok düşük benzerlik
                    continue

                # Kategori uyumu bonusu
                category_bonus = 0.0
                if (event_a.meta.get('category') == event_b.meta.get('category') and
                    event_a.meta.get('category')):
                    category_bonus = 0.2

                # Gecikme tutarlılığı (7-90 gün arası ideal)
                delay_consistency = 1.0
                if delay < 7:
                    delay_consistency = delay / 7.0
                elif delay > 90:
                    delay_consistency = max(0.1, 1.0 - (delay - 90) / 365.0)

                # Toplam skor hesapla
                total_score = (astro_sim * 0.6 +
                              delay_consistency * 0.3 +
                              category_bonus * 0.1)

                if total_score >= min_score:
                    # Pattern oluştur
                    pattern_name = f"{event_a.label} → {event_b.label}"
                    description = (
                        f"Astrolojik benzerlik: {astro_sim:.2f}, "
                        f"Gecikme: {delay} gün, "
                        f"Kategori: {event_a.meta.get('category', 'N/A')}"
                    )

                    pattern = MetaPattern(
                        name=pattern_name,
                        score=total_score,
                        description=description,
                        nodes=[event_a.id, event_b.id],
                        links=[f"{event_a.id}->{event_b.id}"]
                    )

                    patterns.append(pattern)

        # Skorlara göre sırala
        patterns.sort(key=lambda p: p.score, reverse=True)

        logger.info(f"{len(patterns)} pattern keşfedildi")
        return patterns

    except Exception as e:
        logger.error(f"Pattern keşif hatası: {e}")
        return []


def analyze_pattern_clusters(patterns: List[MetaPattern]) -> Dict[str, Any]:
    """Keşfedilen kalıpları kümeler halinde analiz eder.

    Args:
        patterns: Keşfedilen kalıplar listesi

    Returns:
        Dict[str, Any]: Küme analizi sonuçları

    Analiz:
        - Yüksek skorlu kalıplar (>0.7)
        - Orta skorlu kalıplar (0.4-0.7)
        - Düşük skorlu kalıplar (<0.4)
        - En sık tekrar eden node'lar
        - Ortalama gecikme süreleri
    """
    try:
        if not patterns:
            return {"error": "Analiz için pattern bulunamadı"}

        high_score = [p for p in patterns if p.score > 0.7]
        medium_score = [p for p in patterns if 0.4 <= p.score <= 0.7]
        low_score = [p for p in patterns if p.score < 0.4]

        # En sık geçen node'ları bul
        node_frequency = {}
        for pattern in patterns:
            for node in pattern.nodes:
                node_frequency[node] = node_frequency.get(node, 0) + 1

        most_frequent_nodes = sorted(
            node_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return {
            "total_patterns": len(patterns),
            "high_score_patterns": len(high_score),
            "medium_score_patterns": len(medium_score),
            "low_score_patterns": len(low_score),
            "average_score": sum(p.score for p in patterns) / len(patterns),
            "most_frequent_nodes": most_frequent_nodes,
            "top_patterns": [
                {
                    "name": p.name,
                    "score": p.score,
                    "description": p.description
                }
                for p in patterns[:3]
            ]
        }

    except Exception as e:
        logger.error(f"Pattern küme analizi hatası: {e}")
        return {"error": str(e)}
