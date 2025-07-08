#!/usr/bin/env python3
"""
🌙 Phase-Aware Scheduler Module
Reads lunar/weekly markers from doc_phasemetrics.md and schedules temporal document updates
based on optimal ritual timing windows.

Integrates with temporal_doc_sync.py to honor the natural rhythms of development.
"""

import os
import re
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum
import calendar

class LunarPhase(Enum):
    """Lunar phase enumeration based on phasemetrics"""
    NEW_MOON = "new_moon"          # Seeding intentions
    WAXING = "waxing"              # Building energy
    FULL_MOON = "full_moon"        # Peak working
    WANING = "waning"              # Release and integration

class WeeklyPhase(Enum):
    """Weekly rhythm phases from phasemetrics"""
    MONDAY = "foundation"          # Foundation setting
    TUESDAY = "invocation"         # Invocation work
    WEDNESDAY = "deep_diving"      # Deep diving
    THURSDAY = "integration"       # Integration focus
    FRIDAY = "creative"            # Creative expression
    WEEKEND = "renewal"            # Rest and renewal

class PhaseScheduler:
    """Phase-aware scheduler for temporal document updates"""
    
    def __init__(self, bridge_root: Path):
        self.bridge_root = bridge_root
        self.phasemetrics_path = bridge_root / "doc_phasemetrics.md"
        self.current_time = datetime.now(timezone.utc)
        
    def get_lunar_phase(self, date: datetime = None) -> LunarPhase:
        """
        Calculate current lunar phase based on simplified lunar calendar
        Note: This is a simplified implementation. For production, consider using
        astronomical libraries like pyephem or skyfield.
        """
        if date is None:
            date = self.current_time
            
        # Simplified lunar phase calculation (29.5 day cycle)
        # Using a known new moon date as reference
        reference_new_moon = datetime(2024, 1, 11, tzinfo=timezone.utc)
        days_since_reference = (date - reference_new_moon).days
        lunar_cycle_position = (days_since_reference % 29.5) / 29.5
        
        if lunar_cycle_position < 0.125:
            return LunarPhase.NEW_MOON
        elif lunar_cycle_position < 0.375:
            return LunarPhase.WAXING
        elif lunar_cycle_position < 0.625:
            return LunarPhase.FULL_MOON
        else:
            return LunarPhase.WANING
    
    def get_weekly_phase(self, date: datetime = None) -> WeeklyPhase:
        """Get current weekly phase based on phasemetrics rhythm"""
        if date is None:
            date = self.current_time
            
        weekday = date.weekday()  # 0=Monday, 6=Sunday
        
        phase_map = {
            0: WeeklyPhase.MONDAY,     # Foundation setting
            1: WeeklyPhase.TUESDAY,    # Invocation work
            2: WeeklyPhase.WEDNESDAY,  # Deep diving
            3: WeeklyPhase.THURSDAY,   # Integration focus
            4: WeeklyPhase.FRIDAY,     # Creative expression
            5: WeeklyPhase.WEEKEND,    # Rest and renewal
            6: WeeklyPhase.WEEKEND     # Rest and renewal
        }
        
        return phase_map[weekday]
    
    def is_optimal_window(self, operation_type: str = "heavy_report") -> Tuple[bool, str]:
        """
        Determine if current time is optimal for specified operation type
        
        Args:
            operation_type: Type of operation ('heavy_report', 'light_update', 'maintenance')
            
        Returns:
            Tuple of (is_optimal, reason)
        """
        lunar_phase = self.get_lunar_phase()
        weekly_phase = self.get_weekly_phase()
        
        # Define optimal windows based on phasemetrics
        if operation_type == "heavy_report":
            # Heavy operations best during integration phases
            if weekly_phase == WeeklyPhase.THURSDAY:
                return True, "Thursday Integration phase - optimal for heavy report generation"
            elif lunar_phase == LunarPhase.WANING:
                return True, "Waning moon - optimal for release and integration work"
            else:
                return False, f"Current phase ({weekly_phase.value}, {lunar_phase.value}) not optimal for heavy reports"
                
        elif operation_type == "light_update":
            # Light updates can happen most times except rest periods
            if weekly_phase == WeeklyPhase.WEEKEND:
                return False, "Weekend renewal phase - avoiding automated updates"
            else:
                return True, f"Current phase ({weekly_phase.value}) suitable for light updates"
                
        elif operation_type == "maintenance":
            # Maintenance best during stable periods
            if weekly_phase == WeeklyPhase.MONDAY:
                return True, "Monday foundation phase - optimal for maintenance"
            elif lunar_phase == LunarPhase.NEW_MOON:
                return True, "New moon - optimal for foundation work"
            else:
                return False, f"Current phase ({weekly_phase.value}, {lunar_phase.value}) not optimal for maintenance"
        
        return False, "Unknown operation type"
    
    def get_next_optimal_window(self, operation_type: str = "heavy_report") -> Tuple[datetime, str]:
        """
        Calculate next optimal window for specified operation type
        
        Returns:
            Tuple of (next_optimal_datetime, reason)
        """
        current_date = self.current_time
        
        # Look ahead up to 14 days for next optimal window
        for days_ahead in range(1, 15):
            check_date = current_date + timedelta(days=days_ahead)
            
            # Create temporary scheduler for future date
            temp_scheduler = PhaseScheduler(self.bridge_root)
            temp_scheduler.current_time = check_date
            
            is_optimal, reason = temp_scheduler.is_optimal_window(operation_type)
            if is_optimal:
                return check_date, reason
        
        # Fallback if no optimal window found in 14 days
        fallback_date = current_date + timedelta(days=7)
        return fallback_date, "Fallback to weekly rhythm"
    
    def should_defer_operation(self, operation_type: str = "heavy_report") -> Tuple[bool, str, Optional[datetime]]:
        """
        Check if operation should be deferred based on phase timing
        
        Returns:
            Tuple of (should_defer, reason, next_optimal_time)
        """
        is_optimal, reason = self.is_optimal_window(operation_type)
        
        if is_optimal:
            return False, reason, None
        
        next_optimal, next_reason = self.get_next_optimal_window(operation_type)
        
        # Only defer if next optimal window is within reasonable time
        hours_until_optimal = (next_optimal - self.current_time).total_seconds() / 3600
        
        if hours_until_optimal <= 48:  # Within 48 hours
            return True, f"Deferring: {reason}. Next optimal: {next_reason}", next_optimal
        else:
            return False, f"Proceeding despite suboptimal timing: {reason}", None
    
    def get_phase_context(self) -> Dict:
        """Get current phase context for logging and reporting"""
        lunar_phase = self.get_lunar_phase()
        weekly_phase = self.get_weekly_phase()
        
        return {
            "timestamp": self.current_time.isoformat(),
            "lunar_phase": lunar_phase.value,
            "weekly_phase": weekly_phase.value,
            "lunar_description": self._get_lunar_description(lunar_phase),
            "weekly_description": self._get_weekly_description(weekly_phase),
            "optimal_operations": self._get_optimal_operations(lunar_phase, weekly_phase)
        }
    
    def _get_lunar_description(self, phase: LunarPhase) -> str:
        """Get description for lunar phase"""
        descriptions = {
            LunarPhase.NEW_MOON: "Seeding intentions",
            LunarPhase.WAXING: "Building energy",
            LunarPhase.FULL_MOON: "Peak working",
            LunarPhase.WANING: "Release and integration"
        }
        return descriptions[phase]
    
    def _get_weekly_description(self, phase: WeeklyPhase) -> str:
        """Get description for weekly phase"""
        descriptions = {
            WeeklyPhase.MONDAY: "Foundation setting",
            WeeklyPhase.TUESDAY: "Invocation work",
            WeeklyPhase.WEDNESDAY: "Deep diving",
            WeeklyPhase.THURSDAY: "Integration focus",
            WeeklyPhase.FRIDAY: "Creative expression",
            WeeklyPhase.WEEKEND: "Rest and renewal"
        }
        return descriptions[phase]
    
    def _get_optimal_operations(self, lunar: LunarPhase, weekly: WeeklyPhase) -> List[str]:
        """Get list of operations optimal for current phase combination"""
        operations = []
        
        # Lunar phase operations
        if lunar == LunarPhase.NEW_MOON:
            operations.extend(["maintenance", "foundation_work", "planning"])
        elif lunar == LunarPhase.WAXING:
            operations.extend(["development", "creation", "building"])
        elif lunar == LunarPhase.FULL_MOON:
            operations.extend(["peak_work", "intense_operations", "major_releases"])
        elif lunar == LunarPhase.WANING:
            operations.extend(["heavy_report", "integration", "cleanup"])
        
        # Weekly phase operations
        if weekly == WeeklyPhase.MONDAY:
            operations.extend(["foundation_setting", "planning", "setup"])
        elif weekly == WeeklyPhase.TUESDAY:
            operations.extend(["invocation", "initialization", "starting"])
        elif weekly == WeeklyPhase.WEDNESDAY:
            operations.extend(["deep_work", "complex_operations", "analysis"])
        elif weekly == WeeklyPhase.THURSDAY:
            operations.extend(["integration", "heavy_report", "synthesis"])
        elif weekly == WeeklyPhase.FRIDAY:
            operations.extend(["creative_work", "expression", "presentation"])
        elif weekly == WeeklyPhase.WEEKEND:
            operations.extend(["rest", "renewal", "light_maintenance"])
        
        return list(set(operations))  # Remove duplicates


class PhaseAwareConfig:
    """Configuration for phase-aware automation"""
    
    def __init__(self, config_path: Path = None):
        self.config_path = config_path or Path("phase_config.json")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load phase-aware configuration"""
        default_config = {
            "operation_schedules": {
                "heavy_report": {
                    "preferred_lunar": ["waning"],
                    "preferred_weekly": ["integration"],
                    "avoid_lunar": [],
                    "avoid_weekly": ["renewal"]
                },
                "light_update": {
                    "preferred_lunar": ["waxing", "full_moon"],
                    "preferred_weekly": ["foundation", "invocation", "deep_diving", "integration", "creative"],
                    "avoid_lunar": [],
                    "avoid_weekly": ["renewal"]
                },
                "maintenance": {
                    "preferred_lunar": ["new_moon"],
                    "preferred_weekly": ["foundation"],
                    "avoid_lunar": [],
                    "avoid_weekly": ["renewal"]
                }
            },
            "defer_thresholds": {
                "max_defer_hours": 48,
                "force_execute_hours": 168  # 1 week
            },
            "manual_overrides": {
                "emergency_mode": False,
                "phase_awareness_enabled": True
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                print(f"Warning: Could not load config from {self.config_path}: {e}")
        
        return default_config
    
    def save_config(self):
        """Save current configuration"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config to {self.config_path}: {e}")
    
    def is_phase_awareness_enabled(self) -> bool:
        """Check if phase awareness is enabled"""
        return self.config.get("manual_overrides", {}).get("phase_awareness_enabled", True)
    
    def is_emergency_mode(self) -> bool:
        """Check if emergency mode is active (bypasses phase timing)"""
        return self.config.get("manual_overrides", {}).get("emergency_mode", False)


def main():
    """CLI interface for phase scheduler testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="🌙 Phase-Aware Scheduler")
    parser.add_argument("--check", action="store_true", help="Check current phase")
    parser.add_argument("--operation", default="heavy_report", help="Operation type to check")
    parser.add_argument("--bridge-root", default="../Lexigon-Bridge", help="Path to Bridge repository")
    
    args = parser.parse_args()
    
    bridge_root = Path(args.bridge_root)
    scheduler = PhaseScheduler(bridge_root)
    
    if args.check:
        print("🌙 Current Phase Context:")
        context = scheduler.get_phase_context()
        print(json.dumps(context, indent=2))
        
        print(f"\n🎯 Optimal for {args.operation}:")
        is_optimal, reason = scheduler.is_optimal_window(args.operation)
        print(f"  Status: {'✅ Optimal' if is_optimal else '❌ Not optimal'}")
        print(f"  Reason: {reason}")
        
        if not is_optimal:
            should_defer, defer_reason, next_optimal = scheduler.should_defer_operation(args.operation)
            print(f"\n⏰ Should defer: {'Yes' if should_defer else 'No'}")
            print(f"  Reason: {defer_reason}")
            if next_optimal:
                print(f"  Next optimal: {next_optimal.strftime('%Y-%m-%d %H:%M:%S UTC')}")


if __name__ == "__main__":
    main()