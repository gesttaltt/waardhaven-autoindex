"use client";

import { motion } from 'framer-motion';
import { SeriesPoint, RiskMetric } from '../../types/portfolio';

interface PerformanceCardsProps {
  indexSeries: SeriesPoint[];
  allocationsCount: number;
  riskMetrics: RiskMetric | null;
}

export function PerformanceCards({ 
  indexSeries, 
  allocationsCount, 
  riskMetrics 
}: PerformanceCardsProps) {
  // Calculate performance metrics
  const currentPerformance = indexSeries.length > 0 
    ? ((indexSeries[indexSeries.length - 1].value - 100) / 100 * 100).toFixed(2)
    : "0";

  // Calculate volatility
  const calculateVolatility = (data: SeriesPoint[]) => {
    if (!data || data.length < 2) return 0;
    try {
      const returns = data.slice(1).map((point, i) => {
        const prevValue = data[i].value;
        if (prevValue === 0) return 0;
        return (point.value - prevValue) / prevValue;
      });
      
      if (returns.length === 0) return 0;
      
      const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
      const variance = returns.reduce((sum, ret) => sum + Math.pow(ret - avgReturn, 2), 0) / returns.length;
      return Math.sqrt(variance) * Math.sqrt(252) * 100; // Annualized volatility
    } catch (err) {
      console.error('Error calculating volatility:', err);
      return 0;
    }
  };

  const volatility = calculateVolatility(indexSeries);

  const cards = [
    {
      title: "Total Performance",
      value: `${currentPerformance}%`,
      gradient: true,
    },
    {
      title: "Active Assets",
      value: allocationsCount.toString(),
      gradient: true,
    },
    {
      title: riskMetrics ? "Sharpe Ratio" : "Index Value",
      value: riskMetrics 
        ? riskMetrics.sharpe_ratio.toFixed(2)
        : (indexSeries.length > 0 ? indexSeries[indexSeries.length - 1].value.toFixed(2) : "100"),
      gradient: true,
    },
    {
      title: riskMetrics ? "Max Drawdown" : "Volatility (Annual)",
      value: riskMetrics 
        ? `${(riskMetrics.max_drawdown * 100).toFixed(1)}%`
        : `${volatility.toFixed(1)}%`,
      gradient: !riskMetrics,
      className: riskMetrics ? "text-orange-400" : "",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      {cards.map((card, index) => (
        <motion.div
          key={card.title}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 + index * 0.1 }}
          className="card"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-neutral-300">{card.title}</p>
              <p className={`text-3xl font-bold ${
                card.gradient ? 'gradient-text' : card.className || ''
              }`}>
                {card.value}
              </p>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}