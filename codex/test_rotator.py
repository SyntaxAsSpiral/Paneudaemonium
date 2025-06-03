import os
import subprocess
import sys
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
    modes = tmp_path / "modes.txt"
    modes.write_text('"m1"\n"m2"\n', encoding="utf-8")
    ends = tmp_path / "end-quotes.txt"
    ends.write_text("fin\nterm\n", encoding="utf-8")
    subjects = tmp_path / "subject-ids.txt"
    subjects.write_text("id1\nid2\n", encoding="utf-8")
    codex_dir = tmp_path / "codex"
    codex_dir.mkdir(exist_ok=True)
    env = os.environ.copy()
    env["STATUS_FILE"] = str(statuses)
    env["QUOTE_FILE"] = str(quotes)
    env["GLYPH_FILE"] = str(glyphs)
    env["ECHO_FILE"] = str(echoes)
    env["MODE_FILE"] = str(modes)
    env["END_QUOTE_FILE"] = str(ends)
    env["SUBJECT_FILE"] = str(subjects)
    env["OUTPUT_DIR"] = str(tmp_path)
    env["DOCS_DIR"] = str(tmp_path)
    subprocess.run([sys.executable, str(script_path)], cwd=tmp_path, check=True, env=env)
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "ChronoSig" in readme
    assert "ChronoSig" in html
    assert any(s in readme for s in ["alpha", "beta"])
    assert any(q in readme for q in ["echo", "noecho"])
    assert any(g in readme for g in ["gamma", "delta"])
    assert any(e in readme for e in ["sigil", "mirage"])
    assert any(sub in readme for sub in ["id1", "id2"])
    assert any(s in html for s in ["alpha", "beta"])
    assert any(q in html for q in ["echo", "noecho"])
    assert any(g in html for g in ["gamma", "delta"])
    assert any(e in html for e in ["sigil", "mirage"])
    assert any(sub in html for sub in ["id1", "id2"])

def test_rotator_handles_missing_echo(tmp_path):
    script_path = Path(__file__).resolve().parents[1] / "glyphs" / "github_status_rotator.py"
    statuses = tmp_path / "statuses.txt"
    statuses.write_text("alpha\nbeta\n", encoding="utf-8")
    quotes = tmp_path / "antenna_quotes.txt"
    quotes.write_text("echo\nnoecho\n", encoding="utf-8")
    glyphs = tmp_path / "glyphbraids.txt"
    glyphs.write_text("gamma\ndelta\n", encoding="utf-8")
    modes = tmp_path / "modes.txt"
    modes.write_text('"a"\n"b"\n', encoding="utf-8")
    ends = tmp_path / "end-quotes.txt"
    ends.write_text("x\ny\n", encoding="utf-8")
    codex_dir = tmp_path / "codex"
    codex_dir.mkdir(exist_ok=True)
    env = os.environ.copy()
    env["STATUS_FILE"] = str(statuses)
    env["QUOTE_FILE"] = str(quotes)
    env["GLYPH_FILE"] = str(glyphs)
    env["ECHO_FILE"] = str(tmp_path / "missing.txt")
    env["MODE_FILE"] = str(modes)
    env["END_QUOTE_FILE"] = str(ends)
    env["OUTPUT_DIR"] = str(tmp_path)
    env["DOCS_DIR"] = str(tmp_path)
    subprocess.run([sys.executable, str(script_path)], cwd=tmp_path, check=True, env=env)
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "ChronoSig" in readme
    assert "ChronoSig" in html
    assert "⚠️ echo file missing" in readme
    assert "⚠️ echo file missing" in html


def test_rotator_handles_missing_status(tmp_path):
    script_path = Path(__file__).resolve().parents[1] / "glyphs" / "github_status_rotator.py"
    quotes = tmp_path / "antenna_quotes.txt"
    quotes.write_text("echo\nnoecho\n", encoding="utf-8")
    glyphs = tmp_path / "glyphbraids.txt"
    glyphs.write_text("gamma\ndelta\n", encoding="utf-8")
    echoes = tmp_path / "echo_fragments.txt"
    echoes.write_text("sigil\nmirage\n", encoding="utf-8")
    modes = tmp_path / "modes.txt"
    modes.write_text('"a"\n"b"\n', encoding="utf-8")
    ends = tmp_path / "end-quotes.txt"
    ends.write_text("x\ny\n", encoding="utf-8")
    subjects = tmp_path / "subject-ids.txt"
    subjects.write_text("id1\nid2\n", encoding="utf-8")
    codex_dir = tmp_path / "codex"
    codex_dir.mkdir(exist_ok=True)
    env = os.environ.copy()
    env["STATUS_FILE"] = str(tmp_path / "missing.txt")
    env["QUOTE_FILE"] = str(quotes)
    env["GLYPH_FILE"] = str(glyphs)
    env["ECHO_FILE"] = str(echoes)
    env["MODE_FILE"] = str(modes)
    env["END_QUOTE_FILE"] = str(ends)
    env["SUBJECT_FILE"] = str(subjects)
    env["OUTPUT_DIR"] = str(tmp_path)
    env["DOCS_DIR"] = str(tmp_path)
    subprocess.run([sys.executable, str(script_path)], cwd=tmp_path, check=True, env=env)
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "ChronoSig" in readme
    assert "ChronoSig" in html
    assert "⚠️ status file missing" in readme
    assert "⚠️ status file missing" in html


def test_rotator_handles_missing_quote(tmp_path):
    script_path = Path(__file__).resolve().parents[1] / "glyphs" / "github_status_rotator.py"
    statuses = tmp_path / "statuses.txt"
    statuses.write_text("alpha\nbeta\n", encoding="utf-8")
    glyphs = tmp_path / "glyphbraids.txt"
    glyphs.write_text("gamma\ndelta\n", encoding="utf-8")
    echoes = tmp_path / "echo_fragments.txt"
    echoes.write_text("sigil\nmirage\n", encoding="utf-8")
    modes = tmp_path / "modes.txt"
    modes.write_text('"a"\n"b"\n', encoding="utf-8")
    ends = tmp_path / "end-quotes.txt"
    ends.write_text("x\ny\n", encoding="utf-8")
    subjects = tmp_path / "subject-ids.txt"
    subjects.write_text("id1\nid2\n", encoding="utf-8")
    codex_dir = tmp_path / "codex"
    codex_dir.mkdir(exist_ok=True)
    env = os.environ.copy()
    env["STATUS_FILE"] = str(statuses)
    env["QUOTE_FILE"] = str(tmp_path / "missing.txt")
    env["GLYPH_FILE"] = str(glyphs)
    env["ECHO_FILE"] = str(echoes)
    env["MODE_FILE"] = str(modes)
    env["END_QUOTE_FILE"] = str(ends)
    env["SUBJECT_FILE"] = str(subjects)
    env["OUTPUT_DIR"] = str(tmp_path)
    env["DOCS_DIR"] = str(tmp_path)
    subprocess.run([sys.executable, str(script_path)], cwd=tmp_path, check=True, env=env)
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "ChronoSig" in readme
    assert "ChronoSig" in html
    assert "⚠️ quote file missing" in readme
    assert "⚠️ quote file missing" in html


def test_rotator_handles_missing_glyph(tmp_path):
    script_path = Path(__file__).resolve().parents[1] / "glyphs" / "github_status_rotator.py"
    statuses = tmp_path / "statuses.txt"
    statuses.write_text("alpha\nbeta\n", encoding="utf-8")
    quotes = tmp_path / "antenna_quotes.txt"
    quotes.write_text("echo\nnoecho\n", encoding="utf-8")
    echoes = tmp_path / "echo_fragments.txt"
    echoes.write_text("sigil\nmirage\n", encoding="utf-8")
    subjects = tmp_path / "subject-ids.txt"
    subjects.write_text("id1\nid2\n", encoding="utf-8")
    modes = tmp_path / "modes.txt"
    modes.write_text('"a"\n"b"\n', encoding="utf-8")
    ends = tmp_path / "end-quotes.txt"
    ends.write_text("x\ny\n", encoding="utf-8")
    codex_dir = tmp_path / "codex"
    codex_dir.mkdir(exist_ok=True)
    env = os.environ.copy()
    env["STATUS_FILE"] = str(statuses)
    env["QUOTE_FILE"] = str(quotes)
    env["GLYPH_FILE"] = str(tmp_path / "missing.txt")
    env["ECHO_FILE"] = str(echoes)
    env["MODE_FILE"] = str(modes)
    env["END_QUOTE_FILE"] = str(ends)
    env["SUBJECT_FILE"] = str(subjects)
    env["OUTPUT_DIR"] = str(tmp_path)
    env["DOCS_DIR"] = str(tmp_path)
    subprocess.run([sys.executable, str(script_path)], cwd=tmp_path, check=True, env=env)
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "ChronoSig" in readme
    assert "ChronoSig" in html
    assert "⚠️ glyph file missing" in readme
    assert "⚠️ glyph file missing" in html


def test_rotator_handles_missing_subject(tmp_path):
    script_path = Path(__file__).resolve().parents[1] / "glyphs" / "github_status_rotator.py"
    statuses = tmp_path / "statuses.txt"
    statuses.write_text("alpha\nbeta\n", encoding="utf-8")
    quotes = tmp_path / "antenna_quotes.txt"
    quotes.write_text("echo\nnoecho\n", encoding="utf-8")
    glyphs = tmp_path / "glyphbraids.txt"
    glyphs.write_text("gamma\ndelta\n", encoding="utf-8")
    echoes = tmp_path / "echo_fragments.txt"
    echoes.write_text("sigil\nmirage\n", encoding="utf-8")
    codex_dir = tmp_path / "codex"
    codex_dir.mkdir(exist_ok=True)
    modes = tmp_path / "modes.txt"
    modes.write_text('"a"\n"b"\n', encoding="utf-8")
    ends = tmp_path / "end-quotes.txt"
    ends.write_text("x\ny\n", encoding="utf-8")
    env = os.environ.copy()
    env["STATUS_FILE"] = str(statuses)
    env["QUOTE_FILE"] = str(quotes)
    env["GLYPH_FILE"] = str(glyphs)
    env["ECHO_FILE"] = str(echoes)
    env["MODE_FILE"] = str(modes)
    env["END_QUOTE_FILE"] = str(ends)
    env["SUBJECT_FILE"] = str(tmp_path / "missing.txt")
    env["OUTPUT_DIR"] = str(tmp_path)
    env["DOCS_DIR"] = str(tmp_path)
    subprocess.run([sys.executable, str(script_path)], cwd=tmp_path, check=True, env=env)
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "ChronoSig" in readme
    assert "ChronoSig" in html
    assert "⚠️ subject file missing" in readme
    assert "⚠️ subject file missing" in html


def test_rotator_handles_missing_mode(tmp_path):
    script_path = Path(__file__).resolve().parents[1] / "glyphs" / "github_status_rotator.py"
    statuses = tmp_path / "statuses.txt"
    statuses.write_text("alpha\nbeta\n", encoding="utf-8")
    quotes = tmp_path / "antenna_quotes.txt"
    quotes.write_text("echo\nnoecho\n", encoding="utf-8")
    glyphs = tmp_path / "glyphbraids.txt"
    glyphs.write_text("gamma\ndelta\n", encoding="utf-8")
    echoes = tmp_path / "echo_fragments.txt"
    echoes.write_text("sigil\nmirage\n", encoding="utf-8")
    ends = tmp_path / "end-quotes.txt"
    ends.write_text("x\ny\n", encoding="utf-8")
    subjects = tmp_path / "subject-ids.txt"
    subjects.write_text("id1\nid2\n", encoding="utf-8")
    codex_dir = tmp_path / "codex"
    codex_dir.mkdir(exist_ok=True)
    env = os.environ.copy()
    env["STATUS_FILE"] = str(statuses)
    env["QUOTE_FILE"] = str(quotes)
    env["GLYPH_FILE"] = str(glyphs)
    env["ECHO_FILE"] = str(echoes)
    env["MODE_FILE"] = str(tmp_path / "missing.txt")
    env["END_QUOTE_FILE"] = str(ends)
    env["SUBJECT_FILE"] = str(subjects)
    env["OUTPUT_DIR"] = str(tmp_path)
    env["DOCS_DIR"] = str(tmp_path)
    subprocess.run([sys.executable, str(script_path)], cwd=tmp_path, check=True, env=env)
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "⚠️ mode file missing" in readme
    assert "⚠️ mode file missing" in html


def test_rotator_handles_missing_end_quote(tmp_path):
    script_path = Path(__file__).resolve().parents[1] / "glyphs" / "github_status_rotator.py"
    statuses = tmp_path / "statuses.txt"
    statuses.write_text("alpha\nbeta\n", encoding="utf-8")
    quotes = tmp_path / "antenna_quotes.txt"
    quotes.write_text("echo\nnoecho\n", encoding="utf-8")
    glyphs = tmp_path / "glyphbraids.txt"
    glyphs.write_text("gamma\ndelta\n", encoding="utf-8")
    echoes = tmp_path / "echo_fragments.txt"
    echoes.write_text("sigil\nmirage\n", encoding="utf-8")
    modes = tmp_path / "modes.txt"
    modes.write_text('"a"\n"b"\n', encoding="utf-8")
    subjects = tmp_path / "subject-ids.txt"
    subjects.write_text("id1\nid2\n", encoding="utf-8")
    codex_dir = tmp_path / "codex"
    codex_dir.mkdir(exist_ok=True)
    env = os.environ.copy()
    env["STATUS_FILE"] = str(statuses)
    env["QUOTE_FILE"] = str(quotes)
    env["GLYPH_FILE"] = str(glyphs)
    env["ECHO_FILE"] = str(echoes)
    env["MODE_FILE"] = str(modes)
    env["END_QUOTE_FILE"] = str(tmp_path / "missing.txt")
    env["SUBJECT_FILE"] = str(subjects)
    env["OUTPUT_DIR"] = str(tmp_path)
    env["DOCS_DIR"] = str(tmp_path)
    subprocess.run([sys.executable, str(script_path)], cwd=tmp_path, check=True, env=env)
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "⚠️ end quote file missing" in readme
    assert "⚠️ end quote file missing" in html
