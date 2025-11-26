import os

from dotenv import load_dotenv

from src.api.battles import get_player_battlelog
from src.analytics.battle_filters import filter_and_normalize_ranked_1v1
from src.analytics.user_analytics import compute_user_analytics
from src.analytics.plots import generate_card_plots

load_dotenv()

PLAYER_TAG = os.getenv("PLAYER_TAG")  # temporary for testing


def main():
    if not PLAYER_TAG:
        raise RuntimeError("PLAYER_TAG is not set in .env for testing.")

    print(f"Fetching battlelog for {PLAYER_TAG}...")
    raw_battles = get_player_battlelog(PLAYER_TAG)
    print(f"Total battles returned: {len(raw_battles)}")

    norm_battles = filter_and_normalize_ranked_1v1(raw_battles)
    print(f"Ranked/Trophy Road 1v1 battles after filter: {len(norm_battles)}")

    analytics = compute_user_analytics(norm_battles)
    analytics = generate_card_plots(analytics, prefix="user_test")

    print("\n=== Summary ===")
    print(analytics["summary"])

    print("\nPlot files:")
    for name, path in analytics["plots"].items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()
