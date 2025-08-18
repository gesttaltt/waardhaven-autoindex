import { HttpClient, HttpError } from './HttpClient';
import { TokenManager } from '../auth/TokenManager';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiClient {
  private static instance: ApiClient;
  private httpClient: HttpClient;
  private tokenManager: TokenManager;

  private constructor() {
    this.httpClient = new HttpClient(API_BASE_URL);
    this.tokenManager = TokenManager.getInstance();
    this.setupInterceptors();
  }

  static getInstance(): ApiClient {
    if (!ApiClient.instance) {
      ApiClient.instance = new ApiClient();
    }
    return ApiClient.instance;
  }

  private setupInterceptors() {
    // Request interceptor for auth token
    this.httpClient.addRequestInterceptor({
      onRequest: (config) => {
        const token = this.tokenManager.getAccessToken();
        if (token) {
          config.headers = {
            ...config.headers,
            Authorization: `Bearer ${token}`
          };
        }
        return config;
      }
    });

    // Response interceptor for token refresh
    this.httpClient.addResponseInterceptor({
      onError: async (error: HttpError) => {
        if (error.status === 401) {
          const refreshToken = this.tokenManager.getRefreshToken();
          
          if (refreshToken) {
            try {
              const response = await this.httpClient.post<{ access_token: string; refresh_token?: string }>('/api/v1/auth/refresh', {
                refresh_token: refreshToken
              });
              
              this.tokenManager.setTokens({
                accessToken: response.data.access_token,
                refreshToken: response.data.refresh_token,
                expiresIn: 3600
              });

              // Retry original request
              return Promise.resolve(response);
            } catch (refreshError) {
              this.tokenManager.clearTokens();
              if (typeof window !== 'undefined') {
                window.location.href = '/login';
              }
            }
          } else {
            this.tokenManager.clearTokens();
            if (typeof window !== 'undefined') {
              window.location.href = '/login';
            }
          }
        }
        throw error;
      }
    });

    // Request retry interceptor
    this.httpClient.addRequestInterceptor({
      onRequest: (config) => {
        // Add request ID for tracking
        config.headers = {
          ...config.headers,
          'X-Request-ID': this.generateRequestId()
        };
        return config;
      }
    });
  }

  private generateRequestId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  getHttpClient(): HttpClient {
    return this.httpClient;
  }
}