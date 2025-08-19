#!/usr/bin/env python3
"""
AI Investment Project Intelligence Hook
Provides domain-specific analysis and suggestions for financial application development
"""

import sys
import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Setup logging
log_dir = Path(".claude/logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [AI-INTEL] %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"intelligence-{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIInvestmentAnalyzer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.cache_dir = Path(".claude/cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Financial calculation patterns
        self.financial_patterns = {
            'calculations': [
                r'def.*calculate.*return',
                r'portfolio.*value',
                r'index.*weight',
                r'risk.*calculation',
                r'sharpe.*ratio',
                r'beta.*calculation',
                r'correlation.*matrix',
                r'drawdown.*max'
            ],
            'api_integrations': [
                r'twelvedata',
                r'marketaux',
                r'alpha.*vantage',
                r'yahoo.*finance'
            ],
            'data_operations': [
                r'price.*data',
                r'historical.*data',
                r'market.*data',
                r'asset.*allocation',
                r'benchmark.*data'
            ]
        }
        
        # Known AI Investment project structure
        self.project_structure = {
            'backend': 'apps/api',
            'frontend': 'apps/web', 
            'models': 'apps/api/app/models',
            'services': 'apps/api/app/services',
            'routers': 'apps/api/app/routers',
            'tests': 'apps/api/tests',
            'docs': 'docs',
            'hooks': 'hooks'
        }

    def analyze_code_context(self, file_path, content):
        """Analyze code in context of AI Investment domain"""
        suggestions = []
        warnings = []
        
        # Financial calculation analysis
        if self._contains_financial_logic(content):
            suggestions.extend(self._analyze_financial_calculations(content))
        
        # API integration analysis
        if self._contains_api_integration(content):
            suggestions.extend(self._analyze_api_usage(content))
        
        # Data validation analysis
        if self._contains_data_operations(content):
            suggestions.extend(self._analyze_data_operations(content))
        
        # Security analysis for financial data
        security_issues = self._analyze_security(content)
        if security_issues:
            warnings.extend(security_issues)
        
        return suggestions, warnings

    def _contains_financial_logic(self, content):
        """Check if content contains financial calculation logic"""
        for pattern in self.financial_patterns['calculations']:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def _contains_api_integration(self, content):
        """Check if content contains external API integration"""
        for pattern in self.financial_patterns['api_integrations']:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def _contains_data_operations(self, content):
        """Check if content contains financial data operations"""
        for pattern in self.financial_patterns['data_operations']:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def _analyze_financial_calculations(self, content):
        """Analyze financial calculation implementations"""
        suggestions = []
        
        # Check for proper error handling
        if 'def calculate' in content and 'try:' not in content:
            suggestions.append("Financial calculations should include error handling for edge cases (division by zero, missing data)")
        
        # Check for input validation
        if re.search(r'def.*calculate.*\(.*\):', content) and 'isinstance' not in content:
            suggestions.append("Add input type validation for financial calculation functions")
        
        # Check for logging
        if 'calculate' in content and 'logger' not in content:
            suggestions.append("Add logging to financial calculations for audit trail")
        
        # Check for unit tests reference
        if 'def ' in content and re.search(r'calculate|portfolio|index', content):
            suggestions.append("Ensure unit tests exist for financial calculations with edge cases")
        
        # Check for decimal precision
        if re.search(r'[0-9]+\.[0-9]+', content) and 'Decimal' not in content:
            suggestions.append("Consider using Decimal for financial calculations to avoid floating-point precision issues")
        
        # Check for performance considerations
        if 'for' in content and 'portfolio' in content:
            suggestions.append("Consider vectorization with pandas/numpy for portfolio calculations performance")
        
        return suggestions

    def _analyze_api_usage(self, content):
        """Analyze external API integration patterns"""
        suggestions = []
        
        # Rate limiting checks
        if 'requests.get' in content or 'fetch(' in content:
            if 'rate' not in content.lower() and 'limit' not in content.lower():
                suggestions.append("Implement rate limiting for external API calls")
            
            if 'timeout' not in content:
                suggestions.append("Add timeout handling for external API calls")
        
        # TwelveData specific suggestions
        if 'twelvedata' in content.lower():
            suggestions.append("Monitor TwelveData API usage - 500 calls/day limit on free tier")
            if 'cache' not in content.lower():
                suggestions.append("Consider caching TwelveData responses to reduce API calls")
        
        # Error handling for API failures
        if 'api' in content.lower() and 'except' not in content:
            suggestions.append("Add comprehensive error handling for API failures and network issues")
        
        # API key security
        if re.search(r'api.*key', content, re.IGNORECASE) and 'env' not in content.lower():
            suggestions.append("Ensure API keys are loaded from environment variables, not hardcoded")
        
        return suggestions

    def _analyze_data_operations(self, content):
        """Analyze financial data operations"""
        suggestions = []
        
        # Data validation
        if 'price' in content.lower() and 'validate' not in content.lower():
            suggestions.append("Add data validation for price data (positive values, reasonable ranges)")
        
        # Date handling
        if 'date' in content.lower():
            suggestions.append("Ensure proper timezone handling for market data (market hours, different exchanges)")
        
        # Missing data handling
        if 'historical' in content.lower() and 'fillna' not in content and 'dropna' not in content:
            suggestions.append("Consider strategy for handling missing historical data")
        
        # Data freshness
        if 'market.*data' in content.lower():
            suggestions.append("Implement data freshness checks for market data")
        
        return suggestions

    def _analyze_security(self, content):
        """Analyze security aspects of financial code"""
        warnings = []
        
        # Hardcoded secrets
        secret_patterns = [
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'password\s*=\s*["\'][^"\']+["\']'
        ]
        
        for pattern in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                warnings.append("🚨 Potential hardcoded secret detected - use environment variables")
        
        # SQL injection risks
        if 'SELECT' in content and '%s' in content:
            warnings.append("🚨 Potential SQL injection risk - use parameterized queries")
        
        # Dangerous operations
        if re.search(r'DELETE\s+FROM|TRUNCATE|DROP', content, re.IGNORECASE):
            warnings.append("🚨 Dangerous database operation detected - ensure proper safeguards")
        
        return warnings

    def analyze_project_health(self):
        """Analyze overall project health and suggest improvements"""
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'suggestions': [],
            'warnings': [],
            'metrics': {}
        }
        
        # Check for missing critical files
        critical_files = [
            'apps/api/app/services/calculation_service.py',
            'apps/api/app/services/market_data_service.py',
            'apps/api/tests/test_calculations.py',
            'docs/API_DOCUMENTATION.md'
        ]
        
        for file_path in critical_files:
            if not Path(file_path).exists():
                health_report['warnings'].append(f"Missing critical file: {file_path}")
        
        # Check test coverage
        test_files = list(Path('apps/api/tests').glob('test_*.py')) if Path('apps/api/tests').exists() else []
        health_report['metrics']['test_files'] = len(test_files)
        
        if len(test_files) < 5:
            health_report['suggestions'].append("Increase test coverage - aim for at least 10 test files")
        
        # Check documentation
        doc_files = list(Path('docs').glob('*.md')) if Path('docs').exists() else []
        health_report['metrics']['doc_files'] = len(doc_files)
        
        # Check for environment configuration
        if not Path('.env').exists() and not Path('.env.example').exists():
            health_report['warnings'].append("No environment configuration found")
        
        # Save health report
        with open('.claude/cache/project-health.json', 'w') as f:
            json.dump(health_report, f, indent=2)
        
        return health_report

    def suggest_next_actions(self):
        """Suggest next development actions based on project state"""
        suggestions = []
        
        # Check recent activity
        activity_log = Path('.claude/logs')
        if activity_log.exists():
            recent_files = []
            for log_file in activity_log.glob('*.log'):
                if (datetime.now() - datetime.fromtimestamp(log_file.stat().st_mtime)).days < 1:
                    recent_files.append(log_file)
            
            if not recent_files:
                suggestions.append("No recent activity detected - consider running ai-status to see current priorities")
        
        # Check for pending TODO items
        todo_dir = Path('docs/TODO-MVP')
        if todo_dir.exists():
            p0_files = list((todo_dir / 'BACKLOG/P0-CRITICAL').glob('*.md')) if (todo_dir / 'BACKLOG/P0-CRITICAL').exists() else []
            if p0_files:
                suggestions.append(f"🚨 {len(p0_files)} critical P0 tasks need attention")
        
        # Check for outdated dependencies
        package_json = Path('apps/web/package.json')
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    if 'dependencies' in data:
                        suggestions.append("Consider running npm audit to check for security vulnerabilities")
            except:
                pass
        
        return suggestions

def main():
    if len(sys.argv) < 2:
        print("Usage: ai-investment-analyzer.py <action> [file_path] [content]")
        print("Actions: analyze, health, suggest")
        sys.exit(1)
    
    action = sys.argv[1]
    analyzer = AIInvestmentAnalyzer()
    
    if action == "analyze" and len(sys.argv) >= 4:
        file_path = sys.argv[2]
        content = sys.argv[3]
        
        logger.info(f"🧠 Analyzing {file_path}")
        suggestions, warnings = analyzer.analyze_code_context(file_path, content)
        
        if suggestions:
            logger.info("💡 Suggestions:")
            for suggestion in suggestions:
                logger.info(f"  • {suggestion}")
        
        if warnings:
            logger.info("⚠️  Warnings:")
            for warning in warnings:
                logger.info(f"  • {warning}")
        
    elif action == "health":
        logger.info("🏥 Running project health analysis")
        health_report = analyzer.analyze_project_health()
        
        if health_report['warnings']:
            logger.info("⚠️  Health Issues:")
            for warning in health_report['warnings']:
                logger.info(f"  • {warning}")
        
        if health_report['suggestions']:
            logger.info("💡 Health Suggestions:")
            for suggestion in health_report['suggestions']:
                logger.info(f"  • {suggestion}")
        
        logger.info(f"📊 Metrics: {health_report['metrics']}")
        
    elif action == "suggest":
        logger.info("🎯 Analyzing next actions")
        suggestions = analyzer.suggest_next_actions()
        
        if suggestions:
            logger.info("🚀 Suggested Next Actions:")
            for suggestion in suggestions:
                logger.info(f"  • {suggestion}")
        else:
            logger.info("✅ Project is up to date")
    
    else:
        logger.error("Invalid action or missing arguments")
        sys.exit(1)

if __name__ == "__main__":
    main()