#!/bin/bash
# File change detector hook - monitors file modifications and suggests related actions
# Triggered when files are modified to suggest tests, documentation updates, etc.

FILE_PATH="$1"
CHANGE_TYPE="$2"  # created, modified, deleted
CONTENT_PREVIEW="$3"
LOG_FILE=".claude/logs/file-changes-$(date +%Y%m%d).log"

# Create necessary directories
mkdir -p ".claude/logs" ".claude/cache"

# Logging function
log() {
    echo "$(date '+%H:%M:%S') [FILE-CHANGE] $1" | tee -a "$LOG_FILE"
}

log "📝 File change detected: $FILE_PATH ($CHANGE_TYPE)"

# Initialize suggestions array
SUGGESTIONS=()

# Analyze file type and suggest related actions
FILE_EXT="${FILE_PATH##*.}"
FILE_DIR=$(dirname "$FILE_PATH")
FILE_NAME=$(basename "$FILE_PATH")

case "$FILE_EXT" in
    "py")
        log "🐍 Python file changed"
        
        # Check if it's a model file
        if [[ "$FILE_PATH" == *"models"* ]]; then
            SUGGESTIONS+=("Consider running database migrations if model schema changed")
            SUGGESTIONS+=("Update API documentation if new fields added")
            if [[ "$CONTENT_PREVIEW" == *"class"* ]] && [[ "$CONTENT_PREVIEW" == *"Base"* ]]; then
                SUGGESTIONS+=("New model detected - consider adding to __init__.py")
                SUGGESTIONS+=("Create corresponding test file: tests/test_$(basename "$FILE_PATH")")
            fi
        fi
        
        # Check if it's an API endpoint
        if [[ "$FILE_PATH" == *"routers"* ]] || [[ "$CONTENT_PREVIEW" == *"@router"* ]] || [[ "$CONTENT_PREVIEW" == *"@app"* ]]; then
            SUGGESTIONS+=("API endpoint changed - run OpenAPI documentation update")
            SUGGESTIONS+=("Test the endpoint: curl http://localhost:8000/api/v1/...")
            SUGGESTIONS+=("Update frontend if new endpoints added")
        fi
        
        # Check if it's a service file
        if [[ "$FILE_PATH" == *"services"* ]]; then
            SUGGESTIONS+=("Service logic changed - run related unit tests")
            SUGGESTIONS+=("Check if integration tests need updates")
        fi
        
        # General Python suggestions
        SUGGESTIONS+=("Run type checking: cd apps/api && mypy app")
        SUGGESTIONS+=("Run linting: cd apps/api && ruff check .")
        
        # Check for dangerous patterns
        if [[ "$CONTENT_PREVIEW" == *"DELETE FROM"* ]] || [[ "$CONTENT_PREVIEW" == *".delete("* ]]; then
            SUGGESTIONS+=("⚠️  DELETE operation detected - ensure proper safeguards")
            SUGGESTIONS+=("Consider using soft delete instead")
        fi
        
        if [[ "$CONTENT_PREVIEW" == *"SECRET"* ]] || [[ "$CONTENT_PREVIEW" == *"PASSWORD"* ]]; then
            SUGGESTIONS+=("🚨 Potential secret detected - use environment variables")
        fi
        ;;
        
    "ts"|"tsx")
        log "📘 TypeScript/React file changed"
        
        # Check if it's a component
        if [[ "$CONTENT_PREVIEW" == *"export"* ]] && [[ "$CONTENT_PREVIEW" == *"function"* ]]; then
            SUGGESTIONS+=("New React component - consider adding to component index")
            SUGGESTIONS+=("Create corresponding test file: __tests__/$(basename "$FILE_PATH" .tsx).test.tsx")
        fi
        
        # Check if it's a page
        if [[ "$FILE_PATH" == *"app/"* ]] && [[ "$FILE_PATH" == *"page.tsx"* ]]; then
            SUGGESTIONS+=("Page component changed - test routing")
            SUGGESTIONS+=("Update sitemap if new page added")
        fi
        
        # Check if it's an API integration
        if [[ "$CONTENT_PREVIEW" == *"fetch"* ]] || [[ "$CONTENT_PREVIEW" == *"axios"* ]]; then
            SUGGESTIONS+=("API call detected - ensure error handling")
            SUGGESTIONS+=("Check if backend endpoint exists")
        fi
        
        SUGGESTIONS+=("Run TypeScript compilation: cd apps/web && npx tsc --noEmit")
        SUGGESTIONS+=("Run linting: cd apps/web && npm run lint")
        ;;
        
    "md")
        log "📖 Markdown documentation changed"
        
        # Check for broken links
        if [[ "$CONTENT_PREVIEW" == *"[]*("* ]] || [[ "$CONTENT_PREVIEW" == *"]()"* ]]; then
            SUGGESTIONS+=("⚠️  Empty markdown links detected")
        fi
        
        # Check for TODO items
        if [[ "$CONTENT_PREVIEW" == *"TODO"* ]]; then
            SUGGESTIONS+=("TODO items found - consider adding to task management")
        fi
        
        # Check if it's API documentation
        if [[ "$FILE_PATH" == *"api"* ]] || [[ "$CONTENT_PREVIEW" == *"endpoint"* ]]; then
            SUGGESTIONS+=("API documentation changed - verify with actual endpoints")
            SUGGESTIONS+=("Run API health check: ai-api")
        fi
        
        SUGGESTIONS+=("Validate documentation links")
        SUGGESTIONS+=("Update table of contents if structure changed")
        ;;
        
    "json")
        log "📄 JSON configuration changed"
        
        if [[ "$FILE_NAME" == "package.json" ]]; then
            SUGGESTIONS+=("package.json changed - run npm install")
            SUGGESTIONS+=("Check for security vulnerabilities: npm audit")
        elif [[ "$FILE_NAME" == "tsconfig.json" ]]; then
            SUGGESTIONS+=("TypeScript config changed - rebuild project")
        elif [[ "$FILE_PATH" == *".claude"* ]]; then
            SUGGESTIONS+=("Claude configuration changed - restart Claude session")
        fi
        
        # Validate JSON syntax
        if command -v jq >/dev/null 2>&1; then
            if ! jq empty "$FILE_PATH" 2>/dev/null; then
                SUGGESTIONS+=("🚨 Invalid JSON syntax detected")
            fi
        fi
        ;;
        
    "env")
        log "🔧 Environment file changed"
        SUGGESTIONS+=("🚨 Environment variables changed - restart services")
        SUGGESTIONS+=("Verify all required variables are set")
        SUGGESTIONS+=("Check if .env.example needs updating")
        
        # Security check
        if [[ "$CONTENT_PREVIEW" == *"SECRET"* ]] && [[ "$CONTENT_PREVIEW" != *"your_"* ]]; then
            SUGGESTIONS+=("⚠️  Ensure secrets are not committed to git")
        fi
        ;;
        
    "sql")
        log "🗄️ SQL file changed"
        SUGGESTIONS+=("SQL script changed - test on development database first")
        SUGGESTIONS+=("Create database backup before running: ai-backup")
        SUGGESTIONS+=("Check for data loss operations (DELETE, DROP, TRUNCATE)")
        ;;
        
    "yml"|"yaml")
        log "⚙️ YAML configuration changed"
        
        if [[ "$FILE_NAME" == "docker-compose.yml" ]]; then
            SUGGESTIONS+=("Docker Compose changed - restart containers")
        elif [[ "$FILE_NAME" == ".github"* ]]; then
            SUGGESTIONS+=("GitHub Actions changed - test workflow locally")
        elif [[ "$FILE_NAME" == "render.yaml" ]]; then
            SUGGESTIONS+=("Render config changed - review deployment settings")
        fi
        ;;
esac

# Project-specific suggestions based on file location
if [[ "$FILE_PATH" == *"apps/api"* ]]; then
    SUGGESTIONS+=("Backend change - consider running backend tests")
    SUGGESTIONS+=("Check if frontend needs corresponding updates")
elif [[ "$FILE_PATH" == *"apps/web"* ]]; then
    SUGGESTIONS+=("Frontend change - test in browser")
    SUGGESTIONS+=("Check if API calls match backend endpoints")
elif [[ "$FILE_PATH" == *"docs"* ]]; then
    SUGGESTIONS+=("Documentation change - run link validation")
    SUGGESTIONS+=("Consider updating related documentation files")
elif [[ "$FILE_PATH" == *"hooks"* ]]; then
    SUGGESTIONS+=("Hook script changed - test hook functionality")
    SUGGESTIONS+=("Make sure script is executable: chmod +x")
fi

# AI Investment specific suggestions
if [ -f "CLAUDE.md" ]; then
    # Check for financial calculation changes
    if [[ "$CONTENT_PREVIEW" == *"calculate"* ]] || [[ "$CONTENT_PREVIEW" == *"portfolio"* ]] || [[ "$CONTENT_PREVIEW" == *"index"* ]]; then
        SUGGESTIONS+=("Financial calculation logic changed - run calculation tests")
        SUGGESTIONS+=("Verify with sample data")
    fi
    
    # Check for API integration changes
    if [[ "$CONTENT_PREVIEW" == *"twelvedata"* ]] || [[ "$CONTENT_PREVIEW" == *"marketaux"* ]]; then
        SUGGESTIONS+=("External API integration changed - check rate limits")
        SUGGESTIONS+=("Test with actual API calls")
    fi
fi

# Frequency-based suggestions
CHANGE_COUNT_TODAY=$(grep "$(date +%Y-%m-%d)" "$LOG_FILE" 2>/dev/null | grep -c "$FILE_PATH" || echo 0)
if [ $CHANGE_COUNT_TODAY -gt 3 ]; then
    SUGGESTIONS+=("💡 File changed $CHANGE_COUNT_TODAY times today - consider running comprehensive tests")
fi

# Related file suggestions
case "$FILE_PATH" in
    *"models"*)
        if [ -f "${FILE_PATH/models/tests/test_}" ]; then
            SUGGESTIONS+=("Related test file exists: ${FILE_PATH/models/tests/test_}")
        fi
        ;;
    *"routers"*)
        if [ -f "${FILE_PATH/routers/tests/test_}" ]; then
            SUGGESTIONS+=("Related test file exists: ${FILE_PATH/routers/tests/test_}")
        fi
        ;;
esac

# Save change to history for pattern analysis
echo "$(date +%s)|$FILE_PATH|$CHANGE_TYPE|$FILE_EXT" >> ".claude/cache/file-change-history"

# Output suggestions
if [ ${#SUGGESTIONS[@]} -gt 0 ]; then
    log "💡 Suggestions for $FILE_PATH:"
    for suggestion in "${SUGGESTIONS[@]}"; do
        log "  • $suggestion"
    done
    
    # Save suggestions to cache for later reference
    {
        echo "# Suggestions for $FILE_PATH ($(date))"
        printf '%s\n' "${SUGGESTIONS[@]}"
        echo ""
    } >> ".claude/cache/pending-suggestions.md"
else
    log "✅ No specific suggestions for this file type"
fi

# Trigger related hooks based on file type
if [[ "$FILE_EXT" == "py" ]] && [[ "$FILE_PATH" == *"models"* ]]; then
    # Schedule database schema validation
    echo "$FILE_PATH|$(date +%s)" >> ".claude/cache/schema-validation-queue"
fi

if [[ "$FILE_EXT" == "md" ]] && [[ "$FILE_PATH" == *"docs"* ]]; then
    # Schedule documentation validation
    echo "$FILE_PATH" >> ".claude/cache/docs-to-validate"
fi

log "✅ File change analysis complete"

exit 0