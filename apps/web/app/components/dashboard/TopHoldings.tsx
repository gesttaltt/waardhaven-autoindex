"use client";

import { useState } from 'react';
import { motion } from 'framer-motion';
import { AllocationItem } from '../../types/portfolio';
import { CHART_COLORS } from '../../constants/theme';
import { PORTFOLIO_CONFIG } from '../../constants/config';

interface TopHoldingsProps {
  allocations: AllocationItem[];
  loading: boolean;
}

export function TopHoldings({ allocations, loading }: TopHoldingsProps) {
  const [hoveredAsset, setHoveredAsset] = useState<string | null>(null);
  const topHoldings = allocations.slice(0, PORTFOLIO_CONFIG.TOP_HOLDINGS_COUNT);

  if (loading) {
    return (
      <motion.section
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.7 }}
        className="card"
      >
        <h2 className="text-xl font-semibold mb-4 gradient-text">Top Holdings</h2>
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-12 skeleton rounded-lg" />
          ))}
        </div>
      </motion.section>
    );
  }

  return (
    <motion.section
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.7 }}
      className="card"
    >
      <h2 className="text-xl font-semibold mb-4 gradient-text">Top Holdings</h2>
      <div className="space-y-3">
        {topHoldings.map((allocation, index) => (
          <motion.div
            key={allocation.symbol}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.8 + index * 0.1 }}
            className={`flex items-center justify-between p-3 rounded-lg transition-all cursor-pointer ${
              hoveredAsset === allocation.symbol 
                ? 'bg-purple-500/20 border border-purple-500/30' 
                : 'bg-white/5 hover:bg-white/10'
            }`}
            onMouseEnter={() => setHoveredAsset(allocation.symbol)}
            onMouseLeave={() => setHoveredAsset(null)}
          >
            <div className="flex items-center gap-3">
              <motion.div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }}
                animate={{ 
                  scale: hoveredAsset === allocation.symbol ? 1.3 : 1,
                  boxShadow: hoveredAsset === allocation.symbol 
                    ? `0 0 12px ${CHART_COLORS[index % CHART_COLORS.length]}40` 
                    : 'none'
                }}
              />
              <div>
                <span className="font-medium block">{allocation.symbol}</span>
                {allocation.name && (
                  <span className="text-xs text-neutral-500">{allocation.name}</span>
                )}
              </div>
            </div>
            <div className="text-right">
              <span className="font-semibold gradient-text">
                {(allocation.weight * 100).toFixed(2)}%
              </span>
              {allocation.sector && (
                <div className="text-xs text-neutral-500">{allocation.sector}</div>
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </motion.section>
  );
}