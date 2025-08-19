import { useState, useEffect, useCallback } from 'react';
import { SystemHealth } from '../../domain/entities/SystemHealth';
import { MonitorSystemHealthUseCase } from '../../domain/usecases/MonitorSystemHealthUseCase';
import { SystemHealthRepository } from '../../infrastructure/repositories/SystemHealthRepository';

interface UseSystemHealthOptions {
  refreshInterval?: number;
  autoRefresh?: boolean;
}

interface UseSystemHealthResult {
  health: SystemHealth | null;
  isLoading: boolean;
  error: Error | null;
  message: string;
  requiresAction: boolean;
  refresh: () => Promise<void>;
}

export function useSystemHealth(options: UseSystemHealthOptions = {}): UseSystemHealthResult {
  const { refreshInterval = 60000, autoRefresh = true } = options;
  
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [message, setMessage] = useState('');
  const [requiresAction, setRequiresAction] = useState(false);

  // Create use case instance (in production, use dependency injection)
  const repository = new SystemHealthRepository();
  const useCase = new MonitorSystemHealthUseCase(repository);

  const checkHealth = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await useCase.execute({ includeDetails: true });
      
      setHealth(response.health);
      setMessage(response.message);
      setRequiresAction(response.requiresAction);
    } catch (err) {
      setError(err as Error);
      setMessage('Failed to check system health');
      setRequiresAction(true);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
    
    if (autoRefresh) {
      const interval = setInterval(checkHealth, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [checkHealth, refreshInterval, autoRefresh]);

  return {
    health,
    isLoading,
    error,
    message,
    requiresAction,
    refresh: checkHealth
  };
}