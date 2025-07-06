#!/usr/bin/env python3
"""
🛡️ Manual Exclusion Rules
Defines files and patterns that should never be automatically modified by temporal automation.
Protects philosophical and foundational documents from automation interference.
"""

import re
from pathlib import Path
from typing import List, Dict, Set, Optional
import fnmatch

class ManualExclusionEngine:
    """Engine for managing manual-only document exclusions"""
    
    def __init__(self, bridge_root: Path):
        self.bridge_root = bridge_root
        self.exclusion_rules = self._load_exclusion_rules()
    
    def _load_exclusion_rules(self) -> Dict[str, List[str]]:
        """Load exclusion rules for different categories"""
        return {
            # Core philosophical documents - never auto-modify
            "philosophical": [
                "process_infinite_loop.md",
                "principles_lexigon.md",
                "principles_*.md",
                "doc_symbolic_recursion.md"
            ],
            
            # Template and structural documents - manual curation only
            "structural": [
                "audit_oracle_template.md",
                "prompt_*.md",
                "glossary_*.yaml",
                "guide_*.md"
            ],
            
            # Specification documents - require careful review
            "specifications": [
                "spec_*.md",
                "map_breathforms.md"
            ],
            
            # Index documents - may have auto-generated sections but headers are manual
            "protected_sections": [
                "index_*.md",
                "index_*.yaml"
            ],
            
            # System files - never modify
            "system": [
                "README.md",
                ".gitignore",
                "*.sh",
                "*.py"
            ],
            
            # Temporal documents - these ARE auto-modifiable
            "temporal_allowed": [
                "current_development_status.md",
                "spiral_versioning.md"
            ]
        }
    
    def is_excluded(self, file_path: Path) -> tuple:
        """
        Check if a file is excluded from automatic modification
        
        Args:
            file_path: Path to file to check
            
        Returns:
            Tuple of (is_excluded, reason)
        """
        relative_path = file_path.relative_to(self.bridge_root)
        filename = relative_path.name
        
        # Check temporal allowed first (these override other exclusions)
        for pattern in self.exclusion_rules["temporal_allowed"]:
            if fnmatch.fnmatch(filename, pattern):
                return False, f"Explicitly allowed temporal document: {pattern}"
        
        # Check each exclusion category
        for category, patterns in self.exclusion_rules.items():
            if category == "temporal_allowed":
                continue
                
            for pattern in patterns:
                if fnmatch.fnmatch(filename, pattern):
                    return True, f"Excluded by {category} rule: {pattern}"
        
        return False, "No exclusion rules matched"
    
    def get_modifiable_files(self, file_paths: List[Path]) -> tuple:
        """
        Filter list of files to only those that can be automatically modified
        
        Args:
            file_paths: List of file paths to filter
            
        Returns:
            Tuple of (modifiable_files, excluded_files_with_reasons)
        """
        modifiable = []
        excluded = []
        
        for file_path in file_paths:
            is_excluded, reason = self.is_excluded(file_path)
            if is_excluded:
                excluded.append((file_path, reason))
            else:
                modifiable.append(file_path)
        
        return modifiable, excluded
    
    def get_protected_sections(self, file_path: Path) -> List:
        """
        Get list of protected sections within a file that should not be auto-modified
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            List of tuples (section_name, protection_reason)
        """
        filename = file_path.name
        protected_sections = []
        
        if filename.startswith("index_"):
            # Index files have protected headers and manual sections
            protected_sections.extend([
                ("frontmatter", "Manual metadata curation"),
                ("introduction", "Manual introduction text"),
                ("navigation", "Manual navigation structure"),
                ("acknowledgment", "Manual acknowledgment text")
            ])
        
        if filename.startswith("current_development_status"):
            # Current status has some protected sections
            protected_sections.extend([
                ("document_purpose", "Manual document purpose definition"),
                ("temporal_tracking_protocol", "Manual protocol definition")
            ])
        
        if filename.startswith("spiral_versioning"):
            # Spiral versioning has protected philosophy sections
            protected_sections.extend([
                ("spiral_principle", "Manual philosophical statement"),
                ("living_document", "Manual document description")
            ])
        
        return protected_sections
    
    def create_exclusion_markers(self, content: str, file_path: Path) -> str:
        """
        Add exclusion markers to content to protect manual sections
        
        Args:
            content: File content to add markers to
            file_path: Path to file being processed
            
        Returns:
            Content with exclusion markers added
        """
        filename = file_path.name
        
        # Add markers for different file types
        if filename.startswith("index_"):
            # Protect index file headers
            content = re.sub(
                r'(# .+?)\n(.*?\n)(## .+)',
                r'\1\n<!-- MANUAL-ONLY-START -->\n\2<!-- MANUAL-ONLY-END -->\n\3',
                content,
                flags=re.DOTALL
            )
        
        elif filename == "current_development_status.md":
            # Protect protocol sections
            content = re.sub(
                r'(## 📅 Temporal Tracking Protocol.*?)(---)',
                r'<!-- MANUAL-ONLY-START -->\n\1<!-- MANUAL-ONLY-END -->\n\2',
                content,
                flags=re.DOTALL
            )
        
        elif filename == "spiral_versioning.md":
            # Protect philosophical sections
            content = re.sub(
                r'(\*\*🌀 Spiral Principle\*\*:.*?\n)',
                r'<!-- MANUAL-ONLY-START -->\n\1<!-- MANUAL-ONLY-END -->\n',
                content,
                flags=re.DOTALL
            )
        
        return content
    
    def extract_auto_sections(self, content: str) -> tuple:
        """
        Extract auto-modifiable sections from content, preserving manual sections
        
        Args:
            content: Full file content
            
        Returns:
            Tuple of (manual_sections, auto_sections)
        """
        manual_sections = []
        auto_sections = []
        
        # Split content by auto-generation markers
        auto_start_pattern = r'<!--\s*AUTO-PHASE-START\s*-->'
        auto_end_pattern = r'<!--\s*AUTO-PHASE-END\s*-->'
        
        # Find all auto-generated sections
        auto_sections_matches = re.finditer(
            f'{auto_start_pattern}(.*?){auto_end_pattern}',
            content,
            re.DOTALL
        )
        
        last_end = 0
        for match in auto_sections_matches:
            # Add manual section before this auto section
            manual_sections.append(content[last_end:match.start()])
            # Add auto section
            auto_sections.append(match.group(1))
            last_end = match.end()
        
        # Add remaining manual content
        if last_end < len(content):
            manual_sections.append(content[last_end:])
        
        return '\n'.join(manual_sections), auto_sections
    
    def validate_modification_safety(self, file_path: Path, proposed_changes: str) -> tuple:
        """
        Validate that proposed changes are safe and don't modify protected content
        
        Args:
            file_path: Path to file being modified
            proposed_changes: Proposed new content
            
        Returns:
            Tuple of (is_safe, reason)
        """
        is_excluded, exclusion_reason = self.is_excluded(file_path)
        
        if is_excluded:
            return False, f"File is excluded from modification: {exclusion_reason}"
        
        # Check if proposed changes contain manual-only markers
        if "<!-- MANUAL-ONLY-START -->" in proposed_changes:
            # Verify manual sections are preserved
            original_content = file_path.read_text() if file_path.exists() else ""
            
            # Extract manual sections from both
            manual_original = re.findall(
                r'<!-- MANUAL-ONLY-START -->(.*?)<!-- MANUAL-ONLY-END -->',
                original_content,
                re.DOTALL
            )
            manual_proposed = re.findall(
                r'<!-- MANUAL-ONLY-START -->(.*?)<!-- MANUAL-ONLY-END -->',
                proposed_changes,
                re.DOTALL
            )
            
            if manual_original != manual_proposed:
                return False, "Proposed changes would modify manual-only sections"
        
        return True, "Modification is safe"
    
    def get_exclusion_report(self) -> Dict:
        """Generate report of current exclusion rules"""
        total_patterns = sum(len(patterns) for patterns in self.exclusion_rules.values())
        
        # Count actual files affected
        affected_files = []
        if self.bridge_root.exists():
            for md_file in self.bridge_root.glob("*.md"):
                is_excluded, reason = self.is_excluded(md_file)
                if is_excluded:
                    affected_files.append((md_file.name, reason))
        
        return {
            "total_exclusion_patterns": total_patterns,
            "exclusion_categories": list(self.exclusion_rules.keys()),
            "affected_files": affected_files,
            "patterns_by_category": {
                category: len(patterns) 
                for category, patterns in self.exclusion_rules.items()
            }
        }


def main():
    """CLI interface for testing exclusion rules"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="🛡️ Manual Exclusion Rules")
    parser.add_argument("--check", help="Check if file is excluded")
    parser.add_argument("--report", action="store_true", help="Generate exclusion report")
    parser.add_argument("--bridge-root", default="../Lexigon-Bridge", help="Path to Bridge repository")
    
    args = parser.parse_args()
    
    bridge_root = Path(args.bridge_root)
    engine = ManualExclusionEngine(bridge_root)
    
    if args.check:
        file_path = bridge_root / args.check
        is_excluded, reason = engine.is_excluded(file_path)
        print(f"File: {args.check}")
        print(f"Excluded: {'Yes' if is_excluded else 'No'}")
        print(f"Reason: {reason}")
        
        if not is_excluded:
            protected_sections = engine.get_protected_sections(file_path)
            if protected_sections:
                print(f"Protected sections: {len(protected_sections)}")
                for section, reason in protected_sections:
                    print(f"  - {section}: {reason}")
    
    elif args.report:
        report = engine.get_exclusion_report()
        print("🛡️ Exclusion Rules Report:")
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()