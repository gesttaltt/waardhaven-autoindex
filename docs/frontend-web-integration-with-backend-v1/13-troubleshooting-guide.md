# Troubleshooting Guide

## Common Issues & Solutions

### Authentication Issues

#### Token Expired
**Symptom**: User redirected to login unexpectedly
```typescript
// Solution: Check token refresh logic
const tokenManager = TokenManager.getInstance();
const token = tokenManager.getAccessToken();
if (!token) {
  // Token expired, try refresh
  await authRepository.refreshToken();
}
```

#### CORS Errors
**Symptom**: `Access-Control-Allow-Origin` errors
```typescript
// Backend fix
app.use(cors({
  origin: process.env.FRONTEND_URL,
  credentials: true,
}));
```

### API Connection Issues

#### Network Errors
**Symptom**: `Failed to fetch` errors
```typescript
// Check API URL
console.log('API URL:', process.env.NEXT_PUBLIC_API_URL);

// Test connection
curl -I https://api.waardhaven.com/health
```

#### 500 Server Errors
**Check backend logs**
```bash
render logs --service waardhaven-api --tail
```

### Build Issues

#### TypeScript Errors
```bash
# Clear cache and rebuild
rm -rf .next node_modules
npm ci
npm run build
```

#### Module Not Found
```bash
# Check imports
npm ls [package-name]

# Reinstall dependencies
npm ci
```

### Performance Issues

#### Slow Initial Load
```typescript
// Check bundle size
npm run build:analyze

// Implement code splitting
const HeavyComponent = dynamic(() => import('./HeavyComponent'));
```

#### Memory Leaks
```typescript
// Clean up effects
useEffect(() => {
  const timer = setInterval(fetchData, 1000);
  return () => clearInterval(timer); // Cleanup
}, []);
```

### State Management Issues

#### Stale Data
```typescript
// Force refetch
queryClient.invalidateQueries({ queryKey: ['portfolio'] });

// Or use refetch interval
useQuery({
  queryKey: ['portfolio'],
  queryFn: fetchPortfolio,
  refetchInterval: 60000, // 1 minute
});
```

### Database Issues

#### Connection Pool Exhausted
```sql
-- Check connections
SELECT count(*) FROM pg_stat_activity;

-- Kill idle connections
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' AND state_change < NOW() - INTERVAL '10 minutes';
```

## Debugging Tools

### Browser DevTools
```javascript
// Debug API calls
window.addEventListener('fetch', (e) => {
  console.log('Fetch:', e.request.url);
});

// Performance profiling
performance.mark('start');
// ... code ...
performance.mark('end');
performance.measure('operation', 'start', 'end');
```

### React DevTools
- Install React Developer Tools extension
- Use Profiler tab for performance analysis
- Check component props and state

### Network Debugging
```bash
# Check API availability
curl -v https://api.waardhaven.com/health

# Test with specific headers
curl -H "Authorization: Bearer TOKEN" https://api.waardhaven.com/api/v1/index/current
```

## Log Analysis

### Frontend Logs
```typescript
// Enable debug logging
localStorage.setItem('debug', '*');

// Custom logger
const debug = require('debug')('app:component');
debug('Rendering with props:', props);
```

### Backend Logs
```python
# Check Render logs
render logs --service waardhaven-api --since 1h

# SSH into service (if available)
render ssh --service waardhaven-api
```

## Environment Issues

### Missing Environment Variables
```bash
# Check loaded env vars
console.log(process.env);

# Verify in Render dashboard
render env --service waardhaven-web
```

### Wrong Environment
```typescript
// Check environment
console.log('Environment:', process.env.NODE_ENV);
console.log('API URL:', process.env.NEXT_PUBLIC_API_URL);
```

## Recovery Procedures

### Clear Application State
```typescript
// Clear all storage
localStorage.clear();
sessionStorage.clear();

// Clear React Query cache
queryClient.clear();

// Force reload
window.location.reload();
```

### Database Recovery
```sql
-- Backup before recovery
pg_dump $DATABASE_URL > backup.sql

-- Restore from backup
psql $DATABASE_URL < backup.sql

-- Reset sequences
SELECT setval(pg_get_serial_sequence('table_name', 'id'), MAX(id)) FROM table_name;
```

## Error Reporting

### Capture Errors
```typescript
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error);
  // Send to monitoring service
  logError(event.error);
});

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
});
```

## Quick Fixes

### Reset Development Environment
```bash
# Clean everything
rm -rf .next node_modules package-lock.json
npm install
npm run dev
```

### Fix Permission Issues
```bash
# Fix file permissions
chmod -R 755 .
chmod 600 .env.local
```

### Clear CDN Cache
```bash
# Purge CDN cache (if using Cloudflare)
curl -X POST "https://api.cloudflare.com/client/v4/zones/ZONE_ID/purge_cache" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}'
```

## Health Checks

### API Health
```typescript
// Check API health
fetch('/api/health')
  .then(res => res.json())
  .then(data => console.log('API Health:', data));
```

### Database Health
```sql
-- Check database status
SELECT version();
SELECT current_database();
SELECT count(*) FROM pg_stat_activity;
```

## Contact Support

If issues persist:
1. Check documentation
2. Search GitHub issues
3. Contact support with:
   - Error messages
   - Browser console logs
   - Network requests (HAR file)
   - Steps to reproduce