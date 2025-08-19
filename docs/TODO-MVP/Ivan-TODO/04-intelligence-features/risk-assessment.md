# ⚠️ Risk Assessment Engine

**Priority**: HIGH  
**Complexity**: Very High  
**Timeline**: 4-5 days  
**Value**: Protect users from significant losses through comprehensive risk analysis

## 🎯 Objective

Build a comprehensive risk assessment system that:
- Identifies and quantifies various types of investment risk
- Provides early warning of potential losses
- Suggests risk mitigation strategies
- Monitors portfolio-level risk exposure
- Adapts to changing market conditions

## 🔥 Risk Categories

### Risk Taxonomy
```python
RISK_CATEGORIES = {
    'market_risk': {
        'description': 'Risk from overall market movements',
        'measurement': 'Beta, correlation to market indices',
        'mitigation': 'Diversification, hedging',
        'typical_impact': '20-40% in bear markets'
    },
    'company_specific_risk': {
        'description': 'Risk unique to individual company',
        'measurement': 'Idiosyncratic volatility, fundamental metrics',
        'mitigation': 'Diversification, position sizing',
        'typical_impact': '5-50% from company events'
    },
    'liquidity_risk': {
        'description': 'Risk of not being able to sell at fair price',
        'measurement': 'Average daily volume, bid-ask spread',
        'mitigation': 'Avoid low-volume stocks, gradual exit',
        'typical_impact': '2-10% additional transaction costs'
    },
    'event_risk': {
        'description': 'Risk from specific upcoming events',
        'measurement': 'Earnings date proximity, option volatility',
        'mitigation': 'Timing adjustments, hedging',
        'typical_impact': '10-30% on event outcomes'
    },
    'concentration_risk': {
        'description': 'Risk from over-concentration in few positions',
        'measurement': 'Position sizes, correlation between holdings',
        'mitigation': 'Diversification limits, rebalancing',
        'typical_impact': 'Amplified losses during downturns'
    },
    'regime_risk': {
        'description': 'Risk from changing market regimes',
        'measurement': 'Regime detection models, factor loadings',
        'mitigation': 'Adaptive strategies, regime awareness',
        'typical_impact': 'Strategy underperformance in new regime'
    }
}
```

## 🧮 Risk Measurement Framework

### Core Risk Metrics
```python
RISK_METRICS = {
    'value_at_risk': {
        'var_1d_95': 'Maximum 1-day loss at 95% confidence',
        'var_1d_99': 'Maximum 1-day loss at 99% confidence',
        'var_30d_95': 'Maximum 30-day loss at 95% confidence'
    },
    'expected_shortfall': {
        'es_1d_95': 'Average loss beyond VaR (1-day, 95%)',
        'es_30d_95': 'Average loss beyond VaR (30-day, 95%)'
    },
    'volatility_measures': {
        'realized_vol_30d': 'Historical 30-day volatility',
        'implied_vol': 'Options-implied volatility',
        'vol_of_vol': 'Volatility of volatility (uncertainty)'
    },
    'downside_measures': {
        'max_drawdown': 'Maximum peak-to-trough decline',
        'downside_deviation': 'Standard deviation of negative returns',
        'sortino_ratio': 'Return per unit of downside risk'
    }
}
```

## 💾 Risk Database Schema

```sql
-- Risk assessments storage
CREATE TABLE risk_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    symbol VARCHAR(20) NOT NULL,
    assessment_date TIMESTAMP NOT NULL,
    
    -- Overall risk scores (0-100)
    overall_risk_score DECIMAL(5,2),
    market_risk_score DECIMAL(5,2),
    company_risk_score DECIMAL(5,2),
    liquidity_risk_score DECIMAL(5,2),
    event_risk_score DECIMAL(5,2),
    
    -- VaR calculations
    var_1d_95 DECIMAL(8,4),
    var_1d_99 DECIMAL(8,4),
    var_30d_95 DECIMAL(8,4),
    expected_shortfall_1d DECIMAL(8,4),
    
    -- Volatility measures
    realized_volatility_30d DECIMAL(8,4),
    implied_volatility DECIMAL(8,4),
    volatility_percentile DECIMAL(5,2),
    
    -- Downside measures
    max_drawdown_1y DECIMAL(8,4),
    downside_deviation_30d DECIMAL(8,4),
    
    -- Specific risk factors
    earnings_risk DECIMAL(5,2), -- Risk from upcoming earnings
    liquidity_score DECIMAL(5,2), -- Higher = more liquid
    concentration_impact DECIMAL(8,4), -- Impact on portfolio if position goes to zero
    
    -- Market environment
    market_regime VARCHAR(50),
    sector_risk_level VARCHAR(20),
    
    -- Risk warnings
    active_warnings JSONB, -- Array of current warnings
    risk_explanation TEXT,
    mitigation_suggestions JSONB,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(symbol, assessment_date)
);

-- Portfolio risk tracking
CREATE TABLE portfolio_risk (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    user_id UUID NOT NULL,
    assessment_date TIMESTAMP NOT NULL,
    
    -- Portfolio-level risk
    portfolio_var_1d_95 DECIMAL(8,4),
    portfolio_beta DECIMAL(6,4),
    portfolio_volatility DECIMAL(8,4),
    
    -- Diversification metrics
    effective_positions INTEGER, -- Diversification-adjusted position count
    correlation_risk_score DECIMAL(5,2),
    sector_concentration JSONB, -- Concentration by sector
    
    -- Concentration warnings
    max_position_size DECIMAL(5,4),
    positions_over_5pct INTEGER,
    positions_over_10pct INTEGER,
    
    -- Risk attribution
    risk_contribution JSONB, -- Risk contribution by position
    top_risk_contributors TEXT[], -- Symbols contributing most risk
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Risk events and warnings
CREATE TABLE risk_warnings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    symbol VARCHAR(20),
    user_id UUID,
    
    warning_type VARCHAR(100),
    severity VARCHAR(20), -- low, medium, high, critical
    
    -- Warning details
    title VARCHAR(255),
    description TEXT,
    risk_score DECIMAL(5,2),
    
    -- Timing
    triggered_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    acknowledged_at TIMESTAMP,
    
    -- Context
    trigger_data JSONB,
    suggested_actions JSONB,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔧 Risk Assessment Engine

```python
# app/intelligence/risk_assessor.py

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio

class ComprehensiveRiskAssessor:
    """Advanced risk assessment engine"""
    
    def __init__(self):
        self.market_data_client = MarketDataClient()
        self.options_data_client = OptionsDataClient()
        self.fundamental_client = FundamentalDataClient()
        self.regime_detector = MarketRegimeDetector()
        
    async def assess_symbol_risk(self, symbol: str, context_data: Dict = None) -> Dict:
        """Comprehensive risk assessment for individual symbol"""
        
        print(f"Assessing risk for {symbol}")
        
        # Gather risk-relevant data
        risk_data = await self.gather_risk_data(symbol)
        
        # Calculate individual risk components
        risk_components = {
            'market_risk': await self.assess_market_risk(symbol, risk_data),
            'company_risk': await self.assess_company_specific_risk(symbol, risk_data),
            'liquidity_risk': await self.assess_liquidity_risk(symbol, risk_data),
            'event_risk': await self.assess_event_risk(symbol, risk_data),
            'volatility_risk': await self.assess_volatility_risk(symbol, risk_data)
        }
        
        # Calculate VaR and other risk metrics
        var_metrics = await self.calculate_var_metrics(symbol, risk_data)
        
        # Generate risk warnings
        warnings = await self.generate_risk_warnings(symbol, risk_components, var_metrics)
        
        # Overall risk assessment
        overall_assessment = self.calculate_overall_risk(
            risk_components, 
            var_metrics, 
            warnings
        )
        
        # Risk mitigation suggestions
        mitigation = self.suggest_risk_mitigation(
            symbol, 
            risk_components, 
            overall_assessment
        )
        
        return {
            'symbol': symbol,
            'assessment_date': datetime.now(),
            'overall_risk': overall_assessment,
            'risk_components': risk_components,
            'var_metrics': var_metrics,
            'warnings': warnings,
            'mitigation_suggestions': mitigation,
            'risk_explanation': self.generate_risk_explanation(
                symbol, risk_components, overall_assessment
            )
        }
    
    async def assess_market_risk(self, symbol: str, risk_data: Dict) -> Dict:
        """Assess market risk (systematic risk)"""
        
        # Get price history
        prices = risk_data['price_history']
        market_prices = risk_data['market_index_history']  # S&P 500
        
        # Calculate returns
        returns = prices.pct_change().dropna()
        market_returns = market_prices.pct_change().dropna()
        
        # Align the series
        aligned_data = pd.concat([returns, market_returns], axis=1, join='inner')
        stock_returns = aligned_data.iloc[:, 0]
        market_returns = aligned_data.iloc[:, 1]
        
        # Calculate beta
        beta = np.cov(stock_returns, market_returns)[0, 1] / np.var(market_returns)
        
        # Calculate correlation
        correlation = np.corrcoef(stock_returns, market_returns)[0, 1]
        
        # Calculate R-squared (explained variance)
        r_squared = correlation ** 2
        
        # Market risk score (0-100)
        # Higher beta and correlation = higher market risk
        market_risk_score = min(100, max(0, 
            50 + (beta - 1) * 25 + (correlation - 0.5) * 50
        ))
        
        return {
            'beta': beta,
            'correlation_to_market': correlation,
            'r_squared': r_squared,
            'market_risk_score': market_risk_score,
            'systematic_risk_pct': r_squared * 100,
            'idiosyncratic_risk_pct': (1 - r_squared) * 100
        }
    
    async def assess_company_specific_risk(self, symbol: str, risk_data: Dict) -> Dict:
        """Assess company-specific (idiosyncratic) risk"""
        
        company_risk_factors = {
            'financial_health': 0,
            'business_model': 0,
            'management': 0,
            'competitive_position': 0
        }
        
        fundamentals = risk_data.get('fundamentals', {})
        
        # Financial health assessment
        debt_to_equity = fundamentals.get('debt_to_equity', 0.5)
        interest_coverage = fundamentals.get('interest_coverage', 5)
        current_ratio = fundamentals.get('current_ratio', 1.5)
        
        # Higher debt = higher risk
        if debt_to_equity > 1.0:
            company_risk_factors['financial_health'] += 25
        elif debt_to_equity > 0.6:
            company_risk_factors['financial_health'] += 10
        
        # Low interest coverage = higher risk
        if interest_coverage < 2.5:
            company_risk_factors['financial_health'] += 20
        elif interest_coverage < 5:
            company_risk_factors['financial_health'] += 10
        
        # Business model risk (sector-specific)
        sector = risk_data.get('sector', 'Unknown')
        sector_risk_multiplier = {
            'Technology': 1.2,
            'Biotechnology': 1.5,
            'Energy': 1.3,
            'Utilities': 0.8,
            'Consumer Staples': 0.9
        }.get(sector, 1.0)
        
        # Calculate idiosyncratic volatility
        returns = risk_data['price_history'].pct_change().dropna()
        market_returns = risk_data['market_index_history'].pct_change().dropna()
        
        # Regression residuals represent idiosyncratic risk
        aligned_data = pd.concat([returns, market_returns], axis=1, join='inner')
        if len(aligned_data) > 30:
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                aligned_data.iloc[:, 1], aligned_data.iloc[:, 0]
            )
            predicted_returns = intercept + slope * aligned_data.iloc[:, 1]
            residuals = aligned_data.iloc[:, 0] - predicted_returns
            idiosyncratic_vol = residuals.std() * np.sqrt(252)  # Annualized
        else:
            idiosyncratic_vol = returns.std() * np.sqrt(252) * 0.5  # Rough estimate
        
        # Company risk score
        base_score = sum(company_risk_factors.values())
        volatility_adjustment = min(30, idiosyncratic_vol * 100)  # Cap at 30
        sector_adjustment = (sector_risk_multiplier - 1) * 20
        
        company_risk_score = min(100, max(0, 
            base_score + volatility_adjustment + sector_adjustment
        ))
        
        return {
            'company_risk_score': company_risk_score,
            'idiosyncratic_volatility': idiosyncratic_vol,
            'financial_health_risk': company_risk_factors['financial_health'],
            'sector_risk_multiplier': sector_risk_multiplier,
            'key_risk_factors': self.identify_key_company_risks(fundamentals, sector)
        }
    
    async def assess_liquidity_risk(self, symbol: str, risk_data: Dict) -> Dict:
        """Assess liquidity risk"""
        
        volume_data = risk_data.get('volume_history', pd.Series())
        price_data = risk_data.get('price_history', pd.Series())
        
        if volume_data.empty or len(volume_data) < 20:
            return {
                'liquidity_risk_score': 75,  # High risk due to lack of data
                'avg_daily_volume': 0,
                'liquidity_warning': 'Insufficient volume data'
            }
        
        # Calculate liquidity metrics
        avg_daily_volume = volume_data.tail(20).mean()
        avg_daily_dollar_volume = (volume_data * price_data).tail(20).mean()
        volume_volatility = volume_data.tail(20).std() / volume_data.tail(20).mean()
        
        # Liquidity score (0-100, lower is more liquid)
        liquidity_score = 0
        
        # Volume-based scoring
        if avg_daily_dollar_volume < 1_000_000:  # < $1M daily
            liquidity_score += 40
        elif avg_daily_dollar_volume < 5_000_000:  # < $5M daily
            liquidity_score += 20
        elif avg_daily_dollar_volume < 10_000_000:  # < $10M daily
            liquidity_score += 10
        
        # Volume consistency
        if volume_volatility > 1.0:  # Very inconsistent volume
            liquidity_score += 15
        elif volume_volatility > 0.5:
            liquidity_score += 8
        
        # Market cap consideration
        market_cap = risk_data.get('market_cap', 0)
        if market_cap > 0:
            if market_cap < 300_000_000:  # < $300M (small cap)
                liquidity_score += 15
            elif market_cap < 2_000_000_000:  # < $2B (mid cap)
                liquidity_score += 5
        
        return {
            'liquidity_risk_score': min(100, liquidity_score),
            'avg_daily_volume': avg_daily_volume,
            'avg_daily_dollar_volume': avg_daily_dollar_volume,
            'volume_volatility': volume_volatility,
            'estimated_transaction_cost': self.estimate_transaction_cost(
                avg_daily_dollar_volume, volume_volatility
            )
        }
    
    async def calculate_var_metrics(self, symbol: str, risk_data: Dict) -> Dict:
        """Calculate Value at Risk and related metrics"""
        
        returns = risk_data['price_history'].pct_change().dropna()
        
        if len(returns) < 30:
            return {
                'var_1d_95': 0,
                'var_1d_99': 0,
                'expected_shortfall_95': 0,
                'warning': 'Insufficient data for VaR calculation'
            }
        
        # Historical VaR (parametric method)
        mean_return = returns.mean()
        std_return = returns.std()
        
        # 1-day VaR at 95% and 99% confidence levels
        var_1d_95 = -1 * (mean_return - 1.645 * std_return)  # 95% VaR
        var_1d_99 = -1 * (mean_return - 2.326 * std_return)  # 99% VaR
        
        # Historical simulation VaR
        var_1d_95_hist = -1 * np.percentile(returns, 5)
        var_1d_99_hist = -1 * np.percentile(returns, 1)
        
        # Expected Shortfall (Conditional VaR)
        returns_beyond_var = returns[returns <= -var_1d_95_hist]
        expected_shortfall_95 = -1 * returns_beyond_var.mean() if len(returns_beyond_var) > 0 else var_1d_95_hist
        
        # 30-day VaR (scaled)
        var_30d_95 = var_1d_95 * np.sqrt(30)
        
        return {
            'var_1d_95': var_1d_95,
            'var_1d_99': var_1d_99,
            'var_1d_95_hist': var_1d_95_hist,
            'var_1d_99_hist': var_1d_99_hist,
            'var_30d_95': var_30d_95,
            'expected_shortfall_95': expected_shortfall_95,
            'return_volatility_30d': std_return * np.sqrt(252)  # Annualized
        }
```

## 🚨 Risk Warning System

```python
class RiskWarningSystem:
    """Generate and manage risk warnings"""
    
    def __init__(self):
        self.warning_thresholds = self.load_warning_thresholds()
        self.warning_templates = self.load_warning_templates()
        
    async def generate_risk_warnings(self, symbol: str, risk_assessment: Dict) -> List[Dict]:
        """Generate risk warnings based on assessment"""
        
        warnings = []
        
        # Check for high overall risk
        overall_risk = risk_assessment['overall_risk']['risk_score']
        if overall_risk > 80:
            warnings.append({
                'type': 'high_overall_risk',
                'severity': 'high',
                'title': f'High Risk Alert for {symbol}',
                'description': f'Overall risk score of {overall_risk}/100 indicates significant potential for losses.',
                'suggested_actions': [
                    'Consider reducing position size',
                    'Set tight stop-loss orders',
                    'Monitor daily for changes'
                ]
            })
        
        # Check VaR warnings
        var_1d_95 = risk_assessment['var_metrics'].get('var_1d_95', 0)
        if var_1d_95 > 0.05:  # > 5% daily VaR
            warnings.append({
                'type': 'high_var',
                'severity': 'medium',
                'title': f'High Daily Risk for {symbol}',
                'description': f'95% confidence 1-day VaR of {var_1d_95:.1%} indicates high daily risk.',
                'suggested_actions': [
                    'Consider position sizing adjustments',
                    'Use options for hedging'
                ]
            })
        
        # Check liquidity warnings
        liquidity_risk = risk_assessment['risk_components']['liquidity_risk']['liquidity_risk_score']
        if liquidity_risk > 60:
            warnings.append({
                'type': 'liquidity_concern',
                'severity': 'medium',
                'title': f'Liquidity Concern for {symbol}',
                'description': 'Low trading volume may make it difficult to exit positions quickly.',
                'suggested_actions': [
                    'Use limit orders instead of market orders',
                    'Consider smaller position sizes',
                    'Plan exit strategy in advance'
                ]
            })
        
        # Check upcoming events
        event_risk = risk_assessment['risk_components']['event_risk']
        if event_risk.get('earnings_days_away', 999) < 7:
            warnings.append({
                'type': 'earnings_risk',
                'severity': 'medium',
                'title': f'Earnings Risk for {symbol}',
                'description': f'Earnings announcement in {event_risk["earnings_days_away"]} days increases volatility risk.',
                'suggested_actions': [
                    'Consider taking profits before earnings',
                    'Use options strategies to manage risk',
                    'Reduce position size'
                ]
            })
        
        return warnings
    
    def monitor_portfolio_risk(self, portfolio: Dict, risk_assessments: Dict) -> List[Dict]:
        """Monitor portfolio-level risk warnings"""
        
        warnings = []
        
        # Check concentration risk
        position_sizes = [pos['weight'] for pos in portfolio['positions']]
        max_position = max(position_sizes) if position_sizes else 0
        
        if max_position > 0.20:  # > 20% in single position
            warnings.append({
                'type': 'concentration_risk',
                'severity': 'high',
                'title': 'High Concentration Risk',
                'description': f'Largest position represents {max_position:.1%} of portfolio',
                'suggested_actions': [
                    'Consider reducing largest positions',
                    'Diversify across more stocks',
                    'Add hedging positions'
                ]
            })
        
        # Check sector concentration
        sector_exposure = self.calculate_sector_exposure(portfolio)
        max_sector_exposure = max(sector_exposure.values()) if sector_exposure else 0
        
        if max_sector_exposure > 0.40:  # > 40% in single sector
            dominant_sector = max(sector_exposure, key=sector_exposure.get)
            warnings.append({
                'type': 'sector_concentration',
                'severity': 'medium',
                'title': 'Sector Concentration Risk',
                'description': f'{max_sector_exposure:.1%} exposure to {dominant_sector} sector',
                'suggested_actions': [
                    'Diversify across sectors',
                    'Consider defensive sectors',
                    'Add sector hedges'
                ]
            })
        
        return warnings
```

## 📊 Risk Visualization Components

```typescript
// RiskAssessmentDashboard.tsx

const RiskAssessmentDashboard = () => {
  return (
    <div className="risk-assessment">
      {/* Risk Overview */}
      <Card>
        <CardHeader>
          <Title>⚠️ Risk Assessment Overview</Title>
        </CardHeader>
        <CardBody>
          <RiskScoreGauge overallRisk={overallRiskScore} />
          <RiskComponentBreakdown components={riskComponents} />
        </CardBody>
      </Card>
      
      {/* VaR Analysis */}
      <Card>
        <CardHeader>
          <Title>📉 Value at Risk Analysis</Title>
        </CardHeader>
        <CardBody>
          <VaRChart 
            var1d={var1d}
            var30d={var30d}
            historicalReturns={historicalReturns}
          />
          <ExpectedShortfallMetrics es={expectedShortfall} />
        </CardBody>
      </Card>
      
      {/* Risk Warnings */}
      <Card>
        <CardHeader>
          <Title>🚨 Active Risk Warnings</Title>
        </CardHeader>
        <CardBody>
          <RiskWarningsList warnings={activeWarnings} />
          <RiskMitigationSuggestions suggestions={mitigationSuggestions} />
        </CardBody>
      </Card>
      
      {/* Portfolio Risk */}
      <Card>
        <CardHeader>
          <Title>📊 Portfolio Risk Analysis</Title>
        </CardHeader>
        <CardBody>
          <PortfolioRiskMatrix portfolio={portfolioData} />
          <ConcentrationChart concentrationData={concentrationData} />
        </CardBody>
      </Card>
      
      {/* Stress Testing */}
      <Card>
        <CardHeader>
          <Title>🧪 Stress Test Results</Title>
        </CardHeader>
        <CardBody>
          <StressTestResults scenarios={stressScenarios} />
        </CardBody>
      </Card>
    </div>
  );
};
```

## 📈 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Risk prediction accuracy | >75% | - |
| Early warning effectiveness | >80% | - |
| VaR model accuracy | 95% confidence | - |
| User risk awareness score | >8/10 | - |
| False alarm rate | <15% | - |

---

**Next**: Continue with opportunity scanner system.