"use client";

import { motion } from 'framer-motion';

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
  const baseClasses = 'skeleton';
  
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
      className={`${baseClasses} ${variantClasses[variant]} ${animationClasses[animation]} ${className}`}
      style={style}
    />
  );
}

interface LoadingCardProps {
  lines?: number;
  showImage?: boolean;
}

export function LoadingCard({ lines = 3, showImage = false }: LoadingCardProps) {
  return (
    <div className="card">
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
      className="card"
    >
      <div className="flex justify-between items-center mb-4">
        <LoadingSkeleton height={24} width={200} />
        <LoadingSkeleton height={32} width={100} />
      </div>
      <LoadingSkeleton height={400} />
    </motion.div>
  );
}