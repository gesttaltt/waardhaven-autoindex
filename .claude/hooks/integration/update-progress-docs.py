#!/usr/bin/env python3
"""
Progress Documentation Updater
Automatically updates project progress documentation when TODOs change
"""

import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [PROGRESS-UPDATER] %(message)s'
)
logger = logging.getLogger(__name__)

class ProgressUpdater:
    def __init__(self):
        self.project_root = Path.cwd()
        self.todo_dir = self.project_root / "docs" / "TODO-MVP"
        self.docs_dir = self.project_root / "docs"
        self.cache_dir = Path(".claude/cache")
        self.session_dir = Path(".claude/session")
        
        # Ensure directories exist
        self.cache_dir.mkdir(exist_ok=True)
    
    def analyze_todo_changes(self) -> dict:
        """Analyze recent TODO changes and progress"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'active_tasks': {},
            'completed_recently': [],
            'started_recently': [],
            'progress_metrics': {},
            'current_focus': None,
            'blockers': []
        }
        
        # Get current focus from dashboard
        dashboard_path = self.todo_dir / "README.md"
        if dashboard_path.exists():
            try:
                with open(dashboard_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract current focus
                for line in content.split('\n'):
                    if 'Working on:' in line:
                        focus = line.split('Working on:', 1)[1].strip()
                        if focus and focus != 'None':
                            analysis['current_focus'] = focus
                        break
                
                # Extract statistics
                analysis['progress_metrics'] = self._extract_dashboard_metrics(content)
                
            except Exception as e:
                logger.error(f"Error reading dashboard: {e}")
        
        # Analyze task distribution
        analysis['active_tasks'] = self._count_active_tasks()
        
        # Check recent activity from session logs
        if self.session_dir.exists():
            analysis['completed_recently'] = self._get_recent_completions()
            analysis['started_recently'] = self._get_recent_starts()
        
        return analysis
    
    def _extract_dashboard_metrics(self, content: str) -> dict:
        """Extract metrics from dashboard content"""
        metrics = {}
        
        for line in content.split('\n'):
            if 'P0 Tasks:' in line:
                metrics['p0_critical'] = self._extract_number_from_line(line)
            elif 'P1 Tasks:' in line:
                metrics['p1_core'] = self._extract_number_from_line(line)
            elif 'Bugs:' in line:
                metrics['bugs'] = self._extract_number_from_line(line)
            elif 'Tech Debt:' in line:
                metrics['tech_debt'] = self._extract_number_from_line(line, '$')
        
        return metrics
    
    def _extract_number_from_line(self, line: str, prefix: str = '') -> int:
        """Extract number from a dashboard line"""
        try:
            # Remove prefix if present
            if prefix:
                line = line.replace(prefix, '')
            
            # Extract first number found
            import re
            numbers = re.findall(r'\d+', line)
            return int(numbers[0]) if numbers else 0
        except:
            return 0
    
    def _count_active_tasks(self) -> dict:
        """Count active tasks by priority"""
        counts = {
            'P0': 0,
            'P1': 0,
            'P2': 0,
            'P3': 0,
            'BUGS': 0,
            'TECH_DEBT': 0
        }
        
        backlog_mappings = {
            'P0-CRITICAL': 'P0',
            'P1-CORE-MVP': 'P1',
            'P2-ENHANCEMENTS': 'P2',
            'P3-FUTURE': 'P3'
        }
        
        # Count backlog items
        backlog_dir = self.todo_dir / "BACKLOG"
        if backlog_dir.exists():
            for folder, priority in backlog_mappings.items():
                folder_path = backlog_dir / folder
                if folder_path.exists():
                    counts[priority] = len(list(folder_path.glob("*.md")))
        
        # Count bugs
        bugs_dir = self.todo_dir / "BUGS"
        if bugs_dir.exists():
            counts['BUGS'] = len(list(bugs_dir.glob("*.md")))
        
        # Count tech debt
        debt_dir = self.todo_dir / "TECHNICAL-DEBT"
        if debt_dir.exists():
            counts['TECH_DEBT'] = len(list(debt_dir.glob("*.md")))
        
        return counts
    
    def _get_recent_completions(self) -> list:
        """Get recently completed tasks from logs"""
        completions = []
        
        # Check for task completion logs
        activity_log = self.session_dir / "activity.log"
        if activity_log.exists():
            try:
                with open(activity_log, 'r') as f:
                    lines = f.readlines()
                
                # Look for completion entries in last 24 hours
                cutoff_time = datetime.now() - timedelta(hours=24)
                
                for line in lines:
                    if 'task-completed' in line:
                        parts = line.strip().split('|')
                        if len(parts) >= 3:
                            timestamp = datetime.fromtimestamp(int(parts[2]))
                            if timestamp > cutoff_time:
                                completions.append({
                                    'task': parts[1],
                                    'timestamp': timestamp.isoformat()
                                })
            except Exception as e:
                logger.error(f"Error reading activity log: {e}")
        
        return completions
    
    def _get_recent_starts(self) -> list:
        """Get recently started tasks from logs"""
        starts = []
        
        activity_log = self.session_dir / "activity.log"
        if activity_log.exists():
            try:
                with open(activity_log, 'r') as f:
                    lines = f.readlines()
                
                cutoff_time = datetime.now() - timedelta(hours=24)
                
                for line in lines:
                    if 'task-started' in line:
                        parts = line.strip().split('|')
                        if len(parts) >= 3:
                            timestamp = datetime.fromtimestamp(int(parts[2]))
                            if timestamp > cutoff_time:
                                starts.append({
                                    'task': parts[1],
                                    'timestamp': timestamp.isoformat()
                                })
            except Exception as e:
                logger.error(f"Error reading activity log: {e}")
        
        return starts
    
    def update_progress_documentation(self, target_file: str = None) -> str:
        """Update main progress documentation"""
        if target_file:
            progress_file = Path(target_file)
        else:
            progress_file = self.docs_dir / "PROGRESS.md"
        
        # Analyze current state
        analysis = self.analyze_todo_changes()
        
        # Generate progress content
        content = self._generate_progress_content(analysis)
        
        # Ensure parent directory exists
        progress_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write updated content
        with open(progress_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Updated progress documentation: {progress_file}")
        
        # Save analysis to cache
        analysis_file = self.cache_dir / "latest-progress-analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        return str(progress_file)
    
    def _generate_progress_content(self, analysis: dict) -> str:
        """Generate progress documentation content"""
        content = f"""# AI Investment Project Progress

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Current Status

"""
        
        # Current focus
        if analysis['current_focus']:
            content += f"🎯 **Current Focus**: {analysis['current_focus']}\n\n"
        else:
            content += "🎯 **Current Focus**: No active task\n\n"
        
        # Task overview
        content += "## Task Overview\n\n"
        
        active_tasks = analysis['active_tasks']
        total_tasks = sum(active_tasks.values())
        
        content += f"**Total Active Tasks**: {total_tasks}\n\n"
        
        # Priority breakdown
        if active_tasks['P0'] > 0:
            content += f"🚨 **P0 Critical**: {active_tasks['P0']} tasks (requires immediate attention)\n\n"
        
        if active_tasks['P1'] > 0:
            content += f"⚡ **P1 Core MVP**: {active_tasks['P1']} tasks (essential for launch)\n\n"
        
        if active_tasks['P2'] > 0:
            content += f"✨ **P2 Enhancements**: {active_tasks['P2']} tasks\n\n"
        
        if active_tasks['P3'] > 0:
            content += f"🌟 **P3 Future**: {active_tasks['P3']} tasks\n\n"
        
        if active_tasks['BUGS'] > 0:
            content += f"🐛 **Active Bugs**: {active_tasks['BUGS']}\n\n"
        
        if active_tasks['TECH_DEBT'] > 0:
            content += f"🔧 **Technical Debt**: {active_tasks['TECH_DEBT']} items\n\n"
        
        # Recent activity
        content += "## Recent Activity\n\n"
        
        if analysis['completed_recently']:
            content += "### ✅ Recently Completed\n\n"
            for completion in analysis['completed_recently']:
                date = datetime.fromisoformat(completion['timestamp']).strftime('%m-%d %H:%M')
                content += f"- {completion['task']} ({date})\n"
            content += "\n"
        
        if analysis['started_recently']:
            content += "### 🔄 Recently Started\n\n"
            for start in analysis['started_recently']:
                date = datetime.fromisoformat(start['timestamp']).strftime('%m-%d %H:%M')
                content += f"- {start['task']} ({date})\n"
            content += "\n"
        
        if not analysis['completed_recently'] and not analysis['started_recently']:
            content += "No recent activity recorded.\n\n"
        
        # Progress metrics
        if analysis['progress_metrics']:
            content += "## Progress Metrics\n\n"
            
            metrics = analysis['progress_metrics']
            
            # Calculate completion rate (rough estimate)
            if 'p0_critical' in metrics and 'p1_core' in metrics:
                critical_complete = max(0, 10 - metrics['p0_critical'])  # Assume started with ~10 P0s
                core_complete = max(0, 20 - metrics['p1_core'])  # Assume started with ~20 P1s
                
                total_critical_work = 10
                total_core_work = 20
                
                if total_critical_work > 0:
                    critical_progress = (critical_complete / total_critical_work) * 100
                    content += f"- P0 Critical Progress: {critical_progress:.0f}%\n"
                
                if total_core_work > 0:
                    core_progress = (core_complete / total_core_work) * 100
                    content += f"- P1 Core MVP Progress: {core_progress:.0f}%\n"
            
            content += "\n"
        
        # Recommendations
        content += "## Recommendations\n\n"
        
        if active_tasks['P0'] > 0:
            content += f"🚨 **Immediate Action Required**: {active_tasks['P0']} critical P0 tasks need attention\n\n"
        
        if active_tasks['BUGS'] > 0:
            content += f"🐛 **Bug Fixing**: {active_tasks['BUGS']} active bugs should be addressed\n\n"
        
        if active_tasks['P1'] > 0:
            content += f"⚡ **MVP Focus**: Focus on {active_tasks['P1']} core MVP tasks for launch readiness\n\n"
        
        if total_tasks == 0:
            content += "🎉 **Excellent**: No active tasks! Consider planning next sprint or reviewing completed work.\n\n"
        
        # Next steps
        content += "## Suggested Next Steps\n\n"
        
        if active_tasks['P0'] > 0:
            content += "1. Address all P0 critical tasks immediately\n"
        elif active_tasks['BUGS'] > 0:
            content += "1. Fix active bugs to improve system stability\n"
        elif active_tasks['P1'] > 0:
            content += "1. Continue with P1 core MVP development\n"
        else:
            content += "1. Review and plan next development phase\n"
        
        content += "2. Run comprehensive tests and quality checks\n"
        content += "3. Update documentation as needed\n"
        content += "4. Consider deployment readiness\n\n"
        
        # Footer
        content += "---\n\n"
        content += "*This document is automatically updated when TODOs change.*\n"
        content += f"*For detailed task breakdown, see [TODO Dashboard](TODO-MVP/README.md)*\n"
        
        return content
    
    def create_weekly_progress_report(self) -> str:
        """Create a weekly progress report"""
        week_start = datetime.now() - timedelta(days=7)
        
        report = f"""# Weekly Progress Report

*Week ending: {datetime.now().strftime('%Y-%m-%d')}*

## Summary

This week's development activity and task completion summary.

"""
        
        # Analyze activity from the past week
        activity_summary = self._analyze_weekly_activity(week_start)
        
        report += f"- Tasks completed: {len(activity_summary['completed'])}\n"
        report += f"- Tasks started: {len(activity_summary['started'])}\n"
        report += f"- Files modified: {activity_summary['files_modified']}\n"
        report += f"- Tools used: {activity_summary['tools_used']}\n\n"
        
        if activity_summary['completed']:
            report += "## Completed Tasks\n\n"
            for task in activity_summary['completed']:
                report += f"- {task}\n"
            report += "\n"
        
        # Save weekly report
        report_file = self.docs_dir / f"weekly-report-{datetime.now().strftime('%Y-%m-%d')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        return str(report_file)
    
    def _analyze_weekly_activity(self, week_start: datetime) -> dict:
        """Analyze activity from the past week"""
        activity = {
            'completed': [],
            'started': [],
            'files_modified': 0,
            'tools_used': 0
        }
        
        # Check session logs
        if self.session_dir.exists():
            for log_file in self.session_dir.glob("*.log"):
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                    
                    for line in lines:
                        if '|' in line:
                            parts = line.strip().split('|')
                            if len(parts) >= 3:
                                try:
                                    timestamp = datetime.fromtimestamp(int(parts[-1]))
                                    if timestamp > week_start:
                                        if 'task-completed' in line:
                                            activity['completed'].append(parts[1])
                                        elif 'task-started' in line:
                                            activity['started'].append(parts[1])
                                        elif 'Edit' in line or 'Write' in line:
                                            activity['files_modified'] += 1
                                        
                                        activity['tools_used'] += 1
                                except:
                                    continue
                except Exception as e:
                    logger.error(f"Error reading {log_file}: {e}")
        
        return activity

def main():
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    else:
        target_file = None
    
    logger.info("📊 Starting progress documentation update")
    
    updater = ProgressUpdater()
    
    # Update main progress documentation
    progress_file = updater.update_progress_documentation(target_file)
    print(f"📝 Updated progress documentation: {progress_file}")
    
    # Create weekly report if it's been a week since last one
    weekly_report_pattern = updater.docs_dir.glob("weekly-report-*.md")
    latest_weekly = max(weekly_report_pattern, key=os.path.getctime, default=None)
    
    if not latest_weekly or (datetime.now() - datetime.fromtimestamp(os.path.getctime(latest_weekly))).days >= 7:
        weekly_file = updater.create_weekly_progress_report()
        print(f"📊 Created weekly report: {weekly_file}")
    
    logger.info("✅ Progress documentation update complete")

if __name__ == "__main__":
    main()