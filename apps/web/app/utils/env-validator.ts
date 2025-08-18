/**
 * Environment variable validation utility
 * Ensures all required environment variables are present and valid
 */

interface EnvConfig {
  NEXT_PUBLIC_API_URL: string;
  NEXT_PUBLIC_GOOGLE_CLIENT_ID?: string;
  NEXT_PUBLIC_GA_ID?: string;
  NODE_ENV: 'development' | 'production' | 'test';
}

class EnvValidator {
  private config: Partial<EnvConfig> = {};
  private errors: string[] = [];

  constructor() {
    this.validate();
  }

  private validate(): void {
    // Required variables
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    if (!apiUrl) {
      this.errors.push('NEXT_PUBLIC_API_URL is required');
    } else {
      // Validate URL format
      try {
        new URL(apiUrl);
        this.config.NEXT_PUBLIC_API_URL = apiUrl;
      } catch {
        this.errors.push('NEXT_PUBLIC_API_URL must be a valid URL');
      }
    }

    // Optional but recommended variables
    const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
    if (googleClientId) {
      this.config.NEXT_PUBLIC_GOOGLE_CLIENT_ID = googleClientId;
    } else if (process.env.NODE_ENV === 'production') {
      console.warn('NEXT_PUBLIC_GOOGLE_CLIENT_ID not set - Google OAuth will not work');
    }

    // Google Analytics
    const gaId = process.env.NEXT_PUBLIC_GA_ID;
    if (gaId) {
      this.config.NEXT_PUBLIC_GA_ID = gaId;
    }

    // Node environment
    this.config.NODE_ENV = (process.env.NODE_ENV as any) || 'development';

    // Log validation results
    if (this.errors.length > 0) {
      console.error('Environment validation failed:');
      this.errors.forEach(error => console.error(`  - ${error}`));
      
      if (process.env.NODE_ENV === 'production') {
        throw new Error('Environment validation failed in production');
      }
    }
  }

  public getConfig(): EnvConfig {
    if (this.errors.length > 0) {
      // Return defaults for development
      return {
        NEXT_PUBLIC_API_URL: 'http://localhost:8000',
        NODE_ENV: 'development'
      };
    }
    return this.config as EnvConfig;
  }

  public getApiUrl(): string {
    return this.config.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  public getGoogleClientId(): string | undefined {
    return this.config.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
  }

  public isProduction(): boolean {
    return this.config.NODE_ENV === 'production';
  }

  public isDevelopment(): boolean {
    return this.config.NODE_ENV === 'development';
  }

  public hasGoogleAuth(): boolean {
    return !!this.config.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
  }
}

// Export singleton instance
export const envValidator = new EnvValidator();

// Export convenience functions
export const getApiUrl = () => envValidator.getApiUrl();
export const getGoogleClientId = () => envValidator.getGoogleClientId();
export const isProduction = () => envValidator.isProduction();
export const isDevelopment = () => envValidator.isDevelopment();
export const hasGoogleAuth = () => envValidator.hasGoogleAuth();