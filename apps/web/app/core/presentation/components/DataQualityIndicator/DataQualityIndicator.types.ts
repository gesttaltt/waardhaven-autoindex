import { 
  DataQuality, 
  FreshnessStatus, 
  CompletenessStatus, 
  AccuracyStatus, 
  CoverageStatus,
  QualityAssessment 
} from '../../../domain/entities/DataQuality';

export interface DataQualityIndicatorProps {
  className?: string;
  onRefreshNeeded?: () => void;
  expectedAssets?: number;
  refreshInterval?: number;
}

export interface DataQualityDisplayProps {
  quality: DataQuality | null;
  recommendations: string[];
  requiresRefresh: boolean;
  isLoading: boolean;
  isRefreshing: boolean;
  onRefresh: () => void;
  onAssess: () => void;
}

export interface QualityMetricProps {
  label: string;
  score: number;
  status: string;
  detail: string;
  icon?: string;
}

export interface QualityScoreBadgeProps {
  score: number;
  assessment: QualityAssessment;
}

export interface RefreshButtonProps {
  requiresRefresh: boolean;
  isRefreshing: boolean;
  onClick: () => void;
}