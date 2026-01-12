#!/bin/bash
# =============================================================================
# Health Check Script Template
# =============================================================================
#
# Comprehensive health check for all system components.
#
# Usage:
#   ./health_check.sh              # Check all services
#   ./health_check.sh --json       # Output as JSON
#   ./health_check.sh --notify     # Send alerts on failure
#   ./health_check.sh api          # Check specific service
#
# Exit codes:
#   0 - All healthy
#   1 - One or more services unhealthy
#   2 - Configuration error
# =============================================================================

set -e

# Configuration
API_URL="${API_URL:-http://localhost:5050}"
DB_PATH="${DB_PATH:-data/app.db}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNINGS=0

# Results array for JSON output
declare -a RESULTS

# Parse arguments
OUTPUT_FORMAT="text"
NOTIFY=false
SPECIFIC_SERVICE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --json)
            OUTPUT_FORMAT="json"
            shift
            ;;
        --notify)
            NOTIFY=true
            shift
            ;;
        *)
            SPECIFIC_SERVICE="$1"
            shift
            ;;
    esac
done

# Helper functions
log_check() {
    local name=$1
    local status=$2
    local message=$3
    local latency=$4

    ((TOTAL_CHECKS++))

    if [[ "$OUTPUT_FORMAT" == "json" ]]; then
        RESULTS+=("{\"name\":\"$name\",\"status\":\"$status\",\"message\":\"$message\",\"latency_ms\":$latency}")
    else
        case $status in
            "healthy")
                echo -e "${GREEN}✓${NC} $name: $message (${latency}ms)"
                ((PASSED_CHECKS++))
                ;;
            "unhealthy")
                echo -e "${RED}✗${NC} $name: $message"
                ((FAILED_CHECKS++))
                ;;
            "warning")
                echo -e "${YELLOW}⚠${NC} $name: $message"
                ((WARNINGS++))
                ((PASSED_CHECKS++))
                ;;
        esac
    fi
}

measure_latency() {
    local start=$(python3 -c "import time; print(int(time.time() * 1000))" 2>/dev/null || echo 0)
    "$@" > /dev/null 2>&1
    local end=$(python3 -c "import time; print(int(time.time() * 1000))" 2>/dev/null || echo 0)
    echo $((end - start))
}

# Health check functions
check_api() {
    local start_time=$(python3 -c "import time; print(int(time.time() * 1000))" 2>/dev/null || date +%s%3N)

    if curl -s -f "${API_URL}/health" > /dev/null 2>&1; then
        local end_time=$(python3 -c "import time; print(int(time.time() * 1000))" 2>/dev/null || date +%s%3N)
        local latency=$((end_time - start_time))

        # Check response time
        if [[ $latency -gt 5000 ]]; then
            log_check "API Server" "warning" "Slow response" "$latency"
        else
            log_check "API Server" "healthy" "Running at ${API_URL}" "$latency"
        fi
    else
        log_check "API Server" "unhealthy" "Not responding at ${API_URL}" "0"
    fi
}

check_database() {
    if [[ -f "$DB_PATH" ]]; then
        local start_time=$(python3 -c "import time; print(int(time.time() * 1000))" 2>/dev/null || echo 0)

        if sqlite3 "$DB_PATH" "SELECT 1;" > /dev/null 2>&1; then
            local end_time=$(python3 -c "import time; print(int(time.time() * 1000))" 2>/dev/null || echo 0)
            local latency=$((end_time - start_time))

            # Check database size
            local size=$(du -h "$DB_PATH" | cut -f1)
            log_check "Database" "healthy" "SQLite OK (${size})" "$latency"
        else
            log_check "Database" "unhealthy" "SQLite query failed" "0"
        fi
    else
        log_check "Database" "warning" "Database file not found" "0"
    fi
}

check_redis() {
    local start_time=$(python3 -c "import time; print(int(time.time() * 1000))" 2>/dev/null || echo 0)

    if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping > /dev/null 2>&1; then
        local end_time=$(python3 -c "import time; print(int(time.time() * 1000))" 2>/dev/null || echo 0)
        local latency=$((end_time - start_time))
        log_check "Redis" "healthy" "Connected to ${REDIS_HOST}:${REDIS_PORT}" "$latency"
    else
        log_check "Redis" "warning" "Not available (optional)" "0"
    fi
}

check_disk() {
    local usage=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
    local available=$(df -h . | awk 'NR==2 {print $4}')

    if [[ $usage -gt 90 ]]; then
        log_check "Disk Space" "unhealthy" "Critical: ${usage}% used (${available} free)" "0"
    elif [[ $usage -gt 80 ]]; then
        log_check "Disk Space" "warning" "High usage: ${usage}% (${available} free)" "0"
    else
        log_check "Disk Space" "healthy" "${usage}% used (${available} free)" "0"
    fi
}

check_memory() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        local mem_info=$(vm_stat | head -10)
        local free_pages=$(echo "$mem_info" | grep "Pages free" | awk '{print $3}' | tr -d '.')
        local total_mem=$(sysctl -n hw.memsize)
        local page_size=$(pagesize)
        local free_mem=$((free_pages * page_size / 1024 / 1024))
        local total_mb=$((total_mem / 1024 / 1024))
        local used_percent=$(( (total_mb - free_mem) * 100 / total_mb ))
    else
        # Linux
        local mem_info=$(free -m | grep Mem)
        local total_mb=$(echo "$mem_info" | awk '{print $2}')
        local used_mb=$(echo "$mem_info" | awk '{print $3}')
        local used_percent=$((used_mb * 100 / total_mb))
    fi

    if [[ $used_percent -gt 90 ]]; then
        log_check "Memory" "unhealthy" "Critical: ${used_percent}% used" "0"
    elif [[ $used_percent -gt 80 ]]; then
        log_check "Memory" "warning" "High usage: ${used_percent}% used" "0"
    else
        log_check "Memory" "healthy" "${used_percent}% used" "0"
    fi
}

check_process() {
    local process_name=$1
    local display_name=${2:-$process_name}

    if pgrep -f "$process_name" > /dev/null 2>&1; then
        local pid=$(pgrep -f "$process_name" | head -1)
        log_check "$display_name" "healthy" "Running (PID: $pid)" "0"
    else
        log_check "$display_name" "unhealthy" "Not running" "0"
    fi
}

check_port() {
    local port=$1
    local service_name=$2

    if lsof -i ":$port" > /dev/null 2>&1; then
        log_check "$service_name" "healthy" "Listening on port $port" "0"
    else
        log_check "$service_name" "unhealthy" "Port $port not in use" "0"
    fi
}

check_docker() {
    if command -v docker &> /dev/null; then
        if docker info > /dev/null 2>&1; then
            local running=$(docker ps -q | wc -l | tr -d ' ')
            log_check "Docker" "healthy" "${running} containers running" "0"
        else
            log_check "Docker" "warning" "Docker daemon not running" "0"
        fi
    else
        log_check "Docker" "warning" "Docker not installed" "0"
    fi
}

check_ssl_cert() {
    local domain=$1

    if [[ -z "$domain" ]]; then
        return
    fi

    local expiry=$(echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)

    if [[ -n "$expiry" ]]; then
        local expiry_epoch=$(date -j -f "%b %d %T %Y %Z" "$expiry" +%s 2>/dev/null || date -d "$expiry" +%s 2>/dev/null)
        local now_epoch=$(date +%s)
        local days_left=$(( (expiry_epoch - now_epoch) / 86400 ))

        if [[ $days_left -lt 7 ]]; then
            log_check "SSL Cert ($domain)" "unhealthy" "Expires in ${days_left} days!" "0"
        elif [[ $days_left -lt 30 ]]; then
            log_check "SSL Cert ($domain)" "warning" "Expires in ${days_left} days" "0"
        else
            log_check "SSL Cert ($domain)" "healthy" "Valid for ${days_left} days" "0"
        fi
    fi
}

# Notification functions
send_telegram() {
    local message=$1

    if [[ -n "$TELEGRAM_BOT_TOKEN" && -n "$TELEGRAM_CHAT_ID" ]]; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d "chat_id=${TELEGRAM_CHAT_ID}" \
            -d "text=${message}" \
            -d "parse_mode=HTML" > /dev/null
    fi
}

send_slack() {
    local message=$1

    if [[ -n "$SLACK_WEBHOOK" ]]; then
        curl -s -X POST "$SLACK_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"text\":\"$message\"}" > /dev/null
    fi
}

# Main execution
main() {
    if [[ "$OUTPUT_FORMAT" == "text" ]]; then
        echo -e "${BLUE}=== Health Check ===${NC}"
        echo "Time: $(date)"
        echo ""
    fi

    # Run checks based on specific service or all
    case "$SPECIFIC_SERVICE" in
        "api")
            check_api
            ;;
        "db"|"database")
            check_database
            ;;
        "redis")
            check_redis
            ;;
        "disk")
            check_disk
            ;;
        "memory")
            check_memory
            ;;
        "docker")
            check_docker
            ;;
        "")
            # Run all checks
            check_api
            check_database
            check_redis
            check_disk
            check_memory
            check_docker
            check_port 5050 "API Port"
            ;;
        *)
            echo "Unknown service: $SPECIFIC_SERVICE"
            exit 2
            ;;
    esac

    # Output results
    if [[ "$OUTPUT_FORMAT" == "json" ]]; then
        local json_results=$(IFS=,; echo "${RESULTS[*]}")
        echo "{\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"total\":$TOTAL_CHECKS,\"passed\":$PASSED_CHECKS,\"failed\":$FAILED_CHECKS,\"warnings\":$WARNINGS,\"checks\":[$json_results]}"
    else
        echo ""
        echo -e "${BLUE}=== Summary ===${NC}"
        echo "Total: $TOTAL_CHECKS | Passed: $PASSED_CHECKS | Failed: $FAILED_CHECKS | Warnings: $WARNINGS"

        if [[ $FAILED_CHECKS -gt 0 ]]; then
            echo -e "${RED}Status: UNHEALTHY${NC}"
        elif [[ $WARNINGS -gt 0 ]]; then
            echo -e "${YELLOW}Status: DEGRADED${NC}"
        else
            echo -e "${GREEN}Status: HEALTHY${NC}"
        fi
    fi

    # Send notifications if enabled and there are failures
    if [[ "$NOTIFY" == true && $FAILED_CHECKS -gt 0 ]]; then
        local alert_msg="🚨 Health Check Alert\n\nFailed: $FAILED_CHECKS\nWarnings: $WARNINGS\nTime: $(date)"
        send_telegram "$alert_msg"
        send_slack "$alert_msg"
    fi

    # Exit with appropriate code
    if [[ $FAILED_CHECKS -gt 0 ]]; then
        exit 1
    fi

    exit 0
}

main
