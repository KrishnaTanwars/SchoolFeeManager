"""
Recently Opened Items Service for EduLedger ERP v1.9.0.
Tracks recently opened Student profiles, Receipts, and Financial Reports.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

class RecentlyOpenedService:
    _recent_items: List[Dict[str, Any]] = []

    @classmethod
    def add_recent_item(cls, category: str, title: str, item_id: Any, details: str = ""):
        """
        Adds or updates a recently accessed item.
        category: 'Student', 'Receipt', 'Report'
        """
        # Remove duplicate if exists
        cls._recent_items = [
            i for i in cls._recent_items
            if not (i["category"] == category and str(i["item_id"]) == str(item_id))
        ]

        cls._recent_items.insert(0, {
            "category": category,
            "title": title,
            "item_id": item_id,
            "details": details,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

        # Keep top 20
        cls._recent_items = cls._recent_items[:20]

    @classmethod
    def get_recent_items(cls, category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Returns recent items filtered by category if specified."""
        if category and category != "All":
            filtered = [i for i in cls._recent_items if i["category"] == category]
            return filtered[:limit]
        return cls._recent_items[:limit]

    @classmethod
    def clear_recent_items(cls):
        """Clears recent items history."""
        cls._recent_items.clear()
