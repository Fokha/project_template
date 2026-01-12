#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# UPDATE SKILLS - Sync skill templates from source project to project_template
# ═══════════════════════════════════════════════════════════════════════════════
#
# Usage:
#   ./update_skills.sh --list                    # List all skills and status
#   ./update_skills.sh --all                     # Update all skills from default source
#   ./update_skills.sh --category flutter        # Update only Flutter skills
#   ./update_skills.sh --source /path/to/project # Use custom source project
#   ./update_skills.sh --dry-run --all           # Preview changes without applying
#   ./update_skills.sh --backup                  # Create backup of current skills
#   ./update_skills.sh --restore                 # Restore from latest backup
#
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_TEMPLATE_DIR="$(dirname "$SCRIPT_DIR")"
SKILLS_DIR="$PROJECT_TEMPLATE_DIR/skills"
BACKUP_DIR="$PROJECT_TEMPLATE_DIR/.skills_backup"

# Default source (ai_studio project)
DEFAULT_SOURCE="$(dirname "$PROJECT_TEMPLATE_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# ═══════════════════════════════════════════════════════════════════════════════
# FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  ${BOLD}SKILL TEMPLATE UPDATER${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_usage() {
    echo -e "${CYAN}Usage:${NC}"
    echo "  $0 [OPTIONS]"
    echo ""
    echo -e "${CYAN}Options:${NC}"
    echo "  --list                  List all skills and their status"
    echo "  --all                   Update all skills from source"
    echo "  --category <name>       Update only specified category"
    echo "                          Categories: flutter, python_api, machine_learning,"
    echo "                                      agentic, devops, integration, n8n, mql5"
    echo "  --source <path>         Use custom source project directory"
    echo "  --dry-run               Preview changes without applying"
    echo "  --backup                Create backup of current skills"
    echo "  --restore               Restore from latest backup"
    echo "  --extract <file>        Extract template from specific file"
    echo "  --sync-readme           Update README with current template counts"
    echo "  --help                  Show this help message"
    echo ""
    echo -e "${CYAN}Examples:${NC}"
    echo "  $0 --list"
    echo "  $0 --all --dry-run"
    echo "  $0 --category flutter"
    echo "  $0 --source ~/projects/other_project --category python_api"
    echo "  $0 --extract lib/providers/settings_provider.dart"
    echo ""
}

count_templates() {
    local category=$1
    local count=0

    if [ -d "$SKILLS_DIR/$category" ]; then
        count=$(find "$SKILLS_DIR/$category" -type f \( -name "*.dart" -o -name "*.py" -o -name "*.mq5" -o -name "*.json" -o -name "*.sh" \) 2>/dev/null | wc -l | tr -d ' ')
    fi

    echo "$count"
}

count_source_files() {
    local category=$1
    local count=0

    case "$category" in
        flutter)
            count=$(find "$SOURCE_DIR/lib" -name "*.dart" 2>/dev/null | wc -l | tr -d ' ')
            ;;
        python_api)
            count=$(find "$SOURCE_DIR/python_ml" -name "*.py" -not -path "*/venv/*" -not -path "*/__pycache__/*" 2>/dev/null | wc -l | tr -d ' ')
            ;;
        machine_learning)
            count=$(find "$SOURCE_DIR/python_ml/models" "$SOURCE_DIR/python_ml/services" -name "*.py" 2>/dev/null | wc -l | tr -d ' ')
            ;;
        agentic)
            count=$(find "$SOURCE_DIR/python_ml/services" -name "*pattern*" -o -name "*agent*" 2>/dev/null | wc -l | tr -d ' ')
            ;;
        devops)
            count=$(find "$SOURCE_DIR/python_ml/cloud" "$SOURCE_DIR/python_ml/scripts" -name "*.sh" 2>/dev/null | wc -l | tr -d ' ')
            ;;
        integration)
            count=$(find "$SOURCE_DIR/python_ml/bridge" "$SOURCE_DIR/python_ml/services" -name "*bridge*" -o -name "*telegram*" -o -name "*websocket*" 2>/dev/null | wc -l | tr -d ' ')
            ;;
        n8n)
            count=$(find "$SOURCE_DIR/python_ml/config/n8n_workflows" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
            ;;
        mql5)
            count=$(find "$SOURCE_DIR" -path "*MQL5*" -name "*.mq5" -o -name "*.mqh" 2>/dev/null | wc -l | tr -d ' ')
            ;;
    esac

    echo "$count"
}

list_skills() {
    echo -e "${CYAN}Skills Directory:${NC} $SKILLS_DIR"
    echo -e "${CYAN}Source Project:${NC}  $SOURCE_DIR"
    echo ""

    echo -e "${BOLD}Category            Templates   Source Files   Status${NC}"
    echo "─────────────────────────────────────────────────────────"

    local categories="flutter python_api machine_learning agentic devops integration n8n mql5"
    local total_templates=0

    for cat in $categories; do
        local template_count=$(count_templates "$cat")
        local source_count=$(count_source_files "$cat")
        local status="${GREEN}✓${NC}"

        total_templates=$((total_templates + template_count))

        if [ "$template_count" -eq 0 ]; then
            status="${RED}✗ No templates${NC}"
        elif [ "$source_count" -eq 0 ]; then
            status="${YELLOW}⚠ No sources${NC}"
        fi

        printf "%-20s %-12s %-15s %b\n" "$cat" "$template_count" "$source_count" "$status"
    done

    echo ""
    echo -e "${CYAN}Total templates:${NC} $total_templates"
}

create_backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_path="$BACKUP_DIR/skills_$timestamp"

    echo -e "${CYAN}Creating backup...${NC}"

    mkdir -p "$backup_path"
    cp -r "$SKILLS_DIR"/* "$backup_path/" 2>/dev/null || true

    echo -e "${GREEN}✓ Backup created:${NC} $backup_path"

    # Keep only last 5 backups
    local backup_count=$(ls -d "$BACKUP_DIR"/skills_* 2>/dev/null | wc -l | tr -d ' ')
    if [ "$backup_count" -gt 5 ]; then
        echo -e "${YELLOW}Cleaning old backups...${NC}"
        ls -dt "$BACKUP_DIR"/skills_* | tail -n +6 | xargs rm -rf
    fi
}

restore_backup() {
    local latest=$(ls -dt "$BACKUP_DIR"/skills_* 2>/dev/null | head -1)

    if [ -z "$latest" ]; then
        echo -e "${RED}✗ No backup found${NC}"
        exit 1
    fi

    echo -e "${CYAN}Restoring from:${NC} $latest"

    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY-RUN] Would restore from $latest${NC}"
        return
    fi

    rm -rf "$SKILLS_DIR"/*
    cp -r "$latest"/* "$SKILLS_DIR/"

    echo -e "${GREEN}✓ Restored from backup${NC}"
}

extract_template_header() {
    local file_type=$1
    local template_name=$2

    case "$file_type" in
        dart)
            cat << EOF
// ═══════════════════════════════════════════════════════════════
// ${template_name^^} TEMPLATE
// Auto-extracted from source project
// ═══════════════════════════════════════════════════════════════
//
// Usage:
// 1. Copy this file to your project
// 2. Replace placeholder names with your feature name
// 3. Customize as needed
//
// Last updated: $(date +%Y-%m-%d)
// ═══════════════════════════════════════════════════════════════

EOF
            ;;
        py)
            cat << EOF
"""
═══════════════════════════════════════════════════════════════
${template_name^^} TEMPLATE
Auto-extracted from source project
═══════════════════════════════════════════════════════════════

Usage:
1. Copy this file to your project
2. Replace placeholder names with your feature name
3. Customize as needed

Last updated: $(date +%Y-%m-%d)
═══════════════════════════════════════════════════════════════
"""

EOF
            ;;
        sh)
            cat << EOF
#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# ${template_name^^} TEMPLATE
# Auto-extracted from source project
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy this file to your project
# 2. Replace placeholder names with your feature name
# 3. Customize as needed
#
# Last updated: $(date +%Y-%m-%d)
# ═══════════════════════════════════════════════════════════════

EOF
            ;;
    esac
}

extract_from_file() {
    local source_file="$1"
    local output_dir="$2"
    local template_name="$3"

    # Handle both absolute and relative paths
    local full_source="$source_file"
    if [ ! -f "$full_source" ]; then
        full_source="$SOURCE_DIR/$source_file"
    fi

    if [ ! -f "$full_source" ]; then
        echo -e "${RED}✗ Source file not found:${NC} $source_file"
        return 1
    fi

    local ext="${source_file##*.}"
    local output_file="$output_dir/${template_name}_template.$ext"

    echo -e "${CYAN}Extracting:${NC} $full_source"
    echo -e "${CYAN}       To:${NC} $output_file"

    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY-RUN] Would create $output_file${NC}"
        return
    fi

    mkdir -p "$output_dir"

    # Create template with header + original content
    extract_template_header "$ext" "$template_name" > "$output_file"
    cat "$full_source" >> "$output_file"

    echo -e "${GREEN}✓ Created:${NC} $output_file"
}

find_best_source() {
    local category=$1
    local skill_type=$2
    local result=""

    case "$category/$skill_type" in
        # ═══════════════════════════════════════════════════════════════
        # FLUTTER PATTERNS
        # ═══════════════════════════════════════════════════════════════
        flutter/provider)
            # Look for providers with common patterns
            result=$(find "$SOURCE_DIR/lib/providers" -name "*_provider.dart" -not -name "*test*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR/lib" -name "*provider*.dart" -not -path "*/test/*" 2>/dev/null | head -1)
            ;;
        flutter/service)
            # Prefer services with clear business logic
            result=$(find "$SOURCE_DIR/lib/services" -name "*_service.dart" -not -name "*test*" -not -name "*api*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR/lib/services" -name "*.dart" -not -name "*test*" 2>/dev/null | head -1)
            ;;
        flutter/model)
            # Look for data models
            result=$(find "$SOURCE_DIR/lib/models" -name "*_model.dart" -not -name "*test*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR/lib/models" -name "*.dart" -not -name "*test*" 2>/dev/null | head -1)
            ;;
        flutter/api_client)
            # Look for API client patterns
            result=$(find "$SOURCE_DIR/lib/services" -name "*api*service*.dart" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR/lib/services" -name "*_api_*.dart" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR/lib/services" -name "*client*.dart" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR/lib" -name "*http*service*.dart" 2>/dev/null | head -1)
            ;;
        flutter/websocket)
            # Look for WebSocket/realtime patterns
            result=$(find "$SOURCE_DIR/lib/services" -name "*websocket*.dart" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR/lib/services" -name "*realtime*.dart" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR/lib/services" -name "*streaming*.dart" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR/lib/services" -name "*socket*.dart" 2>/dev/null | head -1)
            ;;
        flutter/widget)
            # Look for reusable widget patterns
            result=$(find "$SOURCE_DIR/lib/widgets" -name "*_widget.dart" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR/lib/widgets" -name "*card*.dart" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR/lib/widgets" -name "*panel*.dart" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR/lib/widgets" -name "*.dart" -not -name "*test*" 2>/dev/null | head -1)
            ;;
        flutter/theme)
            # Look for theme/styling patterns
            result=$(find "$SOURCE_DIR/lib/constants" -name "*theme*.dart" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR/lib/constants" -name "*color*.dart" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR/lib" -name "*app_theme*.dart" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR/lib/constants" -name "*.dart" 2>/dev/null | head -1)
            ;;
        flutter/plugin)
            # Look for plugin patterns
            result=$(find "$SOURCE_DIR/lib/plugins" -name "*_plugin.dart" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR/lib/plugins" -name "*.dart" -not -name "*test*" 2>/dev/null | head -1)
            ;;

        # ═══════════════════════════════════════════════════════════════
        # PYTHON API PATTERNS
        # ═══════════════════════════════════════════════════════════════
        python_api/blueprint)
            # Look for Flask blueprints
            result=$(find "$SOURCE_DIR" -path "*/blueprints/*.py" -not -name "__init__*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*_bp.py" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*blueprint*.py" 2>/dev/null | head -1)
            ;;
        python_api/endpoint)
            # Look for main API files
            result=$(find "$SOURCE_DIR" -name "api_server.py" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "app.py" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*routes*.py" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "main.py" 2>/dev/null | head -1)
            ;;
        python_api/service)
            # Look for service layer
            result=$(find "$SOURCE_DIR" -path "*/services/*_service.py" -not -name "__init__*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -path "*/services/*.py" -not -name "__init__*" 2>/dev/null | head -1)
            ;;
        python_api/database)
            # Look for database patterns
            result=$(find "$SOURCE_DIR" -path "*/database/*.py" -not -name "__init__*" -not -name "*migration*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*_db.py" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*database*.py" -not -name "*test*" 2>/dev/null | head -1)
            ;;
        python_api/cache)
            # Look for caching patterns
            result=$(find "$SOURCE_DIR" -name "*cache*.py" -not -name "__init__*" -not -name "*test*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -path "*/services/*cache*.py" 2>/dev/null | head -1)
            ;;
        python_api/validation)
            # Look for validation patterns
            result=$(find "$SOURCE_DIR" -path "*/validation/*.py" -not -name "__init__*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*validator*.py" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*validation*.py" 2>/dev/null | head -1)
            ;;
        python_api/health)
            # Look for health check patterns
            result=$(find "$SOURCE_DIR" -name "*health*.py" -not -name "__init__*" -not -name "*test*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -path "*/utils/*health*.py" 2>/dev/null | head -1)
            ;;
        python_api/logging)
            # Look for logging patterns
            result=$(find "$SOURCE_DIR" -name "*logging*.py" -not -name "__init__*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*logger*.py" 2>/dev/null | head -1)
            ;;
        python_api/error_handler)
            # Look for error handling patterns
            result=$(find "$SOURCE_DIR" -name "*error*.py" -not -name "__init__*" -not -name "*test*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*exception*.py" 2>/dev/null | head -1)
            ;;
        python_api/background_task)
            # Look for background task patterns
            result=$(find "$SOURCE_DIR" -name "*task*.py" -not -name "__init__*" -not -name "*test*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*worker*.py" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*scheduler*.py" 2>/dev/null | head -1)
            ;;
        python_api/dedup)
            # Look for deduplication patterns
            result=$(find "$SOURCE_DIR" -name "*dedup*.py" -not -name "__init__*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*deduplicate*.py" 2>/dev/null | head -1)
            ;;

        # ═══════════════════════════════════════════════════════════════
        # MACHINE LEARNING PATTERNS
        # ═══════════════════════════════════════════════════════════════
        machine_learning/training)
            # Look for training scripts
            result=$(find "$SOURCE_DIR" -path "*/scripts/train*.py" -not -name "__init__*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*train*.py" -not -name "__init__*" -not -name "*test*" 2>/dev/null | head -1)
            ;;
        machine_learning/model)
            # Look for model definitions
            result=$(find "$SOURCE_DIR" -path "*/models/*.py" -not -name "__init__*" -not -name "*test*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*_model.py" 2>/dev/null | head -1)
            ;;
        machine_learning/feature)
            # Look for feature engineering
            result=$(find "$SOURCE_DIR" -name "*feature*.py" -not -name "__init__*" -not -name "*test*" 2>/dev/null | head -1)
            ;;
        machine_learning/ensemble)
            # Look for ensemble methods
            result=$(find "$SOURCE_DIR" -name "*ensemble*.py" -not -name "__init__*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*signal_classification*.py" 2>/dev/null | head -1)
            ;;
        machine_learning/walkforward)
            # Look for walk-forward validation
            result=$(find "$SOURCE_DIR" -name "*walkforward*.py" -not -name "__init__*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*validation*.py" -path "*/scripts/*" 2>/dev/null | head -1)
            ;;
        machine_learning/hyperparameter)
            # Look for hyperparameter tuning
            result=$(find "$SOURCE_DIR" -name "*hyperparameter*.py" -not -name "__init__*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*optim*.py" -path "*/scripts/*" 2>/dev/null | head -1)
            ;;
        machine_learning/sentiment)
            # Look for sentiment analysis
            result=$(find "$SOURCE_DIR" -name "*sentiment*.py" -not -name "__init__*" -not -name "*test*" 2>/dev/null | head -1)
            ;;
        machine_learning/anomaly)
            # Look for anomaly detection
            result=$(find "$SOURCE_DIR" -name "*anomaly*.py" -not -name "__init__*" 2>/dev/null | head -1)
            ;;
        machine_learning/retrain)
            # Look for retraining scripts
            result=$(find "$SOURCE_DIR" -name "*retrain*.py" -not -name "__init__*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*scheduled*train*.py" 2>/dev/null | head -1)
            ;;
        machine_learning/model_serving)
            # Look for model serving
            result=$(find "$SOURCE_DIR" -name "*serving*.py" -not -name "__init__*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*predict*.py" -path "*/services/*" 2>/dev/null | head -1)
            ;;
        machine_learning/calibration)
            # Look for confidence calibration
            result=$(find "$SOURCE_DIR" -name "*calibrat*.py" -not -name "__init__*" 2>/dev/null | head -1)
            ;;
        machine_learning/persistence)
            # Look for model persistence
            result=$(find "$SOURCE_DIR" -name "*persist*.py" -not -name "__init__*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*save*model*.py" 2>/dev/null | head -1)
            ;;

        # ═══════════════════════════════════════════════════════════════
        # AGENTIC AI PATTERNS
        # ═══════════════════════════════════════════════════════════════
        agentic/orchestrator)
            result="$SOURCE_DIR/python_ml/services/pattern_executor.py"
            [ ! -f "$result" ] && result=$(find "$SOURCE_DIR" -name "*orchestrat*.py" -not -name "__init__*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*coordinator*.py" 2>/dev/null | head -1)
            ;;
        agentic/routing)
            # Look for routing/router patterns
            result=$(find "$SOURCE_DIR" -name "*routing*.py" -not -name "__init__*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*router*.py" 2>/dev/null | head -1)
            ;;
        agentic/memory)
            # Look for memory management
            result=$(find "$SOURCE_DIR" -name "*memory*.py" -not -name "__init__*" -not -name "*test*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*context*.py" -not -name "*test*" 2>/dev/null | head -1)
            ;;
        agentic/reflection)
            # Look for reflection patterns
            result=$(find "$SOURCE_DIR" -name "*reflect*.py" -not -name "__init__*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*critique*.py" 2>/dev/null | head -1)
            ;;
        agentic/consensus)
            # Look for consensus/voting patterns
            result=$(find "$SOURCE_DIR" -name "*consensus*.py" -not -name "__init__*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*voting*.py" 2>/dev/null | head -1)
            ;;
        agentic/tool_use)
            # Look for tool use patterns
            result=$(find "$SOURCE_DIR" -name "*tool*.py" -not -name "__init__*" -not -name "*test*" 2>/dev/null | head -1)
            ;;
        agentic/planning)
            # Look for planning patterns
            result=$(find "$SOURCE_DIR" -name "*plan*.py" -not -name "__init__*" -not -name "*test*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*react*.py" 2>/dev/null | head -1)
            ;;
        agentic/guardrails)
            # Look for guardrails
            result=$(find "$SOURCE_DIR" -name "*guardrail*.py" -not -name "__init__*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*safety*.py" 2>/dev/null | head -1)
            ;;
        agentic/fallback)
            # Look for fallback patterns
            result=$(find "$SOURCE_DIR" -name "*fallback*.py" -not -name "__init__*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*failover*.py" 2>/dev/null | head -1)
            ;;
        agentic/feedback_loop)
            # Look for feedback loop patterns
            result=$(find "$SOURCE_DIR" -name "*feedback*.py" -not -name "__init__*" -not -name "*test*" 2>/dev/null | head -1)
            ;;

        # ═══════════════════════════════════════════════════════════════
        # DEVOPS PATTERNS
        # ═══════════════════════════════════════════════════════════════
        devops/docker)
            # Look for Docker files
            result=$(find "$SOURCE_DIR" -name "Dockerfile" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "docker-compose*.yml" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "docker-compose*.yaml" 2>/dev/null | head -1)
            ;;
        devops/backup)
            # Look for backup scripts
            result=$(find "$SOURCE_DIR" -name "*backup*.sh" -not -name "*test*" 2>/dev/null | head -1)
            ;;
        devops/deploy)
            # Look for deployment scripts
            result=$(find "$SOURCE_DIR" -name "*deploy*.sh" -not -name "*test*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "deploy*.py" 2>/dev/null | head -1)
            ;;
        devops/monitoring)
            # Look for monitoring scripts
            result=$(find "$SOURCE_DIR" -name "*monitor*.py" -not -name "__init__*" -not -name "*test*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*watchdog*.py" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*health*check*.py" 2>/dev/null | head -1)
            ;;
        devops/ci_cd)
            # Look for CI/CD configs
            result=$(find "$SOURCE_DIR" -name "*.yml" -path "*/.github/*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name ".gitlab-ci.yml" 2>/dev/null | head -1)
            ;;
        devops/secrets)
            # Look for secrets management
            result=$(find "$SOURCE_DIR" -name "*credential*.py" -not -name "__init__*" -not -name "*test*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*secret*.py" -not -name "*test*" 2>/dev/null | head -1)
            ;;
        devops/logging_infra)
            # Look for logging infrastructure
            result=$(find "$SOURCE_DIR" -name "*log*.py" -path "*/utils/*" -not -name "__init__*" 2>/dev/null | head -1)
            ;;

        # ═══════════════════════════════════════════════════════════════
        # INTEGRATION PATTERNS
        # ═══════════════════════════════════════════════════════════════
        integration/websocket)
            # Look for WebSocket server
            result=$(find "$SOURCE_DIR" -name "websocket*.py" -not -name "__init__*" -not -name "*test*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -path "*/bridge/websocket*.py" 2>/dev/null | head -1)
            ;;
        integration/mt5_bridge)
            # Look for MT5 bridge
            result=$(find "$SOURCE_DIR" -name "*mt5*.py" -path "*/bridge/*" -not -name "__init__*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*mt5*bridge*.py" 2>/dev/null | head -1)
            ;;
        integration/telegram)
            # Look for Telegram integration
            result=$(find "$SOURCE_DIR" -name "*telegram*.py" -not -name "__init__*" -not -name "*test*" 2>/dev/null | head -1)
            ;;
        integration/webhook)
            # Look for webhook handlers
            result=$(find "$SOURCE_DIR" -name "*webhook*.py" -not -name "__init__*" -not -name "*test*" 2>/dev/null | head -1)
            ;;
        integration/api_client)
            # Look for external API clients
            result=$(find "$SOURCE_DIR" -name "*api*client*.py" -not -name "__init__*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*external*api*.py" 2>/dev/null | head -1)
            ;;
        integration/notification)
            # Look for notification services
            result=$(find "$SOURCE_DIR" -name "*notification*.py" -not -name "__init__*" -not -name "*test*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*notify*.py" 2>/dev/null | head -1)
            ;;
        integration/data_sync)
            # Look for data sync patterns
            result=$(find "$SOURCE_DIR" -name "*sync*.py" -not -name "__init__*" -not -name "*test*" 2>/dev/null | head -1)
            ;;

        # ═══════════════════════════════════════════════════════════════
        # N8N WORKFLOW PATTERNS
        # ═══════════════════════════════════════════════════════════════
        n8n/workflow)
            # Look for N8N workflow files
            result=$(find "$SOURCE_DIR" -path "*n8n*" -name "*.json" -not -name "package*.json" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*workflow*.json" 2>/dev/null | head -1)
            ;;
        n8n/webhook)
            # Look for webhook workflow
            result=$(find "$SOURCE_DIR" -path "*n8n*" -name "*webhook*.json" 2>/dev/null | head -1)
            ;;
        n8n/notification)
            # Look for notification workflow
            result=$(find "$SOURCE_DIR" -path "*n8n*" -name "*notification*.json" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -path "*n8n*" -name "*telegram*.json" 2>/dev/null | head -1)
            ;;
        n8n/data_pipeline)
            # Look for data pipeline workflow
            result=$(find "$SOURCE_DIR" -path "*n8n*" -name "*pipeline*.json" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -path "*n8n*" -name "*data*.json" 2>/dev/null | head -1)
            ;;
        n8n/error_handler)
            # Look for error handler workflow
            result=$(find "$SOURCE_DIR" -path "*n8n*" -name "*error*.json" 2>/dev/null | head -1)
            ;;
        n8n/scheduled)
            # Look for scheduled/cron workflow
            result=$(find "$SOURCE_DIR" -path "*n8n*" -name "*cron*.json" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -path "*n8n*" -name "*schedule*.json" 2>/dev/null | head -1)
            ;;

        # ═══════════════════════════════════════════════════════════════
        # MQL5 PATTERNS
        # ═══════════════════════════════════════════════════════════════
        mql5/ea)
            # Look for Expert Advisor
            result=$(find "$SOURCE_DIR" -name "*.mq5" -path "*Expert*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*.mq5" 2>/dev/null | head -1)
            ;;
        mql5/include)
            # Look for include files
            result=$(find "$SOURCE_DIR" -name "*.mqh" -path "*Include*" 2>/dev/null | head -1)
            [ -z "$result" ] && result=$(find "$SOURCE_DIR" -name "*.mqh" 2>/dev/null | head -1)
            ;;
    esac

    echo "$result"
}

update_category() {
    local category="$1"
    local updated=0
    local skipped=0

    echo -e "${MAGENTA}Updating category:${NC} $category"
    echo ""

    # Define skill types per category
    local skill_types=""
    case "$category" in
        flutter)
            skill_types="provider service model api_client websocket widget theme plugin"
            ;;
        python_api)
            skill_types="blueprint endpoint service database cache validation health"
            ;;
        machine_learning)
            skill_types="training model feature ensemble walkforward"
            ;;
        agentic)
            skill_types="orchestrator routing memory reflection consensus"
            ;;
        devops)
            skill_types="docker backup deploy monitoring"
            ;;
        integration)
            skill_types="websocket mt5_bridge telegram webhook"
            ;;
        n8n)
            skill_types="workflow webhook notification"
            ;;
        *)
            echo -e "${YELLOW}Unknown category: $category${NC}"
            return
            ;;
    esac

    for skill in $skill_types; do
        local source_file=$(find_best_source "$category" "$skill")

        if [ -z "$source_file" ] || [ ! -f "$source_file" ]; then
            echo -e "  ${YELLOW}⚠ No source for:${NC} $skill"
            skipped=$((skipped + 1))
            continue
        fi

        extract_from_file "$source_file" "$SKILLS_DIR/$category" "$skill"
        updated=$((updated + 1))
    done

    echo ""
    echo -e "${GREEN}✓ Updated:${NC} $updated templates"
    [ $skipped -gt 0 ] && echo -e "${YELLOW}⚠ Skipped:${NC} $skipped (no sources)"
}

update_all() {
    local categories="flutter python_api machine_learning agentic devops integration n8n"

    for cat in $categories; do
        update_category "$cat"
        echo ""
    done
}

sync_readme() {
    echo -e "${CYAN}Updating README with current counts...${NC}"

    local total=$(find "$SKILLS_DIR" -type f \( -name "*.dart" -o -name "*.py" -o -name "*.mq5" -o -name "*.json" -o -name "*.sh" \) 2>/dev/null | wc -l | tr -d ' ')

    echo -e "${GREEN}✓ Total templates:${NC} $total"
    echo ""
    echo "Update the README.md manually with these counts:"
    echo ""

    local categories="flutter python_api machine_learning agentic devops integration n8n mql5"
    for cat in $categories; do
        local count=$(count_templates "$cat")
        echo "  $cat: $count templates"
    done
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

# Default values
SOURCE_DIR="$DEFAULT_SOURCE"
DRY_RUN=false
ACTION=""
CATEGORY=""
EXTRACT_FILE=""

# Parse arguments
while [ $# -gt 0 ]; do
    case $1 in
        --list)
            ACTION="list"
            shift
            ;;
        --all)
            ACTION="all"
            shift
            ;;
        --category)
            ACTION="category"
            CATEGORY="$2"
            shift 2
            ;;
        --source)
            SOURCE_DIR="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --backup)
            ACTION="backup"
            shift
            ;;
        --restore)
            ACTION="restore"
            shift
            ;;
        --extract)
            ACTION="extract"
            EXTRACT_FILE="$2"
            shift 2
            ;;
        --sync-readme)
            ACTION="sync-readme"
            shift
            ;;
        --help|-h)
            print_header
            print_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option:${NC} $1"
            print_usage
            exit 1
            ;;
    esac
done

# Validate source directory
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}✗ Source directory not found:${NC} $SOURCE_DIR"
    exit 1
fi

print_header

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}>>> DRY-RUN MODE - No changes will be made <<<${NC}"
    echo ""
fi

case "$ACTION" in
    list)
        list_skills
        ;;
    backup)
        create_backup
        ;;
    restore)
        restore_backup
        ;;
    extract)
        if [ -z "$EXTRACT_FILE" ]; then
            echo -e "${RED}✗ No file specified for extraction${NC}"
            exit 1
        fi

        # Determine category from file path
        output_cat="misc"
        if echo "$EXTRACT_FILE" | grep -q "lib/"; then
            output_cat="flutter"
        elif echo "$EXTRACT_FILE" | grep -q "python"; then
            output_cat="python_api"
        fi

        extract_from_file "$EXTRACT_FILE" "$SKILLS_DIR/$output_cat" "$(basename "${EXTRACT_FILE%.*}")"
        ;;
    category)
        if [ -z "$CATEGORY" ]; then
            echo -e "${RED}✗ No category specified${NC}"
            exit 1
        fi

        # Backup before update
        if [ "$DRY_RUN" = false ]; then
            create_backup
        fi

        update_category "$CATEGORY"
        ;;
    all)
        # Backup before update
        if [ "$DRY_RUN" = false ]; then
            create_backup
        fi

        update_all
        ;;
    sync-readme)
        sync_readme
        ;;
    *)
        echo -e "${YELLOW}No action specified. Use --help for usage.${NC}"
        echo ""
        list_skills
        ;;
esac

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Done!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
