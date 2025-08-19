export const scoreColors = {
  excellent: 'text-green-400',
  good: 'text-yellow-400',
  fair: 'text-orange-400',
  poor: 'text-red-400'
};

export const getScoreColor = (score: number): string => {
  if (score >= 90) return scoreColors.excellent;
  if (score >= 70) return scoreColors.good;
  if (score >= 50) return scoreColors.fair;
  return scoreColors.poor;
};

export const containerStyles = {
  base: 'p-4 bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700',
  loading: 'p-4 bg-gray-800/50 rounded-xl border border-gray-700 animate-pulse'
};

export const headerStyles = {
  container: 'flex items-center justify-between mb-4',
  titleGroup: 'div',
  title: 'text-lg font-semibold text-white',
  subtitle: 'text-sm text-gray-400',
  scoreGroup: 'text-right',
  scoreValue: 'text-2xl font-bold',
  scoreLabel: 'text-xs text-gray-500'
};

export const metricStyles = {
  container: 'space-y-3 mb-4',
  row: 'flex items-center justify-between p-2 bg-white/5 rounded-lg',
  labelGroup: 'flex items-center gap-2',
  icon: 'text-sm',
  label: 'text-sm font-medium text-white',
  sublabel: 'text-xs text-gray-400',
  score: 'text-sm font-medium'
};

export const actionStyles = {
  container: 'flex gap-2 pt-3 border-t border-gray-700',
  refreshButton: {
    base: 'flex-1 px-3 py-2 text-sm rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed',
    critical: 'bg-red-600/20 hover:bg-red-600/30 text-red-300 border border-red-500/30',
    warning: 'bg-yellow-600/20 hover:bg-yellow-600/30 text-yellow-300 border border-yellow-500/30',
    normal: 'bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 border border-purple-500/30'
  },
  assessButton: 'px-3 py-2 text-sm bg-gray-600/20 hover:bg-gray-600/30 text-gray-300 rounded-lg transition-all'
};

export const warningStyles = {
  container: 'mt-3 p-2 bg-red-500/10 border border-red-500/30 rounded-lg',
  text: 'text-xs text-red-300'
};

export const loadingSkeletonStyles = {
  header: 'flex items-center justify-between mb-3',
  title: 'h-5 bg-gray-600 rounded w-32',
  score: 'h-8 bg-gray-600 rounded w-16',
  metrics: 'space-y-2',
  metricBar: 'h-3 bg-gray-600 rounded',
  metricBar75: 'h-3 bg-gray-600 rounded w-3/4'
};