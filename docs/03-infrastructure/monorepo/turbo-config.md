# Turborepo Configuration

## Overview
Monorepo management using Turborepo for efficient builds and development.

## Current Setup

### turbo.json Configuration
Root configuration file for Turborepo pipeline.

```json
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    },
    "dev": {
      "cache": false
    },
    "lint": {
      "outputs": []
    },
    "test": {
      "outputs": ["coverage/**"],
      "dependsOn": ["build"]
    }
  }
}
```

## Workspace Structure

### Root Package.json
```json
{
  "name": "ai-investment",
  "private": true,
  "workspaces": [
    "apps/*",
    "packages/*"
  ],
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint"
  }
}
```

### Workspace Layout
```
AI-Investment/
├── apps/
│   ├── api/         # FastAPI backend
│   └── web/         # Next.js frontend
├── packages/        # Shared packages (future)
│   ├── ui/         # Shared components
│   ├── utils/      # Shared utilities
│   └── types/      # TypeScript types
├── turbo.json      # Turborepo config
└── package.json    # Root package.json
```

## Pipeline Configuration

### Build Pipeline
- Topological ordering
- Dependency graph resolution
- Parallel execution
- Cache optimization
- Output caching

### Development Pipeline
- Parallel dev servers
- Hot module replacement
- Shared dependencies
- Port management
- Log aggregation

## Caching Strategy

### Local Caching
- File-based cache
- Content hashing
- Incremental builds
- Cache restoration
- Automatic invalidation

### Remote Caching (Future)
- Vercel Remote Cache
- Team sharing
- CI/CD integration
- Cloud storage
- Cache statistics

## Task Orchestration

### Parallel Tasks
```bash
# Run all dev servers in parallel
turbo run dev

# Build all apps
turbo run build

# Run tests across workspaces
turbo run test
```

### Filtered Execution
```bash
# Run only API tasks
turbo run dev --filter=api

# Build only web app
turbo run build --filter=web

# Test changed packages
turbo run test --filter='...[HEAD^]'
```

## Performance Benefits

### Build Performance
- Incremental builds: 10x faster
- Parallel execution: 3x faster
- Cache hits: <1 second
- Fresh builds: Optimized
- CI/CD: 50% reduction

### Development Experience
- Instant starts with cache
- Parallel development
- Shared hot reload
- Unified commands
- Consistent tooling

## Dependency Management

### Shared Dependencies
- Hoisted to root
- Version consistency
- Reduced duplication
- Smaller node_modules
- Faster installs

### Workspace Dependencies
```json
{
  "dependencies": {
    "@workspace/ui": "*",
    "@workspace/utils": "*",
    "@workspace/types": "*"
  }
}
```

## Scripts Organization

### Root Scripts
- `dev` - Start all dev servers
- `build` - Build all apps
- `test` - Run all tests
- `lint` - Lint all code
- `clean` - Clean all outputs

### App-Specific Scripts
- `dev:api` - Start API only
- `dev:web` - Start web only
- `build:api` - Build API
- `build:web` - Build web
- `deploy` - Deploy all

## Environment Configuration

### Environment Files
```
.env                 # Shared variables
apps/api/.env       # API-specific
apps/web/.env.local # Web-specific
```

### Variable Inheritance
- Root variables shared
- App overrides allowed
- Build-time injection
- Runtime configuration
- Secret management

## CI/CD Integration

### GitHub Actions
```yaml
- name: Setup Turbo
  uses: actions/setup-node@v3
  
- name: Install
  run: npm install
  
- name: Build
  run: npm run build
  env:
    TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
    TURBO_TEAM: ${{ secrets.TURBO_TEAM }}
```

### Optimization
- Remote caching
- Parallel jobs
- Dependency caching
- Artifact storage
- Incremental deploys

## Development Workflow

### Starting Development
```bash
# Install dependencies
npm install

# Start all services
npm run dev

# Or start specific service
npm run dev --filter=web
```

### Building for Production
```bash
# Build all apps
npm run build

# Build specific app
npm run build --filter=api

# Build with analysis
npm run build -- --profile
```

## Troubleshooting

### Common Issues
- Port conflicts
- Cache corruption
- Dependency conflicts
- Build failures
- Memory issues

### Solutions
- Clear cache: `turbo run clean`
- Reset deps: `rm -rf node_modules`
- Check ports: `lsof -i :3000`
- Verbose mode: `--verbose`
- Debug mode: `--debug`

## Future Enhancements

### Planned Features
- Remote caching setup
- Custom tasks
- Plugin system
- Better filtering
- Performance monitoring

### Package Extraction
- Shared UI components
- Common utilities
- Type definitions
- Configuration
- Testing utilities

## Best Practices

### Workspace Organization
- Logical grouping
- Clear boundaries
- Shared code extraction
- Consistent naming
- Documentation

### Performance Tips
- Use caching effectively
- Minimize dependencies
- Optimize build outputs
- Parallel execution
- Incremental updates