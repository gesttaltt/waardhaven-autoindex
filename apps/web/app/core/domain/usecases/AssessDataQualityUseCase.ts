import { DataQuality, DataQualityCalculator } from '../entities/DataQuality';
import { IDataQualityRepository } from '../repositories/IDataQualityRepository';

export interface AssessDataQualityRequest {
  expectedAssets?: number;
}

export interface AssessDataQualityResponse {
  quality: DataQuality;
  recommendations: string[];
  requiresRefresh: boolean;
}

export class AssessDataQualityUseCase {
  constructor(
    private readonly dataQualityRepository: IDataQualityRepository
  ) {}

  async execute(request: AssessDataQualityRequest): Promise<AssessDataQualityResponse> {
    const expectedAssets = request.expectedAssets || 50;
    
    // Fetch raw data from repository
    const rawData = await this.dataQualityRepository.getRawQualityData();
    
    // Calculate freshness metrics
    const freshnessScore = DataQualityCalculator.calculateFreshnessScore(rawData.daysOld);
    const freshnessStatus = DataQualityCalculator.assessFreshness(rawData.daysOld);
    
    // Calculate completeness metrics
    const completenessScore = DataQualityCalculator.calculateCompletenessScore(
      rawData.totalAssets,
      expectedAssets
    );
    const completenessStatus = DataQualityCalculator.assessCompleteness(completenessScore);
    const missingAssets = Math.max(0, expectedAssets - rawData.totalAssets);
    
    // Calculate accuracy metrics
    const accuracyScore = DataQualityCalculator.calculateAccuracyScore(rawData.errorRate);
    const accuracyStatus = DataQualityCalculator.assessAccuracy(rawData.errorRate);
    
    // Calculate coverage metrics
    const coverageScore = DataQualityCalculator.calculateCoverageScore(
      rawData.hasBenchmark,
      rawData.sectors,
      rawData.regions
    );
    const coverageStatus = DataQualityCalculator.assessCoverage(coverageScore);
    
    // Calculate overall score
    const overallScore = DataQualityCalculator.calculateOverallScore(
      freshnessScore,
      completenessScore,
      accuracyScore,
      coverageScore
    );
    
    const assessment = DataQualityCalculator.assessOverallQuality(overallScore);
    
    // Build quality object
    const quality: DataQuality = {
      freshness: {
        score: freshnessScore,
        daysOld: rawData.daysOld,
        lastUpdate: rawData.lastUpdate,
        status: freshnessStatus
      },
      completeness: {
        score: completenessScore,
        missingAssets,
        totalAssets: rawData.totalAssets,
        status: completenessStatus
      },
      accuracy: {
        score: accuracyScore,
        errorRate: rawData.errorRate * 100,
        validationsPassed: rawData.validationsPassed,
        totalValidations: rawData.totalValidations,
        status: accuracyStatus
      },
      coverage: {
        score: coverageScore,
        hasBenchmark: rawData.hasBenchmark,
        sectors: rawData.sectors,
        regions: rawData.regions,
        status: coverageStatus
      },
      overallScore,
      assessment
    };
    
    // Generate recommendations
    const recommendations = this.generateRecommendations(quality);
    
    // Determine if refresh is needed
    const requiresRefresh = freshnessStatus === 'critical' || 
                           completenessStatus === 'incomplete' ||
                           overallScore < 60;
    
    return {
      quality,
      recommendations,
      requiresRefresh
    };
  }
  
  private generateRecommendations(quality: DataQuality): string[] {
    const recommendations: string[] = [];
    
    if (quality.freshness.status === 'critical' || quality.freshness.status === 'stale') {
      recommendations.push('Refresh market data to improve freshness');
    }
    
    if (quality.completeness.missingAssets > 0) {
      recommendations.push(`Add ${quality.completeness.missingAssets} missing assets`);
    }
    
    if (quality.accuracy.errorRate > 3) {
      recommendations.push('Review and fix data accuracy issues');
    }
    
    if (!quality.coverage.hasBenchmark) {
      recommendations.push('Add benchmark data for comparison');
    }
    
    if (quality.coverage.sectors < 5) {
      recommendations.push('Increase sector diversification');
    }
    
    return recommendations;
  }
}