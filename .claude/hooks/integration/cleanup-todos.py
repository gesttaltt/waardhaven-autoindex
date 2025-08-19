#!/usr/bin/env python3
"""
Todo Cleanup Automation for AI Investment Project
Automatically manages completed todos and updates documentation
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [TODO-CLEANUP] %(message)s'
)
logger = logging.getLogger(__name__)

class TodoCleaner:
    def __init__(self):
        self.project_root = Path.cwd()
        self.todo_dir = self.project_root / "docs" / "TODO-MVP"
        self.archive_dir = self.todo_dir / "ARCHIVED"
        self.cache_dir = Path(".claude/cache")
        
        # Ensure directories exist
        self.archive_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Create archive subdirectories
        (self.archive_dir / "completed").mkdir(exist_ok=True)
        (self.archive_dir / "cancelled").mkdir(exist_ok=True)
    
    def analyze_todo_status(self) -> dict:
        """Analyze current TODO status and identify cleanup opportunities"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_files': 0,
            'completed_files': [],
            'empty_files': [],
            'outdated_files': [],
            'statistics': {
                'p0_critical': 0,
                'p1_core': 0,
                'p2_enhancements': 0,
                'p3_future': 0,
                'bugs': 0,
                'tech_debt': 0
            }
        }
        
        if not self.todo_dir.exists():
            logger.warning("TODO directory not found")
            return analysis
        
        # Analyze backlog structure
        backlog_dirs = {
            'P0-CRITICAL': 'p0_critical',
            'P1-CORE-MVP': 'p1_core',
            'P2-ENHANCEMENTS': 'p2_enhancements',
            'P3-FUTURE': 'p3_future'
        }
        
        for dir_name, stat_key in backlog_dirs.items():
            backlog_path = self.todo_dir / "BACKLOG" / dir_name
            if backlog_path.exists():
                files = list(backlog_path.glob("*.md"))
                analysis['statistics'][stat_key] = len(files)
                analysis['total_files'] += len(files)
                
                # Check each file for completion status
                for file_path in files:
                    file_analysis = self._analyze_todo_file(file_path)
                    if file_analysis['is_completed']:
                        analysis['completed_files'].append(str(file_path))
                    elif file_analysis['is_empty']:
                        analysis['empty_files'].append(str(file_path))
                    elif file_analysis['is_outdated']:
                        analysis['outdated_files'].append(str(file_path))
        
        # Analyze bugs and tech debt
        bugs_dir = self.todo_dir / "BUGS"
        if bugs_dir.exists():
            bug_files = list(bugs_dir.glob("*.md"))
            analysis['statistics']['bugs'] = len(bug_files)
            analysis['total_files'] += len(bug_files)
        
        tech_debt_dir = self.todo_dir / "TECHNICAL-DEBT"
        if tech_debt_dir.exists():
            debt_files = list(tech_debt_dir.glob("*.md"))
            analysis['statistics']['tech_debt'] = len(debt_files)
            analysis['total_files'] += len(debt_files)
        
        return analysis
    
    def _analyze_todo_file(self, file_path: Path) -> dict:
        """Analyze individual TODO file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return {'is_completed': False, 'is_empty': True, 'is_outdated': False}
        
        # Check if file is empty or minimal
        is_empty = len(content.strip()) < 50
        
        # Check for completion indicators
        completion_patterns = [
            '✅',
            '[x]',
            'COMPLETED',
            'DONE',
            'FINISHED',
            'IMPLEMENTED'
        ]
        
        is_completed = any(pattern in content for pattern in completion_patterns)
        
        # Check if all tasks are marked complete
        checklist_items = content.count('- [ ]') + content.count('- [x]')
        completed_items = content.count('- [x]')
        
        if checklist_items > 0 and completed_items == checklist_items:
            is_completed = True
        
        # Check for outdated content (references to old dates, deprecated features)
        outdated_patterns = [
            '2024',
            'deprecated',
            'obsolete',
            'no longer needed'
        ]
        
        is_outdated = any(pattern in content.lower() for pattern in outdated_patterns)
        
        return {
            'is_completed': is_completed,
            'is_empty': is_empty,
            'is_outdated': is_outdated,
            'content_length': len(content),
            'checklist_total': checklist_items,
            'checklist_completed': completed_items
        }
    
    def cleanup_completed_todos(self, analysis: dict) -> dict:
        """Move completed TODO files to archive"""
        cleanup_results = {
            'archived_files': [],
            'removed_empty': [],
            'errors': []
        }
        
        # Archive completed files
        for file_path_str in analysis['completed_files']:
            file_path = Path(file_path_str)
            try:
                # Create archive entry
                archive_entry = self._create_archive_entry(file_path)
                
                # Move file to archive
                archive_filename = f"{datetime.now().strftime('%Y%m%d')}_{file_path.name}"
                archive_path = self.archive_dir / "completed" / archive_filename
                
                shutil.move(str(file_path), str(archive_path))
                
                # Save archive metadata
                metadata_path = archive_path.with_suffix('.json')
                with open(metadata_path, 'w') as f:
                    json.dump(archive_entry, f, indent=2)
                
                cleanup_results['archived_files'].append(str(archive_path))
                logger.info(f"Archived completed TODO: {file_path.name}")
                
            except Exception as e:
                logger.error(f"Error archiving {file_path}: {e}")
                cleanup_results['errors'].append(f"Archive error: {file_path.name} - {e}")
        
        # Remove empty files
        for file_path_str in analysis['empty_files']:
            file_path = Path(file_path_str)
            try:
                file_path.unlink()
                cleanup_results['removed_empty'].append(str(file_path))
                logger.info(f"Removed empty TODO: {file_path.name}")
                
            except Exception as e:
                logger.error(f"Error removing {file_path}: {e}")
                cleanup_results['errors'].append(f"Remove error: {file_path.name} - {e}")
        
        return cleanup_results
    
    def _create_archive_entry(self, file_path: Path) -> dict:
        """Create archive metadata entry"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            content = ""
        
        return {
            'original_path': str(file_path),
            'archived_date': datetime.now().isoformat(),
            'file_name': file_path.name,
            'priority': self._extract_priority_from_path(file_path),
            'content_preview': content[:200] + "..." if len(content) > 200 else content,
            'completion_reason': 'auto_detected_completed'
        }
    
    def _extract_priority_from_path(self, file_path: Path) -> str:
        """Extract priority from file path"""
        path_str = str(file_path)
        if 'P0-CRITICAL' in path_str:
            return 'P0'
        elif 'P1-CORE-MVP' in path_str:
            return 'P1'
        elif 'P2-ENHANCEMENTS' in path_str:
            return 'P2'
        elif 'P3-FUTURE' in path_str:
            return 'P3'
        elif 'BUGS' in path_str:
            return 'BUG'
        elif 'TECHNICAL-DEBT' in path_str:
            return 'TECH-DEBT'
        else:
            return 'UNKNOWN'
    
    def update_todo_dashboard(self, analysis: dict, cleanup_results: dict):
        """Update the main TODO dashboard"""
        dashboard_path = self.todo_dir / "README.md"
        
        if not dashboard_path.exists():
            logger.warning("TODO dashboard not found")
            return
        
        try:
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update statistics
            stats = analysis['statistics']
            
            # Update P0 tasks
            content = self._update_dashboard_stat(content, 'P0 Tasks:', stats['p0_critical'])
            content = self._update_dashboard_stat(content, 'P1 Tasks:', stats['p1_core'])
            content = self._update_dashboard_stat(content, 'Bugs:', stats['bugs'])
            content = self._update_dashboard_stat(content, 'Tech Debt:', f"${stats['tech_debt']}")
            
            # Add cleanup activity to progress section
            if cleanup_results['archived_files'] or cleanup_results['removed_empty']:
                cleanup_summary = f"- ✅ Auto-cleanup: {len(cleanup_results['archived_files'])} completed, {len(cleanup_results['removed_empty'])} removed - {datetime.now().strftime('%Y-%m-%d')}"
                
                # Insert after progress header
                if "## 📊 Progress This Week" in content:
                    content = content.replace(
                        "## 📊 Progress This Week",
                        f"## 📊 Progress This Week\n{cleanup_summary}"
                    )
            
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info("Updated TODO dashboard")
            
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
    
    def _update_dashboard_stat(self, content: str, stat_name: str, value) -> str:
        """Update a specific statistic in the dashboard"""
        import re
        pattern = f"({stat_name}).*remaining"
        replacement = f"\\1 {value} remaining"
        return re.sub(pattern, replacement, content)
    
    def generate_cleanup_report(self, analysis: dict, cleanup_results: dict) -> str:
        """Generate cleanup activity report"""
        report = f"""# TODO Cleanup Report

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Summary
- Total TODO files analyzed: {analysis['total_files']}
- Completed files archived: {len(cleanup_results['archived_files'])}
- Empty files removed: {len(cleanup_results['removed_empty'])}
- Errors encountered: {len(cleanup_results['errors'])}

## Current Statistics
- P0 Critical: {analysis['statistics']['p0_critical']} tasks
- P1 Core MVP: {analysis['statistics']['p1_core']} tasks
- P2 Enhancements: {analysis['statistics']['p2_enhancements']} tasks
- P3 Future: {analysis['statistics']['p3_future']} tasks
- Active Bugs: {analysis['statistics']['bugs']}
- Technical Debt: {analysis['statistics']['tech_debt']} items

## Actions Taken

### Archived Completed Files
"""
        
        for archived in cleanup_results['archived_files']:
            report += f"- {Path(archived).name}\n"
        
        if cleanup_results['removed_empty']:
            report += "\n### Removed Empty Files\n"
            for removed in cleanup_results['removed_empty']:
                report += f"- {Path(removed).name}\n"
        
        if cleanup_results['errors']:
            report += "\n### Errors\n"
            for error in cleanup_results['errors']:
                report += f"- {error}\n"
        
        report += f"\n## Next Steps\n"
        
        if analysis['statistics']['p0_critical'] > 0:
            report += f"- 🚨 Address {analysis['statistics']['p0_critical']} critical P0 tasks\n"
        
        if analysis['statistics']['bugs'] > 0:
            report += f"- 🐛 Fix {analysis['statistics']['bugs']} active bugs\n"
        
        if analysis['statistics']['p1_core'] > 0:
            report += f"- 🎯 Focus on {analysis['statistics']['p1_core']} core MVP tasks\n"
        
        return report
    
    def save_cleanup_report(self, report: str):
        """Save cleanup report to cache"""
        report_file = self.cache_dir / f"todo-cleanup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Cleanup report saved: {report_file}")
        
        # Also save latest report
        latest_report = self.cache_dir / "latest-todo-cleanup.md"
        with open(latest_report, 'w', encoding='utf-8') as f:
            f.write(report)

def main():
    logger.info("🧹 Starting TODO cleanup automation")
    
    cleaner = TodoCleaner()
    
    # Analyze current TODO status
    analysis = cleaner.analyze_todo_status()
    logger.info(f"📊 Analysis complete: {analysis['total_files']} files, {len(analysis['completed_files'])} completed")
    
    # Perform cleanup if needed
    if analysis['completed_files'] or analysis['empty_files']:
        cleanup_results = cleaner.cleanup_completed_todos(analysis)
        logger.info(f"🗂️  Cleanup complete: {len(cleanup_results['archived_files'])} archived, {len(cleanup_results['removed_empty'])} removed")
        
        # Update dashboard
        cleaner.update_todo_dashboard(analysis, cleanup_results)
        
        # Generate and save report
        report = cleaner.generate_cleanup_report(analysis, cleanup_results)
        cleaner.save_cleanup_report(report)
        
        print("📝 TODO Cleanup Summary:")
        print(f"  • Archived: {len(cleanup_results['archived_files'])} completed files")
        print(f"  • Removed: {len(cleanup_results['removed_empty'])} empty files")
        
        if cleanup_results['errors']:
            print(f"  • Errors: {len(cleanup_results['errors'])}")
    else:
        logger.info("✨ No cleanup needed - all TODOs are active")
        print("✨ No TODO cleanup needed")
    
    logger.info("✅ TODO cleanup automation complete")

if __name__ == "__main__":
    main()