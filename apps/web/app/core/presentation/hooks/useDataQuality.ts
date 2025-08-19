import { useState, useEffect, useCallback } from 'react';
import { DataQuality } from '../../domain/entities/DataQuality';
import { AssessDataQualityUseCase } from '../../domain/usecases/AssessDataQualityUseCase';
import { DataQualityRepository } from '../../infrastructure/repositories/DataQualityRepository';

interface UseDataQualityOptions {
  expectedAssets?: number;
  refreshInterval?: number;
  autoRefresh?: boolean;
}

interface UseDataQualityResult {
  quality: DataQuality | null;
  recommendations: string[];
  requiresRefresh: boolean;
  isLoading: boolean;
  isRefreshing: boolean;
  error: Error | null;
  assess: () => Promise<void>;
  triggerRefresh: () => Promise<void>;
}

export function useDataQuality(options: UseDataQualityOptions = {}): UseDataQualityResult {
  const { 
    expectedAssets = 50, 
    refreshInterval = 300000, // 5 minutes
    autoRefresh = true 
  } = options;
  
  const [quality, setQuality] = useState<DataQuality | null>(null);
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const [requiresRefresh, setRequiresRefresh] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Create use case instance (in production, use dependency injection)
  const repository = new DataQualityRepository();
  const useCase = new AssessDataQualityUseCase(repository);

  const assessQuality = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await useCase.execute({ expectedAssets });
      
      setQuality(response.quality);
      setRecommendations(response.recommendations);
      setRequiresRefresh(response.requiresRefresh);
    } catch (err) {
      setError(err as Error);
      setRecommendations(['Failed to assess data quality']);
      setRequiresRefresh(true);
    } finally {
      setIsLoading(false);
    }
  }, [expectedAssets]);

  const triggerRefresh = useCallback(async () => {
    try {
      setIsRefreshing(true);
      await repository.triggerDataRefresh({ force: true, mode: 'full' });
      
      // Wait a bit then reassess
      setTimeout(assessQuality, 2000);
    } catch (err) {
      setError(err as Error);
    } finally {
      setIsRefreshing(false);
    }
  }, [assessQuality]);

  useEffect(() => {
    assessQuality();
    
    if (autoRefresh) {
      const interval = setInterval(assessQuality, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [assessQuality, refreshInterval, autoRefresh]);

  return {
    quality,
    recommendations,
    requiresRefresh,
    isLoading,
    isRefreshing,
    error,
    assess: assessQuality,
    triggerRefresh
  };
}