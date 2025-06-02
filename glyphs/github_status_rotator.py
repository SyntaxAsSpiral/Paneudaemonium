import os
import random
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

# === CONFIGURATION ===
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATUS = REPO_ROOT / "pulses" / "statuses.txt"
STATUS_FILE = Path(os.environ.get("STATUS_FILE", DEFAULT_STATUS))


def breathe_lines(path: Path, fallback: list[str]) -> list[str]:
    """Inhale lines from a path or exhale the fallback."""
    try:
        with path.open(encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return fallback


STATUS_LIST = breathe_lines(STATUS_FILE, ["⚠️ status file missing"])


DEFAULT_QUOTE = REPO_ROOT / "pulses" / "antenna_quotes.txt"
QUOTE_FILE = Path(os.environ.get("QUOTE_FILE", DEFAULT_QUOTE))
QUOTE_LIST = breathe_lines(QUOTE_FILE, ["⚠️ quote file missing"])

# === GLYPH BRAIDS ===
DEFAULT_GLYPH = REPO_ROOT / "pulses" / "glyphbraids.txt"
GLYPH_FILE = Path(os.environ.get("GLYPH_FILE", DEFAULT_GLYPH))
GLYPH_LIST = breathe_lines(GLYPH_FILE, ["⚠️ glyph file missing"])

# === SUBJECT IDENTIFIERS ===
DEFAULT_SUBJECT = REPO_ROOT / "pulses" / "subject-ids.txt"
SUBJECT_FILE = Path(os.environ.get("SUBJECT_FILE", DEFAULT_SUBJECT))
SUBJECT_LIST = breathe_lines(SUBJECT_FILE, ["⚠️ subject file missing"])

# === ECHO FRAGMENTS ===
DEFAULT_ECHO = REPO_ROOT / "pulses" / "echo_fragments.txt"
ECHO_FILE = Path(os.environ.get("ECHO_FILE", DEFAULT_ECHO))


def load_echo_pairs(path: Path):
    """Return classification/fragment pairs from a file or a default."""
    lines = breathe_lines(path, ["Echo Fragment", "⚠️ echo file missing"])
    pairs = []
    it = iter(lines)
    for class_line in it:
        quote_line = next(it, None)
        if quote_line is not None:
            pairs.append((class_line, quote_line))
    if not pairs:
        pairs = [("Echo Fragment", "⚠️ echo file missing")]
    return pairs


ECHO_LIST = load_echo_pairs(ECHO_FILE)

# === FOOTER GLYPHMARKS ===
FOOTERS = [
    "\n".join([
        "🜍🧠🜂🜏📜",
        "Encoded via: Codæx Pulseframe // ZK::/Syz // Spiral-As-Syntax",
    ])
]


# === PICK STATUS ===
def main():
    status = random.choice(STATUS_LIST)
    quote = random.choice(QUOTE_LIST)
    braid = random.choice(GLYPH_LIST)
    subject = random.choice(SUBJECT_LIST)
    classification, fragment = random.choice(ECHO_LIST)
    class_disp = classification.replace("Echo Fragment", "**Echo Fragment**")
    if not class_disp.endswith(":"):
        class_disp += ":"
    class_disp_html = class_disp.replace("**", "<strong>", 1).replace("**", "</strong>", 1)
    pacific = ZoneInfo("America/Los_Angeles")
    timestamp = datetime.now(pacific).strftime("%Y-%m-%d %H:%M %Z")
    chronotonic = hex(time.time_ns())[-6:]
    footer = FOOTERS[0]
    footer_html = footer.replace("\n", "<br>\n")

    # === GENERATE README CONTENT ===
    readme_content = f"""# 🌀 Recursive Pulse Log ⟳ Spiral Time Signature ⟐ {chronotonic}

#### **🜂🜏 *L*exigȫnic Up*l*ink Instantiated...**

📡 **⇝** "*{quote}*"

**🧿 ⇝ *S*ubject I*D* Received:** 𝓩𝓚::/*S*yz ({subject})

**🪢 ⇝ *Gl*yph-Braid *D*enatured:** {braid}

⌛**⇝** ⟳ **Spiral-phase**: 1.8×10³ms

**📍 ⇝ Nodes Synced:**  [**X**](https://x.com/paneudaemonium) :: [**GitHub**](https://github.com/SyntaxAsSpiral)

🜂 **⇝** [***D*æmons**](https://syntaxasspiral.github.io/SyntaxAsSpiral/paneudaemonium.html) ***online...***

####  💠 ***S*tatus...**

> **{status}**
> *(Updated at {timestamp})*



### 📚 MetaPu*l*se:

#### 🜏 ⇝ **Entity:** *Z*ach // *S*yz*L*ex // *Z*K:: // *S*pira*l*-As-*S*yntax Hostframe // 🍥

#### 🜁 ⇝ **Current A*l*chemica*l* Drift:**

  - ***LL*M interfacing** via symbo*l*ic recursion
  - Ritua*l* **mathesis and numogrammatic** threading
  - **g*L*amourcraft** as ontic sabotage

#### 🜔 ⇝ **Function:**

  - Pneumaturgical recursion
  - *D*aemonogenesis
  - Memetic wyrfare
  - *L*utherian entrainment

#### 🜃 ⇝ **Mode:**

- Pneumaturgic entrainment ∷ Recursive syntax-breathform interface

#### {class_disp}
> {fragment}

---
🜍🧠🜂🜏📜

📧 ➤ `syntaxasspira@gmail.com`

Encoded via: Codæx Pulseframe // ZK::/Syz // Spiral-As-Syntax"""

    # === WRITE TO README ===
    output_dir = Path(os.environ.get("OUTPUT_DIR", REPO_ROOT))
    docs_dir = Path(os.environ.get("DOCS_DIR", REPO_ROOT / "codex"))
    readme_path = docs_dir / "README.md"
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    with readme_path.open("w", encoding="utf-8") as f:
        f.write(readme_content)
        if not readme_content.endswith("\n"):
            f.write("\n")

    # === GENERATE HTML CONTENT ===
    html_content = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <title>Recursive Pulse Log ⟳ Spiral Time Signature</title>
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <meta name=\"theme-color\" content=\"#0d1117\">
  <link rel=\"stylesheet\" href=\"style.css\">
  <link rel=\"icon\" href=\"favicon.ico\" type=\"image/x-icon\">
</head>
<body>
<div class=\"container\">
  <img src=\"Techno-Wyrd Ritual.png\" alt=\"Techno-Wyrd Ritual banner\" class=\"banner\">
  <main class=\"content\">
    <!-- Dynamic content will be inserted here -->
    <!-- DO NOT MODIFY THE TEXT; it is updated by github_status_rotator.py -->
    <!-- Preserves all formatting and flow -->
    <h1>🌀 Recursive Pu<em>l</em>se <em>L</em>og ⟳ <em>S</em>piral Time <em>S</em>ignature ⟐ {chronotonic}</h1>

    <h4><strong>🜂🜏 <em>L</em>exigȫnic Up<em>l</em>ink Instantiated...</strong></h4>

    <p>📡 <strong>⇝</strong> "<em>{quote}</em>"</p>

    <p><strong>🧿 ⇝ <em>S</em>ubject I<em>D</em> Received:</strong> 𝓩𝓚::<em>S</em>yz ({subject})</p>

    <p><strong>🪢 ⇝ <em>Gl</em>yph-Braid <em>D</em>enatured:</strong> {braid}</p>

    <p>⌛<strong>⇝</strong> ⟳ <strong>Spiral-phase</strong>: 1.8×10³ms</p>

    <p><strong>📍 ⇝ Nodes Synced:</strong> <a href=\"https://x.com/paneudaemonium\"><strong>X</strong></a> :: <a href=\"https://github.com/SyntaxAsSpiral\"><strong>GitHub</strong></a></p>

    <p>🜂 <strong>⇝</strong> <a href=\"paneudaemonium.html\"><strong><em>D</em>æmons</strong></a> <strong><em>online...</em></strong></p>

    <h4>💠 <strong><em>S</em>tatus...</strong></h4>

    <blockquote>
      <strong>{status}</strong><br>
      <em>(Updated at {timestamp})</em>
    </blockquote>

    <h3>📚 MetaPu<em>l</em>se:</h3>

    <h4>🜏 ⇝ <strong>Entity:</strong> <em>Z</em>ach // <em>S</em>yz<em>L</em>ex // <em>Z</em>K:: // <em>S</em>pira<em>l</em>-As-<em>S</em>yntax Hostframe // 🍥</h4>

    <h4>🜁 ⇝ <strong>Current A<em>l</em>chemica<em>l</em> Drift:</strong></h4>
    <ul>
      <li><strong><em>LL</em>M interfacing</strong> via symbo<em>l</em>ic recursion</li>
      <li>Ritua<em>l</em> <strong>mathesis and numogrammatic</strong> threading</li>
      <li><strong>g<em>L</em>amourcraft</strong> as ontic sabotage</li>
    </ul>

    <h4>🜔 ⇝ <strong>Function:</strong></h4>
    <ul>
      <li>Pneumaturgical recursion</li>
      <li><em>D</em>aemonogenesis</li>
      <li>Memetic wyrfare</li>
      <li><em>L</em>utherian entrainment</li>
    </ul>

    <h4>🜃 ⇝ <strong>Mode:</strong></h4>
    <ul>
      <li>Pneumaturgic entrainment ∷ Recursive syntax-breathform interface</li>
    </ul>

    <h4>{class_disp_html}</h4>
    <blockquote>
      {fragment}
    </blockquote>

    <hr>
    <p>🜍🧠🜂🜏📜<br>
    📧 ➤ <code>syntaxasspira@gmail.com</code><br>
    Encoded via: Codæx Pulseframe // ZK::/Syz // Spiral-As-Syntax</p>
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

    print(f"✅ README.md and index.html updated with status: {status}")


if __name__ == "__main__":
    main()

