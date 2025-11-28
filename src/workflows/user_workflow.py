from typing import Any, Dict, List
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END

from src.api.battles import get_player_battlelog
from src.analytics.battle_filters import filter_and_normalize_ranked_1v1
from src.analytics.user_analytics import compute_user_analytics
from src.analytics.plots import generate_card_plots

# ---------- LangGraph State Definition ----------


class UserAnalyticsState(TypedDict, total=False):
    """
    State for the Phase 1 user analytics workflow.

    Fields:

      - player_tag: input from user (e.g. "#8C8JJQLG")
      - battles_raw: raw battlelog list from Clash Royale API
      - battles_filtered: ranked/Trophy Road 1v1 battles (normalized)
      - user_analytics: analytics dict (same schema as meta_analytics)
      - user_plots: optional dict of plot paths (usually analytics["plots"])
      - notes: optional list of debug / info strings
    """

    player_tag: str
    battles_raw: List[Dict[str, Any]]
    battles_filtered: List[Dict[str, Any]]
    user_analytics: Dict[str, Any]
    user_llm_tables: Dict[str, Any]
    user_plots: Dict[str, Any]
    notes: List[str]
    
# ---------- LLM helper table builders ----------

def build_user_summary_table(summary: dict):
    table = []
    for key, value in (summary or {}).items():
        table.append({"metric": key, "value": value})
    return table


def build_user_deck_summary(user_analytics):
    """
    Build a per-deck-type summary for the user.

    Handles a few possible shapes:

    - my_deck_types as a dict:
        {deck_type -> games_played}
    - my_deck_types as a list of rows:
        [{"deck_type": "...", "games": ...}, ...]
    - and falls back to best_decks if my_deck_types is missing/empty.
    """
    # ----- 1) Normalise my_deck_types into {deck_type: games} -----
    raw = user_analytics.get("my_deck_types") or {}
    deck_counts: Dict[str, int] = {}

    if isinstance(raw, dict):
        # Already in the desired shape
        deck_counts = raw
    elif isinstance(raw, list):
        # Build counts from list of dicts
        for row in raw:
            if not isinstance(row, dict):
                continue
            deck_type = (
                row.get("deck_type")
                or row.get("my_deck_type")
                or row.get("deck_type_name")
            )
            if not deck_type:
                continue

            # Try a few common keys for "games"
            games_val = (
                row.get("games")
                or row.get("games_played")
                or row.get("count")
                or 0
            )
            try:
                games_val = int(games_val)
            except (TypeError, ValueError):
                games_val = 0

            deck_counts[deck_type] = deck_counts.get(deck_type, 0) + games_val

    # If we still don't have anything, fall back to best_decks' games
    best_decks_raw = user_analytics.get("best_decks", []) or []
    if not deck_counts and isinstance(best_decks_raw, list):
        for row in best_decks_raw:
            if not isinstance(row, dict):
                continue
            deck_type = row.get("deck_type")
            if not deck_type:
                continue
            games_val = (
                row.get("games")
                or row.get("games_played")
                or row.get("count")
                or 0
            )
            try:
                games_val = int(games_val)
            except (TypeError, ValueError):
                games_val = 0
            deck_counts[deck_type] = deck_counts.get(deck_type, 0) + games_val

    # ----- 2) Index best_decks by deck_type for extra stats -----
    best_decks: Dict[str, dict] = {}
    for d in best_decks_raw:
        if not isinstance(d, dict):
            continue
        deck_type = d.get("deck_type")
        if not deck_type:
            continue
        best_decks[deck_type] = d

    # ----- 3) Build final table -----
    table = []
    for deck_type, games in deck_counts.items():
        row = best_decks.get(deck_type) or {}

        wins = row.get("wins")
        losses = row.get("losses")
        win_rate = row.get("win_rate")

        table.append(
            {
                "deck_type": deck_type,
                "games": games,
                "wins": wins,
                "losses": losses,
                "win_rate": win_rate,
            }
        )

    return table


def build_user_matchup_summary(user_analytics):
    """
    Flatten easy/hard matchup lists into one table of (my_type vs opp_type).
    """
    table: List[dict] = []

    for row in user_analytics.get("easy_matchups", []) or []:
        table.append(
            {
                "attacker_type": row.get("my_deck_type", "Unknown"),
                "defender_type": row.get("opp_deck_type", "Unknown"),
                "games": row.get("games", 0),
                "wins": row.get("wins", 0),
                "losses": row.get("losses", 0),
                "win_rate": row.get("win_rate", 0.0),
                "matchup_category": "easy",
            }
        )

    for row in user_analytics.get("tough_matchups", []) or []:
        table.append(
            {
                "attacker_type": row.get("my_deck_type", "Unknown"),
                "defender_type": row.get("opp_deck_type", "Unknown"),
                "games": row.get("games", 0),
                "wins": row.get("wins", 0),
                "losses": row.get("losses", 0),
                "win_rate": row.get("win_rate", 0.0),
                "matchup_category": "tough",
            }
        )

    return table


def build_user_card_summary(user_analytics):
    """
    Merge best_cards + worst_cards into one per-card summary.
    """
    best = {c.get("card_name"): c for c in (user_analytics.get("best_cards") or []) if c.get("card_name")}
    worst = {c.get("card_name"): c for c in (user_analytics.get("worst_cards") or []) if c.get("card_name")}

    all_cards = set(best.keys()) | set(worst.keys())

    summary_games = (user_analytics.get("summary") or {}).get("games_played", 1) or 1

    table = []
    for card in all_cards:
        best_row = best.get(card) or {}
        worst_row = worst.get(card) or {}

        games = (best_row.get("games", 0) or 0) + (worst_row.get("games", 0) or 0)
        wins = best_row.get("wins", 0) or 0
        losses = worst_row.get("losses", 0) or 0

        win_rate = wins / games if games > 0 else 0.0
        usage_rate = games / summary_games if summary_games > 0 else 0.0

        table.append(
            {
                "card_name": card,
                "games": games,
                "wins": wins,
                "losses": losses,
                "win_rate": win_rate,
                "usage_rate": usage_rate,
            }
        )

    return table


def build_opponent_card_summary(user_analytics):
    """
    Mirror of build_user_card_summary, but from the opponent perspective:
    - tough_opp_cards: cards you struggle against
    - easy_opp_cards: cards you farm
    """
    tough = {c.get("card_name"): c for c in (user_analytics.get("tough_opp_cards") or []) if c.get("card_name")}
    easy = {c.get("card_name"): c for c in (user_analytics.get("easy_opp_cards") or []) if c.get("card_name")}

    all_cards = set(tough.keys()) | set(easy.keys())

    table = []
    for card in all_cards:
        tough_row = tough.get(card) or {}
        easy_row = easy.get(card) or {}

        games = (tough_row.get("games", 0) or 0) + (easy_row.get("games", 0) or 0)
        wins_against = easy_row.get("wins", 0) or 0
        losses_against = tough_row.get("losses", 0) or 0

        win_rate = wins_against / games if games > 0 else 0.0
        threat = losses_against / games if games > 0 else 0.0

        table.append(
            {
                "card_name": card,
                "games": games,
                "wins_against": wins_against,
                "losses_against": losses_against,
                "win_rate": win_rate,
                "threat": threat,
            }
        )

    return table


# ---------- Node: fetch_battlelog ----------


def fetch_battlelog_node(state: UserAnalyticsState) -> Dict[str, Any]:
    """
    Node:
      - reads player_tag from state
      - calls Clash Royale API
      - writes battles_raw into state
    """
    player_tag = state.get("player_tag")
    if not player_tag:
        raise ValueError("player_tag is required in state for fetch_battlelog_node")

    raw_battles = get_player_battlelog(player_tag)

    note = f"Fetched {len(raw_battles)} battles for {player_tag}"
    existing_notes = state.get("notes", []) or []
    existing_notes.append(note)

    return {
        "battles_raw": raw_battles,
        "notes": existing_notes,
    }


# ---------- Node: filter_and_normalize ----------


def filter_and_normalize_node(state: UserAnalyticsState) -> Dict[str, Any]:
    """
    Node:
      - reads battles_raw
      - filters to ranked/Trophy Road 1v1
      - normalizes battles
      - writes battles_filtered into state
    """
    battles_raw = state.get("battles_raw", []) or []
    if not battles_raw:
        raise ValueError("battles_raw is required in state for filter_and_normalize_node")

    battles_filtered = filter_and_normalize_ranked_1v1(battles_raw)

    note = f"Filtered to {len(battles_filtered)} ranked/Trophy Road 1v1 battles"
    existing_notes = state.get("notes", []) or []
    existing_notes.append(note)

    return {
        "battles_filtered": battles_filtered,
        "notes": existing_notes,
    }


# ---------- Node: compute_user_analytics ----------


def compute_user_analytics_node(state: UserAnalyticsState) -> Dict[str, Any]:
    """
    Node:
      - reads battles_filtered
      - computes analytics dict
      - writes user_analytics into state
    """
    battles_filtered = state.get("battles_filtered", []) or []
    if not battles_filtered:
        raise ValueError(
            "battles_filtered is required in state for compute_user_analytics_node"
        )

    analytics = compute_user_analytics(battles_filtered)

    note = (
        f"Computed analytics on {analytics.get('summary', {}).get('games_played', 0)} "
        "ranked/Trophy Road 1v1 battles"
    )
    existing_notes = state.get("notes", []) or []
    existing_notes.append(note)

    return {
        "user_analytics": analytics,
        "notes": existing_notes,
    }


# ---------- Node: generate_user_plots ----------


def generate_user_plots_node(state: UserAnalyticsState) -> Dict[str, Any]:
    """
    Node:
      - reads user_analytics
      - generates card-level plots
      - writes user_plots and updated user_analytics into state
    """
    analytics = state.get("user_analytics") or {}
    if not analytics:
        raise ValueError(
            "user_analytics is required in state for generate_user_plots_node"
        )

    analytics_with_plots = generate_card_plots(analytics, prefix="user")

    note = "Generated user card-level plots"
    existing_notes = state.get("notes", []) or []
    existing_notes.append(note)

    return {
        "user_analytics": analytics_with_plots,
        "user_plots": analytics_with_plots.get("plots", {}),
        "notes": existing_notes,
    }

## ---------- Node: llm tables ----------

def build_user_llm_tables_node(state: UserAnalyticsState) -> Dict[str, Any]:
    """
    Node:
      - reads user_analytics
      - builds compact LLM-ready tables
      - writes user_llm_tables into state

    Layout for user_llm_tables:
      - user_summary
      - user_deck_summary
      - user_matchup_summary
      - user_card_summary
      - opponent_card_summary
    """
    user_analytics = state.get("user_analytics") or {}
    if not user_analytics:
        raise ValueError(
            "user_analytics is required in state for build_user_llm_tables_node"
        )

    user_llm_tables = {
        "user_summary": build_user_summary_table(user_analytics.get("summary") or {}),
        "user_deck_summary": build_user_deck_summary(user_analytics),
        "user_matchup_summary": build_user_matchup_summary(user_analytics),
        "user_card_summary": build_user_card_summary(user_analytics),
        "opponent_card_summary": build_opponent_card_summary(user_analytics),
    }

    existing_notes = state.get("notes", []) or []
    existing_notes.append(
        "build_user_llm_tables: built "
        f"{len(user_llm_tables['user_deck_summary'])} deck rows, "
        f"{len(user_llm_tables['user_matchup_summary'])} matchup rows, "
        f"{len(user_llm_tables['user_card_summary'])} user card rows, "
        f"{len(user_llm_tables['opponent_card_summary'])} opponent card rows."
    )

    return {
        "user_llm_tables": user_llm_tables,
        "notes": existing_notes,
    }



# ---------- Graph Builder ----------


def build_user_analytics_graph():
    """
    Build the Phase 1 LangGraph workflow.

    Pipeline (D4):

        fetch_battlelog
            -> filter_and_normalize
            -> compute_user_analytics
            -> generate_user_plots
            -> END
    """
    graph = StateGraph(UserAnalyticsState)

    # Nodes
    graph.add_node("fetch_battlelog", fetch_battlelog_node)
    graph.add_node("filter_and_normalize", filter_and_normalize_node)
    graph.add_node("compute_user_analytics", compute_user_analytics_node)
    graph.add_node("build_user_llm_tables", build_user_llm_tables_node)  
    graph.add_node("generate_user_plots", generate_user_plots_node)

    # Entry / edges
    graph.set_entry_point("fetch_battlelog")
    graph.add_edge("fetch_battlelog", "filter_and_normalize")
    graph.add_edge("filter_and_normalize", "compute_user_analytics")
    graph.add_edge("compute_user_analytics", "build_user_llm_tables")  
    graph.add_edge("build_user_llm_tables", "generate_user_plots")       
    graph.add_edge("generate_user_plots", END)


    return graph.compile()
