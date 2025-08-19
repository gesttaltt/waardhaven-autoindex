#!/bin/bash
# Post-tool execution hook for cleanup and learning
# Runs after tool execution to clean up and track patterns

TOOL_NAME="$1"
TOOL_ARGS="$2"
TOOL_EXIT_CODE="$3"
TOOL_OUTPUT="$4"
CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID:-$(date +%s)}"
LOG_FILE=".claude/logs/post-tool-$(date +%Y%m%d).log"

# Create necessary directories
mkdir -p ".claude/logs" ".claude/cache" ".claude/session"

# Logging function
log() {
    echo "$(date '+%H:%M:%S') [POST-TOOL] $1" | tee -a "$LOG_FILE"
}

log "🏁 Post-tool cleanup for: $TOOL_NAME (exit: $TOOL_EXIT_CODE)"

# Track successful operations for learning
if [ "$TOOL_EXIT_CODE" = "0" ]; then
    echo "$TOOL_NAME|success|$(date +%s)" >> ".claude/session/successful-operations.log"
    
    # Specific success handling
    case "$TOOL_NAME" in
        "Edit"|"Write"|"MultiEdit")
            if [[ "$TOOL_ARGS" == *".py"* ]]; then
                log "🐍 Python file modified - suggesting type check"
                echo "python-file-modified|$(date +%s)" >> ".claude/cache/pending-checks"
            elif [[ "$TOOL_ARGS" == *".ts"* ]] || [[ "$TOOL_ARGS" == *".tsx"* ]]; then
                log "📘 TypeScript file modified - suggesting compilation check"
                echo "typescript-file-modified|$(date +%s)" >> ".claude/cache/pending-checks"
            elif [[ "$TOOL_ARGS" == *".md"* ]]; then
                log "📝 Documentation modified - running link validation"
                # Schedule link validation
                echo "$TOOL_ARGS" >> ".claude/cache/docs-to-validate"
            fi
            ;;
        "Bash")
            if [[ "$TOOL_ARGS" == *"git commit"* ]]; then
                log "📦 Git commit executed - updating project state"
                git rev-parse HEAD > ".claude/cache/last-commit"
                echo "$(date +%s)" > ".claude/cache/last-deploy-check-needed"
            elif [[ "$TOOL_ARGS" == *"npm install"* ]] || [[ "$TOOL_ARGS" == *"pip install"* ]]; then
                log "📦 Dependencies installed - caching package info"
                if [[ "$TOOL_ARGS" == *"npm"* ]]; then
                    npm list --depth=0 > ".claude/cache/npm-packages.txt" 2>/dev/null
                elif [[ "$TOOL_ARGS" == *"pip"* ]]; then
                    pip list > ".claude/cache/pip-packages.txt" 2>/dev/null
                fi
            elif [[ "$TOOL_ARGS" == *"pytest"* ]] || [[ "$TOOL_ARGS" == *"npm test"* ]]; then
                log "🧪 Tests executed - caching results"
                echo "tests-passed|$(date +%s)" >> ".claude/cache/test-history"
            fi
            ;;
    esac
else
    # Handle failures
    echo "$TOOL_NAME|failed|$TOOL_EXIT_CODE|$(date +%s)" >> ".claude/session/failed-operations.log"
    log "❌ Tool failed with exit code: $TOOL_EXIT_CODE"
    
    # Pattern-based failure handling
    if [[ "$TOOL_OUTPUT" == *"permission denied"* ]]; then
        log "🔒 Permission issue detected - may need chmod or different approach"
    elif [[ "$TOOL_OUTPUT" == *"not found"* ]]; then
        log "🔍 Command/file not found - may need installation or path correction"
    elif [[ "$TOOL_OUTPUT" == *"ENOENT"* ]]; then
        log "📁 File/directory not found - may need creation or path check"
    fi
fi

# Environment-specific cleanup
case "$TOOL_NAME" in
    "Read")
        # Track frequently read files for caching suggestions
        echo "$TOOL_ARGS|$(date +%s)" >> ".claude/cache/file-access-log"
        
        # Clean up access log (keep last 1000 entries)
        tail -1000 ".claude/cache/file-access-log" > ".claude/cache/file-access-log.tmp" 2>/dev/null
        mv ".claude/cache/file-access-log.tmp" ".claude/cache/file-access-log" 2>/dev/null
        ;;
        
    "Bash")
        # Clean up temporary files created by bash commands
        if [[ "$TOOL_ARGS" == *"temp"* ]] || [[ "$TOOL_ARGS" == *"/tmp/"* ]]; then
            log "🧹 Cleaning up temporary files from bash command"
        fi
        
        # Check for long-running processes that might need monitoring
        if [[ "$TOOL_ARGS" == *"uvicorn"* ]] || [[ "$TOOL_ARGS" == *"npm run dev"* ]]; then
            log "🚀 Development server started - monitoring for health"
            echo "dev-server|$(date +%s)" >> ".claude/cache/active-services"
        fi
        ;;
        
    "WebFetch")
        # Cache successful web requests to avoid repeated calls
        if [ "$TOOL_EXIT_CODE" = "0" ]; then
            URL_HASH=$(echo "$TOOL_ARGS" | sha256sum | cut -d' ' -f1)
            echo "$(date +%s)|$TOOL_ARGS" > ".claude/cache/web-cache-$URL_HASH"
        fi
        ;;
esac

# AI Investment project specific cleanup
if [ -f "CLAUDE.md" ]; then
    # Check if TODO status needs updating
    if [[ "$TOOL_NAME" == "Edit" ]] && [[ "$TOOL_ARGS" == *"TODO-MVP"* ]]; then
        log "📋 TODO files modified - triggering status update"
        echo "todo-update-needed|$(date +%s)" >> ".claude/cache/pending-updates"
    fi
    
    # Check if API changes need documentation update
    if [[ "$TOOL_ARGS" == *"apps/api"* ]] && [[ "$TOOL_ARGS" == *".py"* ]]; then
        if [[ "$TOOL_OUTPUT" == *"endpoint"* ]] || [[ "$TOOL_OUTPUT" == *"route"* ]]; then
            log "🔄 API endpoint changes detected - consider updating documentation"
            echo "api-docs-update|$(date +%s)" >> ".claude/cache/pending-updates"
        fi
    fi
    
    # Monitor critical file changes
    CRITICAL_FILES=(
        "CLAUDE.md"
        ".env"
        "docker-compose.yml"
        "package.json"
        "requirements.txt"
        "pyproject.toml"
    )
    
    for file in "${CRITICAL_FILES[@]}"; do
        if [[ "$TOOL_ARGS" == *"$file"* ]] && [ "$TOOL_NAME" != "Read" ]; then
            log "⚠️  Critical file modified: $file"
            echo "$file|$(date +%s)" >> ".claude/cache/critical-changes"
        fi
    done
fi

# Session statistics update
STATS_FILE=".claude/session/stats-$(date +%Y%m%d).json"
if [ -f "$STATS_FILE" ]; then
    # Update existing stats (simplified - in real implementation would use jq)
    TOOL_COUNT=$(grep -c "\"$TOOL_NAME\"" "$STATS_FILE" 2>/dev/null || echo 0)
    TOOL_COUNT=$((TOOL_COUNT + 1))
else
    # Create new stats file
    cat > "$STATS_FILE" << EOF
{
  "date": "$(date +%Y-%m-%d)",
  "session_id": "$CLAUDE_SESSION_ID",
  "tools_used": {
    "$TOOL_NAME": 1
  },
  "start_time": "$(date -Iseconds)"
}
EOF
fi

# Cleanup old logs and cache files (keep last 7 days)
find ".claude/logs" -name "*.log" -mtime +7 -delete 2>/dev/null
find ".claude/cache" -name "*" -mtime +7 -delete 2>/dev/null
find ".claude/session" -name "*" -mtime +7 -delete 2>/dev/null

# Smart suggestions based on patterns
SUGGESTION_FILE=".claude/cache/suggestions-$(date +%Y%m%d).txt"
touch "$SUGGESTION_FILE"

# Suggest running tests if many files changed
FILES_CHANGED_TODAY=$(grep "$(date +%Y-%m-%d)" ".claude/session/successful-operations.log" 2>/dev/null | grep -c "Edit\|Write" || echo 0)
if [ $FILES_CHANGED_TODAY -gt 5 ] && ! grep -q "test-suggestion-shown" "$SUGGESTION_FILE"; then
    log "💡 Suggestion: Consider running tests after multiple file changes"
    echo "test-suggestion-shown" >> "$SUGGESTION_FILE"
fi

# Suggest backup if database operations detected
if [[ "$TOOL_ARGS" == *"database"* ]] && ! grep -q "backup-suggestion-shown" "$SUGGESTION_FILE"; then
    if [ ! -d "backups/database" ] || [ -z "$(find backups/database -name "*.sql*" -mtime -1 2>/dev/null)" ]; then
        log "💡 Suggestion: Consider creating database backup before DB operations"
        echo "backup-suggestion-shown" >> "$SUGGESTION_FILE"
    fi
fi

log "✅ Post-tool cleanup complete"

exit 0