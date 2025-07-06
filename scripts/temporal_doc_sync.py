#!/usr/bin/env python3
"""
🌀 Temporal Document Synchronization Engine
Main orchestrator for automated temporal document updates with phase-aware scheduling,
lockfile protection, commit filtering, throttling, and manual exclusion safeguards.

Integrates all utilities for safe, rhythm-conscious automation.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any

# Add utils directory to path
sys.path.append(str(Path(__file__).parent / "util"))

from phase_metrics import PhaseScheduler, PhaseAwareConfig
from manual_exclusions import ManualExclusionEngine
from lockfile_manager import LockfileManager, LockfileContextManager
from commit_filter import CommitFilter
from commit_throttle import CommitThrottle
from dry_run_diff import DryRunDiff


class TemporalDocSync:
    """Main temporal document synchronization orchestrator"""
    
    def __init__(self, bridge_root: Path, dry_run: bool = False, hook_mode: bool = False):
        self.bridge_root = bridge_root
        self.dry_run = dry_run
        self.hook_mode = hook_mode  # Running from git hook
        self.repo_root = bridge_root.parent  # Assume Paneudaemonium is sibling
        
        # Initialize all utilities
        self.phase_scheduler = PhaseScheduler(bridge_root)
        self.phase_config = PhaseAwareConfig()
        self.exclusion_engine = ManualExclusionEngine(bridge_root)
        self.commit_filter = CommitFilter()
        self.commit_throttle = CommitThrottle(self.repo_root)
        self.dry_diff = DryRunDiff(self.repo_root)
        
        # Sync log
        self.sync_log = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log synchronization messages"""
        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
        prefix = "🔍" if self.dry_run else "🌀"
        log_entry = f"{prefix} [{timestamp}] {level}: {message}"
        print(log_entry)
        self.sync_log.append(log_entry)
    
    def should_run_sync(self) -> Tuple[bool, str]:
        """
        Comprehensive check if synchronization should run
        
        Returns:
            Tuple of (should_run, reason)
        """
        # 1. Check if running from hook and commit should be filtered
        if self.hook_mode:
            should_skip, skip_reason = self.commit_filter.should_skip_commit()
            if should_skip:
                return False, f"Commit filtered: {skip_reason}"
        
        # 2. Check phase timing (unless emergency mode)
        if self.phase_config.is_phase_awareness_enabled() and not self.phase_config.is_emergency_mode():
            should_defer, defer_reason, next_optimal = self.phase_scheduler.should_defer_operation("heavy_report")
            if should_defer:
                return False, f"Phase timing: {defer_reason}"
        
        # 3. Check commit throttling
        is_throttled, throttle_reason, _ = self.commit_throttle.check_throttle_status()
        if is_throttled:
            return False, f"Commit throttled: {throttle_reason}"
        
        # 4. Check automation context
        is_automation, automation_reason = self.commit_filter.is_automation_context()
        if is_automation and not self.dry_run:
            # Extra caution in automation context
            self.log(f"Automation context detected: {automation_reason}", "WARN")
        
        return True, "All checks passed"
    
    def get_temporal_files(self) -> List[Path]:
        """Get list of files that are eligible for temporal updates"""
        all_md_files = list(self.bridge_root.glob("*.md"))
        
        # Filter to only modifiable files
        modifiable_files, excluded_files = self.exclusion_engine.get_modifiable_files(all_md_files)
        
        # Log exclusions
        for file_path, reason in excluded_files:
            self.log(f"Excluded: {file_path.name} - {reason}", "DEBUG")
        
        return modifiable_files
    
    def analyze_proposed_changes(self, file_changes: Dict[str, Tuple[str, str]]) -> Tuple[bool, Dict]:
        """
        Analyze all proposed changes for safety
        
        Args:
            file_changes: Dict mapping file paths to (original, proposed) content tuples
            
        Returns:
            Tuple of (is_safe, analysis)
        """
        # Check with dry-run diff utility
        if file_changes:
            analysis = self.dry_diff.check_multiple_files(file_changes)
            
            if analysis['overall_exceeds_threshold']:
                # Check for force override
                force_override = self.dry_diff.check_force_override()
                if not force_override and not self.dry_run:
                    return False, analysis
            
            return True, analysis
        
        return True, {"total_changes": 0, "message": "No changes to analyze"}
    
    def update_current_development_status(self) -> Optional[Tuple[str, str]]:
        """
        Update current_development_status.md with latest information
        
        Returns:
            Tuple of (original_content, proposed_content) or None if no changes
        """
        status_file = self.bridge_root / "current_development_status.md"
        
        if not status_file.exists():
            self.log("current_development_status.md not found", "WARN")
            return None
        
        original_content = status_file.read_text()
        
        # Generate updated content
        # This is a simplified example - in practice, this would gather
        # real status from git logs, issue trackers, etc.
        
        current_time = datetime.now(timezone.utc)
        phase_context = self.phase_scheduler.get_phase_context()
        
        # Extract auto-updatable sections
        auto_sections_pattern = r'(<!--\s*AUTO-PHASE-START\s*-->)(.*?)(<!--\s*AUTO-PHASE-END\s*-->)'
        
        # For now, just update the timestamp
        proposed_content = original_content
        
        # Update last updated date
        import re
        date_pattern = r'(\*\*Last Updated:\*\*\s+)(\d{4}-\d{2}-\d{2})'
        new_date = current_time.strftime('%Y-%m-%d')
        proposed_content = re.sub(date_pattern, rf'\g<1>{new_date}', proposed_content)
        
        # Add phase context if there's an auto-update section
        if "<!-- AUTO-PHASE-START -->" in proposed_content:
            phase_info = f"""
## 🌙 Current Phase Context (Auto-Updated)

- **Lunar Phase:** {phase_context['lunar_phase']} ({phase_context['lunar_description']})
- **Weekly Phase:** {phase_context['weekly_phase']} ({phase_context['weekly_description']})
- **Last Updated:** {current_time.strftime('%Y-%m-%d %H:%M:%S')} UTC
- **Optimal Operations:** {', '.join(phase_context['optimal_operations'][:3])}

"""
            proposed_content = re.sub(
                r'(<!--\s*AUTO-PHASE-START\s*-->)(.*?)(<!--\s*AUTO-PHASE-END\s*-->)',
                rf'\1{phase_info}\3',
                proposed_content,
                flags=re.DOTALL
            )
        
        if proposed_content != original_content:
            return original_content, proposed_content
        else:
            return None
    
    def update_spiral_versioning(self) -> Optional[Tuple[str, str]]:
        """
        Update spiral_versioning.md with latest developments
        
        Returns:
            Tuple of (original_content, proposed_content) or None if no changes
        """
        spiral_file = self.bridge_root / "spiral_versioning.md"
        
        if not spiral_file.exists():
            self.log("spiral_versioning.md not found", "WARN")
            return None
        
        original_content = spiral_file.read_text()
        
        # For now, just return None to indicate no automatic changes
        # Real implementation would add new spiral entries based on git activity
        
        return None
    
    def execute_sync(self) -> bool:
        """
        Execute the main synchronization process
        
        Returns:
            True if sync completed successfully
        """
        try:
            # Collect all proposed changes
            file_changes = {}
            
            # Check current development status
            status_changes = self.update_current_development_status()
            if status_changes:
                file_changes["current_development_status.md"] = status_changes
            
            # Check spiral versioning
            spiral_changes = self.update_spiral_versioning()
            if spiral_changes:
                file_changes["spiral_versioning.md"] = spiral_changes
            
            if not file_changes:
                self.log("No temporal updates needed")
                return True
            
            # Analyze all changes for safety
            is_safe, analysis = self.analyze_proposed_changes(file_changes)
            
            if not is_safe:
                self.log(f"Changes exceed safety threshold", "ERROR")
                # Save diff report
                if analysis.get('files_exceeding_threshold'):
                    for file_path in analysis['files_exceeding_threshold']:
                        file_analysis = analysis['file_results'][file_path]
                        self.dry_diff.save_diff_report(file_analysis)
                
                return False
            
            # Log changes summary
            if isinstance(analysis.get('file_results'), dict):
                total_changes = analysis['total_changes']
                self.log(f"Proposed changes: {total_changes} lines across {len(file_changes)} files")
            
            if self.dry_run:
                self.log("DRY-RUN: Would apply changes")
                for file_path in file_changes:
                    self.log(f"  Would update: {file_path}")
                return True
            
            # Apply changes
            for file_path, (original, proposed) in file_changes.items():
                full_path = self.bridge_root / file_path
                
                # Validate one more time
                is_safe, reason = self.exclusion_engine.validate_modification_safety(full_path, proposed)
                if not is_safe:
                    self.log(f"Skipping {file_path}: {reason}", "WARN")
                    continue
                
                # Write the file
                full_path.write_text(proposed)
                self.log(f"Updated: {file_path}")
            
            # Record commit for throttling
            if file_changes:
                self.commit_throttle.record_commit(
                    commit_hash="temporal_sync",
                    author="temporal-automation",
                    message=f"Temporal sync: {len(file_changes)} files"
                )
            
            return True
            
        except Exception as e:
            self.log(f"Sync failed: {e}", "ERROR")
            return False
    
    def run(self) -> bool:
        """
        Main entry point for temporal synchronization
        
        Returns:
            True if successful
        """
        self.log("🌀 Temporal Document Sync Engine Starting")
        
        # Check if sync should run
        should_run, reason = self.should_run_sync()
        if not should_run:
            self.log(f"Sync skipped: {reason}")
            return True  # Not an error, just skipped
        
        # Use lockfile to prevent concurrent runs
        try:
            with LockfileContextManager("temporal_sync", force=False):
                self.log("Lock acquired - proceeding with sync")
                success = self.execute_sync()
                
                if success:
                    self.log("✅ Temporal sync completed successfully")
                else:
                    self.log("❌ Temporal sync failed")
                
                return success
                
        except RuntimeError as e:
            self.log(f"Could not acquire lock: {e}")
            # Check if we should batch the update instead
            should_batch, batch_reason = self.commit_throttle.should_batch_updates()
            if should_batch:
                self.log(f"Creating batch for later processing: {batch_reason}")
                # Create batch content (simplified)
                batch_content = f"Temporal sync deferred at {datetime.now(timezone.utc).isoformat()}"
                self.commit_throttle.create_batch_file(batch_content)
            
            return False


def main():
    """CLI entry point for temporal document sync"""
    parser = argparse.ArgumentParser(
        description="🌀 Temporal Document Synchronization Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/temporal_doc_sync.py --dry-run          # Test without changes
  python scripts/temporal_doc_sync.py --hook-mode        # Run from git hook
  python scripts/temporal_doc_sync.py --force            # Bypass phase timing
        """
    )
    
    parser.add_argument('--bridge-root', default="../Lexigon-Bridge",
                       help='Path to Bridge repository')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    parser.add_argument('--hook-mode', action='store_true',
                       help='Running from git hook (enables commit filtering)')
    parser.add_argument('--force', action='store_true',
                       help='Bypass phase timing and throttling checks')
    parser.add_argument('--emergency', action='store_true',
                       help='Emergency mode - bypass all safety checks')
    
    args = parser.parse_args()
    
    bridge_root = Path(args.bridge_root).resolve()
    
    if not bridge_root.exists():
        print(f"❌ Bridge repository not found: {bridge_root}")
        exit(1)
    
    # Configure based on arguments
    if args.force or args.emergency:
        # Override phase awareness
        config = PhaseAwareConfig()
        if args.emergency:
            config.config["manual_overrides"]["emergency_mode"] = True
        if args.force:
            config.config["manual_overrides"]["phase_awareness_enabled"] = False
        config.save_config()
    
    # Create and run sync engine
    sync_engine = TemporalDocSync(
        bridge_root=bridge_root,
        dry_run=args.dry_run,
        hook_mode=args.hook_mode
    )
    
    success = sync_engine.run()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()