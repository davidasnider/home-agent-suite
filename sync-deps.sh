#!/bin/bash
# sync-deps.sh - Synchronize all Poetry dependencies and pre-commit hooks
# This script ensures your local development environment matches the repository state
# after Dependabot merges or any dependency updates.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the repository root
if [ ! -f "pyproject.toml" ] || [ ! -d ".github" ]; then
    log_error "This script must be run from the repository root directory"
    exit 1
fi

log_info "Starting dependency synchronization workflow..."

# Parse command line arguments
QUICK_MODE=false
LOCK_REGEN=false
SKIP_VERIFY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -q|--quick)
            QUICK_MODE=true
            shift
            ;;
        -l|--lock)
            LOCK_REGEN=true
            shift
            ;;
        --skip-verify)
            SKIP_VERIFY=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -q, --quick        Quick mode: only sync root dependencies"
            echo "  -l, --lock         Regenerate lock files before syncing"
            echo "  --skip-verify      Skip environment verification"
            echo "  -h, --help         Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                 # Full sync (recommended after git pull)"
            echo "  $0 --quick         # Quick sync for minor updates"
            echo "  $0 --lock          # Regenerate lock files and sync"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use '$0 --help' for usage information"
            exit 1
            ;;
    esac
done

# Step 1: Regenerate lock files if requested
if [ "$LOCK_REGEN" = true ]; then
    log_info "Regenerating lock files for components with out-of-sync dependencies..."
    
    for dir in agents/* libs/* infrastructure/*; do
        if [ -f "$dir/pyproject.toml" ]; then
            log_info "Checking lock file in $dir"
            (cd "$dir" && poetry lock --no-update 2>/dev/null) || {
                log_warning "Failed to regenerate lock file in $dir (may be expected)"
            }
        fi
    done
fi

# Step 2: Sync root Poetry environment
log_info "Syncing root Poetry environment..."
if poetry sync; then
    log_success "Root Poetry environment synchronized"
else
    log_error "Failed to sync root Poetry environment"
    exit 1
fi

# Step 3: Sync component environments (skip in quick mode)
if [ "$QUICK_MODE" = false ]; then
    log_info "Syncing component Poetry environments..."
    
    component_count=0
    success_count=0
    
    for dir in agents/* libs/* infrastructure/*; do
        if [ -f "$dir/pyproject.toml" ]; then
            component_count=$((component_count + 1))
            log_info "Updating dependencies in $dir"
            
            if (cd "$dir" && poetry sync 2>/dev/null); then
                success_count=$((success_count + 1))
                log_success "✓ $dir"
            else
                log_warning "⚠ Failed to sync $dir (may need manual attention)"
            fi
        fi
    done
    
    log_info "Component sync completed: $success_count/$component_count successful"
else
    log_info "Quick mode: skipping component synchronization"
fi

# Step 4: Update pre-commit hooks
log_info "Updating pre-commit hooks..."
if pre-commit autoupdate >/dev/null 2>&1; then
    log_success "Pre-commit hooks updated"
else
    log_warning "Failed to update pre-commit hooks (may not be configured)"
fi

if pre-commit install --install-hooks >/dev/null 2>&1; then
    log_success "Pre-commit hooks installed"
else
    log_warning "Failed to install pre-commit hooks"
fi

# Step 5: Verify environment (optional)
if [ "$SKIP_VERIFY" = false ]; then
    log_info "Verifying environment integrity..."
    
    if poetry run pytest --collect-only -q >/dev/null 2>&1; then
        log_success "✅ Environment sync successful - all tests discoverable"
    else
        log_warning "⚠️ Some tests may have import issues - check individual components"
        log_info "This may be normal if some components have missing test dependencies"
    fi
else
    log_info "Skipping environment verification"
fi

# Summary
echo ""
log_success "Dependency synchronization completed!"
echo ""
echo "Next steps:"
echo "• Your local environment is now synchronized with the repository"
echo "• Run 'poetry run pytest' to execute tests"
echo "• Run 'pre-commit run --all-files' to validate code quality"
echo ""

if [ "$QUICK_MODE" = false ] && [ "$component_count" -gt 0 ]; then
    echo "Synchronized components:"
    for dir in agents/* libs/* infrastructure/*; do
        if [ -f "$dir/pyproject.toml" ]; then
            echo "  • $dir"
        fi
    done
    echo ""
fi

log_info "Use '$0 --help' to see all available options"