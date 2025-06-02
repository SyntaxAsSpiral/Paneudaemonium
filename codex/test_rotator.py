import os
import subprocess
from pathlib import Path


def test_rotator_creates_readme(tmp_path):
    script_path = Path(__file__).resolve().parents[1] / "glyphs" / "github_status_rotator.py"
    statuses = tmp_path / "statuses.txt"
    statuses.write_text("alpha\nbeta\n", encoding="utf-8")
    quotes = tmp_path / "antenna_quotes.txt"
    quotes.write_text("echo\nnoecho\n", encoding="utf-8")
    glyphs = tmp_path / "glyphbraids.txt"
    glyphs.write_text("gamma\ndelta\n", encoding="utf-8")
    echoes = tmp_path / "echo_fragments.txt"
    echoes.write_text("sigil\nmirage\n", encoding="utf-8")
    env = os.environ.copy()
    env["STATUS_FILE"] = str(statuses)
    env["QUOTE_FILE"] = str(quotes)
    env["GLYPH_FILE"] = str(glyphs)
    env["ECHO_FILE"] = str(echoes)
    subprocess.run(["python", str(script_path)], cwd=tmp_path, check=True, env=env)
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert any(s in readme for s in ["alpha", "beta"])
    assert any(q in readme for q in ["echo", "noecho"])
    assert any(g in readme for g in ["gamma", "delta"])
    assert any(e in readme for e in ["sigil", "mirage"])