#!/bin/bash
# Automatic test runner hook - intelligently runs relevant tests based on code changes
# Triggered when code changes are detected to run appropriate test suites

TRIGGER_TYPE="$1"   # file_change, manual, pre_commit, post_commit
CHANGED_FILES="$2"  # comma-separated list of changed files
FORCE_ALL="$3"      # true to force running all tests

LOG_FILE=".claude/logs/test-runner-$(date +%Y%m%d).log"
CACHE_DIR=".claude/cache"
SESSION_DIR=".claude/session"

# Create necessary directories
mkdir -p ".claude/logs" "$CACHE_DIR" "$SESSION_DIR"

# Logging function
log() {
    echo "$(date '+%H:%M:%S') [TEST-RUNNER] $1" | tee -a "$LOG_FILE"
}

log "🧪 Auto test runner triggered: $TRIGGER_TYPE"

# Test configuration
BACKEND_TEST_CMD="cd apps/api && python -m pytest"
FRONTEND_TEST_CMD="cd apps/web && npm test -- --watchAll=false"
BACKEND_QUICK_CMD="cd apps/api && python -m pytest tests/test_calculations.py -v"
FRONTEND_QUICK_CMD="cd apps/web && npm run lint"

# Initialize test plan
TEST_PLAN=()
QUICK_TESTS=()
FULL_TESTS=()
LINT_CHECKS=()
TYPE_CHECKS=()

# Parse changed files if provided
if [ ! -z "$CHANGED_FILES" ] && [ "$CHANGED_FILES" != "null" ]; then
    IFS=',' read -ra FILES <<< "$CHANGED_FILES"
    
    PYTHON_FILES=()
    TYPESCRIPT_FILES=()
    CONFIG_FILES=()
    
    for file in "${FILES[@]}"; do
        case "$file" in
            *.py)
                PYTHON_FILES+=("$file")
                ;;
            *.ts|*.tsx|*.js|*.jsx)
                TYPESCRIPT_FILES+=("$file")
                ;;
            *.json|*.yml|*.yaml|*.env)
                CONFIG_FILES+=("$file")
                ;;
        esac
    done
    
    log "📁 Changed files analysis:"
    log "  Python files: ${#PYTHON_FILES[@]}"
    log "  TypeScript files: ${#TYPESCRIPT_FILES[@]}"
    log "  Config files: ${#CONFIG_FILES[@]}"
else
    log "📁 No specific files provided - analyzing based on trigger"
fi

# Determine test strategy based on trigger and changes
case "$TRIGGER_TYPE" in
    "file_change")
        log "📝 File change trigger - running targeted tests"
        
        # Python file changes
        if [ ${#PYTHON_FILES[@]} -gt 0 ]; then
            for file in "${PYTHON_FILES[@]}"; do
                if [[ "$file" == *"models"* ]]; then
                    QUICK_TESTS+=("Database model tests")
                    TEST_PLAN+=("cd apps/api && python -m pytest tests/test_models.py -v")
                elif [[ "$file" == *"routers"* ]]; then
                    QUICK_TESTS+=("API endpoint tests")
                    TEST_PLAN+=("cd apps/api && python -m pytest tests/test_routers.py -v")
                elif [[ "$file" == *"services"* ]]; then
                    QUICK_TESTS+=("Service layer tests")
                    if [[ "$file" == *"calculation"* ]]; then
                        TEST_PLAN+=("cd apps/api && python -m pytest tests/test_calculations.py -v")
                    else
                        TEST_PLAN+=("cd apps/api && python -m pytest tests/test_services.py -v")
                    fi
                fi
            done
            
            LINT_CHECKS+=("Python linting: cd apps/api && ruff check .")
            TYPE_CHECKS+=("Python types: cd apps/api && mypy app")
        fi
        
        # TypeScript file changes
        if [ ${#TYPESCRIPT_FILES[@]} -gt 0 ]; then
            QUICK_TESTS+=("TypeScript compilation")
            TYPE_CHECKS+=("TypeScript check: cd apps/web && npx tsc --noEmit")
            LINT_CHECKS+=("Frontend linting: cd apps/web && npm run lint")
            
            # Only run Jest tests if test files exist
            if [ -d "apps/web/__tests__" ] || [ -d "apps/web/src/__tests__" ]; then
                TEST_PLAN+=("cd apps/web && npm test -- --watchAll=false")
            fi
        fi
        
        # Config file changes
        if [ ${#CONFIG_FILES[@]} -gt 0 ]; then
            QUICK_TESTS+=("Configuration validation")
            for file in "${CONFIG_FILES[@]}"; do
                if [[ "$file" == "package.json" ]]; then
                    TEST_PLAN+=("npm audit --audit-level=high")
                elif [[ "$file" == *.json ]]; then
                    if command -v jq >/dev/null 2>&1; then
                        TEST_PLAN+=("jq empty '$file'")
                    fi
                fi
            done
        fi
        ;;
        
    "pre_commit")
        log "📦 Pre-commit trigger - running essential tests"
        
        # Always run critical tests before commit
        QUICK_TESTS+=("Critical calculation tests")
        TEST_PLAN+=("cd apps/api && python -m pytest tests/test_calculations.py -v")
        
        # Type and lint checks
        TYPE_CHECKS+=("TypeScript check: cd apps/web && npx tsc --noEmit")
        LINT_CHECKS+=("Python linting: cd apps/api && ruff check .")
        LINT_CHECKS+=("Frontend linting: cd apps/web && npm run lint")
        
        # Security checks
        TEST_PLAN+=("Security scan: bash .claude/hooks/pre-commit/check-secrets.sh")
        TEST_PLAN+=("Delete operation check: bash .claude/hooks/pre-commit/check-deletes.sh")
        ;;
        
    "post_commit")
        log "✅ Post-commit trigger - comprehensive test suite"
        
        # Run full test suite after successful commit
        FULL_TESTS+=("Complete backend test suite")
        FULL_TESTS+=("Complete frontend test suite")
        TEST_PLAN+=("$BACKEND_TEST_CMD")
        if [ -d "apps/web/__tests__" ]; then
            TEST_PLAN+=("$FRONTEND_TEST_CMD")
        fi
        ;;
        
    "manual")
        log "👤 Manual trigger - running comprehensive tests"
        
        if [ "$FORCE_ALL" = "true" ]; then
            FULL_TESTS+=("All tests (forced)")
            TEST_PLAN+=("$BACKEND_TEST_CMD")
            TEST_PLAN+=("$FRONTEND_TEST_CMD")
            TEST_PLAN+=("cd apps/api && python -m pytest --cov=app --cov-report=term-missing")
        else
            QUICK_TESTS+=("Quick test suite")
            TEST_PLAN+=("$BACKEND_QUICK_CMD")
            TEST_PLAN+=("$FRONTEND_QUICK_CMD")
        fi
        ;;
esac

# Add AI Investment project specific tests
if [ -f "CLAUDE.md" ]; then
    # Financial calculation tests are critical
    if [[ " ${QUICK_TESTS[*]} " == *"Critical calculation tests"* ]] || [[ " ${FULL_TESTS[*]} " == *"All tests"* ]]; then
        log "💰 AI Investment specific tests included"
    else
        # Add minimal financial tests for any change
        TEST_PLAN+=("cd apps/api && python -c \"import app.services.calculation_service; print('Calculation service import: OK')\"")
    fi
fi

# Environment validation before running tests
ENV_ISSUES=0

# Check if we're in the right directory
if [ ! -f "CLAUDE.md" ]; then
    log "⚠️  Not in AI Investment project root"
    ENV_ISSUES=$((ENV_ISSUES + 1))
fi

# Check Python environment for backend tests
if [[ " ${TEST_PLAN[*]} " == *"apps/api"* ]]; then
    if ! command -v python >/dev/null 2>&1; then
        log "❌ Python not found for backend tests"
        ENV_ISSUES=$((ENV_ISSUES + 1))
    elif [ ! -f "apps/api/requirements.txt" ]; then
        log "⚠️  Backend requirements.txt not found"
        ENV_ISSUES=$((ENV_ISSUES + 1))
    fi
fi

# Check Node environment for frontend tests
if [[ " ${TEST_PLAN[*]} " == *"apps/web"* ]]; then
    if ! command -v npm >/dev/null 2>&1; then
        log "❌ npm not found for frontend tests"
        ENV_ISSUES=$((ENV_ISSUES + 1))
    elif [ ! -f "apps/web/package.json" ]; then
        log "⚠️  Frontend package.json not found"
        ENV_ISSUES=$((ENV_ISSUES + 1))
    fi
fi

# Database connectivity for backend tests
if [[ " ${TEST_PLAN[*]} " == *"pytest"* ]]; then
    if [ -z "$DATABASE_URL" ]; then
        log "⚠️  DATABASE_URL not set - tests may fail"
        ENV_ISSUES=$((ENV_ISSUES + 1))
    fi
fi

if [ $ENV_ISSUES -gt 0 ]; then
    log "⚠️  $ENV_ISSUES environment issues detected"
    log "🤔 Some tests may fail or be skipped"
fi

# Execute test plan
if [ ${#TEST_PLAN[@]} -eq 0 ]; then
    log "ℹ️  No tests to run based on trigger and changes"
    exit 0
fi

log "🚀 Executing test plan:"
for test in "${QUICK_TESTS[@]}"; do
    log "  📋 $test"
done
for test in "${FULL_TESTS[@]}"; do
    log "  📋 $test"
done
for test in "${LINT_CHECKS[@]}"; do
    log "  📋 $test"
done
for test in "${TYPE_CHECKS[@]}"; do
    log "  📋 $test"
done

# Track test execution
TESTS_PASSED=0
TESTS_FAILED=0
START_TIME=$(date +%s)

# Execute type checks first (fast feedback)
for check in "${TYPE_CHECKS[@]}"; do
    log "🔍 Running: $check"
    if eval "$check" >> "$LOG_FILE" 2>&1; then
        log "✅ Type check passed"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        log "❌ Type check failed"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
done

# Execute lint checks
for check in "${LINT_CHECKS[@]}"; do
    log "📝 Running: $check"
    if eval "$check" >> "$LOG_FILE" 2>&1; then
        log "✅ Lint check passed"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        log "⚠️  Lint check issues found"
        # Don't count lint failures as hard failures
    fi
done

# Execute actual tests
for test_cmd in "${TEST_PLAN[@]}"; do
    log "🧪 Running: $test_cmd"
    
    if eval "$test_cmd" >> "$LOG_FILE" 2>&1; then
        log "✅ Test passed"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        log "❌ Test failed"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        
        # Show last few lines of failure for context
        log "📄 Recent test output:"
        tail -5 "$LOG_FILE" | sed 's/^/  /'
    fi
done

# Calculate execution time
END_TIME=$(date +%s)
EXECUTION_TIME=$((END_TIME - START_TIME))

# Test summary
log "📊 Test Execution Summary:"
log "  ✅ Passed: $TESTS_PASSED"
log "  ❌ Failed: $TESTS_FAILED"
log "  ⏱️  Duration: ${EXECUTION_TIME}s"

# Save test results to cache
TEST_RESULT_FILE="$CACHE_DIR/test-results-$(date +%Y%m%d-%H%M%S).json"
cat > "$TEST_RESULT_FILE" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "trigger": "$TRIGGER_TYPE",
  "changed_files": "$CHANGED_FILES",
  "tests_passed": $TESTS_PASSED,
  "tests_failed": $TESTS_FAILED,
  "execution_time": $EXECUTION_TIME,
  "environment_issues": $ENV_ISSUES
}
EOF

# Update session statistics
echo "test-run|$TESTS_PASSED|$TESTS_FAILED|$(date +%s)" >> "$SESSION_DIR/test-history.log"

# Recommendations based on results
if [ $TESTS_FAILED -gt 0 ]; then
    log "🔧 Recommendations:"
    log "  • Review test failures in: $LOG_FILE"
    log "  • Fix failing tests before committing"
    if [ $ENV_ISSUES -gt 0 ]; then
        log "  • Address environment issues"
    fi
    
    # Don't block Claude, just warn
    exit 0
else
    log "🎉 All tests passed!"
    
    # Save successful test timestamp
    echo "$(date +%s)" > "$CACHE_DIR/last-successful-tests"
    
    if [ "$TRIGGER_TYPE" = "pre_commit" ]; then
        log "✅ Ready for commit"
    fi
    
    exit 0
fi