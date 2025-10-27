#!/bin/bash

# RiotBot Auto-Deploy Script for Cron
# This script pulls the latest changes from git and restarts the docker container
# if there are any updates

REPO_DIR="/home/pi/RiotBot"
LOG_FILE="$REPO_DIR/deploy-cron.log"

# Function to log messages with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "=== Starting auto-deploy check ==="

# Change to repository directory
cd "$REPO_DIR" || {
    log_message "ERROR: Could not change to directory $REPO_DIR"
    exit 1
}

# Fetch latest changes
log_message "Fetching latest changes..."
git fetch origin main 2>&1 | tee -a "$LOG_FILE"

# Check if there are any updates
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
    log_message "Already up to date. No deployment needed."
    exit 0
fi

log_message "Updates found. Pulling changes..."
git pull origin main 2>&1 | tee -a "$LOG_FILE"

if [ $? -ne 0 ]; then
    log_message "ERROR: Git pull failed"
    exit 1
fi

log_message "Stopping containers..."
docker-compose down 2>&1 | tee -a "$LOG_FILE"

log_message "Building containers..."
docker-compose build --no-cache 2>&1 | tee -a "$LOG_FILE"

if [ $? -ne 0 ]; then
    log_message "ERROR: Docker build failed"
    exit 1
fi

log_message "Starting containers..."
docker-compose up -d 2>&1 | tee -a "$LOG_FILE"

if [ $? -ne 0 ]; then
    log_message "ERROR: Docker compose up failed"
    exit 1
fi

# Wait a moment for container to start
sleep 5

# Verify container is running
if docker ps | grep -q riotbot; then
    log_message "SUCCESS: Deployment completed. Container is running."
    log_message "Recent logs:"
    docker logs riotbot --tail 10 2>&1 | tee -a "$LOG_FILE"
else
    log_message "ERROR: Container is not running after deployment"
    exit 1
fi

log_message "=== Auto-deploy completed ==="