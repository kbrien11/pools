"""Pure scoring rules for the March Madness fantasy game (no Django imports)."""


def multiplier_for_seed(seed: int) -> int:
    """Seeds 1-5 score 1x, 6-11 score 2x, 12-16 score 3x."""
    if 1 <= seed <= 5:
        return 1
    if 6 <= seed <= 11:
        return 2
    if 12 <= seed <= 16:
        return 3
    raise ValueError(f"Seed must be between 1 and 16, got {seed}")


def player_total(raw_points: int, seed: int) -> int:
    """A player's fantasy total: every point scored in the tournament times the seed multiplier."""
    return raw_points * multiplier_for_seed(seed)