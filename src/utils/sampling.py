import random
from typing import List, Dict, Any, Optional


def sample_players(
    players: List[Dict[str, Any]],
    sample_size: int = 50,
    seed: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Randomly sample players from a list (e.g., top 300 global players).

    Args:
        players: List of player dicts (expected length >= sample_size).
        sample_size: Number of players to sample (default: 50).
        seed: Optional random seed for reproducibility.

    Returns:
        List of sampled player dicts.
    """
    if seed is not None:
        random.seed(seed)

    if len(players) < sample_size:
        raise ValueError(
            f"Not enough players to sample: have {len(players)}, "
            f"need {sample_size}"
        )

    indices = random.sample(range(len(players)), sample_size)
    return [players[i] for i in indices]
