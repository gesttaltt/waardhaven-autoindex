"use client";

import { useState } from 'react';
import { motion } from 'framer-motion';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';
import { AllocationItem } from '../../types/portfolio';
import { CHART_COLORS, CHART_TOOLTIP_STYLE } from '../../constants/theme';

interface PortfolioAllocationProps {
  allocations: AllocationItem[];
  loading: boolean;
}

export function PortfolioAllocation({ allocations, loading }: PortfolioAllocationProps) {
  const [hoveredAsset, setHoveredAsset] = useState<string | null>(null);

  const pieData = allocations.map(a => ({
    name: a.symbol,
    value: a.weight * 100,
    fullName: a.name,
    sector: a.sector,
  }));

  if (loading) {
    return (
      <motion.section
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.6 }}
        className="card"
      >
        <h2 className="text-xl font-semibold mb-4 gradient-text">Portfolio Allocation</h2>
        <div className="h-64 skeleton rounded-xl" />
      </motion.section>
    );
  }

  return (
    <motion.section
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.6 }}
      className="card"
    >
      <h2 className="text-xl font-semibold mb-4 gradient-text">Portfolio Allocation</h2>
      {allocations.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={false}
              outerRadius={hoveredAsset ? 90 : 85}
              fill="#8884d8"
              dataKey="value"
              onMouseEnter={(data) => setHoveredAsset(data.name)}
              onMouseLeave={() => setHoveredAsset(null)}
            >
              {pieData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={CHART_COLORS[index % CHART_COLORS.length]}
                  stroke={hoveredAsset === entry.name ? '#ffffff' : 'transparent'}
                  strokeWidth={hoveredAsset === entry.name ? 2 : 0}
                />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{
                ...CHART_TOOLTIP_STYLE,
                color: '#ffffff',
              }}
              labelStyle={{ color: '#e5e5e5' }}
              itemStyle={{ color: '#e5e5e5' }}
              formatter={(value: number, name: string, props: any) => [
                `${value.toFixed(2)}%`,
                props.payload.fullName || props.payload.name
              ]}
            />
          </PieChart>
        </ResponsiveContainer>
      ) : (
        <p className="text-neutral-400">No allocations available</p>
      )}
    </motion.section>
  );
}