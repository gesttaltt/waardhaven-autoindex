# 🔍 Opportunity Scanner

**Priority**: HIGH  
**Complexity**: High  
**Timeline**: 4-5 days  
**Value**: Real-time detection of high-potential investment opportunities

## 🎯 Objective

Build an intelligent opportunity scanning system that:
- Continuously monitors markets for emerging opportunities
- Identifies patterns that precede significant price movements
- Finds undervalued assets before they become popular
- Detects catalyst-driven opportunities
- Ranks opportunities by potential and probability

## 🔍 Opportunity Categories

### Opportunity Types
```python
OPPORTUNITY_TYPES = {
    'value_opportunities': {
        'deep_value': {
            'description': 'Severely undervalued quality companies',
            'criteria': 'P/E < 10, P/B < 1, Strong fundamentals',
            'typical_return': '20-50%',
            'time_horizon': '6-18 months',
            'risk_level': 'Medium'
        },
        'sum_of_parts': {
            'description': 'Conglomerates trading below asset value',
            'criteria': 'Market cap < sum of divisions',
            'typical_return': '15-30%',
            'time_horizon': '12-24 months',
            'risk_level': 'Medium-High'
        },
        'net_cash_plays': {
            'description': 'Companies with cash > market cap',
            'criteria': 'Net cash per share > stock price',
            'typical_return': '10-25%',
            'time_horizon': '3-12 months',
            'risk_level': 'Low-Medium'
        }
    },
    'catalyst_opportunities': {
        'earnings_surprise': {
            'description': 'Stocks likely to beat earnings',
            'criteria': 'Leading indicators suggest beat',
            'typical_return': '5-15%',
            'time_horizon': '1-3 months',
            'risk_level': 'Medium'
        },
        'merger_arbitrage': {
            'description': 'M&A deals with favorable spreads',
            'criteria': 'Announced deals, reasonable spread',
            'typical_return': '3-8%',
            'time_horizon': '3-12 months',
            'risk_level': 'Medium'
        },
        'spinoff_value': {
            'description': 'Value creation from spinoffs',
            'criteria': 'Announced spinoffs, forced selling',
            'typical_return': '10-30%',
            'time_horizon': '6-18 months',
            'risk_level': 'Medium'
        }
    },
    'momentum_opportunities': {
        'breakout_candidates': {
            'description': 'Technical breakouts with volume',
            'criteria': 'Breaking resistance, high volume',
            'typical_return': '8-20%',
            'time_horizon': '1-6 months',
            'risk_level': 'High'
        },
        'earnings_momentum': {
            'description': 'Accelerating fundamental trends',
            'criteria': 'Rising estimates, revenue acceleration',
            'typical_return': '15-40%',
            'time_horizon': '3-12 months',
            'risk_level': 'Medium-High'
        },
        'sector_rotation': {
            'description': 'Early sector rotation plays',
            'criteria': 'Sector showing relative strength',
            'typical_return': '10-25%',
            'time_horizon': '3-9 months',
            'risk_level': 'Medium'
        }
    }
}
```

## 🧠 Scanning Engine Architecture

```python
# app/intelligence/opportunity_scanner.py

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

class OpportunityScanner:
    """Real-time opportunity detection system"""
    
    def __init__(self):
        self.scanners = {
            'value_scanner': ValueOpportunityScanner(),
            'catalyst_scanner': CatalystOpportunityScanner(),
            'momentum_scanner': MomentumOpportunityScanner(),
            'insider_scanner': InsiderOpportunityScanner(),
            'technical_scanner': TechnicalOpportunityScanner()
        }
        self.universe_manager = UniverseManager()
        self.opportunity_ranker = OpportunityRanker()
        
    async def scan_all_opportunities(self, universe: List[str] = None) -> Dict:
        """Run comprehensive opportunity scan"""
        
        if universe is None:
            universe = await self.universe_manager.get_scannable_universe()
        
        print(f"Scanning {len(universe)} symbols for opportunities")
        
        # Run all scanners in parallel
        scanning_tasks = {
            scanner_name: scanner.scan(universe)
            for scanner_name, scanner in self.scanners.items()
        }
        
        scanner_results = await asyncio.gather(
            *scanning_tasks.values(),
            return_exceptions=True
        )
        
        # Combine results
        all_opportunities = []
        for scanner_name, results in zip(scanning_tasks.keys(), scanner_results):
            if not isinstance(results, Exception):
                for opportunity in results:
                    opportunity['scanner'] = scanner_name
                    opportunity['scan_timestamp'] = datetime.now()
                all_opportunities.extend(results)
        
        # Rank and filter opportunities
        ranked_opportunities = await self.opportunity_ranker.rank_opportunities(all_opportunities)
        
        # Filter for quality
        quality_opportunities = self.filter_quality_opportunities(ranked_opportunities)
        
        return {
            'total_scanned': len(universe),
            'opportunities_found': len(all_opportunities),
            'quality_opportunities': len(quality_opportunities),
            'top_opportunities': quality_opportunities[:20],  # Top 20
            'scan_summary': self.generate_scan_summary(all_opportunities),
            'scan_timestamp': datetime.now()
        }
    
    def filter_quality_opportunities(self, opportunities: List[Dict]) -> List[Dict]:
        """Filter for high-quality opportunities"""
        
        quality_ops = []
        
        for opp in opportunities:
            # Minimum score threshold
            if opp.get('overall_score', 0) < 60:
                continue
            
            # Minimum confidence threshold
            if opp.get('confidence', 0) < 0.6:
                continue
            
            # Minimum liquidity threshold
            if opp.get('avg_daily_volume', 0) < 100000:  # 100k shares
                continue
            
            # Risk-adjusted return threshold
            risk_adjusted_return = opp.get('expected_return', 0) / max(opp.get('risk_score', 50), 20)
            if risk_adjusted_return < 0.2:  # 20% return per unit of risk
                continue
            
            quality_ops.append(opp)
        
        return quality_ops

class ValueOpportunityScanner:
    """Scan for value investment opportunities"""
    
    async def scan(self, universe: List[str]) -> List[Dict]:
        """Scan for value opportunities"""
        
        opportunities = []
        
        for symbol in universe:
            try:
                value_opportunity = await self.analyze_value_opportunity(symbol)
                if value_opportunity:
                    opportunities.append(value_opportunity)
            except Exception as e:
                logger.warning(f"Error scanning {symbol} for value: {e}")
        
        return opportunities
    
    async def analyze_value_opportunity(self, symbol: str) -> Optional[Dict]:
        """Analyze individual symbol for value opportunity"""
        
        # Get fundamental data
        fundamentals = await self.get_fundamentals(symbol)
        if not fundamentals:
            return None
        
        # Get price data
        price_data = await self.get_price_data(symbol)
        current_price = price_data['current_price']
        
        value_signals = []
        value_score = 0
        
        # P/E ratio analysis
        pe_ratio = fundamentals.get('pe_ratio')
        if pe_ratio and pe_ratio > 0:
            if pe_ratio < 8:  # Very cheap
                value_signals.append('Extremely low P/E ratio')
                value_score += 25
            elif pe_ratio < 12:
                value_signals.append('Low P/E ratio')
                value_score += 15
        
        # P/B ratio analysis
        pb_ratio = fundamentals.get('pb_ratio')
        if pb_ratio and pb_ratio > 0:
            if pb_ratio < 0.8:  # Below book value
                value_signals.append('Trading below book value')
                value_score += 20
            elif pb_ratio < 1.2:
                value_signals.append('Low price-to-book ratio')
                value_score += 10
        
        # Free cash flow yield
        market_cap = fundamentals.get('market_cap', 0)
        fcf = fundamentals.get('free_cash_flow', 0)
        if market_cap > 0 and fcf > 0:
            fcf_yield = fcf / market_cap
            if fcf_yield > 0.15:  # 15% FCF yield
                value_signals.append('High free cash flow yield')
                value_score += 20
            elif fcf_yield > 0.10:
                value_signals.append('Good free cash flow yield')
                value_score += 10
        
        # Debt analysis
        debt_to_equity = fundamentals.get('debt_to_equity', 0)
        if debt_to_equity < 0.3:
            value_signals.append('Low debt levels')
            value_score += 10
        
        # ROE analysis
        roe = fundamentals.get('roe', 0)
        if roe > 0.15:
            value_signals.append('Strong return on equity')
            value_score += 15
        elif roe > 0.10:
            value_signals.append('Good return on equity')
            value_score += 8
        
        # Net cash analysis
        cash = fundamentals.get('cash_and_equivalents', 0)
        total_debt = fundamentals.get('total_debt', 0)
        shares_outstanding = fundamentals.get('shares_outstanding', 1)
        
        net_cash_per_share = (cash - total_debt) / shares_outstanding
        if net_cash_per_share > current_price * 0.2:  # Net cash > 20% of price
            value_signals.append('Significant net cash position')
            value_score += 25
        
        # Quality filters
        if not self.passes_quality_filters(fundamentals):
            return None
        
        # Minimum value score threshold
        if value_score < 30:
            return None
        
        # Calculate intrinsic value estimate
        intrinsic_value = self.estimate_intrinsic_value(fundamentals)
        upside_potential = (intrinsic_value - current_price) / current_price if intrinsic_value else 0
        
        return {
            'symbol': symbol,
            'opportunity_type': 'value',
            'subtype': 'deep_value' if value_score > 60 else 'value',
            'overall_score': min(100, value_score),
            'confidence': 0.7 if value_score > 50 else 0.6,
            'expected_return': min(0.5, max(0.05, upside_potential)),  # Cap at 50%
            'time_horizon': '12-18 months',
            'value_signals': value_signals,
            'current_price': current_price,
            'intrinsic_value': intrinsic_value,
            'upside_potential': upside_potential,
            'key_metrics': {
                'pe_ratio': pe_ratio,
                'pb_ratio': pb_ratio,
                'fcf_yield': fcf_yield,
                'debt_to_equity': debt_to_equity,
                'roe': roe
            }
        }
    
    def estimate_intrinsic_value(self, fundamentals: Dict) -> Optional[float]:
        """Estimate intrinsic value using multiple methods"""
        
        # DCF-based estimate
        fcf = fundamentals.get('free_cash_flow', 0)
        growth_rate = fundamentals.get('fcf_growth_rate', 0.03)  # Conservative 3%
        discount_rate = 0.10  # 10% discount rate
        terminal_growth = 0.02  # 2% terminal growth
        
        if fcf > 0:
            # Simple DCF calculation
            terminal_value = fcf * (1 + growth_rate) / (discount_rate - terminal_growth)
            shares_outstanding = fundamentals.get('shares_outstanding', 1)
            dcf_value = terminal_value / shares_outstanding
            
            return dcf_value
        
        return None
    
    def passes_quality_filters(self, fundamentals: Dict) -> bool:
        """Check if company passes quality filters"""
        
        # Profitable in recent years
        if fundamentals.get('net_income', 0) <= 0:
            return False
        
        # Positive book value
        if fundamentals.get('book_value', 0) <= 0:
            return False
        
        # Not too much debt
        if fundamentals.get('debt_to_equity', 0) > 2.0:
            return False
        
        # Reasonable current ratio
        if fundamentals.get('current_ratio', 0) < 1.0:
            return False
        
        return True

class CatalystOpportunityScanner:
    """Scan for catalyst-driven opportunities"""
    
    async def scan(self, universe: List[str]) -> List[Dict]:
        """Scan for catalyst opportunities"""
        
        opportunities = []
        
        # Get upcoming catalysts
        catalysts = await self.get_upcoming_catalysts(universe)
        
        for catalyst in catalysts:
            try:
                opportunity = await self.analyze_catalyst_opportunity(catalyst)
                if opportunity:
                    opportunities.append(opportunity)
            except Exception as e:
                logger.warning(f"Error analyzing catalyst for {catalyst.get('symbol')}: {e}")
        
        return opportunities
    
    async def analyze_catalyst_opportunity(self, catalyst: Dict) -> Optional[Dict]:
        """Analyze catalyst opportunity"""
        
        symbol = catalyst['symbol']
        catalyst_type = catalyst['type']
        catalyst_date = catalyst['date']
        
        # Get historical catalyst performance
        historical_performance = await self.get_historical_catalyst_performance(
            symbol, catalyst_type
        )
        
        # Analyze current setup
        current_setup = await self.analyze_current_setup(symbol, catalyst)
        
        if not current_setup or not historical_performance:
            return None
        
        # Calculate opportunity score
        opportunity_score = self.calculate_catalyst_score(
            catalyst, historical_performance, current_setup
        )
        
        if opportunity_score < 50:
            return None
        
        return {
            'symbol': symbol,
            'opportunity_type': 'catalyst',
            'subtype': catalyst_type,
            'catalyst_date': catalyst_date,
            'days_to_catalyst': (catalyst_date - datetime.now()).days,
            'overall_score': opportunity_score,
            'confidence': historical_performance.get('reliability', 0.6),
            'expected_return': historical_performance.get('avg_return', 0.05),
            'historical_success_rate': historical_performance.get('success_rate', 0.5),
            'current_setup': current_setup,
            'catalyst_details': catalyst
        }

class MomentumOpportunityScanner:
    """Scan for momentum opportunities"""
    
    async def scan(self, universe: List[str]) -> List[Dict]:
        """Scan for momentum opportunities"""
        
        opportunities = []
        
        for symbol in universe:
            try:
                momentum_opp = await self.analyze_momentum_opportunity(symbol)
                if momentum_opp:
                    opportunities.append(momentum_opp)
            except Exception as e:
                logger.warning(f"Error scanning {symbol} for momentum: {e}")
        
        return opportunities
    
    async def analyze_momentum_opportunity(self, symbol: str) -> Optional[Dict]:
        """Analyze momentum opportunity"""
        
        # Get price and volume data
        price_data = await self.get_extended_price_data(symbol)
        if len(price_data) < 50:
            return None
        
        momentum_signals = []
        momentum_score = 0
        
        # Price momentum analysis
        returns_1m = (price_data['close'][-1] / price_data['close'][-21] - 1)
        returns_3m = (price_data['close'][-1] / price_data['close'][-63] - 1)
        returns_6m = (price_data['close'][-1] / price_data['close'][-126] - 1)
        
        # Strong recent momentum
        if returns_1m > 0.15:  # 15% in 1 month
            momentum_signals.append('Strong 1-month momentum')
            momentum_score += 20
        elif returns_1m > 0.08:
            momentum_signals.append('Good 1-month momentum')
            momentum_score += 10
        
        # Volume momentum
        avg_volume_recent = np.mean(price_data['volume'][-10:])
        avg_volume_base = np.mean(price_data['volume'][-60:-10])
        volume_ratio = avg_volume_recent / avg_volume_base if avg_volume_base > 0 else 1
        
        if volume_ratio > 2.0:  # Volume surge
            momentum_signals.append('Volume surge detected')
            momentum_score += 15
        elif volume_ratio > 1.5:
            momentum_signals.append('Increased volume')
            momentum_score += 8
        
        # Relative strength vs market
        market_returns = await self.get_market_returns(len(price_data))
        if market_returns is not None:
            relative_strength_1m = returns_1m - market_returns[-21:].sum()
            if relative_strength_1m > 0.05:  # Outperforming by 5%
                momentum_signals.append('Outperforming market')
                momentum_score += 15
        
        # Earnings momentum
        earnings_revisions = await self.get_earnings_revisions(symbol)
        if earnings_revisions:
            if earnings_revisions['direction'] == 'up' and earnings_revisions['magnitude'] > 0.05:
                momentum_signals.append('Earnings estimates rising')
                momentum_score += 20
        
        # Technical breakout
        breakout = self.detect_technical_breakout(price_data)
        if breakout:
            momentum_signals.append(f'Technical breakout: {breakout["type"]}')
            momentum_score += 25
        
        # Minimum threshold
        if momentum_score < 40:
            return None
        
        return {
            'symbol': symbol,
            'opportunity_type': 'momentum',
            'subtype': 'price_momentum',
            'overall_score': min(100, momentum_score),
            'confidence': 0.65,
            'expected_return': min(0.25, max(0.08, returns_1m * 2)),  # Momentum continuation
            'time_horizon': '3-6 months',
            'momentum_signals': momentum_signals,
            'key_metrics': {
                'returns_1m': returns_1m,
                'returns_3m': returns_3m,
                'volume_ratio': volume_ratio,
                'relative_strength_1m': locals().get('relative_strength_1m', 0)
            }
        }
```

## 📊 Opportunity Ranking System

```python
class OpportunityRanker:
    """Rank and prioritize opportunities"""
    
    def __init__(self):
        self.ranking_weights = {
            'expected_return': 0.30,
            'confidence': 0.25,
            'risk_adjusted_return': 0.20,
            'time_to_catalyst': 0.15,
            'liquidity': 0.10
        }
    
    async def rank_opportunities(self, opportunities: List[Dict]) -> List[Dict]:
        """Rank opportunities by attractiveness"""
        
        for opp in opportunities:
            # Calculate composite ranking score
            ranking_score = await self.calculate_ranking_score(opp)
            opp['ranking_score'] = ranking_score
            
            # Add risk-adjusted metrics
            opp['sharpe_estimate'] = self.estimate_sharpe_ratio(opp)
            opp['risk_adjusted_score'] = opp['overall_score'] / max(opp.get('risk_score', 50), 20)
        
        # Sort by ranking score
        ranked_opportunities = sorted(
            opportunities, 
            key=lambda x: x['ranking_score'], 
            reverse=True
        )
        
        return ranked_opportunities
    
    async def calculate_ranking_score(self, opportunity: Dict) -> float:
        """Calculate composite ranking score"""
        
        scores = {}
        
        # Expected return score (0-100)
        expected_return = opportunity.get('expected_return', 0)
        scores['expected_return'] = min(100, expected_return * 500)  # Scale to 0-100
        
        # Confidence score (0-100)
        confidence = opportunity.get('confidence', 0.5)
        scores['confidence'] = confidence * 100
        
        # Risk-adjusted return
        risk_score = opportunity.get('risk_score', 50)
        risk_adjusted = expected_return * 100 / max(risk_score, 20)
        scores['risk_adjusted_return'] = min(100, risk_adjusted * 20)
        
        # Time to catalyst (shorter is better for some opportunity types)
        if 'days_to_catalyst' in opportunity:
            days = opportunity['days_to_catalyst']
            if days <= 30:
                scores['time_to_catalyst'] = 90  # Soon
            elif days <= 90:
                scores['time_to_catalyst'] = 70  # Medium term
            else:
                scores['time_to_catalyst'] = 40  # Long term
        else:
            scores['time_to_catalyst'] = 60  # No specific catalyst
        
        # Liquidity score
        volume = opportunity.get('avg_daily_volume', 0)
        if volume > 1_000_000:
            scores['liquidity'] = 90  # Very liquid
        elif volume > 500_000:
            scores['liquidity'] = 75  # Good liquidity
        elif volume > 100_000:
            scores['liquidity'] = 60  # Adequate
        else:
            scores['liquidity'] = 30  # Poor liquidity
        
        # Calculate weighted score
        ranking_score = sum(
            scores[component] * self.ranking_weights[component]
            for component in self.ranking_weights
            if component in scores
        )
        
        return ranking_score
```

## 🎨 Opportunity Scanner UI

```typescript
// OpportunityScannerDashboard.tsx

const OpportunityScannerDashboard = () => {
  return (
    <div className="opportunity-scanner">
      {/* Scan Controls */}
      <Card>
        <CardHeader>
          <Title>🔍 Opportunity Scanner</Title>
          <Button onClick={runFullScan} loading={isScanning}>
            Run Full Scan
          </Button>
        </CardHeader>
        <CardBody>
          <ScanProgress progress={scanProgress} />
          <ScanFilters filters={scanFilters} onChange={setScanFilters} />
        </CardBody>
      </Card>
      
      {/* Top Opportunities */}
      <Card>
        <CardHeader>
          <Title>🏆 Top Opportunities</Title>
          <Badge>{topOpportunities.length} Found</Badge>
        </CardHeader>
        <CardBody>
          <OpportunityList 
            opportunities={topOpportunities}
            showDetails={true}
            onSelect={handleOpportunitySelect}
          />
        </CardBody>
      </Card>
      
      {/* Opportunity Categories */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <Title>💎 Value Opportunities</Title>
          </CardHeader>
          <CardBody>
            <CategorySummary 
              opportunities={valueOpportunities}
              type="value"
            />
          </CardBody>
        </Card>
        
        <Card>
          <CardHeader>
            <Title>⚡ Catalyst Opportunities</Title>
          </CardHeader>
          <CardBody>
            <CategorySummary 
              opportunities={catalystOpportunities}
              type="catalyst"
            />
          </CardBody>
        </Card>
        
        <Card>
          <CardHeader>
            <Title>🚀 Momentum Opportunities</Title>
          </CardHeader>
          <CardBody>
            <CategorySummary 
              opportunities={momentumOpportunities}
              type="momentum"
            />
          </CardBody>
        </Card>
      </div>
      
      {/* Scan History */}
      <Card>
        <CardHeader>
          <Title>📊 Scan Performance</Title>
        </CardHeader>
        <CardBody>
          <ScanPerformanceChart data={scanPerformanceHistory} />
          <OpportunitySuccessRate successRates={successRates} />
        </CardBody>
      </Card>
    </div>
  );
};

// OpportunityCard.tsx
const OpportunityCard: React.FC<{ opportunity: Opportunity }> = ({ opportunity }) => {
  const getTypeColor = (type: string) => {
    const colors = {
      value: 'bg-blue-50 text-blue-700',
      catalyst: 'bg-green-50 text-green-700',
      momentum: 'bg-purple-50 text-purple-700'
    };
    return colors[type] || colors.value;
  };

  return (
    <Card className="opportunity-card">
      <CardHeader>
        <div className="flex justify-between items-center">
          <h3 className="text-xl font-bold">{opportunity.symbol}</h3>
          <Badge className={getTypeColor(opportunity.opportunityType)}>
            {opportunity.opportunityType.toUpperCase()}
          </Badge>
        </div>
        <div className="flex items-center gap-4 mt-2">
          <ScoreIndicator value={opportunity.overallScore} />
          <ConfidenceIndicator value={opportunity.confidence} />
        </div>
      </CardHeader>
      
      <CardBody>
        {/* Expected Return */}
        <div className="mb-4">
          <h4 className="font-semibold text-gray-700">Expected Return</h4>
          <span className="text-2xl font-bold text-green-600">
            +{(opportunity.expectedReturn * 100).toFixed(1)}%
          </span>
          <p className="text-sm text-gray-500">
            Time Horizon: {opportunity.timeHorizon}
          </p>
        </div>
        
        {/* Key Signals */}
        <div className="mb-4">
          <h4 className="font-semibold text-gray-700 mb-2">Key Signals</h4>
          <ul className="space-y-1">
            {opportunity.keySignals?.map((signal, index) => (
              <li key={index} className="flex items-start gap-2">
                <TrendingUpIcon className="w-4 h-4 text-green-500 mt-0.5" />
                <span className="text-sm">{signal}</span>
              </li>
            ))}
          </ul>
        </div>
        
        <div className="flex gap-2 pt-4 border-t">
          <Button variant="primary" size="sm">
            View Analysis
          </Button>
          <Button variant="outline" size="sm">
            Add Alert
          </Button>
        </div>
      </CardBody>
    </Card>
  );
};
```

## 📈 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Opportunities identified/day | >50 | - |
| Top 10 opportunity success rate | >45% | - |
| Average opportunity return | >12% | - |
| False positive rate | <30% | - |
| Scan completion time | <5 minutes | - |

---

**Next**: Continue with portfolio optimizer.