# CORS Fix for Waardhaven Deployment

## Changes Made (2025-01-17)

### 1. Backend CORS Configuration Updated ✅
**File**: `apps/api/app/main.py`

Updated allowed origins to match actual Render deployment URLs:
```python
allowed_origins = [
    "https://waardhaven-web-frontend.onrender.com",  # Actual frontend URL
    "https://www.waardhaven-web-frontend.onrender.com",  # www variant
    # ... legacy URLs for compatibility
]
```

### 2. Frontend API URL Updated ✅
**File**: `apps/web/.env.production`

Set correct API backend URL:
```env
NEXT_PUBLIC_API_URL=https://waardhaven-api-backend.onrender.com
```

### 3. Added OPTIONS Handlers ✅
**File**: `apps/api/app/routers/auth.py`

Added explicit OPTIONS handlers for preflight requests:
```python
@router.options("/register")
@router.options("/login")
```

### 4. Added CORS Debug Logging ✅
**File**: `apps/api/app/main.py`

Added middleware to log CORS information when `CORS_DEBUG=true` is set.

## Environment Variables Required in Render

### API Backend Service (waardhaven-api-backend)
```env
# Already set by Render
DATABASE_URL=[auto-provided by Render PostgreSQL]
PORT=10000

# Must be set in Render dashboard
SECRET_KEY=[your-secret-key-32-chars-min]
ADMIN_TOKEN=[your-admin-token-32-chars-min]
TWELVEDATA_API_KEY=[your-twelvedata-api-key]

# Optional but recommended
FRONTEND_URL=https://waardhaven-web-frontend.onrender.com
SKIP_STARTUP_REFRESH=true
CORS_DEBUG=true  # Enable CORS debugging (remove after testing)
```

### Web Frontend Service (waardhaven-web-frontend)
```env
# Must be set in Render dashboard
NEXT_PUBLIC_API_URL=https://waardhaven-api-backend.onrender.com
```

## Testing After Deployment

### 1. Test CORS Preflight
```bash
curl -X OPTIONS https://waardhaven-api-backend.onrender.com/api/v1/auth/register \
  -H "Origin: https://waardhaven-web-frontend.onrender.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v
```

Expected response headers:
- `Access-Control-Allow-Origin: https://waardhaven-web-frontend.onrender.com`
- `Access-Control-Allow-Methods: *`
- `Access-Control-Allow-Headers: *`

### 2. Test Registration
```bash
curl -X POST https://waardhaven-api-backend.onrender.com/api/v1/auth/register \
  -H "Origin: https://waardhaven-web-frontend.onrender.com" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPassword123!@#"}' \
  -v
```

### 3. Check Browser Console
Navigate to https://waardhaven-web-frontend.onrender.com/register and check:
1. Network tab for API calls
2. Console for CORS errors
3. Verify API URL is correct

## Troubleshooting

### If CORS errors persist:

1. **Check API logs in Render**:
   - Look for "CORS Debug" messages
   - Verify origin is exactly `https://waardhaven-web-frontend.onrender.com`

2. **Verify environment variables**:
   ```bash
   # In API service logs, you should see:
   CORS Debug - Request from origin: https://waardhaven-web-frontend.onrender.com
   CORS Debug - Allowed origins: [...includes frontend URL...]
   ```

3. **Clear browser cache**:
   - Hard refresh (Ctrl+Shift+R)
   - Try incognito/private mode
   - Test in different browser

4. **Check preflight caching**:
   - OPTIONS requests are cached for 1 hour
   - May need to wait or use different endpoint for testing

## Database Note
PostgreSQL connection is handled automatically by Render through the `DATABASE_URL` environment variable. No additional configuration needed.

## Next Steps After Pushing

1. **Push to GitHub**:
   ```bash
   git add -A
   git commit -m "Fix CORS for actual Render deployment URLs"
   git push origin main
   ```

2. **In Render Dashboard**:
   - Verify environment variables are set
   - Trigger manual deploy if auto-deploy doesn't start
   - Monitor build logs

3. **After Deploy**:
   - Test registration at https://waardhaven-web-frontend.onrender.com/register
   - Check API logs for CORS debug messages
   - Remove `CORS_DEBUG=true` after confirming it works

## Summary
All CORS issues should be resolved with these changes. The key fixes were:
1. ✅ Matching exact frontend URL in CORS allowed origins
2. ✅ Setting correct API URL in frontend production config
3. ✅ Adding explicit OPTIONS handlers for preflight
4. ✅ Adding debug logging to troubleshoot any remaining issues