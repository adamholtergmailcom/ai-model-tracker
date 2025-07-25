#!/bin/bash
# AI Model Tracker - Daily Update and Deploy Script
# This script runs the update_models.py script and pushes changes to GitHub

echo "Starting AI Model Tracker daily update..."

# Navigate to project directory
cd "$(dirname "$0")"

# Activate virtual environment
source server/venv/bin/activate

# Run the update script
echo "Fetching latest model data..."
python server/update_models.py

# Check if there are any changes
if git diff --quiet data/models.json; then
    echo "No new model data found. Exiting."
    exit 0
fi

# Add and commit changes
echo "New model data found. Committing and pushing..."
git add data/models.json
git commit -m "Daily model data update - $(date +%Y-%m-%d)"

# Push to GitHub
git push origin main

echo "Update complete! Dashboard will be updated at https://adamholtergmailcom.github.io/ai-model-tracker/"