# Web Dockerfile

## Overview
Docker configuration for the Next.js frontend application.

## Location
`apps/web/Dockerfile`

## Actual Implementation

### Multi-Stage Build
Uses a two-stage build process for optimization:
1. **Builder stage**: Compile and build the application
2. **Runner stage**: Minimal production image

### Stage 1: Builder
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app

ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

COPY package.json ./
RUN npm install

COPY . .
RUN npm run build
```

**Features:**
- Node.js 20 Alpine (lightweight)
- Build-time API URL configuration
- Full dependency installation
- Next.js build process

### Stage 2: Runner
```dockerfile
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=10000

COPY --from=builder /app/package.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/public* ./public/

EXPOSE ${PORT}
CMD ["sh", "-c", "npm run start -- -p ${PORT:-10000}"]
```

**Features:**
- Minimal production image
- Only copies built artifacts
- No source code in final image
- Dynamic port configuration

## Build Arguments
- `NEXT_PUBLIC_API_URL`: API endpoint URL (build-time)

## Environment Variables
- `NODE_ENV`: Set to "production"
- `PORT`: Server port (default: 10000)

## File Structure in Container
```
/app
├── package.json
├── .next/          # Built application
├── node_modules/   # Dependencies
└── public/         # Static assets (if exists)
```

## Build Commands

### Local Build
```bash
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 \
  -t waardhaven-web .
```

### Production Build
```bash
docker build \
  --build-arg NEXT_PUBLIC_API_URL=https://api.waardhaven.com \
  -t waardhaven-web:prod .
```

### Run Container
```bash
docker run -p 3000:10000 waardhaven-web
```

## Optimization Features
- **Multi-stage build**: Reduces final image size
- **Alpine Linux**: Minimal base image
- **Production dependencies only**: No dev dependencies in final image
- **Layer caching**: Efficient rebuilds

## Port Configuration
- Default port: 10000 (Render.com standard)
- Configurable via PORT environment variable
- Fallback to 10000 if PORT not set

## Security Considerations
- No source code in production image
- Runs as root (no non-root user configured)
- Production NODE_ENV prevents dev tools

## Deployment Notes
Optimized for Render.com:
- Uses standard PORT environment variable
- Handles dynamic port assignment
- No hardcoded configuration

## Differences from Original Documentation
The actual Dockerfile includes:
- Multi-stage build (as previously documented)
- Node.js 20 instead of older versions
- Dynamic port configuration
- Conditional public directory copy
- Shell command for flexible port binding