import os
from collections import Counter
from dotenv import load_dotenv
import requests

load_dotenv()

CR_API_KEY = os.getenv("CR_API_KEY")
PLAYER_TAG = os.getenv("PLAYER_TAG")

assert CR_API_KEY, "CR_API_KEY missing"
assert PLAYER_TAG, "PLAYER_TAG missing"

def fetch_battlelog(player_tag: str):
    tag_no_hash = player_tag.replace("#", "")
    url = f"https://api.clashroyale.com/v1/players/%23{tag_no_hash}/battlelog"
    headers = {"Authorization": f"Bearer {CR_API_KEY}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def inspect_modes():
    battles = fetch_battlelog(PLAYER_TAG)

    mode_counter = Counter()
    extra_info = []

    for b in battles:
        gm = b.get("gameMode", {}) or {}
        mode_name = gm.get("name", "UNKNOWN")
        mode_id = gm.get("id", None)
        mode_counter[(mode_name, mode_id)] += 1

        extra_info.append({
            "mode_name": mode_name,
            "mode_id": mode_id,
            "type": b.get("type"),
            "isLadderTournament": b.get("isLadderTournament"),
            "leagueNumber": b.get("leagueNumber"),
        })

    print("=== Unique game modes in your recent battlelog ===")
    for (name, mid), count in mode_counter.most_common():
        print(f"- {name!r} (id={mid}) -> {count} games")

    print("\n=== Sample extra info for each unique mode ===")
    seen = set()
    for info in extra_info:
        key = (info["mode_name"], info["mode_id"])
        if key in seen:
            continue
        seen.add(key)
        print(
            f"\nMode: {info['mode_name']!r} (id={info['mode_id']})\n"
            f"  type = {info['type']}\n"
            f"  isLadderTournament = {info['isLadderTournament']}\n"
            f"  leagueNumber = {info['leagueNumber']}"
        )

if __name__ == "__main__":
    inspect_modes()
