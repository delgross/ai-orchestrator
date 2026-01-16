#!/bin/zsh

# Antigravity AI - GitHub Backup Script
# Automatically commits and pushes current changes to GitHub repository

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Find the git repository root
find_git_root() {
    local current="$SCRIPT_DIR"
    while [[ "$current" != "/" ]]; do
        if [[ -d "$current/.git" ]]; then
            echo "$current"
            return 0
        fi
        current="$(dirname "$current")"
    done
    echo "$SCRIPT_DIR"  # Fallback to script directory
}

REPO_DIR="$(find_git_root)"
BACKUP_BRANCH="main"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
COMMIT_MESSAGE="Auto-backup: $TIMESTAMP"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Function to check if we're in a git repository
check_git_repo() {
    if [[ ! -d ".git" ]]; then
        log_error "Not a git repository. Please run this script from the project root."
        exit 1
    fi
}

# Function to check git status
check_git_status() {
    if [[ -n $(git status --porcelain) ]]; then
        log_info "Found uncommitted changes"
        return 0
    else
        log_warning "No changes to commit"
        return 1
    fi
}

# Function to add files
add_files() {
    log_info "Adding files to git..."
    git add .

    # Check if there are files staged
    if [[ -z $(git diff --cached --name-only) ]]; then
        log_warning "No files staged for commit"
        return 1
    fi

    log_success "Files added successfully"
    return 0
}

# Function to commit changes
commit_changes() {
    local message="$1"

    log_info "Committing changes with message: $message"

    if git commit -m "$message"; then
        log_success "Changes committed successfully"
        return 0
    else
        log_error "Failed to commit changes"
        return 1
    fi
}

# Function to push to remote
push_to_remote() {
    local branch="$1"

    # Check if remote exists
    if ! git remote get-url origin &>/dev/null; then
        log_error "No remote repository configured. Please set up a GitHub remote first:"
        log_error "  git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
        exit 1
    fi

    log_info "Pushing to remote branch: $branch"

    if git push origin "$branch"; then
        log_success "Successfully pushed to GitHub"
        return 0
    else
        log_error "Failed to push to GitHub"
        return 1
    fi
}

# Function to show status
show_status() {
    log_info "Current git status:"
    git status --short

    log_info "Recent commits:"
    git log --oneline -5
}

# Function to create backup commit
create_backup_commit() {
    local backup_type="$1"

    case "$backup_type" in
        "full")
            COMMIT_MESSAGE="Full backup: $TIMESTAMP - Complete codebase snapshot"
            ;;
        "incremental")
            COMMIT_MESSAGE="Incremental backup: $TIMESTAMP - Latest changes"
            ;;
        "config")
            COMMIT_MESSAGE="Config backup: $TIMESTAMP - Configuration and settings"
            ;;
        "data")
            COMMIT_MESSAGE="Data backup: $TIMESTAMP - Data and logs"
            ;;
        *)
            COMMIT_MESSAGE="Auto-backup: $TIMESTAMP"
            ;;
    esac

    # Add specific files based on backup type
    case "$backup_type" in
        "config")
            git add config/ *.yaml *.yml *.json 2>/dev/null || true
            ;;
        "data")
            git add data/ logs/ *.log 2>/dev/null || true
            ;;
    esac
}

# Main backup function
perform_backup() {
    local backup_type="$1"
    local skip_push="$2"

    log_info "Starting GitHub backup process..."
    log_info "Backup type: $backup_type"
    log_info "Repository: $REPO_DIR"

    # Change to repository directory
    cd "$REPO_DIR"

    # Check if we're in a git repository
    check_git_repo

    # Check for changes
    if ! check_git_status; then
        log_info "No changes to backup. Exiting."
        return 0
    fi

    # Create appropriate commit message and staging
    create_backup_commit "$backup_type"

    # Add files
    if ! add_files; then
        log_warning "No files to backup. Exiting."
        return 0
    fi

    # Commit changes
    if ! commit_changes "$COMMIT_MESSAGE"; then
        return 1
    fi

    # Push to remote (unless skipped)
    if [[ "$skip_push" != "true" ]]; then
        if ! push_to_remote "$BACKUP_BRANCH"; then
            return 1
        fi
    fi

    # Show final status
    show_status

    log_success "Backup completed successfully!"
    log_info "Commit: $COMMIT_MESSAGE"

    return 0
}

# Function to show usage
show_usage() {
    cat << EOF
Antigravity AI - GitHub Backup Script

Usage: $0 [OPTIONS]

Options:
    -t, --type TYPE     Backup type: full, incremental, config, data (default: incremental)
    -b, --branch BRANCH Git branch to push to (default: main)
    -m, --message MSG   Custom commit message
    -n, --no-push       Commit locally only, don't push to remote
    -s, --status        Show current git status and exit
    -h, --help          Show this help message

Examples:
    $0                          # Incremental backup to main branch
    $0 -t full                  # Full backup
    $0 -t config -m "Updated config"  # Config backup with custom message
    $0 -n                       # Commit locally only
    $0 -s                       # Show status only

EOF
}

# Parse command line arguments
backup_type="incremental"
custom_message=""
skip_push="false"
show_status_only="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            backup_type="$2"
            shift 2
            ;;
        -b|--branch)
            BACKUP_BRANCH="$2"
            shift 2
            ;;
        -m|--message)
            custom_message="$2"
            shift 2
            ;;
        -n|--no-push)
            skip_push="true"
            shift
            ;;
        -s|--status)
            show_status_only="true"
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Override commit message if custom one provided
if [[ -n "$custom_message" ]]; then
    COMMIT_MESSAGE="$custom_message"
fi

# Main execution
if [[ "$show_status_only" == "true" ]]; then
    cd "$REPO_DIR"
    check_git_repo
    show_status
    exit 0
fi

# Validate backup type
case "$backup_type" in
    full|incremental|config|data)
        ;;
    *)
        log_error "Invalid backup type: $backup_type"
        log_error "Valid types: full, incremental, config, data"
        exit 1
        ;;
esac

# Run backup
if perform_backup "$backup_type" "$skip_push"; then
    log_success "Backup operation completed successfully"
    exit 0
else
    log_error "Backup operation failed"
    exit 1
fi