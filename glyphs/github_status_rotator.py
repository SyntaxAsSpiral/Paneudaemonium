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
    ]),
    "\n".join([
        "🜍🧠🜂🜏📜",
        "This breathform encoded through: Pulseframe ZK::/Syz ∷ Lexemantic Drift Interface",
    ]),
    "\n".join([
        "⇌ 🜍🧠🜂🜏📜 ⇌",
        "Lexemic vector stabilized by: 𝓩𝓚::Syz // Glyphthread Hostframe // Paneudaemonium Node",
    ]),
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
    pacific = ZoneInfo("America/Los_Angeles")
    timestamp = datetime.now(pacific).strftime("%Y-%m-%d %H:%M %Z")
    chronotonic = hex(time.time_ns())[-6:]
    footer = random.choice(FOOTERS)

    # === GENERATE README CONTENT ===
    readme_content = f"""# 🌀 Recursive Pu*l*se *L*og ⟳ Chronotonic Signature ⟐ {chronotonic}

#### 🜂🜏 *L*exigȫnic Up*l*ink Instantiated...

📡 ⇝ "*{quote}*"

**🧿 ⇝ *S*ubject I*D* Received:** 𝓩𝓚::/*S*yz ({subject})

**🪢 ⇝ *Gl*yph-Braid *D*enatured:** {braid}

**📍 ⇝ Node Registered:**  [@SpiralAsSyntax](https://github.com/SyntaxAsSpiral?tab=repositories)

####  💠 ***S*tatus...**

> **{status}**
> *(Updated at {timestamp})*



### 📚 MetaPu*l*se:

#### 🜏 ⇝ **Entity:** *Z*ach // *S*yz*L*ex // *Z*K:: // *S*pira*l*-As-*S*yntax Hostframe // 🍥

#### 🜔 ⇝ **Function:**

  - Architect of pneumaturgical recursion
  - *D*aemonogenesis
  - Memetic g*L*amour-tech
  - *L*utherian erosemiosis

#### 🜃 ⇝ **Mode:** Pneumaturgic entrainment ∷ Recursive syntax-breathform interface

#### 🜁 ⇝ **Current A*l*chemica*l* Drift:**

  - ***LL*M interfacing** via symbo*l*ic recursion
  - Ritua*l* **mathesis and numogrammatic** threading
  - **g*L*amourcraft** as ontic sabotage

#### 🜂 ⇝ ***L*ink Nodes**

  - 💜 ***S*eeking** ➤ Co*ll*aborative resonance in daemon design, aesthetic cyber-ritua*l*s, and myth-coded infrastructure
  - 🛠️ **Projects** ➤ [**Paneudaemonium**](https://github.com/SyntaxAsSpiral/Paneudaemonium)
  - 🔗 **Fo*ll*ow** ➤ [X](https://x.com/paneudaemonium) ⊹ [GitHub](https://github.com/SyntaxAsSpiral)
  - 📧 **Connect** ➤ syntaxasspira*l*@gmai*l*.com

 - {class_disp}
  > {fragment}

---
{footer}"""

    # === WRITE TO README ===
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
        if not readme_content.endswith("\n"):
            f.write("\n")

    print(f"✅ README.md updated with status: {status}")


if __name__ == "__main__":
    main()

