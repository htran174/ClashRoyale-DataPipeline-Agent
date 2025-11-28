# update_card_metadata.py
"""
One-time script that reads:
    src/data/cards_raw.json     (from Clash API)
    src/data/card_metadata.json (your current metadata skeleton)

And fills in:
    card_metadata[i]["elixir"] = elixirCost from cards_raw.json
"""

import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parent
DATA_DIR = ROOT / "src" / "data"

RAW_PATH = DATA_DIR / "cards_raw.json"
META_PATH = DATA_DIR / "card_metadata.json"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    raw_cards = load_json(RAW_PATH)
    meta_cards = load_json(META_PATH)

    # Build lookup: name → elixirCost
    elixir_lookup = {}
    for c in raw_cards:
        name = c["name"]
        cost = c.get("elixirCost")
        elixir_lookup[name] = cost

    updated = 0
    missing = []

    for c in meta_cards:
        name = c["name"]
        if name in elixir_lookup:
            c["elixir"] = elixir_lookup[name]
            updated += 1
        else:
            missing.append(name)

    save_json(META_PATH, meta_cards)

    print(f"Updated elixir for {updated} cards.")
    if missing:
        print("These cards were not found in cards_raw.json:")
        for m in missing:
            print("   -", m)


if __name__ == "__main__":
    main()