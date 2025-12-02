#!/bin/bash

APP_NAME="mcp-wiki-test-kunal"

WORKSPACE_PATH="/Workspace/Users/kunal.gaurav@databricks.com/Genrative_AI/mcp/Wiki_mcp_server"

# Sync source code to workspace
databricks sync . "$WORKSPACE_PATH"

# Create and deploy the app
databricks apps create "$APP_NAME"

databricks apps deploy "$APP_NAME" --source-code-path "$WORKSPACE_PATH"

