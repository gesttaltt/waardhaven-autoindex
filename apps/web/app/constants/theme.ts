// Theme constants and color palette

export const CHART_COLORS = [
  '#8b5cf6', // Purple
  '#ec4899', // Pink
  '#3b82f6', // Blue
  '#10b981', // Green
  '#f59e0b', // Orange
  '#ef4444', // Red
  '#06b6d4', // Cyan
  '#a855f7', // Violet
] as const;

export const THEME = {
  colors: {
    primary: '#8b5cf6',
    secondary: '#ec4899',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#3b82f6',
    neutral: {
      50: '#fafafa',
      100: '#f5f5f5',
      200: '#e5e5e5',
      300: '#d4d4d4',
      400: '#a3a3a3',
      500: '#737373',
      600: '#525252',
      700: '#404040',
      800: '#262626',
      900: '#171717',
    },
  },
  gradients: {
    primary: 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)',
    chart: 'linear-gradient(180deg, rgba(139, 92, 246, 0.8) 0%, rgba(139, 92, 246, 0.1) 100%)',
    chartSecondary: 'linear-gradient(180deg, rgba(236, 72, 153, 0.6) 0%, rgba(236, 72, 153, 0.1) 100%)',
  },
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
  animation: {
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '500ms',
    },
    easing: {
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
      easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    },
  },
} as const;

export const CHART_TOOLTIP_STYLE = {
  backgroundColor: 'rgba(0,0,0,0.9)',
  border: '1px solid rgba(139,92,246,0.3)',
  borderRadius: '12px',
  backdropFilter: 'blur(20px)',
  boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
  color: '#ffffff',
} as const;

export const CHART_AXIS_STYLE = {
  stroke: 'rgba(255,255,255,0.5)',
  fontSize: 12,
} as const;