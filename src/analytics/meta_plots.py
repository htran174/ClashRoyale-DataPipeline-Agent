# src/analytics/meta_plots.py

from __future__ import annotations

import os
from typing import Any, Dict, List

import matplotlib.pyplot as plt

PLOTS_DIR = "plots"


def _ensure_plots_dir() -> None:
    """Make sure the plots directory exists."""
    os.makedirs(PLOTS_DIR, exist_ok=True)


def _sorted_deck_types(
    my_counts: Dict[str, int],
    opp_counts: Dict[str, int],
    matchups: Dict[str, Any],
) -> List[str]:
    """
    Build a consistent deck-type order across all plots.

    Priority:
      1. Types that appear in matchups keys
      2. Types that appear in my_counts / opp_counts
    """
    names = set(my_counts.keys()) | set(opp_counts.keys()) | set(matchups.keys())
    return sorted(names)


def _plot_combined_deck_type_bar(
    deck_types: List[str],
    my_counts: Dict[str, int],
    opp_counts: Dict[str, int],
    filename: str,
    title: str = "Meta Deck Types (combined games)",
) -> str:
    """Bar chart of combined (my + opp) games per archetype."""
    _ensure_plots_dir()

    combined_counts = [
        int(my_counts.get(t, 0)) + int(opp_counts.get(t, 0)) for t in deck_types
    ]

    plt.figure(figsize=(8, 5))
    plt.bar(deck_types, combined_counts)
    plt.title(title)
    plt.xlabel("Deck Type")
    plt.ylabel("Number of Games")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    path = os.path.join(PLOTS_DIR, f"{filename}.png")
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def _plot_my_vs_opp_deck_type_bar(
    deck_types: List[str],
    my_counts: Dict[str, int],
    opp_counts: Dict[str, int],
    filename: str,
    title: str = "Meta Deck Types (my vs opp)",
) -> str:
    """Grouped bar chart: my deck-type games vs opponent deck-type games."""
    _ensure_plots_dir()

    x = list(range(len(deck_types)))
    width = 0.35
    my_vals = [int(my_counts.get(t, 0)) for t in deck_types]
    opp_vals = [int(opp_counts.get(t, 0)) for t in deck_types]

    left_x = [xi - width / 2 for xi in x]
    right_x = [xi + width / 2 for xi in x]

    plt.figure(figsize=(8, 5))
    plt.bar(left_x, my_vals, width=width, label="My decks")
    plt.bar(right_x, opp_vals, width=width, label="Opponent decks")

    plt.xticks(x, deck_types, rotation=30, ha="right")
    plt.ylabel("Number of Games")
    plt.title(title)
    plt.legend()
    plt.tight_layout()

    path = os.path.join(PLOTS_DIR, f"{filename}.png")
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def _plot_matchup_heatmap(
    deck_types: List[str],
    matchups: Dict[str, Any],
    filename: str,
    title: str = "Meta Deck-Type Matchup Win Rates",
) -> str:
    """
    Heatmap: rows = my deck type, cols = opp deck type, values = win rate (%).
    """
    if not matchups:
        return ""

    _ensure_plots_dir()

    n = len(deck_types)
    matrix = [[0.0 for _ in range(n)] for _ in range(n)]

    for i, my_type in enumerate(deck_types):
        row = matchups.get(my_type, {}) or {}
        for j, opp_type in enumerate(deck_types):
            cell = row.get(opp_type, {}) or {}
            win_rate = cell.get("win_rate")
            if win_rate is None:
                games = cell.get("games", 0)
                wins = cell.get("wins", 0)
                win_rate = (wins / games) if games > 0 else 0.0
            matrix[i][j] = float(win_rate) * 100.0

    plt.figure(figsize=(8, 6))
    im = plt.imshow(matrix, aspect="auto", origin="lower")
    cbar = plt.colorbar(im)
    cbar.set_label("Win rate (%)")

    plt.xticks(range(n), deck_types, rotation=45, ha="right")
    plt.yticks(range(n), deck_types)
    plt.xlabel("Opponent deck type")
    plt.ylabel("My deck type")
    plt.title(title)
    plt.tight_layout()

    path = os.path.join(PLOTS_DIR, f"{filename}.png")
    plt.savefig(path, dpi=150)
    plt.close()
    return path

def plot_meta_matchups_by_deck(
    matchup_summary: List[Dict[str, Any]],
    filename_prefix: str = "meta_matchups",
) -> Dict[str, str]:
    """
    For each deck type (attacker_type), create a bar chart of win rate vs
    every other deck type (defender_type).

    Input: matchup_summary rows like:
        {
          "attacker_type": str,
          "defender_type": str,
          "games": int,
          "win_rate": float,   # 0-1
          ...
        }

    Returns:
        {
          "<deck_type>": "plots/meta_matchups_<deck_type>.png",
          ...
        }
    """
    if not matchup_summary:
        return {}

    _ensure_plots_dir()

    # Group rows by attacker_type
    by_attacker: Dict[str, List[Dict[str, Any]]] = {}
    for row in matchup_summary:
        attacker = row.get("attacker_type")
        defender = row.get("defender_type")
        if not attacker or not defender:
            continue
        by_attacker.setdefault(attacker, []).append(row)

    plot_paths: Dict[str, str] = {}

    for attacker_type, rows in by_attacker.items():
        # Sort by win_rate descending so strongest matchups appear first
        rows = sorted(rows, key=lambda r: r.get("win_rate", 0.0), reverse=True)

        defenders = [r["defender_type"] for r in rows]
        win_rates_pct = [float(r.get("win_rate", 0.0)) * 100.0 for r in rows]
        games = [int(r.get("games", 0)) for r in rows]

        if not defenders:
            continue

        plt.figure(figsize=(8, 5))
        x = list(range(len(defenders)))

        plt.bar(x, win_rates_pct)
        plt.xticks(x, defenders, rotation=30, ha="right")
        plt.ylabel("Win rate (%)")
        plt.xlabel("Opponent deck type")
        plt.title(f"{attacker_type} vs other deck types (meta win rates)")

        # Optional: annotate bars with sample size (games)
        for xi, (rate, g) in enumerate(zip(win_rates_pct, games)):
            plt.text(
                xi,
                rate + 1.0,
                f"{g}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

        plt.tight_layout()

        safe_name = attacker_type.lower().replace(" ", "_")
        filename = f"{filename_prefix}_{safe_name}.png"
        path = os.path.join(PLOTS_DIR, filename)
        plt.savefig(path, dpi=150)
        plt.close()

        plot_paths[attacker_type] = path

    return plot_paths


def attach_meta_plots_to_analytics(
    analytics: Dict[str, Any],
    prefix: str = "meta",
) -> Dict[str, Any]:
    """
    Add useful meta plots to the analytics dict.

    Creates:
      - deck_types_combined_bar
      - deck_types_my_vs_opp_bar
      - deck_type_matchups_heatmap
    """
    my_counts = analytics.get("deck_type_counts_my", {}) or {}
    opp_counts = analytics.get("deck_type_counts_opp", {}) or {}
    matchups = analytics.get("deck_type_matchups", {}) or {}

    deck_types = _sorted_deck_types(my_counts, opp_counts, matchups)
    if not deck_types:
        return analytics

    plots = dict(analytics.get("plots", {}))

    plots["deck_types_combined_bar"] = _plot_combined_deck_type_bar(
        deck_types,
        my_counts,
        opp_counts,
        filename=f"{prefix}_deck_types_combined",
        title="Meta Deck Types (combined my+opp games)",
    )

    plots["deck_types_my_vs_opp_bar"] = _plot_my_vs_opp_deck_type_bar(
        deck_types,
        my_counts,
        opp_counts,
        filename=f"{prefix}_deck_types_my_vs_opp",
        title="Meta Deck Types (my vs opponent games)",
    )

    heatmap_path = _plot_matchup_heatmap(
        deck_types,
        matchups,
        filename=f"{prefix}_deck_type_matchups_heatmap",
        title="Meta Deck-Type Matchup Win Rates",
    )
    if heatmap_path:
        plots["deck_type_matchups_heatmap"] = heatmap_path

    analytics["plots"] = plots
    return analytics
