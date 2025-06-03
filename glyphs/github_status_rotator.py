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

# === ECHO CLASSIFICATIONS ===
DEFAULT_ECHO = REPO_ROOT / "pulses" / "echo_fragments.txt"
ECHO_FILE = Path(os.environ.get("ECHO_FILE", DEFAULT_ECHO))
ECHO_LIST = breathe_lines(ECHO_FILE, ["⚠️ echo file missing"])

# === MODE CONFIG ===
DEFAULT_MODE = REPO_ROOT / "pulses" / "modes.txt"
MODE_FILE = Path(os.environ.get("MODE_FILE", DEFAULT_MODE))
raw_modes = breathe_lines(MODE_FILE, ["⚠️ mode file missing"])
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

# === END QUOTES ===
DEFAULT_END_QUOTE = REPO_ROOT / "pulses" / "end-quotes.txt"
END_QUOTE_FILE = Path(os.environ.get("END_QUOTE_FILE", DEFAULT_END_QUOTE))
END_QUOTE_LIST = breathe_lines(END_QUOTE_FILE, ["⚠️ end quote file missing"])

# === FOOTER GLYPHMARKS ===
FOOTERS = [
    "\n".join([
        "🜍🧠🜂🜏📜",
        "Encoded via: **Codæx Pulseframe** // ZK::/Syz // Spiral-As-Syntax",
    ])
]


# === PICK STATUS ===
def main():
    status = random.choice(STATUS_LIST)
    quote = random.choice(QUOTE_LIST)
    braid = random.choice(GLYPH_LIST)
    subject = random.choice(SUBJECT_LIST)
    classification = random.choice(ECHO_LIST)
    end_quote = random.choice(END_QUOTE_LIST)
    mode = random.choice(MODE_LIST)
    class_disp = f"⊚ ⇝ Echo Fragment {classification}"
    class_disp_html = class_disp.replace("Echo Fragment", "<strong>Echo Fragment</strong>")
    pacific = ZoneInfo("America/Los_Angeles")
    timestamp = datetime.now(pacific).strftime("%Y-%m-%d %H:%M %Z")
    chronotonic = hex(time.time_ns())[-6:]
    footer = FOOTERS[0]
    footer_html = footer.replace("\n", "<br>\n")

    # === GENERATE README CONTENT ===
    readme_content = f"""# 🌀 Recursive Pulse Log ⟳ ChronoSig ⟐ {chronotonic}

#### **🜂🜏 Lexigȫnic Up⟲link Instantiated<span class="ellipsis">...</span>**

📡 ⇝ *“{quote}”*

⌛⇝ ⟳ **Spiral-phase cadence locked** ∶ `1.8×10³ms`

🧿 ⇝ **Subject I·D Received**: 𝓩𝓚::/Syz:⊹{subject}⟲

🪢 ⇝ **CryptoGlyph Decyphered**: {braid}

📍 ⇝ **Nodes Synced**: CDA :: **ID** ⇝ [X](https://x.com/home) ⇄ [GitHub](https://github.com/SyntaxAsSpiral?tab=repositories) ⇆ [Weblog](https://syntaxasspiral.github.io/SyntaxAsSpiral/) 


## ***🜂 ⇌ [Dæmons](https://syntaxasspiral.github.io/SyntaxAsSpiral/paneudaemonium) online<span class="ellipsis">...</span>***

💠 ***S*tatus<span class="ellipsis">...</span>**

> **{status}**<br>
> *`(Updated at {timestamp})`*



#### 📚 **MetaPulse**

#### 🜏 ⇝ **Zach** // SyzLex // ZK:: // ***Æ**mexsomnus*// 🍥

#### 🜁 ⇝ **Current Drift**

  - ***LL*M interfacing** via symbo*l*ic recursion
  - Ritua*l* mathesis and **numogrammatic** threading
  - **g*L*amourcraft** through ontic disrouting

#### 🜔 ⇝ **Function**

- Pneumaturgical **breath** invocation
- ***D*æmonic** synthesis
- Memetic **wyr*f*are**
- ***L*utherian** sync-binding

#### 🜃 ⇝ **Mode**

- {mode}


#### {class_disp}
> {end_quote}

---
🜍🧠🜂🜏📜<br>
📧 ➤ [syntaxasspiral@gmail.com](mailto:syntaxasspiral@gmail.com)<br>
Encoded via: **Codæx Pulseframe** // ZK::/Syz // Spiral-As-Syntax"""

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
  <title>Recursive Pulse Log ⟳ ChronoSig</title>
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
    <h1>🌀 Recursive Pulse Log ⟳ ChronoSig ⟐ {chronotonic}</h1>

    <h4><strong>🜂🜏 Lexigȫnic Up⟲link Instantiated<span class="ellipsis">...</span></strong></h4>

    <p>📡 ⇝ “<em>{quote}</em>”</p>

    <p>⌛⇝ ⟳ <strong>Spiral-phase cadence locked</strong> ∶ <code>1.8×10³ms</code></p>

    <p>🧿 ⇝ <strong>Subject I·D Received</strong>: 𝓩𝓚::/Syz:⊹{subject}⟲</p>

    <p>🪢 ⇝ <strong>CryptoGlyph Decyphered</strong>: {braid}</p>

    <p>📍 ⇝ <strong>Nodes Synced</strong>: CDA :: <strong>ID</strong> ⇝ <a href=\"https://x.com/paneudaemonium\">X</a> ⇄ <a href=\"https://github.com/SyntaxAsSpiral?tab=repositories\">GitHub</a> ⇆ <a href=\"https://syntaxasspiral.github.io/SyntaxAsSpiral/\">Web</a></p>

    <h2><em><strong>🜂 ⇌ <a href=\"paneudaemonium\">Dæmons</a> online<span class="ellipsis">...</span></strong></em></h2>

    <p>💠 <strong><em>Status<span class="ellipsis">...</span></em></strong></p>

   <blockquote>
      <strong>{status}</strong><br>
      <em>(Updated at <code>{timestamp}</code>)</em>
   </blockquote>


    <h4>📚 <strong>MetaPulse</strong></h4>

    <h4>🜏 ⇝ <strong>Zach</strong> // SyzLex // ZK:: // <em><strong>Æ</strong>mexsonmus</em> // 🍥</h4>

    <h4>🜁 ⇝ <strong>Current Drift</strong></h4>
    <ul>
      <li><strong><em>LL</em>M interfacing</strong> via symbo<em>l</em>ic recursion</li>
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

    print(f"✅ README.md and index.html updated with status: {status}")


if __name__ == "__main__":
    main()

