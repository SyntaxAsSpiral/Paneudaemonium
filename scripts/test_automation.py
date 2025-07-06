#!/usr/bin/env python3
"""
🧪 Temporal Automation Test Suite
Simple test suite to validate the temporal automation system components.
Tests phase awareness, exclusion rules, lockfile management, and integration.
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta
import json

# Add utils to path
sys.path.append(str(Path(__file__).parent / "util"))

from phase_metrics import PhaseScheduler, PhaseAwareConfig
from manual_exclusions import ManualExclusionEngine
from lockfile_manager import LockfileManager
from commit_filter import CommitFilter
from commit_throttle import CommitThrottle
from dry_run_diff import DryRunDiff

class AutomationTester:
    """Test suite for temporal automation components"""
    
    def __init__(self):
        self.test_results = []
        self.temp_dir = Path(tempfile.mkdtemp(prefix="temporal_test_"))
        self.bridge_dir = self.temp_dir / "test_bridge"
        self.bridge_dir.mkdir()
        
        # Create minimal test files
        self._setup_test_files()
    
    def _setup_test_files(self):
        """Create minimal test files for testing"""
        # Create a basic phasemetrics file
        phasemetrics_content = """# Test Phasemetrics
        
## Weekly Rhythm
- **Monday**: Foundation setting
- **Tuesday**: Invocation work
- **Wednesday**: Deep diving
- **Thursday**: Integration focus
- **Friday**: Creative expression
- **Weekend**: Rest and renewal

## Monthly Cycles
- **New Moon**: Seeding intentions
- **Waxing**: Building energy
- **Full Moon**: Peak working
- **Waning**: Release and integration
"""
        (self.bridge_dir / "doc_phasemetrics.md").write_text(phasemetrics_content)
        
        # Create test status file
        status_content = """# Current Development Status

**Last Updated:** 2025-01-01

## Test Status
<!-- AUTO-PHASE-START -->
This section will be auto-updated
<!-- AUTO-PHASE-END -->

Manual content here.
"""
        (self.bridge_dir / "current_development_status.md").write_text(status_content)
        
        # Create protected file
        protected_content = """# Process Infinite Loop

This file should never be auto-modified.
"""
        (self.bridge_dir / "process_infinite_loop.md").write_text(protected_content)
    
    def log_test(self, test_name: str, success: bool, message: str):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def test_phase_scheduler(self):
        """Test phase-aware scheduling"""
        try:
            scheduler = PhaseScheduler(self.bridge_dir)
            
            # Test phase detection
            lunar_phase = scheduler.get_lunar_phase()
            weekly_phase = scheduler.get_weekly_phase()
            
            self.log_test(
                "Phase Detection",
                lunar_phase and weekly_phase,
                f"Detected {lunar_phase.value} lunar, {weekly_phase.value} weekly"
            )
            
            # Test optimal window checking
            is_optimal, reason = scheduler.is_optimal_window("heavy_report")
            
            self.log_test(
                "Optimal Window Check",
                True,  # Always pass, just testing it runs
                f"Heavy report optimal: {is_optimal} ({reason})"
            )
            
            # Test phase context
            context = scheduler.get_phase_context()
            
            self.log_test(
                "Phase Context",
                "lunar_phase" in context and "weekly_phase" in context,
                f"Context generated with {len(context)} fields"
            )
            
        except Exception as e:
            self.log_test("Phase Scheduler", False, f"Error: {e}")
    
    def test_manual_exclusions(self):
        """Test manual exclusion rules"""
        try:
            engine = ManualExclusionEngine(self.bridge_dir)
            
            # Test protected file exclusion
            protected_file = self.bridge_dir / "process_infinite_loop.md"
            is_excluded, reason = engine.is_excluded(protected_file)
            
            self.log_test(
                "Protected File Exclusion",
                is_excluded,
                f"process_infinite_loop.md: {reason}"
            )
            
            # Test allowed temporal file
            status_file = self.bridge_dir / "current_development_status.md"
            is_excluded, reason = engine.is_excluded(status_file)
            
            self.log_test(
                "Temporal File Allowed",
                not is_excluded,
                f"current_development_status.md: {reason}"
            )
            
            # Test file filtering
            test_files = [protected_file, status_file]
            modifiable, excluded = engine.get_modifiable_files(test_files)
            
            self.log_test(
                "File Filtering",
                len(modifiable) == 1 and len(excluded) == 1,
                f"Filtered {len(test_files)} files: {len(modifiable)} modifiable, {len(excluded)} excluded"
            )
            
        except Exception as e:
            self.log_test("Manual Exclusions", False, f"Error: {e}")
    
    def test_lockfile_manager(self):
        """Test lockfile management"""
        try:
            manager = LockfileManager("test_lock", self.temp_dir)
            
            # Test lock acquisition
            success, message = manager.acquire_lock()
            
            self.log_test(
                "Lock Acquisition",
                success,
                message
            )
            
            # Test lock status
            if success:
                info = manager.get_lock_info()
                
                self.log_test(
                    "Lock Status Check",
                    info["status"] == "valid",
                    f"Lock status: {info['status']}"
                )
                
                # Test lock release
                success, message = manager.release_lock()
                
                self.log_test(
                    "Lock Release",
                    success,
                    message
                )
            
        except Exception as e:
            self.log_test("Lockfile Manager", False, f"Error: {e}")
    
    def test_commit_filter(self):
        """Test commit filtering"""
        try:
            filter_engine = CommitFilter()
            
            # Test automation context detection
            is_automation, reason = filter_engine.is_automation_context()
            
            self.log_test(
                "Automation Context",
                True,  # Always pass, just testing it runs
                f"Automation detected: {is_automation} ({reason})"
            )
            
            # Test bot author detection
            bot_skip, bot_reason = filter_engine._check_author_filter("claudi-bot <claudi@example.com>")
            
            self.log_test(
                "Bot Author Detection",
                bot_skip,
                f"Bot author filtered: {bot_reason}"
            )
            
            # Test human author
            human_skip, human_reason = filter_engine._check_author_filter("John Doe <john@example.com>")
            
            self.log_test(
                "Human Author Allowed",
                not human_skip,
                f"Human author allowed: {human_reason}"
            )
            
            # Test skip message detection
            skip_msg, skip_reason = filter_engine._check_message_filter("Fix bug [skip-temporal]")
            
            self.log_test(
                "Skip Message Detection",
                skip_msg,
                f"Skip flag detected: {skip_reason}"
            )
            
        except Exception as e:
            self.log_test("Commit Filter", False, f"Error: {e}")
    
    def test_commit_throttle(self):
        """Test commit throttling"""
        try:
            throttle = CommitThrottle(self.temp_dir, max_commits_per_hour=3)
            
            # Test initial status
            is_throttled, reason, _ = throttle.check_throttle_status()
            
            self.log_test(
                "Initial Throttle Status",
                not is_throttled,
                f"Initial status: {reason}"
            )
            
            # Test commit recording
            for i in range(2):
                success = throttle.record_commit(f"test_commit_{i}", "test_author", f"Test commit {i}")
                
                self.log_test(
                    f"Record Commit {i+1}",
                    success,
                    f"Commit {i+1} recorded: {success}"
                )
            
            # Check throttle stats
            stats = throttle.get_throttle_stats()
            
            self.log_test(
                "Throttle Stats",
                stats["current_count"] == 2,
                f"Recorded {stats['current_count']} commits"
            )
            
        except Exception as e:
            self.log_test("Commit Throttle", False, f"Error: {e}")
    
    def test_dry_run_diff(self):
        """Test dry-run diff analysis"""
        try:
            differ = DryRunDiff(self.temp_dir, max_lines_threshold=10)
            
            # Test small change
            original = "Line 1\nLine 2\nLine 3"
            small_change = "Line 1\nLine 2 modified\nLine 3"
            
            analysis = differ.analyze_changes(original, small_change, "test_file.txt")
            
            self.log_test(
                "Small Change Analysis",
                not analysis["exceeds_threshold"],
                f"Small change: {analysis['total_changes']} lines"
            )
            
            # Test large change
            large_original = "\n".join([f"Line {i}" for i in range(20)])
            large_change = "\n".join([f"Modified Line {i}" for i in range(20)])
            
            large_analysis = differ.analyze_changes(large_original, large_change, "large_file.txt")
            
            self.log_test(
                "Large Change Detection",
                large_analysis["exceeds_threshold"],
                f"Large change: {large_analysis['total_changes']} lines (threshold: {large_analysis['threshold']})"
            )
            
        except Exception as e:
            self.log_test("Dry Run Diff", False, f"Error: {e}")
    
    def test_integration(self):
        """Test basic integration between components"""
        try:
            # Test phase-aware config
            config = PhaseAwareConfig(self.temp_dir / "test_config.json")
            
            self.log_test(
                "Phase Config Creation",
                config.is_phase_awareness_enabled(),
                "Phase awareness config created"
            )
            
            # Test exclusion + phase scheduling integration
            scheduler = PhaseScheduler(self.bridge_dir)
            exclusion_engine = ManualExclusionEngine(self.bridge_dir)
            
            # Get modifiable files and check phase timing
            test_files = list(self.bridge_dir.glob("*.md"))
            modifiable, excluded = exclusion_engine.get_modifiable_files(test_files)
            
            is_optimal, reason = scheduler.is_optimal_window("light_update")
            
            self.log_test(
                "Integration Test",
                len(modifiable) > 0,
                f"Found {len(modifiable)} modifiable files, phase optimal: {is_optimal}"
            )
            
        except Exception as e:
            self.log_test("Integration", False, f"Error: {e}")
    
    def run_all_tests(self):
        """Run all test suites"""
        print(f"🧪 Starting Temporal Automation Test Suite")
        print(f"   Test directory: {self.temp_dir}")
        
        # Run all tests
        self.test_phase_scheduler()
        self.test_manual_exclusions()
        self.test_lockfile_manager()
        self.test_commit_filter()
        self.test_commit_throttle()
        self.test_dry_run_diff()
        self.test_integration()
        
        # Summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 Test Summary:")
        print(f"   Total: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test']}: {result['message']}")
        
        # Save test report
        report_path = self.temp_dir / "test_report.json"
        with open(report_path, 'w') as f:
            json.dump({
                "summary": {
                    "total": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "success_rate": passed_tests / total_tests if total_tests > 0 else 0
                },
                "results": self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Test report saved: {report_path}")
        
        return failed_tests == 0
    
    def cleanup(self):
        """Clean up test files"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
            print(f"🧹 Cleaned up test directory: {self.temp_dir}")
        except Exception as e:
            print(f"⚠️  Cleanup failed: {e}")


def main():
    """CLI interface for test suite"""
    import argparse
    
    parser = argparse.ArgumentParser(description="🧪 Temporal Automation Test Suite")
    parser.add_argument("--keep-files", action="store_true", help="Keep test files after completion")
    
    args = parser.parse_args()
    
    tester = AutomationTester()
    
    try:
        success = tester.run_all_tests()
        
        if not args.keep_files:
            tester.cleanup()
        
        exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
        if not args.keep_files:
            tester.cleanup()
        exit(1)
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        if not args.keep_files:
            tester.cleanup()
        exit(1)


if __name__ == "__main__":
    main()