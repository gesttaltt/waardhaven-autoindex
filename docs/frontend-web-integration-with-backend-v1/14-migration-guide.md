# Migration Guide

## Version Migration

### From v0 to v1

#### Breaking Changes
1. **API Endpoints**: All endpoints now require `/api/v1/` prefix
2. **Authentication**: JWT tokens replaced session cookies
3. **Data Format**: Response structures updated

#### Migration Steps

1. **Update API URLs**
```typescript
// Before
const API_URL = 'http://localhost:8000';

// After
const API_URL = 'http://localhost:8000/api/v1';
```

2. **Update Authentication**
```typescript
// Before (cookies)
credentials: 'include'

// After (JWT)
headers: {
  'Authorization': `Bearer ${token}`
}
```

3. **Update Response Handling**
```typescript
// Before
const data = response;

// After
const data = response.data;
```

## Database Migration

### Using Alembic

1. **Create Migration**
```bash
cd apps/api
alembic revision --autogenerate -m "Add new column"
```

2. **Review Migration**
```python
# alembic/versions/xxx_add_new_column.py
def upgrade():
    op.add_column('users', sa.Column('last_login', sa.DateTime()))

def downgrade():
    op.drop_column('users', 'last_login')
```

3. **Apply Migration**
```bash
alembic upgrade head
```

4. **Rollback if Needed**
```bash
alembic downgrade -1
```

## Data Migration

### Export/Import Data

1. **Export Current Data**
```bash
# Export to JSON
pg_dump --data-only --format=plain --inserts $DATABASE_URL > data.sql

# Or use custom script
python scripts/export_data.py > data.json
```

2. **Transform Data**
```python
# scripts/transform_data.py
import json

with open('data.json') as f:
    old_data = json.load(f)

new_data = {
    'users': [transform_user(u) for u in old_data['users']],
    'portfolios': [transform_portfolio(p) for p in old_data['portfolios']]
}

with open('data_v2.json', 'w') as f:
    json.dump(new_data, f)
```

3. **Import Transformed Data**
```python
# scripts/import_data.py
from app.models import User, Portfolio
from app.core.database import SessionLocal

db = SessionLocal()

with open('data_v2.json') as f:
    data = json.load(f)

for user_data in data['users']:
    user = User(**user_data)
    db.add(user)

db.commit()
```

## Code Migration

### Component Migration

1. **Class to Function Components**
```typescript
// Before (Class)
class Dashboard extends Component {
  state = { data: null };
  
  componentDidMount() {
    this.loadData();
  }
  
  render() {
    return <div>{this.state.data}</div>;
  }
}

// After (Function)
const Dashboard = () => {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    loadData();
  }, []);
  
  return <div>{data}</div>;
};
```

2. **Redux to React Query**
```typescript
// Before (Redux)
const mapStateToProps = (state) => ({
  portfolio: state.portfolio
});

// After (React Query)
const { data: portfolio } = useQuery({
  queryKey: ['portfolio'],
  queryFn: fetchPortfolio
});
```

## Dependency Updates

### Package Updates
```bash
# Check outdated packages
npm outdated

# Update minor versions
npm update

# Update major versions (carefully)
npm install package@latest

# Update all dependencies
npx npm-check-updates -u
npm install
```

### Breaking Package Changes

1. **React Router v5 to v6**
```typescript
// Before
<Route path="/dashboard" component={Dashboard} />

// After
<Route path="/dashboard" element={<Dashboard />} />
```

2. **Axios to Fetch**
```typescript
// Before (Axios)
const { data } = await axios.get('/api/data');

// After (Fetch)
const response = await fetch('/api/data');
const data = await response.json();
```

## Environment Migration

### Local to Production

1. **Environment Variables**
```bash
# Copy template
cp .env.example .env.production

# Update values
NEXT_PUBLIC_API_URL=https://api.waardhaven.com
NODE_ENV=production
```

2. **Database Migration**
```bash
# Backup local database
pg_dump local_db > backup.sql

# Restore to production
psql $PRODUCTION_DATABASE_URL < backup.sql
```

3. **File Storage**
```bash
# Migrate uploaded files to cloud storage
aws s3 sync ./uploads s3://waardhaven-uploads/
```

## Rollback Strategy

### Application Rollback

1. **Immediate Rollback**
```bash
# Render.com
render rollback --service waardhaven-web

# Or git revert
git revert HEAD
git push origin main
```

2. **Database Rollback**
```bash
# Rollback migration
alembic downgrade -1

# Restore from backup
psql $DATABASE_URL < backup_20240118.sql
```

### Feature Flags
```typescript
// Use feature flags for gradual rollout
const features = {
  newDashboard: process.env.FEATURE_NEW_DASHBOARD === 'true',
  v2Api: process.env.FEATURE_V2_API === 'true',
};

if (features.newDashboard) {
  return <NewDashboard />;
} else {
  return <OldDashboard />;
}
```

## Testing Migration

### Migration Testing Checklist
- [ ] Backup all data
- [ ] Test in staging environment
- [ ] Run automated tests
- [ ] Manual testing of critical paths
- [ ] Performance benchmarks
- [ ] Load testing
- [ ] Security scan
- [ ] Rollback procedure tested

### Staging Environment
```bash
# Deploy to staging
git push staging main

# Run tests against staging
npm run test:e2e -- --baseUrl=https://staging.waardhaven.com

# Verify data integrity
python scripts/verify_migration.py --env=staging
```

## Post-Migration

### Monitoring
```typescript
// Monitor for errors
window.addEventListener('error', (event) => {
  logToMonitoring({
    error: event.error,
    version: 'v1',
    migration: true
  });
});
```

### Cleanup
```bash
# Remove old code
git rm -r legacy/

# Remove unused dependencies
npm prune

# Clean docker images
docker system prune -a

# Archive old backups
tar -czf backups_v0.tar.gz backups_v0/
rm -rf backups_v0/
```

## Migration Timeline

1. **Week 1**: Development environment
2. **Week 2**: Staging environment
3. **Week 3**: Production (10% users)
4. **Week 4**: Production (50% users)
5. **Week 5**: Production (100% users)
6. **Week 6**: Cleanup and optimization