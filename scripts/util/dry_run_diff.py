#!/usr/bin/env python3
"""
🧪 Dry-Run Diff Utility
Implements dry-run diff for large changes (>100 LOC) with CI failure mechanism.
Prevents automation from making massive changes without human review.
"""

import os
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
import difflib

class DryRunDiff:
    """Dry-run diff analyzer for large changes"""
    
    def __init__(self, repo_root: Path = None, max_lines_threshold: int = 100):
        self.repo_root = repo_root or Path.cwd()
        self.max_lines_threshold = max_lines_threshold
        self.diff_dir = self.repo_root / "tmp" / "diffs"
        self.diff_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_changes(self, original_content: str, proposed_content: str, 
                       file_path: str = "unknown") -> Dict:
        """
        Analyze differences between original and proposed content
        
        Args:
            original_content: Original file content
            proposed_content: Proposed new content
            file_path: Path to file being analyzed
            
        Returns:
            Dictionary with analysis results
        """
        # Generate unified diff
        diff_lines = list(difflib.unified_diff(
            original_content.splitlines(keepends=True),
            proposed_content.splitlines(keepends=True),
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm=''
        ))
        
        # Count changes
        additions = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
        deletions = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
        total_changes = additions + deletions
        
        # Analyze change patterns
        change_patterns = self._analyze_change_patterns(diff_lines)
        
        # Check if changes exceed threshold
        exceeds_threshold = total_changes > self.max_lines_threshold
        
        return {
            "file_path": file_path,
            "total_changes": total_changes,
            "additions": additions,
            "deletions": deletions,
            "exceeds_threshold": exceeds_threshold,
            "threshold": self.max_lines_threshold,
            "diff_lines": diff_lines,
            "change_patterns": change_patterns,
            "analysis_timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _analyze_change_patterns(self, diff_lines: List[str]) -> Dict:
        """Analyze patterns in the diff to understand the nature of changes"""
        patterns = {
            "mass_deletion": 0,
            "mass_addition": 0,
            "whitespace_only": 0,
            "comment_changes": 0,
            "structural_changes": 0,
            "data_changes": 0
        }
        
        consecutive_deletions = 0
        consecutive_additions = 0
        
        for line in diff_lines:
            if line.startswith('-') and not line.startswith('---'):
                consecutive_deletions += 1
                consecutive_additions = 0
                
                # Check for comment changes
                if line.strip().startswith('-#') or line.strip().startswith('-<!--'):
                    patterns["comment_changes"] += 1
                
                # Check for whitespace-only changes
                if line.strip() == '-' or line[1:].strip() == '':
                    patterns["whitespace_only"] += 1
                
            elif line.startswith('+') and not line.startswith('+++'):
                consecutive_additions += 1
                consecutive_deletions = 0
                
                # Check for comment changes
                if line.strip().startswith('+#') or line.strip().startswith('+<!--'):
                    patterns["comment_changes"] += 1
                
                # Check for whitespace-only changes
                if line.strip() == '+' or line[1:].strip() == '':
                    patterns["whitespace_only"] += 1
                
            else:
                # End of consecutive runs
                if consecutive_deletions >= 10:
                    patterns["mass_deletion"] += 1
                if consecutive_additions >= 10:
                    patterns["mass_addition"] += 1
                
                consecutive_deletions = 0
                consecutive_additions = 0
        
        # Check final consecutive runs
        if consecutive_deletions >= 10:
            patterns["mass_deletion"] += 1
        if consecutive_additions >= 10:
            patterns["mass_addition"] += 1
        
        return patterns
    
    def create_diff_report(self, analysis: Dict) -> str:
        """Create a comprehensive diff report"""
        report = f"""# 🧪 Dry-Run Diff Report
        
**File:** {analysis['file_path']}  
**Generated:** {analysis['analysis_timestamp']}  
**Total Changes:** {analysis['total_changes']} lines  
**Threshold:** {analysis['threshold']} lines  
**Exceeds Threshold:** {'⚠️  YES' if analysis['exceeds_threshold'] else '✅ NO'}  

## Change Summary

- **Additions:** {analysis['additions']} lines
- **Deletions:** {analysis['deletions']} lines  
- **Net Change:** {analysis['additions'] - analysis['deletions']} lines

## Change Patterns

"""
        
        patterns = analysis['change_patterns']
        if patterns['mass_deletion']:
            report += f"- ⚠️  Mass deletions detected: {patterns['mass_deletion']} blocks\n"
        if patterns['mass_addition']:
            report += f"- ⚠️  Mass additions detected: {patterns['mass_addition']} blocks\n"
        if patterns['whitespace_only']:
            report += f"- ℹ️  Whitespace-only changes: {patterns['whitespace_only']} lines\n"
        if patterns['comment_changes']:
            report += f"- ℹ️  Comment changes: {patterns['comment_changes']} lines\n"
        
        if analysis['exceeds_threshold']:
            report += f"""
## ⚠️  Threshold Exceeded

This change exceeds the {analysis['threshold']}-line threshold and requires manual review.

### Recommended Actions:
1. Review the full diff below
2. Verify changes align with intended modifications
3. Check for unintended mass changes
4. If approved, re-run with --force flag
5. If rejected, investigate automation logic

"""
        
        report += """
## Full Diff

```diff
"""
        
        # Add first 200 lines of diff to avoid huge reports
        diff_lines = analysis['diff_lines'][:200]
        for line in diff_lines:
            report += line
        
        if len(analysis['diff_lines']) > 200:
            report += f"\n... (truncated, {len(analysis['diff_lines']) - 200} more lines)\n"
        
        report += """```

---
*Generated by Paneudaemonium Dry-Run Diff Utility*
"""
        
        return report
    
    def save_diff_report(self, analysis: Dict, filename: str = None) -> Path:
        """Save diff report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = analysis['file_path'].replace('/', '_').replace('\\', '_')
            filename = f"diff_{safe_filename}_{timestamp}.md"
        
        report_path = self.diff_dir / filename
        report_content = self.create_diff_report(analysis)
        
        try:
            report_path.write_text(report_content)
            print(f"📄 Diff report saved: {report_path}")
            return report_path
        except Exception as e:
            print(f"❌ Error saving diff report: {e}")
            raise
    
    def check_multiple_files(self, file_changes: Dict[str, Tuple[str, str]]) -> Dict:
        """
        Check multiple files for large changes
        
        Args:
            file_changes: Dict mapping file paths to (original, proposed) content tuples
            
        Returns:
            Dictionary with aggregate analysis
        """
        results = {}
        total_changes = 0
        files_exceeding_threshold = []
        
        for file_path, (original, proposed) in file_changes.items():
            analysis = self.analyze_changes(original, proposed, file_path)
            results[file_path] = analysis
            total_changes += analysis['total_changes']
            
            if analysis['exceeds_threshold']:
                files_exceeding_threshold.append(file_path)
        
        aggregate = {
            "total_files": len(file_changes),
            "total_changes": total_changes,
            "files_exceeding_threshold": files_exceeding_threshold,
            "overall_exceeds_threshold": len(files_exceeding_threshold) > 0,
            "file_results": results,
            "analysis_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return aggregate
    
    def create_ci_failure_report(self, analysis: Dict) -> str:
        """Create a CI failure report for integration"""
        if isinstance(analysis.get('file_results'), dict):
            # Multiple files analysis
            exceeding_files = analysis['files_exceeding_threshold']
            total_changes = analysis['total_changes']
            
            report = f"""❌ CI FAILURE: Large Changes Detected

**Total Changes:** {total_changes} lines across {analysis['total_files']} files
**Files Exceeding Threshold:** {len(exceeding_files)}

Files requiring review:
"""
            for file_path in exceeding_files:
                file_analysis = analysis['file_results'][file_path]
                report += f"- {file_path}: {file_analysis['total_changes']} lines\n"
            
        else:
            # Single file analysis
            report = f"""❌ CI FAILURE: Large Changes Detected

**File:** {analysis['file_path']}
**Changes:** {analysis['total_changes']} lines (threshold: {analysis['threshold']})

This automated change exceeds the safety threshold and requires manual review.
"""
        
        report += """
**Next Steps:**
1. Review the diff report in tmp/diffs/
2. Verify changes are intentional and safe
3. If approved, re-run with --force flag
4. If rejected, fix automation logic

**Override:** Add [force-large-changes] to commit message to bypass this check.
"""
        
        return report
    
    def should_fail_ci(self, analysis: Dict) -> Tuple[bool, str]:
        """
        Determine if CI should fail based on analysis
        
        Returns:
            Tuple of (should_fail, reason)
        """
        if isinstance(analysis.get('file_results'), dict):
            # Multiple files
            if analysis['files_exceeding_threshold']:
                return True, f"{len(analysis['files_exceeding_threshold'])} files exceed threshold"
        else:
            # Single file
            if analysis['exceeds_threshold']:
                return True, f"File exceeds {analysis['threshold']}-line threshold"
        
        return False, "Changes within acceptable limits"
    
    def check_force_override(self, commit_message: str = None) -> bool:
        """Check if force override is present in commit message"""
        if not commit_message:
            try:
                result = subprocess.run(
                    ['git', 'log', '-1', '--format=%B'],
                    capture_output=True, text=True, check=True
                )
                commit_message = result.stdout.strip()
            except subprocess.CalledProcessError:
                return False
        
        force_patterns = [
            r'\[force-large-changes\]',
            r'\[force-diff\]',
            r'\[override-threshold\]',
            r'\[large-changes-approved\]'
        ]
        
        import re
        for pattern in force_patterns:
            if re.search(pattern, commit_message, re.IGNORECASE):
                return True
        
        return False


def main():
    """CLI interface for dry-run diff utility"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="🧪 Dry-Run Diff Utility")
    parser.add_argument("--original", help="Original file path")
    parser.add_argument("--proposed", help="Proposed file path")
    parser.add_argument("--threshold", type=int, default=100, help="Line change threshold")
    parser.add_argument("--save-report", action="store_true", help="Save diff report")
    parser.add_argument("--ci-check", action="store_true", help="Check for CI failure")
    parser.add_argument("--force-check", action="store_true", help="Check for force override")
    
    args = parser.parse_args()
    
    differ = DryRunDiff(max_lines_threshold=args.threshold)
    
    if args.original and args.proposed:
        original_path = Path(args.original)
        proposed_path = Path(args.proposed)
        
        if not original_path.exists() or not proposed_path.exists():
            print("❌ Error: File paths do not exist")
            exit(1)
        
        original_content = original_path.read_text()
        proposed_content = proposed_path.read_text()
        
        analysis = differ.analyze_changes(
            original_content, 
            proposed_content, 
            str(original_path)
        )
        
        print(f"📊 Analysis Results:")
        print(f"   Total Changes: {analysis['total_changes']} lines")
        print(f"   Exceeds Threshold: {'YES' if analysis['exceeds_threshold'] else 'NO'}")
        
        if args.save_report:
            report_path = differ.save_diff_report(analysis)
            print(f"📄 Report saved: {report_path}")
        
        if args.ci_check:
            should_fail, reason = differ.should_fail_ci(analysis)
            if should_fail:
                print("❌ CI FAILURE RECOMMENDED")
                print(f"   Reason: {reason}")
                
                if args.force_check:
                    force_override = differ.check_force_override()
                    if force_override:
                        print("✅ Force override detected - proceeding")
                        exit(0)
                
                print(differ.create_ci_failure_report(analysis))
                exit(1)
            else:
                print("✅ CI PASS")
                exit(0)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()