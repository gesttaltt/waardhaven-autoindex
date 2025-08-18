# Frontend Development Guide

**Last Updated**: 2025-01-18  
**Status**: ✅ Active

## Overview

This guide covers development tools, practices, and workflows for the Waardhaven AutoIndex frontend (Next.js/React/TypeScript).

## Code Quality Tools

### Formatting

**Prettier** - Opinionated code formatter
- Version: 3.2.5
- Formats: JS, JSX, TS, TSX, JSON, CSS, MD
- Configuration: Default settings
- Usage:
  ```bash
  # Format all files
  npm run format
  
  # Check formatting (CI mode)
  npm run format:check
  
  # Format specific file
  npx prettier --write app/page.tsx
  ```

### Linting

**ESLint** - JavaScript/TypeScript linter
- Configuration: Next.js defaults + TypeScript
- Plugins:
  - @typescript-eslint/eslint-plugin
  - eslint-config-next
- Usage:
  ```bash
  # Lint with auto-fix (allows warnings)
  npm run lint
  
  # Strict mode (zero warnings, CI mode)
  npm run lint:check
  
  # Lint specific file
  npx eslint app/page.tsx
  ```

### Type Checking

**TypeScript** - Static type checker
- Version: 5.5.4
- Configuration: tsconfig.json
- Usage:
  ```bash
  # Type check entire project
  npm run type-check
  
  # Watch mode
  npx tsc --watch --noEmit
  ```

## NPM Scripts

Added to `package.json`:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint --max-warnings 50",
    "lint:check": "next lint --max-warnings 0",
    "format": "prettier --write \"**/*.{js,jsx,ts,tsx,json,css,md}\"",
    "format:check": "prettier --check \"**/*.{js,jsx,ts,tsx,json,css,md}\"",
    "type-check": "tsc --noEmit",
    "test": "echo 'No tests configured yet' && exit 0"
  }
}
```

## Development Workflow

### 1. Initial Setup

```bash
# Install dependencies
cd apps/web
npm install

# Setup pre-commit hooks (from project root)
bash apps/api/scripts/setup-pre-commit.sh
```

### 2. Development Server

```bash
# Start development server
npm run dev

# Access at http://localhost:3000
```

### 3. Before Committing

**Automatic (with pre-commit hooks):**
- Prettier formats automatically
- ESLint fixes what it can
- Commit proceeds if all checks pass

**Manual checks:**
```bash
# Format code
npm run format

# Fix lint issues
npm run lint

# Check types
npm run type-check
```

### 4. CI Validation

Check if code will pass CI:
```bash
# All checks that CI runs
npm run format:check  # Must pass
npm run lint:check    # Must pass (0 warnings)
npm run type-check    # Must pass
npm run build         # Must succeed
```

## Project Structure

```
apps/web/
├── app/                    # Next.js app directory
│   ├── components/        # Shared components
│   │   ├── dashboard/    # Dashboard components
│   │   └── shared/       # Reusable components
│   ├── core/             # Clean architecture core
│   │   ├── application/  # Use cases
│   │   ├── domain/       # Entities & interfaces
│   │   ├── infrastructure/ # External services
│   │   └── presentation/ # UI components & contexts
│   ├── hooks/            # Custom React hooks
│   ├── services/         # API service layer
│   ├── types/            # TypeScript type definitions
│   └── utils/            # Utility functions
├── public/               # Static assets
├── package.json          # Dependencies & scripts
├── tsconfig.json         # TypeScript config
├── tailwind.config.js    # Tailwind CSS config
└── next.config.js        # Next.js config
```

## Component Development

### Component Structure

```typescript
// app/components/shared/Button/Button.tsx
import { ButtonProps } from './Button.types';
import { buttonStyles } from './Button.styles';

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  onClick,
  ...props
}) => {
  return (
    <button
      className={buttonStyles({ variant })}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  );
};

// app/components/shared/Button/Button.types.ts
export interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'danger';
  onClick?: () => void;
}

// app/components/shared/Button/index.ts
export { Button } from './Button';
export type { ButtonProps } from './Button.types';
```

### Best Practices

1. **Use TypeScript**: Always define types/interfaces
2. **Component Organization**: Group related files
3. **Barrel Exports**: Use index.ts for clean imports
4. **Separate Concerns**: Logic, styles, types in separate files
5. **Custom Hooks**: Extract complex logic to hooks
6. **Memoization**: Use React.memo, useMemo, useCallback wisely

## Styling

### Tailwind CSS

Primary styling solution:
```tsx
<div className="flex items-center justify-between p-4 bg-white rounded-lg shadow">
  <h2 className="text-xl font-semibold text-gray-900">Title</h2>
</div>
```

### CSS Modules (Optional)

For complex component styles:
```css
/* Button.module.css */
.button {
  @apply px-4 py-2 rounded-lg transition-colors;
}

.primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}
```

### Class Variance Authority (CVA)

For component variants:
```typescript
import { cva } from 'class-variance-authority';

export const buttonStyles = cva(
  'px-4 py-2 rounded-lg transition-colors',
  {
    variants: {
      variant: {
        primary: 'bg-blue-600 text-white hover:bg-blue-700',
        secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
      },
    },
  }
);
```

## State Management

### React Context

For global state (auth, theme):
```typescript
// app/core/presentation/contexts/AuthContext.tsx
const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  
  return (
    <AuthContext.Provider value={{ user, setUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

### React Query (TanStack Query)

For server state:
```typescript
// app/hooks/usePortfolioData.ts
import { useQuery } from '@tanstack/react-query';

export const usePortfolioData = () => {
  return useQuery({
    queryKey: ['portfolio'],
    queryFn: () => portfolioService.getPortfolio(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
```

## API Integration

### Service Layer

```typescript
// app/services/api/portfolio.ts
import { apiClient } from './client';

export const portfolioService = {
  async getPortfolio() {
    const response = await apiClient.get('/api/v1/index');
    return response.data;
  },

  async updateStrategy(strategy: StrategyConfig) {
    const response = await apiClient.post('/api/v1/strategy', strategy);
    return response.data;
  },
};
```

### Error Handling

```typescript
// app/hooks/api/useApiCall.ts
export const useApiCall = <T,>(apiCall: () => Promise<T>) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiCall();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, execute };
};
```

## Testing (Planned)

### Jest & React Testing Library

```typescript
// app/components/shared/Button/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders children', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick handler', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### E2E Testing (Planned)

```typescript
// e2e/dashboard.spec.ts
import { test, expect } from '@playwright/test';

test('dashboard loads portfolio data', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page.locator('h1')).toContainText('Portfolio Performance');
  await expect(page.locator('[data-testid="portfolio-value"]')).toBeVisible();
});
```

## Environment Variables

### Configuration

```bash
# apps/web/.env.local (development)
NEXT_PUBLIC_API_URL=http://localhost:8000

# apps/web/.env.production (production)
NEXT_PUBLIC_API_URL=https://api.waardhaven.com
```

### Type Safety

```typescript
// app/utils/env-validator.ts
const envSchema = z.object({
  NEXT_PUBLIC_API_URL: z.string().url(),
});

export const env = envSchema.parse({
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
});
```

## Performance Optimization

### Code Splitting

Next.js automatic code splitting:
```typescript
// Dynamic imports
const DashboardChart = dynamic(
  () => import('@/components/dashboard/PerformanceChart'),
  { loading: () => <LoadingSkeleton /> }
);
```

### Image Optimization

```typescript
import Image from 'next/image';

<Image
  src="/logo.png"
  alt="Logo"
  width={200}
  height={50}
  priority // For above-the-fold images
/>
```

### Bundle Analysis

```bash
# Analyze bundle size
npm run build
npx @next/bundle-analyzer
```

## IDE Configuration

### VS Code

**.vscode/settings.json**
```json
{
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "typescript.tsdk": "node_modules/typescript/lib",
  "tailwindCSS.experimental.classRegex": [
    ["cva\\(([^)]*)\\)", "[\"'`]([^\"'`]*).*?[\"'`]"]
  ]
}
```

### Recommended Extensions

- ESLint
- Prettier - Code formatter
- Tailwind CSS IntelliSense
- TypeScript React code snippets
- Auto Rename Tag

## Debugging

### React Developer Tools

Browser extension for debugging React:
- Component tree inspection
- Props and state viewing
- Performance profiling

### Next.js Debug Mode

```json
// package.json
{
  "scripts": {
    "dev:debug": "NODE_OPTIONS='--inspect' next dev"
  }
}
```

### Console Debugging

```typescript
// Conditional logging
if (process.env.NODE_ENV === 'development') {
  console.log('Debug info:', data);
}

// Structured logging
console.table(data);
console.group('API Call');
console.log('Request:', request);
console.log('Response:', response);
console.groupEnd();
```

## Build & Deployment

### Production Build

```bash
# Build for production
npm run build

# Test production build locally
npm run start
```

### Build Output

```
apps/web/.next/
├── static/       # Static assets
├── server/       # Server-side code
└── cache/        # Build cache
```

### Deployment Checklist

- [ ] Run `npm run format:check`
- [ ] Run `npm run lint:check`
- [ ] Run `npm run type-check`
- [ ] Run `npm run build`
- [ ] Test production build locally
- [ ] Check environment variables
- [ ] Review bundle size

## Troubleshooting

### Common Issues

**TypeScript Errors**
```bash
# Clear TypeScript cache
rm -rf .next
rm tsconfig.tsbuildinfo
npm run type-check
```

**Module Resolution Issues**
```bash
# Clear node_modules
rm -rf node_modules package-lock.json
npm install
```

**Prettier/ESLint Conflicts**
```bash
# Ensure prettier runs last
npm run lint
npm run format
```

**Build Failures**
```bash
# Clean build
rm -rf .next
npm run build
```

## Best Practices

1. **Type Safety First**: Always use TypeScript
2. **Component Composition**: Small, focused components
3. **Performance**: Lazy load heavy components
4. **Accessibility**: Use semantic HTML, ARIA labels
5. **Error Boundaries**: Wrap components in error boundaries
6. **Loading States**: Always show loading feedback
7. **Responsive Design**: Mobile-first approach
8. **Code Splitting**: Dynamic imports for large modules
9. **Caching Strategy**: Use React Query for API caching
10. **Security**: Validate all user inputs

## References

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Prettier Documentation](https://prettier.io/docs/)
- [ESLint Documentation](https://eslint.org/docs/)
- [React Query Documentation](https://tanstack.com/query/)