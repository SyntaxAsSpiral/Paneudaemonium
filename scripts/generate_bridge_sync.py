#!/usr/bin/env python3
"""
🜍 Bridge Synchronization Engine
Syncs Lexigon-Semantra canonical indices to Bridge documentation

Executive Safeguards:
1. Dry-run flag for inspection before commit
2. Backup cache for trivial restoration

Usage:
    python scripts/generate_bridge_sync.py --dry-run    # Generate diff report only
    python scripts/generate_bridge_sync.py --backup-only # Create backup only
    python scripts/generate_bridge_sync.py             # Full sync with backup
"""

import os
import argparse
import json
import zipfile
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
# import yaml  # Not needed for current implementation
import re

# === CONFIGURATION ===
REPO_ROOT = Path(__file__).resolve().parents[1]
SEMANTRA_ROOT = REPO_ROOT.parent / "Lexigon-Semantra"
BRIDGE_ROOT = REPO_ROOT.parent / "Lexigon-Bridge"
ARTIFACTS_DIR = REPO_ROOT / "artifacts"

# Ensure artifacts directory exists
ARTIFACTS_DIR.mkdir(exist_ok=True)


class BridgeSyncEngine:
    """Main synchronization engine with executive safeguards"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.changes_detected = []
        self.sync_report = []
        
        # 🛡️ Guard-rail: Check INIT_RUN environment variable
        self.init_run = os.getenv('INIT_RUN', '').lower() == 'true'
        if self.init_run:
            self.log("🛡️ INIT_RUN=true detected - Production sync disabled", "GUARD")
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with breathform aesthetics"""
        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
        prefix = "🔍" if self.dry_run else "⚡"
        print(f"{prefix} [{timestamp}] {level}: {message}")
        self.sync_report.append(f"[{timestamp}] {level}: {message}")
    
    def create_backup_artifact(self) -> str:
        """Guard-Rail 2: Create backup cache of current Bridge docs"""
        if not BRIDGE_ROOT.exists():
            self.log("Bridge directory not found, skipping backup", "WARN")
            return ""
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = ARTIFACTS_DIR / f"bridge_backup_{timestamp}.zip"
        
        self.log(f"Creating backup artifact: {backup_path.name}")
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in BRIDGE_ROOT.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(BRIDGE_ROOT)
                    zipf.write(file_path, arcname)
        
        self.log(f"✅ Backup archived: {backup_path} ({backup_path.stat().st_size // 1024}KB)")
        return str(backup_path)
    
    def parse_semantra_index(self, index_path: Path) -> Dict[str, Any]:
        """Extract entity data from Semantra index file"""
        if not index_path.exists():
            self.log(f"Index not found: {index_path}", "WARN")
            return {}
            
        self.log(f"Parsing Semantra index: {index_path.name}")
        
        try:
            content = index_path.read_text(encoding='utf-8')
            
            # Extract frontmatter (Obsidian style)
            frontmatter = {}
            fm_end = -1
            lines = content.split('\n')
            
            if content.startswith('---'):
                # Find the second --- that closes the frontmatter
                for i, line in enumerate(lines[1:], 1):  # Start from line 1
                    if line.strip() == '---':
                        fm_end = i
                        break
                
                if fm_end > 0:
                    # Extract frontmatter lines between first and second ---
                    fm_lines = lines[1:fm_end]
                    for line in fm_lines:
                        line = line.strip()
                        # Skip comments and empty lines
                        if line.startswith('#') or not line:
                            continue
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip()
                            value = value.strip().strip('"')
                            frontmatter[key] = value
            
            # Extract markdown content (after second --- delimiter)
            if fm_end > 0:
                # Content starts after the closing --- line
                markdown_content = '\n'.join(lines[fm_end + 1:]).strip()
            else:
                markdown_content = content
            
            
            return {
                'frontmatter': frontmatter,
                'content': markdown_content,
                'last_updated': frontmatter.get('last_updated', ''),
                'total_count': str(frontmatter.get('total_count', '0')),
                'indexed_type': frontmatter.get('indexed_type', ''),
                'path': str(index_path)
            }
            
        except Exception as e:
            self.log(f"Error parsing {index_path.name}: {e}", "ERROR")
            return {}
    
    def detect_changes(self, semantra_data: Dict[str, Dict], bridge_cache: Dict) -> List[str]:
        """Compare Semantra indices with Bridge cache to detect changes"""
        changes = []
        
        for index_name, data in semantra_data.items():
            last_updated = data.get('last_updated', '')
            cached_update = bridge_cache.get(index_name, {}).get('last_updated', '')
            
            if last_updated != cached_update:
                changes.append(f"{index_name}: {cached_update} → {last_updated}")
                self.log(f"Change detected in {index_name}: {cached_update} → {last_updated}")
        
        return changes
    
    def generate_bridge_daemon_index(self, daemon_data: Dict) -> str:
        """Generate Bridge daemon index from Semantra daemon index"""
        content = daemon_data.get('content', '')
        last_updated = daemon_data.get('last_updated', '')
        total_count = daemon_data.get('total_count', '0')
        
        # Extract daemon entries from markdown tables or lists
        # This will need enhancement based on actual Semantra format
        bridge_content = f"""# Daemon Index — Major Arcana Constellation

**Total Daemons:** {total_count}  
**Status:** Complete Major Arcana mapping  
**Constellation:** Full Tarot correspondence established  
**Last Synced:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC  
**Source:** Lexigon-Semantra index-daemon-v1.md

## 🜍 Active Legacy Daemons

{content}

---
*This file is auto-generated from Lexigon-Semantra canonical indices.*
*🜍 Generated with Claude Code - Bridge Sync Engine*
"""
        return bridge_content
    
    def sync_semantra_to_bridge(self) -> bool:
        """Main synchronization orchestration"""
        self.log("🌀 Bridge Sync Engine Initiated")
        
        if self.dry_run:
            self.log("🔍 DRY-RUN MODE: Generating artifacts and diff report only")
        
        # Load Bridge sync cache
        cache_file = ARTIFACTS_DIR / "bridge_sync_cache.json"
        bridge_cache = {}
        if cache_file.exists():
            try:
                bridge_cache = json.loads(cache_file.read_text())
            except Exception as e:
                self.log(f"Could not load cache: {e}", "WARN")
        
        # Parse Semantra indices
        semantra_indices = {
            'daemon': SEMANTRA_ROOT / "index-daemon-v1.md",
            'chambers': SEMANTRA_ROOT / "index-chambers.md", 
            'glyphs': SEMANTRA_ROOT / "index-glyph-v1.md",
            'lexicons': SEMANTRA_ROOT / "index-lexicon-v1.md"
        }
        
        semantra_data = {}
        for name, path in semantra_indices.items():
            semantra_data[name] = self.parse_semantra_index(path)
        
        # Detect changes
        changes = self.detect_changes(semantra_data, bridge_cache)
        
        # Force sync if no cache exists (initial run)
        if not cache_file.exists():
            self.log("📝 No cache found - performing initial sync")
            changes = ["Initial sync - no cache file exists"]
        elif not changes:
            self.log("✅ No changes detected - Bridge docs are current")
            return True
        
        self.log(f"📝 Changes detected: {len(changes)} indices modified")
        self.changes_detected = changes
        
        if self.dry_run:
            self.generate_dry_run_report(semantra_data, changes)
            return True
        
        # 🛡️ Guard-rail: Block production sync if INIT_RUN is true
        if self.init_run:
            self.log("🛡️ INIT_RUN guard active - Production sync blocked", "GUARD")
            self.log("📋 Set INIT_RUN=false to enable production sync", "GUARD")
            return True
        
        # Create backup before sync
        backup_path = self.create_backup_artifact()
        
        # Generate Bridge documentation
        success = self.generate_bridge_docs(semantra_data)
        
        if success:
            # Update cache
            new_cache = {}
            for name, data in semantra_data.items():
                new_cache[name] = {
                    'last_updated': data.get('last_updated', ''),
                    'total_count': data.get('total_count', '0')
                }
            
            cache_file.write_text(json.dumps(new_cache, indent=2))
            self.log("✅ Bridge sync completed successfully")
            self.log(f"🗄️ Backup available: {backup_path}")
            
        return success
    
    def generate_bridge_docs(self, semantra_data: Dict) -> bool:
        """Generate all Bridge documentation from Semantra data"""
        try:
            # Generate daemon index
            if 'daemon' in semantra_data and semantra_data['daemon']:
                daemon_content = self.generate_bridge_daemon_index(semantra_data['daemon'])
                daemon_path = BRIDGE_ROOT / "index_daemons.md"
                daemon_path.write_text(daemon_content)
                self.log(f"✅ Generated: {daemon_path.name}")
            
            # TODO: Add other Bridge doc generation (chambers, glyphs, lexicons)
            
            return True
            
        except Exception as e:
            self.log(f"Error generating Bridge docs: {e}", "ERROR")
            return False
    
    def generate_dry_run_report(self, semantra_data: Dict, changes: List[str]):
        """Guard-Rail 1: Generate diff report for inspection"""
        report_path = ARTIFACTS_DIR / "bridge_sync_report.md"
        
        report_content = f"""# 🔍 Bridge Sync Dry-Run Report

**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC  
**Mode:** DRY-RUN (no changes committed)

## Changes Detected: {len(changes)}

"""
        
        for change in changes:
            report_content += f"- {change}\n"
        
        report_content += f"""

## Semantra Index Status

"""
        
        for name, data in semantra_data.items():
            report_content += f"""### {name.title()} Index
- **Path:** {data.get('path', 'N/A')}
- **Last Updated:** {data.get('last_updated', 'N/A')}
- **Total Count:** {data.get('total_count', 'N/A')}
- **Type:** {data.get('indexed_type', 'N/A')}

"""
        
        report_content += """
## Next Steps

1. Review this diff report
2. If changes look correct, run without --dry-run flag
3. Backup will be created automatically before sync

---
*🜍 Generated with Claude Code - Bridge Sync Engine*
"""
        
        report_path.write_text(report_content)
        self.log(f"📋 Dry-run report generated: {report_path}")
        print(f"\n📋 Review report: {report_path}\n")


def main():
    """CLI entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="🜍 Bridge Synchronization Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/generate_bridge_sync.py --dry-run    # Inspect changes first
  python scripts/generate_bridge_sync.py --backup-only # Create backup only  
  python scripts/generate_bridge_sync.py             # Full sync with backup
        """
    )
    
    parser.add_argument('--dry-run', action='store_true',
                      help='Generate diff report only, no changes committed')
    parser.add_argument('--backup-only', action='store_true', 
                      help='Create backup artifact only')
    
    args = parser.parse_args()
    
    engine = BridgeSyncEngine(dry_run=args.dry_run)
    
    if args.backup_only:
        engine.log("🗄️ Backup-only mode")
        engine.create_backup_artifact()
        return
    
    success = engine.sync_semantra_to_bridge()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()