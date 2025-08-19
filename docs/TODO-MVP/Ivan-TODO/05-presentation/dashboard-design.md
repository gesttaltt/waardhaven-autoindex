# 📊 Dashboard Design - Main Interface Layout

**Priority**: CRITICAL  
**Complexity**: High  
**Timeline**: 4-5 days  
**Value**: Primary user interface that drives daily engagement

## 🎯 Objective

Design and implement a comprehensive dashboard that:
- Provides immediate insight into portfolio performance
- Highlights actionable intelligence and opportunities
- Adapts to user preferences and behavior patterns
- Scales gracefully across all device sizes
- Maintains high performance with real-time updates

## 🏗️ Dashboard Architecture

### Layout Hierarchy
```
┌─────────────────────────────────────────────────────────┐
│                    TOP NAVIGATION                        │
│    Logo | Portfolio | Opportunities | Research | Alerts │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                   INTELLIGENCE BAR                       │
│        🧠 Today's Key Insights | 🚨 Active Alerts       │
└─────────────────────────────────────────────────────────┘
┌─────────────┬─────────────────────────┬─────────────────┐
│   SIDEBAR   │                         │   QUICK PANEL   │
│             │                         │                 │
│ 📈 Portfolio│      MAIN CONTENT       │ 🔍 Search       │
│ 👀 Watchlist│         AREA            │ 📰 News         │
│ 💡 Ideas    │                         │ 📊 Quick Stats  │
│ ⚙️ Settings │                         │ 🔔 Notifications│
│             │                         │                 │
└─────────────┴─────────────────────────┴─────────────────┘
```

## 📱 Responsive Layout System

### Breakpoint Strategy
```scss
// Mobile-first responsive design
$breakpoints: (
  'mobile': 320px,
  'tablet': 768px,
  'desktop': 1024px,
  'wide': 1400px
);

// Layout configurations per breakpoint
$layouts: (
  'mobile': (
    sidebar: 'hidden',
    main: 'full-width',
    quick-panel: 'bottom-sheet',
    intelligence-bar: 'collapsed'
  ),
  'tablet': (
    sidebar: 'collapsible',
    main: 'flexible',
    quick-panel: 'overlay',
    intelligence-bar: 'compact'
  ),
  'desktop': (
    sidebar: 'fixed-250px',
    main: 'flexible',
    quick-panel: 'fixed-300px',
    intelligence-bar: 'full'
  ),
  'wide': (
    sidebar: 'fixed-280px',
    main: 'max-width-1200px',
    quick-panel: 'fixed-350px',
    intelligence-bar: 'full'
  )
);
```

## 🧠 Intelligence Bar Design

```typescript
// IntelligenceBar.tsx
interface IntelligenceBarProps {
  insights: DailyInsight[];
  alerts: Alert[];
  userAttention: AttentionLevel;
}

const IntelligenceBar: React.FC<IntelligenceBarProps> = ({ insights, alerts, userAttention }) => {
  return (
    <div className="intelligence-bar">
      {/* High Priority Alerts */}
      {alerts.filter(alert => alert.priority === 'high').length > 0 && (
        <AlertSection 
          alerts={alerts.filter(alert => alert.priority === 'high')}
          variant="urgent"
        />
      )}
      
      {/* Key Daily Insights */}
      <InsightCarousel 
        insights={insights.slice(0, 3)}
        autoRotate={userAttention === 'low'}
      />
      
      {/* Quick Actions */}
      <QuickActionBar>
        <QuickAction icon="🔍" label="Scan Market" onClick={scanMarket} />
        <QuickAction icon="💼" label="Rebalance" onClick={openRebalancer} />
        <QuickAction icon="📊" label="Generate Report" onClick={generateReport} />
      </QuickActionBar>
      
      {/* Market Status */}
      <MarketStatusIndicator />
    </div>
  );
};

// Key Daily Insights Component
const InsightCarousel: React.FC<{ insights: DailyInsight[] }> = ({ insights }) => {
  const [currentInsight, setCurrentInsight] = useState(0);
  
  return (
    <div className="insight-carousel">
      <div className="insight-container">
        {insights.map((insight, index) => (
          <div 
            key={insight.id}
            className={`insight-card ${index === currentInsight ? 'active' : 'hidden'}`}
          >
            <div className="insight-icon">
              {getInsightIcon(insight.type)}
            </div>
            <div className="insight-content">
              <h4 className="insight-title">{insight.title}</h4>
              <p className="insight-summary">{insight.summary}</p>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => navigateToInsight(insight)}
              >
                Learn More →
              </Button>
            </div>
          </div>
        ))}
      </div>
      
      {/* Navigation dots */}
      <div className="insight-navigation">
        {insights.map((_, index) => (
          <button
            key={index}
            className={`nav-dot ${index === currentInsight ? 'active' : ''}`}
            onClick={() => setCurrentInsight(index)}
          />
        ))}
      </div>
    </div>
  );
};
```

## 📊 Main Content Area Layouts

### Dashboard Grid System
```typescript
// Dashboard layout configurations
const DASHBOARD_LAYOUTS = {
  'overview': {
    name: 'Portfolio Overview',
    default: true,
    components: [
      { id: 'portfolio-summary', size: 'large', position: [0, 0, 2, 1] },
      { id: 'performance-chart', size: 'large', position: [2, 0, 2, 1] },
      { id: 'top-movers', size: 'medium', position: [0, 1, 1, 1] },
      { id: 'recommendations', size: 'medium', position: [1, 1, 1, 1] },
      { id: 'market-sentiment', size: 'medium', position: [2, 1, 1, 1] },
      { id: 'news-feed', size: 'medium', position: [3, 1, 1, 1] }
    ]
  },
  'trading': {
    name: 'Active Trading',
    components: [
      { id: 'watchlist', size: 'large', position: [0, 0, 1, 2] },
      { id: 'active-chart', size: 'xlarge', position: [1, 0, 2, 2] },
      { id: 'order-book', size: 'medium', position: [3, 0, 1, 1] },
      { id: 'positions', size: 'medium', position: [3, 1, 1, 1] }
    ]
  },
  'research': {
    name: 'Stock Research',
    components: [
      { id: 'stock-screener', size: 'large', position: [0, 0, 2, 1] },
      { id: 'comparison-table', size: 'large', position: [2, 0, 2, 1] },
      { id: 'sector-analysis', size: 'medium', position: [0, 1, 1, 1] },
      { id: 'analyst-ratings', size: 'medium', position: [1, 1, 1, 1] },
      { id: 'financial-data', size: 'large', position: [2, 1, 2, 1] }
    ]
  },
  'analytics': {
    name: 'Performance Analytics',
    components: [
      { id: 'attribution-analysis', size: 'xlarge', position: [0, 0, 3, 1] },
      { id: 'risk-metrics', size: 'medium', position: [3, 0, 1, 1] },
      { id: 'benchmark-comparison', size: 'large', position: [0, 1, 2, 1] },
      { id: 'factor-exposure', size: 'large', position: [2, 1, 2, 1] }
    ]
  }
};

// Responsive grid component
const DashboardGrid: React.FC<{ layout: string }> = ({ layout }) => {
  const [gridLayout, setGridLayout] = useState(DASHBOARD_LAYOUTS[layout]);
  const [isEditing, setIsEditing] = useState(false);
  
  return (
    <div className="dashboard-grid">
      {/* Layout Controls */}
      <div className="grid-controls">
        <LayoutSelector 
          current={layout}
          options={Object.keys(DASHBOARD_LAYOUTS)}
          onChange={handleLayoutChange}
        />
        <Button 
          variant="outline"
          onClick={() => setIsEditing(!isEditing)}
        >
          {isEditing ? 'Save Layout' : 'Customize'}
        </Button>
      </div>
      
      {/* Responsive Grid */}
      <ResponsiveGridLayout
        className="grid-layout"
        layouts={gridLayout}
        breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
        cols={{ lg: 4, md: 3, sm: 2, xs: 1, xxs: 1 }}
        rowHeight={200}
        isDraggable={isEditing}
        isResizable={isEditing}
        onLayoutChange={handleLayoutSave}
      >
        {gridLayout.components.map(component => (
          <div key={component.id} className="grid-item">
            <ComponentRenderer 
              componentId={component.id}
              size={component.size}
              isEditing={isEditing}
            />
          </div>
        ))}
      </ResponsiveGridLayout>
    </div>
  );
};
```

## 🎴 Dashboard Component Library

### Portfolio Summary Card
```typescript
const PortfolioSummaryCard: React.FC = () => {
  const { portfolio, loading } = usePortfolio();
  const { performance } = usePortfolioPerformance();
  
  return (
    <Card className="portfolio-summary">
      <CardHeader>
        <div className="flex justify-between items-center">
          <Title>Portfolio Overview</Title>
          <TimeRangeSelector onChange={handleTimeRangeChange} />
        </div>
      </CardHeader>
      
      <CardBody>
        {/* Key Metrics Row */}
        <div className="metrics-grid">
          <MetricCard
            label="Total Value"
            value={formatCurrency(portfolio.totalValue)}
            change={performance.totalReturn}
            trend={performance.trend}
          />
          <MetricCard
            label="Day's Change"
            value={formatCurrency(performance.dayChange)}
            change={performance.dayChangePercent}
            trend={performance.dayTrend}
          />
          <MetricCard
            label="Total Return"
            value={formatPercent(performance.totalReturnPercent)}
            change={performance.totalReturn}
            trend={performance.overallTrend}
          />
        </div>
        
        {/* Performance Chart */}
        <div className="performance-chart">
          <MiniChart
            data={performance.chartData}
            type="area"
            height={120}
            showTooltip={true}
            color={performance.trend === 'up' ? 'green' : 'red'}
          />
        </div>
        
        {/* Top Holdings */}
        <div className="top-holdings">
          <h4 className="section-title">Top Holdings</h4>
          {portfolio.topHoldings.map(holding => (
            <HoldingRow
              key={holding.symbol}
              symbol={holding.symbol}
              name={holding.name}
              value={holding.value}
              weight={holding.weight}
              change={holding.dayChange}
              onClick={() => navigateToStock(holding.symbol)}
            />
          ))}
        </div>
      </CardBody>
    </Card>
  );
};

// Reusable Metric Card
const MetricCard: React.FC<{
  label: string;
  value: string;
  change?: number;
  trend?: 'up' | 'down' | 'neutral';
}> = ({ label, value, change, trend }) => {
  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      {change !== undefined && (
        <div className={`metric-change ${trend}`}>
          <TrendIcon trend={trend} />
          {formatPercent(Math.abs(change))}
        </div>
      )}
    </div>
  );
};
```

### Smart Recommendations Panel
```typescript
const SmartRecommendationsPanel: React.FC = () => {
  const { recommendations, loading } = useRecommendations();
  const [filter, setFilter] = useState<'all' | 'buy' | 'sell' | 'hold'>('all');
  
  return (
    <Card className="recommendations-panel">
      <CardHeader>
        <div className="flex justify-between items-center">
          <Title>🧠 Smart Recommendations</Title>
          <div className="flex gap-2">
            <FilterTabs
              value={filter}
              options={[
                { value: 'all', label: 'All' },
                { value: 'buy', label: 'Buy' },
                { value: 'sell', label: 'Sell' },
                { value: 'hold', label: 'Hold' }
              ]}
              onChange={setFilter}
            />
            <Button variant="outline" size="sm">
              Refresh
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardBody>
        {loading ? (
          <LoadingSpinner />
        ) : (
          <div className="recommendations-list">
            {recommendations
              .filter(rec => filter === 'all' || rec.action === filter)
              .slice(0, 5)
              .map(recommendation => (
                <RecommendationCard
                  key={recommendation.id}
                  recommendation={recommendation}
                  compact={true}
                  onClick={() => openRecommendationDetails(recommendation)}
                />
              ))}
          </div>
        )}
        
        {recommendations.length > 5 && (
          <div className="panel-footer">
            <Button variant="ghost" fullWidth>
              View All Recommendations ({recommendations.length})
            </Button>
          </div>
        )}
      </CardBody>
    </Card>
  );
};
```

### Market Opportunities Scanner
```typescript
const OpportunitiesScannerPanel: React.FC = () => {
  const { opportunities, scanStatus } = useOpportunityScanner();
  const [scanType, setScanType] = useState<'all' | 'value' | 'momentum' | 'catalyst'>('all');
  
  return (
    <Card className="opportunities-panel">
      <CardHeader>
        <div className="flex justify-between items-center">
          <Title>🔍 Market Opportunities</Title>
          <div className="flex items-center gap-2">
            <ScanStatusIndicator status={scanStatus} />
            <Button 
              variant="primary" 
              size="sm"
              onClick={triggerScan}
              disabled={scanStatus === 'scanning'}
            >
              {scanStatus === 'scanning' ? 'Scanning...' : 'Scan Now'}
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardBody>
        {/* Opportunity Type Filters */}
        <div className="opportunity-filters">
          <FilterChips
            value={scanType}
            options={[
              { value: 'all', label: 'All', count: opportunities.length },
              { value: 'value', label: '💎 Value', count: opportunities.filter(o => o.type === 'value').length },
              { value: 'momentum', label: '🚀 Momentum', count: opportunities.filter(o => o.type === 'momentum').length },
              { value: 'catalyst', label: '⚡ Catalyst', count: opportunities.filter(o => o.type === 'catalyst').length }
            ]}
            onChange={setScanType}
          />
        </div>
        
        {/* Opportunities List */}
        <div className="opportunities-list">
          {opportunities
            .filter(opp => scanType === 'all' || opp.type === scanType)
            .slice(0, 6)
            .map(opportunity => (
              <OpportunityCard
                key={opportunity.id}
                opportunity={opportunity}
                compact={true}
                onClick={() => analyzeOpportunity(opportunity)}
              />
            ))}
        </div>
        
        {/* Quick Stats */}
        <div className="scanner-stats">
          <div className="stat">
            <span className="stat-label">Last Scan:</span>
            <span className="stat-value">{formatTimeAgo(scanStatus.lastScan)}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Opportunities Found:</span>
            <span className="stat-value">{opportunities.length}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Success Rate:</span>
            <span className="stat-value">{scanStatus.successRate}%</span>
          </div>
        </div>
      </CardBody>
    </Card>
  );
};
```

## 🔧 Dashboard State Management

```typescript
// Dashboard state management with Zustand
interface DashboardState {
  // Layout state
  currentLayout: string;
  customLayouts: Record<string, DashboardLayout>;
  sidebarCollapsed: boolean;
  quickPanelOpen: boolean;
  
  // Data state
  portfolioData: PortfolioData | null;
  recommendations: Recommendation[];
  opportunities: Opportunity[];
  alerts: Alert[];
  
  // UI state
  loading: Record<string, boolean>;
  errors: Record<string, string>;
  lastUpdated: Record<string, Date>;
  
  // Actions
  setLayout: (layout: string) => void;
  toggleSidebar: () => void;
  toggleQuickPanel: () => void;
  refreshData: (components: string[]) => Promise<void>;
  updateComponent: (componentId: string, data: any) => void;
}

const useDashboardStore = create<DashboardState>((set, get) => ({
  // Initial state
  currentLayout: 'overview',
  customLayouts: {},
  sidebarCollapsed: false,
  quickPanelOpen: false,
  portfolioData: null,
  recommendations: [],
  opportunities: [],
  alerts: [],
  loading: {},
  errors: {},
  lastUpdated: {},
  
  // Actions
  setLayout: (layout) => set({ currentLayout: layout }),
  
  toggleSidebar: () => set(state => ({ 
    sidebarCollapsed: !state.sidebarCollapsed 
  })),
  
  toggleQuickPanel: () => set(state => ({ 
    quickPanelOpen: !state.quickPanelOpen 
  })),
  
  refreshData: async (components) => {
    const { loading } = get();
    
    // Set loading states
    const newLoading = { ...loading };
    components.forEach(comp => newLoading[comp] = true);
    set({ loading: newLoading });
    
    try {
      // Refresh data for specified components
      const refreshPromises = components.map(comp => refreshComponent(comp));
      await Promise.all(refreshPromises);
      
      // Clear loading states
      components.forEach(comp => newLoading[comp] = false);
      set({ loading: newLoading });
      
    } catch (error) {
      // Handle errors
      const newErrors = { ...get().errors };
      components.forEach(comp => {
        newErrors[comp] = 'Failed to refresh data';
        newLoading[comp] = false;
      });
      set({ loading: newLoading, errors: newErrors });
    }
  },
  
  updateComponent: (componentId, data) => {
    const updates: Partial<DashboardState> = {
      lastUpdated: {
        ...get().lastUpdated,
        [componentId]: new Date()
      }
    };
    
    // Update specific component data
    switch (componentId) {
      case 'portfolio-summary':
        updates.portfolioData = data;
        break;
      case 'recommendations':
        updates.recommendations = data;
        break;
      case 'opportunities':
        updates.opportunities = data;
        break;
      case 'alerts':
        updates.alerts = data;
        break;
    }
    
    set(updates);
  }
}));
```

## 🎨 Visual Design System

### Component Styling
```scss
// Dashboard-specific styles
.dashboard-container {
  display: grid;
  grid-template-areas:
    "nav nav nav"
    "intel intel intel"
    "sidebar main quick";
  grid-template-rows: auto auto 1fr;
  grid-template-columns: auto 1fr auto;
  height: 100vh;
  background: var(--bg-primary);
}

.intelligence-bar {
  grid-area: intel;
  padding: 1rem;
  background: linear-gradient(135deg, var(--primary-50) 0%, var(--primary-100) 100%);
  border-bottom: 1px solid var(--border-color);
  
  .insight-carousel {
    display: flex;
    align-items: center;
    gap: 1rem;
    
    .insight-card {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.75rem;
      background: white;
      border-radius: 0.5rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
      transition: all 0.2s ease;
      
      &:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateY(-1px);
      }
    }
  }
}

.dashboard-grid {
  grid-area: main;
  padding: 1rem;
  overflow: auto;
  
  .grid-item {
    background: white;
    border-radius: 0.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    overflow: hidden;
    transition: box-shadow 0.2s ease;
    
    &:hover {
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    // Size variants
    &.size-small { min-height: 200px; }
    &.size-medium { min-height: 300px; }
    &.size-large { min-height: 400px; }
    &.size-xlarge { min-height: 500px; }
  }
}

// Responsive adaptations
@media (max-width: 768px) {
  .dashboard-container {
    grid-template-areas:
      "nav"
      "intel"
      "main";
    grid-template-columns: 1fr;
  }
  
  .sidebar,
  .quick-panel {
    position: fixed;
    top: 0;
    height: 100vh;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    
    &.open {
      transform: translateX(0);
    }
  }
}
```

## 📊 Performance Optimization

### Lazy Loading Strategy
```typescript
// Lazy load dashboard components
const LazyPortfolioSummary = lazy(() => import('./PortfolioSummaryCard'));
const LazyRecommendations = lazy(() => import('./SmartRecommendationsPanel'));
const LazyOpportunities = lazy(() => import('./OpportunitiesScannerPanel'));

// Component renderer with lazy loading
const ComponentRenderer: React.FC<{ componentId: string }> = ({ componentId }) => {
  return (
    <Suspense fallback={<ComponentSkeleton />}>
      {(() => {
        switch (componentId) {
          case 'portfolio-summary':
            return <LazyPortfolioSummary />;
          case 'recommendations':
            return <LazyRecommendations />;
          case 'opportunities':
            return <LazyOpportunities />;
          default:
            return <div>Unknown component</div>;
        }
      })()}
    </Suspense>
  );
};

// Virtualization for large lists
const VirtualizedList: React.FC<{ items: any[]; renderItem: (item: any) => JSX.Element }> = ({ items, renderItem }) => {
  return (
    <FixedSizeList
      height={400}
      itemCount={items.length}
      itemSize={80}
      itemData={items}
    >
      {({ index, style, data }) => (
        <div style={style}>
          {renderItem(data[index])}
        </div>
      )}
    </FixedSizeList>
  );
};
```

## 📈 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Dashboard load time | <2 seconds | - |
| Component render time | <300ms | - |
| Layout switch time | <100ms | - |
| Memory usage | <50MB | - |
| User engagement | >85% daily usage | - |

---

**Next**: Continue with visualization components design.