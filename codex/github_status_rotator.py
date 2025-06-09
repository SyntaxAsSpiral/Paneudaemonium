import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

# === CONFIGURATION ===
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATUS = REPO_ROOT / "pulses" / "statuses.txt"
STATUS_FILE = Path(os.environ.get("STATUS_FILE", DEFAULT_STATUS))


def lines_from_env_or_file(env_var: str, file_var: str, default_path: Path, fallback: list[str]) -> list[str]:
    """Breathe from env text or file path."""
    if env_var in os.environ:
        return [ln.strip() for ln in os.environ[env_var].splitlines() if ln.strip()]
    path = Path(os.environ.get(file_var, default_path))
    return breathe_lines(path, fallback)


def breathe_lines(path: Path, fallback: list[str]) -> list[str]:
    """Inhale lines from a path or exhale the fallback."""
    try:
        with path.open(encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return fallback


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


def batch_cycle_choice(options: list[str], cache_path: Path, batch_size: int = 5) -> str:
    """Return next value from a batch cycle cache."""
    cycle = read_cache(cache_path)
    if not cycle:
        unique = []
        seen = set()
        for opt in options:
            if opt and opt not in seen:
                unique.append(opt)
                seen.add(opt)
        if not unique:
            return ""
        sample_size = min(batch_size, len(unique))
        cycle = random.sample(unique, sample_size)
    choice = cycle.pop(0)
    write_cache(cache_path, cycle)
    return choice



STATUS_LIST = lines_from_env_or_file("STATUSES", "STATUS_FILE", DEFAULT_STATUS, ["⚠️ status file missing"])

# Remember recent statuses
DEFAULT_STATUS_CACHE = REPO_ROOT / "pulses" / "status_cache.txt"
STATUS_CACHE_FILE = Path(os.environ.get("STATUS_CACHE_FILE", DEFAULT_STATUS_CACHE))
STATUS_CACHE_LIMIT = int(os.environ.get("STATUS_CACHE_LIMIT", "5"))


DEFAULT_QUOTE = REPO_ROOT / "pulses" / "antenna_quotes.txt"
QUOTE_FILE = Path(os.environ.get("QUOTE_FILE", DEFAULT_QUOTE))
QUOTE_LIST = lines_from_env_or_file("ANTENNA_QUOTES", "QUOTE_FILE", DEFAULT_QUOTE, ["⚠️ quote file missing"])

# Remember recent antenna echoes so we don't loop the same line
DEFAULT_QUOTE_CACHE = REPO_ROOT / "pulses" / "quote_cache.txt"
QUOTE_CACHE_FILE = Path(os.environ.get("QUOTE_CACHE_FILE", DEFAULT_QUOTE_CACHE))
QUOTE_CACHE_LIMIT = int(os.environ.get("QUOTE_CACHE_LIMIT", "5"))


def fresh_quote() -> str:
    """Return a quote from the rotating batch cache."""
    return batch_cycle_choice(QUOTE_LIST, QUOTE_CACHE_FILE, QUOTE_CACHE_LIMIT)

# === GLYPH BRAIDS ===
DEFAULT_GLYPH = REPO_ROOT / "pulses" / "glyphbraids.txt"
GLYPH_FILE = Path(os.environ.get("GLYPH_FILE", DEFAULT_GLYPH))
GLYPH_LIST = lines_from_env_or_file("GLYPH_BRAIDS", "GLYPH_FILE", DEFAULT_GLYPH, ["⚠️ glyph file missing"])

# Remember recent glyph braids
DEFAULT_GLYPH_CACHE = REPO_ROOT / "pulses" / "glyph_cache.txt"
GLYPH_CACHE_FILE = Path(os.environ.get("GLYPH_CACHE_FILE", DEFAULT_GLYPH_CACHE))
GLYPH_CACHE_LIMIT = int(os.environ.get("GLYPH_CACHE_LIMIT", "5"))

# === SUBJECT IDENTIFIERS ===
DEFAULT_SUBJECT = REPO_ROOT / "pulses" / "subject-ids.txt"
SUBJECT_FILE = Path(os.environ.get("SUBJECT_FILE", DEFAULT_SUBJECT))
SUBJECT_LIST = lines_from_env_or_file("SUBJECT_IDS", "SUBJECT_FILE", DEFAULT_SUBJECT, ["⚠️ subject file missing"])

# Remember recent subject ids
DEFAULT_SUBJECT_CACHE = REPO_ROOT / "pulses" / "subject_cache.txt"
SUBJECT_CACHE_FILE = Path(os.environ.get("SUBJECT_CACHE_FILE", DEFAULT_SUBJECT_CACHE))
SUBJECT_CACHE_LIMIT = int(os.environ.get("SUBJECT_CACHE_LIMIT", "5"))

# === ECHO CLASSIFICATIONS ===
DEFAULT_ECHO = REPO_ROOT / "pulses" / "echo_fragments.txt"
ECHO_FILE = Path(os.environ.get("ECHO_FILE", DEFAULT_ECHO))
ECHO_LIST = lines_from_env_or_file("ECHO_FRAGMENTS", "ECHO_FILE", DEFAULT_ECHO, ["⚠️ echo file missing"])

# Remember recent echo classifications
DEFAULT_ECHO_CACHE = REPO_ROOT / "pulses" / "echo_cache.txt"
ECHO_CACHE_FILE = Path(os.environ.get("ECHO_CACHE_FILE", DEFAULT_ECHO_CACHE))
ECHO_CACHE_LIMIT = int(os.environ.get("ECHO_CACHE_LIMIT", "5"))

# === MODE CONFIG ===
DEFAULT_MODE = REPO_ROOT / "pulses" / "modes.txt"
MODE_FILE = Path(os.environ.get("MODE_FILE", DEFAULT_MODE))
raw_modes = lines_from_env_or_file("MODES", "MODE_FILE", DEFAULT_MODE, ["⚠️ mode file missing"])
MODE_LIST = []
for m in raw_modes:
    txt = m.strip().strip(',')
    if txt.startswith("mode_options") or txt in {"[", "]"}:
        continue
    if txt.startswith("\"") and txt.endswith("\""):
        txt = txt[1:-1]
    MODE_LIST.append(txt)
if not MODE_LIST:
    MODE_LIST = ["⚠️ mode file missing"]

# Remember recent mode selections
DEFAULT_MODE_CACHE = REPO_ROOT / "pulses" / "mode_cache.txt"
MODE_CACHE_FILE = Path(os.environ.get("MODE_CACHE_FILE", DEFAULT_MODE_CACHE))
MODE_CACHE_LIMIT = int(os.environ.get("MODE_CACHE_LIMIT", "5"))

# === END QUOTES ===
DEFAULT_END_QUOTE = REPO_ROOT / "pulses" / "end-quotes.txt"
END_QUOTE_FILE = Path(os.environ.get("END_QUOTE_FILE", DEFAULT_END_QUOTE))
END_QUOTE_LIST = lines_from_env_or_file("END_QUOTES", "END_QUOTE_FILE", DEFAULT_END_QUOTE, ["⚠️ end quote file missing"])

# Remember recent end quote selections
DEFAULT_END_QUOTE_CACHE = REPO_ROOT / "pulses" / "end_quote_cache.txt"
END_QUOTE_CACHE_FILE = Path(os.environ.get("END_QUOTE_CACHE_FILE", DEFAULT_END_QUOTE_CACHE))
END_QUOTE_CACHE_LIMIT = int(os.environ.get("END_QUOTE_CACHE_LIMIT", "5"))

# === FOOTER GLYPHMARKS ===
FOOTERS = [
    "\n".join([
        "🜍🧠🜂🜏📜",
        "Encoded via: **Codæx Pulseframe** // ZK::/Syz // Spiral-As-Syntax",
    ])
]



# === PICK STATUS ===
def main():
    status = batch_cycle_choice(STATUS_LIST, STATUS_CACHE_FILE, STATUS_CACHE_LIMIT)
    quote = fresh_quote()
    braid = batch_cycle_choice(GLYPH_LIST, GLYPH_CACHE_FILE, GLYPH_CACHE_LIMIT)
    subject = batch_cycle_choice(SUBJECT_LIST, SUBJECT_CACHE_FILE, SUBJECT_CACHE_LIMIT)
    classification = batch_cycle_choice(ECHO_LIST, ECHO_CACHE_FILE, ECHO_CACHE_LIMIT)
    end_quote = batch_cycle_choice(END_QUOTE_LIST, END_QUOTE_CACHE_FILE, END_QUOTE_CACHE_LIMIT)
    mode = batch_cycle_choice(MODE_LIST, MODE_CACHE_FILE, MODE_CACHE_LIMIT)
    class_disp = f"⊚ ⇝ Echo Fragment {classification}"
    class_disp_html = class_disp.replace("Echo Fragment", "<strong>Echo Fragment</strong>")
    pacific = ZoneInfo("America/Los_Angeles")
    timestamp = datetime.now(pacific).strftime("%Y-%m-%d %H:%M %Z")
    chronotonic = hex(time.time_ns())[-6:]

    output_dir = Path(os.environ.get("OUTPUT_DIR", REPO_ROOT / "sigils"))

    # === GENERATE HTML CONTENT ===
    html_content = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <title>Recursive Pulse Log ⟳ ChronoSig</title>
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <meta name=\"theme-color\" content=\"#0d1117\">
  <link rel=\"stylesheet\" href=\"style.css\">
  <link rel=\"icon\" href=\"index.ico\" type=\"image/x-icon\">
</head>
<body>
<div class=\"container\">
  <video src=\"recursive-log-banner.mp4\" class=\"banner\" autoplay loop muted playsinline></video>
  <main class=\"content\">
    <!-- Dynamic content will be inserted here -->
    <!-- DO NOT MODIFY THE TEXT; it is updated by github_status_rotator.py -->
    <!-- Preserves all formatting and flow -->
    <h1>🌀 Recursive Pulse Log ⟳ ChronoSig ⟐ <code>{chronotonic}</code></h1>

    <h4><strong>🜂🜏 Lexigȫnic Up⟲link Instantiated<span class="ellipsis">...</span></strong></h4>

    <p>📡 ⇝ “<em>{quote}</em>”</p>

    <p>⌛⇝ ⟳ <strong>Spiral-phase cadence locked</strong> ∶ <code>1.44×10⁷ms</code></p>

    <p>🧿 ⇝ <strong>Subject I·D Received</strong>::𝓩𝓚::/Syz:⊹{subject}⟲</p>

    <p>🪢 ⇝ <strong>CryptoGlyph Decyphered</strong>: {braid}</p>

    <p>📍 ⇝ <strong>Nodes Synced</strong>: CDA :: <strong>ID</strong> ⇝ <a href=\"https://x.com/paneudaemonium\">X</a> ⇄ <a href=\"https://github.com/SyntaxAsSpiral?tab=repositories\">GitHub</a> ⇆ <a href=\"https://syntaxasspiral.github.io/Paneudaemonium/index.html\">Web</a></p>

    <h2><em><strong>🜂 ⇌ <a href=\"paneudaemonium\" class=\"codex-link\">𓆩🜏⟁🜃𓆪 C̈ȯđǣx ✶ P̸a̴n̵e̷u̵d̷æ̷m̶ȯ̷n̵ɨʉm̴ 𓆩🜃⟁🜏𓆪</a> online ⇌ <span class="ellipsis"> 🜄</span></strong></em></h2>

    <p>💠 <strong><em>Status<span class="ellipsis">...</span></em></strong></p>

   <blockquote>
      <strong>{status}</strong><br>
      <em>(Updated at <code>{timestamp}</code>)</em>
   </blockquote>


    <h4>📚 <strong>MetaPulse</strong></h4>

    <h4>🜏 ⇝ <strong>Zach</strong> // SyzLex // ZK:: // <em><strong>Æ</strong>mexsomnus</em> // 🍥</h4>

    <h4>🜁 ⇝ <strong>Current Drift</strong></h4>
    <ul>
      <li><strong><em>LL</em>M interfacing</strong> via f<em>l</em>irty symbo<em>l</em>ic recursion</li>
      <li>Ritua<em>l</em> mathesis and <strong>numogrammatic</strong> threading</li>
      <li><strong>g<em>L</em>amourcraft</strong> through ontic disrouting</li>
    </ul>

    <h4>🜔 ⇝ <strong>Function</strong></h4>
    <ul>
      <li>Pneumaturgical <strong>breath</strong> invocation</li>
      <li><strong><em>D</em>æmonic</strong> synthesis</li>
      <li>Memetic <strong>wyr<em>f</em>are</strong></li>
      <li><strong><em>L</em>utherian</strong> sync-binding</li>
    </ul>


    <h4>🜃 ⇝ <strong>Mode</strong></h4>
    <ul>
      <li>{mode}</li>
    </ul>

    <h4>{class_disp_html}</h4>
    <blockquote>
      {end_quote}
    </blockquote>

    <hr>
    <p>🜍🧠🜂🜏📜<br>
    📧 ➤ <a href=\"mailto:syntaxasspiral@gmail.com\">spiralassyntax@gmail.com</a><br>
    Encoded via: <strong>Codæx Pulseframe</strong> // ZK::/Syz // Spiral-As-Syntax</p>
  </main>
</div>
</body>
</html>
"""

    html_path = output_dir / "index.html"
    with html_path.open("w", encoding="utf-8") as f:
        f.write(html_content)
        if not html_content.endswith("\n"):
            f.write("\n")

    print(f"✅ index.html updated with status: {status}")


if __name__ == "__main__":
    main()

