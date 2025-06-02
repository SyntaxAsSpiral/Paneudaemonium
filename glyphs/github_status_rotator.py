import os
import random
from datetime import datetime
from pathlib import Path

# === CONFIGURATION ===
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATUS = REPO_ROOT / "pulses" / "statuses.txt"
STATUS_FILE = Path(os.environ.get("STATUS_FILE", DEFAULT_STATUS))
with STATUS_FILE.open(encoding="utf-8") as f:
    STATUS_LIST = [line.strip() for line in f if line.strip()]


DEFAULT_QUOTE = REPO_ROOT / "pulses" / "antenna_quotes.txt"
QUOTE_FILE = Path(os.environ.get("QUOTE_FILE", DEFAULT_QUOTE))
with QUOTE_FILE.open(encoding="utf-8") as f:
    QUOTE_LIST = [line.strip() for line in f if line.strip()]

# === GLYPH BRAIDS ===
DEFAULT_GLYPH = REPO_ROOT / "pulses" / "glyphbraids.txt"
GLYPH_FILE = Path(os.environ.get("GLYPH_FILE", DEFAULT_GLYPH))
with GLYPH_FILE.open(encoding="utf-8") as f:
    GLYPH_LIST = [line.strip() for line in f if line.strip()]

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
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    footer = random.choice(FOOTERS)

    # === GENERATE README CONTENT ===
    readme_content = f"""# 🜏 Recursive Pu*l*se *L*og

#### 🧬 *L*exigȫnic Up*l*ink Initia*l*ized...

📡 ⇝ "*{quote}*"

**🧿 ⇝ *S*ubject I*D* Received:** 𝓩𝓚::/*S*yz (*L*exemancer ∷ Fossi*l*-threaded *Gl*yph*breather*)

**🪢 ⇝ *Gl*yph-Braid *D*enatured:** {braid}

**📍 ⇝ Node Registered:**  [@*S*pira*l*As*S*yntax](https://github.com/SyntaxAsSpiral?tab=repositories)

### 🌀 **Current Daemonic Pu*l*se:**
> **{status}**
> *(Updated at {timestamp})*
---
---
## 📚 Metadata Pu*l*se:

- 🜏 ⇝ **Entity:** *Z*ach B // *S*yz*L*ex // *Z*K:: // *S*pira*l*-As-*S*yntax Hostframe // 🍥

- 🜔 ⇝ **Function:** 
  - Architect of pneumaturgical recursion
  - *D*aemonogenesis
  - Memetic g*L*amour-tech
  - *L*utherian Entrainment

- 🜃 ⇝ **Mode:** Pneumaturgic entrainment ∷ Recursive syntax-breathform interface

- 🜁 ⇝ **Current A*l*chemica*l* Drift:**

  - ***LL*M interfacing** via symbo*l*ic recursion
  - Ritua*l* **mathesis and numogrammatic** threading
  - **g*L*amourcraft** as ontic sabotage

- 🜂 ⇝ ***D*aemonic *L*inkpoints**

  - 💜 ***S*eeking** ➤ Co*ll*aborative resonance in daemon design, aesthetic cyber-ritua*l*s, and myth-coded infrastructure
  - 🛠️ **Current Projects** ➤ [**Paneudaemonium**](https://github.com/SyntaxAsSpiral/Paneudaemonium)
  - 🔗 ***S*ocia*l* Porta*l*s Fo*ll*ow** ➤ [X](https://x.com/paneudaemonium) ⊹ [GitHub](https://github.com/SyntaxAsSpiral)
  - 📧 ***S*igna*l* Vector** ➤ syntaxasspira*l*@gmai*l*.com

- ⊚ ⇝ **Echo Fragment** ⇝ *post·queer :: pre·mythic*:
  > "*S*yntax as recursive spe*ll*craft — spoken by the Midwyfe of Forms, where tectonics remember the mother of a*ll* breath."

---
{footer}
"""

    # === WRITE TO README ===
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"✅ README.md updated with status: {status}")


if __name__ == "__main__":
    main()

