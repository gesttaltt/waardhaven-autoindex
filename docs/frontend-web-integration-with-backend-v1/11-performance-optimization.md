# Performance Optimization

## Core Web Vitals

### Target Metrics
- **LCP** (Largest Contentful Paint) < 2.5s
- **FID** (First Input Delay) < 100ms
- **CLS** (Cumulative Layout Shift) < 0.1

## Code Splitting

### Dynamic Imports
```typescript
const DashboardChart = dynamic(
  () => import('../components/DashboardChart'),
  { 
    loading: () => <ChartSkeleton />,
    ssr: false 
  }
);
```

### Route-Based Splitting
```typescript
// Automatic in Next.js App Router
// Each page.tsx is a separate bundle
```

## Bundle Optimization

### Tree Shaking
```javascript
// next.config.js
module.exports = {
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['lodash', 'recharts'],
  },
};
```

### Bundle Analysis
```bash
npm run build:analyze
# Visualize bundle size with @next/bundle-analyzer
```

## Image Optimization

### Next.js Image Component
```typescript
import Image from 'next/image';

<Image
  src="/logo.png"
  alt="Logo"
  width={200}
  height={50}
  priority // For above-fold images
  placeholder="blur"
  blurDataURL={shimmer}
/>
```

### Responsive Images
```typescript
<Image
  src={asset.image}
  alt={asset.name}
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  fill
  style={{ objectFit: 'cover' }}
/>
```

## Data Fetching Optimization

### React Query Caching
```typescript
const { data } = useQuery({
  queryKey: ['portfolio', id],
  queryFn: fetchPortfolio,
  staleTime: 5 * 60 * 1000, // 5 minutes
  gcTime: 10 * 60 * 1000, // 10 minutes
});
```

### Prefetching
```typescript
// Prefetch on hover
const prefetchPortfolio = () => {
  queryClient.prefetchQuery({
    queryKey: ['portfolio', id],
    queryFn: () => portfolioService.get(id),
  });
};

<Link href="/portfolio" onMouseEnter={prefetchPortfolio}>
  Portfolio
</Link>
```

### Parallel Queries
```typescript
const results = useQueries({
  queries: [
    { queryKey: ['portfolio'], queryFn: fetchPortfolio },
    { queryKey: ['benchmark'], queryFn: fetchBenchmark },
    { queryKey: ['news'], queryFn: fetchNews },
  ],
});
```

## Rendering Optimization

### Memoization
```typescript
const ExpensiveComponent = React.memo(({ data }) => {
  const processedData = useMemo(
    () => processComplexData(data),
    [data]
  );
  
  const handleClick = useCallback((id) => {
    console.log('Clicked:', id);
  }, []);
  
  return <DataView data={processedData} onClick={handleClick} />;
});
```

### Virtual Scrolling
```typescript
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={items.length}
  itemSize={50}
  width="100%"
>
  {({ index, style }) => (
    <div style={style}>
      {items[index].name}
    </div>
  )}
</FixedSizeList>
```

## Network Optimization

### API Response Compression
```typescript
// Backend
app.use(compression({
  filter: (req, res) => {
    return req.headers['accept-encoding']?.includes('gzip');
  },
  threshold: 1024, // Only compress > 1KB
}));
```

### Request Deduplication
```typescript
const cache = new Map();

async function fetchWithCache(url: string) {
  if (!cache.has(url)) {
    cache.set(url, fetch(url).then(r => r.json()));
  }
  return cache.get(url);
}
```

## Caching Strategy

### Static Assets
```javascript
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/_next/static/:path*',
        headers: [{
          key: 'Cache-Control',
          value: 'public, max-age=31536000, immutable',
        }],
      },
    ];
  },
};
```

### API Caching
```typescript
// Service Worker
self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/api/static')) {
    event.respondWith(
      caches.match(event.request).then(
        response => response || fetch(event.request)
      )
    );
  }
});
```

## Database Optimization

### Query Optimization
```sql
-- Add indexes
CREATE INDEX idx_prices_symbol_date ON prices(symbol, date);
CREATE INDEX idx_allocations_date ON allocations(date);

-- Optimize queries
EXPLAIN ANALYZE SELECT * FROM prices WHERE symbol = 'AAPL';
```

### Connection Pooling
```typescript
const pool = new Pool({
  max: 20,
  min: 5,
  idleTimeoutMillis: 30000,
});
```

## Monitoring

### Performance Monitoring
```typescript
// Web Vitals
import { getCLS, getFID, getLCP } from 'web-vitals';

function sendToAnalytics(metric) {
  // Send to analytics service
  gtag('event', metric.name, {
    value: Math.round(metric.value),
    metric_id: metric.id,
  });
}

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getLCP(sendToAnalytics);
```

### Custom Metrics
```typescript
// Measure API response time
const startTime = performance.now();
const data = await fetchData();
const duration = performance.now() - startTime;

performance.measure('api-call', {
  start: startTime,
  duration,
});
```

## Lighthouse Scores

### Target Scores
- Performance: > 90
- Accessibility: > 95
- Best Practices: > 95
- SEO: > 95

### Optimization Checklist
- [ ] Enable text compression
- [ ] Minimize main thread work
- [ ] Reduce JavaScript execution time
- [ ] Eliminate render-blocking resources
- [ ] Serve images in next-gen formats
- [ ] Properly size images
- [ ] Remove unused CSS/JS
- [ ] Minify CSS/JS
- [ ] Use efficient cache policy
- [ ] Avoid enormous network payloads