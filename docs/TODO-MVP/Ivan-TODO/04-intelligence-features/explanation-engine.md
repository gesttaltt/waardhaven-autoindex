# 💬 Explanation Engine

**Priority**: MEDIUM  
**Complexity**: High  
**Timeline**: 3-4 days  
**Value**: Transform complex analysis into clear, actionable insights

## 🎯 Objective

Build an AI-powered explanation system that:
- Translates complex financial analysis into plain language
- Provides contextual explanations for recommendations
- Adapts explanation complexity to user experience level
- Explains the "why" behind every insight
- Builds user confidence through transparency

## 🧠 Explanation Framework

### Explanation Types
```python
EXPLANATION_TYPES = {
    'recommendation_explanation': {
        'purpose': 'Explain why we recommend buying/selling/holding',
        'components': ['key_factors', 'reasoning_chain', 'supporting_evidence'],
        'example': 'We recommend buying AAPL because...'
    },
    'risk_explanation': {
        'purpose': 'Explain identified risks and their impact',
        'components': ['risk_sources', 'probability', 'mitigation'],
        'example': 'The main risk is earnings uncertainty because...'
    },
    'pattern_explanation': {
        'purpose': 'Explain detected patterns and their significance',
        'components': ['pattern_description', 'historical_context', 'implications'],
        'example': 'This insider buying pattern typically indicates...'
    },
    'prediction_explanation': {
        'purpose': 'Explain how predictions were made',
        'components': ['model_inputs', 'key_drivers', 'confidence_rationale'],
        'example': 'Our price target is based on...'
    },
    'opportunity_explanation': {
        'purpose': 'Explain why an opportunity exists',
        'components': ['opportunity_type', 'catalyst', 'timing_rationale'],
        'example': 'This value opportunity exists because...'
    }
}
```

## 🗣️ Natural Language Generation Engine

```python
# app/intelligence/explanation_engine.py

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import openai

class ExplanationEngine:
    """Generate natural language explanations for investment insights"""
    
    def __init__(self):
        self.template_manager = ExplanationTemplateManager()
        self.context_analyzer = ContextAnalyzer()
        self.complexity_adapter = ComplexityAdapter()
        self.personalization_engine = PersonalizationEngine()
        
    async def generate_explanation(self, 
                                 insight_type: str, 
                                 data: Dict, 
                                 user_profile: Dict = None) -> Dict:
        """Generate comprehensive explanation for any insight"""
        
        # Analyze the context and data
        context = await self.context_analyzer.analyze_context(insight_type, data)
        
        # Determine explanation complexity based on user profile
        complexity_level = self.determine_complexity_level(user_profile)
        
        # Generate core explanation
        core_explanation = await self.generate_core_explanation(
            insight_type, 
            data, 
            context,
            complexity_level
        )
        
        # Add supporting details
        supporting_details = await self.generate_supporting_details(
            insight_type,
            data,
            complexity_level
        )
        
        # Generate actionable insights
        actionable_insights = await self.generate_actionable_insights(
            insight_type,
            data,
            context
        )
        
        # Personalize for user
        if user_profile:
            personalized = await self.personalization_engine.personalize_explanation(
                core_explanation,
                supporting_details,
                actionable_insights,
                user_profile
            )
        else:
            personalized = {
                'core': core_explanation,
                'details': supporting_details,
                'actions': actionable_insights
            }
        
        return {
            'explanation': personalized,
            'metadata': {
                'insight_type': insight_type,
                'complexity_level': complexity_level,
                'generated_at': datetime.now(),
                'confidence': context.get('confidence', 0.7)
            }
        }
    
    async def generate_recommendation_explanation(self, recommendation: Dict, analysis_data: Dict) -> Dict:
        """Generate explanation for investment recommendation"""
        
        action = recommendation['action']
        symbol = recommendation['symbol']
        confidence = recommendation['confidence']
        key_factors = recommendation.get('key_reasons', [])
        
        # Build explanation narrative
        explanation_parts = []
        
        # Opening statement
        if action in ['strong_buy', 'buy']:
            opening = f"We recommend {'strongly ' if action == 'strong_buy' else ''}buying {symbol} "
            opening += f"with {confidence:.0%} confidence. "
        elif action == 'hold':
            opening = f"We recommend holding {symbol} at current levels. "
        else:
            opening = f"We recommend {'strongly ' if action == 'strong_sell' else ''}selling {symbol}. "
        
        explanation_parts.append(opening)
        
        # Key reasoning
        if len(key_factors) > 0:
            explanation_parts.append("Here's why:")
            
            for i, factor in enumerate(key_factors[:3], 1):  # Top 3 factors
                explanation_parts.append(f"{i}. {factor}")
        
        # Risk context
        risk_level = recommendation.get('risk_level', 'medium')
        risk_context = self.generate_risk_context(risk_level, analysis_data)
        explanation_parts.append(risk_context)
        
        # Time horizon and expectations
        time_horizon = recommendation.get('time_horizon', 'medium-term')
        price_target = recommendation.get('price_targets', {}).get('target')
        
        if price_target:
            expectation = f"We expect the stock to reach ${price_target:.2f} over the {time_horizon}, "
            expectation += f"representing potential upside of {recommendation.get('expected_return', 0):.1%}."
            explanation_parts.append(expectation)
        
        return {
            'full_explanation': ' '.join(explanation_parts),
            'key_points': key_factors,
            'risk_summary': risk_context,
            'action_plan': self.generate_action_plan(recommendation)
        }
    
    async def generate_pattern_explanation(self, pattern: Dict, symbol: str) -> Dict:
        """Generate explanation for detected patterns"""
        
        pattern_type = pattern['type']
        confidence = pattern['confidence']
        
        explanations = {
            'insider_cluster': self.explain_insider_cluster_pattern,
            'earnings_anticipation': self.explain_earnings_pattern,
            'technical_breakout': self.explain_technical_pattern,
            'momentum_acceleration': self.explain_momentum_pattern,
            'value_divergence': self.explain_value_pattern
        }
        
        if pattern_type in explanations:
            explanation = await explanations[pattern_type](pattern, symbol)
        else:
            explanation = await self.explain_generic_pattern(pattern, symbol)
        
        return {
            'pattern_type': pattern_type,
            'explanation': explanation,
            'confidence_explanation': self.explain_confidence_level(confidence),
            'historical_context': await self.get_historical_pattern_context(pattern_type),
            'implications': self.explain_pattern_implications(pattern, symbol)
        }
    
    async def explain_insider_cluster_pattern(self, pattern: Dict, symbol: str) -> str:
        """Explain insider buying cluster pattern"""
        
        num_insiders = pattern.get('insider_count', 0)
        total_value = pattern.get('total_value', 0)
        timeframe = pattern.get('timeframe_days', 30)
        
        explanation = f"We've detected a significant insider buying cluster in {symbol}. "
        explanation += f"Over the past {timeframe} days, {num_insiders} company insiders have purchased "
        explanation += f"${total_value:,.0f} worth of stock. "
        
        explanation += "This pattern is particularly noteworthy because:\n\n"
        explanation += "• Insiders have access to non-public information about the company\n"
        explanation += "• Coordinated buying often precedes positive developments\n"
        explanation += "• Historical data shows stocks with insider clusters outperform by 8-12% over 6 months\n"
        
        if pattern.get('executive_involvement'):
            explanation += "• Senior executives (CEO/CFO level) are participating in the buying\n"
        
        explanation += f"\nBased on our analysis, this pattern has a {pattern['confidence']:.0%} likelihood "
        explanation += "of indicating positive price movement in the coming 3-6 months."
        
        return explanation
    
    async def explain_earnings_pattern(self, pattern: Dict, symbol: str) -> str:
        """Explain earnings anticipation pattern"""
        
        beat_probability = pattern.get('beat_probability', 0.5)
        leading_indicators = pattern.get('leading_indicators', [])
        days_to_earnings = pattern.get('days_to_earnings', 30)
        
        explanation = f"Our analysis suggests {symbol} has a {beat_probability:.0%} probability "
        explanation += f"of beating earnings expectations in {days_to_earnings} days. "
        
        explanation += "This assessment is based on several leading indicators:\n\n"
        
        for indicator in leading_indicators[:4]:  # Top 4 indicators
            explanation += f"• {indicator['description']}: {indicator['signal']}\n"
        
        explanation += f"\nCompanies with similar leading indicator patterns have historically "
        explanation += f"beaten earnings estimates {pattern.get('historical_accuracy', 65):.0f}% of the time, "
        explanation += f"with an average post-earnings return of {pattern.get('avg_post_earnings_return', 0.06):.1%}."
        
        return explanation
    
    def generate_risk_context(self, risk_level: str, analysis_data: Dict) -> str:
        """Generate risk context explanation"""
        
        risk_explanations = {
            'low': "This is a relatively low-risk investment with stable fundamentals and limited downside exposure.",
            'medium': "This investment carries moderate risk, typical for quality stocks in normal market conditions.",
            'high': "This is a higher-risk investment that could experience significant volatility.",
            'very_high': "This investment carries substantial risk and should only be considered by experienced investors."
        }
        
        base_explanation = risk_explanations.get(risk_level, risk_explanations['medium'])
        
        # Add specific risk factors if available
        specific_risks = analysis_data.get('risk_factors', [])
        if specific_risks:
            base_explanation += f" Key risks include: {', '.join(specific_risks[:3])}."
        
        return base_explanation
    
    def generate_action_plan(self, recommendation: Dict) -> List[str]:
        """Generate specific action plan for recommendation"""
        
        action = recommendation['action']
        symbol = recommendation['symbol']
        
        action_plans = {
            'strong_buy': [
                f"Consider allocating 5-10% of portfolio to {symbol}",
                "Enter position gradually over 2-3 days",
                f"Set stop-loss at {recommendation.get('stop_loss', 'TBD')}",
                "Monitor for earnings and news catalysts"
            ],
            'buy': [
                f"Consider allocating 2-5% of portfolio to {symbol}",
                "Enter position on any weakness",
                "Use limit orders to avoid overpaying",
                "Review position in 30 days"
            ],
            'hold': [
                "Maintain current position size",
                "Monitor for changes in fundamentals",
                "Consider trimming on strength above target",
                "Reassess if new information emerges"
            ],
            'sell': [
                "Reduce position by 50-75%",
                "Exit gradually to minimize market impact",
                "Consider tax implications of sale",
                "Look for better opportunities"
            ],
            'strong_sell': [
                "Exit position immediately",
                "Use stop-loss if position is underwater",
                "Avoid new positions in this stock",
                "Monitor for potential short opportunity"
            ]
        }
        
        return action_plans.get(action, action_plans['hold'])

class ComplexityAdapter:
    """Adapt explanation complexity to user level"""
    
    def __init__(self):
        self.complexity_levels = {
            'beginner': {
                'vocabulary': 'simple',
                'technical_terms': 'explained',
                'detail_level': 'high',
                'examples': 'frequent'
            },
            'intermediate': {
                'vocabulary': 'moderate',
                'technical_terms': 'used_with_context',
                'detail_level': 'medium',
                'examples': 'occasional'
            },
            'advanced': {
                'vocabulary': 'sophisticated',
                'technical_terms': 'assumed_knowledge',
                'detail_level': 'concise',
                'examples': 'minimal'
            }
        }
    
    def adapt_explanation(self, explanation: str, complexity_level: str) -> str:
        """Adapt explanation to appropriate complexity level"""
        
        if complexity_level == 'beginner':
            return self.simplify_for_beginners(explanation)
        elif complexity_level == 'advanced':
            return self.condense_for_advanced(explanation)
        else:
            return explanation  # Intermediate is default
    
    def simplify_for_beginners(self, explanation: str) -> str:
        """Simplify explanation for beginner investors"""
        
        # Replace technical terms with simple explanations
        replacements = {
            'P/E ratio': 'price-to-earnings ratio (how expensive the stock is)',
            'market cap': 'company size (total value of all shares)',
            'volatility': 'price swings (how much the price moves up and down)',
            'beta': 'market sensitivity (how much it moves with the overall market)',
            'insider trading': 'company executives buying or selling their own stock'
        }
        
        adapted = explanation
        for technical, simple in replacements.items():
            adapted = adapted.replace(technical, simple)
        
        # Add educational context
        if 'insider' in adapted.lower():
            adapted += "\n\n💡 Educational Note: When company insiders buy stock, it often means they believe the price will go up because they know the company best."
        
        return adapted
    
    def condense_for_advanced(self, explanation: str) -> str:
        """Condense explanation for advanced investors"""
        
        # Remove basic explanations and examples
        lines = explanation.split('\n')
        condensed_lines = []
        
        for line in lines:
            # Skip educational notes and basic explanations
            if any(phrase in line.lower() for phrase in ['educational note', 'this means', 'in simple terms']):
                continue
            condensed_lines.append(line)
        
        return '\n'.join(condensed_lines)

class PersonalizationEngine:
    """Personalize explanations based on user preferences and history"""
    
    async def personalize_explanation(self, 
                                    core_explanation: str,
                                    supporting_details: Dict,
                                    actionable_insights: List[str],
                                    user_profile: Dict) -> Dict:
        """Personalize explanation based on user profile"""
        
        # Adapt for investment style
        investment_style = user_profile.get('investment_style', 'balanced')
        
        if investment_style == 'value':
            core_explanation = self.emphasize_value_aspects(core_explanation)
        elif investment_style == 'growth':
            core_explanation = self.emphasize_growth_aspects(core_explanation)
        elif investment_style == 'income':
            core_explanation = self.emphasize_income_aspects(core_explanation)
        
        # Adapt for risk tolerance
        risk_tolerance = user_profile.get('risk_tolerance', 'medium')
        actionable_insights = self.adapt_actions_for_risk_tolerance(
            actionable_insights, 
            risk_tolerance
        )
        
        # Add sector-specific context if user has preferences
        sector_preferences = user_profile.get('sector_preferences', [])
        if sector_preferences:
            supporting_details['sector_context'] = self.add_sector_context(
                supporting_details,
                sector_preferences
            )
        
        return {
            'core': core_explanation,
            'details': supporting_details,
            'actions': actionable_insights,
            'personalization_applied': True
        }
    
    def emphasize_value_aspects(self, explanation: str) -> str:
        """Emphasize value investing aspects"""
        
        value_terms = ['undervalued', 'cheap', 'discount', 'intrinsic value', 'margin of safety']
        
        # If explanation contains value terms, emphasize them
        for term in value_terms:
            if term in explanation.lower():
                explanation = explanation.replace(
                    term, 
                    f"**{term}**"  # Bold emphasis
                )
        
        return explanation
    
    def adapt_actions_for_risk_tolerance(self, actions: List[str], risk_tolerance: str) -> List[str]:
        """Adapt action recommendations based on risk tolerance"""
        
        adapted_actions = []
        
        for action in actions:
            if risk_tolerance == 'conservative':
                # Make actions more conservative
                if 'allocating 5-10%' in action:
                    action = action.replace('5-10%', '2-5%')
                elif 'gradually over 2-3 days' in action:
                    action = action.replace('2-3 days', '1-2 weeks')
            elif risk_tolerance == 'aggressive':
                # Make actions more aggressive
                if 'allocating 2-5%' in action:
                    action = action.replace('2-5%', '5-10%')
                elif 'Enter position on any weakness' in action:
                    action = action.replace('on any weakness', 'immediately')
            
            adapted_actions.append(action)
        
        return adapted_actions
```

## 🎨 Explanation UI Components

```typescript
// ExplanationCard.tsx

interface ExplanationData {
  type: string;
  explanation: {
    core: string;
    details: any;
    actions: string[];
  };
  metadata: {
    complexity_level: string;
    confidence: number;
  };
}

const ExplanationCard: React.FC<{ explanation: ExplanationData }> = ({ explanation }) => {
  const [showDetails, setShowDetails] = useState(false);
  const [complexity, setComplexity] = useState(explanation.metadata.complexity_level);

  return (
    <Card className="explanation-card">
      <CardHeader>
        <div className="flex justify-between items-center">
          <Title>💬 Explanation</Title>
          <div className="flex items-center gap-2">
            <ComplexitySelector 
              value={complexity}
              onChange={setComplexity}
            />
            <ConfidenceIndicator value={explanation.metadata.confidence} />
          </div>
        </div>
      </CardHeader>
      
      <CardBody>
        {/* Core Explanation */}
        <div className="mb-4">
          <div className="prose max-w-none">
            <ReactMarkdown>{explanation.explanation.core}</ReactMarkdown>
          </div>
        </div>
        
        {/* Action Items */}
        {explanation.explanation.actions.length > 0 && (
          <div className="mb-4">
            <h4 className="font-semibold text-gray-700 mb-2">🎯 Action Items</h4>
            <ul className="space-y-2">
              {explanation.explanation.actions.map((action, index) => (
                <li key={index} className="flex items-start gap-2">
                  <CheckCircleIcon className="w-4 h-4 text-green-500 mt-1" />
                  <span className="text-sm">{action}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {/* Expandable Details */}
        <div className="border-t pt-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowDetails(!showDetails)}
            className="mb-2"
          >
            {showDetails ? 'Hide' : 'Show'} Details
            <ChevronDownIcon className={`w-4 h-4 ml-1 transform ${showDetails ? 'rotate-180' : ''}`} />
          </Button>
          
          {showDetails && (
            <div className="space-y-4">
              {/* Supporting Evidence */}
              {explanation.explanation.details.supporting_evidence && (
                <div>
                  <h5 className="font-medium text-gray-700 mb-2">📊 Supporting Evidence</h5>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {explanation.explanation.details.supporting_evidence.map((evidence, index) => (
                      <li key={index}>• {evidence}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Risk Factors */}
              {explanation.explanation.details.risk_factors && (
                <div>
                  <h5 className="font-medium text-gray-700 mb-2">⚠️ Risk Factors</h5>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {explanation.explanation.details.risk_factors.map((risk, index) => (
                      <li key={index}>• {risk}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Historical Context */}
              {explanation.explanation.details.historical_context && (
                <div>
                  <h5 className="font-medium text-gray-700 mb-2">📚 Historical Context</h5>
                  <p className="text-sm text-gray-600">
                    {explanation.explanation.details.historical_context}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </CardBody>
    </Card>
  );
};

// ComplexitySelector.tsx
const ComplexitySelector: React.FC<{
  value: string;
  onChange: (value: string) => void;
}> = ({ value, onChange }) => {
  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger className="w-32">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="beginner">
          <div className="flex items-center gap-2">
            <AcademicCapIcon className="w-4 h-4" />
            Beginner
          </div>
        </SelectItem>
        <SelectItem value="intermediate">
          <div className="flex items-center gap-2">
            <ChartBarIcon className="w-4 h-4" />
            Intermediate
          </div>
        </SelectItem>
        <SelectItem value="advanced">
          <div className="flex items-center gap-2">
            <CogIcon className="w-4 h-4" />
            Advanced
          </div>
        </SelectItem>
      </SelectContent>
    </Select>
  );
};
```

## 🧪 Explanation Templates

```python
# Explanation templates for different scenarios
EXPLANATION_TEMPLATES = {
    'bullish_recommendation': {
        'opening': "We recommend buying {symbol} based on {primary_factor}.",
        'reasoning': "Our analysis shows {key_evidence}.",
        'expectations': "We expect {expected_outcome} over {time_horizon}.",
        'risks': "Key risks include {main_risks}.",
        'actions': "Consider {recommended_actions}."
    },
    'bearish_recommendation': {
        'opening': "We recommend selling {symbol} due to {primary_concern}.",
        'reasoning': "Our analysis reveals {warning_signals}.",
        'expectations': "We anticipate {negative_outcome} in the {time_horizon}.",
        'alternatives': "Better opportunities may be found in {alternatives}.",
        'actions': "We suggest {exit_strategy}."
    },
    'neutral_recommendation': {
        'opening': "We recommend holding {symbol} at current levels.",
        'reasoning': "While {positive_factors}, we also note {negative_factors}.",
        'monitoring': "Key metrics to watch include {key_metrics}.",
        'triggers': "We would upgrade to buy if {bullish_triggers}.",
        'actions': "Continue monitoring {monitoring_points}."
    }
}
```

## 📈 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Explanation clarity rating | >8.5/10 | - |
| User comprehension score | >85% | - |
| Action item adoption rate | >60% | - |
| Explanation request frequency | <20% | - |
| User satisfaction with explanations | >8/10 | - |

---

**Next**: Continue with presentation layer documentation.