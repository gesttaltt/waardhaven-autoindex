export interface RequestConfig {
  headers?: Record<string, string>;
  params?: Record<string, any>;
  timeout?: number;
  withCredentials?: boolean;
  signal?: AbortSignal;
}

export interface Response<T = any> {
  data: T;
  status: number;
  statusText: string;
  headers: Headers;
}

export interface HttpError {
  message: string;
  status?: number;
  code?: string;
  details?: any;
}

export interface Interceptor<T> {
  onRequest?: (config: T) => T | Promise<T>;
  onResponse?: <R>(response: Response<R>) => Response<R> | Promise<Response<R>>;
  onError?: (error: HttpError) => Promise<any>;
}

export class HttpClient {
  private baseURL: string;
  private defaultHeaders: Record<string, string>;
  private requestInterceptors: Interceptor<RequestConfig>[] = [];
  private responseInterceptors: Interceptor<Response>[] = [];

  constructor(baseURL: string, defaultHeaders: Record<string, string> = {}) {
    this.baseURL = baseURL;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      ...defaultHeaders
    };
  }

  addRequestInterceptor(interceptor: Interceptor<RequestConfig>) {
    this.requestInterceptors.push(interceptor);
  }

  addResponseInterceptor(interceptor: Interceptor<Response>) {
    this.responseInterceptors.push(interceptor);
  }

  private async applyRequestInterceptors(config: RequestConfig): Promise<RequestConfig> {
    let finalConfig = config;
    for (const interceptor of this.requestInterceptors) {
      if (interceptor.onRequest) {
        finalConfig = await interceptor.onRequest(finalConfig);
      }
    }
    return finalConfig;
  }

  private async applyResponseInterceptors<T>(response: Response<T>): Promise<Response<T>> {
    let finalResponse = response;
    for (const interceptor of this.responseInterceptors) {
      if (interceptor.onResponse) {
        finalResponse = await interceptor.onResponse(finalResponse);
      }
    }
    return finalResponse;
  }

  private async handleError(error: any): Promise<never> {
    const httpError: HttpError = {
      message: error.message || 'Network error',
      status: error.status,
      code: error.code,
      details: error.details
    };

    for (const interceptor of this.responseInterceptors) {
      if (interceptor.onError) {
        try {
          const result = await interceptor.onError(httpError);
          if (result !== undefined) {
            return result as never;
          }
        } catch (e) {
          // Continue to next interceptor
        }
      }
    }

    throw httpError;
  }

  private buildURL(endpoint: string, params?: Record<string, any>): string {
    const url = new URL(endpoint, this.baseURL);
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== undefined && params[key] !== null) {
          url.searchParams.append(key, params[key].toString());
        }
      });
    }
    return url.toString();
  }

  async request<T>(
    method: string,
    endpoint: string,
    data?: any,
    config: RequestConfig = {}
  ): Promise<Response<T>> {
    try {
      const finalConfig = await this.applyRequestInterceptors({
        ...config,
        headers: {
          ...this.defaultHeaders,
          ...config.headers
        }
      });

      const url = this.buildURL(endpoint, finalConfig.params);
      
      const fetchConfig: RequestInit = {
        method,
        headers: finalConfig.headers as HeadersInit,
        credentials: finalConfig.withCredentials ? 'include' : 'same-origin',
        signal: finalConfig.signal
      };

      if (data && method !== 'GET' && method !== 'HEAD') {
        fetchConfig.body = JSON.stringify(data);
      }

      const response = await fetch(url, fetchConfig);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw {
          message: errorData.detail || errorData.message || response.statusText,
          status: response.status,
          details: errorData
        };
      }

      const responseData = await response.json().catch(() => null);
      
      const httpResponse: Response<T> = {
        data: responseData,
        status: response.status,
        statusText: response.statusText,
        headers: response.headers
      };

      return await this.applyResponseInterceptors(httpResponse);
    } catch (error) {
      return this.handleError(error);
    }
  }

  get<T>(endpoint: string, config?: RequestConfig): Promise<Response<T>> {
    return this.request<T>('GET', endpoint, null, config);
  }

  post<T>(endpoint: string, data?: any, config?: RequestConfig): Promise<Response<T>> {
    return this.request<T>('POST', endpoint, data, config);
  }

  put<T>(endpoint: string, data?: any, config?: RequestConfig): Promise<Response<T>> {
    return this.request<T>('PUT', endpoint, data, config);
  }

  patch<T>(endpoint: string, data?: any, config?: RequestConfig): Promise<Response<T>> {
    return this.request<T>('PATCH', endpoint, data, config);
  }

  delete<T>(endpoint: string, config?: RequestConfig): Promise<Response<T>> {
    return this.request<T>('DELETE', endpoint, null, config);
  }
}