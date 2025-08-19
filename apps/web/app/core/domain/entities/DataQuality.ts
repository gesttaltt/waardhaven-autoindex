// Domain Entity for Data Quality
export interface DataQuality {
  freshness: FreshnessMetric;
  completeness: CompletenessMetric;
  accuracy: AccuracyMetric;
  coverage: CoverageMetric;
  overallScore: number;
  assessment: QualityAssessment;
}

export interface FreshnessMetric {
  score: number;
  daysOld: number;
  lastUpdate: string;
  status: FreshnessStatus;
}

export interface CompletenessMetric {
  score: number;
  missingAssets: number;
  totalAssets: number;
  status: CompletenessStatus;
}

export interface AccuracyMetric {
  score: number;
  errorRate: number;
  validationsPassed: number;
  totalValidations: number;
  status: AccuracyStatus;
}

export interface CoverageMetric {
  score: number;
  hasBenchmark: boolean;
  sectors: number;
  regions: number;
  status: CoverageStatus;
}

export enum FreshnessStatus {
  EXCELLENT = 'excellent',
  GOOD = 'good',
  STALE = 'stale',
  CRITICAL = 'critical'
}

export enum CompletenessStatus {
  COMPLETE = 'complete',
  PARTIAL = 'partial',
  INCOMPLETE = 'incomplete'
}

export enum AccuracyStatus {
  ACCURATE = 'accurate',
  MINOR_ISSUES = 'minor_issues',
  MAJOR_ISSUES = 'major_issues'
}

export enum CoverageStatus {
  FULL = 'full',
  PARTIAL = 'partial',
  LIMITED = 'limited'
}

export enum QualityAssessment {
  EXCELLENT = 'excellent',
  GOOD = 'good',
  FAIR = 'fair',
  POOR = 'poor'
}

// Business rules for data quality assessment
export class DataQualityCalculator {
  static calculateFreshnessScore(daysOld: number): number {
    return Math.max(0, 100 - (daysOld * 20));
  }

  static assessFreshness(daysOld: number): FreshnessStatus {
    if (daysOld <= 1) return FreshnessStatus.EXCELLENT;
    if (daysOld <= 2) return FreshnessStatus.GOOD;
    if (daysOld <= 7) return FreshnessStatus.STALE;
    return FreshnessStatus.CRITICAL;
  }

  static calculateCompletenessScore(actual: number, expected: number): number {
    if (expected === 0) return 0;
    return Math.min(100, (actual / expected) * 100);
  }

  static assessCompleteness(score: number): CompletenessStatus {
    if (score >= 95) return CompletenessStatus.COMPLETE;
    if (score >= 80) return CompletenessStatus.PARTIAL;
    return CompletenessStatus.INCOMPLETE;
  }

  static calculateAccuracyScore(errorRate: number): number {
    return Math.max(0, 100 - (errorRate * 2000));
  }

  static assessAccuracy(errorRate: number): AccuracyStatus {
    if (errorRate <= 0.01) return AccuracyStatus.ACCURATE;
    if (errorRate <= 0.03) return AccuracyStatus.MINOR_ISSUES;
    return AccuracyStatus.MAJOR_ISSUES;
  }

  static calculateCoverageScore(
    hasBenchmark: boolean,
    sectors: number,
    regions: number
  ): number {
    const benchmarkScore = hasBenchmark ? 40 : 0;
    const sectorScore = Math.min(40, sectors * 5);
    const regionScore = Math.min(20, regions * 4);
    return benchmarkScore + sectorScore + regionScore;
  }

  static assessCoverage(score: number): CoverageStatus {
    if (score >= 90) return CoverageStatus.FULL;
    if (score >= 70) return CoverageStatus.PARTIAL;
    return CoverageStatus.LIMITED;
  }

  static calculateOverallScore(
    freshness: number,
    completeness: number,
    accuracy: number,
    coverage: number
  ): number {
    return Math.round((freshness + completeness + accuracy + coverage) / 4);
  }

  static assessOverallQuality(score: number): QualityAssessment {
    if (score >= 90) return QualityAssessment.EXCELLENT;
    if (score >= 75) return QualityAssessment.GOOD;
    if (score >= 60) return QualityAssessment.FAIR;
    return QualityAssessment.POOR;
  }
}