# getcards.py
"""
Fetch all Clash Royale cards using CR_API_KEY from .env and store the results in:

    src/data/cards_raw.json
    src/data/card_metadata.json
"""

import os
import json
import pathlib
import requests

from dotenv import load_dotenv


# -----------------------------------------
# Load environment variables
# -----------------------------------------

def load_env():
    """Load .env from the project root."""
    root = pathlib.Path(__file__).resolve().parent
    env_path = root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()  # fallback


# -----------------------------------------
# Main
# -----------------------------------------

def main():
    load_env()

    api_key = os.getenv("CR_API_KEY")
    if not api_key:
        raise RuntimeError("CR_API_KEY is missing in your .env file.")

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    print("➡️ Fetching cards from Clash Royale API...")
    resp = requests.get("https://api.clashroyale.com/v1/cards", headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    items = data.get("items", [])
    print(f"✅ Received {len(items)} cards.")

    # -----------------------------------------
    # Ensure src/data/ exists inside your project
    # -----------------------------------------
    project_root = pathlib.Path(__file__).resolve().parent     # location of getcards.py
    data_dir = project_root / "src" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    raw_path = data_dir / "cards_raw.json"
    meta_path = data_dir / "card_metadata.json"

    # -----------------------------------------
    # Save raw API response
    # -----------------------------------------
    with raw_path.open("w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    # -----------------------------------------
    # Build editable metadata template
    # -----------------------------------------
    meta_items = []
    for card in items:
        meta_items.append({
            "id": card.get("id"),
            "name": card.get("name"),
            "maxLevel": card.get("maxLevel"),
            "elixir": card.get("elixir"),  # Some may be null; you'll fill them manually

            # Flags you will edit later
            "is_big_tank": False,
            "is_bait_piece": False,
            "is_bridge_spam_piece": False,
        })

    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta_items, f, ensure_ascii=False, indent=2)

    print(f"💾 Saved raw cards to:        {raw_path}")
    print(f"💾 Saved card metadata to:    {meta_path}")
    print("📝 Now open card_metadata.json and fill in missing elixir costs + flags.")


if __name__ == "__main__":
    main()