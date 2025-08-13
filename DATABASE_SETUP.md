# Database Configuration Guide

## Render Database Setup

### Automatic Setup (via render.yaml)
The database is automatically provisioned when you deploy using the `render.yaml` file:
- Database name: `waardhaven-db`
- Database type: PostgreSQL
- Plan: Starter
- Database name: `waardhaven`
- User: `waardhaven_user`

### Manual Setup in Render Dashboard

1. **Create Database Service:**
   - Go to your Render Dashboard
   - Click "New +" → "PostgreSQL"
   - Name: `waardhaven-db`
   - Database: `waardhaven`
   - User: `waardhaven_user`
   - Region: Same as your API service
   - Plan: Starter (or higher)
   - Click "Create Database"

2. **Connect Database to API Service:**
   - Go to your API service (`waardhaven-api`)
   - Click "Environment" tab
   - Add/Update `DATABASE_URL`:
     - Click "Add Environment Variable"
     - Key: `DATABASE_URL`
     - Value: Click "Add from Database" → Select `waardhaven-db` → "Internal Connection String"
   
3. **Set Other Required Environment Variables:**
   ```
   SECRET_KEY=<generate-a-secure-random-string>
   ADMIN_TOKEN=<your-admin-token>
   ```

## Local Development Setup

1. **PostgreSQL Installation:**
   ```bash
   # macOS
   brew install postgresql
   brew services start postgresql

   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   sudo systemctl start postgresql

   # Windows
   # Download from https://www.postgresql.org/download/windows/
   ```

2. **Create Local Database:**
   ```bash
   createdb waardhaven
   ```

3. **Create .env file in apps/api/:**
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/waardhaven
   SECRET_KEY=your-local-secret-key
   ADMIN_TOKEN=your-local-admin-token
   ```

4. **Initialize Database Tables:**
   ```bash
   cd apps/api
   python -m app.db_init
   ```

5. **Seed Initial Assets:**
   ```bash
   python -m app.seed_assets
   ```

## Database Schema

### Tables:
- **users**: User accounts (email, password_hash)
- **assets**: Stock/ETF information (symbol, name, sector)
- **prices**: Historical price data
- **index_values**: Calculated index values over time
- **allocations**: Asset weightings in the index
- **orders**: User trading orders

### Automatic Initialization
The API automatically initializes the database on startup:
1. Creates all tables if they don't exist
2. Seeds initial asset data
3. Starts the API server

## Connection String Format

### PostgreSQL (Production - Render):
```
postgresql://[user]:[password]@[host]/[database]?sslmode=require
```

### PostgreSQL (Local Development):
```
postgresql://username:password@localhost:5432/waardhaven
```

## Troubleshooting

### Common Issues:

1. **"Database connection failed"**
   - Verify DATABASE_URL is set correctly
   - Check database service is running
   - Ensure network connectivity between services

2. **"Table doesn't exist"**
   - Run database initialization: `python -m app.db_init`
   - Check migrations ran successfully

3. **"Permission denied"**
   - Verify database user has correct permissions
   - Check connection string credentials

4. **SSL Connection Issues (Render)**
   - Ensure `?sslmode=require` is in the connection string
   - Render databases require SSL connections

## Database Migrations

Currently using SQLAlchemy's `create_all()` for simplicity. For production, consider using Alembic:

```bash
# Future migration setup
pip install alembic
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Backup & Restore

### Render Dashboard:
- Go to your database service
- Click "Backups" tab
- Create manual backup or restore from existing

### Manual Backup:
```bash
pg_dump DATABASE_URL > backup.sql
```

### Manual Restore:
```bash
psql DATABASE_URL < backup.sql
```

## Security Notes

1. **Never commit .env files** - Already in .gitignore
2. **Use strong SECRET_KEY** - Generate with: `openssl rand -hex 32`
3. **Rotate credentials regularly**
4. **Use environment-specific databases** (dev/staging/prod)
5. **Enable SSL for production connections**