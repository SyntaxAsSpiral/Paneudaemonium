import subprocess
from pathlib import Path


def test_rotator_creates_readme(tmp_path):
    script_path = Path(__file__).resolve().parents[1] / "github_status_rotator.py"
    subprocess.run(["python", str(script_path)], cwd=tmp_path, check=True)
    assert (tmp_path / "README.md").is_file()
