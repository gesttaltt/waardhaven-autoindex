# Tasks Router

## ⚠️ Implementation Status: MINIMAL
- Only manual refresh endpoint implemented
- No task management system
- No scheduling or monitoring

## Overview
Simple manual refresh endpoint requiring admin authentication.

## Location
`apps/api/app/routers/tasks.py`

## Actual Implementation

### POST /api/v1/tasks/refresh
Trigger manual data refresh (requires admin token).

**Headers:**
```
X-Admin-Token: your-admin-token
```

**Response:**
```json
{
  "status": "ok"
}
```

**Security:**
- Requires admin token in header
- Returns 401 if unauthorized

## Note on Documentation vs Reality

The extensive task management system described in the original documentation is **NOT IMPLEMENTED**. The current implementation only provides a simple admin-protected refresh endpoint.

For actual background task functionality, see:
- `/api/v1/background/*` endpoints (if Celery is configured)
- `/api/v1/manual/*` endpoints for debugging

## Related Modules
- `services/refresh.py`: Refresh logic
- `routers/background.py`: Background task endpoints (if available)
- `routers/manual_refresh.py`: Additional refresh endpoints