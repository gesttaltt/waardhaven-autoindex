// API related types and interfaces

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
  status?: number;
}

export interface ApiError {
  message: string;
  status?: number;
  detail?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  email: string;
  created_at?: string;
}

export interface CurrencyMap {
  [key: string]: string;
}

export interface RefreshStatus {
  isRefreshing: boolean;
  progress?: number;
  message?: string;
  error?: string;
}