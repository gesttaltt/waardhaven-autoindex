#!/bin/bash
# Context awareness hook for AI Investment project
# Provides context-aware suggestions based on current development activity

CURRENT_CONTEXT="$1"  # current_file, task, or session
CONTEXT_DATA="$2"     # file path, task name, or session info
LOG_FILE=".claude/logs/context-$(date +%Y%m%d).log"

# Create necessary directories
mkdir -p ".claude/logs" ".claude/cache" ".claude/session"

# Logging function
log() {
    echo "$(date '+%H:%M:%S') [CONTEXT] $1" | tee -a "$LOG_FILE"
}

log "🧠 Context analysis: $CURRENT_CONTEXT"

# Context-aware suggestions array
SUGGESTIONS=()
CONTEXT_INFO=()
QUICK_ACTIONS=()

case "$CURRENT_CONTEXT" in
    "current_file")
        FILE_PATH="$CONTEXT_DATA"
        log "📁 Analyzing current file: $FILE_PATH"
        
        # Determine project area and provide relevant context
        if [[ "$FILE_PATH" == *"apps/api"* ]]; then
            CONTEXT_INFO+=("🔧 Backend Development Context")
            CONTEXT_INFO+=("  Current API Structure: FastAPI with SQLAlchemy")
            CONTEXT_INFO+=("  Database: PostgreSQL (prod) / SQLite (dev)")
            CONTEXT_INFO+=("  Key Services: calculation, market_data, auth")
            
            QUICK_ACTIONS+=("Start API server: ai-backend")
            QUICK_ACTIONS+=("Run API tests: ai-test-api")
            QUICK_ACTIONS+=("Check API health: ai-api")
            QUICK_ACTIONS+=("Monitor performance: ai-monitor")
            
            # File-specific context
            if [[ "$FILE_PATH" == *"models"* ]]; then
                SUGGESTIONS+=("Database model detected - consider migrations if schema changed")
                SUGGESTIONS+=("Related files: services/, routers/, tests/")
                QUICK_ACTIONS+=("Check database: ai-db")
            elif [[ "$FILE_PATH" == *"routers"* ]]; then
                SUGGESTIONS+=("API router detected - update OpenAPI docs if endpoints changed")
                SUGGESTIONS+=("Test endpoints with: curl http://localhost:8000/api/v1/...")
                QUICK_ACTIONS+=("View API docs: http://localhost:8000/docs")
            elif [[ "$FILE_PATH" == *"services"* ]]; then
                SUGGESTIONS+=("Business logic service - ensure proper error handling")
                SUGGESTIONS+=("Consider caching for expensive operations")
                if [[ "$FILE_PATH" == *"calculation"* ]]; then
                    SUGGESTIONS+=("Financial calculations - verify with test data")
                    SUGGESTIONS+=("Consider decimal precision for monetary values")
                fi
            fi
            
        elif [[ "$FILE_PATH" == *"apps/web"* ]]; then
            CONTEXT_INFO+=("🌐 Frontend Development Context")
            CONTEXT_INFO+=("  Framework: Next.js 14 with React 18")
            CONTEXT_INFO+=("  Styling: Tailwind CSS")
            CONTEXT_INFO+=("  Charts: Recharts for financial visualizations")
            
            QUICK_ACTIONS+=("Start dev server: ai-frontend")
            QUICK_ACTIONS+=("Run frontend tests: ai-test-web")
            QUICK_ACTIONS+=("Type check: ai-types")
            QUICK_ACTIONS+=("Lint code: npm run lint")
            
            if [[ "$FILE_PATH" == *"components"* ]]; then
                SUGGESTIONS+=("React component - ensure proper TypeScript types")
                SUGGESTIONS+=("Consider component reusability and props interface")
                if [[ "$FILE_PATH" == *"chart"* ]] || [[ "$FILE_PATH" == *"graph"* ]]; then
                    SUGGESTIONS+=("Financial chart component - verify data formatting")
                    SUGGESTIONS+=("Consider loading states for data fetching")
                fi
            elif [[ "$FILE_PATH" == *"app/"* ]]; then
                SUGGESTIONS+=("Next.js page/layout - check routing and metadata")
                SUGGESTIONS+=("Ensure proper SEO and accessibility")
            fi
            
        elif [[ "$FILE_PATH" == *"docs"* ]]; then
            CONTEXT_INFO+=("📚 Documentation Context")
            CONTEXT_INFO+=("  Project documentation structure")
            CONTEXT_INFO+=("  Markdown files with cross-references")
            
            QUICK_ACTIONS+=("Validate docs: python .claude/hooks/find-duplicates.py")
            QUICK_ACTIONS+=("Check links: run link validation")
            QUICK_ACTIONS+=("View TODO: ai-status")
            
            SUGGESTIONS+=("Documentation change - ensure accuracy with code")
            SUGGESTIONS+=("Update related docs if API/features changed")
            
        elif [[ "$FILE_PATH" == *"hooks"* ]]; then
            CONTEXT_INFO+=("🪝 Development Hooks Context")
            CONTEXT_INFO+=("  Project automation and safety scripts")
            
            QUICK_ACTIONS+=("Test hook: chmod +x && ./script")
            QUICK_ACTIONS+=("Check hook logs: tail -f .claude/logs/")
            
            SUGGESTIONS+=("Hook script - ensure proper error handling")
            SUGGESTIONS+=("Test hook functionality before committing")
        fi
        
        # Check related files
        if [[ "$FILE_PATH" == *.py ]]; then
            TEST_FILE="${FILE_PATH/app\//tests/test_}"
            if [ -f "$TEST_FILE" ]; then
                CONTEXT_INFO+=("  📝 Related test file: $TEST_FILE")
            else
                SUGGESTIONS+=("Consider creating test file: $TEST_FILE")
            fi
        fi
        ;;
        
    "task")
        TASK_NAME="$CONTEXT_DATA"
        log "📋 Task context: $TASK_NAME"
        
        # Analyze task type and provide relevant context
        if [[ "$TASK_NAME" == *"api"* ]] || [[ "$TASK_NAME" == *"endpoint"* ]]; then
            CONTEXT_INFO+=("🔧 API Development Task")
            QUICK_ACTIONS+=("Start API server: ai-backend")
            QUICK_ACTIONS+=("Test endpoints: ai-api")
            SUGGESTIONS+=("API task - ensure proper error handling and validation")
            SUGGESTIONS+=("Update API documentation after changes")
        fi
        
        if [[ "$TASK_NAME" == *"frontend"* ]] || [[ "$TASK_NAME" == *"ui"* ]]; then
            CONTEXT_INFO+=("🌐 Frontend Development Task")
            QUICK_ACTIONS+=("Start dev server: ai-frontend")
            QUICK_ACTIONS+=("Check types: ai-types")
            SUGGESTIONS+=("Frontend task - test responsive design")
            SUGGESTIONS+=("Ensure accessibility compliance")
        fi
        
        if [[ "$TASK_NAME" == *"database"* ]] || [[ "$TASK_NAME" == *"migration"* ]]; then
            CONTEXT_INFO+=("🗄️  Database Task")
            QUICK_ACTIONS+=("Backup database: ai-backup")
            QUICK_ACTIONS+=("Check DB health: ai-db")
            SUGGESTIONS+=("Database task - create backup before changes")
            SUGGESTIONS+=("Test migration on development database first")
        fi
        
        if [[ "$TASK_NAME" == *"test"* ]] || [[ "$TASK_NAME" == *"bug"* ]]; then
            CONTEXT_INFO+=("🧪 Testing/Bug Fix Task")
            QUICK_ACTIONS+=("Run tests: ai-test-api && ai-test-web")
            QUICK_ACTIONS+=("Check logs: ai-logs")
            SUGGESTIONS+=("Testing task - ensure comprehensive coverage")
            SUGGESTIONS+=("Create regression test for bug fixes")
        fi
        ;;
        
    "session")
        SESSION_INFO="$CONTEXT_DATA"
        log "🎯 Session context analysis"
        
        # Analyze current session activity
        if [ -f ".claude/session/tool-usage.log" ]; then
            RECENT_TOOLS=$(tail -10 ".claude/session/tool-usage.log" | cut -d'|' -f1 | sort | uniq -c | sort -nr)
            CONTEXT_INFO+=("📊 Recent Session Activity:")
            while IFS= read -r line; do
                CONTEXT_INFO+=("  $line")
            done <<< "$RECENT_TOOLS"
        fi
        
        # Check for patterns in recent activity
        if [ -f ".claude/cache/file-change-history" ]; then
            RECENT_CHANGES=$(tail -20 ".claude/cache/file-change-history" | cut -d'|' -f2 | xargs dirname | sort | uniq -c | sort -nr | head -3)
            if [ ! -z "$RECENT_CHANGES" ]; then
                CONTEXT_INFO+=("📁 Most Active Directories:")
                while IFS= read -r line; do
                    CONTEXT_INFO+=("  $line")
                done <<< "$RECENT_CHANGES"
            fi
        fi
        
        # Session-based suggestions
        SESSION_START_TIME=$(cat ".claude/session/start-time" 2>/dev/null || echo $(date +%s))
        SESSION_DURATION=$(( $(date +%s) - SESSION_START_TIME ))
        
        if [ $SESSION_DURATION -gt 7200 ]; then  # 2 hours
            SUGGESTIONS+=("Long session detected - consider taking a break")
            SUGGESTIONS+=("Review progress: ai-status")
        fi
        
        if [ $SESSION_DURATION -gt 3600 ]; then  # 1 hour
            SUGGESTIONS+=("Consider running comprehensive checks: ai-check")
            SUGGESTIONS+=("Review any pending suggestions in .claude/cache/")
        fi
        ;;
esac

# AI Investment project specific context
if [ -f "CLAUDE.md" ]; then
    # Check current TODO status
    if [ -f "docs/TODO-MVP/README.md" ]; then
        CURRENT_TASK=$(grep "Working on:" "docs/TODO-MVP/README.md" | sed 's/Working on: //')
        if [ "$CURRENT_TASK" != "None" ] && [ ! -z "$CURRENT_TASK" ]; then
            CONTEXT_INFO+=("🎯 Current Focus: $CURRENT_TASK")
            QUICK_ACTIONS+=("Complete task: ai-complete \"$CURRENT_TASK\"")
        fi
        
        # Check for critical tasks
        if [ -d "docs/TODO-MVP/BACKLOG/P0-CRITICAL" ]; then
            P0_COUNT=$(find "docs/TODO-MVP/BACKLOG/P0-CRITICAL" -name "*.md" 2>/dev/null | wc -l)
            if [ $P0_COUNT -gt 0 ]; then
                CONTEXT_INFO+=("🚨 Critical Tasks: $P0_COUNT P0 items need attention")
                QUICK_ACTIONS+=("View priorities: ai-status")
            fi
        fi
    fi
    
    # Check system health
    if [ -f ".claude/cache/project-health.json" ]; then
        HEALTH_AGE=$(( $(date +%s) - $(stat -c %Y ".claude/cache/project-health.json" 2>/dev/null || echo 0) ))
        if [ $HEALTH_AGE -gt 3600 ]; then  # 1 hour old
            SUGGESTIONS+=("Project health data is stale - consider running health check")
            QUICK_ACTIONS+=("Health check: python .claude/hooks/intelligence/ai-investment-analyzer.py health")
        fi
    fi
    
    # Financial domain specific context
    CONTEXT_INFO+=("💰 AI Investment Project Domain:")
    CONTEXT_INFO+=("  • Portfolio management and index creation")
    CONTEXT_INFO+=("  • Real-time market data integration")
    CONTEXT_INFO+=("  • Financial calculations and risk metrics")
    CONTEXT_INFO+=("  • External APIs: TwelveData, MarketAux")
fi

# Environmental context
CONTEXT_INFO+=("🔧 Environment Status:")

# Check if services are running
if curl -s http://localhost:8000/api/v1/health >/dev/null 2>&1; then
    CONTEXT_INFO+=("  ✅ API Server: Running")
else
    CONTEXT_INFO+=("  ❌ API Server: Not running")
    QUICK_ACTIONS+=("Start API: ai-backend")
fi

if curl -s http://localhost:3000 >/dev/null 2>&1; then
    CONTEXT_INFO+=("  ✅ Frontend: Running")
else
    CONTEXT_INFO+=("  ❌ Frontend: Not running")
    QUICK_ACTIONS+=("Start frontend: ai-frontend")
fi

# Redis status
if command -v redis-cli >/dev/null 2>&1 && redis-cli ping >/dev/null 2>&1; then
    CONTEXT_INFO+=("  ✅ Redis Cache: Active")
else
    CONTEXT_INFO+=("  ⚠️  Redis Cache: Inactive")
fi

# Output context information
log "🔍 Context Information:"
for info in "${CONTEXT_INFO[@]}"; do
    log "$info"
done

if [ ${#SUGGESTIONS[@]} -gt 0 ]; then
    log "💡 Context-Aware Suggestions:"
    for suggestion in "${SUGGESTIONS[@]}"; do
        log "  • $suggestion"
    done
fi

if [ ${#QUICK_ACTIONS[@]} -gt 0 ]; then
    log "⚡ Quick Actions:"
    for action in "${QUICK_ACTIONS[@]}"; do
        log "  • $action"
    done
fi

# Save context for Claude reference
CONTEXT_FILE=".claude/cache/current-context.json"
cat > "$CONTEXT_FILE" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "context_type": "$CURRENT_CONTEXT",
  "context_data": "$CONTEXT_DATA",
  "suggestions": $(printf '%s\n' "${SUGGESTIONS[@]}" | jq -R . | jq -s .),
  "quick_actions": $(printf '%s\n' "${QUICK_ACTIONS[@]}" | jq -R . | jq -s .),
  "environment_status": {
    "api_running": $(curl -s http://localhost:8000/api/v1/health >/dev/null 2>&1 && echo true || echo false),
    "frontend_running": $(curl -s http://localhost:3000 >/dev/null 2>&1 && echo true || echo false),
    "redis_active": $(command -v redis-cli >/dev/null 2>&1 && redis-cli ping >/dev/null 2>&1 && echo true || echo false)
  }
}
EOF

log "✅ Context analysis complete - saved to $CONTEXT_FILE"

exit 0