# Tasks Refresh Module

## Overview
Background task management for automated data refresh operations.

## Location
`apps/api/app/tasks_refresh.py`

## Purpose
Schedules and manages periodic data refresh tasks for market data and portfolio updates.

## Task Configuration

### Scheduled Tasks
- **Daily Refresh**: 9:30 AM EST
- **Hourly Updates**: Every hour during market hours
- **Weekly Rebalance**: Sunday night
- **Monthly Reports**: First day of month

### Task Types
- Price updates
- Portfolio calculations
- Strategy execution
- Metric calculations
- Report generation

## Implementation

### Task Queue
- Background workers
- Priority queue
- Retry mechanism
- Error handling
- Logging

### Refresh Logic
1. Check market hours
2. Fetch latest data
3. Update database
4. Calculate metrics
5. Notify clients

## Dependencies
- Celery/Redis (future)
- TwelveData service
- Database models
- Strategy service