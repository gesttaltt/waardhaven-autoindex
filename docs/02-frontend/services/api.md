# API Service

## Overview
Frontend API client for backend communication.

## Location
`apps/web/app/utils/api.ts`
`apps/web/app/services/aiInsights.ts`

## Core Functions

### API Client Setup
- Base URL configuration
- Axios instance creation
- Request/response interceptors
- Error handling

### Authentication
- Token attachment
- Auto-refresh logic
- Logout on 401
- Token storage

### Request Methods
- GET requests
- POST with data
- PUT updates
- DELETE operations

## Endpoints Integration

### Portfolio Endpoints
- `/api/v1/index/*`
- `/api/v1/portfolio/*`
- `/api/v1/allocations/*`

### Market Data
- `/api/v1/prices/*`
- `/api/v1/benchmark/*`
- `/api/v1/market/*`

### User Management
- `/api/v1/auth/*`
- `/api/v1/users/*`
- `/api/v1/profile/*`

## Error Handling
- Network errors
- API errors
- Validation errors
- Timeout handling

## Response Processing
- JSON parsing
- Type conversion
- Data transformation
- Error extraction
