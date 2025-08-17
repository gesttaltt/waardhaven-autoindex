'use client';

import { cn } from '../../../lib/utils';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  animation?: 'pulse' | 'wave' | 'none';
}

export function Skeleton({
  className,
  variant = 'text',
  width,
  height,
  animation = 'pulse',
}: SkeletonProps) {
  const baseStyles = 'bg-white/10';
  
  const animationStyles = {
    pulse: 'animate-pulse',
    wave: 'animate-shimmer',
    none: '',
  };
  
  const variantStyles = {
    text: 'rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
  };
  
  const style: React.CSSProperties = {
    width: width || (variant === 'circular' ? 40 : '100%'),
    height: height || (variant === 'text' ? 20 : variant === 'circular' ? 40 : 60),
  };
  
  return (
    <div
      className={cn(
        baseStyles,
        animationStyles[animation],
        variantStyles[variant],
        className
      )}
      style={style}
      aria-label="Loading..."
      role="status"
    />
  );
}

export function SkeletonCard({ lines = 3 }: { lines?: number }) {
  return (
    <div className="bg-white/5 rounded-xl p-6 border border-white/10">
      <Skeleton variant="text" height={24} width="60%" className="mb-4" />
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton key={i} variant="text" className="mb-2" />
      ))}
    </div>
  );
}

export function SkeletonChart() {
  return (
    <div className="bg-white/5 rounded-xl p-6 border border-white/10">
      <div className="flex justify-between items-center mb-4">
        <Skeleton variant="text" height={24} width={200} />
        <Skeleton variant="rectangular" height={32} width={100} />
      </div>
      <Skeleton variant="rectangular" height={400} className="w-full" />
    </div>
  );
}