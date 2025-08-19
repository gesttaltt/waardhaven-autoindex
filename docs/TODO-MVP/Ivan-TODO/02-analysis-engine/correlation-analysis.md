# 🔗 Correlation Analysis Engine

**Priority**: HIGH  
**Complexity**: Very High  
**Timeline**: 4-5 days  
**Value**: Discover hidden relationships between events and price movements

## 🎯 Objective

Build a sophisticated correlation engine that:
- Finds relationships between seemingly unrelated events
- Discovers lead/lag indicators
- Identifies cross-asset correlations
- Detects regime changes
- Uncovers supply chain dependencies

## 🧮 Correlation Types

### 1. Event-Price Correlations
```python
EVENT_CORRELATIONS = {
    'government_contracts': {
        'typical_lag': '0-3 days',
        'correlation_strength': 0.65,
        'confidence': 'high',
        'example': 'Defense contract → Stock price increase'
    },
    'insider_trading': {
        'typical_lag': '30-90 days',
        'correlation_strength': 0.72,
        'confidence': 'very high',
        'example': 'CEO buying → Positive earnings surprise'
    },
    'social_momentum': {
        'typical_lag': '1-5 days',
        'correlation_strength': 0.45,
        'confidence': 'medium',
        'example': 'Reddit mentions spike → Volume surge'
    },
    'patent_filings': {
        'typical_lag': '180-365 days',
        'correlation_strength': 0.38,
        'confidence': 'medium',
        'example': 'AI patents filed → Revenue growth'
    },
    'weather_events': {
        'typical_lag': '0-7 days',
        'correlation_strength': 0.82,
        'confidence': 'very high',
        'example': 'Hurricane → Insurance claims'
    }
}
```

### 2. Cross-Asset Correlations
```python
CROSS_ASSET_MATRIX = {
    'dollar_strength': {
        'gold': -0.75,  # Inverse correlation
        'oil': -0.60,
        'emerging_markets': -0.65,
        'tech_stocks': -0.30
    },
    'interest_rates': {
        'bank_stocks': 0.70,
        'real_estate': -0.65,
        'growth_stocks': -0.55,
        'utilities': -0.45
    },
    'oil_prices': {
        'airlines': -0.80,
        'energy_stocks': 0.85,
        'transportation': -0.60,
        'chemicals': -0.40
    },
    'vix_index': {
        'sp500': -0.78,
        'gold': 0.35,
        'bonds': 0.45,
        'crypto': -0.40
    }
}
```

## 💾 Database Schema

```sql
-- Correlation definitions
CREATE TABLE correlation_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Correlation pair
    source_type VARCHAR(100), -- event_type, asset, indicator
    source_identifier VARCHAR(255),
    target_type VARCHAR(100),
    target_identifier VARCHAR(255),
    
    -- Correlation metrics
    correlation_coefficient DECIMAL(5,4),
    p_value DECIMAL(10,8),
    confidence_interval_lower DECIMAL(5,4),
    confidence_interval_upper DECIMAL(5,4),
    
    -- Time relationship
    optimal_lag_days INTEGER,
    lag_range_start INTEGER,
    lag_range_end INTEGER,
    
    -- Statistical properties
    sample_size INTEGER,
    time_period_days INTEGER,
    last_calculated TIMESTAMP,
    
    -- Stability
    is_stable BOOLEAN,
    stability_score DECIMAL(3,2),
    regime_dependent BOOLEAN,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(source_type, source_identifier, target_type, target_identifier)
);

-- Correlation time series
CREATE TABLE correlation_timeseries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    correlation_id UUID REFERENCES correlation_definitions(id),
    
    -- Time window
    calculation_date DATE NOT NULL,
    window_days INTEGER,
    
    -- Rolling correlation
    correlation_value DECIMAL(5,4),
    
    -- Additional metrics
    beta DECIMAL(8,4),
    r_squared DECIMAL(5,4),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(correlation_id, calculation_date, window_days)
);

-- Discovered relationships
CREATE TABLE discovered_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Discovery details
    discovery_date TIMESTAMP NOT NULL,
    discovery_method VARCHAR(100),
    
    -- Entities
    entity_a VARCHAR(255),
    entity_a_type VARCHAR(50),
    entity_b VARCHAR(255),
    entity_b_type VARCHAR(50),
    
    -- Relationship
    relationship_type VARCHAR(100), -- leads, lags, causes, correlates
    strength DECIMAL(3,2),
    confidence DECIMAL(3,2),
    
    -- Evidence
    supporting_events JSONB,
    historical_accuracy DECIMAL(3,2),
    
    -- Actionability
    is_actionable BOOLEAN,
    suggested_strategy TEXT,
    expected_return DECIMAL(8,4),
    
    -- Validation
    is_validated BOOLEAN DEFAULT FALSE,
    validation_results JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Regime detection
CREATE TABLE market_regimes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Regime identification
    regime_name VARCHAR(100),
    regime_type VARCHAR(50), -- bull, bear, volatile, calm
    
    -- Time period
    start_date DATE NOT NULL,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    
    -- Characteristics
    volatility_level VARCHAR(20),
    trend_direction VARCHAR(20),
    correlation_stability VARCHAR(20),
    
    -- Key correlations in this regime
    dominant_correlations JSONB,
    broken_correlations JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🧬 Correlation Analysis Engine

```python
# app/services/correlation_analyzer.py

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.stattools import grangercausalitytests
import networkx as nx

class CorrelationAnalyzer:
    """Advanced correlation analysis engine"""
    
    def __init__(self):
        self.min_correlation = 0.3
        self.significance_level = 0.05
        self.min_samples = 30
        
    async def find_all_correlations(self, symbol: str = None):
        """Find all significant correlations"""
        
        correlations = {}
        
        # Event-price correlations
        event_corrs = await self.find_event_correlations(symbol)
        correlations['events'] = event_corrs
        
        # Cross-asset correlations
        asset_corrs = await self.find_cross_asset_correlations(symbol)
        correlations['assets'] = asset_corrs
        
        # Leading indicators
        leading = await self.find_leading_indicators(symbol)
        correlations['leading_indicators'] = leading
        
        # Supply chain correlations
        supply_chain = await self.find_supply_chain_correlations(symbol)
        correlations['supply_chain'] = supply_chain
        
        # Sentiment correlations
        sentiment = await self.find_sentiment_correlations(symbol)
        correlations['sentiment'] = sentiment
        
        return correlations
    
    async def find_event_correlations(self, symbol: str) -> List[Dict]:
        """Find correlations between events and price movements"""
        
        # Get price data
        price_data = await self.get_price_data(symbol, days=365)
        
        # Get events
        events = await self.get_events_for_symbol(symbol)
        
        correlations = []
        
        for event_type in events.keys():
            # Create event time series
            event_series = self.create_event_series(events[event_type], price_data.index)
            
            # Test different lags
            for lag in range(0, 91):  # Test up to 90 days lag
                # Shift event series
                lagged_events = event_series.shift(lag)
                
                # Calculate correlation
                if len(lagged_events.dropna()) >= self.min_samples:
                    corr, p_value = stats.pearsonr(
                        lagged_events.dropna(),
                        price_data.loc[lagged_events.dropna().index]['returns']
                    )
                    
                    if abs(corr) >= self.min_correlation and p_value < self.significance_level:
                        correlations.append({
                            'event_type': event_type,
                            'symbol': symbol,
                            'correlation': corr,
                            'p_value': p_value,
                            'optimal_lag': lag,
                            'confidence': self.calculate_confidence(corr, p_value, len(lagged_events.dropna())),
                            'relationship': self.interpret_correlation(corr, lag)
                        })
        
        # Sort by absolute correlation strength
        correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        return correlations
    
    async def find_cross_asset_correlations(self, symbol: str) -> Dict:
        """Find correlations with other assets"""
        
        # Get price data for symbol
        target_data = await self.get_price_data(symbol, days=365)
        
        # Get related assets
        related_assets = await self.get_related_assets(symbol)
        
        correlations = {}
        
        for asset in related_assets:
            # Get asset data
            asset_data = await self.get_price_data(asset, days=365)
            
            # Align time series
            aligned_target, aligned_asset = self.align_time_series(target_data, asset_data)
            
            if len(aligned_target) >= self.min_samples:
                # Calculate various correlation metrics
                correlations[asset] = {
                    'pearson': np.corrcoef(aligned_target, aligned_asset)[0, 1],
                    'spearman': stats.spearmanr(aligned_target, aligned_asset)[0],
                    'rolling_30d': self.calculate_rolling_correlation(aligned_target, aligned_asset, 30),
                    'rolling_90d': self.calculate_rolling_correlation(aligned_target, aligned_asset, 90),
                    'beta': self.calculate_beta(aligned_target, aligned_asset),
                    'is_stable': self.check_correlation_stability(aligned_target, aligned_asset)
                }
        
        return correlations
    
    async def find_leading_indicators(self, symbol: str) -> List[Dict]:
        """Find indicators that lead price movements"""
        
        indicators = []
        
        # Get price data
        price_data = await self.get_price_data(symbol, days=365)
        
        # Test various potential leading indicators
        test_indicators = [
            'insider_buying',
            'institutional_accumulation',
            'social_momentum',
            'options_flow',
            'dark_pool_activity',
            'patent_filings',
            'job_postings',
            'web_traffic'
        ]
        
        for indicator_name in test_indicators:
            # Get indicator data
            indicator_data = await self.get_indicator_data(indicator_name, symbol)
            
            if indicator_data is not None and len(indicator_data) >= self.min_samples:
                # Granger causality test
                granger_result = self.test_granger_causality(indicator_data, price_data)
                
                if granger_result['is_significant']:
                    # Calculate predictive power
                    predictive_power = self.calculate_predictive_power(indicator_data, price_data)
                    
                    indicators.append({
                        'indicator': indicator_name,
                        'symbol': symbol,
                        'granger_p_value': granger_result['p_value'],
                        'optimal_lag': granger_result['optimal_lag'],
                        'predictive_power': predictive_power,
                        'confidence': granger_result['confidence'],
                        'actionability': self.assess_actionability(indicator_name)
                    })
        
        # Sort by predictive power
        indicators.sort(key=lambda x: x['predictive_power'], reverse=True)
        
        return indicators
    
    def test_granger_causality(self, cause_series: pd.Series, effect_series: pd.Series) -> Dict:
        """Test if one series Granger-causes another"""
        
        # Prepare data
        data = pd.DataFrame({
            'cause': cause_series,
            'effect': effect_series
        }).dropna()
        
        # Test different lags
        best_result = {'is_significant': False, 'p_value': 1.0}
        
        for lag in range(1, 11):  # Test lags 1-10
            try:
                result = grangercausalitytests(data[['effect', 'cause']], maxlag=lag, verbose=False)
                
                # Get p-value for the lag
                p_value = result[lag][0]['ssr_ftest'][1]
                
                if p_value < self.significance_level and p_value < best_result['p_value']:
                    best_result = {
                        'is_significant': True,
                        'p_value': p_value,
                        'optimal_lag': lag,
                        'confidence': 1 - p_value
                    }
            except:
                continue
        
        return best_result
```

## 🌐 Network Analysis

```python
class CorrelationNetworkAnalyzer:
    """Analyze correlation networks to find hidden relationships"""
    
    def build_correlation_network(self, correlations: Dict) -> nx.Graph:
        """Build network graph of correlations"""
        
        G = nx.Graph()
        
        # Add nodes
        for entity in correlations.keys():
            G.add_node(entity, type='asset')
        
        # Add edges for significant correlations
        for entity_a, corr_dict in correlations.items():
            for entity_b, corr_value in corr_dict.items():
                if abs(corr_value) >= self.min_correlation:
                    G.add_edge(
                        entity_a,
                        entity_b,
                        weight=abs(corr_value),
                        correlation=corr_value
                    )
        
        return G
    
    def find_correlation_clusters(self, G: nx.Graph) -> List[Set]:
        """Find clusters of highly correlated assets"""
        
        # Use community detection
        communities = nx.community.louvain_communities(G, weight='weight')
        
        clusters = []
        for community in communities:
            if len(community) >= 3:  # Minimum cluster size
                clusters.append({
                    'members': list(community),
                    'size': len(community),
                    'density': nx.density(G.subgraph(community)),
                    'central_node': self.find_central_node(G, community)
                })
        
        return clusters
    
    def find_bridge_assets(self, G: nx.Graph) -> List[str]:
        """Find assets that bridge different correlation clusters"""
        
        # Calculate betweenness centrality
        centrality = nx.betweenness_centrality(G, weight='weight')
        
        # Sort by centrality
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        
        # Return top bridge assets
        return [node for node, score in sorted_nodes[:10] if score > 0.1]
```

## 🔄 Dynamic Correlation Tracking

```python
class DynamicCorrelationTracker:
    """Track how correlations change over time"""
    
    def calculate_rolling_correlation_matrix(self, assets: List[str], window: int = 30):
        """Calculate rolling correlation matrix"""
        
        # Get price data for all assets
        price_data = self.get_multi_asset_prices(assets)
        
        # Calculate returns
        returns = price_data.pct_change()
        
        # Calculate rolling correlations
        rolling_corr = returns.rolling(window).corr()
        
        return rolling_corr
    
    def detect_correlation_breaks(self, asset_a: str, asset_b: str) -> List[Dict]:
        """Detect when correlations break down"""
        
        # Get historical correlation
        hist_corr = self.get_correlation_history(asset_a, asset_b)
        
        breaks = []
        
        # Use statistical tests to detect breaks
        for i in range(60, len(hist_corr)):
            # Compare recent vs historical correlation
            recent = hist_corr[i-30:i].mean()
            historical = hist_corr[:i-30].mean()
            historical_std = hist_corr[:i-30].std()
            
            # Check if significant deviation
            if abs(recent - historical) > 2 * historical_std:
                breaks.append({
                    'date': hist_corr.index[i],
                    'historical_corr': historical,
                    'recent_corr': recent,
                    'deviation_sigmas': abs(recent - historical) / historical_std,
                    'likely_cause': self.identify_break_cause(asset_a, asset_b, hist_corr.index[i])
                })
        
        return breaks
    
    def identify_regime_changes(self) -> List[Dict]:
        """Identify market regime changes"""
        
        # Get market indicators
        indicators = {
            'volatility': self.get_vix_history(),
            'correlation': self.get_average_correlation(),
            'dispersion': self.get_cross_sectional_dispersion(),
            'momentum': self.get_market_momentum()
        }
        
        # Use Hidden Markov Model to identify regimes
        regimes = self.fit_regime_model(indicators)
        
        return regimes
```

## 🧑‍🔬 Advanced Statistical Methods

```python
class AdvancedCorrelationMethods:
    """Advanced statistical methods for correlation analysis"""
    
    def calculate_partial_correlation(self, x: pd.Series, y: pd.Series, z: pd.Series) -> float:
        """Calculate partial correlation controlling for z"""
        
        # Standardize
        x_std = (x - x.mean()) / x.std()
        y_std = (y - y.mean()) / y.std()
        z_std = (z - z.mean()) / z.std()
        
        # Calculate residuals
        x_resid = x_std - z_std * np.cov(x_std, z_std)[0, 1] / np.var(z_std)
        y_resid = y_std - z_std * np.cov(y_std, z_std)[0, 1] / np.var(z_std)
        
        # Partial correlation
        return np.corrcoef(x_resid, y_resid)[0, 1]
    
    def calculate_distance_correlation(self, x: pd.Series, y: pd.Series) -> float:
        """Calculate distance correlation (captures non-linear relationships)"""
        
        from dcor import distance_correlation
        return distance_correlation(x, y)
    
    def calculate_mutual_information(self, x: pd.Series, y: pd.Series) -> float:
        """Calculate mutual information between variables"""
        
        from sklearn.feature_selection import mutual_info_regression
        return mutual_info_regression(x.values.reshape(-1, 1), y.values)[0]
    
    def detect_nonlinear_relationships(self, x: pd.Series, y: pd.Series) -> Dict:
        """Detect non-linear relationships"""
        
        # Linear correlation
        linear_corr = np.corrcoef(x, y)[0, 1]
        
        # Distance correlation
        dist_corr = self.calculate_distance_correlation(x, y)
        
        # Mutual information
        mi = self.calculate_mutual_information(x, y)
        
        # Check for non-linearity
        is_nonlinear = (dist_corr - abs(linear_corr)) > 0.1
        
        return {
            'linear_correlation': linear_corr,
            'distance_correlation': dist_corr,
            'mutual_information': mi,
            'is_nonlinear': is_nonlinear,
            'relationship_type': self.classify_relationship(linear_corr, dist_corr, mi)
        }
```

## 🎨 Visualization

```typescript
// CorrelationDashboard.tsx

const CorrelationDashboard = () => {
  return (
    <div className="correlation-analysis">
      {/* Correlation Matrix Heatmap */}
      <Card>
        <CardHeader>
          <Title>🔥 Correlation Heatmap</Title>
        </CardHeader>
        <CardBody>
          <CorrelationHeatmap 
            data={correlationMatrix}
            showValues={true}
            colorScale="RdBu"
          />
        </CardBody>
      </Card>
      
      {/* Network Graph */}
      <Card>
        <CardHeader>
          <Title>🌐 Correlation Network</Title>
        </CardHeader>
        <CardBody>
          <ForceDirectedGraph 
            nodes={correlationNodes}
            edges={correlationEdges}
            showClusters={true}
          />
        </CardBody>
      </Card>
      
      {/* Leading Indicators */}
      <Card>
        <CardHeader>
          <Title>📈 Leading Indicators</Title>
        </CardHeader>
        <CardBody>
          <LeadingIndicatorTable 
            indicators={leadingIndicators}
            sortBy="predictive_power"
          />
        </CardBody>
      </Card>
      
      {/* Correlation Stability */}
      <Card>
        <CardHeader>
          <Title>📊 Correlation Stability Over Time</Title>
        </CardHeader>
        <CardBody>
          <RollingCorrelationChart 
            pairs={correlationPairs}
            window={30}
          />
        </CardBody>
      </Card>
    </div>
  );
};
```

## 📊 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Correlations tracked | 1000+ | 0 |
| Leading indicators found | 50+ | 0 |
| Prediction accuracy | >70% | - |
| False discovery rate | <10% | - |
| Regime detection accuracy | >85% | - |

---

**Next**: Continue with predictive scoring models.