from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from codex.github_status_rotator import *  # mirrors the codex script

if __name__ == "__main__":
    main()
