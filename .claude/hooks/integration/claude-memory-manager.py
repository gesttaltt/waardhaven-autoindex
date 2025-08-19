#!/usr/bin/env python3
"""
Claude Memory Manager - Persistent context and learning system
Maintains project knowledge and provides intelligent context for Claude Code sessions
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [MEMORY-MANAGER] %(message)s'
)
logger = logging.getLogger(__name__)

class ClaudeMemoryManager:
    def __init__(self):
        self.project_root = Path.cwd()
        self.memory_dir = Path(".claude/memory")
        self.cache_dir = Path(".claude/cache")
        self.session_dir = Path(".claude/session")
        
        # Ensure directories exist
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Memory categories
        self.categories = {
            'project_patterns': 'coding_patterns.json',
            'user_preferences': 'user_preferences.json',
            'common_issues': 'common_issues.json',
            'successful_solutions': 'successful_solutions.json',
            'ai_investment_domain': 'ai_investment_knowledge.json',
            'command_history': 'command_patterns.json',
            'context_mappings': 'context_mappings.json'
        }
        
        # Initialize memory files
        self._initialize_memory_files()
    
    def _initialize_memory_files(self):
        """Initialize memory files with default structures"""
        for category, filename in self.categories.items():
            file_path = self.memory_dir / filename
            if not file_path.exists():
                initial_data = self._get_initial_data(category)
                with open(file_path, 'w') as f:
                    json.dump(initial_data, f, indent=2)
    
    def _get_initial_data(self, category: str) -> Dict:
        """Get initial data structure for memory category"""
        base_structure = {
            'created': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'version': '1.0',
            'entries': []
        }
        
        if category == 'ai_investment_domain':
            base_structure.update({
                'domain_knowledge': {
                    'financial_terms': ['portfolio', 'index', 'sharpe ratio', 'beta', 'correlation', 'drawdown'],
                    'api_endpoints': ['/api/v1/portfolios', '/api/v1/assets', '/api/v1/calculations'],
                    'database_models': ['Asset', 'Portfolio', 'Price', 'IndexValue', 'Allocation'],
                    'external_apis': ['TwelveData', 'MarketAux', 'Alpha Vantage'],
                    'calculation_types': ['returns', 'volatility', 'sharpe', 'beta', 'correlation']
                },
                'common_patterns': {
                    'financial_calculations': 'Always include error handling and input validation',
                    'api_integrations': 'Implement rate limiting and caching',
                    'database_operations': 'Use transactions and avoid hard deletes',
                    'frontend_charts': 'Use Recharts for financial visualizations'
                }
            })
        
        return base_structure
    
    def store_pattern(self, category: str, pattern_data: Dict):
        """Store a new pattern or update existing one"""
        file_path = self.memory_dir / self.categories[category]
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = self._get_initial_data(category)
        
        # Create pattern entry
        pattern_entry = {
            'id': self._generate_pattern_id(pattern_data),
            'timestamp': datetime.now().isoformat(),
            'data': pattern_data,
            'frequency': 1,
            'confidence': 0.5
        }
        
        # Check if pattern already exists
        existing_entry = None
        for entry in data['entries']:
            if entry['id'] == pattern_entry['id']:
                existing_entry = entry
                break
        
        if existing_entry:
            # Update existing pattern
            existing_entry['frequency'] += 1
            existing_entry['confidence'] = min(1.0, existing_entry['confidence'] + 0.1)
            existing_entry['last_seen'] = datetime.now().isoformat()
        else:
            # Add new pattern
            data['entries'].append(pattern_entry)
        
        # Update metadata
        data['last_updated'] = datetime.now().isoformat()
        
        # Save updated data
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Stored pattern in {category}: {pattern_data.get('description', 'unnamed')}")
    
    def get_relevant_patterns(self, context: str, category: str = None) -> List[Dict]:
        """Get patterns relevant to current context"""
        relevant_patterns = []
        
        categories_to_search = [category] if category else self.categories.keys()
        
        for cat in categories_to_search:
            file_path = self.memory_dir / self.categories[cat]
            
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                for entry in data['entries']:
                    relevance_score = self._calculate_relevance(context, entry['data'])
                    if relevance_score > 0.3:  # Threshold for relevance
                        pattern = entry.copy()
                        pattern['relevance_score'] = relevance_score
                        pattern['category'] = cat
                        relevant_patterns.append(pattern)
            
            except (FileNotFoundError, json.JSONDecodeError):
                continue
        
        # Sort by relevance and confidence
        relevant_patterns.sort(
            key=lambda x: (x['relevance_score'] * x['confidence']), 
            reverse=True
        )
        
        return relevant_patterns[:10]  # Return top 10 most relevant
    
    def learn_from_session(self):
        """Learn patterns from current session activity"""
        logger.info("🧠 Learning from session activity")
        
        # Analyze tool usage patterns
        self._learn_tool_patterns()
        
        # Analyze file modification patterns
        self._learn_file_patterns()
        
        # Analyze successful solutions
        self._learn_solution_patterns()
        
        # Analyze user preferences
        self._learn_user_preferences()
        
        # AI Investment specific learning
        self._learn_domain_patterns()
    
    def _learn_tool_patterns(self):
        """Learn from tool usage patterns"""
        tool_log = self.session_dir / "tool-usage.log"
        if not tool_log.exists():
            return
        
        try:
            with open(tool_log, 'r') as f:
                lines = f.readlines()
            
            # Analyze tool sequences
            tools = [line.split('|')[0] for line in lines if '|' in line]
            
            # Find common tool sequences
            for i in range(len(tools) - 1):
                sequence = f"{tools[i]} -> {tools[i+1]}"
                
                pattern_data = {
                    'type': 'tool_sequence',
                    'sequence': sequence,
                    'description': f"Common tool sequence: {sequence}",
                    'context': 'development_workflow'
                }
                
                self.store_pattern('project_patterns', pattern_data)
        
        except Exception as e:
            logger.error(f"Error learning tool patterns: {e}")
    
    def _learn_file_patterns(self):
        """Learn from file modification patterns"""
        change_log = self.cache_dir / "file-change-history"
        if not change_log.exists():
            return
        
        try:
            with open(change_log, 'r') as f:
                lines = f.readlines()
            
            # Analyze recent changes (last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            cutoff_timestamp = cutoff_time.timestamp()
            
            recent_changes = []
            for line in lines:
                parts = line.strip().split('|')
                if len(parts) >= 4:
                    timestamp = float(parts[0])
                    if timestamp >= cutoff_timestamp:
                        recent_changes.append({
                            'file': parts[1],
                            'type': parts[2],
                            'extension': parts[3]
                        })
            
            # Learn file type patterns
            ext_patterns = {}
            for change in recent_changes:
                ext = change['extension']
                if ext not in ext_patterns:
                    ext_patterns[ext] = 0
                ext_patterns[ext] += 1
            
            for ext, count in ext_patterns.items():
                if count > 1:  # Only learn from repeated patterns
                    pattern_data = {
                        'type': 'file_pattern',
                        'extension': ext,
                        'frequency': count,
                        'description': f"Frequent modifications to {ext} files",
                        'context': 'file_editing'
                    }
                    
                    self.store_pattern('project_patterns', pattern_data)
        
        except Exception as e:
            logger.error(f"Error learning file patterns: {e}")
    
    def _learn_solution_patterns(self):
        """Learn from successful solutions"""
        success_log = self.session_dir / "successful-operations.log"
        if not success_log.exists():
            return
        
        try:
            with open(success_log, 'r') as f:
                lines = f.readlines()
            
            # Analyze successful operations
            for line in lines:
                parts = line.strip().split('|')
                if len(parts) >= 2:
                    operation = parts[0]
                    result = parts[1]
                    
                    if result == 'success':
                        pattern_data = {
                            'type': 'successful_solution',
                            'operation': operation,
                            'description': f"Successful {operation} operation",
                            'context': 'problem_solving'
                        }
                        
                        self.store_pattern('successful_solutions', pattern_data)
        
        except Exception as e:
            logger.error(f"Error learning solution patterns: {e}")
    
    def _learn_user_preferences(self):
        """Learn user preferences from session activity"""
        # Analyze command preferences
        enhancer_log = self.session_dir / "enhancer-usage.log"
        if enhancer_log.exists():
            try:
                with open(enhancer_log, 'r') as f:
                    lines = f.readlines()
                
                command_preferences = {}
                for line in lines:
                    parts = line.strip().split('|')
                    if len(parts) >= 3 and parts[1] == 'execute':
                        command = parts[2]
                        command_preferences[command] = command_preferences.get(command, 0) + 1
                
                # Store top preferences
                for command, frequency in command_preferences.items():
                    if frequency > 1:
                        pattern_data = {
                            'type': 'command_preference',
                            'command': command,
                            'frequency': frequency,
                            'description': f"Preferred command: {command}",
                            'context': 'user_preference'
                        }
                        
                        self.store_pattern('user_preferences', pattern_data)
            
            except Exception as e:
                logger.error(f"Error learning user preferences: {e}")
    
    def _learn_domain_patterns(self):
        """Learn AI Investment domain-specific patterns"""
        if not Path("CLAUDE.md").exists():
            return
        
        # Analyze financial calculation patterns
        calc_files = list(Path("apps/api").rglob("*calculation*"))
        if calc_files:
            pattern_data = {
                'type': 'domain_pattern',
                'domain': 'financial_calculations',
                'file_count': len(calc_files),
                'description': 'Financial calculation module usage',
                'context': 'ai_investment_domain'
            }
            
            self.store_pattern('ai_investment_domain', pattern_data)
        
        # Analyze API endpoint patterns
        router_files = list(Path("apps/api").rglob("*router*"))
        for router_file in router_files:
            try:
                with open(router_file, 'r') as f:
                    content = f.read()
                
                # Look for API endpoints
                if '/api/v1/' in content:
                    pattern_data = {
                        'type': 'api_pattern',
                        'file': str(router_file),
                        'description': f'API endpoints in {router_file.name}',
                        'context': 'api_development'
                    }
                    
                    self.store_pattern('ai_investment_domain', pattern_data)
            
            except Exception as e:
                continue
    
    def get_context_suggestions(self, current_context: str) -> List[str]:
        """Get context-aware suggestions based on learned patterns"""
        suggestions = []
        
        # Get relevant patterns
        patterns = self.get_relevant_patterns(current_context)
        
        for pattern in patterns:
            pattern_type = pattern['data'].get('type', '')
            
            if pattern_type == 'tool_sequence':
                suggestions.append(f"Consider the workflow: {pattern['data']['sequence']}")
            
            elif pattern_type == 'successful_solution':
                suggestions.append(f"Previous success with: {pattern['data']['operation']}")
            
            elif pattern_type == 'command_preference':
                suggestions.append(f"You often use: {pattern['data']['command']}")
            
            elif pattern_type == 'domain_pattern':
                suggestions.append(f"AI Investment context: {pattern['data']['description']}")
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def get_ai_investment_context(self) -> Dict:
        """Get AI Investment project specific context"""
        context = {
            'current_focus': None,
            'domain_knowledge': {},
            'recent_patterns': [],
            'suggestions': []
        }
        
        # Load AI Investment domain knowledge
        domain_file = self.memory_dir / self.categories['ai_investment_domain']
        try:
            with open(domain_file, 'r') as f:
                data = json.load(f)
            
            context['domain_knowledge'] = data.get('domain_knowledge', {})
            
            # Get recent domain patterns
            recent_patterns = [
                entry for entry in data.get('entries', [])
                if self._is_recent(entry.get('timestamp', ''))
            ]
            context['recent_patterns'] = recent_patterns[:5]
        
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        # Get current focus from TODO
        todo_dashboard = Path("docs/TODO-MVP/README.md")
        if todo_dashboard.exists():
            try:
                with open(todo_dashboard, 'r') as f:
                    content = f.read()
                
                for line in content.split('\n'):
                    if 'Working on:' in line:
                        focus = line.split('Working on:', 1)[1].strip()
                        if focus and focus != 'None':
                            context['current_focus'] = focus
                        break
            except:
                pass
        
        return context
    
    def cleanup_old_memories(self, days_to_keep: int = 30):
        """Clean up old memory entries"""
        logger.info(f"🧹 Cleaning up memories older than {days_to_keep} days")
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cleaned_count = 0
        
        for category, filename in self.categories.items():
            file_path = self.memory_dir / filename
            
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                original_count = len(data.get('entries', []))
                
                # Filter out old entries with low confidence
                data['entries'] = [
                    entry for entry in data.get('entries', [])
                    if (self._is_recent(entry.get('timestamp', ''), days_to_keep) or 
                        entry.get('confidence', 0) > 0.7)
                ]
                
                new_count = len(data['entries'])
                cleaned_count += original_count - new_count
                
                # Save cleaned data
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
            
            except (FileNotFoundError, json.JSONDecodeError):
                continue
        
        logger.info(f"Cleaned up {cleaned_count} old memory entries")
    
    def _generate_pattern_id(self, pattern_data: Dict) -> str:
        """Generate unique ID for pattern"""
        pattern_str = json.dumps(pattern_data, sort_keys=True)
        return hashlib.md5(pattern_str.encode()).hexdigest()[:12]
    
    def _calculate_relevance(self, context: str, pattern_data: Dict) -> float:
        """Calculate relevance score between context and pattern"""
        context_lower = context.lower()
        pattern_str = json.dumps(pattern_data).lower()
        
        # Simple relevance scoring based on keyword matching
        context_words = set(context_lower.split())
        pattern_words = set(pattern_str.split())
        
        if not context_words:
            return 0.0
        
        overlap = len(context_words.intersection(pattern_words))
        relevance = overlap / len(context_words)
        
        # Boost relevance for exact matches
        if context_lower in pattern_str:
            relevance += 0.3
        
        return min(1.0, relevance)
    
    def _is_recent(self, timestamp_str: str, days: int = 7) -> bool:
        """Check if timestamp is within recent days"""
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            cutoff = datetime.now() - timedelta(days=days)
            return timestamp > cutoff
        except:
            return False

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: claude-memory-manager.py <learn|suggest|context|cleanup> [args]")
        sys.exit(1)
    
    action = sys.argv[1]
    manager = ClaudeMemoryManager()
    
    if action == "learn":
        logger.info("🧠 Learning from session")
        manager.learn_from_session()
        print("✅ Session learning complete")
    
    elif action == "suggest":
        context = sys.argv[2] if len(sys.argv) > 2 else "general"
        suggestions = manager.get_context_suggestions(context)
        
        print(f"💡 Context suggestions for '{context}':")
        for suggestion in suggestions:
            print(f"  • {suggestion}")
    
    elif action == "context":
        context_data = manager.get_ai_investment_context()
        
        print("🏗️  AI Investment Project Context:")
        if context_data['current_focus']:
            print(f"  🎯 Current Focus: {context_data['current_focus']}")
        
        if context_data['domain_knowledge']:
            print(f"  📚 Domain Knowledge: {len(context_data['domain_knowledge'])} categories")
        
        if context_data['recent_patterns']:
            print(f"  📈 Recent Patterns: {len(context_data['recent_patterns'])} entries")
    
    elif action == "cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        manager.cleanup_old_memories(days)
        print(f"✅ Memory cleanup complete (kept last {days} days)")
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()