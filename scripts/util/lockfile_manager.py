#!/usr/bin/env python3
"""
🔒 Lockfile Management Utility
Implements PID + timestamp lockfile semantics with 60-minute timeout for temporal automation.
Prevents concurrent automation runs and provides clean recovery mechanisms.
"""

import os
import time
import json
import signal
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

class LockfileManager:
    """Manager for temporal automation lockfiles with PID + timestamp semantics"""
    
    def __init__(self, lock_name: str = "temporal_automation", lock_dir: Path = None):
        self.lock_name = lock_name
        self.lock_dir = lock_dir or Path.cwd() / "locks"
        self.lock_dir.mkdir(exist_ok=True)
        self.lock_file = self.lock_dir / f"{lock_name}.lock"
        self.timeout_minutes = 60
        self.current_pid = os.getpid()
        
    def acquire_lock(self, force: bool = False) -> tuple[bool, str]:
        """
        Acquire the lockfile with PID + timestamp
        
        Args:
            force: Force acquisition even if valid lock exists
            
        Returns:
            Tuple of (success, message)
        """
        # Check if lock exists and is valid
        if self.lock_file.exists() and not force:
            is_valid, reason = self._is_lock_valid()
            if is_valid:
                return False, f"Lock already held: {reason}"
            else:
                self._log(f"Cleaning stale lock: {reason}")
                self._remove_lock()
        
        # Create new lock
        lock_data = {
            "pid": self.current_pid,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hostname": os.uname().nodename,
            "command": " ".join(os.sys.argv),
            "lock_name": self.lock_name
        }
        
        try:
            with open(self.lock_file, 'w') as f:
                json.dump(lock_data, f, indent=2)
            
            self._log(f"Lock acquired: PID {self.current_pid}")
            return True, f"Lock acquired successfully"
            
        except Exception as e:
            return False, f"Failed to acquire lock: {e}"
    
    def release_lock(self) -> tuple[bool, str]:
        """
        Release the lockfile if held by current process
        
        Returns:
            Tuple of (success, message)
        """
        if not self.lock_file.exists():
            return True, "No lock to release"
        
        try:
            lock_data = self._read_lock_data()
            if lock_data and lock_data.get("pid") == self.current_pid:
                self._remove_lock()
                self._log(f"Lock released: PID {self.current_pid}")
                return True, "Lock released successfully"
            else:
                return False, "Lock not held by current process"
                
        except Exception as e:
            return False, f"Failed to release lock: {e}"
    
    def _is_lock_valid(self) -> tuple[bool, str]:
        """
        Check if existing lock is valid (process alive and within timeout)
        
        Returns:
            Tuple of (is_valid, reason)
        """
        try:
            lock_data = self._read_lock_data()
            if not lock_data:
                return False, "Invalid lock data"
            
            lock_pid = lock_data.get("pid")
            lock_timestamp = lock_data.get("timestamp")
            
            if not lock_pid or not lock_timestamp:
                return False, "Missing PID or timestamp"
            
            # Check if process is still alive
            if not self._is_process_alive(lock_pid):
                return False, f"Process {lock_pid} no longer exists"
            
            # Check timeout
            lock_time = datetime.fromisoformat(lock_timestamp.replace('Z', '+00:00'))
            age_minutes = (datetime.now(timezone.utc) - lock_time).total_seconds() / 60
            
            if age_minutes > self.timeout_minutes:
                return False, f"Lock expired: {age_minutes:.1f} minutes old (timeout: {self.timeout_minutes})"
            
            return True, f"Valid lock held by PID {lock_pid} for {age_minutes:.1f} minutes"
            
        except Exception as e:
            return False, f"Error checking lock validity: {e}"
    
    def _read_lock_data(self) -> Optional[Dict[str, Any]]:
        """Read lock data from file"""
        try:
            if not self.lock_file.exists():
                return None
            
            with open(self.lock_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            self._log(f"Error reading lock file: {e}")
            return None
    
    def _is_process_alive(self, pid: int) -> bool:
        """Check if process with given PID is still alive"""
        if HAS_PSUTIL:
            try:
                return psutil.pid_exists(pid)
            except Exception:
                pass
        
        # Fallback to OS-level check
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False
    
    def _remove_lock(self):
        """Remove lock file"""
        try:
            if self.lock_file.exists():
                self.lock_file.unlink()
        except Exception as e:
            self._log(f"Error removing lock file: {e}")
    
    def _log(self, message: str):
        """Log lockfile operations"""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(f"🔒 [{timestamp}] {message}")
    
    def get_lock_info(self) -> Dict[str, Any]:
        """Get information about current lock"""
        if not self.lock_file.exists():
            return {"status": "no_lock", "message": "No lock file exists"}
        
        lock_data = self._read_lock_data()
        if not lock_data:
            return {"status": "invalid_lock", "message": "Lock file is corrupted"}
        
        is_valid, reason = self._is_lock_valid()
        
        return {
            "status": "valid" if is_valid else "stale",
            "message": reason,
            "lock_data": lock_data,
            "lock_file": str(self.lock_file)
        }
    
    def cleanup_stale_locks(self) -> tuple[int, list]:
        """
        Cleanup all stale locks in the lock directory
        
        Returns:
            Tuple of (cleaned_count, cleanup_messages)
        """
        cleaned_count = 0
        messages = []
        
        for lock_file in self.lock_dir.glob("*.lock"):
            try:
                # Create temporary manager for this lock
                temp_manager = LockfileManager(
                    lock_name=lock_file.stem,
                    lock_dir=self.lock_dir
                )
                
                if lock_file.exists():
                    is_valid, reason = temp_manager._is_lock_valid()
                    if not is_valid:
                        temp_manager._remove_lock()
                        cleaned_count += 1
                        messages.append(f"Cleaned {lock_file.name}: {reason}")
                        
            except Exception as e:
                messages.append(f"Error checking {lock_file.name}: {e}")
        
        return cleaned_count, messages


class LockfileContextManager:
    """Context manager for automatic lock acquisition and release"""
    
    def __init__(self, lock_name: str = "temporal_automation", force: bool = False):
        self.manager = LockfileManager(lock_name)
        self.force = force
        self.acquired = False
    
    def __enter__(self):
        success, message = self.manager.acquire_lock(force=self.force)
        if not success:
            raise RuntimeError(f"Failed to acquire lock: {message}")
        
        self.acquired = True
        return self.manager
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.acquired:
            self.manager.release_lock()


def main():
    """CLI interface for lockfile management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="🔒 Lockfile Manager")
    parser.add_argument("--lock-name", default="temporal_automation", help="Name of lock")
    parser.add_argument("--acquire", action="store_true", help="Acquire lock")
    parser.add_argument("--release", action="store_true", help="Release lock")
    parser.add_argument("--status", action="store_true", help="Check lock status")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup stale locks")
    parser.add_argument("--force", action="store_true", help="Force operations")
    
    args = parser.parse_args()
    
    manager = LockfileManager(args.lock_name)
    
    if args.acquire:
        success, message = manager.acquire_lock(force=args.force)
        print(f"{'✅' if success else '❌'} {message}")
        exit(0 if success else 1)
    
    elif args.release:
        success, message = manager.release_lock()
        print(f"{'✅' if success else '❌'} {message}")
        exit(0 if success else 1)
    
    elif args.status:
        info = manager.get_lock_info()
        print(f"🔒 Lock Status: {info['status']}")
        print(f"   Message: {info['message']}")
        if info.get('lock_data'):
            lock_data = info['lock_data']
            print(f"   PID: {lock_data.get('pid')}")
            print(f"   Timestamp: {lock_data.get('timestamp')}")
            print(f"   Hostname: {lock_data.get('hostname')}")
    
    elif args.cleanup:
        cleaned_count, messages = manager.cleanup_stale_locks()
        print(f"🧹 Cleaned {cleaned_count} stale locks")
        for message in messages:
            print(f"   {message}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()