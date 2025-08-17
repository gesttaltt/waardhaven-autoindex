import { useState, useEffect, useCallback } from 'react';

interface ApiCallState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

interface UseApiCallOptions {
  immediate?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
}

export function useApiCall<T>(
  apiCall: () => Promise<T>,
  options: UseApiCallOptions = {}
) {
  const { immediate = true, onSuccess, onError } = options;
  
  const [state, setState] = useState<ApiCallState<T>>({
    data: null,
    loading: immediate,
    error: null,
  });

  const execute = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const data = await apiCall();
      setState({ data, loading: false, error: null });
      onSuccess?.(data);
      return data;
    } catch (error) {
      const err = error as Error;
      setState({ data: null, loading: false, error: err });
      onError?.(err);
      throw err;
    }
  }, [apiCall, onSuccess, onError]);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [immediate]);

  const refetch = useCallback(() => {
    return execute();
  }, [execute]);

  return {
    ...state,
    refetch,
    execute,
  };
}