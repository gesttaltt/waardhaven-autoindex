'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, AuthTokens } from '../../domain/entities/User';
import { LoginCredentials, RegisterData } from '../../domain/repositories/IAuthRepository';
import { AuthRepository } from '../../infrastructure/repositories/AuthRepository';
import { LoginUseCase } from '../../application/usecases/auth/LoginUseCase';
import { GoogleAuthUseCase } from '../../application/usecases/auth/GoogleAuthUseCase';
import { GoogleAuthProvider, GoogleUser } from '../../infrastructure/auth/GoogleAuthProvider';

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  googleLogin: () => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  const authRepository = new AuthRepository();
  const loginUseCase = new LoginUseCase(authRepository);
  const googleAuthUseCase = new GoogleAuthUseCase(authRepository);
  const googleProvider = GoogleAuthProvider.getInstance();

  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      setIsLoading(true);
      
      // Initialize Google Auth
      await googleProvider.initialize();
      
      // Check if user is authenticated
      if (authRepository.isAuthenticated()) {
        const currentUser = await authRepository.getCurrentUser();
        setUser(currentUser);
      }
    } catch (error) {
      console.error('Failed to initialize auth:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials: LoginCredentials) => {
    try {
      await loginUseCase.execute(credentials);
      const currentUser = await authRepository.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const register = async (data: RegisterData) => {
    try {
      await authRepository.register(data);
      const currentUser = await authRepository.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  };

  const googleLogin = async () => {
    try {
      const googleUser = await googleProvider.signIn();
      await googleAuthUseCase.execute(googleUser.idToken);
      const currentUser = await authRepository.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      console.error('Google login failed:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authRepository.logout();
      googleProvider.signOut();
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const refreshUser = async () => {
    try {
      const currentUser = await authRepository.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      console.error('Failed to refresh user:', error);
    }
  };

  const value: AuthContextValue = {
    user,
    isAuthenticated: authRepository.isAuthenticated(),
    isLoading,
    login,
    register,
    googleLogin,
    logout,
    refreshUser
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};