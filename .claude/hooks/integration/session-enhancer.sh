#!/bin/bash
# Session enhancement hook - provides context and session management
# Integrates with Claude Code sessions for enhanced development experience

HOOK_TYPE="$1"  # session_start, session_end, prompt_submit, tool_use
CONTEXT_DATA="$2"  # additional context based on hook type

LOG_FILE=".claude/logs/session-$(date +%Y%m%d).log"
CACHE_DIR=".claude/cache"
SESSION_DIR=".claude/session"

# Create necessary directories
mkdir -p ".claude/logs" "$CACHE_DIR" "$SESSION_DIR"

# Logging function
log() {
    echo "$(date '+%H:%M:%S') [SESSION] $1" | tee -a "$LOG_FILE"
}

case "$HOOK_TYPE" in
    "session_start")
        log "🚀 Claude Code session starting"
        
        # Record session start
        echo "$(date +%s)" > "$SESSION_DIR/start-time"
        echo "session-started|$(date +%s)" >> "$SESSION_DIR/activity.log"
        
        # Show project context
        log "📋 Project Context Loading..."
        
        # Project identification
        if [ -f "CLAUDE.md" ]; then
            PROJECT_NAME=$(grep "PROJECT_NAME" CLAUDE.md | cut -d'"' -f2 2>/dev/null || echo "AI Investment Project")
            log "🏗️  Project: $PROJECT_NAME"
        fi
        
        # Active TODOs count
        if [ -f "docs/TODO-MVP/README.md" ]; then
            CURRENT_TASK=$(grep "Working on:" "docs/TODO-MVP/README.md" | sed 's/Working on: //')
            if [ "$CURRENT_TASK" != "None" ] && [ ! -z "$CURRENT_TASK" ]; then
                log "🎯 Current Focus: $CURRENT_TASK"
            fi
            
            # Count critical tasks
            if [ -d "docs/TODO-MVP/BACKLOG/P0-CRITICAL" ]; then
                P0_COUNT=$(find "docs/TODO-MVP/BACKLOG/P0-CRITICAL" -name "*.md" 2>/dev/null | wc -l)
                P1_COUNT=$(find "docs/TODO-MVP/BACKLOG/P1-CORE-MVP" -name "*.md" 2>/dev/null | wc -l)
                log "📊 Active TODOs: $P0_COUNT critical, $P1_COUNT core MVP"
                
                if [ $P0_COUNT -gt 0 ]; then
                    log "🚨 $P0_COUNT critical tasks need attention!"
                fi
            fi
        fi
        
        # Recent git activity
        if command -v git >/dev/null 2>&1 && [ -d ".git" ]; then
            log "🔄 Recent Activity:"
            git log --oneline -3 | sed 's/^/  /'
            
            # Check for uncommitted changes
            UNCOMMITTED=$(git status --porcelain | wc -l)
            if [ $UNCOMMITTED -gt 0 ]; then
                log "📝 $UNCOMMITTED uncommitted changes"
            fi
        fi
        
        # Environment status
        log "🔧 Environment Status:"
        
        # Check if services are running
        if curl -s http://localhost:8000/api/v1/health >/dev/null 2>&1; then
            log "  ✅ API Server: Running"
        else
            log "  ❌ API Server: Not running (Start with: ai-backend)"
        fi
        
        if curl -s http://localhost:3000 >/dev/null 2>&1; then
            log "  ✅ Frontend: Running"
        else
            log "  ❌ Frontend: Not running (Start with: ai-frontend)"
        fi
        
        # Redis status
        if command -v redis-cli >/dev/null 2>&1 && redis-cli ping >/dev/null 2>&1; then
            log "  ✅ Redis Cache: Active"
        else
            log "  ⚠️  Redis Cache: Inactive"
        fi
        
        # Quick wins suggestions
        if [ -f "$CACHE_DIR/pending-suggestions.md" ]; then
            SUGGESTION_COUNT=$(wc -l < "$CACHE_DIR/pending-suggestions.md")
            if [ $SUGGESTION_COUNT -gt 0 ]; then
                log "💡 $SUGGESTION_COUNT pending suggestions available"
            fi
        fi
        
        log "🎉 Session ready! Type 'ai-help' for available commands"
        ;;
        
    "session_end")
        log "👋 Claude Code session ending"
        
        # Calculate session duration
        if [ -f "$SESSION_DIR/start-time" ]; then
            START_TIME=$(cat "$SESSION_DIR/start-time")
            END_TIME=$(date +%s)
            DURATION=$((END_TIME - START_TIME))
            HOURS=$((DURATION / 3600))
            MINUTES=$(((DURATION % 3600) / 60))
            
            log "⏱️  Session duration: ${HOURS}h ${MINUTES}m"
        fi
        
        # Session summary
        if [ -f "$SESSION_DIR/tool-usage.log" ]; then
            TOOLS_USED=$(wc -l < "$SESSION_DIR/tool-usage.log")
            log "🛠️  Tools used: $TOOLS_USED"
            
            # Most used tools
            MOST_USED=$(cut -d'|' -f1 "$SESSION_DIR/tool-usage.log" | sort | uniq -c | sort -nr | head -3)
            log "📊 Most used tools:"
            echo "$MOST_USED" | while read -r count tool; do
                log "  • $tool: $count times"
            done
        fi
        
        # Files modified
        if [ -f "$SESSION_DIR/successful-operations.log" ]; then
            MODIFICATIONS=$(grep -c "Edit\|Write\|MultiEdit" "$SESSION_DIR/successful-operations.log" 2>/dev/null || echo 0)
            log "📝 Files modified: $MODIFICATIONS"
        fi
        
        # Generate session summary
        python ".claude/hooks/integration/generate-session-summary.py" 2>/dev/null || log "📄 Session summary generation skipped"
        
        log "✅ Session completed successfully"
        echo "session-ended|$(date +%s)" >> "$SESSION_DIR/activity.log"
        ;;
        
    "prompt_submit")
        log "💬 Processing prompt submission"
        
        # Auto-inject project context
        if [ -f "CLAUDE.md" ]; then
            log "📋 Auto-injecting project context"
            
            # Show recent project context
            echo "📁 Project Context:"
            head -20 CLAUDE.md | grep -E "^#|^-|Tech Stack|Recently Implemented" | head -10
            
            # Show recent changes
            if command -v git >/dev/null 2>&1; then
                echo ""
                echo "🔄 Recent Changes:"
                git log --oneline -5
            fi
            
            # Show current focus
            if [ -f "docs/TODO-MVP/README.md" ]; then
                CURRENT_TASK=$(grep "Working on:" "docs/TODO-MVP/README.md" | sed 's/Working on: //')
                if [ "$CURRENT_TASK" != "None" ] && [ ! -z "$CURRENT_TASK" ]; then
                    echo ""
                    echo "🎯 Current Focus: $CURRENT_TASK"
                fi
            fi
        fi
        
        # Validate prompt if available
        if [ -f ".claude/hooks/integration/validate-prompt.py" ]; then
            python ".claude/hooks/integration/validate-prompt.py" "$CONTEXT_DATA" 2>/dev/null || true
        fi
        ;;
        
    "tool_use")
        TOOL_NAME="$CONTEXT_DATA"
        log "🔧 Tool use detected: $TOOL_NAME"
        
        # Record tool usage
        echo "$TOOL_NAME|$(date +%s)" >> "$SESSION_DIR/tool-usage.log"
        
        # Auto-format and test for code changes
        if [[ "$TOOL_NAME" == "Edit" ]] || [[ "$TOOL_NAME" == "Write" ]] || [[ "$TOOL_NAME" == "MultiEdit" ]]; then
            log "📝 Code modification detected - triggering quality checks"
            
            # Schedule linting (non-blocking)
            {
                if [ -d "apps/web" ]; then
                    cd apps/web && npm run lint --silent 2>/dev/null || true
                fi
                
                if [ -d "apps/api" ]; then
                    cd apps/api && ruff check . --quiet 2>/dev/null || true
                fi
            } &
        fi
        
        # Auto-cleanup completed todos
        if [[ "$TOOL_NAME" == "TodoWrite" ]]; then
            log "📋 TODO modification detected"
            
            # Schedule todo cleanup
            if [ -f ".claude/hooks/integration/cleanup-todos.py" ]; then
                python ".claude/hooks/integration/cleanup-todos.py" &
            fi
            
            # Update progress documentation
            if [ -f ".claude/hooks/integration/update-progress-docs.py" ]; then
                python ".claude/hooks/integration/update-progress-docs.py" "docs/TODO-MVP/README.md" &
            fi
        fi
        
        # Pre-commit checks for git operations
        if [[ "$TOOL_NAME" == "Bash" ]] && [[ "$CONTEXT_DATA" == *"git commit"* ]]; then
            log "📦 Git commit detected - running pre-commit checks"
            
            # Run type checking
            if [ -d "apps/web" ]; then
                log "🔍 Running TypeScript check..."
                if ! (cd apps/web && npx tsc --noEmit); then
                    log "❌ TypeScript errors found - commit may fail"
                fi
            fi
            
            # Run critical tests
            if [ -d "apps/api" ] && [ -f "apps/api/tests/test_calculations.py" ]; then
                log "🧪 Running critical tests..."
                if ! (cd apps/api && python -m pytest tests/test_calculations.py -x); then
                    log "❌ Critical tests failed - commit may fail"
                fi
            fi
        fi
        ;;
        
    *)
        log "❓ Unknown hook type: $HOOK_TYPE"
        ;;
esac

# Log execution stats
echo "$(date +%s)|$HOOK_TYPE|$CONTEXT_DATA" >> "$SESSION_DIR/hook-executions.log"

exit 0