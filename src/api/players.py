from typing import List, Dict, Any, Optional

from .cr_client import get_global_top_players


def fetch_top_300_players() -> List[Dict[str, Any]]:
    """
    Fetch approximately the top 300 global players.

    Uses:
      - first call:  limit=200
      - second call: limit=100 with 'after' cursor from the first page

    Returns:
        List of player dicts (truncated to 300 if API returns more).
    """
    # First page: top ~200
    first_page = get_global_top_players(limit=200)
    items: List[Dict[str, Any]] = first_page.get("items", [])

    # Try to get the 'after' cursor for pagination
    paging = first_page.get("paging", {})
    cursors: Dict[str, Optional[str]] = paging.get("cursors", {}) if paging else {}
    after_cursor: Optional[str] = cursors.get("after")

    # Second page: next ~100 players if cursor exists
    if after_cursor:
        second_page = get_global_top_players(limit=100, after=after_cursor)
        items.extend(second_page.get("items", []))

    # Ensure we only keep the first 300 entries
    return items[:300]
