import os
from typing import Any, Dict, List

import matplotlib.pyplot as plt


PLOTS_DIR = "plots"


def _ensure_plots_dir() -> None:
    """Make sure the plots directory exists."""
    os.makedirs(PLOTS_DIR, exist_ok=True)


def _top_n_cards(cards: List[Dict[str, Any]], n: int = 10) -> List[Dict[str, Any]]:
    """Return top-n entries from a card stats list."""
    return cards[:n]


def plot_card_bar_chart(
    cards: List[Dict[str, Any]],
    title: str,
    filename: str,
    *,
    metric: str = "win_rate",
) -> str:
    """
    Generic bar chart for card stats.

    Args:
        cards: List of card dicts with at least keys: "card", metric.
        title: Plot title.
        filename: File name (inside plots/).
        metric: Metric key to plot on y-axis (default: "win_rate").

    Returns:
        Relative path to the saved PNG.
    """
    _ensure_plots_dir()

    if not cards:
        # Nothing to plot; return path but don't create a file.
        return os.path.join(PLOTS_DIR, f"{filename}.png")

    top_cards = _top_n_cards(cards, n=10)
    labels = [c["card"] for c in top_cards]
    values = [c.get(metric, 0.0) for c in top_cards]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(labels, values)
    ax.set_title(title)
    ax.set_ylabel(metric.replace("_", " ").title())
    ax.set_xticklabels(labels, rotation=45, ha="right")

    plt.tight_layout()

    path = os.path.join(PLOTS_DIR, f"{filename}.png")
    fig.savefig(path)
    plt.close(fig)

    return path


def generate_card_plots(analytics: Dict[str, Any], prefix: str = "user") -> Dict[str, Any]:
    """
    Generate card-level plots for the given analytics dict and
    update analytics["plots"] with file paths.

    Args:
        analytics: Analytics dict returned by compute_user_analytics().
        prefix: Prefix for filenames (e.g., "user" or "meta").

    Returns:
        The same analytics dict with analytics["plots"] updated.
    """
    plots = analytics.get("plots", {})

    best_cards = analytics.get("best_cards", [])
    worst_cards = analytics.get("worst_cards", [])
    tough_opp_cards = analytics.get("tough_opp_cards", [])
    easy_opp_cards = analytics.get("easy_opp_cards", [])

    plots["best_cards"] = plot_card_bar_chart(
        best_cards,
        title="Best Cards (Win Rate)",
        filename=f"{prefix}_best_cards",
    )

    plots["worst_cards"] = plot_card_bar_chart(
        worst_cards,
        title="Worst Cards (Win Rate)",
        filename=f"{prefix}_worst_cards",
    )

    plots["tough_opp_cards"] = plot_card_bar_chart(
        tough_opp_cards,
        title="Opponent Threat Cards (Their Win Rate)",
        filename=f"{prefix}_tough_opp_cards",
    )

    plots["easy_opp_cards"] = plot_card_bar_chart(
        easy_opp_cards,
        title="Opponent Easy Cards (Their Win Rate)",
        filename=f"{prefix}_easy_opp_cards",
    )

    analytics["plots"] = plots
    return analytics
