"""Ephemeris Engine - Skyfield tabanlı gezegen pozisyon hesaplamaları

Bu modül Skyfield kütüphanesi kullanarak gezegenlerin ekliptik boylamlarını,
retrograd durumlarını ve burç pozisyonlarını hesaplar.

Desteklenen gök cisimleri:
- Güneş, Ay, Merkür, Venüs, Mars, Jüpiter, Satürn, Uranüs, Neptün, Plüton

Ephemeris verileri: DE440s (öncelik), DE421 (yedek)
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

from skyfield.api import Loader, utc

logger = logging.getLogger(__name__)

ZODIAC_SIGNS = [
    "Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak",
    "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"
]

CELESTIAL_BODIES = {
    'sun': 'sun',
    'moon': 'moon',
    'mercury': 'mercury',
    'venus': 'venus',
    'mars': 'mars barycenter',
    'jupiter': 'jupiter barycenter',
    'saturn': 'saturn barycenter',
    'uranus': 'uranus barycenter',
    'neptune': 'neptune barycenter',
    'pluto': 'pluto barycenter'
}

@dataclass
class BodyPosition:
    """Gök cismi pozisyon bilgileri (kullanıcı API'si için)"""
    name: str
    lon_deg: float
    retrograde: bool
    sign_index: int
    sign_name: str
    deg_in_sign: float
    dms: Tuple[int, int, float]  # derece, dakika, saniye

_loader = None
_ephemeris = None

def _get_ephemeris():
    """Ephemeris verilerini yükler (DE440s öncelik, DE421 yedek)"""
    global _loader, _ephemeris

    if _ephemeris is not None:
        return _ephemeris

    try:
        _loader = Loader('~/skyfield-data', verbose=False)

        try:
            _ephemeris = _loader('de440s.bsp')
            logger.info("DE440s ephemeris yüklendi")
        except Exception as e:
            logger.warning(f"DE440s yüklenemedi: {e}, DE421 deneniyor...")
            _ephemeris = _loader('de421.bsp')
            logger.info("DE421 ephemeris yüklendi")

        return _ephemeris

    except Exception as e:
        logger.error(f"Ephemeris yüklenemedi: {e}")
        raise RuntimeError(f"Ephemeris verileri yüklenemedi: {e}") from e

def degrees_to_dms(angle_deg: float) -> Tuple[int, int, float]:
    """Derece değerini derece/dakika/saniye formatına çevirir (test API'si)"""
    angle_deg = angle_deg % 360.0
    degrees = int(angle_deg)
    minutes_float = (angle_deg - degrees) * 60.0
    minutes = int(minutes_float)
    seconds = (minutes_float - minutes) * 60.0
    return degrees, minutes, seconds

def degrees_to_zodiac(angle_deg: float) -> Dict[str, Any]:
    """Derece değerini burç bilgilerine çevirir (test API'si)"""
    angle_deg = angle_deg % 360.0
    sign_index = int(angle_deg // 30)
    sign_name = ZODIAC_SIGNS[sign_index]
    deg_in_sign = angle_deg % 30.0
    degrees, minutes, seconds = degrees_to_dms(deg_in_sign)

    return {
        "sign": sign_name,
        "sign_index": sign_index,
        "degree": degrees,
        "minute": minutes,
        "second": seconds
    }

def deg_to_sign(angle_deg: float) -> Tuple[int, str, float, Tuple[int, int, float]]:
    """Derece değerini burç bilgilerine çevirir (kullanıcı API'si)"""
    angle_deg = angle_deg % 360.0
    sign_index = int(angle_deg // 30)
    sign_name = ZODIAC_SIGNS[sign_index]
    deg_in_sign = angle_deg % 30.0
    degrees, minutes, seconds = degrees_to_dms(deg_in_sign)
    return sign_index, sign_name, deg_in_sign, (degrees, minutes, seconds)

def _calculate_retrograde(planet_name: str, when: datetime, delta_days: float = 1.0) -> bool:
    """Retrograd durumunu hesaplar (boylam türevinden)"""
    try:
        if planet_name in ['sun', 'moon']:
            return False

        ephemeris = _get_ephemeris()
        earth = ephemeris['earth']

        ts = _loader.timescale()
        t1 = ts.from_datetime(when.replace(tzinfo=utc))
        t2 = ts.from_datetime((when + timedelta(days=delta_days)).replace(tzinfo=utc))

        if planet_name in CELESTIAL_BODIES:
            planet = ephemeris[CELESTIAL_BODIES[planet_name]]
        else:
            return False

        astrometric1 = earth.at(t1).observe(planet)
        apparent1 = astrometric1.apparent()
        lat1, lon1, distance1 = apparent1.ecliptic_latlon()

        astrometric2 = earth.at(t2).observe(planet)
        apparent2 = astrometric2.apparent()
        lat2, lon2, distance2 = apparent2.ecliptic_latlon()

        lon1_deg = float(lon1.degrees)
        lon2_deg = float(lon2.degrees)

        if abs(lon2_deg - lon1_deg) > 180:
            if lon2_deg > lon1_deg:
                lon1_deg += 360
            else:
                lon2_deg += 360

        derivative = (lon2_deg - lon1_deg) / delta_days
        return bool(derivative < 0)

    except Exception as e:
        logger.warning(f"Retrograd hesaplama hatası {planet_name}: {e}")
        return False

def is_retrograde(planet_name: str, when: datetime) -> bool:
    """Retrograd durumunu kontrol eder (test API'si)"""
    return _calculate_retrograde(planet_name, when)

def compute_positions(when: Optional[datetime], location: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """Belirtilen zamandaki gezegen pozisyonlarını hesaplar (test API'si)"""
    try:
        if when is None:
            return {"error": "Geçersiz tarih"}

        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        elif when.tzinfo != timezone.utc:
            when = when.astimezone(timezone.utc)

        ephemeris = _get_ephemeris()
        earth = ephemeris['earth']
        ts = _loader.timescale()
        t = ts.from_datetime(when)

        positions = {}

        for body_name in CELESTIAL_BODIES.keys():
            try:
                if body_name == 'sun':
                    planet = ephemeris['sun']
                elif body_name == 'moon':
                    planet = ephemeris['moon']
                else:
                    planet = ephemeris[CELESTIAL_BODIES[body_name]]

                astrometric = earth.at(t).observe(planet)
                apparent = astrometric.apparent()
                lat, lon, distance = apparent.ecliptic_latlon()

                lon_deg = float(lon.degrees)
                if lon_deg < 0:
                    lon_deg += 360.0
                elif lon_deg >= 360:
                    lon_deg -= 360.0

                zodiac_info = degrees_to_zodiac(lon_deg)

                body_pos = {
                    "longitude": lon_deg,
                    "zodiac": zodiac_info
                }

                positions[body_name] = body_pos

            except Exception as e:
                logger.error(f"Pozisyon hesaplama hatası {body_name}: {e}")
                continue

        result = {
            "timestamp": when.isoformat(),
            "positions": positions
        }

        if location:
            result["location"] = location

        return result

    except Exception as e:
        logger.error(f"compute_positions hatası: {e}")
        return {"error": str(e)}

def compute_houses_whole_sign(ascendant_deg: float) -> Dict[str, Any]:
    """Whole Sign ev sistemi hesaplaması"""
    try:
        asc_sign_index = int(ascendant_deg // 30)
        asc_sign_name = ZODIAC_SIGNS[asc_sign_index]

        houses = {}
        for house_num in range(1, 13):
            sign_index = (asc_sign_index + house_num - 1) % 12
            sign_name = ZODIAC_SIGNS[sign_index]
            houses[house_num] = {"sign": sign_name}

        return {
            "system": "whole_sign",
            "ascendant_sign": asc_sign_name,
            "houses": houses
        }

    except Exception as e:
        logger.error(f"Whole sign ev hesaplama hatası: {e}")
        return {"error": str(e)}

def compute_houses_placidus(when: datetime, location: Dict[str, float]) -> Dict[str, Any]:
    """Placidus ev sistemi placeholder"""
    return {
        "system": "placidus",
        "status": "not_implemented"
    }

def ready() -> bool:
    """Modülün hazır olup olmadığını döndürür"""
    try:
        _get_ephemeris()
        return True
    except Exception:
        return False

def describe() -> Dict[str, Any]:
    """Modül özeti"""
    return {
        "name": "ephemeris_engine",
        "ready": ready(),
        "notes": "Skyfield tabanlı ephemeris engine (DE440s/DE421)",
        "supported_bodies": list(CELESTIAL_BODIES.keys()),
        "zodiac_signs": ZODIAC_SIGNS
    }
