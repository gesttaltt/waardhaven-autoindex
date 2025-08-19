# ⚙️ Customization System - Personalized User Experience

**Priority**: MEDIUM  
**Complexity**: Medium-High  
**Timeline**: 3-4 days  
**Value**: Enable users to tailor the platform to their specific needs and preferences

## 🎯 Objective

Build a comprehensive customization system that:
- Allows users to personalize their dashboard and workflows
- Adapts interface complexity based on user experience level
- Provides role-based views for different user types
- Enables custom alerts, notifications, and preferences
- Learns from user behavior to suggest optimizations

## 🎨 Customization Architecture

### User Preference Categories
```typescript
interface UserCustomization {
  // Interface preferences
  interface: {
    theme: 'light' | 'dark' | 'auto';
    density: 'compact' | 'comfortable' | 'spacious';
    complexity_level: 'beginner' | 'intermediate' | 'advanced';
    animation_level: 'minimal' | 'reduced' | 'full';
    font_size: 'small' | 'medium' | 'large';
  };
  
  // Dashboard layout
  dashboard: {
    layout_id: string;
    custom_components: DashboardComponent[];
    widget_sizes: Record<string, ComponentSize>;
    hidden_components: string[];
    component_order: string[];
  };
  
  // Data preferences
  data: {
    default_time_range: '1D' | '1W' | '1M' | '3M' | '6M' | '1Y' | '5Y';
    chart_types: Record<string, ChartType>;
    benchmark_symbol: string;
    currency_display: string;
    number_format: 'standard' | 'abbreviated' | 'scientific';
  };
  
  // Notifications
  notifications: {
    push_enabled: boolean;
    email_enabled: boolean;
    alert_types: AlertType[];
    frequency_limits: Record<string, number>;
    quiet_hours: { start: string; end: string; };
  };
  
  // Trading preferences
  trading: {
    default_order_type: 'market' | 'limit' | 'stop';
    confirmation_required: boolean;
    position_sizing_method: 'fixed_amount' | 'percentage' | 'risk_based';
    auto_rebalance: boolean;
    max_position_size: number;
  };
}
```

## 🏗️ Dashboard Customization Engine

### Drag-and-Drop Dashboard Builder
```typescript
// DashboardCustomizer.tsx
const DashboardCustomizer: React.FC = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [availableComponents, setAvailableComponents] = useState<ComponentLibrary[]>([]);
  const [currentLayout, setCurrentLayout] = useState<DashboardLayout>();
  const [previewMode, setPreviewMode] = useState(false);
  
  const COMPONENT_LIBRARY = {
    'portfolio': {
      'portfolio_summary': {
        title: 'Portfolio Summary',
        description: 'Overview of total portfolio value and performance',
        sizes: ['small', 'medium', 'large'],
        required_data: ['portfolio'],
        complexity: 'beginner'
      },
      'portfolio_allocation': {
        title: 'Asset Allocation',
        description: 'Visual breakdown of portfolio by asset class',
        sizes: ['medium', 'large'],
        required_data: ['portfolio', 'allocations'],
        complexity: 'intermediate'
      },
      'performance_attribution': {
        title: 'Performance Attribution',
        description: 'Detailed breakdown of return sources',
        sizes: ['large', 'xlarge'],
        required_data: ['portfolio', 'performance'],
        complexity: 'advanced'
      }
    },
    'market': {
      'market_overview': {
        title: 'Market Overview',
        description: 'Major indices and market sentiment',
        sizes: ['medium', 'large'],
        required_data: ['market_data'],
        complexity: 'beginner'
      },
      'sector_performance': {
        title: 'Sector Performance',
        description: 'Heatmap of sector returns',
        sizes: ['medium', 'large'],
        required_data: ['sector_data'],
        complexity: 'intermediate'
      }
    },
    'analysis': {
      'ai_recommendations': {
        title: 'AI Recommendations',
        description: 'Latest stock recommendations from AI analysis',
        sizes: ['medium', 'large'],
        required_data: ['recommendations'],
        complexity: 'beginner'
      },
      'opportunity_scanner': {
        title: 'Opportunity Scanner',
        description: 'Real-time market opportunity detection',
        sizes: ['large', 'xlarge'],
        required_data: ['opportunities'],
        complexity: 'intermediate'
      },
      'risk_monitor': {
        title: 'Risk Monitor',
        description: 'Portfolio risk metrics and alerts',
        sizes: ['medium', 'large'],
        required_data: ['risk_data'],
        complexity: 'advanced'
      }
    }
  };
  
  return (
    <div className="dashboard-customizer">
      {/* Customization Header */}
      <div className="customizer-header">
        <div className="header-left">
          <h2>Customize Dashboard</h2>
          <p>Drag components to create your perfect layout</p>
        </div>
        
        <div className="header-actions">
          <Button
            variant="outline"
            onClick={() => setPreviewMode(!previewMode)}
          >
            {previewMode ? 'Edit Mode' : 'Preview'}
          </Button>
          
          <LayoutTemplateSelector
            templates={DASHBOARD_TEMPLATES}
            onSelect={applyTemplate}
          />
          
          <Button
            variant="primary"
            onClick={saveDashboardLayout}
          >
            Save Layout
          </Button>
        </div>
      </div>
      
      <div className="customizer-content">
        {/* Component Library Sidebar */}
        <div className="component-library">
          <h3>Available Components</h3>
          
          <ComponentCategoryTabs
            categories={Object.keys(COMPONENT_LIBRARY)}
            activeCategory={activeCategory}
            onCategoryChange={setActiveCategory}
          />
          
          <div className="component-list">
            {Object.entries(COMPONENT_LIBRARY[activeCategory]).map(([id, component]) => (
              <DraggableComponent
                key={id}
                id={id}
                component={component}
                onDragStart={() => setDraggedComponent(id)}
              />
            ))}
          </div>
          
          {/* Custom Component Creator */}
          <div className="custom-component-section">
            <Button
              variant="outline"
              fullWidth
              onClick={() => openCustomComponentCreator()}
            >
              + Create Custom Component
            </Button>
          </div>
        </div>
        
        {/* Dashboard Canvas */}
        <div className="dashboard-canvas">
          <ResponsiveGridLayout
            className="layout"
            layouts={currentLayout}
            breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480 }}
            cols={{ lg: 12, md: 10, sm: 6, xs: 4 }}
            rowHeight={60}
            isDraggable={isEditing && !previewMode}
            isResizable={isEditing && !previewMode}
            onLayoutChange={handleLayoutChange}
            droppingItem={{ i: 'drop', w: 4, h: 4 }}
            isDroppable={isEditing}
          >
            {currentLayout.map(item => (
              <div
                key={item.i}
                className={`dashboard-component ${isEditing ? 'editing' : ''}`}
              >
                {/* Component Controls (in edit mode) */}
                {isEditing && !previewMode && (
                  <div className="component-controls">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => configureComponent(item.i)}
                    >
                      ⚙️
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => removeComponent(item.i)}
                    >
                      ✕
                    </Button>
                  </div>
                )}
                
                {/* Component Content */}
                <ComponentRenderer
                  componentId={item.i}
                  size={item}
                  preview={previewMode}
                />
              </div>
            ))}
          </ResponsiveGridLayout>
          
          {/* Drop Zone Indicator */}
          {isEditing && draggedComponent && (
            <div className="drop-zone-indicator">
              Drop component here to add to dashboard
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Draggable component from library
const DraggableComponent: React.FC<{
  id: string;
  component: ComponentDefinition;
  onDragStart: () => void;
}> = ({ id, component, onDragStart }) => {
  return (
    <div
      className="draggable-component"
      draggable
      onDragStart={onDragStart}
      data-component-id={id}
    >
      <div className="component-preview">
        <ComponentPreview componentId={id} />
      </div>
      
      <div className="component-info">
        <h4>{component.title}</h4>
        <p>{component.description}</p>
        
        <div className="component-metadata">
          <ComplexityBadge level={component.complexity} />
          <SizeBadges sizes={component.sizes} />
        </div>
      </div>
      
      <div className="drag-handle">
        <DragIcon />
      </div>
    </div>
  );
};
```

### Theme Customization System
```typescript
// ThemeCustomizer.tsx
const ThemeCustomizer: React.FC = () => {
  const [activeTheme, setActiveTheme] = useState('light');
  const [customTheme, setCustomTheme] = useState<CustomTheme>();
  const [previewMode, setPreviewMode] = useState(false);
  
  const PREDEFINED_THEMES = {
    'light': {
      name: 'Light Mode',
      colors: {
        primary: '#3b82f6',
        background: '#ffffff',
        surface: '#f8fafc',
        text: '#0f172a',
        border: '#e2e8f0'
      }
    },
    'dark': {
      name: 'Dark Mode',
      colors: {
        primary: '#60a5fa',
        background: '#0f172a',
        surface: '#1e293b',
        text: '#f8fafc',
        border: '#334155'
      }
    },
    'high_contrast': {
      name: 'High Contrast',
      colors: {
        primary: '#000000',
        background: '#ffffff',
        surface: '#f0f0f0',
        text: '#000000',
        border: '#000000'
      }
    },
    'terminal': {
      name: 'Terminal',
      colors: {
        primary: '#00ff00',
        background: '#000000',
        surface: '#1a1a1a',
        text: '#00ff00',
        border: '#333333'
      }
    }
  };
  
  return (
    <div className="theme-customizer">
      <div className="theme-header">
        <h2>Customize Appearance</h2>
        <div className="theme-actions">
          <Button
            variant="outline"
            onClick={() => setPreviewMode(!previewMode)}
          >
            {previewMode ? 'Edit' : 'Preview'}
          </Button>
          <Button
            variant="primary"
            onClick={saveTheme}
          >
            Save Theme
          </Button>
        </div>
      </div>
      
      <div className="theme-content">
        {/* Predefined Themes */}
        <div className="predefined-themes">
          <h3>Predefined Themes</h3>
          
          <div className="theme-grid">
            {Object.entries(PREDEFINED_THEMES).map(([id, theme]) => (
              <ThemePreviewCard
                key={id}
                themeId={id}
                theme={theme}
                active={activeTheme === id}
                onClick={() => setActiveTheme(id)}
              />
            ))}
          </div>
        </div>
        
        {/* Custom Theme Editor */}
        <div className="custom-theme-editor">
          <h3>Custom Theme</h3>
          
          <div className="color-customization">
            <ColorPicker
              label="Primary Color"
              value={customTheme?.colors.primary}
              onChange={(color) => updateThemeColor('primary', color)}
            />
            <ColorPicker
              label="Background Color"
              value={customTheme?.colors.background}
              onChange={(color) => updateThemeColor('background', color)}
            />
            <ColorPicker
              label="Text Color"
              value={customTheme?.colors.text}
              onChange={(color) => updateThemeColor('text', color)}
            />
            <ColorPicker
              label="Border Color"
              value={customTheme?.colors.border}
              onChange={(color) => updateThemeColor('border', color)}
            />
          </div>
          
          <div className="typography-customization">
            <h4>Typography</h4>
            
            <Select
              label="Font Family"
              value={customTheme?.typography.fontFamily}
              options={[
                { value: 'Inter', label: 'Inter (Default)' },
                { value: 'Roboto', label: 'Roboto' },
                { value: 'Open Sans', label: 'Open Sans' },
                { value: 'Fira Code', label: 'Fira Code (Monospace)' }
              ]}
              onChange={(font) => updateThemeTypography('fontFamily', font)}
            />
            
            <Slider
              label="Font Size Scale"
              value={customTheme?.typography.scale || 1}
              min={0.8}
              max={1.4}
              step={0.1}
              onChange={(scale) => updateThemeTypography('scale', scale)}
            />
          </div>
          
          <div className="spacing-customization">
            <h4>Spacing & Layout</h4>
            
            <Slider
              label="Component Spacing"
              value={customTheme?.spacing.component || 1}
              min={0.5}
              max={2}
              step={0.1}
              onChange={(spacing) => updateThemeSpacing('component', spacing)}
            />
            
            <Slider
              label="Border Radius"
              value={customTheme?.borderRadius || 8}
              min={0}
              max={20}
              step={2}
              onChange={(radius) => updateTheme('borderRadius', radius)}
            />
          </div>
        </div>
        
        {/* Theme Preview */}
        <div className="theme-preview">
          <h3>Preview</h3>
          
          <div className={`preview-container theme-${activeTheme}`}>
            <MockDashboard theme={activeTheme} customTheme={customTheme} />
          </div>
        </div>
      </div>
    </div>
  );
};

// Color accessibility checker
const ColorAccessibilityChecker: React.FC<{
  backgroundColor: string;
  textColor: string;
}> = ({ backgroundColor, textColor }) => {
  const contrastRatio = calculateContrastRatio(backgroundColor, textColor);
  const wcagLevel = getWCAGLevel(contrastRatio);
  
  return (
    <div className="accessibility-checker">
      <div className="contrast-info">
        <span>Contrast Ratio: {contrastRatio.toFixed(2)}</span>
        <WCAGBadge level={wcagLevel} />
      </div>
      
      {wcagLevel === 'fail' && (
        <div className="accessibility-warning">
          ⚠️ This color combination may be difficult to read
        </div>
      )}
    </div>
  );
};
```

### Alert & Notification Customization
```typescript
// AlertCustomizer.tsx
const AlertCustomizer: React.FC = () => {
  const [alertRules, setAlertRules] = useState<AlertRule[]>([]);
  const [notificationSettings, setNotificationSettings] = useState<NotificationSettings>();
  
  const ALERT_TYPES = {
    'price_movement': {
      name: 'Price Movement',
      description: 'Alert when stock price moves by a certain percentage',
      parameters: {
        'threshold': { type: 'percentage', default: 5, min: 1, max: 50 },
        'direction': { type: 'select', options: ['up', 'down', 'both'], default: 'both' },
        'timeframe': { type: 'select', options: ['1m', '5m', '1h', '1d'], default: '1d' }
      }
    },
    'volume_spike': {
      name: 'Volume Spike',
      description: 'Alert when trading volume exceeds normal levels',
      parameters: {
        'multiplier': { type: 'number', default: 3, min: 1.5, max: 10 },
        'lookback_period': { type: 'number', default: 20, min: 5, max: 100 }
      }
    },
    'recommendation_change': {
      name: 'AI Recommendation Change',
      description: 'Alert when AI recommendation changes for tracked stocks',
      parameters: {
        'min_confidence': { type: 'percentage', default: 70, min: 50, max: 95 },
        'action_types': { type: 'multiselect', options: ['buy', 'sell', 'hold'], default: ['buy', 'sell'] }
      }
    },
    'insider_activity': {
      name: 'Insider Activity',
      description: 'Alert when company insiders buy or sell shares',
      parameters: {
        'min_transaction_value': { type: 'currency', default: 100000, min: 10000 },
        'insider_types': { type: 'multiselect', options: ['CEO', 'CFO', 'Director', 'Officer'], default: ['CEO', 'CFO'] }
      }
    },
    'earnings_announcement': {
      name: 'Earnings Announcement',
      description: 'Alert before earnings announcements',
      parameters: {
        'days_before': { type: 'number', default: 3, min: 1, max: 14 },
        'include_guidance': { type: 'boolean', default: true }
      }
    }
  };
  
  return (
    <div className="alert-customizer">
      <div className="alert-header">
        <h2>Alert & Notification Settings</h2>
        <Button
          variant="primary"
          onClick={() => createNewAlert()}
        >
          + New Alert Rule
        </Button>
      </div>
      
      <div className="alert-content">
        {/* Global Notification Settings */}
        <div className="notification-settings">
          <h3>Notification Preferences</h3>
          
          <div className="notification-channels">
            <CheckboxGroup
              label="Notification Channels"
              options={[
                { value: 'push', label: '📱 Push Notifications' },
                { value: 'email', label: '📧 Email' },
                { value: 'sms', label: '💬 SMS' },
                { value: 'in_app', label: '🔔 In-App Only' }
              ]}
              value={notificationSettings?.channels || []}
              onChange={(channels) => updateNotificationSettings({ channels })}
            />
          </div>
          
          <div className="quiet-hours">
            <h4>Quiet Hours</h4>
            <TimePicker
              label="Start Time"
              value={notificationSettings?.quietHours?.start}
              onChange={(start) => updateQuietHours({ start })}
            />
            <TimePicker
              label="End Time"
              value={notificationSettings?.quietHours?.end}
              onChange={(end) => updateQuietHours({ end })}
            />
          </div>
          
          <div className="frequency-limits">
            <h4>Frequency Limits</h4>
            <Select
              label="Maximum alerts per hour"
              value={notificationSettings?.maxAlertsPerHour || 10}
              options={[
                { value: 5, label: '5 alerts' },
                { value: 10, label: '10 alerts' },
                { value: 20, label: '20 alerts' },
                { value: -1, label: 'Unlimited' }
              ]}
              onChange={(limit) => updateNotificationSettings({ maxAlertsPerHour: limit })}
            />
          </div>
        </div>
        
        {/* Alert Rules List */}
        <div className="alert-rules">
          <h3>Active Alert Rules</h3>
          
          {alertRules.length === 0 ? (
            <EmptyState
              icon="🔔"
              title="No alert rules set up"
              description="Create your first alert rule to get notified about important market events"
              action={
                <Button onClick={() => createNewAlert()}>
                  Create Alert Rule
                </Button>
              }
            />
          ) : (
            <div className="alert-rules-list">
              {alertRules.map(rule => (
                <AlertRuleCard
                  key={rule.id}
                  rule={rule}
                  onEdit={() => editAlertRule(rule)}
                  onDelete={() => deleteAlertRule(rule.id)}
                  onToggle={() => toggleAlertRule(rule.id)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
      
      {/* Alert Rule Editor Modal */}
      {showAlertEditor && (
        <AlertRuleEditor
          rule={editingRule}
          alertTypes={ALERT_TYPES}
          onSave={saveAlertRule}
          onCancel={() => setShowAlertEditor(false)}
        />
      )}
    </div>
  );
};

// Alert Rule Editor
const AlertRuleEditor: React.FC<{
  rule?: AlertRule;
  alertTypes: Record<string, AlertTypeDefinition>;
  onSave: (rule: AlertRule) => void;
  onCancel: () => void;
}> = ({ rule, alertTypes, onSave, onCancel }) => {
  const [selectedType, setSelectedType] = useState(rule?.type || '');
  const [ruleConfig, setRuleConfig] = useState(rule || {});
  const [targetSymbols, setTargetSymbols] = useState<string[]>(rule?.symbols || []);
  
  return (
    <Modal isOpen onClose={onCancel} size="large">
      <ModalHeader>
        <h3>{rule ? 'Edit Alert Rule' : 'Create Alert Rule'}</h3>
      </ModalHeader>
      
      <ModalBody>
        <div className="alert-rule-form">
          {/* Alert Type Selection */}
          <div className="alert-type-selection">
            <label>Alert Type</label>
            <div className="alert-type-grid">
              {Object.entries(alertTypes).map(([typeId, type]) => (
                <div
                  key={typeId}
                  className={`alert-type-card ${selectedType === typeId ? 'selected' : ''}`}
                  onClick={() => setSelectedType(typeId)}
                >
                  <h4>{type.name}</h4>
                  <p>{type.description}</p>
                </div>
              ))}
            </div>
          </div>
          
          {/* Target Symbols */}
          <div className="target-symbols">
            <label>Target Stocks/Symbols</label>
            <SymbolSelector
              selected={targetSymbols}
              onChange={setTargetSymbols}
              placeholder="Add stocks to monitor..."
              allowWatchlistImport={true}
              allowPortfolioImport={true}
            />
          </div>
          
          {/* Alert Parameters */}
          {selectedType && (
            <div className="alert-parameters">
              <h4>Alert Parameters</h4>
              {Object.entries(alertTypes[selectedType].parameters).map(([paramId, param]) => (
                <ParameterInput
                  key={paramId}
                  parameter={param}
                  value={ruleConfig[paramId]}
                  onChange={(value) => setRuleConfig(prev => ({ ...prev, [paramId]: value }))}
                />
              ))}
            </div>
          )}
          
          {/* Alert Preview */}
          <div className="alert-preview">
            <h4>Preview</h4>
            <AlertPreview
              type={selectedType}
              config={ruleConfig}
              symbols={targetSymbols}
            />
          </div>
        </div>
      </ModalBody>
      
      <ModalFooter>
        <Button variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button
          variant="primary"
          onClick={() => onSave({ ...ruleConfig, type: selectedType, symbols: targetSymbols })}
          disabled={!selectedType || targetSymbols.length === 0}
        >
          {rule ? 'Save Changes' : 'Create Alert'}
        </Button>
      </ModalFooter>
    </Modal>
  );
};
```

## 🤖 Adaptive Learning System

```typescript
// AdaptiveLearningEngine.tsx
const AdaptiveLearningEngine = {
  // Track user behavior patterns
  trackUserBehavior: (event: UserBehaviorEvent) => {
    const behaviorLog = {
      timestamp: Date.now(),
      userId: getCurrentUserId(),
      action: event.action,
      context: event.context,
      duration: event.duration,
      success: event.success
    };
    
    // Store behavior data
    storeBehaviorEvent(behaviorLog);
    
    // Analyze patterns
    analyzeBehaviorPatterns(behaviorLog);
  },
  
  // Generate personalization suggestions
  generateSuggestions: async (userId: string): Promise<PersonalizationSuggestion[]> => {
    const userBehavior = await getUserBehaviorHistory(userId);
    const currentSettings = await getUserSettings(userId);
    
    const suggestions: PersonalizationSuggestion[] = [];
    
    // Analyze dashboard usage
    const dashboardAnalysis = analyzeDashboardUsage(userBehavior);
    if (dashboardAnalysis.underutilizedComponents.length > 0) {
      suggestions.push({
        type: 'hide_component',
        title: 'Simplify Your Dashboard',
        description: `Hide unused components: ${dashboardAnalysis.underutilizedComponents.join(', ')}`,
        impact: 'medium',
        category: 'layout'
      });
    }
    
    // Analyze feature usage
    const featureAnalysis = analyzeFeatureUsage(userBehavior);
    if (featureAnalysis.advancedFeaturesReady) {
      suggestions.push({
        type: 'complexity_upgrade',
        title: 'Ready for Advanced Features?',
        description: 'Based on your usage, you might benefit from advanced analysis tools',
        impact: 'high',
        category: 'features'
      });
    }
    
    // Analyze notification effectiveness
    const notificationAnalysis = analyzeNotificationResponse(userBehavior);
    if (notificationAnalysis.lowResponseRate) {
      suggestions.push({
        type: 'notification_optimization',
        title: 'Optimize Your Alerts',
        description: 'Reduce notification frequency or adjust types based on your response patterns',
        impact: 'medium',
        category: 'notifications'
      });
    }
    
    return suggestions;
  },
  
  // Auto-apply safe optimizations
  autoOptimize: async (userId: string) => {
    const suggestions = await this.generateSuggestions(userId);
    const safeOptimizations = suggestions.filter(s => s.autoApplyable && s.impact !== 'high');
    
    for (const optimization of safeOptimizations) {
      await applyOptimization(userId, optimization);
      
      // Log the auto-optimization
      logAutoOptimization(userId, optimization);
    }
    
    return safeOptimizations;
  }
};

// Usage pattern analysis
const UsagePatternAnalyzer = {
  // Analyze component usage patterns
  analyzeDashboardUsage: (events: UserBehaviorEvent[]) => {
    const componentInteractions = events.filter(e => e.action === 'component_interaction');
    const componentUsage = componentInteractions.reduce((acc, event) => {
      const componentId = event.context.componentId;
      acc[componentId] = (acc[componentId] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    const totalInteractions = Object.values(componentUsage).reduce((sum, count) => sum + count, 0);
    const underutilizedComponents = Object.entries(componentUsage)
      .filter(([_, count]) => count / totalInteractions < 0.05) // Less than 5% usage
      .map(([componentId]) => componentId);
    
    return {
      componentUsage,
      underutilizedComponents,
      totalInteractions
    };
  },
  
  // Analyze feature adoption
  analyzeFeatureUsage: (events: UserBehaviorEvent[]) => {
    const featureUsage = events.filter(e => e.action === 'feature_usage');
    const advancedFeatures = ['advanced_charts', 'custom_alerts', 'portfolio_optimization'];
    
    const basicFeatureUsage = featureUsage.filter(e => !advancedFeatures.includes(e.context.feature));
    const advancedFeatureUsage = featureUsage.filter(e => advancedFeatures.includes(e.context.feature));
    
    // Determine if user is ready for advanced features
    const advancedFeaturesReady = 
      basicFeatureUsage.length > 50 && // Sufficient basic usage
      advancedFeatureUsage.length < 5; // Limited advanced usage
    
    return {
      basicFeatureUsage: basicFeatureUsage.length,
      advancedFeatureUsage: advancedFeatureUsage.length,
      advancedFeaturesReady
    };
  }
};
```

## 🎨 Customization UI Components

```scss
// Customization interface styles
.customization-interface {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 2rem;
  height: 100vh;
  
  .customization-sidebar {
    background: var(--surface-color);
    border-right: 1px solid var(--border-color);
    padding: 1.5rem;
    overflow-y: auto;
    
    .customization-section {
      margin-bottom: 2rem;
      
      h3 {
        margin-bottom: 1rem;
        color: var(--text-primary);
        font-weight: 600;
      }
      
      .customization-option {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem;
        border-radius: 0.5rem;
        cursor: pointer;
        transition: background-color 0.2s ease;
        
        &:hover {
          background: var(--hover-color);
        }
        
        &.active {
          background: var(--primary-color);
          color: white;
        }
        
        .option-icon {
          font-size: 1.25rem;
        }
        
        .option-content {
          flex: 1;
          
          .option-title {
            font-weight: 500;
            margin-bottom: 0.25rem;
          }
          
          .option-description {
            font-size: 0.875rem;
            opacity: 0.7;
          }
        }
      }
    }
  }
  
  .customization-main {
    padding: 2rem;
    overflow-y: auto;
    
    .customization-header {
      display: flex;
      justify-content: between;
      align-items: center;
      margin-bottom: 2rem;
      
      h2 {
        color: var(--text-primary);
        font-weight: 700;
      }
      
      .preview-toggle {
        display: flex;
        gap: 0.5rem;
      }
    }
    
    .customization-content {
      .setting-group {
        margin-bottom: 2rem;
        
        .setting-group-title {
          font-size: 1.125rem;
          font-weight: 600;
          margin-bottom: 1rem;
          color: var(--text-primary);
        }
        
        .setting-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          border: 1px solid var(--border-color);
          border-radius: 0.5rem;
          margin-bottom: 0.75rem;
          
          .setting-info {
            .setting-label {
              font-weight: 500;
              margin-bottom: 0.25rem;
            }
            
            .setting-description {
              font-size: 0.875rem;
              color: var(--text-secondary);
            }
          }
          
          .setting-control {
            min-width: 200px;
            text-align: right;
          }
        }
      }
    }
  }
}

// Theme preview styles
.theme-preview-card {
  border: 2px solid transparent;
  border-radius: 0.75rem;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: var(--primary-color);
  }
  
  &.active {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
  }
  
  .theme-preview-content {
    .theme-colors {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 0.75rem;
      
      .color-swatch {
        width: 24px;
        height: 24px;
        border-radius: 4px;
        border: 1px solid rgba(0,0,0,0.1);
      }
    }
    
    .theme-name {
      font-weight: 500;
      color: var(--text-primary);
    }
  }
}
```

## 📊 Customization Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| User customization adoption | >60% | - |
| Dashboard personalization rate | >75% | - |
| Theme customization usage | >40% | - |
| Alert rule creation rate | >50% | - |
| User satisfaction with customization | >8.5/10 | - |

---

**Next**: Complete 05-presentation section and move to 06-infrastructure files.