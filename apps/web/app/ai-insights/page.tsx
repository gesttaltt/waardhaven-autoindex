"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Treemap, Cell } from "recharts";
import api from "../utils/api";
import { aiInsights, PortfolioAnalysis, AIInsight, MarketSentiment } from "../services/aiInsights";

type Allocation = { symbol: string; weight: number; name?: string; sector?: string };
type SeriesPoint = { date: string; value: number };

export default function AIInsightsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [allocations, setAllocations] = useState<Allocation[]>([]);
  const [indexSeries, setIndexSeries] = useState<SeriesPoint[]>([]);
  const [spSeries, setSpSeries] = useState<SeriesPoint[]>([]);
  const [portfolioAnalysis, setPortfolioAnalysis] = useState<PortfolioAnalysis | null>(null);
  const [marketSentiment, setMarketSentiment] = useState<MarketSentiment | null>(null);
  const [investmentReasons, setInvestmentReasons] = useState<string[]>([]);
  const [selectedInsight, setSelectedInsight] = useState<AIInsight | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'reasons' | 'recommendations' | 'sentiment'>('overview');
  
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  useEffect(() => {
    if (!token) {
      router.push("/login");
      return;
    }
    
    loadData();
  }, [token, router]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Fetch data from API
      const [indexRes, spRes, allocRes] = await Promise.all([
        api.get('/api/v1/index/history'),
        api.get('/api/v1/benchmark/sp500'),
        api.get('/api/v1/index/current')
      ]);
      
      const indexData = indexRes.data.series;
      const spData = spRes.data.series;
      const allocData = allocRes.data.allocations;
      
      setIndexSeries(indexData);
      setSpSeries(spData);
      setAllocations(allocData);
      
      // Generate AI insights
      const analysis = await aiInsights.analyzePortfolio(allocData, indexData, spData);
      const sentiment = await aiInsights.analyzeMarketSentiment();
      const reasons = aiInsights.generateInvestmentReasons(allocData);
      
      setPortfolioAnalysis(analysis);
      setMarketSentiment(sentiment);
      setInvestmentReasons(reasons);
      
    } catch (err) {
      console.error('Failed to load AI insights:', err);
    } finally {
      setLoading(false);
    }
  };

  const radarData = portfolioAnalysis ? [
    { metric: 'Diversification', value: portfolioAnalysis.diversification_score, fullMark: 100 },
    { metric: 'Performance', value: portfolioAnalysis.overall_score, fullMark: 100 },
    { metric: 'Risk Management', value: portfolioAnalysis.risk_level === 'conservative' ? 90 : portfolioAnalysis.risk_level === 'moderate' ? 60 : 30, fullMark: 100 },
    { metric: 'Market Timing', value: 75, fullMark: 100 },
    { metric: 'Asset Quality', value: 85, fullMark: 100 },
    { metric: 'Efficiency', value: 80, fullMark: 100 }
  ] : [];

  const treemapData = allocations.map((allocation, index) => ({
    name: allocation.symbol,
    size: allocation.weight * 100,
    sector: allocation.sector,
    color: `hsl(${(index * 137.508) % 360}, 70%, 60%)`
  }));

  const getInsightIcon = (type: AIInsight['type']) => {
    switch (type) {
      case 'recommendation': return 'REC';
      case 'analysis': return 'ANA';
      case 'warning': return 'WARN';
      case 'opportunity': return 'OPP';
      default: return 'INFO';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-green-400';
    if (confidence >= 60) return 'text-yellow-400';
    return 'text-orange-400';
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'bullish': return 'text-green-400';
      case 'bearish': return 'text-red-400';
      default: return 'text-neutral-400';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Navigation */}
      <nav className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push("/dashboard")}
                className="text-white/70 hover:text-white transition-colors"
              >
                ← Back to Dashboard
              </button>
              <h1 className="text-xl font-semibold text-white flex items-center gap-2">
AI-Powered AutoIndex
              </h1>
            </div>
            
            <button
              onClick={() => {
                localStorage.removeItem("token");
                router.push("/login");
              }}
              className="text-white/70 hover:text-white transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h2 className="text-3xl font-bold gradient-text mb-2">
            Intelligent Portfolio Analysis
          </h2>
          <p className="text-neutral-400 max-w-2xl mx-auto">
            AI-powered insights into your AutoIndex strategy with deep analysis of investment decisions, 
            market conditions, and optimization opportunities.
          </p>
        </motion.div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="bg-white/5 rounded-lg p-1 flex">
            {[
              { key: 'overview', label: 'Overview', icon: 'OVR' },
              { key: 'reasons', label: 'Investment Logic', icon: 'LOGIC' },
              { key: 'recommendations', label: 'AI Recommendations', icon: 'AI' },
              { key: 'sentiment', label: 'Market Sentiment', icon: 'SENT' }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                  activeTab === tab.key
                    ? "bg-purple-500 text-white"
                    : "text-neutral-400 hover:text-white hover:bg-white/5"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-white/5 rounded-lg p-6 animate-pulse">
                <div className="h-6 bg-white/10 rounded mb-4"></div>
                <div className="h-32 bg-white/10 rounded"></div>
              </div>
            ))}
          </div>
        ) : (
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              
              {/* Overview Tab */}
              {activeTab === 'overview' && portfolioAnalysis && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  
                  {/* Portfolio Health Radar */}
                  <div className="bg-white/5 rounded-lg p-6 backdrop-blur-sm">
                    <h3 className="text-xl font-semibold mb-4 gradient-text">Portfolio Health Score</h3>
                    <div className="h-80">
                      <ResponsiveContainer width="100%" height="100%">
                        <RadarChart data={radarData}>
                          <PolarGrid stroke="rgba(255,255,255,0.1)" />
                          <PolarAngleAxis dataKey="metric" tick={{ fontSize: 12, fill: '#ffffff' }} />
                          <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} />
                          <Radar
                            name="Score"
                            dataKey="value"
                            stroke="#8b5cf6"
                            fill="#8b5cf6"
                            fillOpacity={0.3}
                            strokeWidth={2}
                          />
                        </RadarChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="mt-4 text-center">
                      <p className="text-2xl font-bold gradient-text">
                        {portfolioAnalysis.overall_score}/100
                      </p>
                      <p className="text-sm text-neutral-400">Overall Portfolio Score</p>
                    </div>
                  </div>

                  {/* Asset Allocation Treemap */}
                  <div className="bg-white/5 rounded-lg p-6 backdrop-blur-sm">
                    <h3 className="text-xl font-semibent mb-4 gradient-text">Asset Allocation Map</h3>
                    <div className="h-80">
                      <ResponsiveContainer width="100%" height="100%">
                        <Treemap
                          data={treemapData}
                          dataKey="size"
                          aspectRatio={4/3}
                          stroke="rgba(255,255,255,0.2)"
                          fill="#8b5cf6"
                        >
                          {treemapData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Treemap>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Risk Analysis */}
                  <div className="bg-white/5 rounded-lg p-6 backdrop-blur-sm">
                    <h3 className="text-xl font-semibold mb-4 gradient-text">Risk Analysis</h3>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-neutral-300">Risk Level</span>
                        <span className={`font-semibold capitalize ${
                          portfolioAnalysis.risk_level === 'conservative' ? 'text-green-400' :
                          portfolioAnalysis.risk_level === 'moderate' ? 'text-yellow-400' :
                          'text-red-400'
                        }`}>
                          {portfolioAnalysis.risk_level}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-neutral-300">Diversification</span>
                        <span className="font-semibold text-purple-400">
                          {portfolioAnalysis.diversification_score}/100
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-neutral-300">Trend</span>
                        <span className={`font-semibold capitalize ${
                          portfolioAnalysis.performance_trend === 'upward' ? 'text-green-400' :
                          portfolioAnalysis.performance_trend === 'downward' ? 'text-red-400' :
                          'text-neutral-400'
                        }`}>
                          {portfolioAnalysis.performance_trend}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Sector Analysis */}
                  <div className="bg-white/5 rounded-lg p-6 backdrop-blur-sm">
                    <h3 className="text-xl font-semibold mb-4 gradient-text">Sector Analysis</h3>
                    <div className="space-y-3">
                      {portfolioAnalysis.sector_analysis.slice(0, 5).map((sector, index) => (
                        <motion.div
                          key={sector.sector}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className="flex items-center justify-between p-3 bg-white/5 rounded-lg"
                        >
                          <div>
                            <p className="font-medium text-white">{sector.sector}</p>
                            <p className="text-sm text-neutral-400">{sector.allocation}% allocation</p>
                          </div>
                          <div className="text-right">
                            <p className={`text-sm font-medium ${getSentimentColor(sector.sentiment)}`}>
                              {sector.sentiment.toUpperCase()}
                            </p>
                            <p className={`text-lg font-bold ${
                              sector.performance > 0 ? 'text-green-400' : 'text-red-400'
                            }`}>
                              {sector.performance > 0 ? '+' : ''}{sector.performance}%
                            </p>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Investment Logic Tab */}
              {activeTab === 'reasons' && (
                <div className="max-w-4xl mx-auto">
                  <div className="bg-white/5 rounded-lg p-8 backdrop-blur-sm">
                    <h3 className="text-2xl font-semibold mb-6 gradient-text text-center">
                      🧠 Why We Invest This Way
                    </h3>
                    <p className="text-neutral-400 text-center mb-8">
                      Our AI analyzes market conditions, risk factors, and performance patterns to make intelligent investment decisions.
                    </p>
                    
                    <div className="grid gap-6">
                      {investmentReasons.map((reason, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className="bg-white/10 rounded-lg p-6 border border-purple-500/20"
                        >
                          <p className="text-white text-lg leading-relaxed">{reason}</p>
                        </motion.div>
                      ))}
                    </div>
                    
                    {/* Strategy Summary */}
                    <div className="mt-8 p-6 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-lg border border-purple-500/30">
                      <h4 className="text-lg font-semibold mb-3 text-purple-300">Strategy Summary</h4>
                      <p className="text-neutral-300 leading-relaxed">
                        Our AutoIndex employs a quantitative approach that dynamically filters underperforming assets 
                        while maintaining optimal diversification. The strategy adapts to market conditions, focusing on 
                        risk-adjusted returns and long-term wealth preservation.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* AI Recommendations Tab */}
              {activeTab === 'recommendations' && portfolioAnalysis && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="text-xl font-semibold gradient-text">AI Recommendations</h3>
                    {portfolioAnalysis.key_insights.map((insight, index) => (
                      <motion.div
                        key={insight.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        onClick={() => setSelectedInsight(insight)}
                        className="bg-white/5 rounded-lg p-4 cursor-pointer hover:bg-white/10 transition-all border border-white/10 hover:border-purple-500/30"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3">
                            <span className="text-2xl">{getInsightIcon(insight.type)}</span>
                            <div>
                              <h4 className="font-medium text-white">{insight.title}</h4>
                              <p className="text-sm text-neutral-400 mt-1">{insight.description}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className={`text-sm font-medium ${getConfidenceColor(insight.confidence)}`}>
                              {insight.confidence}% confidence
                            </p>
                            <p className="text-xs text-neutral-500 capitalize">{insight.impact} impact</p>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                  
                  {/* Detailed Insight Panel */}
                  <div className="bg-white/5 rounded-lg p-6 backdrop-blur-sm">
                    {selectedInsight ? (
                      <div>
                        <div className="flex items-center gap-3 mb-4">
                          <span className="text-3xl">{getInsightIcon(selectedInsight.type)}</span>
                          <h4 className="text-lg font-semibold text-white">{selectedInsight.title}</h4>
                        </div>
                        
                        <p className="text-neutral-300 mb-6">{selectedInsight.description}</p>
                        
                        <div className="space-y-3">
                          <h5 className="font-medium text-purple-300">Reasoning:</h5>
                          {selectedInsight.reasoning.map((reason, index) => (
                            <div key={index} className="flex items-start gap-2">
                              <span className="text-purple-400 mt-1">•</span>
                              <p className="text-sm text-neutral-400">{reason}</p>
                            </div>
                          ))}
                        </div>
                        
                        <div className="mt-6 p-4 bg-white/5 rounded-lg">
                          <div className="flex justify-between items-center">
                            <div>
                              <p className="text-sm text-neutral-400">Confidence Level</p>
                              <p className={`text-lg font-bold ${getConfidenceColor(selectedInsight.confidence)}`}>
                                {selectedInsight.confidence}%
                              </p>
                            </div>
                            <div>
                              <p className="text-sm text-neutral-400">Impact</p>
                              <p className="text-lg font-bold text-white capitalize">{selectedInsight.impact}</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-12">
                        <div className="text-6xl opacity-50 font-bold text-neutral-600">AI</div>
                        <p className="text-neutral-400 mt-4">Select a recommendation to see detailed analysis</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Market Sentiment Tab */}
              {activeTab === 'sentiment' && marketSentiment && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  
                  {/* Sentiment Overview */}
                  <div className="bg-white/5 rounded-lg p-6 backdrop-blur-sm">
                    <h3 className="text-xl font-semibold mb-6 gradient-text">Market Sentiment Analysis</h3>
                    
                    <div className="text-center mb-6">
                      <div className={`text-4xl mb-3 font-bold ${getSentimentColor(marketSentiment.overall)}`}>
                        {marketSentiment.overall === 'bullish' ? 'BULL' : 
                         marketSentiment.overall === 'bearish' ? 'BEAR' : 'NEUTRAL'}
                      </div>
                      <p className={`text-2xl font-bold capitalize ${getSentimentColor(marketSentiment.overall)}`}>
                        {marketSentiment.overall}
                      </p>
                      <p className="text-neutral-400">
                        Sentiment Score: {marketSentiment.score}/100
                      </p>
                    </div>
                    
                    <div className="space-y-4">
                      <div className="w-full bg-white/10 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full transition-all duration-1000 ${
                            marketSentiment.score > 0 ? 'bg-green-400' : 'bg-red-400'
                          }`}
                          style={{ width: `${Math.abs(marketSentiment.score)}%` }}
                        />
                      </div>
                      
                      <p className="text-neutral-300 leading-relaxed">
                        {marketSentiment.narrative}
                      </p>
                    </div>
                  </div>

                  {/* Sentiment Factors */}
                  <div className="bg-white/5 rounded-lg p-6 backdrop-blur-sm">
                    <h4 className="text-lg font-semibold mb-4 text-white">Contributing Factors</h4>
                    
                    <div className="space-y-4">
                      {Object.entries(marketSentiment.factors).map(([factor, value]) => (
                        <div key={factor} className="space-y-2">
                          <div className="flex justify-between items-center">
                            <span className="text-neutral-300 capitalize">
                              {factor.replace('_', ' ')}
                            </span>
                            <span className={`font-semibold ${
                              value > 20 ? 'text-green-400' : 
                              value < -20 ? 'text-red-400' : 
                              'text-neutral-400'
                            }`}>
                              {value > 0 ? '+' : ''}{value}
                            </span>
                          </div>
                          <div className="w-full bg-white/10 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full transition-all duration-500 ${
                                value > 0 ? 'bg-green-400' : 'bg-red-400'
                              }`}
                              style={{ 
                                width: `${Math.abs(value)}%`,
                                marginLeft: value < 0 ? `${100 - Math.abs(value)}%` : '0'
                              }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}