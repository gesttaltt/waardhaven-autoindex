#!/bin/bash
# Claude-aware deployment hook
# Integrates with Claude Code session for deployment awareness and feedback

DEPLOYMENT_TYPE="$1"  # staging, production, rollback
TARGET_ENVIRONMENT="$2"  # specific environment name
CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID:-$(date +%s)}"
LOG_FILE=".claude/logs/deployment-$(date +%Y%m%d).log"

# Create necessary directories
mkdir -p ".claude/logs" ".claude/cache" ".claude/session"

# Logging function with Claude context
log() {
    echo "$(date '+%H:%M:%S') [DEPLOY-CLAUDE] $1" | tee -a "$LOG_FILE"
}

log "🚀 Claude-aware deployment initiated: $DEPLOYMENT_TYPE to $TARGET_ENVIRONMENT"

# Claude session integration
DEPLOYMENT_ID="deploy-$(date +%Y%m%d-%H%M%S)"
echo "$DEPLOYMENT_ID|$CLAUDE_SESSION_ID|$DEPLOYMENT_TYPE|$TARGET_ENVIRONMENT|$(date +%s)" >> ".claude/session/deployments.log"

# Pre-deployment Claude context analysis
analyze_claude_context() {
    log "🧠 Analyzing Claude session context for deployment readiness"
    
    local context_issues=0
    local context_warnings=()
    local context_recommendations=()
    
    # Check recent Claude activity
    if [ -f ".claude/session/tool-usage.log" ]; then
        RECENT_ACTIVITY=$(tail -20 ".claude/session/tool-usage.log" | wc -l)
        if [ $RECENT_ACTIVITY -lt 5 ]; then
            context_warnings+=("Low recent Claude activity - ensure development is complete")
            context_issues=$((context_issues + 1))
        fi
        
        # Check for recent file modifications
        RECENT_EDITS=$(tail -20 ".claude/session/tool-usage.log" | grep -c "Edit\|Write\|MultiEdit" || echo 0)
        if [ $RECENT_EDITS -gt 10 ]; then
            context_warnings+=("Many recent file changes ($RECENT_EDITS) - ensure stability")
            context_issues=$((context_issues + 1))
        fi
    fi
    
    # Check for pending suggestions or issues
    if [ -f ".claude/cache/pending-suggestions.md" ]; then
        PENDING_SUGGESTIONS=$(wc -l < ".claude/cache/pending-suggestions.md")
        if [ $PENDING_SUGGESTIONS -gt 0 ]; then
            context_warnings+=("$PENDING_SUGGESTIONS pending suggestions - review before deploy")
        fi
    fi
    
    # Check recent test results
    if [ -f ".claude/cache/last-successful-tests" ]; then
        LAST_TEST_TIME=$(cat ".claude/cache/last-successful-tests")
        CURRENT_TIME=$(date +%s)
        TIME_SINCE_TESTS=$((CURRENT_TIME - LAST_TEST_TIME))
        
        if [ $TIME_SINCE_TESTS -gt 3600 ]; then  # 1 hour
            context_warnings+=("Tests last run $(($TIME_SINCE_TESTS / 3600)) hours ago - consider running tests")
            context_issues=$((context_issues + 1))
        fi
    else
        context_warnings+=("No recent test execution found")
        context_issues=$((context_issues + 1))
    fi
    
    # Check for quality metrics
    if [ -f ".claude/cache/latest-quality-metrics.json" ]; then
        QUALITY_SCORE=$(jq -r '.metrics.quality_score // 0' ".claude/cache/latest-quality-metrics.json" 2>/dev/null || echo 0)
        if [ $QUALITY_SCORE -lt 75 ]; then
            context_warnings+=("Code quality score is $QUALITY_SCORE - consider improvements")
            context_issues=$((context_issues + 1))
        fi
    fi
    
    # Output context analysis
    if [ $context_issues -eq 0 ]; then
        log "✅ Claude context analysis: Ready for deployment"
        context_recommendations+=("Claude session indicates readiness for deployment")
    else
        log "⚠️  Claude context analysis: $context_issues potential issues"
        
        for warning in "${context_warnings[@]}"; do
            log "  • $warning"
        done
        
        context_recommendations+=("Review Claude session context before proceeding")
        context_recommendations+=("Consider running: ai-check for comprehensive validation")
    fi
    
    # Save context analysis
    {
        echo "# Deployment Context Analysis - $DEPLOYMENT_ID"
        echo "Date: $(date)"
        echo "Deployment Type: $DEPLOYMENT_TYPE"
        echo "Target Environment: $TARGET_ENVIRONMENT"
        echo ""
        echo "## Issues: $context_issues"
        for warning in "${context_warnings[@]}"; do
            echo "- $warning"
        done
        echo ""
        echo "## Recommendations"
        for rec in "${context_recommendations[@]}"; do
            echo "- $rec"
        done
        echo ""
    } > ".claude/cache/deployment-context-$DEPLOYMENT_ID.md"
    
    return $context_issues
}

# Integration with existing deployment checks
run_enhanced_pre_deployment_checks() {
    log "🔍 Running enhanced pre-deployment checks with Claude integration"
    
    # Run standard pre-deployment checks
    if [ -f "hooks/deployment/pre-deploy-checks.sh" ]; then
        log "📋 Executing standard pre-deployment checks"
        if ! bash hooks/deployment/pre-deploy-checks.sh; then
            log "❌ Standard pre-deployment checks failed"
            return 1
        fi
    else
        log "⚠️  Standard pre-deployment checks not found"
    fi
    
    # Claude-specific checks
    analyze_claude_context
    local claude_issues=$?
    
    # Check for Claude-generated documentation
    if [ -d "docs" ]; then
        AUTO_DOCS=$(find docs -name "*.md" -exec grep -l "Auto-generated" {} \; 2>/dev/null | wc -l)
        if [ $AUTO_DOCS -gt 0 ]; then
            log "📝 Found $AUTO_DOCS auto-generated documentation files"
            log "💡 Consider updating documentation: python .claude/hooks/documentation/auto-doc-generator.py all"
        fi
    fi
    
    # Check for recent AI Investment specific changes
    if [ -f "CLAUDE.md" ]; then
        log "💰 AI Investment project detected - running domain-specific checks"
        
        # Check financial calculation safety
        if find apps/api -name "*calculation*" -newer ".claude/cache/last-deploy-check" 2>/dev/null | grep -q .; then
            log "🧮 Financial calculation files modified since last deployment"
            log "🔬 Running calculation validation"
            
            if command -v python >/dev/null 2>&1; then
                if python .claude/hooks/intelligence/ai-investment-analyzer.py analyze 2>/dev/null; then
                    log "✅ Financial domain analysis passed"
                else
                    log "⚠️  Financial domain analysis had warnings - review logs"
                fi
            fi
        fi
        
        # Check API rate limit status before deployment
        if [ -f "hooks/api/check-rate-limits.sh" ]; then
            bash hooks/api/check-rate-limits.sh
        fi
    fi
    
    # Interactive deployment confirmation if issues found
    if [ $claude_issues -gt 0 ]; then
        log "❓ Claude context analysis found issues. Continue with deployment?"
        log "📄 Review: .claude/cache/deployment-context-$DEPLOYMENT_ID.md"
        
        # In non-interactive mode, we'll proceed with warnings
        log "⚠️  Proceeding with deployment despite context warnings"
    fi
    
    return 0
}

# Enhanced deployment execution with Claude monitoring
execute_deployment() {
    log "🚀 Executing deployment: $DEPLOYMENT_TYPE"
    
    local deployment_start=$(date +%s)
    
    # Save pre-deployment state
    git rev-parse HEAD > ".claude/cache/pre-deploy-commit-$DEPLOYMENT_ID"
    
    # Record deployment in Claude session
    echo "deployment-started|$DEPLOYMENT_ID|$(date +%s)" >> ".claude/session/activity.log"
    
    case "$DEPLOYMENT_TYPE" in
        "staging")
            log "🧪 Deploying to staging environment"
            execute_staging_deployment
            ;;
        "production")
            log "🌟 Deploying to production environment"
            execute_production_deployment
            ;;
        "rollback")
            log "⏪ Executing rollback deployment"
            execute_rollback_deployment
            ;;
        *)
            log "❌ Unknown deployment type: $DEPLOYMENT_TYPE"
            return 1
            ;;
    esac
    
    local deployment_result=$?
    local deployment_end=$(date +%s)
    local deployment_duration=$((deployment_end - deployment_start))
    
    # Record deployment completion
    echo "deployment-completed|$DEPLOYMENT_ID|$deployment_result|$deployment_duration|$(date +%s)" >> ".claude/session/activity.log"
    
    return $deployment_result
}

execute_staging_deployment() {
    log "📤 Pushing to staging branch"
    
    # Push to staging
    if git push origin staging; then
        log "✅ Code pushed to staging"
        
        # Wait for deployment and verify
        sleep 30
        
        if [ -f "hooks/deployment/post-deploy-verify.sh" ]; then
            bash hooks/deployment/post-deploy-verify.sh staging
        else
            log "⚠️  Post-deployment verification script not found"
        fi
    else
        log "❌ Failed to push to staging"
        return 1
    fi
}

execute_production_deployment() {
    log "🌟 Deploying to production"
    
    # Create release tag
    RELEASE_TAG="v$(date +%Y%m%d-%H%M%S)"
    git tag -a "$RELEASE_TAG" -m "Production release $RELEASE_TAG"
    
    # Push to production
    if git push origin main --tags; then
        log "✅ Code pushed to production with tag $RELEASE_TAG"
        
        # Wait for deployment
        sleep 60
        
        if [ -f "hooks/deployment/post-deploy-verify.sh" ]; then
            bash hooks/deployment/post-deploy-verify.sh production
        else
            log "⚠️  Post-deployment verification script not found"
        fi
        
        # Update Claude cache with successful production deployment
        echo "$RELEASE_TAG|$(date +%s)" > ".claude/cache/last-production-deploy"
    else
        log "❌ Failed to push to production"
        return 1
    fi
}

execute_rollback_deployment() {
    log "⏪ Executing rollback"
    
    # Get last successful deployment
    if [ -f ".claude/cache/last-production-deploy" ]; then
        LAST_TAG=$(cut -d'|' -f1 ".claude/cache/last-production-deploy")
        log "🔄 Rolling back to $LAST_TAG"
        
        git checkout "$LAST_TAG"
        git push origin main --force
        
        log "✅ Rollback completed to $LAST_TAG"
    else
        log "❌ No previous deployment found for rollback"
        return 1
    fi
}

# Post-deployment Claude integration
post_deployment_claude_integration() {
    local deployment_result=$1
    
    log "🔄 Post-deployment Claude integration"
    
    if [ $deployment_result -eq 0 ]; then
        log "✅ Deployment successful - updating Claude context"
        
        # Update deployment cache
        echo "$(date +%s)" > ".claude/cache/last-deploy-check"
        
        # Generate deployment summary for Claude
        DEPLOYMENT_SUMMARY="{
            \"deployment_id\": \"$DEPLOYMENT_ID\",
            \"type\": \"$DEPLOYMENT_TYPE\",
            \"environment\": \"$TARGET_ENVIRONMENT\",
            \"timestamp\": \"$(date -Iseconds)\",
            \"result\": \"success\",
            \"claude_session\": \"$CLAUDE_SESSION_ID\",
            \"git_commit\": \"$(git rev-parse HEAD)\"
        }"
        
        echo "$DEPLOYMENT_SUMMARY" > ".claude/cache/last-deployment.json"
        
        # Trigger documentation update if this was a significant deployment
        if [ "$DEPLOYMENT_TYPE" = "production" ]; then
            log "📝 Triggering documentation update for production deployment"
            if command -v python >/dev/null 2>&1; then
                python .claude/hooks/documentation/auto-doc-generator.py changelog "Production deployment $DEPLOYMENT_ID"
            fi
        fi
        
        # Clean up old deployment context files
        find ".claude/cache" -name "deployment-context-*.md" -mtime +7 -delete 2>/dev/null
        
        log "🎉 Deployment completed successfully!"
        log "📊 View deployment details: .claude/cache/last-deployment.json"
        
    else
        log "❌ Deployment failed - preserving context for analysis"
        
        # Save failure context
        FAILURE_SUMMARY="{
            \"deployment_id\": \"$DEPLOYMENT_ID\",
            \"type\": \"$DEPLOYMENT_TYPE\",
            \"environment\": \"$TARGET_ENVIRONMENT\",
            \"timestamp\": \"$(date -Iseconds)\",
            \"result\": \"failure\",
            \"claude_session\": \"$CLAUDE_SESSION_ID\",
            \"exit_code\": $deployment_result
        }"
        
        echo "$FAILURE_SUMMARY" > ".claude/cache/failed-deployment.json"
        
        log "🔍 Failure analysis available: .claude/cache/failed-deployment.json"
        log "📋 Review context: .claude/cache/deployment-context-$DEPLOYMENT_ID.md"
        log "🛠️  Consider running diagnostic tools: ai-monitor, ai-check"
    fi
}

# Main execution flow
main() {
    # Validate arguments
    if [ -z "$DEPLOYMENT_TYPE" ]; then
        log "❌ Deployment type required"
        echo "Usage: claude-aware-deploy.sh <staging|production|rollback> [environment]"
        exit 1
    fi
    
    # Set default environment if not specified
    if [ -z "$TARGET_ENVIRONMENT" ]; then
        TARGET_ENVIRONMENT="$DEPLOYMENT_TYPE"
    fi
    
    log "🎯 Claude-aware deployment starting"
    log "  Type: $DEPLOYMENT_TYPE"
    log "  Environment: $TARGET_ENVIRONMENT"
    log "  Session: $CLAUDE_SESSION_ID"
    log "  ID: $DEPLOYMENT_ID"
    
    # Execute deployment flow
    if run_enhanced_pre_deployment_checks; then
        log "✅ Pre-deployment checks passed"
        
        execute_deployment
        local result=$?
        
        post_deployment_claude_integration $result
        
        if [ $result -eq 0 ]; then
            log "🚀 Claude-aware deployment completed successfully"
            exit 0
        else
            log "❌ Claude-aware deployment failed"
            exit $result
        fi
    else
        log "❌ Pre-deployment checks failed"
        log "🛑 Deployment aborted"
        exit 1
    fi
}

# Execute main function
main "$@"