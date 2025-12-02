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

### 3. Deploy to Databricks Apps

Run the deployment script:

```bash
chmod +x deployment.sh
./deployment.sh
```

The script will:
- Sync your code to Databricks workspace
- Create the Databricks App
- Deploy with your Confluence credentials

### 4. Test the Deployment

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

