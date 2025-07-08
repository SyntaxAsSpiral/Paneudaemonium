#!/usr/bin/env python3
"""
🚦 Commit Throttling Utility
Implements commit throttling mechanism with 5/hr limit using hooks/commit_count.dat.
Prevents automation from overwhelming the repository with excessive commits.
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
import fcntl

class CommitThrottle:
    """Throttling mechanism for git commits"""
    
    def __init__(self, repo_root: Path = None, max_commits_per_hour: int = 5):
        self.repo_root = repo_root or Path.cwd()
        self.hooks_dir = self.repo_root / ".git" / "hooks"
        self.count_file = self.hooks_dir / "commit_count.dat"
        self.max_commits_per_hour = max_commits_per_hour
        
        # Ensure hooks directory exists
        self.hooks_dir.mkdir(parents=True, exist_ok=True)
    
    def _read_count_data(self) -> Dict:
        """Read commit count data with file locking"""
        if not self.count_file.exists():
            return {"commits": [], "last_cleanup": datetime.now(timezone.utc).isoformat()}
        
        try:
            with open(self.count_file, 'r') as f:
                # Use file locking to prevent race conditions
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                data = json.load(f)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                return data
        except Exception as e:
            print(f"⚠️  Error reading commit count data: {e}")
            return {"commits": [], "last_cleanup": datetime.now(timezone.utc).isoformat()}
    
    def _write_count_data(self, data: Dict):
        """Write commit count data with file locking"""
        try:
            with open(self.count_file, 'w') as f:
                # Use file locking to prevent race conditions
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                json.dump(data, f, indent=2)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except Exception as e:
            print(f"⚠️  Error writing commit count data: {e}")
    
    def _cleanup_old_commits(self, data: Dict) -> Dict:
        """Remove commits older than 1 hour"""
        current_time = datetime.now(timezone.utc)
        one_hour_ago = current_time - timedelta(hours=1)
        
        # Filter out commits older than 1 hour
        recent_commits = []
        for commit in data.get("commits", []):
            try:
                commit_time = datetime.fromisoformat(commit["timestamp"].replace('Z', '+00:00'))
                if commit_time > one_hour_ago:
                    recent_commits.append(commit)
            except Exception as e:
                print(f"⚠️  Error parsing commit timestamp: {e}")
        
        data["commits"] = recent_commits
        data["last_cleanup"] = current_time.isoformat()
        return data
    
    def record_commit(self, commit_hash: str = None, author: str = None, message: str = None) -> bool:
        """
        Record a new commit and check if throttling should apply
        
        Args:
            commit_hash: Git commit hash
            author: Commit author
            message: Commit message
            
        Returns:
            True if commit was recorded, False if throttled
        """
        data = self._read_count_data()
        data = self._cleanup_old_commits(data)
        
        # Check if we're at the limit
        if len(data["commits"]) >= self.max_commits_per_hour:
            oldest_commit = min(data["commits"], key=lambda x: x["timestamp"])
            return False  # Throttled
        
        # Record new commit
        commit_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hash": commit_hash or "unknown",
            "author": author or os.getenv("GIT_AUTHOR_NAME", "unknown"),
            "message": (message or "unknown")[:100],  # Truncate long messages
            "pid": os.getpid()
        }
        
        data["commits"].append(commit_record)
        self._write_count_data(data)
        
        return True
    
    def check_throttle_status(self) -> Tuple[bool, str, Optional[datetime]]:
        """
        Check current throttle status without recording a commit
        
        Returns:
            Tuple of (is_throttled, reason, next_available_time)
        """
        data = self._read_count_data()
        data = self._cleanup_old_commits(data)
        
        current_count = len(data["commits"])
        
        if current_count >= self.max_commits_per_hour:
            # Find the oldest commit to determine when throttling expires
            oldest_commit = min(data["commits"], key=lambda x: x["timestamp"])
            oldest_time = datetime.fromisoformat(oldest_commit["timestamp"].replace('Z', '+00:00'))
            next_available = oldest_time + timedelta(hours=1)
            
            return (
                True,
                f"Throttled: {current_count}/{self.max_commits_per_hour} commits in last hour",
                next_available
            )
        
        return (
            False,
            f"OK: {current_count}/{self.max_commits_per_hour} commits in last hour",
            None
        )
    
    def get_throttle_stats(self) -> Dict:
        """Get detailed throttle statistics"""
        data = self._read_count_data()
        data = self._cleanup_old_commits(data)
        
        current_count = len(data["commits"])
        is_throttled, reason, next_available = self.check_throttle_status()
        
        # Calculate time distribution
        if data["commits"]:
            timestamps = [
                datetime.fromisoformat(c["timestamp"].replace('Z', '+00:00'))
                for c in data["commits"]
            ]
            oldest = min(timestamps)
            newest = max(timestamps)
            time_span = (newest - oldest).total_seconds() / 60  # minutes
        else:
            time_span = 0
        
        return {
            "current_count": current_count,
            "max_per_hour": self.max_commits_per_hour,
            "is_throttled": is_throttled,
            "reason": reason,
            "next_available": next_available.isoformat() if next_available else None,
            "time_span_minutes": time_span,
            "commits": data["commits"],
            "last_cleanup": data.get("last_cleanup")
        }
    
    def reset_throttle(self, force: bool = False) -> bool:
        """
        Reset throttle counters
        
        Args:
            force: Force reset even if not administrator
            
        Returns:
            True if reset successful
        """
        if not force:
            # Check if current user should be able to reset
            current_user = os.getenv("USER", "unknown")
            if current_user in ["root", "admin"]:
                force = True
        
        if not force:
            print("⚠️  Reset requires force flag or administrator privileges")
            return False
        
        try:
            empty_data = {
                "commits": [],
                "last_cleanup": datetime.now(timezone.utc).isoformat(),
                "reset_by": os.getenv("USER", "unknown"),
                "reset_at": datetime.now(timezone.utc).isoformat()
            }
            
            self._write_count_data(empty_data)
            print("✅ Throttle counters reset")
            return True
            
        except Exception as e:
            print(f"❌ Error resetting throttle: {e}")
            return False
    
    def should_batch_updates(self) -> Tuple[bool, str]:
        """
        Check if updates should be batched instead of immediate
        
        Returns:
            Tuple of (should_batch, reason)
        """
        is_throttled, reason, next_available = self.check_throttle_status()
        
        if is_throttled:
            return True, f"Throttled - batching until {next_available.strftime('%H:%M:%S')}"
        
        # Check if we're close to the limit
        stats = self.get_throttle_stats()
        if stats["current_count"] >= self.max_commits_per_hour * 0.8:  # 80% of limit
            return True, f"Close to limit ({stats['current_count']}/{self.max_commits_per_hour}) - batching recommended"
        
        return False, "No batching needed"
    
    def create_batch_file(self, batch_content: str) -> Path:
        """
        Create a batch file for deferred updates
        
        Args:
            batch_content: Content to be applied later
            
        Returns:
            Path to created batch file
        """
        batch_dir = self.hooks_dir / "batches"
        batch_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        batch_file = batch_dir / f"batch_{timestamp}.json"
        
        batch_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content": batch_content,
            "pid": os.getpid(),
            "author": os.getenv("GIT_AUTHOR_NAME", "unknown")
        }
        
        try:
            with open(batch_file, 'w') as f:
                json.dump(batch_data, f, indent=2)
            
            print(f"📦 Created batch file: {batch_file}")
            return batch_file
            
        except Exception as e:
            print(f"❌ Error creating batch file: {e}")
            raise
    
    def process_batch_files(self) -> int:
        """
        Process pending batch files if throttling allows
        
        Returns:
            Number of batch files processed
        """
        batch_dir = self.hooks_dir / "batches"
        if not batch_dir.exists():
            return 0
        
        batch_files = list(batch_dir.glob("batch_*.json"))
        if not batch_files:
            return 0
        
        # Check if we can process batches
        is_throttled, reason, _ = self.check_throttle_status()
        if is_throttled:
            print(f"🚦 Cannot process batches: {reason}")
            return 0
        
        processed = 0
        for batch_file in sorted(batch_files)[:self.max_commits_per_hour]:
            try:
                with open(batch_file, 'r') as f:
                    batch_data = json.load(f)
                
                # Process the batch content here
                # This would typically involve applying the deferred changes
                print(f"📦 Processing batch: {batch_file.name}")
                
                # Record the batch processing as a commit
                if self.record_commit(
                    commit_hash=f"batch_{batch_file.stem}",
                    author=batch_data.get("author", "batch"),
                    message=f"Batch processing: {batch_file.name}"
                ):
                    batch_file.unlink()  # Remove processed batch
                    processed += 1
                else:
                    print(f"🚦 Throttled while processing batch: {batch_file.name}")
                    break
                
            except Exception as e:
                print(f"❌ Error processing batch {batch_file}: {e}")
        
        return processed


def main():
    """CLI interface for commit throttling"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="🚦 Commit Throttle")
    parser.add_argument("--record", action="store_true", help="Record a new commit")
    parser.add_argument("--check", action="store_true", help="Check throttle status")
    parser.add_argument("--stats", action="store_true", help="Show detailed statistics")
    parser.add_argument("--reset", action="store_true", help="Reset throttle counters")
    parser.add_argument("--force", action="store_true", help="Force operations")
    parser.add_argument("--batch", action="store_true", help="Process batch files")
    parser.add_argument("--max-commits", type=int, default=5, help="Max commits per hour")
    
    args = parser.parse_args()
    
    throttle = CommitThrottle(max_commits_per_hour=args.max_commits)
    
    if args.record:
        success = throttle.record_commit()
        if success:
            print("✅ Commit recorded")
            exit(0)
        else:
            print("🚦 Commit throttled")
            exit(1)
    
    elif args.check:
        is_throttled, reason, next_available = throttle.check_throttle_status()
        print(f"🚦 Throttle Status: {'Throttled' if is_throttled else 'OK'}")
        print(f"   Reason: {reason}")
        if next_available:
            print(f"   Next available: {next_available.strftime('%H:%M:%S')}")
        
        exit(1 if is_throttled else 0)
    
    elif args.stats:
        stats = throttle.get_throttle_stats()
        print("🚦 Throttle Statistics:")
        print(json.dumps(stats, indent=2, default=str))
    
    elif args.reset:
        success = throttle.reset_throttle(force=args.force)
        exit(0 if success else 1)
    
    elif args.batch:
        processed = throttle.process_batch_files()
        print(f"📦 Processed {processed} batch files")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()