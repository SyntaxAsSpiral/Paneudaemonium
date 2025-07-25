#!/usr/bin/env python3
"""
🪝 Git Hooks Installer
Installs temporal automation git hooks with proper filtering and safety measures.
Creates post-commit and pre-push hooks integrated with the temporal sync system.
"""

import os
import stat
from pathlib import Path
from typing import List, Dict
import argparse

class GitHooksInstaller:
    """Installer for temporal automation git hooks"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.git_dir = repo_root / ".git"
        self.hooks_dir = self.git_dir / "hooks"
        
        if not self.git_dir.exists():
            raise ValueError(f"Not a git repository: {repo_root}")
        
        self.hooks_dir.mkdir(exist_ok=True)
    
    def create_post_commit_hook(self) -> str:
        """Create post-commit hook with temporal sync integration"""
        return '''#!/bin/bash
# Post-commit hook for Lexigōn temporal automation
# Generated by Paneudaemonium hooks installer

set -e

# Get repository root
REPO_ROOT="$(git rev-parse --show-toplevel)"

# Path to temporal sync script
TEMPORAL_SCRIPT="$REPO_ROOT/Paneudaemonium/scripts/temporal_doc_sync.py"

# Check if script exists
if [ ! -f "$TEMPORAL_SCRIPT" ]; then
    echo "⚠️  Temporal sync script not found: $TEMPORAL_SCRIPT"
    exit 0
fi

# Check if Python3 is available
if ! command -v python3 &> /dev/null; then
    echo "⚠️  Python3 not found - skipping temporal sync"
    exit 0
fi

echo "🌀 Post-commit: Running temporal document sync..."

# Run temporal sync in hook mode (enables commit filtering)
python3 "$TEMPORAL_SCRIPT" --hook-mode || {
    echo "⚠️  Temporal sync failed - continuing anyway"
    echo "   Check logs for details"
}

echo "✅ Post-commit hook completed"
'''
    
    def create_pre_push_hook(self) -> str:
        """Create pre-push hook for batch processing"""
        return '''#!/bin/bash
# Pre-push hook for Lexigōn temporal automation batch processing
# Generated by Paneudaemonium hooks installer

set -e

# Get repository root  
REPO_ROOT="$(git rev-parse --show-toplevel)"

# Path to commit throttle script
THROTTLE_SCRIPT="$REPO_ROOT/Paneudaemonium/scripts/util/commit_throttle.py"

# Check if script exists
if [ ! -f "$THROTTLE_SCRIPT" ]; then
    echo "⚠️  Throttle script not found: $THROTTLE_SCRIPT"
    exit 0
fi

# Check if Python3 is available
if ! command -v python3 &> /dev/null; then
    echo "⚠️  Python3 not found - skipping batch processing"
    exit 0
fi

echo "📦 Pre-push: Processing any batched temporal updates..."

# Process batch files
python3 "$THROTTLE_SCRIPT" --batch || {
    echo "⚠️  Batch processing failed - continuing anyway"
}

echo "✅ Pre-push hook completed"
'''
    
    def create_commit_msg_hook(self) -> str:
        """Create commit-msg hook for filtering validation"""
        return '''#!/bin/bash
# Commit-msg hook for temporal automation filtering
# Generated by Paneudaemonium hooks installer

COMMIT_MSG_FILE="$1"
REPO_ROOT="$(git rev-parse --show-toplevel)"

# Path to commit filter script
FILTER_SCRIPT="$REPO_ROOT/Paneudaemonium/scripts/util/commit_filter.py"

# Check if script exists
if [ ! -f "$FILTER_SCRIPT" ]; then
    # No filter script, allow commit
    exit 0
fi

# Check if Python3 is available
if ! command -v python3 &> /dev/null; then
    # No Python3, allow commit
    exit 0
fi

# Read the commit message
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# Check if this is a temporal automation commit that should be filtered
echo "$COMMIT_MSG" | grep -q "\\[skip-temporal\\]" && {
    echo "🚫 Temporal automation will be skipped for this commit"
    exit 0
}

# Check for force override flags
echo "$COMMIT_MSG" | grep -q "\\[force-large-changes\\]" && {
    echo "✅ Large changes override detected"
    exit 0
}

exit 0
'''
    
    def install_hook(self, hook_name: str, hook_content: str, backup: bool = True) -> bool:
        """
        Install a git hook with optional backup
        
        Args:
            hook_name: Name of the hook (e.g., 'post-commit')
            hook_content: Shell script content for the hook
            backup: Whether to backup existing hook
            
        Returns:
            True if installation successful
        """
        hook_path = self.hooks_dir / hook_name
        
        try:
            # Backup existing hook if requested
            if backup and hook_path.exists():
                backup_path = self.hooks_dir / f"{hook_name}.backup"
                hook_path.rename(backup_path)
                print(f"📄 Backed up existing hook: {backup_path}")
            
            # Write new hook
            hook_path.write_text(hook_content)
            
            # Make executable
            current_mode = hook_path.stat().st_mode
            hook_path.chmod(current_mode | stat.S_IEXEC)
            
            print(f"✅ Installed hook: {hook_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to install {hook_name}: {e}")
            return False
    
    def install_all_hooks(self, backup: bool = True) -> Dict[str, bool]:
        """
        Install all temporal automation hooks
        
        Args:
            backup: Whether to backup existing hooks
            
        Returns:
            Dictionary mapping hook names to installation success
        """
        hooks = {
            "post-commit": self.create_post_commit_hook(),
            "pre-push": self.create_pre_push_hook(),
            "commit-msg": self.create_commit_msg_hook()
        }
        
        results = {}
        
        print(f"🪝 Installing temporal automation hooks in {self.hooks_dir}")
        
        for hook_name, hook_content in hooks.items():
            results[hook_name] = self.install_hook(hook_name, hook_content, backup)
        
        return results
    
    def uninstall_hooks(self, restore_backups: bool = True) -> Dict[str, bool]:
        """
        Uninstall temporal automation hooks
        
        Args:
            restore_backups: Whether to restore backup files
            
        Returns:
            Dictionary mapping hook names to uninstall success
        """
        hook_names = ["post-commit", "pre-push", "commit-msg"]
        results = {}
        
        print(f"🗑️  Uninstalling temporal automation hooks from {self.hooks_dir}")
        
        for hook_name in hook_names:
            hook_path = self.hooks_dir / hook_name
            backup_path = self.hooks_dir / f"{hook_name}.backup"
            
            try:
                # Remove current hook if it exists
                if hook_path.exists():
                    hook_path.unlink()
                    print(f"🗑️  Removed hook: {hook_name}")
                
                # Restore backup if requested and available
                if restore_backups and backup_path.exists():
                    backup_path.rename(hook_path)
                    print(f"📄 Restored backup: {hook_name}")
                
                results[hook_name] = True
                
            except Exception as e:
                print(f"❌ Failed to uninstall {hook_name}: {e}")
                results[hook_name] = False
        
        return results
    
    def check_hook_status(self) -> Dict[str, Dict]:
        """Check status of all temporal automation hooks"""
        hook_names = ["post-commit", "pre-push", "commit-msg"]
        status = {}
        
        for hook_name in hook_names:
            hook_path = self.hooks_dir / hook_name
            backup_path = self.hooks_dir / f"{hook_name}.backup"
            
            hook_status = {
                "installed": hook_path.exists(),
                "executable": False,
                "backup_exists": backup_path.exists(),
                "size": 0
            }
            
            if hook_path.exists():
                stat_info = hook_path.stat()
                hook_status["executable"] = bool(stat_info.st_mode & stat.S_IEXEC)
                hook_status["size"] = stat_info.st_size
                
                # Check if it's our hook by looking for our signature
                try:
                    content = hook_path.read_text()
                    hook_status["is_temporal_hook"] = "Paneudaemonium" in content
                except:
                    hook_status["is_temporal_hook"] = False
            
            status[hook_name] = hook_status
        
        return status
    
    def create_cron_job(self) -> str:
        """Create cron job for scheduled batch processing"""
        cron_command = f"""# Lexigōn temporal automation batch processing
# Runs every hour to process batched updates
0 * * * * cd {self.repo_root} && python3 Paneudaemonium/scripts/util/commit_throttle.py --batch >/dev/null 2>&1

# Cleanup stale locks daily at 2 AM
0 2 * * * cd {self.repo_root} && python3 Paneudaemonium/scripts/util/lockfile_manager.py --cleanup >/dev/null 2>&1
"""
        return cron_command


def main():
    """CLI interface for git hooks installer"""
    parser = argparse.ArgumentParser(description="🪝 Git Hooks Installer")
    parser.add_argument("--install", action="store_true", help="Install temporal automation hooks")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall temporal automation hooks")
    parser.add_argument("--status", action="store_true", help="Check hook installation status")
    parser.add_argument("--no-backup", action="store_true", help="Don't backup existing hooks")
    parser.add_argument("--cron", action="store_true", help="Show cron job configuration")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root).resolve()
    
    try:
        installer = GitHooksInstaller(repo_root)
    except ValueError as e:
        print(f"❌ {e}")
        exit(1)
    
    if args.install:
        results = installer.install_all_hooks(backup=not args.no_backup)
        success_count = sum(results.values())
        total_count = len(results)
        
        if success_count == total_count:
            print(f"✅ All {total_count} hooks installed successfully")
        else:
            print(f"⚠️  {success_count}/{total_count} hooks installed")
            exit(1)
    
    elif args.uninstall:
        results = installer.uninstall_hooks(restore_backups=not args.no_backup)
        success_count = sum(results.values())
        total_count = len(results)
        
        if success_count == total_count:
            print(f"✅ All {total_count} hooks uninstalled successfully")
        else:
            print(f"⚠️  {success_count}/{total_count} hooks uninstalled")
            exit(1)
    
    elif args.status:
        status = installer.check_hook_status()
        print("🪝 Hook Installation Status:")
        
        for hook_name, hook_info in status.items():
            installed = "✅" if hook_info["installed"] else "❌"
            executable = "✅" if hook_info["executable"] else "❌"
            is_ours = "✅" if hook_info.get("is_temporal_hook", False) else "❓"
            backup = "📄" if hook_info["backup_exists"] else "  "
            
            print(f"  {hook_name}:")
            print(f"    Installed: {installed}")
            print(f"    Executable: {executable}")
            print(f"    Temporal Hook: {is_ours}")
            print(f"    Backup: {backup}")
            print(f"    Size: {hook_info['size']} bytes")
    
    elif args.cron:
        cron_config = installer.create_cron_job()
        print("⏰ Cron Job Configuration:")
        print(cron_config)
        print("\nTo install, run: crontab -e")
        print("Then add the above lines to your crontab")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()