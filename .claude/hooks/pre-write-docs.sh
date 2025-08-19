#!/bin/bash
# Enhanced pre-write hook for documentation files
# Comprehensive validation and auto-fixing for documentation

FILE_PATH="$1"
CONTENT="$2"
LOG_FILE=".claude/logs/doc-validation-$(date +%Y%m%d).log"

# Create log directory if needed
mkdir -p ".claude/logs" ".claude/cache"

# Logging function
log() {
    echo "$(date '+%H:%M:%S') [DOC-WRITE] $1" | tee -a "$LOG_FILE"
}

# Check if it's a documentation file
if [[ "$FILE_PATH" == *"/docs/"* ]] || [[ "$FILE_PATH" == *.md ]]; then
    log "🔍 Enhanced validation for: $FILE_PATH"
    
    ISSUES=0
    WARNINGS=0
    SUGGESTIONS=()
    AUTO_FIXES=()
    
    # 1. Check for duplicate file names with better intelligence
    BASENAME=$(basename "$FILE_PATH")
    DIRNAME=$(dirname "$FILE_PATH")
    
    # Find similar files (not just exact matches)
    SIMILAR_FILES=$(find "$DIRNAME" -name "*.md" -type f 2>/dev/null | while read -r file; do
        if [ "$file" != "$FILE_PATH" ]; then
            similarity=$(echo "$BASENAME" "$file" | awk '{
                gsub(/[-_]/, " ", $1); gsub(/[-_]/, " ", $2)
                gsub(/\.md$/, "", $1); gsub(/\.md$/, "", $2)
                if (tolower($1) == tolower($2)) print "exact"
                else if (index(tolower($2), tolower($1)) > 0 || index(tolower($1), tolower($2)) > 0) print "similar"
            }')
            if [ "$similarity" = "exact" ] || [ "$similarity" = "similar" ]; then
                echo "$file ($similarity)"
            fi
        fi
    done)
    
    if [ ! -z "$SIMILAR_FILES" ]; then
        log "⚠️  Similar files detected:"
        echo "$SIMILAR_FILES" | while read -r similar; do
            log "  • $similar"
        done
        WARNINGS=$((WARNINGS + 1))
        SUGGESTIONS+=("Consider consolidating with existing similar files")
    fi
    
    # 2. Enhanced content validation
    
    # Check for TODO items with context
    TODO_COUNT=$(echo "$CONTENT" | grep -c "TODO\|FIXME\|XXX" || echo 0)
    if [ $TODO_COUNT -gt 0 ]; then
        log "📝 Found $TODO_COUNT TODO items"
        SUGGESTIONS+=("Document contains $TODO_COUNT TODO items - consider creating tasks")
    fi
    
    # Check for placeholder patterns
    PLACEHOLDERS=$(echo "$CONTENT" | grep -oE '\[PLACEHOLDER[^]]*\]|\[TBD\]|\[TODO[^]]*\]|\{[A-Z_]+\}' | wc -l)
    if [ $PLACEHOLDERS -gt 0 ]; then
        log "⚠️  Found $PLACEHOLDERS placeholder patterns"
        ISSUES=$((ISSUES + 1))
        SUGGESTIONS+=("Replace placeholder text with actual content")
    fi
    
    # 3. Markdown link validation
    
    # Empty links
    EMPTY_LINKS=$(echo "$CONTENT" | grep -oE '\[.*\]\(\s*\)' | wc -l)
    if [ $EMPTY_LINKS -gt 0 ]; then
        log "⚠️  Found $EMPTY_LINKS empty markdown links"
        ISSUES=$((ISSUES + 1))
        AUTO_FIXES+=("Remove or fix empty markdown links")
    fi
    
    # Malformed links
    MALFORMED_LINKS=$(echo "$CONTENT" | grep -oE '\[[^]]*\]\([^)]*[^)]$' | wc -l)
    if [ $MALFORMED_LINKS -gt 0 ]; then
        log "⚠️  Found $MALFORMED_LINKS malformed links"
        ISSUES=$((ISSUES + 1))
    fi
    
    # Internal links validation
    INTERNAL_LINKS=$(echo "$CONTENT" | grep -oE '\[[^]]*\]\([^http][^)]*\)' | grep -o '([^)]*)' | tr -d '()')
    if [ ! -z "$INTERNAL_LINKS" ]; then
        log "🔗 Validating internal links..."
        echo "$INTERNAL_LINKS" | while read -r link; do
            if [ ! -z "$link" ] && [ ! -f "$link" ] && [ ! -d "$link" ]; then
                # Try relative to document directory
                if [ ! -f "$DIRNAME/$link" ]; then
                    log "❌ Broken internal link: $link"
                    ISSUES=$((ISSUES + 1))
                fi
            fi
        done
    fi
    
    # 4. AI Investment project specific validation
    if [ -f "CLAUDE.md" ]; then
        log "💰 AI Investment project documentation checks"
        
        # Check for outdated API references
        if echo "$CONTENT" | grep -q "/api/v1/me"; then
            log "⚠️  Outdated API reference: /api/v1/me endpoint removed"
            WARNINGS=$((WARNINGS + 1))
            SUGGESTIONS+=("Update API endpoints to current specification")
        fi
        
        # Check for financial term consistency
        FINANCIAL_TERMS="portfolio index calculation sharpe beta correlation drawdown"
        for term in $FINANCIAL_TERMS; do
            variations=$(echo "$CONTENT" | grep -io "$term\|${term}s\|${term^}\|${term^}s" | sort | uniq)
            if [ $(echo "$variations" | wc -l) -gt 1 ]; then
                log "📊 Inconsistent financial terminology: $term"
                SUGGESTIONS+=("Standardize financial terminology: $term")
            fi
        done
        
        # Check for security mentions in financial context
        if echo "$CONTENT" | grep -qi "api.*key\|secret\|password" && ! echo "$CONTENT" | grep -qi "environment\|config"; then
            log "🔒 Security content detected - ensure no secrets disclosed"
            WARNINGS=$((WARNINGS + 1))
        fi
    fi
    
    # 5. Documentation structure analysis
    
    # Check for proper heading structure
    HEADINGS=$(echo "$CONTENT" | grep -E '^#{1,6} ' | sed 's/^#* //' | head -10)
    if [ ! -z "$HEADINGS" ]; then
        log "📋 Document structure detected"
        
        # Check for table of contents if document is long
        LINES=$(echo "$CONTENT" | wc -l)
        if [ $LINES -gt 100 ] && ! echo "$CONTENT" | grep -qi "table of contents\|toc"; then
            SUGGESTIONS+=("Consider adding table of contents for long document ($LINES lines)")
        fi
    fi
    
    # Check for code blocks formatting
    CODE_BLOCKS=$(echo "$CONTENT" | grep -c '```' || echo 0)
    if [ $((CODE_BLOCKS % 2)) -ne 0 ]; then
        log "❌ Unmatched code block markers"
        ISSUES=$((ISSUES + 1))
    fi
    
    # 6. Date and version information
    if ! echo "$CONTENT" | grep -qi "last.updated\|date\|version"; then
        SUGGESTIONS+=("Consider adding last updated date or version information")
    fi
    
    # Check for 2024 dates (potentially outdated)
    if echo "$CONTENT" | grep -q "2024"; then
        log "📅 Document contains 2024 dates - may need updating"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # 7. Generate auto-fixes if possible
    FIXED_CONTENT="$CONTENT"
    
    # Auto-fix: Remove empty links
    if [ $EMPTY_LINKS -gt 0 ]; then
        FIXED_CONTENT=$(echo "$FIXED_CONTENT" | sed 's/\[[^]]*\](\s*)//g')
        AUTO_FIXES+=("Removed $EMPTY_LINKS empty links")
    fi
    
    # Auto-fix: Update dates to current year
    if echo "$CONTENT" | grep -q "Last updated:.*2024"; then
        FIXED_CONTENT=$(echo "$FIXED_CONTENT" | sed "s/Last updated:.*2024.*/Last updated: $(date '+%Y-%m-%d')/g")
        AUTO_FIXES+=("Updated last modified date")
    fi
    
    # 8. Save validation results
    VALIDATION_RESULT="{
        \"file\": \"$FILE_PATH\",
        \"timestamp\": \"$(date -Iseconds)\",
        \"issues\": $ISSUES,
        \"warnings\": $WARNINGS,
        \"suggestions\": $(printf '%s\n' "${SUGGESTIONS[@]}" | jq -R . | jq -s .),
        \"auto_fixes\": $(printf '%s\n' "${AUTO_FIXES[@]}" | jq -R . | jq -s .)
    }"
    
    echo "$VALIDATION_RESULT" > ".claude/cache/doc-validation-$(basename "$FILE_PATH").json"
    
    # 9. Output summary
    if [ $ISSUES -eq 0 ] && [ $WARNINGS -eq 0 ]; then
        log "✅ Documentation validation passed"
    else
        log "📊 Validation summary: $ISSUES issues, $WARNINGS warnings"
        
        if [ ${#SUGGESTIONS[@]} -gt 0 ]; then
            log "💡 Suggestions:"
            for suggestion in "${SUGGESTIONS[@]}"; do
                log "  • $suggestion"
            done
        fi
        
        if [ ${#AUTO_FIXES[@]} -gt 0 ]; then
            log "🔧 Auto-fixes applied:"
            for fix in "${AUTO_FIXES[@]}"; do
                log "  • $fix"
            done
        fi
    fi
    
    # 10. Integration with other documentation
    if [[ "$FILE_PATH" == *"API"* ]] || [[ "$CONTENT" == *"endpoint"* ]]; then
        log "🔄 API documentation detected - consider updating OpenAPI spec"
        SUGGESTIONS+=("Sync with OpenAPI specification")
    fi
    
    if [[ "$FILE_PATH" == *"README"* ]]; then
        log "📖 README file - ensure it reflects current project state"
        SUGGESTIONS+=("Verify README accuracy with current codebase")
    fi
    
    log "✅ Enhanced documentation validation complete"
    
    # Return fixed content if auto-fixes were applied
    if [ ${#AUTO_FIXES[@]} -gt 0 ]; then
        echo "$FIXED_CONTENT" > "/tmp/claude-doc-autofixed-$$.md"
        log "💾 Auto-fixed content saved to temp file for review"
    fi
fi

exit 0