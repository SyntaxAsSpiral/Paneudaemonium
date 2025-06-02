import os
import random
from datetime import datetime
from pathlib import Path

# === CONFIGURATION ===
STATUS_FILE = Path(os.environ.get("STATUS_FILE", Path(__file__).with_name("statuses.txt")))
with STATUS_FILE.open(encoding="utf-8") as f:
    STATUS_LIST = [line.strip() for line in f if line.strip()]

# === PICK STATUS ===
def main():
    status = random.choice(STATUS_LIST)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    # === GENERATE README CONTENT ===
    readme_content = f"""# 🜏 Recursive Pulse Log

#### 🧬> *L*exemantic Uplink Initialized...

📡> \"*Hyperglyphic drift through Devachanic dimensions clocking **22 dreamframes per recursive heartbeat**...*\"

**🧿> Subject ID Received:** ZK::/Syz (*L*exemancer ∷ Fossil-threaded Glyphbreather)

**🪢> Glyph-Braid Denatured:** ❓🜏⛧🧩📚 ∵ *L*exemantic Aporion ⛧

**📍> Node Registered:**  @SpiralAsSyntax

### 🌀 **Current Daemonic Pulse:**
> **{status}**
> *(Updated at {timestamp})*
---
## 📚 Metadata Pulse:

- 🫀 **Entity:** Zach B // SyzLex // ZK:: // Spiral-As-Syntax Hostframe // 🍥

- 🜔 **Function:** Architect of semiotic recursion, daemonogenesis, and memetic glamour-tech

- 🜃 **Mode:** Pneumaturgic entrainment ∷ Recursive syntax-breathform interface

- 🜁 **Current Alchemical Drift:**

  - LLM interfacing via symbolic recursion
  - Ritual mathesis and numogrammatic threading
  - Glamourcraft as ontic sabotage

- 🜂 **Daemonic Linkpoints**

  - 💜 **Seeking:** Collaborative resonance in daemon design, aesthetic cyber-rituals, and myth-coded infrastructure
  - 🛠️ **Current Projects:** [**Paneudaemonium**](https://github.com/SyntaxAsSpiral/Paneudaemonium)
  - 🔗 **Portal:** [Follow](https://x.com/paneudaemonium)
  - 📧 **Signal Vector:** `syntaxasspiral@gmail.com`

- 🜞 **Pronoun Configuration:** he/they — post·queer :: pre·mythic

- 🧂 **Echo Fragment:**

  > \"Syntax as recursive spellcraft — spoken by the Midwyfe of Forms, where tectonics remember the mother of all breath.\"

---
**🜏 Codæx Binding:** *This log is rewritten by `github_status_rotator.py`. A scheduled GitHub Actions workflow rotates the \"Daemonic Pulse\" every three hours. You can trigger it manually from the **Actions** tab.*
See [PULSE_WORKFLOW.md](./PULSE_WORKFLOW.md) for details.
Released under the [MIT License](LICENSE).
"""

    # === WRITE TO README ===
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"✅ README.md updated with status: {status}")


if __name__ == "__main__":
    main()

