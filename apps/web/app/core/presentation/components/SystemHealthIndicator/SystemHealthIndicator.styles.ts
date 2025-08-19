import { HealthStatus } from '../../../domain/entities/SystemHealth';

export const healthStatusStyles = {
  [HealthStatus.HEALTHY]: {
    text: 'text-green-400',
    bg: 'bg-green-500/10',
    border: 'border-green-500/30',
    icon: '●'
  },
  [HealthStatus.WARNING]: {
    text: 'text-yellow-400',
    bg: 'bg-yellow-500/10',
    border: 'border-yellow-500/30',
    icon: '◐'
  },
  [HealthStatus.ERROR]: {
    text: 'text-red-400',
    bg: 'bg-red-500/10',
    border: 'border-red-500/30',
    icon: '●'
  },
  [HealthStatus.UNKNOWN]: {
    text: 'text-gray-400',
    bg: 'bg-gray-500/10',
    border: 'border-gray-500/30',
    icon: '○'
  }
};

export const containerStyles = {
  base: 'relative',
  button: 'w-full p-3 rounded-lg border backdrop-blur-sm transition-all hover:shadow-lg',
  loading: 'p-3 bg-gray-800/50 rounded-lg border border-gray-700 animate-pulse'
};

export const headerStyles = {
  container: 'flex items-center justify-between',
  titleGroup: 'flex items-center gap-3',
  icon: 'text-lg',
  textGroup: 'text-left',
  title: 'text-sm font-medium text-white',
  subtitle: 'text-xs text-gray-400',
  timestamp: 'text-xs text-gray-500',
  chevron: 'text-gray-400 text-sm'
};

export const detailsStyles = {
  container: 'absolute top-full left-0 right-0 z-50 mt-2 p-4 bg-gray-900/95 backdrop-blur-sm rounded-lg border border-gray-700 shadow-xl',
  section: 'space-y-4',
  metric: {
    row: 'flex justify-between items-center',
    label: 'text-sm font-medium text-white',
    sublabel: 'text-xs text-gray-400',
    value: 'text-sm',
    status: 'text-right'
  },
  actions: {
    container: 'pt-2 border-t border-gray-700',
    buttonGroup: 'flex gap-2',
    button: 'flex-1 px-3 py-1 text-xs rounded transition-colors',
    refreshButton: 'bg-purple-600/20 hover:bg-purple-600/30 text-purple-300',
    detailsButton: 'bg-blue-600/20 hover:bg-blue-600/30 text-blue-300'
  }
};

export const loadingSkeletonStyles = {
  container: 'flex items-center gap-2',
  dot: 'w-3 h-3 bg-gray-600 rounded-full',
  bar: 'h-4 bg-gray-600 rounded w-20'
};