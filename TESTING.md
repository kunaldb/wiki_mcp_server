# Testing Guide

Quick reference for testing your Wiki MCP Server.

## Prerequisites

```bash
# Install test dependencies (one-time)
uv pip install databricks-mcp databricks-sdk
```

## Simple Usage

### Auto-detect App Name

Just run the test script - it auto-detects everything!

```bash
python test.py
```

**What it does:**
1. ✅ Reads app name from `deployment.sh`
2. ✅ Queries Databricks CLI for the app URL
3. ✅ Tests all MCP tools automatically

### Test Specific App

```bash
python test.py --app-name my-custom-app
```

## Complete Workflow

```bash
# 1. Deploy your app
./deployment.sh

# 2. Test it immediately
python test.py

# 3. Make changes and redeploy
# ... edit your code ...
./deployment.sh

# 4. Test again
python test.py
```

## One-Liner Deploy + Test

```bash
./deployment.sh && python test.py
```

## Sample Output

```
📱 Auto-detected app name from deployment.sh: mcp-wiki-server
🔍 Getting URL for app 'mcp-wiki-server' from Databricks...
✓ Found app URL: https://mcp-wiki-server-1444828305810485.aws.databricksapps.com/mcp

============================================================
Testing Wiki MCP Server
============================================================
App Name: mcp-wiki-server
MCP URL:  https://mcp-wiki-server-1444828305810485.aws.databricksapps.com/mcp
============================================================

1. Listing available tools...
Available tools (3):
  - search_confluence: Search for Confluence wiki pages by query text...
  - get_wiki_content: Get the full content of a Confluence wiki page...
  - list_confluence_spaces: List all available Confluence spaces

2. Testing list_confluence_spaces tool...
Spaces Result: [...]

3. Testing search_confluence tool...
Search Result: [...]

4. Testing get_wiki_content tool...
   (Skipping - requires a valid page ID from your Confluence)

============================================================
✅ All tests completed successfully!
============================================================
```

## Troubleshooting

### Error: Could not detect app name

**Solution:**
```bash
# Option 1: Specify app name
python test.py --app-name your-app-name

# Option 2: Set environment variable
export APP_NAME=your-app-name
python test.py
```

### Error: Could not find app

**Make sure:**
1. App is deployed: `./deployment.sh`
2. You're authenticated: `databricks auth login`
3. App name is correct: `databricks apps list`

### Error: Connection refused / 403 Forbidden

**Check:**
1. App is running: `databricks apps get mcp-wiki-server`
2. View logs: `databricks apps logs mcp-wiki-server`
3. Confluence credentials are correct in `app.yaml`

## Manual Testing

If you prefer to test manually:

```bash
# Get the app URL
APP_URL=$(databricks apps get mcp-wiki-server --output json | jq -r '.url')
echo "MCP Endpoint: ${APP_URL}/mcp"

# Test with curl
curl -X POST "${APP_URL}/mcp/list_tools"
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Override auto-detected app name | From `deployment.sh` |
| `DATABRICKS_PROFILE` | Databricks CLI profile | `DEFAULT` |

## Advanced Usage

### Test Multiple Environments

```bash
# Test dev environment
python test.py --app-name wiki-mcp-dev

# Test prod environment
python test.py --app-name wiki-mcp-prod
```

### With Custom Profile

```bash
export DATABRICKS_PROFILE=PROD
python test.py
```

