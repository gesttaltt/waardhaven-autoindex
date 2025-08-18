# Error Handling

## Overview

Comprehensive error handling ensures a robust user experience by gracefully managing failures at every level of the application stack.

## Error Handling Architecture

```
┌─────────────────────────────────────────┐
│         User Interface                  │
│      (Error Boundaries, Toast)          │
├─────────────────────────────────────────┤
│        Component Level                  │
│      (try/catch, Error States)          │
├─────────────────────────────────────────┤
│         Service Level                   │
│      (API Error Handling)               │
├─────────────────────────────────────────┤
│        Network Level                    │
│      (Interceptors, Retry)              │
└─────────────────────────────────────────┘
```

## Error Types

### Application Error Types

```typescript
// types/errors.ts
export enum ErrorCode {
  // Authentication Errors
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  TOKEN_EXPIRED = 'TOKEN_EXPIRED',
  INVALID_CREDENTIALS = 'INVALID_CREDENTIALS',
  
  // Validation Errors
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  INVALID_INPUT = 'INVALID_INPUT',
  MISSING_REQUIRED_FIELD = 'MISSING_REQUIRED_FIELD',
  
  // Business Logic Errors
  INSUFFICIENT_FUNDS = 'INSUFFICIENT_FUNDS',
  PORTFOLIO_LOCKED = 'PORTFOLIO_LOCKED',
  REBALANCE_IN_PROGRESS = 'REBALANCE_IN_PROGRESS',
  
  // System Errors
  NETWORK_ERROR = 'NETWORK_ERROR',
  SERVER_ERROR = 'SERVER_ERROR',
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',
  TIMEOUT = 'TIMEOUT',
  
  // Client Errors
  NOT_FOUND = 'NOT_FOUND',
  CONFLICT = 'CONFLICT',
  RATE_LIMITED = 'RATE_LIMITED',
}

export class AppError extends Error {
  constructor(
    public code: ErrorCode,
    message: string,
    public statusCode?: number,
    public details?: any
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export class ValidationError extends AppError {
  constructor(
    message: string,
    public fields: Record<string, string>
  ) {
    super(ErrorCode.VALIDATION_ERROR, message, 400, fields);
  }
}

export class AuthenticationError extends AppError {
  constructor(message: string = 'Authentication required') {
    super(ErrorCode.UNAUTHORIZED, message, 401);
  }
}

export class NetworkError extends AppError {
  constructor(message: string = 'Network request failed') {
    super(ErrorCode.NETWORK_ERROR, message);
  }
}
```

## Error Boundaries

### Global Error Boundary

```typescript
// components/ErrorBoundary.tsx
interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<
  { children: ReactNode; fallback?: ComponentType<any> },
  ErrorBoundaryState
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error, errorInfo: null };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log to error reporting service
    console.error('Error caught by boundary:', error, errorInfo);
    
    // Send to monitoring service
    if (typeof window !== 'undefined') {
      this.logErrorToService(error, errorInfo);
    }
    
    this.setState({ error, errorInfo });
  }

  logErrorToService(error: Error, errorInfo: ErrorInfo) {
    // Send to Sentry, LogRocket, etc.
    if (window.Sentry) {
      window.Sentry.captureException(error, {
        contexts: {
          react: {
            componentStack: errorInfo.componentStack,
          },
        },
      });
    }
  }

  render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback;
      return (
        <FallbackComponent
          error={this.state.error}
          resetError={() => this.setState({ hasError: false, error: null })}
        />
      );
    }

    return this.props.children;
  }
}

// Default error fallback
const DefaultErrorFallback: React.FC<{
  error: Error | null;
  resetError: () => void;
}> = ({ error, resetError }) => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50">
    <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
      <div className="text-center">
        <div className="text-6xl mb-4">⚠️</div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Oops! Something went wrong
        </h1>
        <p className="text-gray-600 mb-4">
          {error?.message || 'An unexpected error occurred'}
        </p>
        <div className="space-y-2">
          <button
            onClick={resetError}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Try Again
          </button>
          <button
            onClick={() => window.location.href = '/'}
            className="w-full px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
          >
            Go Home
          </button>
        </div>
        {process.env.NODE_ENV === 'development' && error && (
          <details className="mt-4 text-left">
            <summary className="cursor-pointer text-sm text-gray-500">
              Error Details
            </summary>
            <pre className="mt-2 text-xs bg-gray-100 p-2 rounded overflow-auto">
              {error.stack}
            </pre>
          </details>
        )}
      </div>
    </div>
  </div>
);
```

### Async Error Boundary

```typescript
// components/AsyncErrorBoundary.tsx
export const AsyncErrorBoundary: React.FC<{ children: ReactNode }> = ({ 
  children 
}) => {
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      setError(new Error(event.reason));
    };

    window.addEventListener('unhandledrejection', handleUnhandledRejection);
    return () => {
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, []);

  if (error) {
    return <ErrorFallback error={error} onReset={() => setError(null)} />;
  }

  return <>{children}</>;
};
```

## API Error Handling

### Service Layer Error Handling

```typescript
// services/api/base.ts
export class ApiService {
  protected async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error = await this.parseErrorResponse(response);
      throw error;
    }
    
    return this.parseSuccessResponse<T>(response);
  }

  private async parseErrorResponse(response: Response): Promise<AppError> {
    let errorData: any = {};
    
    try {
      errorData = await response.json();
    } catch {
      // Response might not be JSON
    }

    // Map HTTP status to error codes
    switch (response.status) {
      case 400:
        return new ValidationError(
          errorData.detail || 'Invalid request',
          errorData.errors || {}
        );
      
      case 401:
        return new AuthenticationError(errorData.detail);
      
      case 403:
        return new AppError(
          ErrorCode.FORBIDDEN,
          errorData.detail || 'Access denied',
          403
        );
      
      case 404:
        return new AppError(
          ErrorCode.NOT_FOUND,
          errorData.detail || 'Resource not found',
          404
        );
      
      case 429:
        return new AppError(
          ErrorCode.RATE_LIMITED,
          errorData.detail || 'Too many requests',
          429,
          { retryAfter: response.headers.get('Retry-After') }
        );
      
      case 500:
      case 502:
      case 503:
        return new AppError(
          ErrorCode.SERVER_ERROR,
          errorData.detail || 'Server error',
          response.status
        );
      
      default:
        return new AppError(
          ErrorCode.NETWORK_ERROR,
          errorData.detail || `Request failed with status ${response.status}`,
          response.status
        );
    }
  }
}
```

### Error Interceptors

```typescript
// infrastructure/api/errorInterceptor.ts
export const errorInterceptor: Interceptor<Response> = {
  onError: async (error: HttpError) => {
    // Log error
    console.error('API Error:', error);
    
    // Handle specific error codes
    switch (error.status) {
      case 401:
        // Token expired - try refresh
        const refreshed = await tryRefreshToken();
        if (!refreshed) {
          // Redirect to login
          window.location.href = '/login';
        }
        break;
      
      case 403:
        // Show permission denied message
        showToast('You do not have permission to perform this action', 'error');
        break;
      
      case 429:
        // Rate limited - show message and retry after delay
        const retryAfter = error.details?.retryAfter || 60;
        showToast(`Rate limited. Please try again in ${retryAfter} seconds`, 'warning');
        break;
      
      case 500:
      case 502:
      case 503:
        // Server error - show generic message
        showToast('Server error. Please try again later', 'error');
        break;
    }
    
    throw error;
  }
};
```

## Component Error Handling

### Error States in Components

```typescript
// components/DataDisplay.tsx
const DataDisplay: React.FC = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    loadData()
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorDisplay error={error} onRetry={() => window.location.reload()} />;
  }

  if (!data) {
    return <EmptyState message="No data available" />;
  }

  return <DataView data={data} />;
};

// Error display component
const ErrorDisplay: React.FC<{
  error: Error;
  onRetry?: () => void;
}> = ({ error, onRetry }) => {
  const errorMessage = getErrorMessage(error);
  const errorIcon = getErrorIcon(error);

  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div className="text-6xl mb-4">{errorIcon}</div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        {errorMessage.title}
      </h3>
      <p className="text-gray-600 text-center max-w-md mb-4">
        {errorMessage.description}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Try Again
        </button>
      )}
    </div>
  );
};
```

### Form Error Handling

```typescript
// components/FormWithValidation.tsx
const FormWithValidation: React.FC = () => {
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [generalError, setGeneralError] = useState<string | null>(null);

  const handleSubmit = async (values: FormValues) => {
    try {
      setErrors({});
      setGeneralError(null);
      
      // Validate
      const validationErrors = validate(values);
      if (Object.keys(validationErrors).length > 0) {
        setErrors(validationErrors);
        return;
      }
      
      // Submit
      await submitForm(values);
    } catch (error) {
      if (error instanceof ValidationError) {
        setErrors(error.fields);
      } else if (error instanceof AppError) {
        setGeneralError(error.message);
      } else {
        setGeneralError('An unexpected error occurred');
      }
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {generalError && (
        <Alert variant="error" onClose={() => setGeneralError(null)}>
          {generalError}
        </Alert>
      )}
      
      <FormField
        name="email"
        error={errors.email}
        onChange={() => setErrors(prev => ({ ...prev, email: '' }))}
      />
      
      <FormField
        name="password"
        error={errors.password}
        onChange={() => setErrors(prev => ({ ...prev, password: '' }))}
      />
      
      <button type="submit">Submit</button>
    </form>
  );
};
```

## Toast Notifications

```typescript
// contexts/ToastContext.tsx
interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
}

const ToastContext = createContext<{
  showToast: (message: string, type?: Toast['type'], duration?: number) => void;
  hideToast: (id: string) => void;
}>({
  showToast: () => {},
  hideToast: () => {},
});

export const ToastProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = (
    message: string,
    type: Toast['type'] = 'info',
    duration = 5000
  ) => {
    const id = Date.now().toString();
    const toast: Toast = { id, message, type, duration };
    
    setToasts(prev => [...prev, toast]);
    
    if (duration > 0) {
      setTimeout(() => hideToast(id), duration);
    }
  };

  const hideToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  return (
    <ToastContext.Provider value={{ showToast, hideToast }}>
      {children}
      <ToastContainer toasts={toasts} onClose={hideToast} />
    </ToastContext.Provider>
  );
};

// Toast container component
const ToastContainer: React.FC<{
  toasts: Toast[];
  onClose: (id: string) => void;
}> = ({ toasts, onClose }) => {
  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      <AnimatePresence>
        {toasts.map(toast => (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 100 }}
            className={`
              px-4 py-3 rounded-lg shadow-lg flex items-center space-x-2
              ${getToastStyles(toast.type)}
            `}
          >
            <span>{getToastIcon(toast.type)}</span>
            <span>{toast.message}</span>
            <button
              onClick={() => onClose(toast.id)}
              className="ml-4 text-white hover:opacity-75"
            >
              ✕
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};
```

## Retry Logic

### Exponential Backoff

```typescript
// utils/retry.ts
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: {
    maxAttempts?: number;
    initialDelay?: number;
    maxDelay?: number;
    factor?: number;
    shouldRetry?: (error: any) => boolean;
  } = {}
): Promise<T> {
  const {
    maxAttempts = 3,
    initialDelay = 1000,
    maxDelay = 30000,
    factor = 2,
    shouldRetry = () => true,
  } = options;

  let attempt = 0;
  let delay = initialDelay;

  while (attempt < maxAttempts) {
    try {
      return await fn();
    } catch (error) {
      attempt++;
      
      if (attempt >= maxAttempts || !shouldRetry(error)) {
        throw error;
      }
      
      console.log(`Retry attempt ${attempt}/${maxAttempts} after ${delay}ms`);
      await new Promise(resolve => setTimeout(resolve, delay));
      
      delay = Math.min(delay * factor, maxDelay);
    }
  }

  throw new Error('Max retry attempts reached');
}

// Usage
const data = await retryWithBackoff(
  () => fetchData(),
  {
    maxAttempts: 3,
    shouldRetry: (error) => error.status >= 500,
  }
);
```

## Error Logging

### Client-Side Logging

```typescript
// services/errorLogger.ts
class ErrorLogger {
  private queue: ErrorLog[] = [];
  private flushTimer: NodeJS.Timeout | null = null;

  log(error: Error, context?: any) {
    const errorLog: ErrorLog = {
      message: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString(),
      context,
      userAgent: navigator.userAgent,
      url: window.location.href,
    };

    this.queue.push(errorLog);
    this.scheduleFlush();
  }

  private scheduleFlush() {
    if (this.flushTimer) return;
    
    this.flushTimer = setTimeout(() => {
      this.flush();
      this.flushTimer = null;
    }, 1000);
  }

  private async flush() {
    if (this.queue.length === 0) return;
    
    const logs = [...this.queue];
    this.queue = [];
    
    try {
      await fetch('/api/logs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ logs }),
      });
    } catch (error) {
      // Re-add logs to queue if sending fails
      this.queue.unshift(...logs);
    }
  }
}

export const errorLogger = new ErrorLogger();
```

## Error Recovery

### Fallback UI

```typescript
// components/FallbackUI.tsx
const FallbackUI: React.FC<{
  error: Error;
  resetError: () => void;
  suggestion?: string;
}> = ({ error, resetError, suggestion }) => {
  const isNetworkError = error instanceof NetworkError;
  const isAuthError = error instanceof AuthenticationError;

  if (isNetworkError) {
    return (
      <NetworkErrorFallback
        onRetry={resetError}
        message="Unable to connect to our servers"
      />
    );
  }

  if (isAuthError) {
    return (
      <AuthErrorFallback
        message="Your session has expired"
        onLogin={() => window.location.href = '/login'}
      />
    );
  }

  return (
    <GenericErrorFallback
      error={error}
      onRetry={resetError}
      suggestion={suggestion}
    />
  );
};
```

## Testing Error Handling

```typescript
// __tests__/errorHandling.test.tsx
describe('Error Handling', () => {
  it('should display error boundary on component error', () => {
    const ThrowError = () => {
      throw new Error('Test error');
    };

    const { getByText } = render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    expect(getByText(/something went wrong/i)).toBeInTheDocument();
  });

  it('should retry failed API calls', async () => {
    const mockFetch = jest.fn()
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce({ data: 'success' });

    const result = await retryWithBackoff(mockFetch, { maxAttempts: 2 });
    
    expect(mockFetch).toHaveBeenCalledTimes(2);
    expect(result).toEqual({ data: 'success' });
  });
});
```

## Best Practices

1. **Always handle async errors** - Use try/catch or .catch()
2. **Provide meaningful error messages** - Help users understand what went wrong
3. **Log errors for debugging** - But don't expose sensitive information
4. **Implement retry logic** - For transient failures
5. **Use error boundaries** - Prevent entire app crashes
6. **Show loading states** - Don't leave users wondering
7. **Provide recovery options** - Let users retry or navigate away
8. **Test error scenarios** - Ensure error handling works correctly

## Next Steps

- Review [Testing Guide](./09-testing-guide.md)
- Learn about [Performance Optimization](./11-performance-optimization.md)
- Understand [Security Best Practices](./12-security-best-practices.md)