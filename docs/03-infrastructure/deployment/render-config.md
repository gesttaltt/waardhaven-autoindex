# Render Deployment Configuration

## Overview
Cloud deployment configuration for Render.com platform.

## Location
`render.yaml`

## Services Configured

### API Service
- Type: Web Service
- Runtime: Python 3.11
- Build: Docker
- Port: 8000
- Health check: /health

### Web Service
- Type: Static Site
- Build: Node.js 18
- Framework: Next.js
- Port: 3000
- Auto-deploy: Enabled

### Database
- Type: PostgreSQL
- Version: 14
- Plan: Starter/Standard
- Backup: Daily
- High availability: Optional

## Environment Variables

### API Environment
- DATABASE_URL (auto)
- SECRET_KEY
- TWELVEDATA_API_KEY
- NODE_ENV
- ALLOWED_ORIGINS

### Web Environment
- NEXT_PUBLIC_API_URL
- NODE_ENV
- BUILD_COMMAND

## Deployment Process
1. Git push to main
2. Render webhook triggered
3. Build process starts
4. Health checks
5. Traffic routing
6. Old version shutdown

## Scaling Options
- Horizontal scaling
- Vertical scaling
- Auto-scaling rules
- Load balancing
