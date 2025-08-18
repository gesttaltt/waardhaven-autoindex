import { useState, useCallback } from 'react';
import { HttpError } from '../../infrastructure/api/HttpClient';

interface UseApiRequestOptions {
  onSuccess?: (data: any) => void;
  onError?: (error: HttpError) => void;
  retryCount?: number;
  retryDelay?: number;
}

interface UseApiRequestResult<T> {
  data: T | null;
  error: HttpError | null;
  isLoading: boolean;
  execute: (...args: any[]) => Promise<T | null>;
  reset: () => void;
}

export function useApiRequest<T>(
  apiFunction: (...args: any[]) => Promise<T>,
  options: UseApiRequestOptions = {}
): UseApiRequestResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<HttpError | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const { onSuccess, onError, retryCount = 0, retryDelay = 1000 } = options;

  const execute = useCallback(
    async (...args: any[]): Promise<T | null> => {
      setIsLoading(true);
      setError(null);

      let attempt = 0;
      let lastError: HttpError | null = null;

      while (attempt <= retryCount) {
        try {
          const result = await apiFunction(...args);
          setData(result);
          onSuccess?.(result);
          setIsLoading(false);
          return result;
        } catch (err) {
          lastError = err as HttpError;
          
          if (attempt < retryCount) {
            await new Promise(resolve => setTimeout(resolve, retryDelay * (attempt + 1)));
            attempt++;
          } else {
            break;
          }
        }
      }

      setError(lastError);
      onError?.(lastError!);
      setIsLoading(false);
      return null;
    },
    [apiFunction, onSuccess, onError, retryCount, retryDelay]
  );

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setIsLoading(false);
  }, []);

  return {
    data,
    error,
    isLoading,
    execute,
    reset
  };
}