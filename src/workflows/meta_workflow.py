from typing import Any, Dict, List, Set
from typing_extensions import TypedDict
import random

from langgraph.graph import StateGraph, END

from src.api.players import fetch_top_300_players


# ======================================================
# PHASE 0 STATE (Meta Build)
# ======================================================

class MetaState(TypedDict, total=False):
    top_players: List[Dict[str, Any]]
    required_deck_types: List[str]

    selected_players: List[Dict[str, Any]]     # players selected so far
    used_player_indices: Set[int]              # indices from top_players already used

    meta_raw_battles: List[Dict[str, Any]]
    normalized_battles: List[Dict[str, Any]]
    deck_type_counts: Dict[str, int]

    is_balanced: bool
    loop_count: int

    meta_analytics: Dict[str, Any]
    meta_plots: Dict[str, Any]

    notes: List[str]


# ======================================================
# NODE: fetch_top_300
# ======================================================

def fetch_top_300_node(state: MetaState) -> Dict[str, Any]:
    """
    Fetch top ~300 global players from leaderboard API.
    Initialize empty tracking structures for later steps.
    """
    top_players = fetch_top_300_players()

    note = f"Fetched {len(top_players)} top players from API"

    return {
        "top_players": top_players,
        "selected_players": [],
        "used_player_indices": set(),
        "meta_raw_battles": [],
        "normalized_battles": [],
        "deck_type_counts": {},
        "is_balanced": False,
        "loop_count": 0,
        "notes": [note],
        "required_deck_types": [
            "Siege",
            "Bait",
            "Cycle",
            "Bridge Spam",
            "Beatdown",
            # Hybrid intentionally excluded from quota
        ],
    }


# ======================================================
# NODE: sample_initial_50
# ======================================================

def sample_initial_50_node(state: MetaState) -> Dict[str, Any]:
    """
    Randomly sample 50 players from top_players.

    - selected_players: list of 50 player dicts
    - used_player_indices: set of their indices (for future +5 loops)
    """
    top_players = state.get("top_players", [])
    n = len(top_players)

    if n == 0:
        # Defensive: nothing to sample
        note = "sample_initial_50: top_players is empty, nothing to sample."
        notes = state.get("notes", []) + [note]
        return {"selected_players": [], "used_player_indices": set(), "notes": notes}

    sample_size = min(50, n)
    indices = random.sample(range(n), sample_size)

    selected = [top_players[i] for i in indices]
    used_indices = set(indices)

    note = f"sample_initial_50: sampled {sample_size} players out of {n}."

    notes = state.get("notes", []) + [note]

    return {
        "selected_players": selected,
        "used_player_indices": used_indices,
        "loop_count": 0,   # first batch, loop_count starts at 0
        "notes": notes,
    }


# ======================================================
# PHASE 0 — Graph Builder (with first two nodes)
# ======================================================

def build_meta_graph():
    """
    Phase 0 workflow so far:

        START → fetch_top_300 → sample_initial_50 → END

    In later steps we will insert the battle-fetch loop and analytics nodes
    after sample_initial_50.
    """
    graph = StateGraph(MetaState)

    graph.add_node("fetch_top_300", fetch_top_300_node)
    graph.add_node("sample_initial_50", sample_initial_50_node)

    graph.set_entry_point("fetch_top_300")
    graph.add_edge("fetch_top_300", "sample_initial_50")
    graph.add_edge("sample_initial_50", END)

    return graph.compile()
