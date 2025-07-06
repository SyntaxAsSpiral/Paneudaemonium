#!/usr/bin/env python3
"""
🚫 Commit Filtering Utility
Implements author & message filtering to prevent bot loops and honor [skip-temporal] flags.
Protects against infinite automation cycles and respects manual override signals.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone

class CommitFilter:
    """Filter for git commits to prevent automation loops"""
    
    def __init__(self):
        self.bot_author_patterns = [
            r'^claudi-bot',
            r'^claude-code',
            r'^temporal-bot',
            r'^automation-bot',
            r'@anthropic\.com$',
            r'noreply@anthropic\.com$'
        ]
        
        self.skip_message_patterns = [
            r'\[skip-temporal\]',
            r'\[no-temporal\]', 
            r'\[temporal-skip\]',
            r'\[automation-skip\]',
            r'\[manual-only\]'
        ]
        
        self.sensitive_file_patterns = [
            r'process_infinite_loop\.md$',
            r'principles_.*\.md$',
            r'.*\.py$',
            r'.*\.sh$',
            r'README\.md$'
        ]
    
    def should_skip_commit(self, commit_hash: str = "HEAD") -> Tuple[bool, str]:
        """
        Check if commit should be skipped by temporal automation
        
        Args:
            commit_hash: Git commit hash to check (default: HEAD)
            
        Returns:
            Tuple of (should_skip, reason)
        """
        try:
            # Get commit information
            commit_info = self._get_commit_info(commit_hash)
            
            # Check author filter
            author_skip, author_reason = self._check_author_filter(commit_info['author'])
            if author_skip:
                return True, author_reason
            
            # Check message filter
            message_skip, message_reason = self._check_message_filter(commit_info['message'])
            if message_skip:
                return True, message_reason
            
            # Check sensitive files
            files_skip, files_reason = self._check_sensitive_files(commit_hash)
            if files_skip:
                return True, files_reason
            
            return False, "No skip conditions matched"
            
        except Exception as e:
            return True, f"Error checking commit: {e}"
    
    def _get_commit_info(self, commit_hash: str) -> Dict[str, str]:
        """Get commit information from git"""
        try:
            # Get author name and email
            author_result = subprocess.run(
                ['git', 'log', '-1', '--format=%an <%ae>', commit_hash],
                capture_output=True, text=True, check=True
            )
            author = author_result.stdout.strip()
            
            # Get commit message
            message_result = subprocess.run(
                ['git', 'log', '-1', '--format=%B', commit_hash],
                capture_output=True, text=True, check=True
            )
            message = message_result.stdout.strip()
            
            # Get commit date
            date_result = subprocess.run(
                ['git', 'log', '-1', '--format=%ci', commit_hash],
                capture_output=True, text=True, check=True
            )
            date = date_result.stdout.strip()
            
            return {
                'author': author,
                'message': message,
                'date': date,
                'hash': commit_hash
            }
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get commit info: {e}")
    
    def _check_author_filter(self, author: str) -> Tuple[bool, str]:
        """Check if author matches bot patterns"""
        for pattern in self.bot_author_patterns:
            if re.search(pattern, author, re.IGNORECASE):
                return True, f"Author matches bot pattern '{pattern}': {author}"
        
        return False, f"Author OK: {author}"
    
    def _check_message_filter(self, message: str) -> Tuple[bool, str]:
        """Check if message contains skip flags"""
        for pattern in self.skip_message_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True, f"Message contains skip flag '{pattern}'"
        
        return False, "No skip flags in message"
    
    def _check_sensitive_files(self, commit_hash: str) -> Tuple[bool, str]:
        """Check if commit touches sensitive files that should pause automation"""
        try:
            # Get list of files changed in commit
            files_result = subprocess.run(
                ['git', 'diff', '--name-only', f'{commit_hash}~1', commit_hash],
                capture_output=True, text=True, check=True
            )
            changed_files = files_result.stdout.strip().split('\n')
            
            if not changed_files or changed_files == ['']:
                return False, "No files changed"
            
            # Check each file against sensitive patterns
            for file_path in changed_files:
                for pattern in self.sensitive_file_patterns:
                    if re.search(pattern, file_path):
                        return True, f"Sensitive file modified: {file_path} (pattern: {pattern})"
            
            return False, f"No sensitive files in {len(changed_files)} changed files"
            
        except subprocess.CalledProcessError as e:
            return True, f"Error checking changed files: {e}"
    
    def get_recent_commits(self, count: int = 10) -> List[Dict[str, str]]:
        """Get recent commits for analysis"""
        try:
            commits = []
            
            # Get recent commit hashes
            hash_result = subprocess.run(
                ['git', 'log', f'-{count}', '--format=%H'],
                capture_output=True, text=True, check=True
            )
            hashes = hash_result.stdout.strip().split('\n')
            
            for commit_hash in hashes:
                if commit_hash:
                    commit_info = self._get_commit_info(commit_hash)
                    should_skip, reason = self.should_skip_commit(commit_hash)
                    commit_info['should_skip'] = should_skip
                    commit_info['skip_reason'] = reason
                    commits.append(commit_info)
            
            return commits
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get recent commits: {e}")
    
    def check_git_environment(self) -> Dict[str, str]:
        """Check git environment variables for automation context"""
        env_vars = {
            'GIT_AUTHOR_NAME': os.getenv('GIT_AUTHOR_NAME', ''),
            'GIT_AUTHOR_EMAIL': os.getenv('GIT_AUTHOR_EMAIL', ''),
            'GIT_COMMITTER_NAME': os.getenv('GIT_COMMITTER_NAME', ''),
            'GIT_COMMITTER_EMAIL': os.getenv('GIT_COMMITTER_EMAIL', ''),
            'CI': os.getenv('CI', ''),
            'GITHUB_ACTIONS': os.getenv('GITHUB_ACTIONS', ''),
            'AUTOMATION_CONTEXT': os.getenv('AUTOMATION_CONTEXT', '')
        }
        
        return env_vars
    
    def is_automation_context(self) -> Tuple[bool, str]:
        """Check if we're running in an automation context"""
        env_vars = self.check_git_environment()
        
        # Check CI environment
        if env_vars['CI'] or env_vars['GITHUB_ACTIONS']:
            return True, "Running in CI/GitHub Actions"
        
        # Check automation-specific environment
        if env_vars['AUTOMATION_CONTEXT']:
            return True, f"Automation context: {env_vars['AUTOMATION_CONTEXT']}"
        
        # Check bot authors in environment
        author_name = env_vars['GIT_AUTHOR_NAME'] or env_vars['GIT_COMMITTER_NAME']
        author_email = env_vars['GIT_AUTHOR_EMAIL'] or env_vars['GIT_COMMITTER_EMAIL']
        
        if author_name or author_email:
            author_string = f"{author_name} <{author_email}>"
            is_bot, reason = self._check_author_filter(author_string)
            if is_bot:
                return True, f"Bot author in environment: {reason}"
        
        return False, "No automation context detected"
    
    def create_git_hook_script(self, hook_type: str = "post-commit") -> str:
        """
        Generate git hook script content with filtering
        
        Args:
            hook_type: Type of git hook (post-commit, pre-push, etc.)
            
        Returns:
            Shell script content for git hook
        """
        script_content = f'''#!/bin/bash
# {hook_type} hook with temporal automation filtering
# Generated by Paneudaemonium commit filter

# Exit immediately if any command fails
set -e

# Get the directory of this script
HOOK_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
PROJECT_ROOT="$(cd "$HOOK_DIR/../.." && pwd)"

# Path to commit filter script
FILTER_SCRIPT="$PROJECT_ROOT/Paneudaemonium/scripts/util/commit_filter.py"

# Check if filter script exists
if [ ! -f "$FILTER_SCRIPT" ]; then
    echo "⚠️  Warning: Commit filter script not found at $FILTER_SCRIPT"
    exit 0
fi

# Run commit filter check
echo "🔍 Checking commit for temporal automation skip conditions..."
python3 "$FILTER_SCRIPT" --check-current || {{
    echo "🚫 Commit filtered - skipping temporal automation"
    exit 0
}}

echo "✅ Commit passed filters - temporal automation can proceed"

# Run temporal automation here
TEMPORAL_SCRIPT="$PROJECT_ROOT/Paneudaemonium/scripts/temporal_doc_sync.py"
if [ -f "$TEMPORAL_SCRIPT" ]; then
    echo "🌀 Running temporal document sync..."
    python3 "$TEMPORAL_SCRIPT" --hook-mode || {{
        echo "⚠️  Temporal sync failed - continuing anyway"
    }}
else
    echo "⚠️  Temporal sync script not found at $TEMPORAL_SCRIPT"
fi

echo "✅ {hook_type} hook completed"
'''
        
        return script_content


def main():
    """CLI interface for commit filtering"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="🚫 Commit Filter")
    parser.add_argument("--check-current", action="store_true", help="Check current HEAD commit")
    parser.add_argument("--check-commit", help="Check specific commit hash")
    parser.add_argument("--recent", type=int, default=10, help="Check recent commits")
    parser.add_argument("--environment", action="store_true", help="Check git environment")
    parser.add_argument("--generate-hook", help="Generate git hook script")
    
    args = parser.parse_args()
    
    filter_engine = CommitFilter()
    
    if args.check_current or args.check_commit:
        commit_hash = args.check_commit or "HEAD"
        should_skip, reason = filter_engine.should_skip_commit(commit_hash)
        
        print(f"🔍 Commit: {commit_hash}")
        print(f"   Skip: {'Yes' if should_skip else 'No'}")
        print(f"   Reason: {reason}")
        
        # Exit with appropriate code for shell scripts
        exit(0 if should_skip else 1)
    
    elif args.recent:
        commits = filter_engine.get_recent_commits(args.recent)
        print(f"📜 Recent {len(commits)} commits:")
        
        for commit in commits:
            skip_indicator = "🚫" if commit['should_skip'] else "✅"
            print(f"   {skip_indicator} {commit['hash'][:8]} - {commit['author']}")
            print(f"      {commit['message'][:60]}...")
            if commit['should_skip']:
                print(f"      Skip reason: {commit['skip_reason']}")
    
    elif args.environment:
        env_vars = filter_engine.check_git_environment()
        is_automation, reason = filter_engine.is_automation_context()
        
        print("🔧 Git Environment:")
        for key, value in env_vars.items():
            if value:
                print(f"   {key}: {value}")
        
        print(f"\n🤖 Automation Context: {'Yes' if is_automation else 'No'}")
        print(f"   Reason: {reason}")
    
    elif args.generate_hook:
        hook_script = filter_engine.create_git_hook_script(args.generate_hook)
        print(f"# Git {args.generate_hook} hook script:")
        print(hook_script)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()