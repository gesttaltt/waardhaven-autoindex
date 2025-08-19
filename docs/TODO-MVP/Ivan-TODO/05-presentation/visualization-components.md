# 📈 Visualization Components - Charts & Data Display

**Priority**: HIGH  
**Complexity**: Medium-High  
**Timeline**: 3-4 days  
**Value**: Transform complex data into intuitive visual insights

## 🎯 Objective

Build a comprehensive library of visualization components that:
- Make complex financial data immediately understandable
- Support interactive exploration and analysis
- Adapt to different screen sizes and contexts
- Provide consistent visual language across the platform
- Enable real-time data updates without performance issues

## 📊 Chart Component Library

### Core Chart Types
```typescript
// Chart type definitions
interface ChartProps {
  data: any[];
  width?: number;
  height?: number;
  responsive?: boolean;
  interactive?: boolean;
  theme?: 'light' | 'dark';
  onDataPointClick?: (data: any) => void;
}

// Supported chart types
const CHART_TYPES = {
  // Price and performance charts
  'candlestick': 'OHLC price data with volume',
  'line': 'Price trends and performance over time',
  'area': 'Filled line charts for cumulative data',
  'mountain': 'Portfolio value with gradient fill',
  
  // Comparison charts
  'multi_line': 'Compare multiple stocks/portfolios',
  'normalized_line': 'Compare performance from same starting point',
  'scatter': 'Risk vs return analysis',
  'bubble': '3D data with size dimension',
  
  // Composition charts
  'treemap': 'Portfolio allocation by size',
  'donut': 'Portfolio breakdown by sector/holding',
  'stacked_bar': 'Performance attribution over time',
  'waterfall': 'Performance breakdown by factors',
  
  // Distribution charts
  'histogram': 'Return distributions',
  'box_plot': 'Statistical summary of returns',
  'violin': 'Return distribution shape',
  'heatmap': 'Correlation matrix visualization'
};
```

### Advanced Candlestick Chart
```typescript
// AdvancedCandlestickChart.tsx
import { ResponsiveContainer, ComposedChart, CandlestickChart, XAxis, YAxis, Tooltip, Volume } from 'recharts';

interface CandlestickData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  indicators?: {
    sma20?: number;
    sma50?: number;
    bollinger_upper?: number;
    bollinger_lower?: number;
    rsi?: number;
  };
}

const AdvancedCandlestickChart: React.FC<{
  data: CandlestickData[];
  height?: number;
  showVolume?: boolean;
  showIndicators?: boolean;
  timeRange?: string;
}> = ({ data, height = 400, showVolume = true, showIndicators = true, timeRange = '6M' }) => {
  const [zoomLevel, setZoomLevel] = useState(1);
  const [selectedRange, setSelectedRange] = useState<[number, number] | null>(null);
  const [crosshair, setCrosshair] = useState<{ x: number; y: number } | null>(null);
  
  return (
    <div className="candlestick-chart-container">
      {/* Chart Controls */}
      <div className="chart-controls">
        <TimeRangeSelector 
          value={timeRange}
          options={['1D', '1W', '1M', '3M', '6M', '1Y', '2Y', '5Y']}
          onChange={handleTimeRangeChange}
        />
        <IndicatorSelector
          selected={['SMA20', 'SMA50']}
          available={['SMA20', 'SMA50', 'EMA', 'Bollinger', 'RSI', 'MACD']}
          onChange={handleIndicatorToggle}
        />
        <Button variant="outline" size="sm" onClick={resetZoom}>
          Reset Zoom
        </Button>
      </div>
      
      {/* Main Chart */}
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <XAxis 
            dataKey="date"
            type="category"
            tickFormatter={formatDateTick}
            domain={selectedRange || ['dataMin', 'dataMax']}
          />
          <YAxis 
            yAxisId="price"
            orientation="right"
            tickFormatter={formatPriceTick}
            domain={['dataMin - 5%', 'dataMax + 5%']}
          />
          {showVolume && (
            <YAxis 
              yAxisId="volume"
              orientation="left"
              tickFormatter={formatVolumeTick}
            />
          )}
          
          {/* Candlesticks */}
          <CandlestickSeries
            yAxisId="price"
            data={data}
            fill={(entry) => entry.close > entry.open ? '#10b981' : '#ef4444'}
            stroke={(entry) => entry.close > entry.open ? '#059669' : '#dc2626'}
          />
          
          {/* Moving Averages */}
          {showIndicators && data[0]?.indicators?.sma20 && (
            <Line
              yAxisId="price"
              type="monotone"
              dataKey="indicators.sma20"
              stroke="#f59e0b"
              strokeWidth={1.5}
              dot={false}
              name="SMA 20"
            />
          )}
          
          {showIndicators && data[0]?.indicators?.sma50 && (
            <Line
              yAxisId="price"
              type="monotone"
              dataKey="indicators.sma50"
              stroke="#3b82f6"
              strokeWidth={1.5}
              dot={false}
              name="SMA 50"
            />
          )}
          
          {/* Volume Bars */}
          {showVolume && (
            <Bar
              yAxisId="volume"
              dataKey="volume"
              fill="#64748b"
              opacity={0.3}
              name="Volume"
            />
          )}
          
          {/* Bollinger Bands */}
          {showIndicators && data[0]?.indicators?.bollinger_upper && (
            <Area
              yAxisId="price"
              type="monotone"
              dataKey="indicators.bollinger_upper"
              stackId="bollinger"
              stroke="#e5e7eb"
              fill="transparent"
            />
          )}
          
          <Tooltip content={<CustomCandlestickTooltip />} />
          <Crosshair stroke="#6b7280" strokeDasharray="3 3" />
        </ComposedChart>
      </ResponsiveContainer>
      
      {/* Volume Chart (if shown separately) */}
      {showVolume && (
        <ResponsiveContainer width="100%" height={100}>
          <BarChart data={data}>
            <XAxis dataKey="date" hide />
            <YAxis tickFormatter={formatVolumeTick} />
            <Bar 
              dataKey="volume" 
              fill={(entry) => entry.close > entry.open ? '#10b981' : '#ef4444'}
            />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
};

// Custom tooltip for candlestick chart
const CustomCandlestickTooltip: React.FC<any> = ({ active, payload, label }) => {
  if (!active || !payload || !payload.length) return null;
  
  const data = payload[0].payload;
  const change = data.close - data.open;
  const changePercent = (change / data.open) * 100;
  
  return (
    <div className="candlestick-tooltip">
      <h4 className="tooltip-date">{formatDate(label)}</h4>
      <div className="price-data">
        <div className="price-row">
          <span>Open:</span>
          <span>${data.open.toFixed(2)}</span>
        </div>
        <div className="price-row">
          <span>High:</span>
          <span>${data.high.toFixed(2)}</span>
        </div>
        <div className="price-row">
          <span>Low:</span>
          <span>${data.low.toFixed(2)}</span>
        </div>
        <div className="price-row">
          <span>Close:</span>
          <span>${data.close.toFixed(2)}</span>
        </div>
        <div className={`price-row ${change >= 0 ? 'positive' : 'negative'}`}>
          <span>Change:</span>
          <span>
            {change >= 0 ? '+' : ''}${change.toFixed(2)} ({changePercent.toFixed(2)}%)
          </span>
        </div>
        <div className="price-row">
          <span>Volume:</span>
          <span>{formatVolume(data.volume)}</span>
        </div>
      </div>
    </div>
  );
};
```

### Portfolio Performance Chart
```typescript
// PortfolioPerformanceChart.tsx
const PortfolioPerformanceChart: React.FC<{
  portfolioData: PerformanceData[];
  benchmarkData?: PerformanceData[];
  height?: number;
  showBenchmark?: boolean;
}> = ({ portfolioData, benchmarkData, height = 300, showBenchmark = true }) => {
  const [timeRange, setTimeRange] = useState('1Y');
  const [chartType, setChartType] = useState<'cumulative' | 'periodic'>('cumulative');
  
  return (
    <div className="portfolio-performance-chart">
      {/* Chart Header */}
      <div className="chart-header">
        <div className="chart-title">
          <h3>Portfolio Performance</h3>
          <div className="performance-summary">
            <span className="total-return">
              Total Return: {formatPercent(portfolioData[portfolioData.length - 1]?.totalReturn || 0)}
            </span>
            {showBenchmark && benchmarkData && (
              <span className="vs-benchmark">
                vs Benchmark: {formatPercent(
                  (portfolioData[portfolioData.length - 1]?.totalReturn || 0) - 
                  (benchmarkData[benchmarkData.length - 1]?.totalReturn || 0)
                )}
              </span>
            )}
          </div>
        </div>
        
        <div className="chart-controls">
          <ToggleGroup
            value={chartType}
            options={[
              { value: 'cumulative', label: 'Cumulative' },
              { value: 'periodic', label: 'Periodic' }
            ]}
            onChange={setChartType}
          />
          <TimeRangeSelector
            value={timeRange}
            options={['1M', '3M', '6M', '1Y', '2Y', '5Y', 'All']}
            onChange={setTimeRange}
          />
        </div>
      </div>
      
      {/* Chart Area */}
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart data={portfolioData}>
          <XAxis 
            dataKey="date"
            tickFormatter={formatDateTick}
          />
          <YAxis 
            tickFormatter={chartType === 'cumulative' ? formatPercent : formatCurrency}
          />
          
          {/* Portfolio Performance Line */}
          <Area
            type="monotone"
            dataKey={chartType === 'cumulative' ? 'totalReturn' : 'periodReturn'}
            stroke="#10b981"
            fill="url(#portfolioGradient)"
            strokeWidth={2}
            name="Portfolio"
          />
          
          {/* Benchmark Line */}
          {showBenchmark && benchmarkData && (
            <Line
              type="monotone"
              dataKey={chartType === 'cumulative' ? 'totalReturn' : 'periodReturn'}
              stroke="#6b7280"
              strokeWidth={1.5}
              strokeDasharray="5 5"
              dot={false}
              name="Benchmark"
            />
          )}
          
          {/* Gradient Definitions */}
          <defs>
            <linearGradient id="portfolioGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
            </linearGradient>
          </defs>
          
          <Tooltip content={<PerformanceTooltip />} />
          <Legend />
        </ComposedChart>
      </ResponsiveContainer>
      
      {/* Performance Metrics */}
      <div className="performance-metrics">
        <MetricDisplay
          label="Sharpe Ratio"
          value={calculateSharpeRatio(portfolioData)}
          format="decimal"
        />
        <MetricDisplay
          label="Max Drawdown"
          value={calculateMaxDrawdown(portfolioData)}
          format="percent"
          negative
        />
        <MetricDisplay
          label="Volatility"
          value={calculateVolatility(portfolioData)}
          format="percent"
        />
        <MetricDisplay
          label="Alpha"
          value={calculateAlpha(portfolioData, benchmarkData)}
          format="percent"
        />
      </div>
    </div>
  );
};
```

### Risk-Return Scatter Plot
```typescript
// RiskReturnScatterPlot.tsx
const RiskReturnScatterPlot: React.FC<{
  assets: AssetMetrics[];
  portfolioPoint?: { risk: number; return: number };
  benchmarkPoint?: { risk: number; return: number };
}> = ({ assets, portfolioPoint, benchmarkPoint }) => {
  const [selectedAssets, setSelectedAssets] = useState<string[]>([]);
  const [highlightQuadrant, setHighlightQuadrant] = useState<string | null>(null);
  
  return (
    <div className="risk-return-chart">
      <div className="chart-header">
        <h3>Risk vs Return Analysis</h3>
        <div className="quadrant-legend">
          <QuadrantIndicator 
            quadrant="high-return-low-risk" 
            label="🎯 Sweet Spot"
            active={highlightQuadrant === 'high-return-low-risk'}
            onClick={() => setHighlightQuadrant('high-return-low-risk')}
          />
          <QuadrantIndicator 
            quadrant="high-return-high-risk" 
            label="🚀 High Growth"
            active={highlightQuadrant === 'high-return-high-risk'}
            onClick={() => setHighlightQuadrant('high-return-high-risk')}
          />
          <QuadrantIndicator 
            quadrant="low-return-low-risk" 
            label="🛡️ Conservative"
            active={highlightQuadrant === 'low-return-low-risk'}
            onClick={() => setHighlightQuadrant('low-return-low-risk')}
          />
          <QuadrantIndicator 
            quadrant="low-return-high-risk" 
            label="⚠️ Avoid"
            active={highlightQuadrant === 'low-return-high-risk'}
            onClick={() => setHighlightQuadrant('low-return-high-risk')}
          />
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={400}>
        <ScatterChart>
          <XAxis 
            type="number" 
            dataKey="risk"
            name="Risk (Volatility)"
            tickFormatter={formatPercent}
            label={{ value: 'Risk (Volatility)', position: 'insideBottom', offset: -10 }}
          />
          <YAxis 
            type="number" 
            dataKey="return"
            name="Expected Return"
            tickFormatter={formatPercent}
            label={{ value: 'Expected Return', angle: -90, position: 'insideLeft' }}
          />
          
          {/* Quadrant Background */}
          <QuadrantBackground highlightQuadrant={highlightQuadrant} />
          
          {/* Efficient Frontier Line */}
          <Line 
            type="monotone"
            dataKey="efficientFrontier"
            stroke="#3b82f6"
            strokeWidth={2}
            strokeDasharray="3 3"
            dot={false}
            name="Efficient Frontier"
          />
          
          {/* Asset Scatter Points */}
          <Scatter 
            name="Assets" 
            data={assets}
            fill={(entry) => getAssetColor(entry)}
          >
            {assets.map((asset, index) => (
              <Cell 
                key={asset.symbol}
                fill={selectedAssets.includes(asset.symbol) ? '#10b981' : getAssetColor(asset)}
                stroke={selectedAssets.includes(asset.symbol) ? '#059669' : 'transparent'}
                strokeWidth={selectedAssets.includes(asset.symbol) ? 2 : 0}
                r={asset.marketCap ? Math.log(asset.marketCap) * 2 : 6}
              />
            ))}
          </Scatter>
          
          {/* Portfolio Point */}
          {portfolioPoint && (
            <Scatter
              name="Portfolio"
              data={[portfolioPoint]}
              fill="#8b5cf6"
              shape="diamond"
            />
          )}
          
          {/* Benchmark Point */}
          {benchmarkPoint && (
            <Scatter
              name="Benchmark"
              data={[benchmarkPoint]}
              fill="#f59e0b"
              shape="square"
            />
          )}
          
          <Tooltip content={<RiskReturnTooltip />} />
          <Legend />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};
```

### Interactive Treemap
```typescript
// InteractiveTreemap.tsx
const InteractiveTreemap: React.FC<{
  data: TreemapData[];
  colorBy: 'performance' | 'allocation' | 'sector';
  onNodeClick?: (node: TreemapData) => void;
}> = ({ data, colorBy, onNodeClick }) => {
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [zoomedNode, setZoomedNode] = useState<string | null>(null);
  
  const getNodeColor = (node: TreemapData) => {
    switch (colorBy) {
      case 'performance':
        return node.performance > 0 ? '#10b981' : '#ef4444';
      case 'allocation':
        const intensity = Math.min(node.allocation / 10, 1); // Max 10% for full intensity
        return `rgba(59, 130, 246, ${0.3 + intensity * 0.7})`;
      case 'sector':
        return SECTOR_COLORS[node.sector] || '#6b7280';
      default:
        return '#6b7280';
    }
  };
  
  return (
    <div className="treemap-container">
      <div className="treemap-controls">
        <ColorBySelector
          value={colorBy}
          options={[
            { value: 'performance', label: 'Performance' },
            { value: 'allocation', label: 'Allocation' },
            { value: 'sector', label: 'Sector' }
          ]}
          onChange={handleColorByChange}
        />
        {zoomedNode && (
          <Button variant="outline" onClick={() => setZoomedNode(null)}>
            Zoom Out
          </Button>
        )}
      </div>
      
      <ResponsiveContainer width="100%" height={400}>
        <Treemap
          data={zoomedNode ? data.filter(d => d.parent === zoomedNode) : data}
          dataKey="value"
          stroke="#fff"
          fill={getNodeColor}
        >
          {data.map((node, index) => (
            <Cell
              key={node.id}
              fill={getNodeColor(node)}
              stroke={hoveredNode === node.id ? '#374151' : '#fff'}
              strokeWidth={hoveredNode === node.id ? 2 : 1}
              onClick={() => handleNodeClick(node)}
              onMouseEnter={() => setHoveredNode(node.id)}
              onMouseLeave={() => setHoveredNode(null)}
            />
          ))}
        </Treemap>
      </ResponsiveContainer>
      
      {/* Node Details Panel */}
      {hoveredNode && (
        <TreemapTooltip 
          node={data.find(d => d.id === hoveredNode)}
          colorBy={colorBy}
        />
      )}
    </div>
  );
};
```

### Performance Attribution Waterfall
```typescript
// PerformanceWaterfallChart.tsx
const PerformanceWaterfallChart: React.FC<{
  attributionData: AttributionData[];
  baseReturn: number;
  totalReturn: number;
}> = ({ attributionData, baseReturn, totalReturn }) => {
  return (
    <div className="waterfall-chart">
      <h3>Performance Attribution</h3>
      
      <ResponsiveContainer width="100%" height={350}>
        <ComposedChart data={attributionData}>
          <XAxis 
            dataKey="factor"
            angle={-45}
            textAnchor="end"
            height={100}
          />
          <YAxis tickFormatter={formatPercent} />
          
          {/* Positive Contributions */}
          <Bar
            dataKey="positiveContribution"
            stackId="contribution"
            fill="#10b981"
            name="Positive"
          />
          
          {/* Negative Contributions */}
          <Bar
            dataKey="negativeContribution"
            stackId="contribution"
            fill="#ef4444"
            name="Negative"
          />
          
          {/* Running Total Line */}
          <Line
            type="monotone"
            dataKey="runningTotal"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={{ fill: '#3b82f6', r: 4 }}
            name="Running Total"
          />
          
          <Tooltip content={<AttributionTooltip />} />
          <Legend />
        </ComposedChart>
      </ResponsiveContainer>
      
      {/* Summary Stats */}
      <div className="attribution-summary">
        <div className="summary-row">
          <span>Base Return:</span>
          <span>{formatPercent(baseReturn)}</span>
        </div>
        <div className="summary-row">
          <span>Total Attribution:</span>
          <span>{formatPercent(totalReturn - baseReturn)}</span>
        </div>
        <div className="summary-row total">
          <span>Total Return:</span>
          <span>{formatPercent(totalReturn)}</span>
        </div>
      </div>
    </div>
  );
};
```

## 🎨 Visualization Styling System

```scss
// Chart component styles
.chart-container {
  .chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    
    .chart-title {
      h3 {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--text-primary);
      }
      
      .chart-subtitle {
        font-size: 0.875rem;
        color: var(--text-secondary);
      }
    }
    
    .chart-controls {
      display: flex;
      gap: 0.5rem;
      align-items: center;
    }
  }
  
  .chart-tooltip {
    background: white;
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    padding: 0.75rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    
    .tooltip-header {
      font-weight: 600;
      margin-bottom: 0.5rem;
      color: var(--text-primary);
    }
    
    .tooltip-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: 0.25rem;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .label {
        color: var(--text-secondary);
      }
      
      .value {
        font-weight: 500;
        
        &.positive { color: var(--success-color); }
        &.negative { color: var(--danger-color); }
      }
    }
  }
}

// Responsive chart adaptations
@media (max-width: 768px) {
  .chart-container {
    .chart-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.75rem;
    }
    
    .chart-controls {
      width: 100%;
      justify-content: space-between;
    }
  }
}
```

## 📊 Chart Performance Optimization

```typescript
// Chart optimization utilities
const ChartOptimizer = {
  // Data sampling for large datasets
  sampleData: (data: any[], maxPoints: number = 500) => {
    if (data.length <= maxPoints) return data;
    
    const step = Math.ceil(data.length / maxPoints);
    return data.filter((_, index) => index % step === 0);
  },
  
  // Debounced resize handler
  useResizeObserver: (ref: RefObject<HTMLElement>, callback: (size: { width: number; height: number }) => void) => {
    useEffect(() => {
      if (!ref.current) return;
      
      const observer = new ResizeObserver((entries) => {
        const { width, height } = entries[0].contentRect;
        callback({ width, height });
      });
      
      observer.observe(ref.current);
      return () => observer.disconnect();
    }, [ref, callback]);
  },
  
  // Virtual scrolling for large datasets
  useVirtualizedData: (data: any[], containerHeight: number, itemHeight: number) => {
    const [startIndex, setStartIndex] = useState(0);
    const [endIndex, setEndIndex] = useState(Math.ceil(containerHeight / itemHeight));
    
    const handleScroll = useCallback((scrollTop: number) => {
      const newStartIndex = Math.floor(scrollTop / itemHeight);
      const newEndIndex = newStartIndex + Math.ceil(containerHeight / itemHeight);
      
      setStartIndex(newStartIndex);
      setEndIndex(Math.min(newEndIndex, data.length));
    }, [data.length, itemHeight, containerHeight]);
    
    return {
      visibleData: data.slice(startIndex, endIndex),
      startIndex,
      endIndex,
      handleScroll
    };
  }
};
```

## 📈 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Chart render time | <300ms | - |
| Data update latency | <100ms | - |
| Memory usage (large datasets) | <100MB | - |
| User interaction responsiveness | <50ms | - |
| Mobile chart usability | >8/10 rating | - |

---

**Next**: Continue with user experience design.