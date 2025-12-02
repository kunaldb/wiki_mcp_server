# Wiki MCP Server

A Model Context Protocol (MCP) server for Confluence wiki integration, deployed on Databricks Apps.

## Features

- 🔍 **Search Confluence** - Search for wiki pages by query text
- 📄 **Get Page Content** - Retrieve full content from Confluence pages
- 📚 **List Spaces** - Browse available Confluence spaces

## Prerequisites

- Databricks workspace with Apps enabled
- Confluence account with API access
- Databricks CLI configured
- Python 3.11+

## Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd wiki_mcp_server
```

### 2. Configure Confluence Credentials

Copy the template file:

```bash
cp app.yaml.template app.yaml
```

Update `app.yaml` with your actual credentials:

- **CONFLUENCE_URL**: Your Confluence instance URL (e.g., `https://your-company.atlassian.net`)
- **CONFLUENCE_EMAIL**: Your Confluence/Jira email address
- **CONFLUENCE_API_TOKEN**: Generate at https://id.atlassian.com/manage-profile/security/api-tokens

### 3. Configure Deployment Settings (Optional)

The deployment script uses sensible defaults but can be customized with environment variables:

#### Default Behavior
By default, the script will:
- Auto-detect your Databricks username
- Sync files to: `/Workspace/Users/<your-username>/mcp_servers/wiki_mcp_server`
- Deploy with app name: `mcp-wiki-server`

#### Customize App Name
```bash
export APP_NAME="my-custom-wiki-mcp-server"
```

#### Customize Workspace Path
To change where files are synced in your Databricks workspace:

```bash
# Option 1: Set the full workspace path
export WORKSPACE_PATH="/Workspace/Users/your.email@company.com/custom_folder/wiki_mcp"

# Option 2: Set just the base path (will append username and default subfolder)
export WORKSPACE_BASE_PATH="/Workspace/Shared/mcp_servers"
```

**Examples:**

```bash
# Sync to a specific personal folder
export WORKSPACE_PATH="/Workspace/Users/kunal.gaurav@databricks.com/Generative_AI/mcp/Wiki_mcp_server"
./deployment.sh

# Sync to a shared team folder
export WORKSPACE_PATH="/Workspace/Shared/team_projects/wiki_mcp"
./deployment.sh

# Use a custom app name
export APP_NAME="prod-wiki-mcp-server"
./deployment.sh
```

#### Use a Configuration File (Recommended)
Create a persistent configuration file:

```bash
# Copy the example config
cp deployment-config.example.sh deployment-config.sh

# Edit with your settings
nano deployment-config.sh

# Source and deploy
source deployment-config.sh && ./deployment.sh
```

#### Edit deployment.sh Directly
You can also edit `deployment.sh` and change the default values at the top:

```bash
# Edit these lines in deployment.sh
APP_NAME="${APP_NAME:-mcp-wiki-server}"
WORKSPACE_BASE_PATH="${WORKSPACE_BASE_PATH:-/Workspace/Users}"
```

### 4. Deploy to Databricks Apps

Make the script executable and run it:

```bash
chmod +x deployment.sh
./deployment.sh
```

The script will:
1. Auto-detect your Databricks username
2. Show you the configuration (app name, workspace path)
3. Ask for confirmation
4. Sync your code to the Databricks workspace
5. Create the Databricks App (if it doesn't exist)
6. Deploy with your Confluence credentials

### 5. Test the Deployment

Update `test.py` with your deployed app URL (you'll get this after deployment):

```python
mcp_server_url = "https://your-app-name-xxxxx.aws.databricksapps.com/mcp"
```

Install test dependencies and run:

```bash
uv pip install databricks-mcp databricks-sdk
uv run test.py
```

## Available MCP Tools

### 1. `search_confluence`

Search for Confluence pages by query text.

**Parameters:**
- `query` (required): Search query text
- `space_key` (optional): Limit search to a specific space
- `limit` (optional): Maximum results (default: 10)

**Example:**
```python
result = mcp_client.call_tool(
    "search_confluence",
    {"query": "API documentation", "limit": 5}
)
```

### 2. `get_wiki_content`

Get full content from a Confluence page.

**Parameters:**
- `page_id` (required): Confluence page ID or URL
- `format` (optional): "storage" (HTML) or "view" (rendered). Default: "storage"

**Example:**
```python
result = mcp_client.call_tool(
    "get_wiki_content",
    {"page_id": "123456789", "format": "storage"}
)
```

### 3. `list_confluence_spaces`

List all available Confluence spaces.

**Parameters:**
- `limit` (optional): Maximum spaces to return (default: 25)

**Example:**
```python
result = mcp_client.call_tool(
    "list_confluence_spaces",
    {"limit": 10}
)
```

## Deployment Quick Reference

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Name of your Databricks App | `mcp-wiki-server` |
| `WORKSPACE_PATH` | Full path in Databricks workspace | `/Workspace/Users/<username>/mcp_servers/wiki_mcp_server` |
| `WORKSPACE_BASE_PATH` | Base workspace path (auto-appends user/folder) | `/Workspace/Users` |

### Common Deployment Commands

```bash
# Standard deployment (uses defaults)
./deployment.sh

# Deploy with custom app name
APP_NAME="my-wiki-mcp" ./deployment.sh

# Deploy to specific workspace path
WORKSPACE_PATH="/Workspace/Users/you@company.com/my_apps/wiki_mcp" ./deployment.sh

# Deploy to shared folder
WORKSPACE_PATH="/Workspace/Shared/team_mcps/wiki_server" ./deployment.sh

# Check app status
databricks apps get mcp-wiki-server

# View app logs
databricks apps logs mcp-wiki-server

# Redeploy after changes
./deployment.sh

# Delete the app
databricks apps delete mcp-wiki-server
```

### Workspace Path Examples

**Personal workspace:**
```bash
/Workspace/Users/kunal.gaurav@databricks.com/mcp_servers/wiki_mcp_server
/Workspace/Users/kunal.gaurav@databricks.com/Generative_AI/mcp/Wiki_mcp_server
/Workspace/Users/kunal.gaurav@databricks.com/projects/confluence_mcp
```

**Shared workspace:**
```bash
/Workspace/Shared/mcp_servers/wiki
/Workspace/Shared/team_apps/confluence_integration
/Workspace/Shared/ai_tools/wiki_mcp
```

## Development

### Local Testing

Install dependencies:

```bash
uv pip install -r requirements.txt
```

Test Confluence connection locally:

```bash
python confluence_cred.py
```

### Project Structure

```
wiki_mcp_server/
├── app.py                 # Main MCP server implementation
├── main.py                # Entry point
├── app.yaml              # Databricks App config (not in Git)
├── app.yaml.template     # Template for app.yaml
├── requirements.txt      # Python dependencies
├── deployment.sh         # Deployment script
├── test.py              # Test client
└── README.md            # This file
```

## Security Notes

⚠️ **Important**: Never commit `app.yaml` or files with actual credentials to Git!

The following files are excluded from Git (see `.gitignore`):
- `app.yaml` - Contains your actual credentials
- `confluence_cred.py` - Local test script with credentials
- `.env` - Environment variables

Only template files (`app.yaml.template`, `.env.template`) should be committed.

## Troubleshooting

### 403 Forbidden Errors

If you get 403 errors when the app tries to access Confluence:

1. **Verify credentials** - Make sure your API token is valid
2. **Check IP allowlisting** - Your Confluence instance may restrict access by IP
3. **Test from Databricks notebook** - Verify Databricks can reach Confluence
4. **Contact IT** - You may need to allowlist Databricks Apps IP ranges

### App Won't Start

Check deployment logs:

```bash
databricks apps logs <app-name>
```

Common issues:
- Missing or invalid environment variables
- Dependencies not installed correctly
- Port conflicts

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here]

