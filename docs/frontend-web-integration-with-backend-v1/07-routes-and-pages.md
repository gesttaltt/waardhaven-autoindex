# Routes and Pages

## Overview

The application uses Next.js 14 App Router with file-based routing. Each folder in the `app` directory represents a route segment.

## Route Structure

```
app/
├── page.tsx                 # / (Landing page)
├── layout.tsx              # Root layout
├── login/
│   └── page.tsx           # /login
├── register/
│   └── page.tsx           # /register
├── dashboard/
│   └── page.tsx           # /dashboard (Protected)
├── news/
│   └── page.tsx           # /news (Protected)
├── admin/
│   └── page.tsx           # /admin (Protected, Admin only)
├── diagnostics/
│   └── page.tsx           # /diagnostics (Protected)
└── tasks/
    └── page.tsx           # /tasks (Protected)
```

## Page Implementations

### Landing Page (`/`)

Public landing page with marketing content and authentication links.

```typescript
// app/page.tsx
"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { useInView } from "react-intersection-observer";

export default function Landing() {
  const [featuresRef, featuresInView] = useInView({ 
    threshold: 0.1, 
    triggerOnce: true 
  });

  return (
    <main className="min-h-screen overflow-hidden relative">
      {/* Hero Section */}
      <section className="max-w-5xl mx-auto px-6 py-24 text-center">
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-5xl md:text-6xl font-bold"
        >
          <span className="gradient-text">Smarter Long-Term Investing.</span>
          <br/>
          <span className="text-white">Fully Automated.</span>
        </motion.h1>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7, duration: 0.8 }}
          className="mt-10 flex items-center justify-center gap-4"
        >
          <Link href="/register">
            <button className="btn">Sign Up</button>
          </Link>
          <Link href="/login">
            <button className="btn-secondary">Log In</button>
          </Link>
        </motion.div>
      </section>

      {/* Features Section */}
      <div ref={featuresRef} className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
        {features.map((feature, index) => (
          <motion.div
            key={feature.title}
            initial={{ opacity: 0, y: 50 }}
            animate={featuresInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: index * 0.2, duration: 0.6 }}
            className="card"
          >
            <h3 className="font-semibold text-xl">{feature.title}</h3>
            <p className="mt-2 text-neutral-300">{feature.description}</p>
          </motion.div>
        ))}
      </div>
    </main>
  );
}
```

### Login Page (`/login`)

Authentication page with email/password and Google OAuth.

```typescript
// app/login/page.tsx
'use client';

import dynamic from 'next/dynamic';

const LoginForm = dynamic(
  () => import('../core/presentation/components/auth/LoginForm')
    .then(mod => mod.LoginForm),
  { 
    ssr: false,
    loading: () => <LoadingSpinner />
  }
);

export default function LoginPage() {
  return (
    <main className="min-h-screen flex items-center justify-center">
      <div className="w-full max-w-md p-8 bg-white rounded-xl shadow-lg">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome Back</h1>
        <p className="text-gray-600">Sign in to Waardhaven AutoIndex</p>
        <LoginForm />
      </div>
    </main>
  );
}
```

### Dashboard Page (`/dashboard`)

Main application dashboard with portfolio data visualization.

```typescript
// app/dashboard/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { 
  portfolioService, 
  benchmarkService, 
  strategyService 
} from "../services/api";
import { ProtectedRoute } from "../core/presentation/components/ProtectedRoute";

export default function Dashboard() {
  const router = useRouter();
  const [indexSeries, setIndexSeries] = useState<SeriesPoint[]>([]);
  const [allocations, setAllocations] = useState<AllocationItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [indexRes, allocRes] = await Promise.all([
        portfolioService.getIndexHistory(),
        portfolioService.getCurrentAllocations(),
      ]);
      
      setIndexSeries(indexRes.series);
      setAllocations(allocRes.allocations);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ProtectedRoute>
      <DashboardLayout>
        {loading ? (
          <LoadingSkeleton />
        ) : (
          <div className="space-y-6">
            <PerformanceCards data={indexSeries} />
            <PerformanceChart data={indexSeries} />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <PortfolioAllocation allocations={allocations} />
              <TopHoldings allocations={allocations} />
            </div>
          </div>
        )}
      </DashboardLayout>
    </ProtectedRoute>
  );
}
```

### News Page (`/news`)

Market news and sentiment analysis page.

```typescript
// app/news/page.tsx
"use client";

import { useEffect, useState } from "react";
import { newsService, portfolioService } from "../services/api";

export default function NewsPage() {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [trendingEntities, setTrendingEntities] = useState<TrendingEntity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }
    loadNewsData();
  }, []);

  const loadNewsData = async () => {
    try {
      const allocRes = await portfolioService.getCurrentAllocations();
      const symbols = allocRes.allocations.map(a => a.symbol);
      
      const [newsRes, trendingRes] = await Promise.all([
        newsService.searchNews({ symbols, limit: 50 }),
        newsService.getTrendingEntities()
      ]);
      
      setArticles(newsRes);
      setTrendingEntities(trendingRes);
    } catch (err) {
      console.error('Failed to load news:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <NewsLayout>
      <TrendingSection entities={trendingEntities} />
      <NewsArticles articles={articles} loading={loading} />
    </NewsLayout>
  );
}
```

## Route Protection

### Protected Route Wrapper

```typescript
// core/presentation/components/ProtectedRoute.tsx
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
  redirectTo = '/login'
}) => {
  const { isAuthenticated, user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) {
        router.push(redirectTo);
      } else if (requiredRole && user?.role !== requiredRole) {
        router.push('/unauthorized');
      }
    }
  }, [isAuthenticated, isLoading, user, requiredRole]);

  if (isLoading) return <LoadingSpinner />;
  if (!isAuthenticated) return null;
  if (requiredRole && user?.role !== requiredRole) return null;

  return <>{children}</>;
};
```

### Middleware Protection

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token');
  const isAuthPage = request.nextUrl.pathname.startsWith('/login') || 
                     request.nextUrl.pathname.startsWith('/register');
  const isProtectedPage = request.nextUrl.pathname.startsWith('/dashboard') ||
                          request.nextUrl.pathname.startsWith('/admin');

  if (isProtectedPage && !token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  if (isAuthPage && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/admin/:path*', '/login', '/register']
};
```

## Navigation

### Navigation Component

```typescript
// components/Navigation.tsx
export const Navigation: React.FC = () => {
  const { user, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: HomeIcon },
    { href: '/news', label: 'Market News', icon: NewsIcon },
    { href: '/tasks', label: 'Tasks', icon: TaskIcon },
    { href: '/diagnostics', label: 'Diagnostics', icon: DiagIcon },
  ];

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between h-16">
          <div className="flex items-center space-x-8">
            <Logo />
            {navItems.map(item => (
              <NavLink
                key={item.href}
                href={item.href}
                active={pathname === item.href}
              >
                <item.icon className="w-5 h-5 mr-2" />
                {item.label}
              </NavLink>
            ))}
          </div>
          
          <div className="flex items-center space-x-4">
            <UserMenu user={user} onLogout={logout} />
          </div>
        </div>
      </div>
    </nav>
  );
};
```

### Breadcrumbs

```typescript
// components/Breadcrumbs.tsx
export const Breadcrumbs: React.FC = () => {
  const pathname = usePathname();
  const segments = pathname.split('/').filter(Boolean);

  return (
    <nav className="flex" aria-label="Breadcrumb">
      <ol className="inline-flex items-center space-x-1">
        <li>
          <Link href="/" className="text-gray-500 hover:text-gray-700">
            Home
          </Link>
        </li>
        {segments.map((segment, index) => {
          const href = `/${segments.slice(0, index + 1).join('/')}`;
          const isLast = index === segments.length - 1;
          const label = segment.charAt(0).toUpperCase() + segment.slice(1);

          return (
            <li key={segment} className="flex items-center">
              <ChevronRight className="w-4 h-4 mx-1 text-gray-400" />
              {isLast ? (
                <span className="text-gray-900 font-medium">{label}</span>
              ) : (
                <Link href={href} className="text-gray-500 hover:text-gray-700">
                  {label}
                </Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};
```

## Dynamic Routes

### Dynamic Route Example

```typescript
// app/portfolio/[symbol]/page.tsx
export default function AssetPage({ 
  params 
}: { 
  params: { symbol: string } 
}) {
  const [assetData, setAssetData] = useState(null);

  useEffect(() => {
    portfolioService.getAssetHistory(params.symbol)
      .then(setAssetData);
  }, [params.symbol]);

  return (
    <div>
      <h1>Asset: {params.symbol}</h1>
      {assetData && <AssetChart data={assetData} />}
    </div>
  );
}
```

### Catch-All Routes

```typescript
// app/docs/[...slug]/page.tsx
export default function DocPage({ 
  params 
}: { 
  params: { slug: string[] } 
}) {
  const path = params.slug.join('/');
  
  return <DocumentViewer path={path} />;
}
```

## Route Groups

### Layout Groups

```typescript
// app/(auth)/layout.tsx
export default function AuthLayout({ 
  children 
}: { 
  children: React.ReactNode 
}) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="flex items-center justify-center min-h-screen">
        {children}
      </div>
    </div>
  );
}

// app/(auth)/login/page.tsx
// app/(auth)/register/page.tsx
// These pages will use the AuthLayout
```

### Private Routes Group

```typescript
// app/(private)/layout.tsx
export default function PrivateLayout({ 
  children 
}: { 
  children: React.ReactNode 
}) {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <main className="max-w-7xl mx-auto px-4 py-6">
          {children}
        </main>
      </div>
    </ProtectedRoute>
  );
}
```

## Loading States

### Loading UI

```typescript
// app/dashboard/loading.tsx
export default function DashboardLoading() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
      <div className="bg-white rounded-lg p-6 h-96 animate-pulse">
        <div className="h-full bg-gray-200 rounded"></div>
      </div>
    </div>
  );
}
```

## Error Handling

### Error UI

```typescript
// app/dashboard/error.tsx
'use client';

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="min-h-[400px] flex items-center justify-center">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Something went wrong!
        </h2>
        <p className="text-gray-600 mb-4">
          {error.message || 'An unexpected error occurred'}
        </p>
        <button
          onClick={reset}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
```

### Not Found Page

```typescript
// app/not-found.tsx
export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-900">404</h1>
        <p className="text-xl text-gray-600 mt-4">Page not found</p>
        <Link href="/" className="mt-6 inline-block px-6 py-3 bg-blue-600 text-white rounded-lg">
          Go Home
        </Link>
      </div>
    </div>
  );
}
```

## Route Metadata

### Static Metadata

```typescript
// app/dashboard/page.tsx
export const metadata: Metadata = {
  title: 'Dashboard - Waardhaven AutoIndex',
  description: 'View your portfolio performance and allocations',
};
```

### Dynamic Metadata

```typescript
// app/portfolio/[symbol]/page.tsx
export async function generateMetadata({ 
  params 
}: { 
  params: { symbol: string } 
}): Promise<Metadata> {
  const asset = await getAssetData(params.symbol);
  
  return {
    title: `${asset.name} (${asset.symbol}) - Waardhaven`,
    description: `View performance and details for ${asset.name}`,
  };
}
```

## Route Handlers

### API Route Handler

```typescript
// app/api/webhook/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const body = await request.json();
  
  // Process webhook
  await processWebhook(body);
  
  return NextResponse.json({ success: true });
}
```

## Parallel Routes

```typescript
// app/dashboard/@analytics/page.tsx
// app/dashboard/@portfolio/page.tsx
// app/dashboard/layout.tsx

export default function DashboardLayout({
  children,
  analytics,
  portfolio,
}: {
  children: React.ReactNode;
  analytics: React.ReactNode;
  portfolio: React.ReactNode;
}) {
  return (
    <div>
      {children}
      <div className="grid grid-cols-2 gap-6">
        {analytics}
        {portfolio}
      </div>
    </div>
  );
}
```

## Best Practices

1. **Use Dynamic Imports** - For heavy components
2. **Implement Loading States** - Show feedback during navigation
3. **Handle Errors Gracefully** - Use error boundaries
4. **Protect Sensitive Routes** - Use middleware and components
5. **Optimize Metadata** - For SEO and sharing
6. **Cache Static Pages** - Use ISR when appropriate
7. **Prefetch Links** - Next.js does this automatically
8. **Use Route Groups** - Organize related routes

## Next Steps

- Review [Error Handling](./08-error-handling.md)
- Learn about [Performance Optimization](./11-performance-optimization.md)
- Understand [Deployment Configuration](./10-deployment-configuration.md)