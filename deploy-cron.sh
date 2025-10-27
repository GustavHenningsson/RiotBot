#!/bin/bash

# RiotBot Auto-Deploy Script for Cron
# This script pulls the latest changes from git and restarts the docker container
# if there are any updates

REPO_DIR="/home/dietpi/RiotBot"
LOG_FILE="$REPO_DIR/deploy-cron.log"
CONTAINER_NAME="riotbot"
BRANCH="main"

# ===== Utility Functions =====

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

exit_with_error() {
    log_message "ERROR: $1"
    exit 1
}

run_command() {
    local description="$1"
    local command="$2"

    log_message "$description"
    eval "$command 2>&1 | tee -a '$LOG_FILE'"

    if [ ${PIPESTATUS[0]} -ne 0 ]; then
        exit_with_error "$description failed"
    fi
}

# ===== Git Functions =====

fetch_latest_changes() {
    run_command "Fetching latest changes..." "git fetch origin $BRANCH"
}

check_for_updates() {
    local local_commit=$(git rev-parse HEAD)
    local remote_commit=$(git rev-parse origin/$BRANCH)

    [ "$local_commit" != "$remote_commit" ]
}

pull_changes() {
    run_command "Pulling changes..." "git pull origin $BRANCH"
}

# ===== Container Functions =====

is_container_running() {
    docker ps | grep -q "$CONTAINER_NAME"
}

stop_containers() {
    run_command "Stopping containers..." "docker-compose down"
}

build_containers() {
    run_command "Building containers (no cache)..." "docker-compose build --no-cache"
}

build_containers_with_cache() {
    run_command "Building containers (with cache)..." "docker-compose build"
}

start_containers() {
    run_command "Starting containers..." "docker-compose up -d"
}

verify_container_running() {
    sleep 5

    if is_container_running; then
        log_message "SUCCESS: Container is running."
        log_message "Recent logs:"
        docker logs "$CONTAINER_NAME" --tail 10 2>&1 | tee -a "$LOG_FILE"
    else
        exit_with_error "Container is not running after deployment"
    fi
}

# ===== Deployment Functions =====

deploy_with_rebuild() {
    pull_changes
    stop_containers
    build_containers
    start_containers
    verify_container_running
}

deploy_without_rebuild() {
    build_containers_with_cache
    start_containers
    verify_container_running
}

# ===== Main Script =====

main() {
    log_message "=== Starting auto-deploy check ==="

    cd "$REPO_DIR" || exit_with_error "Could not change to directory $REPO_DIR"

    fetch_latest_changes

    if check_for_updates; then
        log_message "Updates found. Deploying with rebuild..."
        deploy_with_rebuild
    else
        log_message "Already up to date. No new changes to pull."

        if is_container_running; then
            log_message "Container is already running. No action needed."
        else
            log_message "Container is not running. Starting it..."
            deploy_without_rebuild
        fi
    fi

    log_message "=== Auto-deploy completed ==="
}

main