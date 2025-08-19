import { SystemHealth, HealthStatus } from '../../../domain/entities/SystemHealth';

export interface SystemHealthIndicatorProps {
  className?: string;
  showDetails?: boolean;
  refreshInterval?: number;
}

export interface SystemHealthDisplayProps {
  health: SystemHealth | null;
  message: string;
  requiresAction: boolean;
  isLoading: boolean;
  expanded: boolean;
  lastUpdate: Date;
  onToggleExpanded: () => void;
  onRefresh: () => void;
  onNavigateToDiagnostics: () => void;
}

export interface HealthStatusBadgeProps {
  status: HealthStatus;
  size?: 'sm' | 'md' | 'lg';
}

export interface HealthMetricProps {
  label: string;
  value: string | number;
  status: HealthStatus;
  detail?: string;
}