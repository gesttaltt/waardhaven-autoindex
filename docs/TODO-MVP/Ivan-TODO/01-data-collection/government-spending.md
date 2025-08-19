# 🏛️ Government Spending & Contract Tracking

**Priority**: HIGH  
**Complexity**: Medium  
**Timeline**: 2-3 days  
**Value**: Identify stocks that benefit from government contracts and spending

## 🎯 Objective

Track government spending patterns to predict which companies will benefit from:
- Defense contracts
- Infrastructure spending
- Healthcare initiatives
- Green energy subsidies
- Technology contracts
- Research grants

## 📊 Primary Data Sources

### 1. USASpending.gov API (Free)
```python
USA_SPENDING_API = {
    'base_url': 'https://api.usaspending.gov/api/v2/',
    'endpoints': {
        'awards': 'awards/',
        'search': 'search/spending_by_award/',
        'recipients': 'recipient/duns/',
        'agencies': 'references/agency/',
        'contracts': 'search/awards/'
    }
}

# Example: Get recent defense contracts
{
    "filters": {
        "agencies": [{"name": "Department of Defense"}],
        "award_amounts": [{"lower_bound": 1000000}],
        "time_period": [{"start_date": "2024-01-01"}]
    }
}
```

### 2. Federal Procurement Data System (FPDS)
```python
FPDS_DATA = {
    'url': 'https://www.fpds.gov/fpdsng_cms/index.php/en/',
    'data_types': [
        'contracts',
        'modifications',
        'obligations',
        'vendors'
    ]
}
```

### 3. SAM.gov (System for Award Management)
```python
SAM_GOV_API = {
    'entity_management': '/entity-information/v2/',
    'contract_opportunities': '/opportunities/v2/',
    'wage_determinations': '/wage-determination/v1/'
}
```

### 4. Congressional Budget Data
```python
BUDGET_SOURCES = {
    'cbo': 'https://www.cbo.gov/data/budget-economic-data',
    'treasury': 'https://api.fiscaldata.treasury.gov/',
    'omb': 'https://www.whitehouse.gov/omb/budget/'
}
```

## 💾 Database Schema

```sql
-- Government contracts table
CREATE TABLE government_contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Contract details
    contract_id VARCHAR(255) UNIQUE NOT NULL,
    award_type VARCHAR(50), -- 'contract', 'grant', 'loan'
    
    -- Parties
    agency_name VARCHAR(255) NOT NULL,
    agency_code VARCHAR(50),
    recipient_name VARCHAR(255) NOT NULL,
    recipient_duns VARCHAR(20),
    parent_company VARCHAR(255),
    
    -- Financial
    award_amount DECIMAL(15,2),
    total_obligation DECIMAL(15,2),
    
    -- Dates
    award_date DATE NOT NULL,
    start_date DATE,
    end_date DATE,
    
    -- Classification
    product_service_code VARCHAR(50),
    naics_code VARCHAR(10),
    description TEXT,
    
    -- Stock mapping
    ticker_symbol VARCHAR(20),
    parent_ticker VARCHAR(20),
    confidence_score DECIMAL(3,2), -- How confident in stock mapping
    
    -- Analysis
    sector VARCHAR(100),
    is_competitive BOOLEAN,
    number_of_offers INTEGER,
    
    -- Source
    source_url TEXT,
    raw_data JSONB,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_gov_contracts_ticker ON government_contracts(ticker_symbol);
CREATE INDEX idx_gov_contracts_agency ON government_contracts(agency_name);
CREATE INDEX idx_gov_contracts_date ON government_contracts(award_date DESC);
CREATE INDEX idx_gov_contracts_amount ON government_contracts(award_amount DESC);

-- Company to ticker mapping
CREATE TABLE company_ticker_mapping (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL,
    duns_number VARCHAR(20),
    ticker_symbol VARCHAR(20),
    parent_ticker VARCHAR(20),
    is_subsidiary BOOLEAN DEFAULT FALSE,
    confidence DECIMAL(3,2),
    
    UNIQUE(company_name, ticker_symbol)
);

-- Sector spending trends
CREATE TABLE gov_spending_trends (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sector VARCHAR(100) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    total_spending DECIMAL(15,2),
    contract_count INTEGER,
    avg_contract_size DECIMAL(15,2),
    
    top_recipients JSONB, -- Array of {company, amount, ticker}
    growth_rate DECIMAL(8,4), -- vs previous period
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(sector, period_start, period_end)
);
```

## 🔄 Collection & Analysis Pipeline

```python
# app/services/gov_spending_collector.py

import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List

class GovernmentSpendingCollector:
    def __init__(self):
        self.base_url = "https://api.usaspending.gov/api/v2"
        self.sectors = {
            'defense': ['DOD', 'DOS', 'DHS'],
            'healthcare': ['HHS', 'VA'],
            'infrastructure': ['DOT', 'DOE'],
            'technology': ['NASA', 'NSF', 'DOC']
        }
        
    async def collect_recent_contracts(self, days_back: int = 7):
        """Fetch recent contract awards"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        contracts = []
        for sector, agencies in self.sectors.items():
            sector_contracts = await self.fetch_sector_contracts(
                sector, agencies, start_date, end_date
            )
            contracts.extend(sector_contracts)
            
        # Map to stock tickers
        enriched = await self.enrich_with_tickers(contracts)
        
        # Analyze impact
        analyzed = self.analyze_contract_impact(enriched)
        
        return analyzed
    
    async def fetch_sector_contracts(self, sector, agencies, start_date, end_date):
        """Fetch contracts for specific sector"""
        
        payload = {
            "filters": {
                "agencies": [{"type": "awarding", "tier": "toptier", "name": a} for a in agencies],
                "time_period": [{
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d")
                }],
                "award_amounts": [{"lower_bound": 1000000}]  # Only $1M+
            },
            "limit": 100,
            "page": 1
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/search/spending_by_award/",
                json=payload
            ) as response:
                data = await response.json()
                
        return self.process_contracts(data['results'], sector)
    
    def map_company_to_ticker(self, company_name: str) -> Dict:
        """Map company name to stock ticker"""
        
        # Use fuzzy matching and lookup tables
        mappings = {
            'Lockheed Martin': 'LMT',
            'Boeing': 'BA',
            'Raytheon': 'RTX',
            'Northrop Grumman': 'NOC',
            'General Dynamics': 'GD',
            'L3Harris': 'LHX',
            'Microsoft': 'MSFT',
            'Amazon Web Services': 'AMZN',
            'Palantir': 'PLTR',
            'CACI': 'CACI',
            'SAIC': 'SAIC',
            'Booz Allen': 'BAH'
        }
        
        # Fuzzy match logic here
        for known_company, ticker in mappings.items():
            if known_company.lower() in company_name.lower():
                return {
                    'ticker': ticker,
                    'confidence': 0.9,
                    'method': 'exact_match'
                }
        
        # Try subsidiary mapping
        subsidiary = self.check_subsidiary(company_name)
        if subsidiary:
            return subsidiary
            
        return {'ticker': None, 'confidence': 0, 'method': 'not_found'}
    
    def analyze_contract_impact(self, contracts: List[Dict]) -> List[Dict]:
        """Analyze potential impact on stock"""
        
        for contract in contracts:
            if contract.get('ticker'):
                # Get company market cap
                market_cap = self.get_market_cap(contract['ticker'])
                
                # Calculate materiality
                if market_cap:
                    contract['materiality'] = contract['award_amount'] / market_cap
                    contract['impact_score'] = self.calculate_impact_score(contract)
                    
        return contracts
    
    def calculate_impact_score(self, contract: Dict) -> float:
        """Calculate how impactful this contract is for the stock"""
        
        score = 0.0
        
        # Size factor (larger = more impact)
        if contract['award_amount'] > 1_000_000_000:  # $1B+
            score += 0.3
        elif contract['award_amount'] > 100_000_000:  # $100M+
            score += 0.2
        else:
            score += 0.1
            
        # Materiality factor
        if contract.get('materiality', 0) > 0.05:  # >5% of market cap
            score += 0.3
        elif contract.get('materiality', 0) > 0.01:  # >1%
            score += 0.2
        else:
            score += 0.1
            
        # Duration factor (longer = more stable revenue)
        duration_years = (contract.get('end_date', contract['start_date']) - contract['start_date']).days / 365
        if duration_years > 5:
            score += 0.2
        elif duration_years > 2:
            score += 0.1
            
        # Competition factor
        if not contract.get('is_competitive', True):
            score += 0.1  # Sole source is better
            
        return min(score, 1.0)  # Cap at 1.0
```

## 📈 Sector Analysis

```python
class SectorAnalyzer:
    """Analyze government spending by sector"""
    
    def __init__(self):
        self.sectors = {
            'defense': {
                'agencies': ['DOD', 'DOS'],
                'keywords': ['defense', 'military', 'weapon', 'aircraft'],
                'stocks': ['LMT', 'BA', 'RTX', 'NOC', 'GD', 'LHX']
            },
            'healthcare': {
                'agencies': ['HHS', 'VA', 'CDC'],
                'keywords': ['medical', 'health', 'pharma', 'vaccine'],
                'stocks': ['JNJ', 'PFE', 'UNH', 'CVS', 'MCK']
            },
            'infrastructure': {
                'agencies': ['DOT', 'DOE'],
                'keywords': ['construction', 'highway', 'bridge', 'energy'],
                'stocks': ['CAT', 'DE', 'VMC', 'MLM', 'PAVE']
            },
            'technology': {
                'agencies': ['NASA', 'NSF', 'DOC'],
                'keywords': ['software', 'cloud', 'cyber', 'AI'],
                'stocks': ['MSFT', 'AMZN', 'GOOGL', 'PLTR', 'SNOW']
            },
            'green_energy': {
                'agencies': ['DOE', 'EPA'],
                'keywords': ['solar', 'wind', 'renewable', 'battery'],
                'stocks': ['TSLA', 'ENPH', 'SEDG', 'RUN', 'PLUG']
            }
        }
    
    async def analyze_sector_trends(self, sector: str, days: int = 90):
        """Analyze spending trends for a sector"""
        
        contracts = await self.get_sector_contracts(sector, days)
        
        analysis = {
            'sector': sector,
            'period': days,
            'total_spending': sum(c['award_amount'] for c in contracts),
            'contract_count': len(contracts),
            'avg_size': self.calculate_average(contracts),
            'top_recipients': self.get_top_recipients(contracts),
            'growth_rate': self.calculate_growth_rate(sector, contracts),
            'benefiting_stocks': self.identify_beneficiaries(contracts),
            'momentum': self.calculate_momentum(contracts)
        }
        
        return analysis
    
    def identify_beneficiaries(self, contracts: List[Dict]) -> List[Dict]:
        """Identify stocks that benefit from contracts"""
        
        beneficiaries = {}
        
        for contract in contracts:
            ticker = contract.get('ticker')
            if ticker:
                if ticker not in beneficiaries:
                    beneficiaries[ticker] = {
                        'symbol': ticker,
                        'total_value': 0,
                        'contract_count': 0,
                        'contracts': []
                    }
                
                beneficiaries[ticker]['total_value'] += contract['award_amount']
                beneficiaries[ticker]['contract_count'] += 1
                beneficiaries[ticker]['contracts'].append({
                    'id': contract['contract_id'],
                    'amount': contract['award_amount'],
                    'agency': contract['agency_name']
                })
        
        # Sort by total value
        sorted_stocks = sorted(
            beneficiaries.values(),
            key=lambda x: x['total_value'],
            reverse=True
        )
        
        return sorted_stocks[:10]  # Top 10
```

## 🚨 Alert System

```python
GOV_SPENDING_ALERTS = {
    'mega_contract': {
        'trigger': 'contract_value > 1_billion',
        'severity': 'high',
        'notification': 'immediate'
    },
    'sector_surge': {
        'trigger': 'sector_spending_increase > 50%',
        'severity': 'medium',
        'notification': 'daily'
    },
    'new_contractor': {
        'trigger': 'first_time_contractor',
        'severity': 'low',
        'notification': 'weekly'
    },
    'competitive_win': {
        'trigger': 'won_competitive_bid',
        'severity': 'medium',
        'notification': 'daily'
    }
}

async def check_spending_alerts(contract: Dict):
    """Check if contract triggers any alerts"""
    
    alerts = []
    
    # Mega contract
    if contract['award_amount'] > 1_000_000_000:
        alerts.append({
            'type': 'mega_contract',
            'message': f"${contract['award_amount']:,.0f} awarded to {contract['recipient_name']}",
            'ticker': contract.get('ticker'),
            'severity': 'high'
        })
    
    # New contractor
    if is_first_time_contractor(contract['recipient_name']):
        alerts.append({
            'type': 'new_contractor',
            'message': f"New contractor: {contract['recipient_name']}",
            'ticker': contract.get('ticker'),
            'severity': 'low'
        })
    
    return alerts
```

## 📊 Budget Bill Analysis

```python
class BudgetBillAnalyzer:
    """Analyze congressional budget bills for sector impacts"""
    
    def analyze_bill(self, bill_text: str) -> Dict:
        """Parse bill for spending allocations"""
        
        allocations = self.extract_allocations(bill_text)
        
        sector_impacts = {}
        for allocation in allocations:
            sector = self.categorize_allocation(allocation)
            if sector not in sector_impacts:
                sector_impacts[sector] = {
                    'amount': 0,
                    'programs': [],
                    'benefiting_stocks': []
                }
            
            sector_impacts[sector]['amount'] += allocation['amount']
            sector_impacts[sector]['programs'].append(allocation['program'])
            
        # Map to stocks
        for sector in sector_impacts:
            stocks = self.get_sector_stocks(sector)
            sector_impacts[sector]['benefiting_stocks'] = stocks
            
        return sector_impacts
```

## 🎨 UI Components

```typescript
// GovernmentSpendingDashboard.tsx

interface ContractAlert {
  id: string;
  type: 'mega_contract' | 'sector_surge' | 'new_contractor';
  ticker?: string;
  amount: number;
  agency: string;
  recipient: string;
  impact_score: number;
}

const GovernmentSpendingDashboard = () => {
  const [sector, setSector] = useState('defense');
  const [timeframe, setTimeframe] = useState(30);
  
  return (
    <div className="grid grid-cols-12 gap-4">
      {/* Sector Overview */}
      <Card className="col-span-8">
        <CardHeader>
          <Title>Government Contract Awards</Title>
          <SectorSelector value={sector} onChange={setSector} />
        </CardHeader>
        <CardBody>
          <SpendingChart data={sectorData} />
          <TopContractors contractors={topContractors} />
        </CardBody>
      </Card>
      
      {/* Benefiting Stocks */}
      <Card className="col-span-4">
        <CardHeader>
          <Title>📈 Stocks to Watch</Title>
        </CardHeader>
        <CardBody>
          <StockList stocks={benefitingStocks} />
        </CardBody>
      </Card>
      
      {/* Recent Alerts */}
      <Card className="col-span-12">
        <AlertsFeed alerts={recentAlerts} />
      </Card>
    </div>
  );
};
```

## 📊 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Contracts tracked daily | 50+ | 0 |
| Ticker mapping accuracy | 90% | - |
| Alert relevance | 85% | - |
| Sector analysis accuracy | 80% | - |

---

**Next**: Implement [news-sentiment.md](news-sentiment.md) for news aggregation.