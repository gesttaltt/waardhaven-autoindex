# RIVL — Real-time Information Velocity & Latent Consensus
## 14-Day Implementation Roadmap

### Vision
**"We don't tell you what to buy; we show why consensus will change and link the proof."**

RIVL is a belief-revision intelligence system for mid/long-term investors, focused on detecting when market consensus is about to shift by analyzing information velocity, filing changes, and earnings credibility signals.

### Core Value Proposition
- **Belief-revision focus**: Track when and why consensus shifts, not just price movements
- **Linked evidence**: Every signal comes with document-level attribution and proof
- **Language arbitrage**: LatAm coverage with ES/PT→EN translation advantage
- **Small/mid-cap coverage**: Focus on underserved market segments

## 14-Day Sprint Plan

### Days 1-3: Foundation & Ingestion Pipeline
**Goal**: Establish multi-source data ingestion with entity resolution

#### Day 1: Core Infrastructure
- Set up event bus architecture for real-time data flow
- Implement columnar storage for time-series data
- Configure TwelveData integration (OHLCV + fundamentals)
- Design entity resolution schema

#### Day 2: SEC EDGAR Integration
- Implement EDGAR API client for 10-K/Q retrieval
- XBRL parser for structured financial data extraction
- Set up filing storage and versioning system
- Create filing diff detection mechanism

#### Day 3: Additional Data Sources
- FRED integration for macroeconomic indicators
- News feed ingestion framework (GDELT/provider-agnostic)
- Earnings transcript retrieval system
- Entity linker with OpenFIGI/LEI implementation

**Deliverables**:
- Working ingestion pipeline with 4+ data sources
- Entity resolution system v0
- Data storage layer with proper indexing

### Days 4-7: Core Signal Generation
**Goal**: Implement primary belief-revision signals

#### Day 4: Δ-Filings Redline System
- Semantic diff algorithm for Risk Factors and MD&A sections
- Token-level change detection with materiality weighting
- Historical filing comparison engine
- Change scoring: `score = Σ(token_change × materiality_weight)`

#### Day 5: Novelty & Velocity (N&V) Signal
- Deduplication algorithm for news across sources
- "New information per minute" calculator
- Cross-source propagation tracker
- Language detection and translation pipeline
- Velocity scoring: `velocity = propagation_speed × source_credibility`

#### Day 6: Earnings Truth Meter v0
- Transcript text extraction and preprocessing
- Audio prosody analysis (tempo, pauses, intensity)
- Contradiction detection between statements
- Credibility scoring: `credibility = 1 - (prosody_anomaly + text_contradiction)`

#### Day 7: Consensus-Gap Calculator
- Expected impact model from N&V and Δ-Filings
- Actual price/volume reaction measurement
- Gap calculation: `gap = |actual_reaction - expected_impact|`
- Integration with other signals

**Deliverables**:
- 4 working signals with mathematical scoring
- Signal storage and retrieval API
- Basic signal dashboard

### Days 8-10: Intelligence Layer & Backtesting
**Goal**: Build predictive models and validate with historical data

#### Day 8: Regime Detection System
- Implement BOCPD (Bayesian Online Changepoint Detection)
- Bayesian nowcasting for 30-90 day horizons
- Regime probability calculator
- Market condition classifier (risk-on/risk-off)

#### Day 9: Surprise Index Implementation
- KL divergence calculator: `SI = KL(p_prior || p_post)`
- Feature weight learning system
- Prior/posterior update mechanism
- Document-level attribution storage

#### Day 10: 24-Month Sector Backtest
- Historical signal generation for 2 years
- Performance metrics by Surprise Index quintile
- Information Ratio and Sortino calculation
- Drawdown analysis and hit-rate measurement

**Deliverables**:
- Complete intelligence layer with 2 models
- Backtest results with performance metrics
- 3 detailed case studies with evidence packs

### Days 11-14: Productization & Documentation
**Goal**: Create investor-ready system with complete documentation

#### Day 11: Evidence Pack System
- JSON schema implementation for evidence packs
- Automated pack generation for each signal
- Attribution linker for source documents
- Example pack for AAPL with full data

#### Day 12: API & Dashboard Development
- Read-only REST API for all signals
- Three core views implementation:
  - Regime Dial (market conditions)
  - Filings-Δ Heatmap (change visualization)
  - 1-Click Ticker Explainer (evidence summary)
- Rate limiting and error handling

#### Day 13: Compliance & Metrics Framework
- Source licensing documentation
- Data retention policies
- PII handling procedures
- SLA targets (p95 < 500ms ingestion)
- Coverage metrics tracking

#### Day 14: Investor Package
- 6-slide pitch deck draft
- Performance metrics summary
- Differentiator documentation
- Pricing model (base + success kicker)
- "No evidence, no signal" guarantee

**Final Deliverables**:
- Production-ready RIVL system
- Complete API documentation
- Investor pitch materials
- Compliance framework
- Evidence pack examples

## Success Metrics

### Technical KPIs
- **Ingestion latency**: p95 < 500ms
- **Signal coverage**: >80% of S&P 500 + Russell 2000
- **Evidence completeness**: 100% signals with attribution
- **System uptime**: 99.9% availability

### Investment Performance
- **Information Ratio**: >1.5 for top quintile
- **Sortino Ratio**: >2.0 for systematic strategy
- **Hit-rate**: >65% for regime change predictions
- **Max drawdown**: <15% during backtest period

### Business Metrics
- **Time to first signal**: <3 minutes from news
- **Language coverage**: EN, ES, PT at launch
- **Small-cap coverage**: >500 tickers < $2B market cap
- **Evidence pack generation**: <1 second per ticker

## Risk Mitigation

### Data Quality
- Multiple source validation for critical signals
- Automated anomaly detection in ingested data
- Manual review queue for high-impact changes

### Model Risk
- Out-of-sample validation mandatory
- Walk-forward analysis for all strategies
- Human-in-the-loop for extreme predictions

### Operational Risk
- Redundant data sources where possible
- Graceful degradation for missing data
- Circuit breakers for anomalous trading signals

## Next Steps After Day 14

### Month 2 Priorities
- Expand to cryptocurrency markets
- Add options flow analysis
- Implement regulatory filing alerts
- Build mobile application

### Quarter 2 Goals
- Launch paid tier with institutional features
- Add custom signal builder interface
- Implement backtesting-as-a-service
- Expand to Asian markets

### Year 1 Vision
- Full global equity coverage
- Real-time streaming architecture
- AI-powered research assistant
- White-label platform offering

## TODO Items

- `TODO(data-team, 2025-01-20)`: Finalize GDELT integration specs
- `TODO(ml-team, 2025-01-22)`: Select specific prosody analysis library
- `TODO(product, 2025-01-25)`: Define exact success kicker formula
- `TODO(compliance, 2025-01-27)`: Review EDGAR usage limits
- `TODO(eng-lead, 2025-01-30)`: Architecture review and sign-off