"use client";

import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';

interface LoadingSkeletonProps {
  className?: string;
  height?: string | number;
  width?: string | number;
  variant?: 'text' | 'rectangular' | 'circular';
  animation?: 'pulse' | 'wave';
}

export function LoadingSkeleton({
  className = '',
  height = 'auto',
  width = '100%',
  variant = 'rectangular',
  animation = 'pulse',
}: LoadingSkeletonProps) {
  const baseClasses = 'bg-white/10';
  
  const variantClasses = {
    text: 'rounded',
    rectangular: 'rounded-lg',
    circular: 'rounded-full',
  };

  const animationClasses = {
    pulse: 'animate-pulse',
    wave: 'animate-shimmer',
  };

  const style = {
    height: typeof height === 'number' ? `${height}px` : height,
    width: typeof width === 'number' ? `${width}px` : width,
  };

  return (
    <div
      className={cn(
        baseClasses,
        variantClasses[variant],
        animationClasses[animation],
        className
      )}
      style={style}
      aria-label="Loading..."
      role="status"
    />
  );
}

interface LoadingCardProps {
  lines?: number;
  showImage?: boolean;
}

export function LoadingCard({ lines = 3, showImage = false }: LoadingCardProps) {
  return (
    <div className="bg-white/5 rounded-xl p-6 border border-white/10">
      {showImage && (
        <LoadingSkeleton height={200} className="mb-4" />
      )}
      <LoadingSkeleton height={24} width="60%" className="mb-2" />
      {[...Array(lines)].map((_, i) => (
        <LoadingSkeleton
          key={i}
          height={16}
          width={i === lines - 1 ? "80%" : "100%"}
          className="mb-2"
        />
      ))}
    </div>
  );
}

export function LoadingChart() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-white/5 rounded-xl p-6 border border-white/10"
    >
      <div className="flex justify-between items-center mb-4">
        <LoadingSkeleton height={24} width={200} />
        <LoadingSkeleton height={32} width={100} />
      </div>
      <LoadingSkeleton height={400} />
    </motion.div>
  );
}

// Export additional skeleton components for specific use cases
export function LoadingMetricCard() {
  return (
    <div className="bg-white/5 rounded-xl p-6 border border-white/10">
      <LoadingSkeleton height={16} width="40%" className="mb-2" />
      <LoadingSkeleton height={32} width="60%" className="mb-1" />
      <LoadingSkeleton height={14} width="50%" />
    </div>
  );
}

export function LoadingTableRow() {
  return (
    <div className="flex items-center gap-4 p-4 border-b border-white/10">
      <LoadingSkeleton variant="circular" height={40} width={40} />
      <div className="flex-1">
        <LoadingSkeleton height={16} width="30%" className="mb-1" />
        <LoadingSkeleton height={14} width="20%" />
      </div>
      <LoadingSkeleton height={20} width={80} />
    </div>
  );
}