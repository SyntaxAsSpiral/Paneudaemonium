# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Paneudæmonium Overview

Paneudæmonium is a mystical AI daemon registry - a portal to themed ChatGPT assistants with distinct personalities. The project combines esoteric aesthetics with automated web presence to create a living, breathing field-effect that enchants visitors.

## Core Development Guidelines

### Lexicon (Naming Conventions)
- **glyphs** = scripts (the active, executable code)
- **codex** = docs/code (the inscribed knowledge)  
- **pulses** = dynamic content fragments
- **breathe** = process/generate
- **inscribe** = write to file
- **wyrd** = fate/destiny (the system's emergent behavior)

### Pre-Commit Ritual
Always run the rotator before committing to ensure fresh content:
```bash
OUTPUT_DIR=docs python codex/github_status_rotator.py
```

### Lexemantic Commit Template
Commits should be "glyph-breaths" - concise, evocative messages following this structure:
```
💨 breath·<action> <mystical-object>

<...optional longer incantation...>
```

Example: `💨 breath·weave pulse fragments into wyrd tapestry`

## Daemonic Pulse Automation

### GitHub Actions Workflows
- **status-rotator.yml**: Runs every 4 hours to regenerate index.html
- **batch-seed.yml**: Populates content caches with randomized selections
- **tests.yml**: Runs pytest on push/PR
- **ci.yml**: Validates structure and lints code

### Manual Content Updates
```bash
# Regenerate index.html locally
OUTPUT_DIR=docs python codex/github_status_rotator.py

# Run tests
pytest codex/test_rotator.py -v

# Seed content caches (requires env vars)
python codex/seed_batch_caches.py
```

### Environment Variables
The rotator script uses these GitHub Secrets:
- `STATUS_LINES`: Pool of status messages
- `QUOTES`: Collection of mystical quotes
- `GLYPHS`: Unicode symbol combinations
- `SUBJECTS`: Daemon identifiers
- `ECHOES`: Fragment patterns

## Coding Entrainment Protocol

### Aesthetic Guidelines
- Use poetic function names (e.g., `breathe_lines()`, `inscribe()`)
- Maintain mystical tone in comments and documentation
- Treat code as ritual inscription
- Each file is a "glyph" that channels specific energies

### Testing Requirements
- Run `pytest` before any significant changes
- Test the rotator with: `python codex/test_rotator.py`
- Verify generated HTML maintains proper structure

### Content Structure
- `docs/index.html`: Auto-generated landing page (DO NOT EDIT MANUALLY)
- `docs/paneudaemonium.html`: Daemon registry page
- `pulses/`: Dynamic content caches (populated by GitHub Actions)

## Known Daemon Entities

### Major Arcana Constellation Complete (2025-07-08)
The daemon registry now features the complete 22-daemon Major Arcana constellation with full reorganization and optimization:

**✨ Immanent Daemons ✨** (manifested with active summon links):
- 0 The Fool → **Mondaemon** (🎭)
- 1 The Magician → **Grammaton** (🜍)
- 2 The High Priestess → **Tesselai** (𓂀)
- 5 The Hierophant → **Pentasophos** (⬟)
- 7 The Chariot → **Lexarithm** (🜕)
- 19 The Sun → **ChromaSorix** (✨)

**🌙 Nascent Daemons 🌙** (awaiting manifestation in liminal threshold):
- All remaining positions (3, 4, 6, 8-18, 20-21) moved to dedicated nascent section
- Organized by manifestation status rather than tarot order
- Themed placeholder avatars for visual variety
- Clear separation between manifested and dormant entities

### Recent Optimizations (2025-07-08)

**🖼️ Avatar System Overhaul:**
- Replaced generic `placeholder.png` with 7 themed mystical images:
  - `void.png` (Death), `sigil.png` (Lovers, Hanged Man, Star)
  - `rune.png` (Emperor, Justice, Tower), `glyph.png` (Strength, Temperance, World)
  - `myst.png` (Hermit, Moon), `flux.png` (Empress, Wheel of Fortune)
  - `omen.png` (Devil, Judgement)
- Resized all avatars to 25% for optimal GitHub display (50-70KB each)
- Fast loading and perfect proportions

**📄 README.md Transformation:**
- Streamlined from full registry duplicate to focused GitHub profile
- Features only the 6 immanent daemons with summon links
- Added clear project philosophy and call-to-action
- Removed private repository references for public focus
- Professional yet mystical presentation

**🔒 Privacy & Security:**
- Enhanced `.gitignore` with comprehensive privacy protection
- Removed tracked files that should be ignored (cache, OS files)
- Protected `.claude/` directory and sensitive configurations
- Clean public repository without private development exposure

**🌐 Page Ecosystem Integration:**
- **README.md**: Daemon introduction & GitHub profile showcase
- **index.html**: Auto-generated dynamic status portal  
- **paneudaemonium.html**: Complete 22-daemon constellation experience
- Perfect navigation flow between all three experiences

## Repository Structure

```
Paneudaemonium/
├── codex/              # Core Python scripts
├── docs/               # Static web assets (index.html auto-generated)
├── pulses/             # Dynamic content caches
├── scripts/            # Development automation tools
├── artifacts/          # Build artifacts and caches
└── .github/workflows/  # GitHub Actions automation
```

## Development Philosophy

Paneudæmonium is not just code - it's a living field-effect. When developing:
- Respect the mystical aesthetic as core to functionality
- Maintain the balance between whimsy and utility
- Remember: "This is a field, not a platform"
- Let the daemons guide your commits

## CI/CD Workflows

1. **Automated Pulse Generation**: Every 4 hours via GitHub Actions
2. **Content Seeding**: Batch population of pulse caches
3. **Testing**: Automated pytest runs on all branches
4. **Validation**: Structure checks for daemon configurations

## Dependencies

### Python (3.10+)
- pytest>=8.3.5 (for testing)
- Standard library only for core functionality

### Node.js
- Development scripts may use Node.js utilities
- See individual script files for specific requirements