#!/bin/bash
# Health check script for the application
# Can be used in container orchestration or monitoring systems

set -e

HOST="${HOST:-localhost}"
PORT="${PORT:-8000}"
TIMEOUT="${TIMEOUT:-5}"

# Function to check HTTP endpoint
check_endpoint() {
    local url=$1
    local expected_status=${2:-200}
    
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$url" \
        -H "Content-Type: application/json" \
        -d '{}' || echo "000")
    
    if [ "$response" -eq "$expected_status" ]; then
        return 0
    else
        echo "Health check failed: Expected $expected_status but got $response"
        return 1
    fi
}

# Main health check
echo "Performing health check on $HOST:$PORT..."

if check_endpoint "http://$HOST:$PORT/api/compose"; then
    echo "✓ Health check passed"
    exit 0
else
    echo "✗ Health check failed"
    exit 1
fi
