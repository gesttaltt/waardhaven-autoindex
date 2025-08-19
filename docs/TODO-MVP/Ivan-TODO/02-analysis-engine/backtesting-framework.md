# 🔙 Backtesting Framework

**Priority**: MEDIUM  
**Complexity**: High  
**Timeline**: 4-5 days  
**Value**: Validate strategies and predictions against historical data

## 🎯 Objective

Build a comprehensive backtesting system that:
- Tests strategies against historical data
- Validates prediction accuracy
- Simulates realistic trading conditions
- Accounts for transaction costs and slippage
- Provides detailed performance analytics

## 🏎️ Backtesting Architecture

### System Components
```python
BACKTEST_COMPONENTS = {
    'data_engine': {
        'purpose': 'Historical data management',
        'features': ['Point-in-time data', 'Survivorship bias free', 'Corporate actions']
    },
    'strategy_engine': {
        'purpose': 'Strategy execution',
        'features': ['Signal generation', 'Position sizing', 'Risk management']
    },
    'execution_engine': {
        'purpose': 'Trade simulation',
        'features': ['Slippage modeling', 'Transaction costs', 'Market impact']
    },
    'analytics_engine': {
        'purpose': 'Performance analysis',
        'features': ['Returns analysis', 'Risk metrics', 'Attribution']
    },
    'optimization_engine': {
        'purpose': 'Parameter optimization',
        'features': ['Grid search', 'Genetic algorithms', 'Walk-forward analysis']
    }
}
```

## 💾 Database Schema

```sql
-- Backtest definitions
CREATE TABLE backtest_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Backtest identification
    backtest_name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    
    -- Strategy details
    strategy_type VARCHAR(100),
    strategy_params JSONB,
    
    -- Time period
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    
    -- Universe
    universe_filter JSONB,
    symbol_list TEXT[],
    
    -- Execution parameters
    initial_capital DECIMAL(20,2),
    position_sizing VARCHAR(50),
    max_positions INTEGER,
    
    -- Costs
    commission_per_trade DECIMAL(10,2),
    slippage_model VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Backtest results
CREATE TABLE backtest_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    backtest_id UUID REFERENCES backtest_definitions(id),
    run_date TIMESTAMP NOT NULL,
    
    -- Overall performance
    total_return DECIMAL(12,4),
    annualized_return DECIMAL(12,4),
    sharpe_ratio DECIMAL(8,4),
    sortino_ratio DECIMAL(8,4),
    calmar_ratio DECIMAL(8,4),
    
    -- Risk metrics
    max_drawdown DECIMAL(8,4),
    volatility DECIMAL(8,4),
    beta DECIMAL(8,4),
    alpha DECIMAL(8,4),
    
    -- Trading statistics
    total_trades INTEGER,
    winning_trades INTEGER,
    losing_trades INTEGER,
    win_rate DECIMAL(5,4),
    
    -- Return distribution
    avg_win DECIMAL(12,4),
    avg_loss DECIMAL(12,4),
    profit_factor DECIMAL(8,4),
    
    -- Costs
    total_commission DECIMAL(20,2),
    total_slippage DECIMAL(20,2),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Individual trades
CREATE TABLE backtest_trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    backtest_id UUID REFERENCES backtest_definitions(id),
    
    -- Trade details
    symbol VARCHAR(20) NOT NULL,
    trade_type VARCHAR(10), -- buy/sell
    
    -- Timing
    entry_date TIMESTAMP NOT NULL,
    exit_date TIMESTAMP,
    holding_period_days INTEGER,
    
    -- Prices
    entry_price DECIMAL(10,2),
    exit_price DECIMAL(10,2),
    
    -- Size
    shares INTEGER,
    position_value DECIMAL(20,2),
    
    -- P&L
    gross_pnl DECIMAL(20,2),
    commission DECIMAL(10,2),
    slippage DECIMAL(10,2),
    net_pnl DECIMAL(20,2),
    return_pct DECIMAL(12,4),
    
    -- Signal details
    entry_signal VARCHAR(100),
    entry_score DECIMAL(5,4),
    exit_signal VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Performance attribution
CREATE TABLE performance_attribution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    backtest_id UUID REFERENCES backtest_definitions(id),
    
    -- Attribution factors
    factor_name VARCHAR(100),
    contribution DECIMAL(12,4),
    
    -- Time period
    period_start DATE,
    period_end DATE,
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🧪 Backtesting Engine

```python
# app/backtesting/engine.py

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio

class BacktestEngine:
    """Main backtesting engine"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.data_provider = HistoricalDataProvider()
        self.strategy = self.load_strategy(config['strategy'])
        self.portfolio = Portfolio(config['initial_capital'])
        self.execution = ExecutionSimulator(config['execution'])
        self.analytics = PerformanceAnalytics()
        
    async def run_backtest(self) -> Dict:
        """Run complete backtest"""
        
        print(f"Starting backtest: {self.config['name']}")
        
        # Load historical data
        data = await self.load_data()
        
        # Initialize results tracking
        results = {
            'trades': [],
            'daily_returns': [],
            'positions': [],
            'signals': []
        }
        
        # Iterate through time periods
        for date in self.get_trading_dates():
            # Get point-in-time data
            current_data = self.get_pit_data(data, date)
            
            # Generate signals
            signals = await self.strategy.generate_signals(current_data, date)
            results['signals'].extend(signals)
            
            # Execute trades
            trades = await self.execute_signals(signals, current_data, date)
            results['trades'].extend(trades)
            
            # Update portfolio
            self.portfolio.update(date, current_data)
            
            # Record daily performance
            daily_perf = self.portfolio.get_daily_performance(date)
            results['daily_returns'].append(daily_perf)
            
            # Risk management
            await self.apply_risk_management(date)
            
        # Calculate final metrics
        final_results = self.calculate_results(results)
        
        return final_results
    
    async def execute_signals(self, signals: List[Dict], data: pd.DataFrame, date: datetime) -> List[Dict]:
        """Execute trading signals"""
        
        trades = []
        
        for signal in signals:
            # Check if we can execute
            if not self.can_execute(signal):
                continue
                
            # Calculate position size
            position_size = self.calculate_position_size(signal)
            
            # Simulate execution
            execution = await self.execution.simulate(
                symbol=signal['symbol'],
                side=signal['side'],
                size=position_size,
                price=data[signal['symbol']]['close'],
                date=date
            )
            
            # Record trade
            trade = {
                'date': date,
                'symbol': signal['symbol'],
                'side': signal['side'],
                'shares': position_size,
                'entry_price': execution['fill_price'],
                'commission': execution['commission'],
                'slippage': execution['slippage'],
                'signal': signal['signal_name'],
                'score': signal['score']
            }
            
            trades.append(trade)
            
            # Update portfolio
            self.portfolio.add_position(trade)
            
        return trades
    
    def calculate_position_size(self, signal: Dict) -> int:
        """Calculate position size based on strategy"""
        
        if self.config['position_sizing'] == 'equal_weight':
            # Equal weight across all positions
            capital_per_position = self.portfolio.cash / self.config['max_positions']
            shares = int(capital_per_position / signal['price'])
            
        elif self.config['position_sizing'] == 'kelly':
            # Kelly criterion
            kelly_fraction = self.calculate_kelly_fraction(signal)
            position_value = self.portfolio.total_value * kelly_fraction
            shares = int(position_value / signal['price'])
            
        elif self.config['position_sizing'] == 'risk_parity':
            # Risk parity sizing
            target_risk = self.config['target_risk_per_position']
            position_value = self.calculate_risk_parity_size(signal, target_risk)
            shares = int(position_value / signal['price'])
            
        else:
            # Fixed size
            shares = self.config['fixed_position_size']
            
        # Apply constraints
        shares = self.apply_position_constraints(shares, signal)
        
        return shares
```

## 🎯 Strategy Implementation

```python
class Strategy:
    """Base strategy class for backtesting"""
    
    async def generate_signals(self, data: pd.DataFrame, date: datetime) -> List[Dict]:
        """Generate trading signals"""
        raise NotImplementedError
        
class MLPredictiveStrategy(Strategy):
    """Strategy based on ML predictions"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.scorer = PredictiveScorer()
        self.min_score = config.get('min_score', 0.7)
        self.min_confidence = config.get('min_confidence', 0.6)
        
    async def generate_signals(self, data: pd.DataFrame, date: datetime) -> List[Dict]:
        """Generate signals from ML predictions"""
        
        signals = []
        
        # Score all symbols
        for symbol in data.index:
            # Get prediction
            prediction = await self.scorer.score_stock(symbol, date)
            
            if prediction['score'] >= self.min_score and prediction['confidence'] >= self.min_confidence:
                signals.append({
                    'date': date,
                    'symbol': symbol,
                    'side': 'buy',
                    'signal_name': 'ml_prediction',
                    'score': prediction['score'],
                    'confidence': prediction['confidence'],
                    'price': data.loc[symbol, 'close'],
                    'target': prediction['price_target_30d']
                })
                
            # Check exit conditions for existing positions
            if self.has_position(symbol):
                if prediction['score'] < 0.3 or self.hit_stop_loss(symbol):
                    signals.append({
                        'date': date,
                        'symbol': symbol,
                        'side': 'sell',
                        'signal_name': 'ml_exit',
                        'score': prediction['score'],
                        'price': data.loc[symbol, 'close']
                    })
                    
        return signals

class InsiderMomentumStrategy(Strategy):
    """Strategy based on insider trading and momentum"""
    
    async def generate_signals(self, data: pd.DataFrame, date: datetime) -> List[Dict]:
        """Generate signals from insider activity"""
        
        signals = []
        
        for symbol in data.index:
            # Check insider activity
            insider_score = await self.get_insider_score(symbol, date)
            
            # Check momentum
            momentum = self.calculate_momentum(data.loc[symbol], periods=30)
            
            # Combined signal
            if insider_score > 0.7 and momentum > 0.1:
                signals.append({
                    'date': date,
                    'symbol': symbol,
                    'side': 'buy',
                    'signal_name': 'insider_momentum',
                    'score': (insider_score + momentum) / 2,
                    'price': data.loc[symbol, 'close']
                })
                
        return signals
```

## 📊 Performance Analytics

```python
class PerformanceAnalytics:
    """Calculate performance metrics"""
    
    def calculate_metrics(self, returns: pd.Series, trades: List[Dict]) -> Dict:
        """Calculate comprehensive performance metrics"""
        
        metrics = {}
        
        # Return metrics
        metrics['total_return'] = self.calculate_total_return(returns)
        metrics['annualized_return'] = self.calculate_annualized_return(returns)
        metrics['cagr'] = self.calculate_cagr(returns)
        
        # Risk metrics
        metrics['volatility'] = self.calculate_volatility(returns)
        metrics['sharpe_ratio'] = self.calculate_sharpe(returns)
        metrics['sortino_ratio'] = self.calculate_sortino(returns)
        metrics['calmar_ratio'] = self.calculate_calmar(returns)
        
        # Drawdown metrics
        metrics['max_drawdown'] = self.calculate_max_drawdown(returns)
        metrics['avg_drawdown'] = self.calculate_avg_drawdown(returns)
        metrics['recovery_time'] = self.calculate_recovery_time(returns)
        
        # Trade statistics
        metrics['total_trades'] = len(trades)
        metrics['win_rate'] = self.calculate_win_rate(trades)
        metrics['profit_factor'] = self.calculate_profit_factor(trades)
        metrics['avg_win'] = self.calculate_avg_win(trades)
        metrics['avg_loss'] = self.calculate_avg_loss(trades)
        
        # Risk-adjusted metrics
        metrics['information_ratio'] = self.calculate_information_ratio(returns)
        metrics['treynor_ratio'] = self.calculate_treynor_ratio(returns)
        
        return metrics
    
    def calculate_sharpe(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        
        excess_returns = returns - risk_free_rate / 252
        if excess_returns.std() == 0:
            return 0
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    
    def calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def calculate_profit_factor(self, trades: List[Dict]) -> float:
        """Calculate profit factor"""
        
        gross_profit = sum(t['net_pnl'] for t in trades if t['net_pnl'] > 0)
        gross_loss = abs(sum(t['net_pnl'] for t in trades if t['net_pnl'] < 0))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0
        return gross_profit / gross_loss
```

## 🔄 Walk-Forward Optimization

```python
class WalkForwardOptimizer:
    """Walk-forward analysis for robust parameter optimization"""
    
    def optimize(self, strategy_class, param_grid: Dict, data: pd.DataFrame):
        """Run walk-forward optimization"""
        
        # Split data into windows
        windows = self.create_windows(data, 
                                     window_size=252,  # 1 year
                                     step_size=63)     # 3 months
        
        results = []
        
        for i, (train_start, train_end, test_start, test_end) in enumerate(windows):
            print(f"Window {i+1}/{len(windows)}")
            
            # Training data
            train_data = data[train_start:train_end]
            
            # Optimize on training data
            best_params = self.optimize_window(strategy_class, param_grid, train_data)
            
            # Test on out-of-sample data
            test_data = data[test_start:test_end]
            test_results = self.test_strategy(strategy_class, best_params, test_data)
            
            results.append({
                'window': i,
                'train_period': (train_start, train_end),
                'test_period': (test_start, test_end),
                'best_params': best_params,
                'in_sample_sharpe': best_params['sharpe'],
                'out_sample_sharpe': test_results['sharpe'],
                'out_sample_return': test_results['total_return']
            })
            
        return self.analyze_results(results)
    
    def optimize_window(self, strategy_class, param_grid: Dict, data: pd.DataFrame) -> Dict:
        """Optimize parameters for a single window"""
        
        best_sharpe = -float('inf')
        best_params = None
        
        # Grid search
        for params in self.generate_param_combinations(param_grid):
            # Create strategy with params
            strategy = strategy_class(params)
            
            # Run backtest
            backtest = BacktestEngine({
                'strategy': strategy,
                'data': data
            })
            
            results = backtest.run_backtest()
            
            # Track best
            if results['sharpe_ratio'] > best_sharpe:
                best_sharpe = results['sharpe_ratio']
                best_params = params
                best_params['sharpe'] = best_sharpe
                
        return best_params
```

## 🎨 Visualization

```typescript
// BacktestingDashboard.tsx

const BacktestingDashboard = () => {
  return (
    <div className="backtesting">
      {/* Performance Chart */}
      <Card>
        <CardHeader>
          <Title>📈 Strategy Performance</Title>
        </CardHeader>
        <CardBody>
          <EquityCurve 
            data={equityData}
            benchmark={benchmarkData}
            showDrawdown={true}
          />
        </CardBody>
      </Card>
      
      {/* Metrics Summary */}
      <Card>
        <CardHeader>
          <Title>📊 Performance Metrics</Title>
        </CardHeader>
        <CardBody>
          <MetricsGrid metrics={performanceMetrics} />
          <RiskMetrics metrics={riskMetrics} />
        </CardBody>
      </Card>
      
      {/* Trade Analysis */}
      <Card>
        <CardHeader>
          <Title>💹 Trade Analysis</Title>
        </CardHeader>
        <CardBody>
          <TradeDistribution trades={allTrades} />
          <WinLossAnalysis trades={allTrades} />
        </CardBody>
      </Card>
      
      {/* Optimization Results */}
      <Card>
        <CardHeader>
          <Title>🎯 Parameter Optimization</Title>
        </CardHeader>
        <CardBody>
          <OptimizationHeatmap results={optimizationResults} />
          <WalkForwardResults windows={walkForwardWindows} />
        </CardBody>
      </Card>
    </div>
  );
};
```

## 📊 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Backtest speed | <1min for 5 years | - |
| Strategy types supported | 10+ | 0 |
| Sharpe ratio (average) | >1.5 | - |
| Win rate | >55% | - |
| Max drawdown | <20% | - |

---

**Next**: Continue with time machine architecture.