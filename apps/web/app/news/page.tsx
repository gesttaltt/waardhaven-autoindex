"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { newsService, type NewsArticle, type TrendingEntity } from "../services/api/news";
import { portfolioService } from "../services/api";

export default function NewsInsightsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [trendingEntities, setTrendingEntities] = useState<TrendingEntity[]>([]);
  const [allocations, setAllocations] = useState<any[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);
  const [sentimentFilter, setSentimentFilter] = useState<'all' | 'positive' | 'negative'>('all');
  
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Get current portfolio allocations
      const allocRes = await portfolioService.getCurrentAllocations();
      setAllocations(allocRes.allocations);
      
      // Get portfolio symbols
      const symbols = allocRes.allocations.map(a => a.symbol);
      
      // Fetch news for portfolio symbols
      const [newsRes, trendingRes] = await Promise.all([
        newsService.searchNews({ 
          symbols, 
          limit: 50 
        }),
        newsService.getTrendingEntities()
      ]);
      
      setArticles(newsRes);
      setTrendingEntities(trendingRes);
      
    } catch (err) {
      console.error('Failed to load news data:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredArticles = articles.filter(article => {
    if (selectedSymbol && !article.symbols.includes(selectedSymbol)) return false;
    if (sentimentFilter === 'positive' && (article.sentiment_score || 0) <= 0) return false;
    if (sentimentFilter === 'negative' && (article.sentiment_score || 0) >= 0) return false;
    return true;
  });

  const getSentimentColor = (score: number | undefined) => {
    if (!score) return 'text-neutral-400';
    if (score > 0.2) return 'text-green-400';
    if (score < -0.2) return 'text-red-400';
    return 'text-neutral-400';
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
              <h1 className="text-xl font-semibold text-white">
                Market News & Sentiment
              </h1>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Trending Entities */}
        {trendingEntities.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-white mb-4">Trending Assets</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {trendingEntities.slice(0, 8).map(entity => (
                <motion.div
                  key={entity.symbol}
                  whileHover={{ scale: 1.05 }}
                  className="bg-white/5 rounded-lg p-4 backdrop-blur-sm cursor-pointer"
                  onClick={() => setSelectedSymbol(entity.symbol)}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-semibold text-white">{entity.symbol}</p>
                      <p className="text-sm text-neutral-400">{entity.mention_count} mentions</p>
                    </div>
                    <span className={`text-sm ${getSentimentColor(entity.sentiment_score)}`}>
                      {entity.sentiment_score > 0 ? '↑' : entity.sentiment_score < 0 ? '↓' : '→'}
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="flex gap-4 mb-6">
          <select
            value={selectedSymbol || ''}
            onChange={(e) => setSelectedSymbol(e.target.value || null)}
            className="bg-white/10 text-white rounded-lg px-4 py-2"
          >
            <option value="">All Symbols</option>
            {allocations.map(a => (
              <option key={a.symbol} value={a.symbol}>{a.symbol}</option>
            ))}
          </select>
          
          <div className="flex gap-2">
            {(['all', 'positive', 'negative'] as const).map(filter => (
              <button
                key={filter}
                onClick={() => setSentimentFilter(filter)}
                className={`px-4 py-2 rounded-lg transition-all ${
                  sentimentFilter === filter
                    ? 'bg-purple-500 text-white'
                    : 'bg-white/10 text-white/70 hover:text-white'
                }`}
              >
                {filter.charAt(0).toUpperCase() + filter.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* News Articles */}
        <div className="space-y-4">
          {loading ? (
            [...Array(5)].map((_, i) => (
              <div key={i} className="bg-white/5 rounded-lg p-6 animate-pulse">
                <div className="h-6 bg-white/10 rounded mb-2 w-3/4"></div>
                <div className="h-4 bg-white/10 rounded w-full"></div>
              </div>
            ))
          ) : filteredArticles.length > 0 ? (
            filteredArticles.map(article => (
              <motion.div
                key={article.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white/5 rounded-lg p-6 backdrop-blur-sm hover:bg-white/10 transition-all"
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-lg font-semibold text-white flex-1">
                    <a href={article.url} target="_blank" rel="noopener noreferrer" className="hover:text-purple-400">
                      {article.title}
                    </a>
                  </h3>
                  {article.sentiment_score && (
                    <span className={`ml-4 font-medium ${getSentimentColor(article.sentiment_score)}`}>
                      {article.sentiment_score > 0 ? '+' : ''}{(article.sentiment_score * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
                
                <p className="text-neutral-400 mb-3">{article.description}</p>
                
                <div className="flex items-center justify-between text-sm">
                  <div className="flex gap-4">
                    <span className="text-neutral-500">{article.source}</span>
                    <span className="text-neutral-500">
                      {new Date(article.published_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex gap-2">
                    {article.symbols.map(symbol => (
                      <span
                        key={symbol}
                        onClick={() => setSelectedSymbol(symbol)}
                        className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded cursor-pointer hover:bg-purple-500/30"
                      >
                        {symbol}
                      </span>
                    ))}
                  </div>
                </div>
              </motion.div>
            ))
          ) : (
            <div className="text-center py-12">
              <p className="text-neutral-400">No news articles found</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}