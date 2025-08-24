import pytest
import tempfile
import os

from app.modules.historical_event_importer import import_historical_events, ready, describe


class TestHistoricalEventImporter:
    
    def test_ready_function(self):
        """Test that the module reports as ready when pandas is available."""
        assert ready() is True
    
    def test_describe_function(self):
        """Test module description."""
        desc = describe()
        assert desc["name"] == "historical_event_importer"
        assert desc["ready"] is True
        assert "required_columns" in desc
        assert "optional_columns" in desc
    
    def test_import_bom_csv(self):
        """Test importing CSV with UTF-8 BOM."""
        events = import_historical_events("tests/data/test_bom.csv")
        assert len(events) == 1
        assert events[0]["title"] == "Test Event"
        assert events[0]["category"] == "macro"
        assert events[0]["weight"] == 1.0
    
    def test_import_minimal_csv(self):
        """Test importing CSV with only required columns."""
        events = import_historical_events("tests/data/test_minimal.csv")
        assert len(events) == 2
        
        for event in events:
            assert "id" in event
            assert event["category"] == "macro"
            assert event["weight"] == 1.0
            assert event["title"] in ["Minimal Event", "Another Event"]
    
    def test_stable_id_generation(self):
        """Test that IDs are generated consistently for same title+date."""
        events1 = import_historical_events("tests/data/test_minimal.csv")
        events2 = import_historical_events("tests/data/test_minimal.csv")
        
        assert events1[0]["id"] == events2[0]["id"]
        assert events1[1]["id"] == events2[1]["id"]
    
    def test_min_weight_filter(self):
        """Test minimum weight filtering."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("date,title,weight\n")
            f.write("2024-01-01,Low Weight,0.5\n")
            f.write("2024-01-02,High Weight,2.0\n")
            f.write("2024-01-03,Medium Weight,1.5\n")
            temp_path = f.name
        
        try:
            events = import_historical_events(temp_path, min_weight=1.0)
            assert len(events) == 2
            titles = [e["title"] for e in events]
            assert "Low Weight" not in titles
            assert "High Weight" in titles
            assert "Medium Weight" in titles
        finally:
            os.unlink(temp_path)
    
    def test_category_filter(self):
        """Test category filtering."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("date,title,category\n")
            f.write("2024-01-01,Financial Event,financial\n")
            f.write("2024-01-02,Political Event,political\n")
            f.write("2024-01-03,Tech Event,technology\n")
            temp_path = f.name
        
        try:
            events = import_historical_events(temp_path, category_filter="financial")
            assert len(events) == 1
            assert events[0]["title"] == "Financial Event"
            assert events[0]["category"] == "financial"
        finally:
            os.unlink(temp_path)
    
    def test_invalid_dates_skipped(self):
        """Test that rows with invalid dates are skipped."""
        events = import_historical_events("tests/data/test_invalid_dates.csv")
        
        valid_events = [e for e in events if e["title"] == "Valid Event"]
        assert len(valid_events) == 1
        
        invalid_titles = [e["title"] for e in events]
        assert "Invalid Date Event" not in invalid_titles
    
    def test_weight_clamping(self):
        """Test weight clamping to 0.0-5.0 range."""
        events = import_historical_events("tests/data/test_weight_clamping.csv")
        
        weights = {e["title"]: e["weight"] for e in events}
        assert weights["Negative Weight"] == 0.0
        assert weights["High Weight"] == 5.0
        assert weights["Normal Weight"] == 2.5
    
    def test_empty_title_skipped(self):
        """Test that rows with empty titles are skipped."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("date,title\n")
            f.write("2024-01-01,Valid Title\n")
            f.write("2024-01-02,\n")
            f.write("2024-01-03,nan\n")
            f.write("2024-01-04,Another Valid\n")
            temp_path = f.name
        
        try:
            events = import_historical_events(temp_path)
            assert len(events) == 2
            titles = [e["title"] for e in events]
            assert "Valid Title" in titles
            assert "Another Valid" in titles
        finally:
            os.unlink(temp_path)
    
    def test_missing_required_columns_raises_error(self):
        """Test that missing required columns raise ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("title,category\n")
            f.write("Event Without Date,macro\n")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Gerekli sütunlar eksik"):
                import_historical_events(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_file_not_found_raises_error(self):
        """Test that missing file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            import_historical_events("nonexistent_file.csv")
    
    def test_combined_filters(self):
        """Test combining min_weight and category filters."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("date,title,category,weight\n")
            f.write("2024-01-01,Financial High,financial,3.0\n")
            f.write("2024-01-02,Financial Low,financial,0.5\n")
            f.write("2024-01-03,Tech High,technology,3.0\n")
            f.write("2024-01-04,Tech Low,technology,0.5\n")
            temp_path = f.name
        
        try:
            events = import_historical_events(
                temp_path, 
                min_weight=1.0, 
                category_filter="financial"
            )
            assert len(events) == 1
            assert events[0]["title"] == "Financial High"
            assert events[0]["category"] == "financial"
            assert events[0]["weight"] == 3.0
        finally:
            os.unlink(temp_path)
