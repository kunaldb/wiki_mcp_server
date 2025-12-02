#!/bin/bash
# Databricks Deployment Configuration Example
# Copy this file to deployment-config.sh and customize your settings
# Then source it before deploying: source deployment-config.sh && ./deployment.sh

# ===== App Configuration =====
export APP_NAME="mcp-wiki-server"

# ===== Workspace Path Configuration =====
# Option 1: Set the full workspace path explicitly
export WORKSPACE_PATH="/Workspace/Users/your.email@company.com/mcp_servers/wiki_mcp_server"

# Option 2: Set just the base path (script will append username and subfolder)
# export WORKSPACE_BASE_PATH="/Workspace/Users"
# export WORKSPACE_BASE_PATH="/Workspace/Shared"

# ===== Usage Examples =====

# Example 1: Personal workspace with custom structure
# export WORKSPACE_PATH="/Workspace/Users/kunal.gaurav@databricks.com/Generative_AI/mcp/Wiki_mcp_server"

# Example 2: Shared team folder
# export WORKSPACE_PATH="/Workspace/Shared/team_projects/wiki_mcp"

# Example 3: Development environment
# export APP_NAME="wiki-mcp-dev"
# export WORKSPACE_PATH="/Workspace/Users/you@company.com/dev/wiki_mcp"

# Example 4: Production environment
# export APP_NAME="wiki-mcp-prod"
# export WORKSPACE_PATH="/Workspace/Shared/production/wiki_mcp"

echo "✓ Deployment configuration loaded:"
echo "  APP_NAME: $APP_NAME"
echo "  WORKSPACE_PATH: $WORKSPACE_PATH"

