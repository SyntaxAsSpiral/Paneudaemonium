from __future__ import annotations

import random
from collections import deque
from pathlib import Path


def read_cache(path: Path) -> list[str]:
    """Exhale memory traces from a cache file."""
    try:
        with path.open(encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def write_cache(path: Path, lines: list[str]) -> None:
    """Inscribe the latest traces back into the cache."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for ln in lines:
            f.write(ln + "\n")


def summon_novonox(options: list[str], cache_path: Path, limit: int = 5, echo_log: Path | None = None) -> str:
    """Breathform-aware selector.

    Prefers unseen options. Old echoes fade back by chance.
    Skipped items may be inscribed in ``echo_log`` for divinatory review.
    """

    recent = deque(read_cache(cache_path), maxlen=limit)
    unseen = [o for o in options if o not in recent]

    if not unseen:
        if echo_log:
            echo_log.parent.mkdir(parents=True, exist_ok=True)
            with echo_log.open("a", encoding="utf-8") as f:
                f.write("# Nōvonox Cycle Reset\n")
                for item in recent:
                    f.write(f"\U0001FA9E Previously Echoed: {item}\n")
        recent.clear()
        unseen = options

    decay_weighted = list(unseen)
    decay_weighted.extend([o for o in recent if random.random() < 0.15])

    choice = random.choice(decay_weighted)
    recent.append(choice)
    write_cache(cache_path, list(recent))
    return choice
