# 🎭 User Experience Design - Flows & Interactions

**Priority**: HIGH  
**Complexity**: Medium  
**Timeline**: 3-4 days  
**Value**: Ensure users can efficiently accomplish their investment goals

## 🎯 Objective

Design intuitive user experience flows that:
- Guide users to accomplish their investment goals efficiently
- Reduce cognitive load through smart defaults and suggestions
- Provide contextual help and education where needed
- Support both novice and expert user workflows
- Enable quick decision-making with confidence

## 🗺️ User Journey Mapping

### Primary User Personas
```typescript
interface UserPersona {
  id: string;
  name: string;
  experience: 'beginner' | 'intermediate' | 'advanced';
  goals: string[];
  pain_points: string[];
  preferred_workflows: string[];
}

const USER_PERSONAS = {
  'novice_investor': {
    id: 'novice_investor',
    name: 'Sarah - New Investor',
    experience: 'beginner',
    goals: [
      'Learn about investing',
      'Start building a portfolio',
      'Understand risks',
      'Get reliable recommendations'
    ],
    pain_points: [
      'Overwhelmed by information',
      'Afraid of making mistakes',
      'Doesn\'t understand financial jargon',
      'Needs guidance and education'
    ],
    preferred_workflows: [
      'Guided onboarding',
      'Simple dashboard',
      'Educational tooltips',
      'Conservative recommendations'
    ]
  },
  
  'active_trader': {
    id: 'active_trader',
    name: 'Mike - Active Trader',
    experience: 'intermediate',
    goals: [
      'Find short-term opportunities',
      'Track multiple positions',
      'Get timely alerts',
      'Analyze technical patterns'
    ],
    pain_points: [
      'Information overload',
      'Missing opportunities',
      'Slow data updates',
      'Too many clicks to execute'
    ],
    preferred_workflows: [
      'Real-time dashboard',
      'Quick-action buttons',
      'Customizable alerts',
      'Keyboard shortcuts'
    ]
  },
  
  'portfolio_manager': {
    id: 'portfolio_manager',
    name: 'David - Portfolio Manager',
    experience: 'advanced',
    goals: [
      'Optimize portfolio allocation',
      'Manage risk exposure',
      'Track performance attribution',
      'Research new investments'
    ],
    pain_points: [
      'Need comprehensive analytics',
      'Complex rebalancing decisions',
      'Risk monitoring complexity',
      'Time-consuming research'
    ],
    preferred_workflows: [
      'Advanced analytics',
      'Bulk operations',
      'Custom reports',
      'API access'
    ]
  }
};
```

## 🚀 Onboarding Experience

### Progressive Disclosure Onboarding
```typescript
// OnboardingFlow.tsx
const OnboardingFlow: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [userProfile, setUserProfile] = useState<Partial<UserProfile>>({});
  
  const ONBOARDING_STEPS = [
    {
      id: 'welcome',
      title: 'Welcome to Intelligent Investing',
      component: WelcomeStep,
      skippable: false
    },
    {
      id: 'goals',
      title: 'What are your investment goals?',
      component: GoalsStep,
      skippable: false
    },
    {
      id: 'experience',
      title: 'Tell us about your experience',
      component: ExperienceStep,
      skippable: false
    },
    {
      id: 'risk_tolerance',
      title: 'How do you feel about risk?',
      component: RiskToleranceStep,
      skippable: false
    },
    {
      id: 'portfolio_setup',
      title: 'Let\'s set up your portfolio',
      component: PortfolioSetupStep,
      skippable: true
    },
    {
      id: 'preferences',
      title: 'Customize your experience',
      component: PreferencesStep,
      skippable: true
    },
    {
      id: 'tour',
      title: 'Take a quick tour',
      component: PlatformTourStep,
      skippable: true
    }
  ];
  
  return (
    <div className="onboarding-container">
      {/* Progress Indicator */}
      <div className="onboarding-progress">
        <ProgressSteps
          steps={ONBOARDING_STEPS.map(step => ({
            id: step.id,
            title: step.title,
            completed: currentStep > ONBOARDING_STEPS.findIndex(s => s.id === step.id),
            current: currentStep === ONBOARDING_STEPS.findIndex(s => s.id === step.id)
          }))}
        />
      </div>
      
      {/* Step Content */}
      <div className="onboarding-content">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            {(() => {
              const StepComponent = ONBOARDING_STEPS[currentStep].component;
              return (
                <StepComponent
                  userProfile={userProfile}
                  onProfileUpdate={setUserProfile}
                  onNext={() => setCurrentStep(prev => Math.min(prev + 1, ONBOARDING_STEPS.length - 1))}
                  onBack={() => setCurrentStep(prev => Math.max(prev - 1, 0))}
                  onSkip={() => setCurrentStep(prev => prev + 1)}
                />
              );
            })()}
          </motion.div>
        </AnimatePresence>
      </div>
      
      {/* Navigation */}
      <div className="onboarding-navigation">
        <Button
          variant="outline"
          onClick={() => setCurrentStep(prev => Math.max(prev - 1, 0))}
          disabled={currentStep === 0}
        >
          Back
        </Button>
        
        <div className="step-indicator">
          {currentStep + 1} of {ONBOARDING_STEPS.length}
        </div>
        
        <div className="next-actions">
          {ONBOARDING_STEPS[currentStep].skippable && (
            <Button
              variant="ghost"
              onClick={() => setCurrentStep(prev => prev + 1)}
            >
              Skip
            </Button>
          )}
          <Button
            variant="primary"
            onClick={() => {
              if (currentStep === ONBOARDING_STEPS.length - 1) {
                completeOnboarding(userProfile);
              } else {
                setCurrentStep(prev => prev + 1);
              }
            }}
          >
            {currentStep === ONBOARDING_STEPS.length - 1 ? 'Get Started' : 'Continue'}
          </Button>
        </div>
      </div>
    </div>
  );
};

// Risk Tolerance Assessment Step
const RiskToleranceStep: React.FC<OnboardingStepProps> = ({ userProfile, onProfileUpdate, onNext }) => {
  const [selectedScenario, setSelectedScenario] = useState<string | null>(null);
  
  const RISK_SCENARIOS = [
    {
      id: 'conservative',
      title: 'Conservative Investor',
      description: 'I prefer steady, predictable returns even if they\'re lower',
      scenario: 'Your portfolio drops 5% in a month. How do you feel?',
      response: 'Concerned but okay - I expected some fluctuation',
      characteristics: ['Capital preservation', 'Steady income', 'Low volatility'],
      allocation: { stocks: 30, bonds: 60, cash: 10 }
    },
    {
      id: 'moderate',
      title: 'Moderate Investor',
      description: 'I want growth but can handle some ups and downs',
      scenario: 'Your portfolio drops 15% in a month. How do you feel?',
      response: 'Nervous but I understand markets go up and down',
      characteristics: ['Balanced growth', 'Moderate risk', 'Long-term focus'],
      allocation: { stocks: 60, bonds: 30, cash: 10 }
    },
    {
      id: 'aggressive',
      title: 'Aggressive Investor',
      description: 'I want maximum growth and can handle significant volatility',
      scenario: 'Your portfolio drops 25% in a month. How do you feel?',
      response: 'Disappointed but see it as a buying opportunity',
      characteristics: ['Maximum growth', 'High volatility tolerance', 'Long-term horizon'],
      allocation: { stocks: 80, bonds: 15, cash: 5 }
    }
  ];
  
  return (
    <div className="risk-tolerance-step">
      <div className="step-header">
        <h2>How do you feel about investment risk?</h2>
        <p>Understanding your risk tolerance helps us provide better recommendations</p>
      </div>
      
      <div className="risk-scenarios">
        {RISK_SCENARIOS.map(scenario => (
          <div
            key={scenario.id}
            className={`risk-scenario ${selectedScenario === scenario.id ? 'selected' : ''}`}
            onClick={() => setSelectedScenario(scenario.id)}
          >
            <div className="scenario-header">
              <h3>{scenario.title}</h3>
              <p>{scenario.description}</p>
            </div>
            
            <div className="scenario-test">
              <div className="scenario-question">
                <strong>Scenario:</strong> {scenario.scenario}
              </div>
              <div className="scenario-response">
                <strong>Your response:</strong> "{scenario.response}"
              </div>
            </div>
            
            <div className="scenario-details">
              <div className="characteristics">
                <h4>Investment Characteristics:</h4>
                <ul>
                  {scenario.characteristics.map(char => (
                    <li key={char}>{char}</li>
                  ))}
                </ul>
              </div>
              
              <div className="sample-allocation">
                <h4>Sample Allocation:</h4>
                <div className="allocation-chart">
                  <div className="allocation-bar">
                    <div 
                      className="stocks" 
                      style={{ width: `${scenario.allocation.stocks}%` }}
                    >
                      Stocks {scenario.allocation.stocks}%
                    </div>
                    <div 
                      className="bonds" 
                      style={{ width: `${scenario.allocation.bonds}%` }}
                    >
                      Bonds {scenario.allocation.bonds}%
                    </div>
                    <div 
                      className="cash" 
                      style={{ width: `${scenario.allocation.cash}%` }}
                    >
                      Cash {scenario.allocation.cash}%
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {selectedScenario && (
        <div className="step-actions">
          <Button
            variant="primary"
            onClick={() => {
              onProfileUpdate({
                ...userProfile,
                riskTolerance: selectedScenario
              });
              onNext();
            }}
          >
            Continue with {RISK_SCENARIOS.find(s => s.id === selectedScenario)?.title}
          </Button>
        </div>
      )}
    </div>
  );
};
```

## 🎯 Core User Workflows

### Stock Research Workflow
```typescript
// StockResearchWorkflow.tsx
const StockResearchWorkflow: React.FC<{ symbol?: string }> = ({ symbol: initialSymbol }) => {
  const [currentSymbol, setCurrentSymbol] = useState(initialSymbol);
  const [researchTabs, setResearchTabs] = useState(['overview']);
  const [comparisonList, setComparisonList] = useState<string[]>([]);
  
  const RESEARCH_TABS = {
    'overview': {
      title: 'Overview',
      component: StockOverviewTab,
      icon: '📊'
    },
    'analysis': {
      title: 'AI Analysis',
      component: AIAnalysisTab,
      icon: '🧠'
    },
    'financials': {
      title: 'Financials',
      component: FinancialsTab,
      icon: '💰'
    },
    'technicals': {
      title: 'Technical Analysis',
      component: TechnicalAnalysisTab,
      icon: '📈'
    },
    'news': {
      title: 'News & Events',
      component: NewsTab,
      icon: '📰'
    },
    'insider': {
      title: 'Insider Activity',
      component: InsiderActivityTab,
      icon: '👥'
    }
  };
  
  return (
    <div className="stock-research-workflow">
      {/* Research Header */}
      <div className="research-header">
        <StockSearchBar
          value={currentSymbol}
          onChange={setCurrentSymbol}
          placeholder="Search stocks to research..."
          showRecentSearches={true}
          showSuggestions={true}
        />
        
        <div className="research-actions">
          <Button
            variant="outline"
            onClick={() => addToComparison(currentSymbol)}
            disabled={comparisonList.includes(currentSymbol)}
          >
            Add to Compare
          </Button>
          <Button
            variant="outline"
            onClick={() => addToWatchlist(currentSymbol)}
          >
            Add to Watchlist
          </Button>
          <Button
            variant="primary"
            onClick={() => openTradingModal(currentSymbol)}
          >
            Trade
          </Button>
        </div>
      </div>
      
      {/* Research Tabs */}
      <div className="research-tabs">
        <TabNavigation
          tabs={Object.entries(RESEARCH_TABS).map(([key, tab]) => ({
            id: key,
            label: tab.title,
            icon: tab.icon,
            active: researchTabs.includes(key)
          }))}
          onTabClick={(tabId) => {
            if (!researchTabs.includes(tabId)) {
              setResearchTabs(prev => [...prev, tabId]);
            }
          }}
          onTabClose={(tabId) => {
            setResearchTabs(prev => prev.filter(id => id !== tabId));
          }}
        />
      </div>
      
      {/* Research Content */}
      <div className="research-content">
        <TabPanels
          activeTabs={researchTabs}
          panels={Object.entries(RESEARCH_TABS).reduce((acc, [key, tab]) => {
            acc[key] = (
              <tab.component
                symbol={currentSymbol}
                onSymbolChange={setCurrentSymbol}
                comparisonList={comparisonList}
                onAddToComparison={addToComparison}
              />
            );
            return acc;
          }, {} as Record<string, React.ReactNode>)}
        />
      </div>
      
      {/* Comparison Panel */}
      {comparisonList.length > 0 && (
        <ComparisonPanel
          symbols={comparisonList}
          onRemoveSymbol={(symbol) => setComparisonList(prev => prev.filter(s => s !== symbol))}
          onClearAll={() => setComparisonList([])}
        />
      )}
    </div>
  );
};

// AI Analysis Tab with Smart Insights
const AIAnalysisTab: React.FC<{ symbol: string }> = ({ symbol }) => {
  const { analysis, loading } = useAIAnalysis(symbol);
  const [selectedInsight, setSelectedInsight] = useState<string | null>(null);
  
  return (
    <div className="ai-analysis-tab">
      {loading ? (
        <AnalysisLoadingState />
      ) : (
        <>
          {/* Quick Recommendation */}
          <div className="quick-recommendation">
            <RecommendationCard
              recommendation={analysis.recommendation}
              showDetailedView={true}
              onExplainClick={() => setSelectedInsight('recommendation')}
            />
          </div>
          
          {/* Key Insights Grid */}
          <div className="insights-grid">
            <InsightCard
              title="🎯 Price Target"
              value={analysis.priceTarget}
              confidence={analysis.priceTargetConfidence}
              explanation="Based on DCF, comparable analysis, and technical levels"
              onClick={() => setSelectedInsight('price_target')}
            />
            <InsightCard
              title="⚠️ Risk Assessment"
              value={analysis.riskScore}
              scale="Low to High"
              explanation="Comprehensive risk analysis including volatility, fundamentals, and events"
              onClick={() => setSelectedInsight('risk')}
            />
            <InsightCard
              title="📈 Technical Signal"
              value={analysis.technicalSignal}
              trend={analysis.technicalTrend}
              explanation="Multiple timeframe technical analysis with support/resistance levels"
              onClick={() => setSelectedInsight('technical')}
            />
            <InsightCard
              title="💼 Insider Activity"
              value={analysis.insiderScore}
              change={analysis.insiderTrend}
              explanation="Recent insider trading patterns and their historical significance"
              onClick={() => setSelectedInsight('insider')}
            />
          </div>
          
          {/* Detailed Analysis Sections */}
          <div className="detailed-analysis">
            <Accordion>
              <AccordionItem title="🔍 Pattern Recognition">
                <PatternAnalysisSection patterns={analysis.patterns} />
              </AccordionItem>
              <AccordionItem title="📊 Valuation Analysis">
                <ValuationAnalysisSection valuation={analysis.valuation} />
              </AccordionItem>
              <AccordionItem title="🏢 Fundamental Health">
                <FundamentalAnalysisSection fundamentals={analysis.fundamentals} />
              </AccordionItem>
              <AccordionItem title="🔮 Predictive Modeling">
                <PredictiveModelingSection predictions={analysis.predictions} />
              </AccordionItem>
            </Accordion>
          </div>
        </>
      )}
      
      {/* Insight Explanation Modal */}
      {selectedInsight && (
        <InsightExplanationModal
          insight={selectedInsight}
          data={analysis}
          onClose={() => setSelectedInsight(null)}
        />
      )}
    </div>
  );
};
```

### Portfolio Management Workflow
```typescript
// PortfolioManagementWorkflow.tsx
const PortfolioManagementWorkflow: React.FC = () => {
  const { portfolio, loading } = usePortfolio();
  const [selectedAction, setSelectedAction] = useState<string | null>(null);
  const [selectedPositions, setSelectedPositions] = useState<string[]>([]);
  
  const PORTFOLIO_ACTIONS = {
    'rebalance': {
      title: 'Rebalance Portfolio',
      description: 'Adjust allocations to target weights',
      component: RebalanceModal,
      requiresSelection: false
    },
    'trim_winners': {
      title: 'Trim Winners',
      description: 'Take profits from top performers',
      component: TrimWinnersModal,
      requiresSelection: false
    },
    'add_positions': {
      title: 'Add Positions',
      description: 'Add recommended stocks to portfolio',
      component: AddPositionsModal,
      requiresSelection: false
    },
    'review_losers': {
      title: 'Review Underperformers',
      description: 'Analyze and decide on losing positions',
      component: ReviewLosersModal,
      requiresSelection: false
    },
    'bulk_edit': {
      title: 'Bulk Edit',
      description: 'Modify multiple positions at once',
      component: BulkEditModal,
      requiresSelection: true
    }
  };
  
  return (
    <div className="portfolio-management-workflow">
      {/* Portfolio Summary Header */}
      <div className="portfolio-header">
        <PortfolioSummaryCard portfolio={portfolio} />
        
        <div className="portfolio-actions">
          <ActionDropdown
            trigger="Quick Actions"
            actions={Object.entries(PORTFOLIO_ACTIONS).map(([key, action]) => ({
              id: key,
              title: action.title,
              description: action.description,
              disabled: action.requiresSelection && selectedPositions.length === 0,
              onClick: () => setSelectedAction(key)
            }))}
          />
          
          <Button variant="outline" onClick={() => generatePortfolioReport()}>
            Generate Report
          </Button>
        </div>
      </div>
      
      {/* Portfolio Positions Table */}
      <div className="portfolio-positions">
        <div className="positions-controls">
          <div className="selection-controls">
            <Checkbox
              checked={selectedPositions.length === portfolio.positions.length}
              indeterminate={selectedPositions.length > 0 && selectedPositions.length < portfolio.positions.length}
              onChange={(checked) => {
                if (checked) {
                  setSelectedPositions(portfolio.positions.map(p => p.symbol));
                } else {
                  setSelectedPositions([]);
                }
              }}
            />
            <span className="selection-text">
              {selectedPositions.length > 0 
                ? `${selectedPositions.length} selected`
                : 'Select all'
              }
            </span>
          </div>
          
          <div className="view-controls">
            <ViewToggle
              options={['table', 'cards', 'allocation']}
              value={portfolioView}
              onChange={setPortfolioView}
            />
            <SortSelector
              options={[
                { value: 'weight', label: 'Weight' },
                { value: 'performance', label: 'Performance' },
                { value: 'alphabetical', label: 'Alphabetical' }
              ]}
              value={sortBy}
              onChange={setSortBy}
            />
          </div>
        </div>
        
        <PortfolioPositionsTable
          positions={portfolio.positions}
          selectedPositions={selectedPositions}
          onPositionSelect={(symbol, selected) => {
            if (selected) {
              setSelectedPositions(prev => [...prev, symbol]);
            } else {
              setSelectedPositions(prev => prev.filter(s => s !== symbol));
            }
          }}
          onPositionClick={(symbol) => navigateToStockAnalysis(symbol)}
        />
      </div>
      
      {/* Smart Suggestions Panel */}
      <div className="smart-suggestions">
        <SmartSuggestionsPanel
          portfolio={portfolio}
          onAcceptSuggestion={(suggestion) => executeSuggestion(suggestion)}
          onDismissSuggestion={(suggestion) => dismissSuggestion(suggestion)}
        />
      </div>
      
      {/* Action Modals */}
      {selectedAction && (
        (() => {
          const ActionComponent = PORTFOLIO_ACTIONS[selectedAction].component;
          return (
            <ActionComponent
              portfolio={portfolio}
              selectedPositions={selectedPositions}
              onComplete={() => {
                setSelectedAction(null);
                setSelectedPositions([]);
                refreshPortfolio();
              }}
              onCancel={() => setSelectedAction(null)}
            />
          );
        })()
      )}
    </div>
  );
};
```

## 🎭 Interaction Patterns

### Smart Search Experience
```typescript
// SmartSearchInterface.tsx
const SmartSearchInterface: React.FC = () => {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState<'stocks' | 'ideas' | 'insights'>('stocks');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  
  const { suggestions, loading } = useSmartSuggestions(query, searchType);
  
  return (
    <div className="smart-search">
      {/* Search Input with Context */}
      <div className="search-input-container">
        <SearchInput
          value={query}
          onChange={setQuery}
          placeholder={`Search ${searchType}...`}
          leftIcon={<SearchIcon />}
          rightActions={
            <SearchTypeToggle
              value={searchType}
              options={[
                { value: 'stocks', label: '📈 Stocks', shortcut: 'S' },
                { value: 'ideas', label: '💡 Ideas', shortcut: 'I' },
                { value: 'insights', label: '🧠 Insights', shortcut: 'N' }
              ]}
              onChange={setSearchType}
            />
          }
        />
        
        {/* Search Shortcuts */}
        <div className="search-shortcuts">
          <ShortcutChip
            text="Recent earnings"
            onClick={() => setQuery('recent earnings')}
          />
          <ShortcutChip
            text="High dividend yield"
            onClick={() => setQuery('dividend yield > 4%')}
          />
          <ShortcutChip
            text="Insider buying"
            onClick={() => setQuery('insider buying last 30 days')}
          />
        </div>
      </div>
      
      {/* Search Results */}
      <div className="search-results">
        {loading ? (
          <SearchLoadingState />
        ) : (
          <>
            {/* Smart Suggestions */}
            {suggestions.length > 0 && (
              <div className="search-suggestions">
                <h4>Suggestions</h4>
                {suggestions.map(suggestion => (
                  <SuggestionItem
                    key={suggestion.id}
                    suggestion={suggestion}
                    onClick={() => applySuggestion(suggestion)}
                  />
                ))}
              </div>
            )}
            
            {/* Search Results */}
            <div className="results-list">
              {results.map(result => (
                <SearchResultItem
                  key={result.id}
                  result={result}
                  searchType={searchType}
                  query={query}
                  onClick={() => handleResultClick(result)}
                />
              ))}
            </div>
          </>
        )}
      </div>
      
      {/* Recent Searches */}
      {query === '' && recentSearches.length > 0 && (
        <div className="recent-searches">
          <h4>Recent Searches</h4>
          {recentSearches.map(search => (
            <RecentSearchItem
              key={search}
              search={search}
              onClick={() => setQuery(search)}
              onRemove={() => removeRecentSearch(search)}
            />
          ))}
        </div>
      )}
    </div>
  );
};
```

### Contextual Help System
```typescript
// ContextualHelpSystem.tsx
const ContextualHelpSystem: React.FC = () => {
  const [helpMode, setHelpMode] = useState(false);
  const [activeHelp, setActiveHelp] = useState<string | null>(null);
  const { currentPath, userLevel } = useUserContext();
  
  const getContextualHelp = (elementId: string) => {
    const helpContent = HELP_CONTENT[currentPath]?.[elementId];
    
    // Adapt help content based on user level
    if (helpContent && userLevel === 'beginner') {
      return {
        ...helpContent,
        explanation: helpContent.explanation_detailed || helpContent.explanation,
        showEducationalLinks: true
      };
    }
    
    return helpContent;
  };
  
  return (
    <div className={`contextual-help ${helpMode ? 'active' : ''}`}>
      {/* Help Toggle */}
      <div className="help-toggle">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setHelpMode(!helpMode)}
          className={helpMode ? 'active' : ''}
        >
          <HelpIcon />
          Help Mode
        </Button>
      </div>
      
      {/* Help Overlay */}
      {helpMode && (
        <div className="help-overlay">
          <HelpSpotlights
            elements={HELP_ELEMENTS[currentPath]}
            onElementClick={(elementId) => setActiveHelp(elementId)}
          />
        </div>
      )}
      
      {/* Help Tooltip */}
      {activeHelp && (
        <HelpTooltip
          content={getContextualHelp(activeHelp)}
          onClose={() => setActiveHelp(null)}
          onNext={() => {
            const nextElement = getNextHelpElement(activeHelp);
            setActiveHelp(nextElement);
          }}
        />
      )}
      
      {/* Help Chat Assistant */}
      <HelpChatAssistant
        isOpen={helpMode}
        context={currentPath}
        userLevel={userLevel}
      />
    </div>
  );
};
```

## 🎨 Micro-Interactions

```scss
// Micro-interaction styles
.micro-interactions {
  // Hover effects
  .hover-lift {
    transition: all 0.2s ease;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
  }
  
  // Button interactions
  .interactive-button {
    position: relative;
    overflow: hidden;
    
    &::before {
      content: '';
      position: absolute;
      top: 50%;
      left: 50%;
      width: 0;
      height: 0;
      background: rgba(255,255,255,0.3);
      border-radius: 50%;
      transform: translate(-50%, -50%);
      transition: width 0.6s, height 0.6s;
    }
    
    &:active::before {
      width: 300px;
      height: 300px;
    }
  }
  
  // Loading states
  .skeleton-loading {
    @keyframes skeleton-pulse {
      0% { opacity: 1; }
      50% { opacity: 0.4; }
      100% { opacity: 1; }
    }
    
    animation: skeleton-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
  }
  
  // Success feedback
  .success-pulse {
    @keyframes success-pulse {
      0% { transform: scale(1); }
      50% { transform: scale(1.05); }
      100% { transform: scale(1); }
    }
    
    animation: success-pulse 0.6s ease-in-out;
  }
}
```

## 📊 UX Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Task completion rate | >90% | - |
| Time to complete common tasks | <30 seconds | - |
| User satisfaction score | >8.5/10 | - |
| Help system usage | <10% of sessions | - |
| Error recovery rate | >95% | - |

---

**Next**: Continue with mobile interface design.