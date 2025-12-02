#!/bin/bash

# Databricks MCP Server Deployment Script
# This script syncs your code to Databricks workspace and deploys the app

set -e  # Exit on error

# Configuration - You can override these via environment variables or command line
APP_NAME="${APP_NAME:-mcp-wiki-server}"
WORKSPACE_BASE_PATH="${WORKSPACE_BASE_PATH:-/Workspace/Users}"

# Get current Databricks user
DATABRICKS_USER=$(databricks current-user me --output json 2>/dev/null | jq -r '.userName' || echo "")

if [ -z "$DATABRICKS_USER" ]; then
    echo "❌ Error: Could not detect Databricks user. Make sure you're authenticated."
    echo "   Run: databricks auth login"
    exit 1
fi

# Construct full workspace path
# You can customize the subfolder structure here
WORKSPACE_PATH="${WORKSPACE_PATH:-$WORKSPACE_BASE_PATH/$DATABRICKS_USER/mcp_servers/wiki_mcp_server}"

echo "======================================"
echo "📦 Databricks MCP Server Deployment"
echo "======================================"
echo "App Name:        $APP_NAME"
echo "Databricks User: $DATABRICKS_USER"
echo "Workspace Path:  $WORKSPACE_PATH"
echo "======================================"
echo ""

# Confirm before proceeding
read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo "📤 Step 1: Syncing source code to workspace..."
databricks sync . "$WORKSPACE_PATH"

echo ""
echo "🔨 Step 2: Creating app (if it doesn't exist)..."
# Try to create the app, ignore error if it already exists
databricks apps create "$APP_NAME" 2>/dev/null || echo "   App already exists, skipping creation..."

echo ""
echo "🚀 Step 3: Deploying app..."
databricks apps deploy "$APP_NAME" --source-code-path "$WORKSPACE_PATH"

echo ""
echo "======================================"
echo "✅ Deployment completed!"
echo "======================================"
echo ""
echo "To view your app:"
echo "  databricks apps get $APP_NAME"
echo ""
echo "To view logs:"
echo "  databricks apps logs $APP_NAME"

