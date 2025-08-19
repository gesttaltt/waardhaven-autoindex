# 🌍 Global Government Spending & Political Trading Tracker

**Priority**: CRITICAL  
**Complexity**: High  
**Timeline**: 5-7 days  
**Value**: Track government spending and political trading across all major economies

## 🎯 Objective

Monitor government spending, contracts, and political trading globally:
- 🇺🇸 USA - Congress, Federal contracts
- 🇪🇺 European Union - MEPs, EU tenders
- 🇬🇧 United Kingdom - MPs, UK contracts
- 🇨🇳 China - State investments, SOE activities
- 🇯🇵 Japan - Diet members, government projects
- 🇮🇳 India - Parliament, government tenders
- 🇩🇪 Germany - Bundestag, federal contracts
- 🇫🇷 France - National Assembly, public contracts
- 🇨🇦 Canada - Parliament, Crown corporations
- 🇦🇺 Australia - Parliament, government contracts
- 🇰🇷 South Korea - National Assembly, chaebols
- 🇧🇷 Brazil - Congress, state enterprises

## 📊 Global Data Sources

### United States 🇺🇸
```python
USA_SOURCES = {
    'contracts': 'https://api.usaspending.gov',
    'congress_trading': 'QuiverQuant API',
    'lobbying': 'https://www.opensecrets.org/api',
    'federal_reserve': 'https://fred.stlouisfed.org/api'
}
```

### European Union 🇪🇺
```python
EU_SOURCES = {
    'tenders': 'https://ted.europa.eu/api',  # Tenders Electronic Daily
    'mep_declarations': 'https://www.europarl.europa.eu',
    'eu_budget': 'https://ec.europa.eu/budget/api',
    'ecb_data': 'https://sdw-wsrest.ecb.europa.eu'
}
```

### United Kingdom 🇬🇧
```python
UK_SOURCES = {
    'contracts': 'https://www.contractsfinder.service.gov.uk/api',
    'mp_register': 'https://www.parliament.uk/mps-lords-and-offices',
    'companies_house': 'https://api.companieshouse.gov.uk',
    'uk_statistics': 'https://api.ons.gov.uk'
}
```

### China 🇨🇳
```python
CHINA_SOURCES = {
    'state_investments': 'http://www.stats.gov.cn',  # National Bureau of Statistics
    'soe_activities': 'SASAC announcements',
    'belt_road': 'BRI project databases',
    'alibaba_gov_contracts': 'Alibaba Cloud Government',
    'five_year_plans': 'NDRC announcements'
}
```

### Japan 🇯🇵
```python
JAPAN_SOURCES = {
    'public_works': 'https://www.e-gov.go.jp',
    'diet_disclosures': 'National Diet Library',
    'mof_data': 'Ministry of Finance',
    'infrastructure': 'MLIT database'
}
```

### Other Major Economies
```python
GLOBAL_SOURCES = {
    'india': {
        'gem_portal': 'https://gem.gov.in',  # Government e-Marketplace
        'cppp': 'https://eprocure.gov.in',  # Central Public Procurement Portal
        'parliament': 'Lok Sabha/Rajya Sabha disclosures'
    },
    'germany': {
        'ted_germany': 'TED Europa filtered',
        'bundestag': 'Bundestag financial disclosures',
        'federal_tenders': 'www.service.bund.de'
    },
    'france': {
        'boamp': 'https://www.boamp.fr',  # Public contracts bulletin
        'assembly': 'Assemblée Nationale declarations',
        'marches_publics': 'www.marches-publics.gouv.fr'
    },
    'canada': {
        'buyandsell': 'https://buyandsell.gc.ca',
        'parliament': 'House of Commons disclosures',
        'crown_corps': 'Crown corporation reports'
    },
    'australia': {
        'austender': 'https://www.tenders.gov.au',
        'parliament': 'Parliamentary disclosure',
        'states': 'State government tenders'
    },
    'south_korea': {
        'g2b': 'Korea ON-line E-Procurement System',
        'assembly': 'National Assembly disclosures',
        'chaebol_gov': 'Chaebol-government contracts'
    }
}
```

## 💾 Global Database Schema

```sql
-- Global government contracts
CREATE TABLE global_gov_contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Location
    country_code VARCHAR(2) NOT NULL,
    country_name VARCHAR(100) NOT NULL,
    region VARCHAR(50), -- EU, APAC, Americas, etc.
    currency VARCHAR(3),
    
    -- Contract details
    contract_id VARCHAR(255),
    local_contract_id VARCHAR(255), -- Original ID in country system
    
    -- Parties
    agency_name VARCHAR(255),
    agency_name_local TEXT, -- In local language
    recipient_name VARCHAR(255),
    recipient_name_local TEXT,
    
    -- Financial
    award_amount_local DECIMAL(20,2),
    award_amount_usd DECIMAL(20,2), -- Converted to USD
    
    -- Dates
    award_date DATE,
    start_date DATE,
    end_date DATE,
    
    -- Classification
    sector VARCHAR(100),
    industry_code VARCHAR(50),
    description TEXT,
    description_translated TEXT, -- English translation
    
    -- Stock mapping
    local_ticker VARCHAR(20),
    us_ticker VARCHAR(20), -- ADR if available
    intl_ticker VARCHAR(50), -- Format: TICKER.EXCHANGE
    
    -- Analysis
    impact_score DECIMAL(3,2),
    is_strategic BOOLEAN, -- Part of strategic initiative
    
    -- Source
    source VARCHAR(100),
    source_url TEXT,
    raw_data JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Global political trading
CREATE TABLE global_political_trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Trader location
    country_code VARCHAR(2) NOT NULL,
    country_name VARCHAR(100),
    
    -- Trader info
    trader_name VARCHAR(255),
    trader_name_local TEXT,
    position VARCHAR(255), -- Senator, MP, MEP, etc.
    party VARCHAR(100),
    
    -- Trade details
    symbol VARCHAR(50), -- Can include exchange suffix
    local_symbol VARCHAR(50),
    us_symbol VARCHAR(20), -- If US-listed
    
    transaction_type VARCHAR(20),
    shares INTEGER,
    value_local DECIMAL(15,2),
    value_usd DECIMAL(15,2),
    
    -- Dates
    transaction_date DATE,
    disclosure_date DATE,
    
    -- Analysis
    days_before_policy DATE, -- Days before relevant policy
    is_suspicious BOOLEAN,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Country-specific economic indicators
CREATE TABLE global_economic_indicators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    country_code VARCHAR(2),
    indicator_type VARCHAR(100), -- GDP, inflation, unemployment, etc.
    value DECIMAL(20,4),
    period DATE,
    
    -- Impact on markets
    market_impact VARCHAR(50), -- positive, negative, neutral
    affected_sectors TEXT[],
    
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🌐 Multi-Language Processing

```python
class GlobalDataProcessor:
    """Process government data from multiple countries and languages"""
    
    def __init__(self):
        self.translators = {
            'zh': ChineseTranslator(),
            'ja': JapaneseTranslator(),
            'ko': KoreanTranslator(),
            'de': GermanTranslator(),
            'fr': FrenchTranslator(),
            'pt': PortugueseTranslator(),
            'hi': HindiTranslator()
        }
        
        self.currency_converter = CurrencyConverter()
        
    async def process_contract(self, contract: Dict, country_code: str) -> Dict:
        """Process contract from any country"""
        
        # Detect language
        language = self.detect_language(contract)
        
        # Translate if needed
        if language != 'en':
            contract = await self.translate_contract(contract, language)
        
        # Convert currency to USD
        contract['amount_usd'] = await self.convert_to_usd(
            contract['amount'],
            contract['currency'],
            contract['date']
        )
        
        # Map to global tickers
        contract['global_tickers'] = await self.map_to_global_tickers(
            contract['recipient'],
            country_code
        )
        
        # Assess global impact
        contract['global_impact'] = self.assess_global_impact(contract)
        
        return contract
    
    def map_to_global_tickers(self, company: str, country: str) -> Dict:
        """Map local company to all relevant tickers"""
        
        tickers = {
            'local': self.get_local_ticker(company, country),
            'us_adr': self.get_adr_ticker(company),
            'european': self.get_european_listing(company),
            'asian': self.get_asian_listings(company)
        }
        
        return tickers
```

## 🏛️ Country-Specific Collectors

### China Collector 🇨🇳
```python
class ChinaGovCollector:
    """Collect Chinese government investments and SOE activities"""
    
    async def collect_state_investments(self):
        """Track state-owned enterprise investments"""
        
        soe_companies = [
            'Sinopec', 'PetroChina', 'China Mobile',
            'ICBC', 'China Construction Bank', 'SAIC Motor'
        ]
        
        investments = []
        for company in soe_companies:
            # Check for new government directives
            directives = await self.get_gov_directives(company)
            
            # Check for Belt and Road projects
            bri_projects = await self.get_bri_projects(company)
            
            # Check for domestic infrastructure
            infrastructure = await self.get_infrastructure_projects(company)
            
            investments.extend(directives + bri_projects + infrastructure)
            
        return investments
    
    async def track_five_year_plan(self):
        """Track allocations from Five Year Plan"""
        
        plan_priorities = {
            'semiconductors': ['SMIC', 'Hua Hong', 'JCET'],
            'renewable_energy': ['LONGi', 'JinkoSolar', 'BYD'],
            'ai_technology': ['Baidu', 'Alibaba', 'Tencent', 'SenseTime'],
            'biotech': ['WuXi AppTec', 'BeiGene', 'GenScript']
        }
        
        allocations = []
        for sector, companies in plan_priorities.items():
            sector_allocation = await self.get_sector_allocation(sector)
            allocations.append({
                'sector': sector,
                'amount_rmb': sector_allocation,
                'benefiting_companies': companies
            })
            
        return allocations
```

### European Union Collector 🇪🇺
```python
class EUGovCollector:
    """Collect EU tenders and MEP disclosures"""
    
    async def collect_eu_tenders(self):
        """Fetch from TED (Tenders Electronic Daily)"""
        
        # EU Green Deal projects
        green_deal = await self.get_green_deal_contracts()
        
        # Digital Europe Programme
        digital = await self.get_digital_contracts()
        
        # Horizon Europe (research)
        research = await self.get_horizon_contracts()
        
        # Defense contracts
        defense = await self.get_eu_defense_contracts()
        
        return green_deal + digital + research + defense
    
    async def track_mep_trading(self):
        """Track Member of European Parliament financial disclosures"""
        
        # Note: Limited disclosure requirements
        # Focus on voting patterns related to industries
        
        voting_patterns = await self.analyze_mep_voting()
        
        return voting_patterns
```

### India Collector 🇮🇳
```python
class IndiaGovCollector:
    """Collect Indian government tenders and investments"""
    
    async def collect_gem_tenders(self):
        """Government e-Marketplace tenders"""
        
        sectors = {
            'infrastructure': ['L&T', 'Adani Ports', 'GMR'],
            'defense': ['HAL', 'BEL', 'BDL'],
            'technology': ['TCS', 'Infosys', 'Wipro'],
            'pharma': ['Sun Pharma', 'Dr. Reddy', 'Cipla']
        }
        
        tenders = []
        for sector, companies in sectors.items():
            sector_tenders = await self.fetch_sector_tenders(sector)
            mapped = self.map_to_companies(sector_tenders, companies)
            tenders.extend(mapped)
            
        return tenders
    
    async def track_pli_schemes(self):
        """Production Linked Incentive schemes"""
        
        pli_sectors = [
            'electronics', 'pharma', 'automobiles',
            'textiles', 'solar', 'batteries'
        ]
        
        beneficiaries = {}
        for sector in pli_sectors:
            companies = await self.get_pli_beneficiaries(sector)
            beneficiaries[sector] = companies
            
        return beneficiaries
```

## 🌏 Regional Analysis

```python
class RegionalAnalyzer:
    """Analyze government spending by region"""
    
    def analyze_global_trends(self) -> Dict:
        """Identify global government spending trends"""
        
        trends = {
            'green_energy': self.analyze_green_spending(),
            'defense': self.analyze_defense_spending(),
            'infrastructure': self.analyze_infrastructure(),
            'technology': self.analyze_tech_spending(),
            'healthcare': self.analyze_healthcare_spending()
        }
        
        return trends
    
    def analyze_green_spending(self) -> Dict:
        """Global green energy initiatives"""
        
        return {
            'usa': {
                'amount': 369_000_000_000,  # Inflation Reduction Act
                'beneficiaries': ['TSLA', 'ENPH', 'SEDG']
            },
            'eu': {
                'amount': 1_000_000_000_000,  # Green Deal
                'beneficiaries': ['ORSTED', 'VESTAS', 'SIEMENS']
            },
            'china': {
                'amount': 500_000_000_000,  # Estimated
                'beneficiaries': ['LONGi', 'BYD', 'CATL']
            },
            'india': {
                'amount': 100_000_000_000,
                'beneficiaries': ['Adani Green', 'Tata Power']
            }
        }
```

## 🚨 Global Alert System

```python
GLOBAL_ALERTS = {
    'cross_border_pattern': {
        'description': 'Multiple countries investing in same sector',
        'example': 'US, EU, China all increasing semiconductor spending',
        'impact': 'Major opportunity in semiconductor stocks globally'
    },
    'trade_war_indicator': {
        'description': 'Protectionist policies detected',
        'example': 'Tariffs, domestic preference in contracts',
        'impact': 'Shift from global to local suppliers'
    },
    'coordinated_stimulus': {
        'description': 'Multiple central banks acting together',
        'example': 'Fed, ECB, BoJ all easing',
        'impact': 'Risk-on environment, growth stocks benefit'
    }
}
```

## 🎨 Global Dashboard UI

```typescript
// GlobalGovernmentDashboard.tsx

const GlobalGovernmentDashboard = () => {
  const [selectedCountries, setSelectedCountries] = useState(['US', 'EU', 'CN']);
  const [sector, setSector] = useState('all');
  
  return (
    <div className="global-dashboard">
      {/* World Map Heat Map */}
      <WorldMap 
        data={governmentSpendingByCountry}
        colorScale="spending"
      />
      
      {/* Country Comparison */}
      <CountryComparison countries={selectedCountries}>
        <SpendingByCountry />
        <TopContractsByCountry />
        <PoliticalTradingActivity />
      </CountryComparison>
      
      {/* Global Trends */}
      <GlobalTrends>
        <TrendCard title="Green Energy" trend={greenEnergyTrend} />
        <TrendCard title="Defense" trend={defenseTrend} />
        <TrendCard title="Technology" trend={techTrend} />
      </GlobalTrends>
      
      {/* Stock Opportunities */}
      <GlobalStockOpportunities>
        <StockList 
          title="Benefiting from Multiple Governments"
          stocks={multiGovBeneficiaries}
        />
      </GlobalStockOpportunities>
    </div>
  );
};
```

## 📊 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Countries tracked | 15+ | 0 |
| Daily contracts collected | 500+ | 0 |
| Political trades tracked | 100+ | 0 |
| Translation accuracy | 95% | - |
| Currency conversion accuracy | 99.9% | - |

---

**Note**: This comprehensive global tracking system will give us unique insights into worldwide government spending patterns and political trading, helping identify stocks that benefit from government actions globally.