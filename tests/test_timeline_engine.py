"""Tests for timeline_engine module (Retrokausal Zaman Tüneli)"""

from datetime import date

from app.modules.timeline_engine import (
    CausalLink,
    EventNode,
    MetaPattern,
    build_window,
    describe,
    discover_triggers,
    ready,
)


class TestDataClasses:
    """Test timeline engine dataclasses"""

    def test_event_node(self):
        """Test EventNode dataclass"""
        event = EventNode(
            id="test_1",
            date=date(2024, 1, 15),
            label="Test Event",
            astro_signature={"sun": 295.5, "moon": 120.3},
            meta={"category": "test"}
        )

        assert event.id == "test_1"
        assert event.date == date(2024, 1, 15)
        assert event.label == "Test Event"
        assert event.astro_signature["sun"] == 295.5
        assert event.meta["category"] == "test"

    def test_causal_link(self):
        """Test CausalLink dataclass"""
        link = CausalLink(
            src_id="event_1",
            dst_id="event_2",
            weight=0.75,
            delay_days=30,
            evidence={"correlation": 0.8}
        )

        assert link.src_id == "event_1"
        assert link.dst_id == "event_2"
        assert link.weight == 0.75
        assert link.delay_days == 30
        assert link.evidence["correlation"] == 0.8

    def test_meta_pattern(self):
        """Test MetaPattern dataclass"""
        pattern = MetaPattern(
            name="test_pattern",
            score=0.85,
            description="Test pattern description",
            nodes=["1", "2", "3"],
            links=["1->2", "2->3"]
        )

        assert pattern.name == "test_pattern"
        assert pattern.score == 0.85
        assert pattern.description == "Test pattern description"
        assert len(pattern.nodes) == 3
        assert len(pattern.links) == 2


class TestBuildWindow:
    """Test build_window function"""

    def test_build_window_with_data(self):
        """Test building window with existing CSV data"""
        events = build_window(date(2024, 1, 1), date(2024, 12, 31))

        assert isinstance(events, list)

        if events:
            event = events[0]
            assert isinstance(event, EventNode)
            assert hasattr(event, 'id')
            assert hasattr(event, 'date')
            assert hasattr(event, 'label')
            assert hasattr(event, 'astro_signature')
            assert hasattr(event, 'meta')

    def test_build_window_narrow_range(self):
        """Test building window with narrow date range"""
        events = build_window(date(2024, 2, 15), date(2024, 2, 25))
        assert isinstance(events, list)

        for event in events:
            assert date(2024, 2, 15) <= event.date <= date(2024, 2, 25)

    def test_build_window_no_data(self):
        """Test building window with no matching data"""
        events = build_window(date(2025, 1, 1), date(2025, 1, 2))
        assert isinstance(events, list)

    def test_build_window_missing_file(self):
        """Test graceful handling of missing CSV file"""
        events = build_window(date(2024, 1, 1), date(2024, 1, 31), "nonexistent.csv")
        assert isinstance(events, list)
        assert len(events) == 0

    def test_build_window_invalid_dates(self):
        """Test with invalid date range"""
        events = build_window(date(2024, 12, 31), date(2024, 1, 1))
        assert isinstance(events, list)
        assert len(events) == 0


class TestDiscoverTriggers:
    """Test discover_triggers function"""

    def test_discover_triggers_empty_windows(self):
        """Test pattern discovery with empty windows"""
        patterns = discover_triggers([], [])
        assert isinstance(patterns, list)
        assert len(patterns) == 0

    def test_discover_triggers_single_events(self):
        """Test pattern discovery with single events"""
        event_a = EventNode("1", date(2024, 1, 1), "Event A", {"sun": 0.0})
        event_b = EventNode("2", date(2024, 1, 15), "Event B", {"sun": 30.0})

        patterns = discover_triggers([event_a], [event_b])
        assert isinstance(patterns, list)

    def test_discover_triggers_similar_signatures(self):
        """Test pattern discovery with similar astrological signatures"""
        event_a = EventNode("1", date(2024, 1, 1), "Event A", {"sun": 0.0, "moon": 90.0})
        event_b = EventNode("2", date(2024, 1, 15), "Event B", {"sun": 5.0, "moon": 95.0})

        patterns = discover_triggers([event_a], [event_b])
        assert isinstance(patterns, list)

        if patterns:
            pattern = patterns[0]
            assert isinstance(pattern, MetaPattern)
            assert pattern.score > 0.0
            assert "1" in pattern.nodes
            assert "2" in pattern.nodes

    def test_discover_triggers_dissimilar_signatures(self):
        """Test pattern discovery with dissimilar signatures"""
        event_a = EventNode("1", date(2024, 1, 1), "Event A", {"sun": 0.0})
        event_b = EventNode("2", date(2024, 1, 15), "Event B", {"sun": 180.0})

        patterns = discover_triggers([event_a], [event_b])
        assert isinstance(patterns, list)

    def test_discover_triggers_reverse_chronology(self):
        """Test that reverse chronology is ignored"""
        event_a = EventNode("1", date(2024, 1, 15), "Event A", {"sun": 0.0})
        event_b = EventNode("2", date(2024, 1, 1), "Event B", {"sun": 5.0})

        patterns = discover_triggers([event_a], [event_b])
        assert isinstance(patterns, list)

    def test_discover_triggers_multiple_events(self):
        """Test pattern discovery with multiple events"""
        window_a = [
            EventNode("1", date(2024, 1, 1), "Event 1", {"sun": 0.0}),
            EventNode("2", date(2024, 1, 5), "Event 2", {"sun": 30.0})
        ]
        window_b = [
            EventNode("3", date(2024, 1, 10), "Event 3", {"sun": 5.0}),
            EventNode("4", date(2024, 1, 15), "Event 4", {"sun": 35.0})
        ]

        patterns = discover_triggers(window_a, window_b)
        assert isinstance(patterns, list)
        assert len(patterns) <= 10  # Should limit to top 10


class TestModuleFunctions:
    """Test module utility functions"""

    def test_ready(self):
        """Test ready function"""
        assert ready() is True

    def test_describe(self):
        """Test describe function"""
        desc = describe()
        assert isinstance(desc, dict)
        assert desc["name"] == "timeline_engine"
        assert "version" in desc
        assert desc["ready"] is True
        assert "components" in desc
        assert "functions" in desc
        assert desc["data_source"] == "data/historical_events.csv"
