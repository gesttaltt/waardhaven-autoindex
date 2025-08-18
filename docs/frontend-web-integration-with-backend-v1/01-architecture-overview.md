# Architecture Overview

## Clean Architecture Implementation

The frontend follows Clean Architecture principles, ensuring separation of concerns and maintainability. The architecture is divided into four main layers:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  (Components, Hooks, Contexts, Pages)                       │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                         │
│  (Use Cases, Business Logic)                                │
├─────────────────────────────────────────────────────────────┤
│                      Domain Layer                            │
│  (Entities, Repository Interfaces)                          │
├─────────────────────────────────────────────────────────────┤
│                  Infrastructure Layer                        │
│  (API Clients, External Services, Implementations)          │
└─────────────────────────────────────────────────────────────┘
```

## Layer Descriptions

### 1. Domain Layer (`app/core/domain/`)
The heart of the application containing business entities and repository interfaces.

**Entities:**
- `User.ts` - User entity with authentication tokens
- `Portfolio.ts` - Portfolio, Asset, and Allocation entities

**Repository Interfaces:**
- `IAuthRepository.ts` - Authentication operations interface
- `IPortfolioRepository.ts` - Portfolio operations interface

```typescript
// Example Entity
export interface User {
  id: string;
  email: string;
  name?: string;
  role: UserRole;
  createdAt: Date;
  updatedAt: Date;
}

// Example Repository Interface
export interface IAuthRepository {
  login(credentials: LoginCredentials): Promise<AuthTokens>;
  register(data: RegisterData): Promise<AuthTokens>;
  logout(): Promise<void>;
  getCurrentUser(): Promise<User | null>;
}
```

### 2. Application Layer (`app/core/application/`)
Contains use cases that orchestrate business logic.

**Use Cases:**
- `LoginUseCase.ts` - Handles user login with validation
- `GoogleAuthUseCase.ts` - Manages Google OAuth authentication

```typescript
export class LoginUseCase {
  constructor(private authRepository: IAuthRepository) {}

  async execute(credentials: LoginCredentials): Promise<AuthTokens> {
    // Validation logic
    if (!this.isValidEmail(credentials.email)) {
      throw new Error('Invalid email format');
    }
    // Delegate to repository
    return await this.authRepository.login(credentials);
  }
}
```

### 3. Infrastructure Layer (`app/core/infrastructure/`)
Implements external service integrations and repository implementations.

**API Infrastructure:**
- `HttpClient.ts` - Generic HTTP client with interceptors
- `ApiClient.ts` - Configured API client singleton

**Auth Infrastructure:**
- `TokenManager.ts` - JWT token management
- `GoogleAuthProvider.ts` - Google OAuth integration
- `AuthRepository.ts` - IAuthRepository implementation

```typescript
export class HttpClient {
  private requestInterceptors: Interceptor<RequestConfig>[] = [];
  private responseInterceptors: Interceptor<Response>[] = [];

  async request<T>(
    method: string,
    endpoint: string,
    data?: any,
    config: RequestConfig = {}
  ): Promise<Response<T>> {
    // Apply interceptors
    // Make request
    // Handle response
  }
}
```

### 4. Presentation Layer (`app/core/presentation/`)
User interface components and React-specific implementations.

**Components:**
- `auth/LoginForm.tsx` - Login form component
- `ProtectedRoute.tsx` - Route protection component

**Contexts:**
- `AuthContext.tsx` - Authentication state management

**Hooks:**
- `useApiRequest.ts` - Generic API request hook with retry logic

## SOLID Principles Implementation

### Single Responsibility Principle (SRP)
Each class and component has a single, well-defined purpose:
- `TokenManager` - Only manages tokens
- `LoginForm` - Only handles login UI
- `AuthRepository` - Only implements auth operations

### Open/Closed Principle (OCP)
Classes are open for extension but closed for modification:
- `ApiService` base class extended by specific services
- `HttpClient` extensible through interceptors

### Liskov Substitution Principle (LSP)
Repository implementations can be swapped without affecting the system:
- `AuthRepository` implements `IAuthRepository`
- Can replace with `MockAuthRepository` for testing

### Interface Segregation Principle (ISP)
Interfaces are focused and specific:
- `IAuthRepository` - Only auth operations
- `IPortfolioRepository` - Only portfolio operations

### Dependency Inversion Principle (DIP)
High-level modules depend on abstractions:
- Use cases depend on repository interfaces, not implementations
- Components use contexts and hooks, not direct API calls

## Dependency Flow

```
Pages/Components
    ↓
Contexts/Hooks
    ↓
Use Cases
    ↓
Repository Interfaces
    ↑
Repository Implementations
    ↓
API Clients/External Services
```

## File Organization

```
app/core/
├── domain/
│   ├── entities/
│   │   ├── User.ts
│   │   └── Portfolio.ts
│   └── repositories/
│       ├── IAuthRepository.ts
│       └── IPortfolioRepository.ts
├── application/
│   └── usecases/
│       └── auth/
│           ├── LoginUseCase.ts
│           └── GoogleAuthUseCase.ts
├── infrastructure/
│   ├── api/
│   │   ├── HttpClient.ts
│   │   └── ApiClient.ts
│   ├── auth/
│   │   ├── TokenManager.ts
│   │   └── GoogleAuthProvider.ts
│   └── repositories/
│       └── AuthRepository.ts
└── presentation/
    ├── components/
    │   ├── auth/
    │   │   └── LoginForm.tsx
    │   └── ProtectedRoute.tsx
    ├── contexts/
    │   └── AuthContext.tsx
    └── hooks/
        └── useApiRequest.ts
```

## Benefits of This Architecture

1. **Testability**: Each layer can be tested independently
2. **Maintainability**: Clear separation of concerns
3. **Flexibility**: Easy to swap implementations
4. **Scalability**: Can add features without affecting existing code
5. **Type Safety**: Full TypeScript support across layers
6. **Reusability**: Business logic separated from UI

## Design Patterns Used

1. **Repository Pattern**: Abstract data access logic
2. **Dependency Injection**: Inject dependencies rather than hard-coding
3. **Singleton Pattern**: Single instances for managers and providers
4. **Factory Pattern**: Create complex objects (API clients)
5. **Observer Pattern**: React contexts and hooks
6. **Interceptor Pattern**: Request/response middleware

## Communication Between Layers

### From Presentation to Domain
```typescript
// Component uses context
const { login } = useAuth();

// Context uses use case
const loginUseCase = new LoginUseCase(authRepository);
await loginUseCase.execute(credentials);

// Use case uses repository interface
return await this.authRepository.login(credentials);

// Repository implementation makes API call
const response = await this.apiClient.post('/auth/login', credentials);
```

### Error Propagation
Errors flow up from infrastructure to presentation:
```
API Error → Repository → Use Case → Context → Component → User
```

## Next Steps

- Continue to [API Integration Guide](./02-api-integration-guide.md)
- Review [Component Structure](./05-component-structure.md)
- Learn about [State Management](./06-state-management.md)