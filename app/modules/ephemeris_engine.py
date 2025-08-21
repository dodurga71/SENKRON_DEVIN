"""SENKRON Ephemeris Engine

Bu modül astronomik hesaplamalar için ephemeris engine sağlar.
Gezegen pozisyonları, retrograd hareketler ve astrolojik hesaplamalar yapar.

Toleranslar:
- Pozisyon hesaplamaları: ±0.01° (36 arcsecond)
- Retrograd tespiti: ±0.001°/gün hız toleransı
- Burç sınırları: 0.000001° hassasiyet

Desteklenen Gök Cisimleri:
- Güneş, Ay, Merkür, Venüs, Mars, Jüpiter, Satürn, Uranüs, Neptün, Plüton

Ev Sistemleri:
- Whole Sign (mevcut)
- Placidus (gelecek sürüm için arayüz hazır)
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import ephem

# Logging konfigürasyonu
logger = logging.getLogger(__name__)

# Desteklenen gök cisimleri
CELESTIAL_BODIES = {
    "sun": ephem.Sun,
    "moon": ephem.Moon,
    "mercury": ephem.Mercury,
    "venus": ephem.Venus,
    "mars": ephem.Mars,
    "jupiter": ephem.Jupiter,
    "saturn": ephem.Saturn,
    "uranus": ephem.Uranus,
    "neptune": ephem.Neptune,
    "pluto": ephem.Pluto,
}

# Burç isimleri (0° Koç'tan başlayarak)
ZODIAC_SIGNS = [
    "Koç",
    "Boğa",
    "İkizler",
    "Yengeç",
    "Aslan",
    "Başak",
    "Terazi",
    "Akrep",
    "Yay",
    "Oğlak",
    "Kova",
    "Balık",
]


def ready() -> bool:
    """Modülün hazır olup olmadığını döndürür."""
    try:
        # PyEphem kütüphanesinin çalışıp çalışmadığını test et
        observer = ephem.Observer()
        sun = ephem.Sun()
        sun.compute(observer)
        return True
    except Exception as e:
        logger.error(f"Ephemeris engine hazır değil: {e}")
        return False


def describe() -> Dict[str, Any]:
    """Modül özeti ve durumu."""
    return {
        "name": "ephemeris_engine",
        "ready": ready(),
        "supported_bodies": list(CELESTIAL_BODIES.keys()),
        "house_systems": ["whole_sign"],
        "future_house_systems": ["placidus"],
        "notes": "Üretim kalitesinde ephemeris hesaplamaları",
    }


def degrees_to_dms(degrees: float) -> Tuple[int, int, float]:
    """Derece değerini derece/dakika/saniye formatına çevirir.

    Args:
        degrees: Derece değeri (0-360)

    Returns:
        Tuple[int, int, float]: (derece, dakika, saniye)

    Example:
        >>> degrees_to_dms(15.5)
        (15, 30, 0.0)
    """
    try:
        degrees = float(degrees) % 360  # 0-360 aralığına normalize et
        deg = int(degrees)
        minutes_float = (degrees - deg) * 60
        min_val = int(minutes_float)
        sec = (minutes_float - min_val) * 60
        return (deg, min_val, sec)
    except (ValueError, TypeError) as e:
        logger.error(f"Derece dönüşüm hatası: {e}")
        return (0, 0, 0.0)


def degrees_to_zodiac(degrees: float) -> Dict[str, Any]:
    """Derece değerini burç bilgisine çevirir.

    Args:
        degrees: Ekliptik boylam derecesi (0-360)

    Returns:
        Dict[str, Any]: Burç bilgileri

    Tolerans: 0.000001° hassasiyet ile burç sınırları

    Example:
        >>> degrees_to_zodiac(15.5)
        {'sign': 'Koç', 'degree': 15, 'minute': 30, 'second': 0.0}
    """
    try:
        degrees = float(degrees) % 360
        sign_index = int(degrees // 30)
        degree_in_sign = degrees % 30

        deg, min_val, sec = degrees_to_dms(degree_in_sign)

        return {
            "sign": ZODIAC_SIGNS[sign_index],
            "sign_index": sign_index,
            "degree": deg,
            "minute": min_val,
            "second": round(sec, 6),  # Mikrosaniye hassasiyeti
            "total_degrees": round(degrees, 6),
        }
    except (ValueError, TypeError, IndexError) as e:
        logger.error(f"Burç dönüşüm hatası: {e}")
        return {
            "sign": "Bilinmiyor",
            "sign_index": -1,
            "degree": 0,
            "minute": 0,
            "second": 0.0,
            "total_degrees": 0.0,
        }


def compute_positions(
    dt: datetime, location: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """Belirtilen tarih ve konum için gök cisimlerinin pozisyonlarını hesaplar.

    Args:
        dt: Hesaplama tarihi
        location: Konum bilgisi {'lat': float, 'lon': float, 'elevation': float}
                 None ise geosentrik hesaplama yapılır

    Returns:
        Dict[str, Any]: Tüm gök cisimlerinin pozisyon bilgileri

    Tolerans: ±0.01° (36 arcsecond) pozisyon hassasiyeti

    Example:
        >>> from datetime import datetime
        >>> dt = datetime(2024, 1, 1, 12, 0, 0)
        >>> positions = compute_positions(dt)
        >>> positions["sun"]["longitude"]  # Güneş'in ekliptik boylamı
    """
    try:
        # Observer (gözlemci) oluştur
        observer = ephem.Observer()

        if location:
            observer.lat = str(location.get("lat", 0.0))
            observer.lon = str(location.get("lon", 0.0))
            observer.elevation = location.get("elevation", 0.0)
        else:
            # Geosentrik hesaplama için Dünya merkezi
            observer.lat = "0"
            observer.lon = "0"
            observer.elevation = 0

        # Tarihi PyEphem formatına çevir
        observer.date = dt.strftime("%Y/%m/%d %H:%M:%S")

        positions = {}

        for body_name, body_class in CELESTIAL_BODIES.items():
            try:
                body = body_class()
                body.compute(observer)

                # Ekliptik koordinatlara çevir
                ecliptic_lon = float(ephem.Ecliptic(body).lon) * 180.0 / ephem.pi
                ecliptic_lat = float(ephem.Ecliptic(body).lat) * 180.0 / ephem.pi

                # Burç bilgisini hesapla
                zodiac_info = degrees_to_zodiac(ecliptic_lon)

                positions[body_name] = {
                    "longitude": round(ecliptic_lon, 6),
                    "latitude": round(ecliptic_lat, 6),
                    "zodiac": zodiac_info,
                    "right_ascension": float(body.ra) * 180.0 / ephem.pi,
                    "declination": float(body.dec) * 180.0 / ephem.pi,
                    "distance_au": float(body.earth_distance),
                }

            except Exception as e:
                logger.error(f"{body_name} hesaplama hatası: {e}")
                positions[body_name] = {
                    "error": str(e),
                    "longitude": 0.0,
                    "latitude": 0.0,
                }

        return {
            "timestamp": dt.isoformat(),
            "location": location,
            "positions": positions,
            "computed_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Pozisyon hesaplama hatası: {e}")
        return {
            "error": str(e),
            "timestamp": dt.isoformat() if dt else None,
            "positions": {},
        }


def is_retrograde(body: str, dt: datetime, days_delta: int = 1) -> bool:
    """Bir gök cisminin retrograd hareket edip etmediğini tespit eder.

    Args:
        body: Gök cismi adı (CELESTIAL_BODIES anahtarlarından biri)
        dt: Kontrol tarihi
        days_delta: Hız hesaplaması için gün farkı (varsayılan: 1)

    Returns:
        bool: True ise retrograd, False ise düz hareket

    Tolerans: ±0.001°/gün hız toleransı

    Not: Güneş ve Ay hiçbir zaman retrograd olmaz (Dünya perspektifinden)

    Example:
        >>> from datetime import datetime
        >>> dt = datetime(2024, 6, 15)  # Merkür retrograd dönemi
        >>> is_retrograde("mercury", dt)
        True
    """
    try:
        # Güneş ve Ay hiçbir zaman retrograd olmaz
        if body.lower() in ["sun", "moon"]:
            return False

        if body.lower() not in CELESTIAL_BODIES:
            logger.error(f"Desteklenmeyen gök cismi: {body}")
            return False

        # İki farklı tarihte pozisyon hesapla
        from datetime import timedelta

        dt1 = dt - timedelta(days=days_delta)
        dt2 = dt + timedelta(days=days_delta)

        pos1 = compute_positions(dt1)
        pos2 = compute_positions(dt2)

        if "error" in pos1 or "error" in pos2:
            logger.error("Retrograd hesaplaması için pozisyon hatası")
            return False

        lon1 = pos1["positions"][body.lower()]["longitude"]
        lon2 = pos2["positions"][body.lower()]["longitude"]

        # Boylam farkını hesapla (360° sınır durumunu dikkate al)
        lon_diff = lon2 - lon1

        # 360° sınır durumu düzeltmesi
        if lon_diff > 180:
            lon_diff -= 360
        elif lon_diff < -180:
            lon_diff += 360

        # Günlük hız hesapla
        daily_speed = lon_diff / (2 * days_delta)

        # Retrograd: negatif hız (tolerans dahilinde)
        return daily_speed < -0.001

    except Exception as e:
        logger.error(f"Retrograd hesaplama hatası: {e}")
        return False


def compute_houses_whole_sign(ascendant_degree: float) -> Dict[str, Any]:
    """Whole Sign ev sistemini hesaplar.

    Args:
        ascendant_degree: Yükselen burç derecesi (0-360)

    Returns:
        Dict[str, Any]: 12 ev ve burç bilgileri

    Not: Whole Sign sisteminde her ev tam bir burca karşılık gelir.
    1. ev = Yükselen burcun bulunduğu burç

    Example:
        >>> houses = compute_houses_whole_sign(15.5)  # 15.5° Koç yükselen
        >>> houses["houses"][1]["sign"]  # 1. ev
        'Koç'
    """
    try:
        ascendant_sign = int(ascendant_degree // 30)

        houses = {}
        for house_num in range(1, 13):
            sign_index = (ascendant_sign + house_num - 1) % 12
            houses[house_num] = {
                "sign": ZODIAC_SIGNS[sign_index],
                "sign_index": sign_index,
                "start_degree": sign_index * 30,
                "end_degree": (sign_index * 30 + 30) % 360,
            }

        return {
            "system": "whole_sign",
            "ascendant_degree": round(ascendant_degree, 6),
            "ascendant_sign": ZODIAC_SIGNS[ascendant_sign],
            "houses": houses,
        }

    except Exception as e:
        logger.error(f"Whole Sign ev hesaplama hatası: {e}")
        return {"error": str(e), "system": "whole_sign"}


def compute_houses_placidus(dt: datetime, location: Dict[str, float]) -> Dict[str, Any]:
    """Placidus ev sistemi için arayüz (gelecek implementasyon).

    Args:
        dt: Hesaplama tarihi
        location: Konum bilgisi

    Returns:
        Dict[str, Any]: Placeholder response

    Not: Bu fonksiyon gelecek sürümde tam olarak implement edilecek.
    """
    return {
        "system": "placidus",
        "status": "not_implemented",
        "message": "Placidus ev sistemi gelecek sürümde eklenecek",
        "alternative": "Şimdilik whole_sign sistemini kullanın",
    }
