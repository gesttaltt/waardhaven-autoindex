import { IAuthRepository, GoogleAuthData } from '../../../domain/repositories/IAuthRepository';
import { AuthTokens } from '../../../domain/entities/User';

export class GoogleAuthUseCase {
  constructor(private authRepository: IAuthRepository) {}

  async execute(idToken: string): Promise<AuthTokens> {
    if (!idToken) {
      throw new Error('Google ID token is required');
    }

    const authData: GoogleAuthData = { idToken };
    return await this.authRepository.googleAuth(authData);
  }
}