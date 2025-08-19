#!/bin/bash
# Pre-tool execution hook for development environment validation
# Runs before any tool execution to ensure environment is ready

TOOL_NAME="$1"
TOOL_ARGS="$2"
CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID:-$(date +%s)}"
LOG_FILE=".claude/logs/pre-tool-$(date +%Y%m%d).log"

# Create log directory if it doesn't exist
mkdir -p ".claude/logs"

# Logging function
log() {
    echo "$(date '+%H:%M:%S') [PRE-TOOL] $1" | tee -a "$LOG_FILE"
}

log "🔧 Pre-tool check for: $TOOL_NAME"

# Environment validation
ENV_ISSUES=0

# Check if we're in the AI Investment project
if [ ! -f "CLAUDE.md" ]; then
    log "⚠️  Warning: Not in AI Investment project root"
    ENV_ISSUES=$((ENV_ISSUES + 1))
fi

# Check for required environment variables
if [ "$TOOL_NAME" = "Bash" ] && [[ "$TOOL_ARGS" == *"python"* ]]; then
    if [ -z "$DATABASE_URL" ]; then
        log "⚠️  DATABASE_URL not set for Python operations"
        ENV_ISSUES=$((ENV_ISSUES + 1))
    fi
fi

# Check for API operations
if [[ "$TOOL_ARGS" == *"api"* ]] || [[ "$TOOL_ARGS" == *"curl"* ]]; then
    # Check if API server is running
    if ! curl -s http://localhost:8000/api/v1/health >/dev/null 2>&1; then
        log "⚠️  API server not running on localhost:8000"
        log "💡 Consider running: cd apps/api && uvicorn app.main:app --reload"
        ENV_ISSUES=$((ENV_ISSUES + 1))
    fi
fi

# Check for database operations
if [[ "$TOOL_ARGS" == *"database"* ]] || [[ "$TOOL_ARGS" == *"migrate"* ]] || [[ "$TOOL_ARGS" == *"psql"* ]]; then
    log "🗄️  Database operation detected - checking backup status"
    
    # Check if recent backup exists
    if [ -d "backups/database" ]; then
        LATEST_BACKUP=$(find backups/database -name "*.sql*" -type f -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-)
        if [ ! -z "$LATEST_BACKUP" ]; then
            BACKUP_AGE=$(( $(date +%s) - $(stat -c %Y "$LATEST_BACKUP" 2>/dev/null || echo 0) ))
            if [ $BACKUP_AGE -gt 86400 ]; then # 24 hours
                log "⚠️  Latest backup is over 24 hours old"
                log "💡 Consider running: ./hooks/database/backup-before-migration.sh"
                ENV_ISSUES=$((ENV_ISSUES + 1))
            else
                log "✅ Recent backup found: $LATEST_BACKUP"
            fi
        else
            log "⚠️  No database backups found"
            ENV_ISSUES=$((ENV_ISSUES + 1))
        fi
    fi
fi

# Check for npm/node operations
if [[ "$TOOL_ARGS" == *"npm"* ]] || [[ "$TOOL_ARGS" == *"node"* ]]; then
    # Check if in correct directory
    if [[ "$TOOL_ARGS" == *"apps/web"* ]] || [ -f "package.json" ]; then
        if [ ! -d "node_modules" ]; then
            log "⚠️  node_modules not found - dependencies may not be installed"
            log "💡 Consider running: npm install"
            ENV_ISSUES=$((ENV_ISSUES + 1))
        fi
    fi
fi

# Check for Git operations
if [[ "$TOOL_ARGS" == *"git"* ]]; then
    # Check for uncommitted changes before destructive operations
    if [[ "$TOOL_ARGS" == *"reset"* ]] || [[ "$TOOL_ARGS" == *"clean"* ]]; then
        UNCOMMITTED=$(git status --porcelain | wc -l)
        if [ $UNCOMMITTED -gt 0 ]; then
            log "⚠️  $UNCOMMITTED uncommitted changes detected before destructive git operation"
            log "💡 Consider committing or stashing changes first"
            ENV_ISSUES=$((ENV_ISSUES + 1))
        fi
    fi
    
    # Check current branch for main operations
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)
    if [ "$CURRENT_BRANCH" = "main" ] && [[ "$TOOL_ARGS" == *"push"* ]]; then
        log "🌟 Pushing to main branch - ensuring quality checks"
        
        # Check if pre-deployment checks have been run recently
        if [ ! -f ".claude/cache/last-deploy-check" ] || [ $(( $(date +%s) - $(cat .claude/cache/last-deploy-check 2>/dev/null || echo 0) )) -gt 3600 ]; then
            log "💡 Consider running pre-deployment checks: ai-check"
        fi
    fi
fi

# Check for file operations that might affect critical files
if [[ "$TOOL_ARGS" == *"rm"* ]] && [[ "$TOOL_ARGS" == *".env"* ]]; then
    log "🚨 WARNING: Attempting to delete .env file"
    ENV_ISSUES=$((ENV_ISSUES + 1))
fi

# Rate limit check for external APIs
if [[ "$TOOL_ARGS" == *"curl"* ]] && [[ "$TOOL_ARGS" == *"api.twelvedata.com"* ]]; then
    # Check recent API calls
    API_CALLS_TODAY=$(grep "$(date +%Y-%m-%d)" "$LOG_FILE" 2>/dev/null | grep -c "TwelveData API" || echo 0)
    if [ $API_CALLS_TODAY -gt 450 ]; then  # 500 daily limit with buffer
        log "⚠️  TwelveData API calls today: $API_CALLS_TODAY (approaching limit)"
        ENV_ISSUES=$((ENV_ISSUES + 1))
    fi
fi

# Session tracking
echo "$TOOL_NAME|$CLAUDE_SESSION_ID|$(date +%s)" >> ".claude/session/tool-usage.log"

# Summary
if [ $ENV_ISSUES -eq 0 ]; then
    log "✅ Environment checks passed"
else
    log "⚠️  $ENV_ISSUES environment issues detected"
    log "🤖 Claude can still proceed, but consider addressing these issues"
fi

log "🏁 Pre-tool check complete for $TOOL_NAME"

# Always exit 0 - we don't want to block Claude, just warn
exit 0