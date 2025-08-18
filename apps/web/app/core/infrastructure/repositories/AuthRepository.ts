import { IAuthRepository, LoginCredentials, RegisterData, GoogleAuthData } from '../../domain/repositories/IAuthRepository';
import { User, AuthTokens } from '../../domain/entities/User';
import { ApiClient } from '../api/ApiClient';
import { TokenManager } from '../auth/TokenManager';

export class AuthRepository implements IAuthRepository {
  private apiClient: ApiClient;
  private tokenManager: TokenManager;
  private currentUser: User | null = null;

  constructor() {
    this.apiClient = ApiClient.getInstance();
    this.tokenManager = TokenManager.getInstance();
  }

  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const response = await this.apiClient.getHttpClient().post<{
      access_token: string;
      refresh_token?: string;
      token_type: string;
      expires_in: number;
    }>('/api/v1/auth/login', credentials);

    const tokens: AuthTokens = {
      accessToken: response.data.access_token,
      refreshToken: response.data.refresh_token,
      expiresIn: response.data.expires_in || 3600
    };

    this.tokenManager.setTokens(tokens);
    return tokens;
  }

  async register(data: RegisterData): Promise<AuthTokens> {
    const response = await this.apiClient.getHttpClient().post<{
      access_token: string;
      refresh_token?: string;
      token_type: string;
      expires_in: number;
    }>('/api/v1/auth/register', data);

    const tokens: AuthTokens = {
      accessToken: response.data.access_token,
      refreshToken: response.data.refresh_token,
      expiresIn: response.data.expires_in || 3600
    };

    this.tokenManager.setTokens(tokens);
    return tokens;
  }

  async googleAuth(data: GoogleAuthData): Promise<AuthTokens> {
    const response = await this.apiClient.getHttpClient().post<{
      access_token: string;
      refresh_token?: string;
      token_type: string;
      expires_in: number;
    }>('/api/v1/auth/google', data);

    const tokens: AuthTokens = {
      accessToken: response.data.access_token,
      refreshToken: response.data.refresh_token,
      expiresIn: response.data.expires_in || 3600
    };

    this.tokenManager.setTokens(tokens);
    return tokens;
  }

  async refreshToken(refreshToken: string): Promise<AuthTokens> {
    const response = await this.apiClient.getHttpClient().post<{
      access_token: string;
      refresh_token?: string;
      token_type: string;
      expires_in: number;
    }>('/api/v1/auth/refresh', { refresh_token: refreshToken });

    const tokens: AuthTokens = {
      accessToken: response.data.access_token,
      refreshToken: response.data.refresh_token || refreshToken,
      expiresIn: response.data.expires_in || 3600
    };

    this.tokenManager.setTokens(tokens);
    return tokens;
  }

  async logout(): Promise<void> {
    try {
      await this.apiClient.getHttpClient().post('/api/v1/auth/logout');
    } catch (error) {
      // Ignore logout errors
    } finally {
      this.tokenManager.clearTokens();
      this.currentUser = null;
    }
  }

  async getCurrentUser(): Promise<User | null> {
    if (!this.isAuthenticated()) {
      return null;
    }

    if (this.currentUser) {
      return this.currentUser;
    }

    try {
      const response = await this.apiClient.getHttpClient().get<User>('/api/v1/auth/me');
      this.currentUser = response.data;
      return this.currentUser;
    } catch (error) {
      return null;
    }
  }

  isAuthenticated(): boolean {
    return this.tokenManager.isAuthenticated();
  }
}