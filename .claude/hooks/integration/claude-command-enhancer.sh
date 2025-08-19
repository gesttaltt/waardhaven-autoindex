#!/bin/bash
# Claude Command Enhancer - Advanced shell integration with intelligent command suggestions
# Provides context-aware command completion and workflow automation

COMMAND_TYPE="$1"    # suggest, execute, learn, analyze
CONTEXT="$2"         # current context or command
USER_INPUT="$3"      # user's input or intent

LOG_FILE=".claude/logs/command-enhancer-$(date +%Y%m%d).log"
CACHE_DIR=".claude/cache"
SESSION_DIR=".claude/session"

# Create necessary directories
mkdir -p ".claude/logs" "$CACHE_DIR" "$SESSION_DIR"

# Logging function
log() {
    echo "$(date '+%H:%M:%S') [CMD-ENHANCER] $1" | tee -a "$LOG_FILE"
}

# Command database for AI Investment project
declare -A COMMAND_DATABASE
COMMAND_DATABASE=(
    # Development commands
    ["start-backend"]="cd apps/api && uvicorn app.main:app --reload"
    ["start-frontend"]="cd apps/web && npm run dev"
    ["test-backend"]="cd apps/api && python -m pytest"
    ["test-frontend"]="cd apps/web && npm test"
    ["lint-python"]="cd apps/api && ruff check ."
    ["lint-typescript"]="cd apps/web && npm run lint"
    ["type-check"]="cd apps/web && npx tsc --noEmit"
    
    # Database commands
    ["backup-db"]="./hooks/database/backup-before-migration.sh"
    ["check-db"]="./hooks/monitoring/slow-query-detector.sh"
    ["migrate-db"]="cd apps/api && alembic upgrade head"
    
    # Monitoring commands
    ["check-api"]="./hooks/api/monitor-endpoints.sh"
    ["check-rates"]="./hooks/api/check-rate-limits.sh"
    ["monitor-perf"]="./hooks/monitoring/performance-monitor.sh"
    ["quality-check"]="./hooks/quality/code-quality-monitor.sh daily"
    
    # TODO management
    ["show-todos"]="./hooks/task-management/show-priorities.sh"
    ["start-task"]="./hooks/task-management/task-start.sh"
    ["complete-task"]="./hooks/task-management/task-complete.sh"
    
    # Deployment
    ["pre-deploy"]="./hooks/deployment/pre-deploy-checks.sh"
    ["deploy-staging"]="./hooks/deployment/claude-aware-deploy.sh staging"
    ["deploy-prod"]="./hooks/deployment/claude-aware-deploy.sh production"
    
    # Documentation
    ["gen-docs"]="python .claude/hooks/documentation/auto-doc-generator.py all"
    ["update-docs"]="python .claude/hooks/integration/update-progress-docs.py"
    
    # AI Investment specific
    ["analyze-portfolio"]="cd apps/api && python -c \"from app.services.calculation_service import *; print('Portfolio analysis ready')\""
    ["test-calculations"]="cd apps/api && python -m pytest tests/test_calculations.py -v"
    ["check-external-apis"]="curl -s https://api.twelvedata.com/api_usage?apikey=\$TWELVE_DATA_API_KEY"
)

# Context patterns for intelligent suggestions
declare -A CONTEXT_PATTERNS
CONTEXT_PATTERNS=(
    ["error"]="test|debug|check|fix"
    ["slow"]="monitor|optimize|profile|cache"
    ["deploy"]="test|check|backup|deploy"
    ["api"]="test|monitor|docs|check"
    ["database"]="backup|migrate|check|optimize"
    ["frontend"]="build|test|lint|serve"
    ["backend"]="test|lint|run|debug"
    ["todo"]="show|start|complete|status"
    ["quality"]="lint|test|check|fix"
    ["docs"]="generate|update|validate|sync"
)

case "$COMMAND_TYPE" in
    "suggest")
        log "🧠 Generating command suggestions for context: $CONTEXT"
        
        suggestions=()
        confidence_scores=()
        
        # Analyze current context
        if [[ "$CONTEXT" == *"error"* ]] || [[ "$CONTEXT" == *"fail"* ]]; then
            suggestions+=("test-backend" "test-frontend" "check-api" "monitor-perf")
            confidence_scores+=(90 85 80 75)
            log "💡 Error context detected - suggesting diagnostic commands"
            
        elif [[ "$CONTEXT" == *"slow"* ]] || [[ "$CONTEXT" == *"performance"* ]]; then
            suggestions+=("monitor-perf" "check-db" "check-rates" "quality-check")
            confidence_scores+=(95 90 85 80)
            log "💡 Performance context detected - suggesting monitoring commands"
            
        elif [[ "$CONTEXT" == *"deploy"* ]] || [[ "$CONTEXT" == *"release"* ]]; then
            suggestions+=("pre-deploy" "test-backend" "test-frontend" "backup-db")
            confidence_scores+=(95 90 90 85)
            log "💡 Deployment context detected - suggesting safety commands"
            
        elif [[ "$CONTEXT" == *"api"* ]] || [[ "$CONTEXT" == *"endpoint"* ]]; then
            suggestions+=("check-api" "test-backend" "gen-docs" "check-rates")
            confidence_scores+=(90 85 80 75)
            log "💡 API context detected - suggesting API-related commands"
            
        elif [[ "$CONTEXT" == *"database"* ]] || [[ "$CONTEXT" == *"model"* ]]; then
            suggestions+=("backup-db" "check-db" "migrate-db" "test-backend")
            confidence_scores+=(90 85 80 75)
            log "💡 Database context detected - suggesting DB commands"
            
        elif [[ "$CONTEXT" == *"todo"* ]] || [[ "$CONTEXT" == *"task"* ]]; then
            suggestions+=("show-todos" "start-task" "complete-task" "update-docs")
            confidence_scores+=(95 85 85 75)
            log "💡 Task management context detected"
            
        elif [[ "$CONTEXT" == *"test"* ]] || [[ "$CONTEXT" == *"quality"* ]]; then
            suggestions+=("test-backend" "test-frontend" "quality-check" "lint-python")
            confidence_scores+=(95 90 85 80)
            log "💡 Testing context detected"
            
        else
            # General suggestions based on project state
            log "💡 Analyzing project state for general suggestions"
            
            # Check if services are running
            if ! curl -s http://localhost:8000/api/v1/health >/dev/null 2>&1; then
                suggestions+=("start-backend")
                confidence_scores+=(85)
            fi
            
            if ! curl -s http://localhost:3000 >/dev/null 2>&1; then
                suggestions+=("start-frontend")
                confidence_scores+=(85)
            fi
            
            # Check for pending TODOs
            if [ -d "docs/TODO-MVP/BACKLOG/P0-CRITICAL" ]; then
                P0_COUNT=$(find "docs/TODO-MVP/BACKLOG/P0-CRITICAL" -name "*.md" 2>/dev/null | wc -l)
                if [ $P0_COUNT -gt 0 ]; then
                    suggestions+=("show-todos")
                    confidence_scores+=(80)
                fi
            fi
            
            # Default development suggestions
            suggestions+=("test-backend" "quality-check" "show-todos")
            confidence_scores+=(70 65 60)
        fi
        
        # Output suggestions
        echo "🎯 Command Suggestions:"
        for i in "${!suggestions[@]}"; do
            cmd_key="${suggestions[$i]}"
            confidence="${confidence_scores[$i]}"
            cmd_value="${COMMAND_DATABASE[$cmd_key]}"
            
            echo "  $((i+1)). $cmd_key (${confidence}% confidence)"
            echo "     Command: $cmd_value"
            echo ""
        done
        
        # Save suggestions to cache for learning
        {
            echo "Context: $CONTEXT"
            echo "Timestamp: $(date)"
            echo "Suggestions:"
            for i in "${!suggestions[@]}"; do
                echo "  ${suggestions[$i]}:${confidence_scores[$i]}"
            done
            echo ""
        } >> "$CACHE_DIR/command-suggestions.log"
        ;;
        
    "execute")
        COMMAND_KEY="$CONTEXT"
        log "⚡ Executing command: $COMMAND_KEY"
        
        if [[ -n "${COMMAND_DATABASE[$COMMAND_KEY]}" ]]; then
            COMMAND="${COMMAND_DATABASE[$COMMAND_KEY]}"
            log "🔧 Running: $COMMAND"
            
            # Record command execution
            echo "$(date +%s)|$COMMAND_KEY|$COMMAND" >> "$SESSION_DIR/command-executions.log"
            
            # Execute with proper error handling
            echo "Executing: $COMMAND"
            if eval "$COMMAND"; then
                log "✅ Command executed successfully"
                echo "success|$(date +%s)" >> "$CACHE_DIR/command-success.log"
            else
                log "❌ Command execution failed"
                echo "failure|$COMMAND_KEY|$(date +%s)" >> "$CACHE_DIR/command-failures.log"
            fi
        else
            log "❌ Unknown command key: $COMMAND_KEY"
            echo "Unknown command: $COMMAND_KEY"
            echo "Available commands:"
            for key in "${!COMMAND_DATABASE[@]}"; do
                echo "  - $key"
            done
        fi
        ;;
        
    "learn")
        log "📚 Learning from user command pattern: $CONTEXT"
        
        # Extract command intent from user input
        intent=$(echo "$CONTEXT" | tr '[:upper:]' '[:lower:]')
        
        # Update command usage patterns
        echo "$(date +%s)|$intent|$USER_INPUT" >> "$CACHE_DIR/command-learning.log"
        
        # Analyze patterns for future improvements
        if [[ "$intent" == *"start"* ]] && [[ "$intent" == *"server"* ]]; then
            echo "Learned: User wants to start servers - suggest start-backend/start-frontend"
        elif [[ "$intent" == *"test"* ]]; then
            echo "Learned: User wants to run tests - suggest test commands"
        elif [[ "$intent" == *"check"* ]] || [[ "$intent" == *"status"* ]]; then
            echo "Learned: User wants status check - suggest monitoring commands"
        fi
        ;;
        
    "analyze")
        log "📊 Analyzing command usage patterns"
        
        echo "📈 Command Usage Analysis:"
        
        # Analyze most used commands
        if [ -f "$SESSION_DIR/command-executions.log" ]; then
            echo ""
            echo "Most Used Commands (This Session):"
            cut -d'|' -f2 "$SESSION_DIR/command-executions.log" | sort | uniq -c | sort -nr | head -5 | while read count cmd; do
                echo "  $count× $cmd"
            done
        fi
        
        # Analyze success rate
        if [ -f "$CACHE_DIR/command-success.log" ] && [ -f "$CACHE_DIR/command-failures.log" ]; then
            successes=$(wc -l < "$CACHE_DIR/command-success.log" 2>/dev/null || echo 0)
            failures=$(wc -l < "$CACHE_DIR/command-failures.log" 2>/dev/null || echo 0)
            total=$((successes + failures))
            
            if [ $total -gt 0 ]; then
                success_rate=$((successes * 100 / total))
                echo ""
                echo "Command Success Rate: $success_rate% ($successes/$total)"
            fi
        fi
        
        # Show context patterns
        if [ -f "$CACHE_DIR/command-suggestions.log" ]; then
            echo ""
            echo "Recent Context Patterns:"
            grep "Context:" "$CACHE_DIR/command-suggestions.log" | tail -5 | sed 's/Context: /  /'
        fi
        
        # AI Investment specific analysis
        if [ -f "CLAUDE.md" ]; then
            echo ""
            echo "AI Investment Project Analysis:"
            
            # Check service status
            if curl -s http://localhost:8000/api/v1/health >/dev/null 2>&1; then
                echo "  ✅ API Server: Running"
            else
                echo "  ❌ API Server: Stopped"
                echo "     Suggest: start-backend"
            fi
            
            if curl -s http://localhost:3000 >/dev/null 2>&1; then
                echo "  ✅ Frontend: Running"
            else
                echo "  ❌ Frontend: Stopped"
                echo "     Suggest: start-frontend"
            fi
            
            # Check recent activity
            if [ -f "$CACHE_DIR/file-change-history" ]; then
                recent_changes=$(tail -10 "$CACHE_DIR/file-change-history" | wc -l)
                echo "  📝 Recent Changes: $recent_changes files"
                
                if [ $recent_changes -gt 5 ]; then
                    echo "     Suggest: test-backend, quality-check"
                fi
            fi
        fi
        ;;
        
    *)
        log "❓ Unknown command type: $COMMAND_TYPE"
        echo "Usage: claude-command-enhancer.sh <suggest|execute|learn|analyze> [context] [input]"
        echo ""
        echo "Examples:"
        echo "  $0 suggest \"api error\" - Get command suggestions for API errors"
        echo "  $0 execute \"test-backend\" - Execute backend tests"
        echo "  $0 learn \"start server\" \"npm run dev\" - Learn from user command"
        echo "  $0 analyze - Analyze command usage patterns"
        ;;
esac

# Update command enhancer stats
echo "$(date +%s)|$COMMAND_TYPE|$CONTEXT" >> "$SESSION_DIR/enhancer-usage.log"

log "✅ Command enhancer operation complete"

exit 0