#!/usr/bin/env python3
"""
Prompt Validator for Claude Code
Analyzes user prompts for clarity, completeness, and context
"""

import sys
import re
from typing import List, Dict, Tuple
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [PROMPT-VALIDATOR] %(message)s'
)
logger = logging.getLogger(__name__)

class PromptValidator:
    def __init__(self):
        # Patterns for unclear prompts
        self.unclear_patterns = [
            r'\b(fix|improve|update|change|modify)\s+it\b',
            r'\b(this|that|these|those)\s+(?:files?|functions?|components?)\b',
            r'\bmake\s+it\s+better\b',
            r'\badd\s+some\b',
            r'\bdo\s+something\b',
            r'\bwhatever\b',
            r'\bstuff\b',
            r'\bthingy?\b'
        ]
        
        # Patterns for overly broad tasks
        self.broad_patterns = [
            r'\bbuild\s+(?:a|an|the)?\s*(?:entire|complete|full)?\s*(?:application|app|system|website)\b',
            r'\bcreate\s+(?:a|an|the)?\s*(?:entire|complete|full)?\s*(?:project|solution)\b',
            r'\bimplement\s+everything\b',
            r'\bfix\s+all\s+(?:issues|problems|bugs)\b',
            r'\bmake\s+it\s+perfect\b',
            r'\boptimize\s+everything\b'
        ]
        
        # Patterns for missing context
        self.context_patterns = [
            r'\bwhich\s+file\b',
            r'\bwhere\s+(?:is|should)\b',
            r'\bin\s+(?:this|that)\s+file\b',
            r'\bthe\s+function\b',
            r'\bthis\s+(?:component|service|model)\b'
        ]
        
        # AI Investment domain-specific patterns
        self.domain_patterns = [
            r'\b(?:portfolio|index|calculation|trading|investment|financial|market)\b',
            r'\b(?:api|endpoint|database|model|component)\b',
            r'\b(?:twelvedata|marketaux|redis|fastapi|nextjs)\b'
        ]
        
        # Positive indicators
        self.specific_patterns = [
            r'\bfile:?\s+[^\s]+\.(?:py|ts|tsx|js|md)\b',
            r'\bfunction:?\s+\w+\b',
            r'\bclass:?\s+\w+\b',
            r'\bcomponent:?\s+\w+\b',
            r'\bendpoint:?\s+/\w+\b'
        ]

    def validate_prompt(self, prompt: str) -> Dict:
        """Validate a prompt and return analysis results"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'clarity_score': 0,
            'specificity_score': 0,
            'context_score': 0,
            'domain_relevance': 0,
            'issues': [],
            'suggestions': [],
            'warnings': []
        }
        
        if not prompt or len(prompt.strip()) < 5:
            analysis['issues'].append("Prompt is too short or empty")
            return analysis
        
        prompt_lower = prompt.lower()
        
        # Check for unclear language
        unclear_count = 0
        for pattern in self.unclear_patterns:
            if re.search(pattern, prompt_lower):
                unclear_count += 1
                analysis['issues'].append(f"Unclear reference found: {pattern}")
        
        # Check for overly broad requests
        broad_count = 0
        for pattern in self.broad_patterns:
            if re.search(pattern, prompt_lower):
                broad_count += 1
                analysis['warnings'].append(f"Very broad request detected: {pattern}")
        
        # Check for missing context
        context_issues = 0
        for pattern in self.context_patterns:
            if re.search(pattern, prompt_lower):
                context_issues += 1
                analysis['issues'].append(f"Missing context: {pattern}")
        
        # Check for domain relevance
        domain_matches = 0
        for pattern in self.domain_patterns:
            if re.search(pattern, prompt_lower):
                domain_matches += 1
        
        # Check for specificity
        specific_matches = 0
        for pattern in self.specific_patterns:
            if re.search(pattern, prompt):
                specific_matches += 1
        
        # Calculate scores
        analysis['clarity_score'] = max(0, 100 - (unclear_count * 20) - (context_issues * 15))
        analysis['specificity_score'] = min(100, specific_matches * 25 + (50 if broad_count == 0 else 0))
        analysis['context_score'] = max(0, 100 - (context_issues * 25))
        analysis['domain_relevance'] = min(100, domain_matches * 20)
        
        # Generate suggestions
        self._generate_suggestions(analysis, prompt, unclear_count, broad_count, context_issues, specific_matches)
        
        return analysis
    
    def _generate_suggestions(self, analysis: Dict, prompt: str, unclear_count: int, broad_count: int, context_issues: int, specific_matches: int):
        """Generate improvement suggestions"""
        
        if unclear_count > 0:
            analysis['suggestions'].append("Be more specific about what you want to modify or improve")
            analysis['suggestions'].append("Instead of 'fix it', describe what's broken or what behavior you expect")
        
        if broad_count > 0:
            analysis['suggestions'].append("Break down large requests into smaller, specific tasks")
            analysis['suggestions'].append("Focus on one feature or component at a time")
        
        if context_issues > 0:
            analysis['suggestions'].append("Specify exact file paths, function names, or component names")
            analysis['suggestions'].append("Provide context about where changes should be made")
        
        if specific_matches == 0:
            analysis['suggestions'].append("Include specific file names, functions, or endpoints in your request")
            analysis['suggestions'].append("Use format: 'In file X, modify function Y to do Z'")
        
        # AI Investment specific suggestions
        if 'api' in prompt.lower() and 'endpoint' not in prompt.lower():
            analysis['suggestions'].append("For API work, specify the endpoint path (e.g., /api/v1/portfolios)")
        
        if 'database' in prompt.lower() and 'model' not in prompt.lower():
            analysis['suggestions'].append("For database work, specify the model or table name")
        
        if 'frontend' in prompt.lower() and 'component' not in prompt.lower():
            analysis['suggestions'].append("For frontend work, specify the component or page name")
        
        if 'calculation' in prompt.lower():
            analysis['suggestions'].append("For financial calculations, specify the formula or metric type")
            analysis['suggestions'].append("Consider mentioning test requirements for financial calculations")
    
    def format_analysis_output(self, analysis: Dict) -> str:
        """Format analysis results for display"""
        output = []
        
        # Overall assessment
        avg_score = (analysis['clarity_score'] + analysis['specificity_score'] + analysis['context_score']) / 3
        
        if avg_score >= 80:
            output.append("✅ Prompt is clear and specific")
        elif avg_score >= 60:
            output.append("⚠️  Prompt could be more specific")
        else:
            output.append("❌ Prompt needs clarification")
        
        # Scores
        output.append(f"📊 Analysis Scores:")
        output.append(f"  • Clarity: {analysis['clarity_score']}/100")
        output.append(f"  • Specificity: {analysis['specificity_score']}/100")
        output.append(f"  • Context: {analysis['context_score']}/100")
        output.append(f"  • Domain Relevance: {analysis['domain_relevance']}/100")
        
        # Issues
        if analysis['issues']:
            output.append("🚨 Issues Found:")
            for issue in analysis['issues']:
                output.append(f"  • {issue}")
        
        # Warnings
        if analysis['warnings']:
            output.append("⚠️  Warnings:")
            for warning in analysis['warnings']:
                output.append(f"  • {warning}")
        
        # Suggestions
        if analysis['suggestions']:
            output.append("💡 Suggestions for Improvement:")
            for suggestion in analysis['suggestions'][:5]:  # Limit to top 5
                output.append(f"  • {suggestion}")
        
        return "\n".join(output)
    
    def get_ai_investment_context_suggestions(self) -> List[str]:
        """Get context suggestions specific to AI Investment project"""
        return [
            "For API work: Specify endpoint like '/api/v1/portfolios' or router file",
            "For database work: Mention model name like 'Asset', 'Portfolio', 'Price'",
            "For frontend work: Specify component like 'PortfolioChart', 'AssetList'",
            "For calculations: Mention metric like 'Sharpe ratio', 'portfolio return'",
            "For services: Specify service like 'calculation_service', 'market_data_service'",
            "For external APIs: Mention 'TwelveData' or 'MarketAux' integration",
            "For testing: Specify test file like 'test_calculations.py'",
            "For documentation: Mention doc section like 'API docs', 'model schema'"
        ]

def main():
    if len(sys.argv) < 2:
        logger.info("Usage: validate-prompt.py <prompt_text>")
        return
    
    prompt_text = " ".join(sys.argv[1:])
    
    validator = PromptValidator()
    analysis = validator.validate_prompt(prompt_text)
    
    # Output analysis
    output = validator.format_analysis_output(analysis)
    print(output)
    
    # Save analysis for learning
    import json
    import os
    
    cache_dir = ".claude/cache"
    os.makedirs(cache_dir, exist_ok=True)
    
    analysis_file = os.path.join(cache_dir, f"prompt-analysis-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json")
    analysis['prompt'] = prompt_text
    
    with open(analysis_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    # Show context suggestions for AI Investment project
    if analysis['domain_relevance'] > 0:
        print("\n🏗️  AI Investment Project Context Suggestions:")
        suggestions = validator.get_ai_investment_context_suggestions()
        for suggestion in suggestions[:3]:  # Show top 3
            print(f"  • {suggestion}")

if __name__ == "__main__":
    main()