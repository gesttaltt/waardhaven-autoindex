#!/bin/bash
# Code quality monitoring hook - tracks code quality metrics and trends
# Provides insights into code quality changes and technical debt

ANALYSIS_TYPE="$1"  # real_time, daily, weekly, or specific file
TARGET="$2"         # file path or date range
LOG_FILE=".claude/logs/quality-$(date +%Y%m%d).log"
CACHE_DIR=".claude/cache"
METRICS_DIR=".claude/cache/metrics"

# Create necessary directories
mkdir -p ".claude/logs" "$CACHE_DIR" "$METRICS_DIR"

# Logging function
log() {
    echo "$(date '+%H:%M:%S') [QUALITY] $1" | tee -a "$LOG_FILE"
}

log "📊 Code quality analysis: $ANALYSIS_TYPE"

# Quality metrics structure
declare -A METRICS
METRICS[total_files]=0
METRICS[python_files]=0
METRICS[typescript_files]=0
METRICS[test_files]=0
METRICS[doc_files]=0
METRICS[lines_of_code]=0
METRICS[complexity_score]=0
METRICS[test_coverage]=0
METRICS[lint_issues]=0
METRICS[type_errors]=0
METRICS[security_issues]=0
METRICS[duplication_score]=0

# Quality thresholds
COMPLEXITY_THRESHOLD=10
COVERAGE_THRESHOLD=80
LINT_THRESHOLD=5
DUPLICATION_THRESHOLD=5

# Initialize quality report
QUALITY_REPORT=()
RECOMMENDATIONS=()
TRENDS=()

# Function to analyze Python code quality
analyze_python_quality() {
    local files_analyzed=0
    local total_complexity=0
    local total_lines=0
    
    log "🐍 Analyzing Python code quality..."
    
    # Find Python files
    if [ -d "apps/api" ]; then
        while IFS= read -r -d '' file; do
            if [[ "$file" == *"__pycache__"* ]] || [[ "$file" == *".pyc" ]]; then
                continue
            fi
            
            files_analyzed=$((files_analyzed + 1))
            METRICS[python_files]=$((METRICS[python_files] + 1))
            
            # Count lines of code (excluding comments and empty lines)
            lines=$(grep -cve '^\s*#' -e '^\s*$' "$file" 2>/dev/null || echo 0)
            total_lines=$((total_lines + lines))
            
            # Basic complexity analysis (count function definitions, loops, conditionals)
            complexity=$(grep -c -E '^\s*(def |if |for |while |try:|except|class )' "$file" 2>/dev/null || echo 0)
            total_complexity=$((total_complexity + complexity))
            
        done < <(find apps/api -name "*.py" -type f -print0 2>/dev/null)
        
        METRICS[lines_of_code]=$((METRICS[lines_of_code] + total_lines))
        if [ $files_analyzed -gt 0 ]; then
            METRICS[complexity_score]=$((total_complexity / files_analyzed))
        fi
        
        QUALITY_REPORT+=("Python files analyzed: $files_analyzed")
        QUALITY_REPORT+=("Python lines of code: $total_lines")
        QUALITY_REPORT+=("Average complexity: ${METRICS[complexity_score]}")
        
        # Run linting if available
        if command -v ruff >/dev/null 2>&1; then
            log "🔍 Running Python linting..."
            lint_output=$(cd apps/api && ruff check . 2>/dev/null | wc -l)
            METRICS[lint_issues]=$((METRICS[lint_issues] + lint_output))
            QUALITY_REPORT+=("Python lint issues: $lint_output")
            
            if [ $lint_output -gt $LINT_THRESHOLD ]; then
                RECOMMENDATIONS+=("🔧 Python: $lint_output lint issues exceed threshold ($LINT_THRESHOLD)")
            fi
        fi
        
        # Run type checking if available
        if command -v mypy >/dev/null 2>&1; then
            log "📝 Running Python type checking..."
            type_errors=$(cd apps/api && mypy app --ignore-missing-imports 2>/dev/null | grep -c "error:" || echo 0)
            METRICS[type_errors]=$((METRICS[type_errors] + type_errors))
            QUALITY_REPORT+=("Python type errors: $type_errors")
            
            if [ $type_errors -gt 0 ]; then
                RECOMMENDATIONS+=("📝 Python: $type_errors type errors found")
            fi
        fi
    fi
}

# Function to analyze TypeScript code quality
analyze_typescript_quality() {
    local files_analyzed=0
    local total_lines=0
    
    log "📘 Analyzing TypeScript code quality..."
    
    # Find TypeScript files
    if [ -d "apps/web" ]; then
        while IFS= read -r -d '' file; do
            if [[ "$file" == *"node_modules"* ]] || [[ "$file" == *".next"* ]]; then
                continue
            fi
            
            files_analyzed=$((files_analyzed + 1))
            METRICS[typescript_files]=$((METRICS[typescript_files] + 1))
            
            # Count lines of code
            lines=$(grep -cve '^\s*//' -e '^\s*$' "$file" 2>/dev/null || echo 0)
            total_lines=$((total_lines + lines))
            
        done < <(find apps/web -name "*.ts" -o -name "*.tsx" -type f -print0 2>/dev/null)
        
        METRICS[lines_of_code]=$((METRICS[lines_of_code] + total_lines))
        
        QUALITY_REPORT+=("TypeScript files analyzed: $files_analyzed")
        QUALITY_REPORT+=("TypeScript lines of code: $total_lines")
        
        # Run TypeScript compilation check
        if [ -f "apps/web/tsconfig.json" ]; then
            log "🔍 Running TypeScript compilation check..."
            ts_errors=$(cd apps/web && npx tsc --noEmit 2>&1 | grep -c "error TS" || echo 0)
            METRICS[type_errors]=$((METRICS[type_errors] + ts_errors))
            QUALITY_REPORT+=("TypeScript compilation errors: $ts_errors")
            
            if [ $ts_errors -gt 0 ]; then
                RECOMMENDATIONS+=("📘 TypeScript: $ts_errors compilation errors found")
            fi
        fi
        
        # Run ESLint if available
        if [ -f "apps/web/package.json" ] && grep -q "eslint" "apps/web/package.json"; then
            log "🔍 Running TypeScript linting..."
            eslint_issues=$(cd apps/web && npm run lint 2>/dev/null | grep -c "warning\|error" || echo 0)
            METRICS[lint_issues]=$((METRICS[lint_issues] + eslint_issues))
            QUALITY_REPORT+=("TypeScript lint issues: $eslint_issues")
            
            if [ $eslint_issues -gt $LINT_THRESHOLD ]; then
                RECOMMENDATIONS+=("🔧 TypeScript: $eslint_issues lint issues exceed threshold ($LINT_THRESHOLD)")
            fi
        fi
    fi
}

# Function to analyze test coverage
analyze_test_coverage() {
    log "🧪 Analyzing test coverage..."
    
    # Count test files
    test_count=0
    if [ -d "apps/api/tests" ]; then
        test_count=$(find apps/api/tests -name "test_*.py" -type f | wc -l)
        METRICS[test_files]=$((METRICS[test_files] + test_count))
    fi
    
    if [ -d "apps/web/__tests__" ] || [ -d "apps/web/src/__tests__" ]; then
        test_count=$((test_count + $(find apps/web -name "*.test.ts" -o -name "*.test.tsx" -type f | wc -l)))
        METRICS[test_files]=$((METRICS[test_files] + test_count))
    fi
    
    QUALITY_REPORT+=("Test files found: ${METRICS[test_files]}")
    
    # Estimate coverage based on file ratios
    if [ ${METRICS[python_files]} -gt 0 ]; then
        python_test_ratio=$((METRICS[test_files] * 100 / METRICS[python_files]))
        QUALITY_REPORT+=("Python test ratio: ${python_test_ratio}%")
        
        if [ $python_test_ratio -lt 50 ]; then
            RECOMMENDATIONS+=("🧪 Python: Test coverage appears low (${python_test_ratio}% test files)")
        fi
    fi
    
    # Run pytest coverage if available
    if command -v pytest >/dev/null 2>&1 && [ -d "apps/api" ]; then
        coverage_output=$(cd apps/api && python -m pytest --cov=app --cov-report=term-missing 2>/dev/null | grep "TOTAL" | awk '{print $4}' | sed 's/%//' || echo 0)
        if [ ! -z "$coverage_output" ] && [ "$coverage_output" != "0" ]; then
            METRICS[test_coverage]=$coverage_output
            QUALITY_REPORT+=("Python test coverage: ${coverage_output}%")
            
            if [ $coverage_output -lt $COVERAGE_THRESHOLD ]; then
                RECOMMENDATIONS+=("🧪 Python: Test coverage ($coverage_output%) below threshold ($COVERAGE_THRESHOLD%)")
            fi
        fi
    fi
}

# Function to check for code duplication
analyze_code_duplication() {
    log "🔍 Analyzing code duplication..."
    
    # Simple duplication detection based on identical lines
    duplication_score=0
    
    if [ -d "apps/api" ]; then
        # Find potential duplicated functions/classes
        duplicates=$(find apps/api -name "*.py" -exec grep -l "def \|class " {} \; | xargs grep -h "def \|class " | sort | uniq -d | wc -l)
        duplication_score=$((duplication_score + duplicates))
    fi
    
    if [ -d "apps/web" ]; then
        # Find potential duplicated components/functions
        duplicates=$(find apps/web -name "*.ts" -o -name "*.tsx" | xargs grep -h "function \|const.*= \|export.*function" 2>/dev/null | sort | uniq -d | wc -l)
        duplication_score=$((duplication_score + duplicates))
    fi
    
    METRICS[duplication_score]=$duplication_score
    QUALITY_REPORT+=("Potential duplications: $duplication_score")
    
    if [ $duplication_score -gt $DUPLICATION_THRESHOLD ]; then
        RECOMMENDATIONS+=("🔄 Code duplication detected: $duplication_score potential duplicates")
    fi
}

# Function to check for security issues
analyze_security() {
    log "🔒 Analyzing security patterns..."
    
    security_issues=0
    
    # Check for hardcoded secrets
    secrets=$(grep -r -i "api_key\s*=\|secret\s*=\|password\s*=" --include="*.py" --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v ".env\|example\|test" | wc -l)
    security_issues=$((security_issues + secrets))
    
    # Check for SQL injection patterns
    sql_issues=$(grep -r "SELECT.*%s\|INSERT.*%s" --include="*.py" . 2>/dev/null | wc -l)
    security_issues=$((security_issues + sql_issues))
    
    # Check for dangerous operations
    dangerous_ops=$(grep -r "DELETE FROM\|TRUNCATE\|DROP TABLE" --include="*.py" --include="*.sql" . 2>/dev/null | grep -v "test\|#.*safe" | wc -l)
    security_issues=$((security_issues + dangerous_ops))
    
    METRICS[security_issues]=$security_issues
    QUALITY_REPORT+=("Security issues detected: $security_issues")
    
    if [ $security_issues -gt 0 ]; then
        RECOMMENDATIONS+=("🔒 Security: $security_issues potential security issues found")
    fi
}

# Function to analyze documentation quality
analyze_documentation() {
    log "📖 Analyzing documentation quality..."
    
    if [ -d "docs" ]; then
        doc_count=$(find docs -name "*.md" -type f | wc -l)
        METRICS[doc_files]=$doc_count
        QUALITY_REPORT+=("Documentation files: $doc_count")
        
        # Check for TODO items in docs
        todo_count=$(find docs -name "*.md" -exec grep -c "TODO\|FIXME\|XXX" {} \; 2>/dev/null | awk '{sum+=$1} END {print sum+0}')
        if [ $todo_count -gt 0 ]; then
            QUALITY_REPORT+=("Documentation TODOs: $todo_count")
            RECOMMENDATIONS+=("📝 Documentation: $todo_count TODO items need attention")
        fi
        
        # Check for broken links (simple check)
        broken_links=$(find docs -name "*.md" -exec grep -c "\[\](\|]()" {} \; 2>/dev/null | awk '{sum+=$1} END {print sum+0}')
        if [ $broken_links -gt 0 ]; then
            QUALITY_REPORT+=("Potential broken links: $broken_links")
            RECOMMENDATIONS+=("🔗 Documentation: $broken_links potential broken links")
        fi
    fi
}

# Function to calculate overall quality score
calculate_quality_score() {
    local score=100
    
    # Deduct points for issues
    score=$((score - METRICS[lint_issues]))
    score=$((score - METRICS[type_errors] * 2))
    score=$((score - METRICS[security_issues] * 5))
    score=$((score - METRICS[duplication_score]))
    
    # Bonus points for good practices
    if [ ${METRICS[test_coverage]} -gt 80 ]; then
        score=$((score + 10))
    fi
    
    if [ ${METRICS[test_files]} -gt 5 ]; then
        score=$((score + 5))
    fi
    
    # Ensure score is between 0 and 100
    if [ $score -lt 0 ]; then score=0; fi
    if [ $score -gt 100 ]; then score=100; fi
    
    echo $score
}

# Main analysis execution
case "$ANALYSIS_TYPE" in
    "real_time"|"file_change")
        log "⚡ Real-time quality analysis"
        
        if [ ! -z "$TARGET" ] && [ -f "$TARGET" ]; then
            # Analyze specific file
            log "📁 Analyzing file: $TARGET"
            
            case "$TARGET" in
                *.py)
                    analyze_python_quality
                    ;;
                *.ts|*.tsx)
                    analyze_typescript_quality
                    ;;
                *.md)
                    analyze_documentation
                    ;;
            esac
        else
            # Quick analysis
            analyze_python_quality
            analyze_typescript_quality
            analyze_security
        fi
        ;;
        
    "daily")
        log "📅 Daily quality analysis"
        
        # Comprehensive daily analysis
        analyze_python_quality
        analyze_typescript_quality
        analyze_test_coverage
        analyze_code_duplication
        analyze_security
        analyze_documentation
        ;;
        
    "weekly")
        log "📊 Weekly quality analysis"
        
        # Full comprehensive analysis with trends
        analyze_python_quality
        analyze_typescript_quality
        analyze_test_coverage
        analyze_code_duplication
        analyze_security
        analyze_documentation
        
        # Analyze trends from previous reports
        if [ -d "$METRICS_DIR" ]; then
            RECENT_REPORTS=$(find "$METRICS_DIR" -name "quality-*.json" -mtime -7 | wc -l)
            QUALITY_REPORT+=("Reports in last 7 days: $RECENT_REPORTS")
        fi
        ;;
        
    *)
        log "❓ Unknown analysis type: $ANALYSIS_TYPE"
        exit 1
        ;;
esac

# Calculate overall quality score
QUALITY_SCORE=$(calculate_quality_score)
QUALITY_REPORT+=("Overall Quality Score: $QUALITY_SCORE/100")

# AI Investment project specific analysis
if [ -f "CLAUDE.md" ]; then
    log "💰 AI Investment project specific analysis"
    
    # Check for financial calculation safety
    calc_files=$(find apps/api -name "*calculation*" -o -name "*portfolio*" -o -name "*index*" | wc -l)
    if [ $calc_files -gt 0 ]; then
        QUALITY_REPORT+=("Financial calculation files: $calc_files")
        
        # Check for proper error handling in financial code
        error_handling=$(find apps/api -name "*calculation*" -exec grep -c "try:\|except" {} \; 2>/dev/null | awk '{sum+=$1} END {print sum+0}')
        if [ $error_handling -lt $calc_files ]; then
            RECOMMENDATIONS+=("💰 Financial: Add error handling to calculation modules")
        fi
    fi
    
    # Check API integration safety
    api_files=$(find apps/api -name "*service*" -exec grep -l "requests\|http" {} \; 2>/dev/null | wc -l)
    if [ $api_files -gt 0 ]; then
        QUALITY_REPORT+=("API integration files: $api_files")
        
        # Check for rate limiting
        rate_limiting=$(find apps/api -exec grep -c "rate.*limit\|sleep\|timeout" {} \; 2>/dev/null | awk '{sum+=$1} END {print sum+0}')
        if [ $rate_limiting -lt $api_files ]; then
            RECOMMENDATIONS+=("🌐 API: Implement rate limiting for external API calls")
        fi
    fi
fi

# Output quality report
log "📊 Quality Analysis Report:"
for report_item in "${QUALITY_REPORT[@]}"; do
    log "  📋 $report_item"
done

if [ ${#RECOMMENDATIONS[@]} -gt 0 ]; then
    log "💡 Quality Recommendations:"
    for recommendation in "${RECOMMENDATIONS[@]}"; do
        log "  • $recommendation"
    done
fi

# Save metrics to file
METRICS_FILE="$METRICS_DIR/quality-$(date +%Y%m%d-%H%M%S).json"
cat > "$METRICS_FILE" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "analysis_type": "$ANALYSIS_TYPE",
  "metrics": {
    "total_files": ${METRICS[total_files]},
    "python_files": ${METRICS[python_files]},
    "typescript_files": ${METRICS[typescript_files]},
    "test_files": ${METRICS[test_files]},
    "doc_files": ${METRICS[doc_files]},
    "lines_of_code": ${METRICS[lines_of_code]},
    "complexity_score": ${METRICS[complexity_score]},
    "test_coverage": ${METRICS[test_coverage]},
    "lint_issues": ${METRICS[lint_issues]},
    "type_errors": ${METRICS[type_errors]},
    "security_issues": ${METRICS[security_issues]},
    "duplication_score": ${METRICS[duplication_score]},
    "quality_score": $QUALITY_SCORE
  },
  "recommendations": $(printf '%s\n' "${RECOMMENDATIONS[@]}" | jq -R . | jq -s .),
  "report": $(printf '%s\n' "${QUALITY_REPORT[@]}" | jq -R . | jq -s .)
}
EOF

# Update latest metrics cache
cp "$METRICS_FILE" "$CACHE_DIR/latest-quality-metrics.json"

# Clean up old metrics (keep last 30 days)
find "$METRICS_DIR" -name "quality-*.json" -mtime +30 -delete 2>/dev/null

log "✅ Quality analysis complete - saved to $METRICS_FILE"

# Quality score summary
if [ $QUALITY_SCORE -ge 90 ]; then
    log "🌟 Excellent code quality!"
elif [ $QUALITY_SCORE -ge 75 ]; then
    log "✅ Good code quality"
elif [ $QUALITY_SCORE -ge 50 ]; then
    log "⚠️  Code quality needs improvement"
else
    log "🚨 Code quality needs immediate attention"
fi

exit 0