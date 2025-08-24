# -*- coding: utf-8 -*-
"""Historical Event Importer

Bu modül SENKRON'un historical event importer bileşeni için esnek CSV okuma sağlar.
UTF-8 BOM toleransı, opsiyonel sütunlar ve güçlü veri doğrulama destekler.

Desteklenen özellikler:
- UTF-8 BOM ve BOM'suz CSV dosyaları
- Opsiyonel sütunlar: id, category, weight
- Veri doğrulama ve filtreleme
- Güçlü hata yönetimi ve logging
"""

import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

def import_historical_events(
    csv_path: str,
    min_weight: float = 0.0,
    category_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    CSV dosyasından historical event verilerini esnek şekilde okur.
    
    Args:
        csv_path: CSV dosya yolu
        min_weight: Minimum ağırlık filtresi (varsayılan: 0.0)
        category_filter: Kategori filtresi (None ise tüm kategoriler)
    
    Returns:
        İşlenmiş event listesi
    
    Raises:
        FileNotFoundError: CSV dosyası bulunamadığında
        ValueError: CSV formatı geçersiz olduğunda
    """
    try:
        if not Path(csv_path).exists():
            raise FileNotFoundError(f"CSV dosyası bulunamadı: {csv_path}")
        
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
        
        if df.empty:
            logger.warning(f"Boş CSV dosyası: {csv_path}")
            return []
        
        df.columns = [col.strip().lower().lstrip('\ufeff') for col in df.columns]
        
        required_columns = {'date', 'title'}
        if not required_columns.issubset(set(df.columns)):
            missing = required_columns - set(df.columns)
            raise ValueError(f"Gerekli sütunlar eksik: {missing}")
        
        events = []
        skipped_invalid_date = 0
        skipped_empty_title = 0
        skipped_filter = 0
        
        for idx, row in df.iterrows():
            try:
                title = str(row['title']).strip()
                if not title or title.lower() in ['nan', 'none', '']:
                    skipped_empty_title += 1
                    continue
                
                date_parsed = pd.to_datetime(row['date'], errors='coerce')
                if pd.isna(date_parsed):
                    skipped_invalid_date += 1
                    continue
                
                if 'id' in df.columns and pd.notna(row['id']):
                    event_id = str(row['id'])
                else:
                    event_id = hashlib.md5(f"{title}_{date_parsed.date()}".encode()).hexdigest()[:8]
                
                category = str(row.get('category', 'macro')).strip()
                if category.lower() in ['nan', 'none', '']:
                    category = 'macro'
                
                try:
                    weight = float(row.get('weight', 1.0))
                    weight = max(0.0, min(5.0, weight))
                except (ValueError, TypeError):
                    weight = 1.0
                
                if weight < min_weight:
                    skipped_filter += 1
                    continue
                
                if category_filter and category.lower() != category_filter.lower():
                    skipped_filter += 1
                    continue
                
                event = {
                    'id': event_id,
                    'date': date_parsed.isoformat(),
                    'title': title,
                    'category': category,
                    'weight': weight
                }
                events.append(event)
                
            except Exception as e:
                logger.debug(f"Satır {idx} işlenirken hata: {e}")
                continue
        
        total_processed = len(events)
        total_skipped = skipped_invalid_date + skipped_empty_title + skipped_filter
        
        logger.info(f"CSV işlendi: {csv_path} - işlenen={total_processed}, "
                   f"atlanan={total_skipped} (geçersiz_tarih={skipped_invalid_date}, "
                   f"boş_başlık={skipped_empty_title}, filtre={skipped_filter})")
        
        if total_skipped > 0 and logger.isEnabledFor(logging.DEBUG):
            logger.debug("İlk 3 problemli satır örneği için debug logları kontrol edin")
        
        return events
        
    except Exception as e:
        logger.error(f"CSV okuma hatası {csv_path}: {e}")
        raise

def ready() -> bool:
    """Modülün hazır olup olmadığını döndürür."""
    try:
        import pandas  # noqa: F401
        return True
    except ImportError:
        return False

def describe() -> Dict[str, Any]:
    """Modül özeti."""
    return {
        "name": "historical_event_importer",
        "ready": ready(),
        "notes": "Esnek CSV importer - UTF-8 BOM, opsiyonel sütunlar, filtreleme",
        "supported_formats": ["CSV with UTF-8 BOM", "CSV without BOM"],
        "required_columns": ["date", "title"],
        "optional_columns": ["id", "category", "weight"]
    }
