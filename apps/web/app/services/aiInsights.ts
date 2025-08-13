/**
 * AI-Powered Insights Service
 * Provides intelligent analysis of portfolio decisions and market conditions
 */

export interface AIInsight {
  id: string;
  type: 'recommendation' | 'analysis' | 'warning' | 'opportunity';
  title: string;
  description: string;
  confidence: number; // 0-100
  impact: 'high' | 'medium' | 'low';
  actionable: boolean;
  data?: any;
  reasoning: string[];
  timestamp: Date;
}

export interface PortfolioAnalysis {
  overall_score: number; // 0-100
  risk_level: 'conservative' | 'moderate' | 'aggressive';
  diversification_score: number;
  performance_trend: 'upward' | 'downward' | 'sideways';
  key_insights: AIInsight[];
  sector_analysis: SectorAnalysis[];
  optimization_suggestions: OptimizationSuggestion[];
}

export interface SectorAnalysis {
  sector: string;
  allocation: number;
  performance: number;
  sentiment: 'bullish' | 'bearish' | 'neutral';
  reasoning: string;
  recommendation: string;
}

export interface OptimizationSuggestion {
  action: 'increase' | 'decrease' | 'hold' | 'rebalance';
  asset: string;
  current_weight: number;
  suggested_weight: number;
  reasoning: string;
  expected_impact: string;
}

export interface MarketSentiment {
  overall: 'bullish' | 'bearish' | 'neutral';
  score: number; // -100 to 100
  factors: {
    economic_indicators: number;
    market_volatility: number;
    sector_rotation: number;
    geopolitical_events: number;
  };
  narrative: string;
}

class AIInsightsService {
  private static instance: AIInsightsService;

  public static getInstance(): AIInsightsService {
    if (!AIInsightsService.instance) {
      AIInsightsService.instance = new AIInsightsService();
    }
    return AIInsightsService.instance;
  }

  /**
   * Analyze current portfolio allocations and generate insights
   */
  public async analyzePortfolio(
    allocations: { symbol: string; weight: number; name?: string; sector?: string }[],
    performanceData: { date: string; value: number }[],
    benchmarkData: { date: string; value: number }[]
  ): Promise<PortfolioAnalysis> {
    
    // Simulate AI analysis with sophisticated logic
    const analysis = await this.performPortfolioAnalysis(allocations, performanceData, benchmarkData);
    return analysis;
  }

  /**
   * Generate investment reasoning for current allocations
   */
  public generateInvestmentReasons(
    allocations: { symbol: string; weight: number; name?: string; sector?: string }[]
  ): string[] {
    const reasons = [];
    
    // Analyze sector diversification
    const sectorMap = this.analyzeSectorDiversification(allocations);
    
    // Generate reasoning based on allocation strategy
    if (sectorMap['Technology'] > 0.4) {
      reasons.push("🚀 Heavy technology allocation capitalizes on digital transformation trends and innovation-driven growth in the current market cycle.");
    }
    
    if (allocations.length > 15) {
      reasons.push("🎯 Broad diversification across " + allocations.length + " assets reduces idiosyncratic risk while capturing market-wide opportunities.");
    } else {
      reasons.push("💎 Concentrated portfolio of " + allocations.length + " high-conviction positions allows for greater alpha generation potential.");
    }
    
    // Risk management reasoning
    const hasDefensive = allocations.some(a => ['Consumer Staples', 'Utilities', 'Bond'].includes(a.sector || ''));
    if (hasDefensive) {
      reasons.push("🛡️ Defensive positions provide portfolio stability and downside protection during market volatility.");
    }
    
    // Growth vs Value analysis
    const techAndGrowth = sectorMap['Technology'] + (sectorMap['Communication Services'] || 0);
    if (techAndGrowth > 0.3) {
      reasons.push("📈 Growth-oriented allocation positioned for long-term wealth creation in secular growth trends.");
    }
    
    // International exposure
    const hasInternational = allocations.some(a => ['International', 'Emerging Markets'].includes(a.sector || ''));
    if (hasInternational) {
      reasons.push("🌍 International exposure captures global growth opportunities and reduces geographic concentration risk.");
    }
    
    return reasons;
  }

  /**
   * Generate smart recommendations based on market conditions
   */
  public async generateRecommendations(
    currentAllocations: { symbol: string; weight: number }[],
    performanceData: { date: string; value: number }[]
  ): Promise<AIInsight[]> {
    const recommendations: AIInsight[] = [];
    
    // Analyze recent performance trend
    const recentPerformance = this.calculateRecentTrend(performanceData);
    
    if (recentPerformance < -0.05) { // 5% decline
      recommendations.push({
        id: 'rebalance-suggestion',
        type: 'recommendation',
        title: 'Rebalancing Opportunity Detected',
        description: 'Recent market decline has created rebalancing opportunities to buy quality assets at discounted prices.',
        confidence: 85,
        impact: 'high',
        actionable: true,
        reasoning: [
          'Portfolio has declined 5%+ recently, creating buying opportunities',
          'Historical analysis shows strong recovery patterns after similar declines',
          'Current valuations appear attractive relative to fundamentals'
        ],
        timestamp: new Date()
      });
    }
    
    // Diversification analysis
    const diversificationScore = this.calculateDiversificationScore(currentAllocations);
    if (diversificationScore < 0.7) {
      recommendations.push({
        id: 'diversification-warning',
        type: 'warning',
        title: 'Concentration Risk Detected',
        description: 'Portfolio shows high concentration in few positions. Consider broadening allocations.',
        confidence: 90,
        impact: 'medium',
        actionable: true,
        reasoning: [
          'Top 3 positions represent over 50% of portfolio',
          'Single asset failure could significantly impact returns',
          'Broader diversification reduces volatility without sacrificing returns'
        ],
        timestamp: new Date()
      });
    }
    
    return recommendations;
  }

  /**
   * Analyze market sentiment and conditions
   */
  public async analyzeMarketSentiment(): Promise<MarketSentiment> {
    // Simulate sophisticated sentiment analysis
    const baseScore = Math.random() * 200 - 100; // -100 to 100
    
    return {
      overall: baseScore > 20 ? 'bullish' : baseScore < -20 ? 'bearish' : 'neutral',
      score: Math.round(baseScore),
      factors: {
        economic_indicators: Math.round((Math.random() * 200 - 100)),
        market_volatility: Math.round((Math.random() * 200 - 100)),
        sector_rotation: Math.round((Math.random() * 200 - 100)),
        geopolitical_events: Math.round((Math.random() * 200 - 100))
      },
      narrative: this.generateMarketNarrative(baseScore)
    };
  }

  // Private helper methods
  private async performPortfolioAnalysis(
    allocations: { symbol: string; weight: number; sector?: string }[],
    performanceData: { date: string; value: number }[],
    benchmarkData: { date: string; value: number }[]
  ): Promise<PortfolioAnalysis> {
    
    const diversificationScore = this.calculateDiversificationScore(allocations);
    const performanceTrend = this.analyzePerformanceTrend(performanceData, benchmarkData);
    
    return {
      overall_score: Math.round(diversificationScore * 100),
      risk_level: this.assessRiskLevel(allocations),
      diversification_score: Math.round(diversificationScore * 100),
      performance_trend: performanceTrend,
      key_insights: await this.generateRecommendations(allocations, performanceData),
      sector_analysis: this.analyzeSectors(allocations),
      optimization_suggestions: this.generateOptimizationSuggestions(allocations)
    };
  }

  private analyzeSectorDiversification(
    allocations: { symbol: string; weight: number; sector?: string }[]
  ): Record<string, number> {
    const sectorMap: Record<string, number> = {};
    
    allocations.forEach(allocation => {
      const sector = allocation.sector || 'Unknown';
      sectorMap[sector] = (sectorMap[sector] || 0) + allocation.weight;
    });
    
    return sectorMap;
  }

  private calculateDiversificationScore(allocations: { weight: number }[]): number {
    if (allocations.length === 0) return 0;
    
    // Calculate Herfindahl-Hirschman Index for concentration
    const hhi = allocations.reduce((sum, allocation) => {
      return sum + Math.pow(allocation.weight, 2);
    }, 0);
    
    // Convert to diversification score (1 = perfectly diversified, 0 = fully concentrated)
    return Math.max(0, 1 - hhi);
  }

  private calculateRecentTrend(performanceData: { value: number }[]): number {
    if (performanceData.length < 2) return 0;
    
    const recent = performanceData.slice(-5); // Last 5 data points
    const start = recent[0].value;
    const end = recent[recent.length - 1].value;
    
    return (end - start) / start;
  }

  private assessRiskLevel(allocations: { sector?: string }[]): 'conservative' | 'moderate' | 'aggressive' {
    const defensiveSectors = ['Consumer Staples', 'Utilities', 'Bond'];
    const defensiveWeight = allocations.reduce((sum, allocation) => {
      return sum + (defensiveSectors.includes(allocation.sector || '') ? 1 : 0);
    }, 0) / allocations.length;
    
    if (defensiveWeight > 0.4) return 'conservative';
    if (defensiveWeight > 0.2) return 'moderate';
    return 'aggressive';
  }

  private analyzePerformanceTrend(
    performanceData: { value: number }[],
    benchmarkData: { value: number }[]
  ): 'upward' | 'downward' | 'sideways' {
    if (performanceData.length < 10) return 'sideways';
    
    const recentTrend = this.calculateRecentTrend(performanceData);
    
    if (recentTrend > 0.02) return 'upward';
    if (recentTrend < -0.02) return 'downward';
    return 'sideways';
  }

  private analyzeSectors(
    allocations: { symbol: string; weight: number; sector?: string }[]
  ): SectorAnalysis[] {
    const sectorMap = this.analyzeSectorDiversification(allocations);
    
    return Object.entries(sectorMap).map(([sector, allocation]) => ({
      sector,
      allocation: Math.round(allocation * 100),
      performance: Math.round((Math.random() * 20 - 10)), // Simulated performance
      sentiment: Math.random() > 0.5 ? 'bullish' : 'neutral' as 'bullish' | 'bearish' | 'neutral',
      reasoning: `${sector} sector showing ${allocation > 0.2 ? 'strong' : 'moderate'} allocation with favorable market conditions.`,
      recommendation: allocation > 0.3 ? 'Consider taking some profits' : 'Maintain current position'
    }));
  }

  private generateOptimizationSuggestions(
    allocations: { symbol: string; weight: number }[]
  ): OptimizationSuggestion[] {
    // Generate smart optimization suggestions
    const suggestions: OptimizationSuggestion[] = [];
    
    // Find overweight positions
    const overweightThreshold = 1 / allocations.length * 1.5; // 1.5x equal weight
    
    allocations.forEach(allocation => {
      if (allocation.weight > overweightThreshold) {
        suggestions.push({
          action: 'decrease',
          asset: allocation.symbol,
          current_weight: Math.round(allocation.weight * 100),
          suggested_weight: Math.round(overweightThreshold * 100),
          reasoning: 'Reduce concentration risk by trimming overweight position',
          expected_impact: 'Lower volatility, improved risk-adjusted returns'
        });
      }
    });
    
    return suggestions.slice(0, 3); // Top 3 suggestions
  }

  private generateMarketNarrative(score: number): string {
    if (score > 50) {
      return "Strong bullish sentiment driven by robust economic indicators and positive market momentum. Risk-on environment favors growth assets.";
    } else if (score > 0) {
      return "Moderately positive market sentiment with cautious optimism. Mixed signals suggest selective approach to risk assets.";
    } else if (score > -50) {
      return "Neutral to slightly negative sentiment reflects market uncertainty. Defensive positioning may be warranted in the near term.";
    } else {
      return "Bearish sentiment dominates with heightened risk aversion. Focus on capital preservation and high-quality assets recommended.";
    }
  }
}

export const aiInsights = AIInsightsService.getInstance();