"""Legacy bridge to ``codex.github_status_rotator``."""
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from codex.github_status_rotator import main

if __name__ == "__main__":
    main()
