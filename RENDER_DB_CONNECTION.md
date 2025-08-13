# Render Database Connection Setup

## Your Database Details
- **Database Name:** waardhaven_db_5t62
- **Username:** waardhaven_db_5t62_user
- **Hostname (Internal):** dpg-d2dpibbe5dus7390qqcg-a
- **Port:** 5432

## Setting Up DATABASE_URL in Render Dashboard

### Method 1: Automatic Connection (Recommended)
1. Go to your **waardhaven-api** service in Render Dashboard
2. Click on "Environment" tab
3. For DATABASE_URL, click "Add Environment Variable"
4. Click "Add from Database"
5. Select your database "waardhaven-db"
6. Choose "Internal Database URL" (for services in same Render account)
7. Save

### Method 2: Manual Connection String
If you need to set it manually, the DATABASE_URL format is:

**Internal Connection (between Render services):**
```
postgresql://waardhaven_db_5t62_user:[PASSWORD]@dpg-d2dpibbe5dus7390qqcg-a:5432/waardhaven_db_5t62
```

**External Connection (from local development):**
```
postgresql://waardhaven_db_5t62_user:[PASSWORD]@[EXTERNAL_HOSTNAME]:5432/waardhaven_db_5t62?ssl=require
```

## Step-by-Step Setup in Render

1. **Navigate to your API Service:**
   - Go to https://dashboard.render.com
   - Click on "waardhaven-api" service

2. **Set Environment Variables:**
   - Click "Environment" in the left sidebar
   - Add/Update these variables:

   | Key | Value | Notes |
   |-----|-------|-------|
   | DATABASE_URL | (Use "Add from Database" option) | Select waardhaven-db → Internal Database URL |
   | SECRET_KEY | (generate with: openssl rand -hex 32) | Keep this secure! |
   | ADMIN_TOKEN | your-admin-token | For manual refresh tasks |

3. **For the Web Service:**
   - Go to "waardhaven-web" service
   - Click "Environment"
   - Set:
   
   | Key | Value |
   |-----|-------|
   | NEXT_PUBLIC_API_URL | https://waardhaven-api.onrender.com | Your API service URL |

## Verify Connection

After setting up, you can verify the connection by:

1. **Check API Logs:**
   - Go to your API service
   - Click "Logs" tab
   - Look for "DB tables created" message
   - Should see "Starting uvicorn server..." if successful

2. **Test Health Endpoint:**
   ```bash
   curl https://waardhaven-api.onrender.com/health
   ```
   Should return: `{"status":"ok"}`

## Troubleshooting

### Common Issues:

1. **"Connection refused" or "Connection timeout"**
   - Ensure you're using Internal Database URL for Render services
   - External URL requires SSL and proper firewall rules

2. **"Password authentication failed"**
   - Double-check the password in Render Dashboard (Database → Connection → Password)
   - Passwords are case-sensitive

3. **"Database does not exist"**
   - Verify database name is `waardhaven_db_5t62`
   - Check you're connecting to the right database

4. **SSL Connection Issues**
   - Internal connections don't require SSL
   - External connections must use `?ssl=require` or `?sslmode=require`

## Local Development Connection

For local development, you need the external hostname:
1. Go to your database in Render Dashboard
2. Click "Connect" button
3. Copy "External Database URL"
4. Add to your local `.env` file in `apps/api/`

Example `.env` for local development:
```env
DATABASE_URL=postgresql://waardhaven_db_5t62_user:[PASSWORD]@[EXTERNAL_HOSTNAME].oregon-postgres.render.com:5432/waardhaven_db_5t62?ssl=require
SECRET_KEY=your-local-secret-key
ADMIN_TOKEN=your-local-admin-token
```

## Important Notes

- **Never commit passwords or connection strings to Git**
- The render.yaml file references the database by name, not connection string
- Render automatically injects the DATABASE_URL when using "fromDatabase" in render.yaml
- Internal connections are faster and don't count against connection limits