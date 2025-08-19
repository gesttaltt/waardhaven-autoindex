#!/usr/bin/env python3
"""
Session Summary Generator for Claude Code
Creates comprehensive summaries of development sessions with insights and next steps
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [SESSION-SUMMARY] %(message)s'
)
logger = logging.getLogger(__name__)

class SessionSummaryGenerator:
    def __init__(self):
        self.project_root = Path.cwd()
        self.cache_dir = Path(".claude/cache")
        self.session_dir = Path(".claude/session")
        self.docs_dir = self.project_root / "docs"
        
        # Ensure directories exist
        self.cache_dir.mkdir(exist_ok=True)
        self.session_dir.mkdir(exist_ok=True)
    
    def generate_session_summary(self) -> dict:
        """Generate comprehensive session summary"""
        summary = {
            'session_info': self._get_session_info(),
            'activity_metrics': self._analyze_activity_metrics(),
            'code_changes': self._analyze_code_changes(),
            'todo_progress': self._analyze_todo_progress(),
            'quality_metrics': self._get_quality_metrics(),
            'ai_investment_insights': self._get_ai_investment_insights(),
            'recommendations': [],
            'next_steps': []
        }
        
        # Generate recommendations based on analysis
        summary['recommendations'] = self._generate_recommendations(summary)
        summary['next_steps'] = self._generate_next_steps(summary)
        
        return summary
    
    def _get_session_info(self) -> dict:
        """Get basic session information"""
        session_info = {
            'start_time': None,
            'end_time': datetime.now().isoformat(),
            'duration_minutes': 0,
            'session_id': None
        }
        
        # Get session start time
        start_file = self.session_dir / "start-time"
        if start_file.exists():
            try:
                with open(start_file, 'r') as f:
                    start_timestamp = int(f.read().strip())
                    start_time = datetime.fromtimestamp(start_timestamp)
                    session_info['start_time'] = start_time.isoformat()
                    
                    # Calculate duration
                    duration = datetime.now() - start_time
                    session_info['duration_minutes'] = int(duration.total_seconds() / 60)
            except Exception as e:
                logger.error(f"Error reading session start time: {e}")
        
        return session_info
    
    def _analyze_activity_metrics(self) -> dict:
        """Analyze session activity metrics"""
        metrics = {
            'tools_used': {},
            'total_operations': 0,
            'files_modified': 0,
            'most_active_directories': {},
            'error_rate': 0
        }
        
        # Analyze tool usage
        tool_log = self.session_dir / "tool-usage.log"
        if tool_log.exists():
            try:
                with open(tool_log, 'r') as f:
                    lines = f.readlines()
                
                tools = [line.split('|')[0] for line in lines if '|' in line]
                metrics['tools_used'] = dict(Counter(tools))
                metrics['total_operations'] = len(tools)
                
                # Count file modifications
                edit_tools = ['Edit', 'Write', 'MultiEdit']
                metrics['files_modified'] = sum(
                    count for tool, count in metrics['tools_used'].items() 
                    if tool in edit_tools
                )
                
            except Exception as e:
                logger.error(f"Error analyzing tool usage: {e}")
        
        # Analyze successful vs failed operations
        success_log = self.session_dir / "successful-operations.log"
        failed_log = self.session_dir / "failed-operations.log"
        
        successful_count = 0
        failed_count = 0
        
        if success_log.exists():
            successful_count = sum(1 for _ in open(success_log))
        
        if failed_log.exists():
            failed_count = sum(1 for _ in open(failed_log))
        
        total_ops = successful_count + failed_count
        if total_ops > 0:
            metrics['error_rate'] = (failed_count / total_ops) * 100
        
        return metrics
    
    def _analyze_code_changes(self) -> dict:
        """Analyze code changes made during session"""
        changes = {
            'languages': {},
            'file_types': {},
            'directories_modified': {},
            'estimated_lines_changed': 0,
            'new_files_created': 0
        }
        
        # Analyze file change history
        change_log = self.cache_dir / "file-change-history"
        if change_log.exists():
            try:
                with open(change_log, 'r') as f:
                    lines = f.readlines()
                
                # Get changes from this session (rough estimate)
                session_start_time = self._get_session_start_timestamp()
                
                for line in lines:
                    parts = line.strip().split('|')
                    if len(parts) >= 4:
                        try:
                            timestamp = int(parts[0])
                            if session_start_time and timestamp >= session_start_time:
                                file_path = parts[1]
                                change_type = parts[2]
                                file_ext = parts[3]
                                
                                # Count by file extension
                                changes['file_types'][file_ext] = changes['file_types'].get(file_ext, 0) + 1
                                
                                # Count by directory
                                directory = str(Path(file_path).parent)
                                changes['directories_modified'][directory] = changes['directories_modified'].get(directory, 0) + 1
                                
                                # Count new files
                                if change_type == 'created':
                                    changes['new_files_created'] += 1
                                
                        except:
                            continue
                
            except Exception as e:
                logger.error(f"Error analyzing code changes: {e}")
        
        # Map file extensions to languages
        ext_to_lang = {
            'py': 'Python',
            'ts': 'TypeScript',
            'tsx': 'TypeScript/React',
            'js': 'JavaScript',
            'jsx': 'JavaScript/React',
            'md': 'Markdown',
            'json': 'JSON',
            'yml': 'YAML',
            'yaml': 'YAML'
        }
        
        for ext, count in changes['file_types'].items():
            lang = ext_to_lang.get(ext, ext.upper())
            changes['languages'][lang] = changes['languages'].get(lang, 0) + count
        
        return changes
    
    def _analyze_todo_progress(self) -> dict:
        """Analyze TODO progress during session"""
        progress = {
            'tasks_completed': [],
            'tasks_started': [],
            'current_focus': None,
            'priority_distribution': {}
        }
        
        # Check for TODO-related activity
        activity_log = self.session_dir / "activity.log"
        if activity_log.exists():
            try:
                with open(activity_log, 'r') as f:
                    lines = f.readlines()
                
                session_start = self._get_session_start_timestamp()
                
                for line in lines:
                    parts = line.strip().split('|')
                    if len(parts) >= 3:
                        try:
                            activity_type = parts[0]
                            task_name = parts[1]
                            timestamp = int(parts[2])
                            
                            if session_start and timestamp >= session_start:
                                if activity_type == 'task-completed':
                                    progress['tasks_completed'].append(task_name)
                                elif activity_type == 'task-started':
                                    progress['tasks_started'].append(task_name)
                        except:
                            continue
                
            except Exception as e:
                logger.error(f"Error analyzing TODO progress: {e}")
        
        # Get current focus from dashboard
        dashboard_path = self.project_root / "docs" / "TODO-MVP" / "README.md"
        if dashboard_path.exists():
            try:
                with open(dashboard_path, 'r') as f:
                    content = f.read()
                
                for line in content.split('\n'):
                    if 'Working on:' in line:
                        focus = line.split('Working on:', 1)[1].strip()
                        if focus and focus != 'None':
                            progress['current_focus'] = focus
                        break
            except Exception as e:
                logger.error(f"Error reading dashboard: {e}")
        
        return progress
    
    def _get_quality_metrics(self) -> dict:
        """Get code quality metrics from recent analysis"""
        metrics = {
            'quality_score': None,
            'test_coverage': None,
            'lint_issues': None,
            'type_errors': None,
            'last_test_run': None
        }
        
        # Get latest quality metrics
        quality_file = self.cache_dir / "latest-quality-metrics.json"
        if quality_file.exists():
            try:
                with open(quality_file, 'r') as f:
                    quality_data = json.load(f)
                
                if 'metrics' in quality_data:
                    quality_metrics = quality_data['metrics']
                    metrics['quality_score'] = quality_metrics.get('quality_score')
                    metrics['test_coverage'] = quality_metrics.get('test_coverage')
                    metrics['lint_issues'] = quality_metrics.get('lint_issues')
                    metrics['type_errors'] = quality_metrics.get('type_errors')
                
            except Exception as e:
                logger.error(f"Error reading quality metrics: {e}")
        
        # Check last test execution
        test_cache = self.cache_dir / "last-successful-tests"
        if test_cache.exists():
            try:
                with open(test_cache, 'r') as f:
                    test_timestamp = int(f.read().strip())
                    test_time = datetime.fromtimestamp(test_timestamp)
                    metrics['last_test_run'] = test_time.isoformat()
            except Exception as e:
                logger.error(f"Error reading test timestamp: {e}")
        
        return metrics
    
    def _get_ai_investment_insights(self) -> dict:
        """Get AI Investment project specific insights"""
        insights = {
            'financial_code_changes': 0,
            'api_endpoint_changes': 0,
            'database_model_changes': 0,
            'external_api_usage': 0,
            'domain_focus': []
        }
        
        # Analyze changes in financial domain context
        change_log = self.cache_dir / "file-change-history"
        if change_log.exists():
            try:
                with open(change_log, 'r') as f:
                    lines = f.readlines()
                
                session_start = self._get_session_start_timestamp()
                
                for line in lines:
                    parts = line.strip().split('|')
                    if len(parts) >= 2:
                        try:
                            timestamp = int(parts[0])
                            if session_start and timestamp >= session_start:
                                file_path = parts[1].lower()
                                
                                # Detect financial domain changes
                                if any(term in file_path for term in ['calculation', 'portfolio', 'index', 'financial']):
                                    insights['financial_code_changes'] += 1
                                    insights['domain_focus'].append('Financial Calculations')
                                
                                # Detect API changes
                                if 'router' in file_path or 'endpoint' in file_path:
                                    insights['api_endpoint_changes'] += 1
                                    insights['domain_focus'].append('API Development')
                                
                                # Detect model changes
                                if 'model' in file_path:
                                    insights['database_model_changes'] += 1
                                    insights['domain_focus'].append('Database Design')
                                
                        except:
                            continue
                
            except Exception as e:
                logger.error(f"Error analyzing AI Investment insights: {e}")
        
        # Remove duplicates from domain focus
        insights['domain_focus'] = list(set(insights['domain_focus']))
        
        return insights
    
    def _generate_recommendations(self, summary: dict) -> list:
        """Generate recommendations based on session analysis"""
        recommendations = []
        
        # Quality-based recommendations
        quality = summary['quality_metrics']
        if quality['quality_score'] is not None and quality['quality_score'] < 75:
            recommendations.append("📊 Code quality score is below 75 - consider running quality improvements")
        
        if quality['lint_issues'] is not None and quality['lint_issues'] > 5:
            recommendations.append("🔧 Multiple lint issues detected - run linting tools to clean up code")
        
        if quality['type_errors'] is not None and quality['type_errors'] > 0:
            recommendations.append("📝 Type errors found - run TypeScript/mypy checks and fix errors")
        
        # Test recommendations
        if quality['last_test_run']:
            last_test = datetime.fromisoformat(quality['last_test_run'])
            if (datetime.now() - last_test).total_seconds() > 3600:  # 1 hour
                recommendations.append("🧪 Tests haven't been run recently - consider running test suite")
        else:
            recommendations.append("🧪 No recent test execution found - run tests to verify functionality")
        
        # Activity-based recommendations
        activity = summary['activity_metrics']
        if activity['error_rate'] > 20:
            recommendations.append("⚠️  High error rate in operations - review recent failures")
        
        if activity['files_modified'] > 10:
            recommendations.append("📝 Many files modified - ensure comprehensive testing before commit")
        
        # TODO progress recommendations
        todo = summary['todo_progress']
        if not todo['current_focus']:
            recommendations.append("🎯 No current focus set - consider setting a specific task in TODO dashboard")
        
        # AI Investment specific recommendations
        ai_insights = summary['ai_investment_insights']
        if ai_insights['financial_code_changes'] > 0:
            recommendations.append("💰 Financial calculation changes detected - run calculation-specific tests")
        
        if ai_insights['api_endpoint_changes'] > 0:
            recommendations.append("🔄 API changes detected - update OpenAPI documentation")
        
        return recommendations
    
    def _generate_next_steps(self, summary: dict) -> list:
        """Generate suggested next steps"""
        next_steps = []
        
        # Based on current focus
        todo = summary['todo_progress']
        if todo['current_focus']:
            next_steps.append(f"Continue working on: {todo['current_focus']}")
        
        # Based on changes made
        changes = summary['code_changes']
        if changes['new_files_created'] > 0:
            next_steps.append("Add tests for newly created files")
        
        if 'Python' in changes['languages']:
            next_steps.append("Run Python linting and type checking")
        
        if 'TypeScript' in changes['languages'] or 'TypeScript/React' in changes['languages']:
            next_steps.append("Run TypeScript compilation check")
        
        # Quality improvements
        quality = summary['quality_metrics']
        if quality['quality_score'] is not None and quality['quality_score'] < 80:
            next_steps.append("Address code quality issues")
        
        # Testing
        if not summary['quality_metrics']['last_test_run']:
            next_steps.append("Run comprehensive test suite")
        
        # Documentation
        if changes['files_modified'] > 5:
            next_steps.append("Update relevant documentation")
        
        # Deployment readiness
        activity = summary['activity_metrics']
        if activity['files_modified'] > 0 and activity['error_rate'] < 10:
            next_steps.append("Consider running pre-deployment checks")
        
        return next_steps
    
    def _get_session_start_timestamp(self) -> int:
        """Get session start timestamp"""
        start_file = self.session_dir / "start-time"
        if start_file.exists():
            try:
                with open(start_file, 'r') as f:
                    return int(f.read().strip())
            except:
                pass
        return None
    
    def create_summary_document(self, summary: dict) -> str:
        """Create formatted summary document"""
        session_info = summary['session_info']
        duration = session_info['duration_minutes']
        
        doc = f"""# Claude Code Session Summary

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Session Overview

- **Duration**: {duration} minutes
- **Start Time**: {session_info['start_time'] or 'Unknown'}
- **End Time**: {session_info['end_time']}

## Activity Summary

### Tools Used
"""
        
        activity = summary['activity_metrics']
        for tool, count in sorted(activity['tools_used'].items(), key=lambda x: x[1], reverse=True):
            doc += f"- **{tool}**: {count} times\n"
        
        doc += f"\n### Overall Metrics\n"
        doc += f"- Total Operations: {activity['total_operations']}\n"
        doc += f"- Files Modified: {activity['files_modified']}\n"
        doc += f"- Error Rate: {activity['error_rate']:.1f}%\n\n"
        
        # Code changes
        changes = summary['code_changes']
        if changes['languages']:
            doc += "### Code Changes\n\n"
            doc += "**Languages worked with:**\n"
            for lang, count in changes['languages'].items():
                doc += f"- {lang}: {count} files\n"
            
            if changes['new_files_created'] > 0:
                doc += f"\n- **New files created**: {changes['new_files_created']}\n"
            
            doc += "\n"
        
        # TODO progress
        todo = summary['todo_progress']
        if todo['tasks_completed'] or todo['tasks_started'] or todo['current_focus']:
            doc += "### TODO Progress\n\n"
            
            if todo['current_focus']:
                doc += f"**Current Focus**: {todo['current_focus']}\n\n"
            
            if todo['tasks_completed']:
                doc += "**Tasks Completed:**\n"
                for task in todo['tasks_completed']:
                    doc += f"- ✅ {task}\n"
                doc += "\n"
            
            if todo['tasks_started']:
                doc += "**Tasks Started:**\n"
                for task in todo['tasks_started']:
                    doc += f"- 🔄 {task}\n"
                doc += "\n"
        
        # Quality metrics
        quality = summary['quality_metrics']
        if any(v is not None for v in quality.values()):
            doc += "### Code Quality\n\n"
            
            if quality['quality_score'] is not None:
                doc += f"- Quality Score: {quality['quality_score']}/100\n"
            
            if quality['test_coverage'] is not None:
                doc += f"- Test Coverage: {quality['test_coverage']}%\n"
            
            if quality['lint_issues'] is not None:
                doc += f"- Lint Issues: {quality['lint_issues']}\n"
            
            if quality['type_errors'] is not None:
                doc += f"- Type Errors: {quality['type_errors']}\n"
            
            doc += "\n"
        
        # AI Investment insights
        ai_insights = summary['ai_investment_insights']
        if any(v > 0 for v in [ai_insights['financial_code_changes'], ai_insights['api_endpoint_changes'], ai_insights['database_model_changes']]):
            doc += "### AI Investment Project Insights\n\n"
            
            if ai_insights['financial_code_changes'] > 0:
                doc += f"- Financial calculation files modified: {ai_insights['financial_code_changes']}\n"
            
            if ai_insights['api_endpoint_changes'] > 0:
                doc += f"- API endpoint files modified: {ai_insights['api_endpoint_changes']}\n"
            
            if ai_insights['database_model_changes'] > 0:
                doc += f"- Database model files modified: {ai_insights['database_model_changes']}\n"
            
            if ai_insights['domain_focus']:
                doc += f"\n**Domain Focus**: {', '.join(ai_insights['domain_focus'])}\n"
            
            doc += "\n"
        
        # Recommendations
        if summary['recommendations']:
            doc += "## Recommendations\n\n"
            for rec in summary['recommendations']:
                doc += f"- {rec}\n"
            doc += "\n"
        
        # Next steps
        if summary['next_steps']:
            doc += "## Suggested Next Steps\n\n"
            for step in summary['next_steps']:
                doc += f"1. {step}\n"
            doc += "\n"
        
        doc += "---\n\n"
        doc += "*This summary was automatically generated based on session activity.*\n"
        
        return doc
    
    def save_session_summary(self, summary: dict) -> str:
        """Save session summary to file"""
        # Create summary document
        doc_content = self.create_summary_document(summary)
        
        # Save to docs directory
        summary_file = self.docs_dir / f"session-summary-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        # Also save JSON version to cache
        json_file = self.cache_dir / f"session-summary-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(json_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Save as latest
        latest_file = self.cache_dir / "latest-session-summary.json"
        with open(latest_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Session summary saved: {summary_file}")
        return str(summary_file)

def main():
    logger.info("📋 Generating session summary")
    
    generator = SessionSummaryGenerator()
    
    # Generate comprehensive summary
    summary = generator.generate_session_summary()
    
    # Save summary document
    summary_file = generator.save_session_summary(summary)
    
    # Print brief summary to console
    session_info = summary['session_info']
    activity = summary['activity_metrics']
    
    print(f"📊 Session Summary Generated: {summary_file}")
    print(f"⏱️  Duration: {session_info['duration_minutes']} minutes")
    print(f"🛠️  Operations: {activity['total_operations']}")
    print(f"📝 Files Modified: {activity['files_modified']}")
    
    if summary['recommendations']:
        print(f"💡 Recommendations: {len(summary['recommendations'])}")
    
    if summary['next_steps']:
        print(f"🎯 Next Steps: {len(summary['next_steps'])}")
    
    logger.info("✅ Session summary generation complete")

if __name__ == "__main__":
    main()