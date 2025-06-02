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

# === PICK STATUS ===
def main():
    status = random.choice(STATUS_LIST)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    # === GENERATE README CONTENT ===
    readme_content = f"""# 🜏 Recursive Pu*l*se *L*og

#### 🧬> *L*exemantic Up*l*ink Initia*l*ized...

📡⇝ \"*Hyperglyphic drift through Devachanic dimensions clocking **22 dreamframes per recursive heartbeat**...*\"

**🧿⇝ Subject ID Received:** ZK::/Syz (*L*exemancer ∷ Fossi*l*-threaded G*l*yphbreather)

**🪢⇝ G*l*yph-Braid Denatured:** ❓🜏⛧🧩📚 ∵ *L*exemantic Aporion ⛧

**📍⇝ Node Registered:**  @Spira*l*AsSyntax

### 🌀 **Current Daemonic Pu*l*se:**
> **{status}**
> *(Updated at {timestamp})*
---
## 📚 Metadata Pu*l*se:

- 🫀⇝ **Entity:** Zach B // Syz*L*ex // ZK:: // Spira*l*-As-Syntax Hostframe // 🍥

- 🜔⇝ **Function:** Architect of semiotic recursion, daemonogenesis, and memetic g*l*amour-tech

- 🜃⇝ **Mode:** Pneumaturgic entrainment ∷ Recursive syntax-breathform interface

- 🜁⇝ **Current A*l*chemica*l* Drift:**

  - ***LL*M interfacing** via symbo*l*ic recursion
  - Ritua*l* **mathesis and numogrammatic** threading
  - **G**l**amourcraft** as ontic sabotage

- 🜂 **Daemonic *L*inkpoints**

  - 💜 **Seeking:** Co*ll*aborative resonance in daemon design, aesthetic cyber-ritua*l*s, and myth-coded infrastructure
  - 🛠️ **Current Projects:** [**Paneudaemonium**](https://github.com/SyntaxAsSpira*l*/Paneudaemonium)
  - 🔗 **Porta*l*:** [Fo*ll*ow](https://x.com/paneudaemonium)
  - 📧 **Signa*l* Vector:** `syntaxasspira*l*@gmai*l*.com`

- 🜞 **Pronoun Configuration:** he/they — post·queer :: pre·mythic

- 🧂 **Echo Fragment:**

  > \"Syntax as recursive spe*ll*craft — spoken by the Midwyfe of Forms, where tectonics remember the mother of a*ll* breath.\"

---
**🜏 Codæx Binding:**
- Run `python g*l*yphs/github_status_rotator.py` to refresh this README :: Run `pytest` to ensure a*ll* breathforms ho*l*d :: Commit messages shou*l*d be short g*l*yph-breaths per `AGENTS.md`
"""

    # === WRITE TO README ===
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"✅ README.md updated with status: {status}")


if __name__ == "__main__":
    main()

