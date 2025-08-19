#!/usr/bin/env python3
"""
Session Analytics for Claude Code
Comprehensive analytics and insights for development sessions
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Any, Tuple
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [SESSION-ANALYTICS] %(message)s'
)
logger = logging.getLogger(__name__)

class SessionAnalytics:
    def __init__(self):
        self.project_root = Path.cwd()
        self.cache_dir = Path(".claude/cache")
        self.session_dir = Path(".claude/session")
        self.analytics_dir = Path(".claude/analytics")
        
        # Ensure directories exist
        self.analytics_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize analytics database
        self.db_path = self.analytics_dir / "sessions.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration_minutes INTEGER,
                tools_used INTEGER,
                files_modified INTEGER,
                commands_executed INTEGER,
                errors_encountered INTEGER,
                tests_run INTEGER,
                quality_score REAL,
                productivity_score REAL,
                focus_area TEXT,
                notes TEXT
            )
        """)
        
        # Tool usage table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tool_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                tool_name TEXT,
                usage_count INTEGER,
                timestamp TIMESTAMP,
                success_rate REAL,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        """)
        
        # File changes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                file_path TEXT,
                change_type TEXT,
                file_extension TEXT,
                lines_changed INTEGER,
                timestamp TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        """)
        
        # Productivity metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productivity_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                metric_name TEXT,
                metric_value REAL,
                timestamp TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def collect_session_data(self) -> Dict:
        """Collect comprehensive session data"""
        session_data = {
            'session_info': self._get_session_info(),
            'tool_usage': self._analyze_tool_usage(),
            'file_changes': self._analyze_file_changes(),
            'command_patterns': self._analyze_command_patterns(),
            'productivity_metrics': self._calculate_productivity_metrics(),
            'quality_metrics': self._get_quality_metrics(),
            'ai_investment_metrics': self._get_ai_investment_metrics(),
            'focus_analysis': self._analyze_focus_patterns(),
            'error_analysis': self._analyze_errors()
        }
        
        return session_data
    
    def _get_session_info(self) -> Dict:
        """Get basic session information"""
        session_info = {
            'start_time': None,
            'end_time': datetime.now(),
            'duration_minutes': 0
        }
        
        start_file = self.session_dir / "start-time"
        if start_file.exists():
            try:
                with open(start_file, 'r') as f:
                    start_timestamp = int(f.read().strip())
                    start_time = datetime.fromtimestamp(start_timestamp)
                    session_info['start_time'] = start_time
                    
                    duration = datetime.now() - start_time
                    session_info['duration_minutes'] = int(duration.total_seconds() / 60)
            except Exception as e:
                logger.error(f"Error reading session start time: {e}")
        
        return session_info
    
    def _analyze_tool_usage(self) -> Dict:
        """Analyze tool usage patterns"""
        tool_data = {
            'total_operations': 0,
            'tool_distribution': {},
            'tool_sequences': [],
            'efficiency_score': 0.0
        }
        
        tool_log = self.session_dir / "tool-usage.log"
        if tool_log.exists():
            try:
                with open(tool_log, 'r') as f:
                    lines = f.readlines()
                
                tools = []
                for line in lines:
                    parts = line.strip().split('|')
                    if len(parts) >= 2:
                        tool_name = parts[0]
                        tools.append(tool_name)
                
                tool_data['total_operations'] = len(tools)
                tool_data['tool_distribution'] = dict(Counter(tools))
                
                # Analyze tool sequences
                sequences = []
                for i in range(len(tools) - 2):
                    sequence = f"{tools[i]} -> {tools[i+1]} -> {tools[i+2]}"
                    sequences.append(sequence)
                
                tool_data['tool_sequences'] = dict(Counter(sequences))
                
                # Calculate efficiency score based on tool variety and patterns
                unique_tools = len(set(tools))
                total_tools = len(tools)
                
                if total_tools > 0:
                    tool_data['efficiency_score'] = min(1.0, unique_tools / max(1, total_tools * 0.3))
                
            except Exception as e:
                logger.error(f"Error analyzing tool usage: {e}")
        
        return tool_data
    
    def _analyze_file_changes(self) -> Dict:
        """Analyze file modification patterns"""
        file_data = {
            'files_modified': 0,
            'languages_used': {},
            'change_distribution': {},
            'productivity_score': 0.0,
            'file_patterns': {}
        }
        
        change_log = self.cache_dir / "file-change-history"
        if change_log.exists():
            try:
                with open(change_log, 'r') as f:
                    lines = f.readlines()
                
                # Analyze recent changes (this session)
                session_start = self._get_session_start_timestamp()
                changes = []
                
                for line in lines:
                    parts = line.strip().split('|')
                    if len(parts) >= 4:
                        timestamp = float(parts[0])
                        if session_start and timestamp >= session_start:
                            changes.append({
                                'file': parts[1],
                                'type': parts[2],
                                'extension': parts[3],
                                'timestamp': timestamp
                            })
                
                file_data['files_modified'] = len(changes)
                
                # Language distribution
                extensions = [change['extension'] for change in changes]
                file_data['change_distribution'] = dict(Counter(extensions))
                
                # Map extensions to languages
                ext_to_lang = {
                    'py': 'Python',
                    'ts': 'TypeScript',
                    'tsx': 'TypeScript/React',
                    'js': 'JavaScript',
                    'jsx': 'JavaScript/React',
                    'md': 'Markdown'
                }
                
                languages = [ext_to_lang.get(ext, ext) for ext in extensions]
                file_data['languages_used'] = dict(Counter(languages))
                
                # Calculate productivity score
                if changes:
                    unique_files = len(set(change['file'] for change in changes))
                    file_data['productivity_score'] = unique_files / len(changes)
                
                # Analyze file patterns
                directories = [str(Path(change['file']).parent) for change in changes]
                file_data['file_patterns'] = dict(Counter(directories))
                
            except Exception as e:
                logger.error(f"Error analyzing file changes: {e}")
        
        return file_data
    
    def _analyze_command_patterns(self) -> Dict:
        """Analyze command execution patterns"""
        command_data = {
            'commands_executed': 0,
            'command_distribution': {},
            'success_rate': 0.0,
            'automation_score': 0.0
        }
        
        # Analyze command executions
        exec_log = self.session_dir / "command-executions.log"
        if exec_log.exists():
            try:
                with open(exec_log, 'r') as f:
                    lines = f.readlines()
                
                commands = []
                for line in lines:
                    parts = line.strip().split('|')
                    if len(parts) >= 2:
                        commands.append(parts[1])
                
                command_data['commands_executed'] = len(commands)
                command_data['command_distribution'] = dict(Counter(commands))
                
                # Calculate automation score (how much user relied on automated commands)
                automated_commands = ['test-backend', 'test-frontend', 'quality-check', 'pre-deploy']
                automated_count = sum(
                    count for cmd, count in command_data['command_distribution'].items()
                    if cmd in automated_commands
                )
                
                if commands:
                    command_data['automation_score'] = automated_count / len(commands)
                
            except Exception as e:
                logger.error(f"Error analyzing commands: {e}")
        
        # Analyze success rate
        success_log = self.cache_dir / "command-success.log"
        failure_log = self.cache_dir / "command-failures.log"
        
        successes = 0
        failures = 0
        
        if success_log.exists():
            successes = sum(1 for _ in open(success_log))
        
        if failure_log.exists():
            failures = sum(1 for _ in open(failure_log))
        
        total = successes + failures
        if total > 0:
            command_data['success_rate'] = successes / total
        
        return command_data
    
    def _calculate_productivity_metrics(self) -> Dict:
        """Calculate productivity metrics"""
        metrics = {
            'overall_score': 0.0,
            'focus_score': 0.0,
            'efficiency_score': 0.0,
            'quality_score': 0.0,
            'velocity_score': 0.0
        }
        
        session_info = self._get_session_info()
        duration = session_info['duration_minutes']
        
        if duration > 0:
            # Files modified per minute
            tool_data = self._analyze_tool_usage()
            file_data = self._analyze_file_changes()
            
            files_per_minute = file_data['files_modified'] / duration
            operations_per_minute = tool_data['total_operations'] / duration
            
            # Focus score (consistency in file types/directories)
            if file_data['file_patterns']:
                max_dir_changes = max(file_data['file_patterns'].values())
                total_changes = sum(file_data['file_patterns'].values())
                metrics['focus_score'] = max_dir_changes / max(1, total_changes)
            
            # Efficiency score (operations per minute, normalized)
            metrics['efficiency_score'] = min(1.0, operations_per_minute / 5.0)  # 5 ops/min = 100%
            
            # Velocity score (files modified per minute, normalized)
            metrics['velocity_score'] = min(1.0, files_per_minute / 2.0)  # 2 files/min = 100%
            
            # Quality score from recent quality metrics
            quality_file = self.cache_dir / "latest-quality-metrics.json"
            if quality_file.exists():
                try:
                    with open(quality_file, 'r') as f:
                        quality_data = json.load(f)
                    
                    quality_score = quality_data.get('metrics', {}).get('quality_score', 0)
                    metrics['quality_score'] = quality_score / 100.0
                
                except:
                    pass
            
            # Overall score (weighted average)
            weights = {
                'focus_score': 0.25,
                'efficiency_score': 0.25,
                'velocity_score': 0.25,
                'quality_score': 0.25
            }
            
            metrics['overall_score'] = sum(
                metrics[metric] * weight 
                for metric, weight in weights.items()
            )
        
        return metrics
    
    def _get_quality_metrics(self) -> Dict:
        """Get code quality metrics"""
        quality_data = {
            'quality_score': None,
            'test_coverage': None,
            'lint_issues': 0,
            'type_errors': 0,
            'tests_run': 0
        }
        
        # Load latest quality metrics
        quality_file = self.cache_dir / "latest-quality-metrics.json"
        if quality_file.exists():
            try:
                with open(quality_file, 'r') as f:
                    data = json.load(f)
                
                metrics = data.get('metrics', {})
                quality_data.update({
                    'quality_score': metrics.get('quality_score'),
                    'test_coverage': metrics.get('test_coverage'),
                    'lint_issues': metrics.get('lint_issues', 0),
                    'type_errors': metrics.get('type_errors', 0)
                })
            
            except Exception as e:
                logger.error(f"Error loading quality metrics: {e}")
        
        # Check test executions
        test_log = self.session_dir / "test-history.log"
        if test_log.exists():
            try:
                with open(test_log, 'r') as f:
                    lines = f.readlines()
                
                quality_data['tests_run'] = len(lines)
            
            except:
                pass
        
        return quality_data
    
    def _get_ai_investment_metrics(self) -> Dict:
        """Get AI Investment project specific metrics"""
        ai_metrics = {
            'financial_files_modified': 0,
            'api_endpoints_worked': 0,
            'database_changes': 0,
            'calculation_tests_run': 0,
            'external_api_usage': 0,
            'domain_focus_score': 0.0
        }
        
        # Analyze file changes for AI Investment context
        change_log = self.cache_dir / "file-change-history"
        if change_log.exists():
            try:
                with open(change_log, 'r') as f:
                    lines = f.readlines()
                
                session_start = self._get_session_start_timestamp()
                financial_terms = ['calculation', 'portfolio', 'index', 'asset', 'price']
                api_terms = ['router', 'endpoint', 'api']
                db_terms = ['model', 'schema', 'database']
                
                for line in lines:
                    parts = line.strip().split('|')
                    if len(parts) >= 2:
                        timestamp = float(parts[0])
                        if session_start and timestamp >= session_start:
                            file_path = parts[1].lower()
                            
                            # Check for financial domain files
                            if any(term in file_path for term in financial_terms):
                                ai_metrics['financial_files_modified'] += 1
                            
                            # Check for API files
                            if any(term in file_path for term in api_terms):
                                ai_metrics['api_endpoints_worked'] += 1
                            
                            # Check for database files
                            if any(term in file_path for term in db_terms):
                                ai_metrics['database_changes'] += 1
                
                # Calculate domain focus score
                total_changes = len([
                    line for line in lines 
                    if len(line.split('|')) >= 2 and 
                    session_start and float(line.split('|')[0]) >= session_start
                ])
                
                if total_changes > 0:
                    domain_changes = (
                        ai_metrics['financial_files_modified'] + 
                        ai_metrics['api_endpoints_worked'] + 
                        ai_metrics['database_changes']
                    )
                    ai_metrics['domain_focus_score'] = domain_changes / total_changes
                
            except Exception as e:
                logger.error(f"Error analyzing AI Investment metrics: {e}")
        
        return ai_metrics
    
    def _analyze_focus_patterns(self) -> Dict:
        """Analyze focus and attention patterns"""
        focus_data = {
            'primary_focus': None,
            'context_switches': 0,
            'focus_duration_avg': 0.0,
            'distraction_score': 0.0
        }
        
        # Analyze file change patterns for context switches
        change_log = self.cache_dir / "file-change-history"
        if change_log.exists():
            try:
                with open(change_log, 'r') as f:
                    lines = f.readlines()
                
                session_start = self._get_session_start_timestamp()
                directories = []
                
                for line in lines:
                    parts = line.strip().split('|')
                    if len(parts) >= 2:
                        timestamp = float(parts[0])
                        if session_start and timestamp >= session_start:
                            file_path = parts[1]
                            directory = str(Path(file_path).parent)
                            directories.append(directory)
                
                # Count context switches (directory changes)
                context_switches = 0
                for i in range(1, len(directories)):
                    if directories[i] != directories[i-1]:
                        context_switches += 1
                
                focus_data['context_switches'] = context_switches
                
                # Find primary focus
                if directories:
                    dir_counts = Counter(directories)
                    focus_data['primary_focus'] = dir_counts.most_common(1)[0][0]
                    
                    # Calculate distraction score
                    max_focus = dir_counts.most_common(1)[0][1]
                    total_changes = len(directories)
                    focus_data['distraction_score'] = 1.0 - (max_focus / total_changes)
                
            except Exception as e:
                logger.error(f"Error analyzing focus patterns: {e}")
        
        return focus_data
    
    def _analyze_errors(self) -> Dict:
        """Analyze error patterns and resolution"""
        error_data = {
            'total_errors': 0,
            'error_types': {},
            'resolution_rate': 0.0,
            'error_density': 0.0
        }
        
        # Analyze failed operations
        failed_log = self.session_dir / "failed-operations.log"
        if failed_log.exists():
            try:
                with open(failed_log, 'r') as f:
                    lines = f.readlines()
                
                error_data['total_errors'] = len(lines)
                
                # Categorize errors
                error_types = []
                for line in lines:
                    parts = line.strip().split('|')
                    if len(parts) >= 2:
                        error_types.append(parts[0])
                
                error_data['error_types'] = dict(Counter(error_types))
                
            except Exception as e:
                logger.error(f"Error analyzing errors: {e}")
        
        # Calculate error density (errors per operation)
        tool_data = self._analyze_tool_usage()
        if tool_data['total_operations'] > 0:
            error_data['error_density'] = error_data['total_errors'] / tool_data['total_operations']
        
        # Calculate resolution rate (assuming resolved if session continues productively)
        if error_data['total_errors'] > 0:
            file_data = self._analyze_file_changes()
            if file_data['files_modified'] > error_data['total_errors']:
                error_data['resolution_rate'] = 0.8  # Estimate based on continued productivity
        
        return error_data
    
    def store_session_analytics(self, session_data: Dict) -> int:
        """Store session analytics in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert session record
            session_info = session_data['session_info']
            productivity = session_data['productivity_metrics']
            quality = session_data['quality_metrics']
            focus = session_data['focus_patterns']
            
            cursor.execute("""
                INSERT INTO sessions (
                    start_time, end_time, duration_minutes, tools_used, files_modified,
                    commands_executed, errors_encountered, tests_run, quality_score,
                    productivity_score, focus_area, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_info['start_time'],
                session_info['end_time'],
                session_info['duration_minutes'],
                session_data['tool_usage']['total_operations'],
                session_data['file_changes']['files_modified'],
                session_data['command_patterns']['commands_executed'],
                session_data['error_analysis']['total_errors'],
                quality['tests_run'],
                quality['quality_score'],
                productivity['overall_score'],
                focus['primary_focus'],
                json.dumps(session_data['ai_investment_metrics'])
            ))
            
            session_id = cursor.lastrowid
            
            # Insert tool usage details
            for tool, count in session_data['tool_usage']['tool_distribution'].items():
                cursor.execute("""
                    INSERT INTO tool_usage (session_id, tool_name, usage_count, timestamp, success_rate)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    session_id, tool, count, datetime.now(),
                    session_data['command_patterns']['success_rate']
                ))
            
            # Insert productivity metrics
            for metric, value in productivity.items():
                if isinstance(value, (int, float)):
                    cursor.execute("""
                        INSERT INTO productivity_metrics (session_id, metric_name, metric_value, timestamp)
                        VALUES (?, ?, ?, ?)
                    """, (session_id, metric, value, datetime.now()))
            
            conn.commit()
            logger.info(f"Stored session analytics with ID: {session_id}")
            return session_id
        
        except Exception as e:
            logger.error(f"Error storing session analytics: {e}")
            conn.rollback()
            return -1
        
        finally:
            conn.close()
    
    def generate_analytics_report(self, days: int = 7) -> str:
        """Generate comprehensive analytics report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get sessions from last N days
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute("""
                SELECT * FROM sessions 
                WHERE start_time >= ? 
                ORDER BY start_time DESC
            """, (cutoff_date,))
            
            sessions = cursor.fetchall()
            
            if not sessions:
                return "No sessions found in the specified time period."
            
            # Generate report
            report = f"""# Development Analytics Report

*Period: Last {days} days*
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Overview

- **Total Sessions**: {len(sessions)}
- **Total Development Time**: {sum(s[3] or 0 for s in sessions)} minutes
- **Average Session Length**: {sum(s[3] or 0 for s in sessions) / len(sessions):.1f} minutes

## Productivity Metrics

"""
            
            # Calculate averages
            avg_tools = sum(s[4] or 0 for s in sessions) / len(sessions)
            avg_files = sum(s[5] or 0 for s in sessions) / len(sessions)
            avg_productivity = sum(s[10] or 0 for s in sessions) / len(sessions)
            
            report += f"- **Average Tools Used**: {avg_tools:.1f} per session\n"
            report += f"- **Average Files Modified**: {avg_files:.1f} per session\n"
            report += f"- **Average Productivity Score**: {avg_productivity:.2f}\n\n"
            
            # Quality metrics
            quality_scores = [s[9] for s in sessions if s[9] is not None]
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                report += f"- **Average Quality Score**: {avg_quality:.1f}/100\n\n"
            
            # Most productive sessions
            productive_sessions = sorted(sessions, key=lambda x: x[10] or 0, reverse=True)[:3]
            
            report += "## Most Productive Sessions\n\n"
            for i, session in enumerate(productive_sessions, 1):
                start_time = datetime.fromisoformat(session[1]) if session[1] else "Unknown"
                report += f"{i}. {start_time.strftime('%Y-%m-%d %H:%M')} - Score: {session[10]:.2f}\n"
            
            report += "\n"
            
            # Tool usage analysis
            cursor.execute("""
                SELECT tool_name, SUM(usage_count) as total_usage
                FROM tool_usage tu
                JOIN sessions s ON tu.session_id = s.id
                WHERE s.start_time >= ?
                GROUP BY tool_name
                ORDER BY total_usage DESC
                LIMIT 10
            """, (cutoff_date,))
            
            tool_usage = cursor.fetchall()
            
            if tool_usage:
                report += "## Most Used Tools\n\n"
                for tool, usage in tool_usage:
                    report += f"- **{tool}**: {usage} times\n"
                report += "\n"
            
            # Focus analysis
            focus_areas = [s[11] for s in sessions if s[11]]
            if focus_areas:
                focus_counts = Counter(focus_areas)
                report += "## Focus Areas\n\n"
                for area, count in focus_counts.most_common(5):
                    report += f"- **{area}**: {count} sessions\n"
                report += "\n"
            
            # Recommendations
            report += "## Recommendations\n\n"
            
            if avg_productivity < 0.5:
                report += "- 📈 **Productivity**: Consider using more automated tools and workflows\n"
            
            if quality_scores and sum(quality_scores) / len(quality_scores) < 75:
                report += "- 🔧 **Quality**: Focus on improving code quality metrics\n"
            
            if avg_files < 2:
                report += "- 🚀 **Velocity**: Consider working on larger features or breaking down tasks differently\n"
            
            total_errors = sum(s[7] or 0 for s in sessions)
            if total_errors > len(sessions) * 2:
                report += "- 🐛 **Error Rate**: High error rate detected - consider improving testing practices\n"
            
            report += "\n---\n\n*Analytics powered by Claude Code Session Analytics*\n"
            
            return report
        
        except Exception as e:
            logger.error(f"Error generating analytics report: {e}")
            return f"Error generating report: {e}"
        
        finally:
            conn.close()
    
    def _get_session_start_timestamp(self) -> float:
        """Get session start timestamp"""
        start_file = self.session_dir / "start-time"
        if start_file.exists():
            try:
                with open(start_file, 'r') as f:
                    return float(f.read().strip())
            except:
                pass
        return 0.0

def main():
    import sys
    
    analytics = SessionAnalytics()
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        
        if action == "collect":
            logger.info("📊 Collecting session analytics")
            session_data = analytics.collect_session_data()
            session_id = analytics.store_session_analytics(session_data)
            print(f"✅ Session analytics collected (ID: {session_id})")
            
        elif action == "report":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            report = analytics.generate_analytics_report(days)
            
            # Save report
            report_file = analytics.analytics_dir / f"report-{datetime.now().strftime('%Y%m%d')}.md"
            with open(report_file, 'w') as f:
                f.write(report)
            
            print(f"📈 Analytics report generated: {report_file}")
            print("\n" + "="*50)
            print(report)
            
        else:
            print(f"Unknown action: {action}")
    else:
        # Default: collect current session data
        session_data = analytics.collect_session_data()
        session_id = analytics.store_session_analytics(session_data)
        
        print("📊 Session Analytics Summary:")
        print(f"  Duration: {session_data['session_info']['duration_minutes']} minutes")
        print(f"  Tools Used: {session_data['tool_usage']['total_operations']}")
        print(f"  Files Modified: {session_data['file_changes']['files_modified']}")
        print(f"  Productivity Score: {session_data['productivity_metrics']['overall_score']:.2f}")
        
        if session_data['ai_investment_metrics']['domain_focus_score'] > 0:
            print(f"  AI Investment Focus: {session_data['ai_investment_metrics']['domain_focus_score']:.2f}")

if __name__ == "__main__":
    main()