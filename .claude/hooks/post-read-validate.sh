#!/bin/bash
# Post-read hook to validate documentation consistency
# Checks for outdated references and issues

FILE_PATH="$1"

# Only process documentation files
if [[ "$FILE_PATH" == *"/docs/"* ]] || [[ "$FILE_PATH" == *.md ]]; then
    echo "📖 Analyzing documentation: $(basename "$FILE_PATH")"
    
    # Check for outdated API references
    if grep -q "/api/v1/me" "$FILE_PATH" 2>/dev/null; then
        echo "⚠️  Outdated API reference found: /api/v1/me endpoint no longer exists"
    fi
    
    # Check for deprecated features
    if grep -q "WebSocket" "$FILE_PATH" 2>/dev/null; then
        echo "📌 Note: WebSocket support mentioned but not implemented"
    fi
    
    # Check for missing features marked as complete
    if grep -q "sentiment analysis.*✅\|✅.*sentiment analysis" "$FILE_PATH" 2>/dev/null; then
        echo "⚠️  Warning: Sentiment analysis marked as complete but only partially implemented"
    fi
    
    # Check date stamps
    if grep -qE "Last Updated:.*2024|Generated:.*2024" "$FILE_PATH" 2>/dev/null; then
        echo "📅 Document may be outdated (contains 2024 dates)"
    fi
fi

exit 0