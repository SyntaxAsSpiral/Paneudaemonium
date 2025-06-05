from __future__ import annotations

import random
from collections import deque
from pathlib import Path

# Import ritual cache helpers from the rotator
from .github_status_rotator import read_cache, write_cache


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
