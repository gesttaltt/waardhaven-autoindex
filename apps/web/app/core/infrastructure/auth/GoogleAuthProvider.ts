declare global {
  interface Window {
    google?: any;
  }
}

export interface GoogleUser {
  id: string;
  email: string;
  name: string;
  picture?: string;
  idToken: string;
}

export class GoogleAuthProvider {
  private static instance: GoogleAuthProvider;
  private clientId: string;
  private initialized: boolean = false;

  private constructor() {
    this.clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || '';
  }

  static getInstance(): GoogleAuthProvider {
    if (!GoogleAuthProvider.instance) {
      GoogleAuthProvider.instance = new GoogleAuthProvider();
    }
    return GoogleAuthProvider.instance;
  }

  async initialize(): Promise<void> {
    if (this.initialized || typeof window === 'undefined') return;

    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      
      script.onload = () => {
        if (window.google) {
          window.google.accounts.id.initialize({
            client_id: this.clientId,
            callback: this.handleCredentialResponse.bind(this),
            auto_select: false,
            cancel_on_tap_outside: true,
          });
          this.initialized = true;
          resolve();
        } else {
          reject(new Error('Google Identity Services failed to load'));
        }
      };

      script.onerror = () => {
        reject(new Error('Failed to load Google Identity Services script'));
      };

      document.head.appendChild(script);
    });
  }

  private handleCredentialResponse(response: any) {
    // This will be overridden by the component using the provider
  }

  renderButton(
    element: HTMLElement,
    onSuccess: (user: GoogleUser) => void,
    onError?: (error: Error) => void
  ): void {
    if (!this.initialized || !window.google) {
      console.error('Google Auth not initialized');
      return;
    }

    // Override the callback to handle the response
    window.google.accounts.id.initialize({
      client_id: this.clientId,
      callback: (response: any) => {
        try {
          const user = this.parseJwtToken(response.credential);
          onSuccess({
            ...user,
            idToken: response.credential
          });
        } catch (error) {
          onError?.(error as Error);
        }
      }
    });

    window.google.accounts.id.renderButton(element, {
      type: 'standard',
      theme: 'outline',
      size: 'large',
      text: 'continue_with',
      shape: 'rectangular',
      logo_alignment: 'left',
      width: '100%'
    });
  }

  async signIn(): Promise<GoogleUser> {
    if (!this.initialized || !window.google) {
      throw new Error('Google Auth not initialized');
    }

    return new Promise((resolve, reject) => {
      window.google.accounts.id.initialize({
        client_id: this.clientId,
        callback: (response: any) => {
          try {
            const user = this.parseJwtToken(response.credential);
            resolve({
              ...user,
              idToken: response.credential
            });
          } catch (error) {
            reject(error);
          }
        }
      });

      window.google.accounts.id.prompt((notification: any) => {
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          reject(new Error('Google Sign-In was cancelled'));
        }
      });
    });
  }

  signOut(): void {
    if (window.google?.accounts?.id) {
      window.google.accounts.id.disableAutoSelect();
    }
  }

  private parseJwtToken(token: string): Omit<GoogleUser, 'idToken'> {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );

      const payload = JSON.parse(jsonPayload);
      
      return {
        id: payload.sub,
        email: payload.email,
        name: payload.name,
        picture: payload.picture
      };
    } catch (error) {
      throw new Error('Failed to parse Google ID token');
    }
  }
}