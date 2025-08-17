'use client';

import { Card, CardBody } from '../../ui/Card';
import { formatPercentage, formatCurrency } from '../../../lib/utils';
import { PerformanceMetrics as Metrics } from '../../../lib/calculations/portfolio';

interface PerformanceMetricsProps {
  metrics: Metrics;
  currentValue: number;
  initialValue: number;
  currency?: string;
}

export function PerformanceMetrics({
  metrics,
  currentValue,
  initialValue,
  currency = 'USD',
}: PerformanceMetricsProps) {
  const profit = currentValue - initialValue;
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
      <MetricCard
        label="Portfolio Value"
        value={formatCurrency(currentValue, currency)}
        change={formatPercentage(metrics.totalReturn)}
        positive={metrics.totalReturn >= 0}
      />
      
      <MetricCard
        label="Total Return"
        value={formatPercentage(metrics.totalReturn)}
        subValue={formatCurrency(profit, currency)}
        positive={profit >= 0}
      />
      
      <MetricCard
        label="Sharpe Ratio"
        value={metrics.sharpeRatio.toFixed(2)}
        description="Risk-adjusted return"
        positive={metrics.sharpeRatio > 1}
      />
      
      <MetricCard
        label="Max Drawdown"
        value={formatPercentage(metrics.maxDrawdown)}
        description="Peak to trough"
        positive={false}
        variant="warning"
      />
    </div>
  );
}

interface MetricCardProps {
  label: string;
  value: string;
  change?: string;
  subValue?: string;
  description?: string;
  positive?: boolean;
  variant?: 'default' | 'warning';
}

function MetricCard({
  label,
  value,
  change,
  subValue,
  description,
  positive = true,
  variant = 'default',
}: MetricCardProps) {
  const colorClass = variant === 'warning' 
    ? 'text-orange-400' 
    : positive 
    ? 'text-green-400' 
    : 'text-red-400';
    
  return (
    <Card>
      <CardBody className="space-y-2">
        <p className="text-sm text-neutral-400">{label}</p>
        <p className={`text-2xl font-bold ${colorClass}`}>
          {value}
        </p>
        {(change || subValue) && (
          <div className="flex items-center gap-2 text-sm">
            {change && <span className={colorClass}>{change}</span>}
            {subValue && <span className="text-neutral-400">{subValue}</span>}
          </div>
        )}
        {description && (
          <p className="text-xs text-neutral-500">{description}</p>
        )}
      </CardBody>
    </Card>
  );
}