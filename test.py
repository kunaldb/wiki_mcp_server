"""
Test script for the Wiki MCP Server deployed on Databricks Apps

This script auto-detects your deployed app URL and tests the MCP server.

Usage:
  python test.py                           # Auto-detect app name from deployment.sh
  python test.py --app-name my-custom-app  # Use specific app name
"""

import os
import sys
import json
import subprocess
import re
from databricks_mcp import DatabricksMCPClient
from databricks.sdk import WorkspaceClient


def get_app_name_from_deployment_sh():
    """Read APP_NAME from deployment.sh"""
    try:
        with open("deployment.sh", "r") as f:
            content = f.read()
            # Look for APP_NAME="${APP_NAME:-mcp-wiki-server}"
            match = re.search(r'APP_NAME="\$\{APP_NAME:-([^}]+)\}"', content)
            if match:
                return match.group(1)
    except FileNotFoundError:
        pass
    return None


def get_app_url_from_cli(app_name):
    """Get app URL from Databricks CLI"""
    try:
        result = subprocess.run(
            ["databricks", "apps", "get", app_name, "--output", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        app_info = json.loads(result.stdout)
        return app_info.get("url")
    except Exception as e:
        print(f"❌ Error getting app URL: {e}")
        return None


# Get app name
app_name = None
if len(sys.argv) > 1 and sys.argv[1] == "--app-name" and len(sys.argv) > 2:
    app_name = sys.argv[2]
    print(f"📱 Using app name from command line: {app_name}")
elif os.getenv("APP_NAME"):
    app_name = os.getenv("APP_NAME")
    print(f"📱 Using app name from environment: {app_name}")
else:
    app_name = get_app_name_from_deployment_sh()
    if app_name:
        print(f"📱 Auto-detected app name from deployment.sh: {app_name}")

if not app_name:
    print("❌ Could not detect app name!")
    print("\nPlease either:")
    print("  1. Run: python test.py --app-name your-app-name")
    print("  2. Or set: export APP_NAME=your-app-name")
    sys.exit(1)

# Get app URL from Databricks
print(f"🔍 Getting URL for app '{app_name}' from Databricks...")
base_url = get_app_url_from_cli(app_name)

if not base_url:
    print(f"❌ Could not find app '{app_name}'")
    print("\nMake sure:")
    print("  1. The app is deployed: ./deployment.sh")
    print("  2. You're authenticated: databricks auth login")
    print("  3. The app name is correct")
    sys.exit(1)

# Construct MCP endpoint URL
mcp_server_url = f"{base_url.rstrip('/')}/mcp"
print(f"✓ Found app URL: {mcp_server_url}")

# Initialize Databricks workspace client
databricks_cli_profile = os.getenv("DATABRICKS_PROFILE", "DEFAULT")

try:
    workspace_client = WorkspaceClient(profile=databricks_cli_profile)
except Exception as e:
    print(f"❌ Error connecting to Databricks: {e}")
    sys.exit(1)

# Create the MCP client
mcp_client = DatabricksMCPClient(
    server_url=mcp_server_url, 
    workspace_client=workspace_client
)

print("\n" + "=" * 60)
print("Testing Wiki MCP Server")
print("=" * 60)
print(f"App Name: {app_name}")
print(f"MCP URL:  {mcp_server_url}")
print("=" * 60)

try:
    # List available tools
    print("\n1. Listing available tools...")
    tools = mcp_client.list_tools()
    print(f"Available tools ({len(tools)}):")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # Test list_confluence_spaces
    print("\n2. Testing list_confluence_spaces tool...")
    spaces_result = mcp_client.call_tool(
        "list_confluence_spaces",
        {"limit": 10}
    )
    print(f"Spaces Result: {spaces_result}")
    
    # Test search_confluence
    print("\n3. Testing search_confluence tool...")
    search_result = mcp_client.call_tool(
        "search_confluence",
        {
            "query": "API",
            "limit": 5
        }
    )
    print(f"Search Result: {search_result}")
    
    # Test get_wiki_content with a page ID
    # Note: Replace with an actual page ID from your Confluence instance
    print("\n4. Testing get_wiki_content tool...")
    print("   (Skipping - requires a valid page ID from your Confluence)")
    print("   To test this, uncomment below and add a valid page_id:")
    print("   # content_result = mcp_client.call_tool(")
    print("   #     'get_wiki_content',")
    print("   #     {'page_id': 'YOUR_PAGE_ID', 'format': 'storage'}")
    print("   # )")
    
    # Uncomment to test with a real page ID:
    # content_result = mcp_client.call_tool(
    #     "get_wiki_content",
    #     {
    #         "page_id": "123456789",  # Replace with actual page ID
    #         "format": "storage"
    #     }
    # )
    # print(f"Content Result: {content_result}")
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nMake sure:")
    print("  1. Your MCP server is deployed and running")
    print("  2. You've updated the mcp_server_url with your actual app URL")
    print("  3. You have the databricks_mcp package installed")
    print("     Run: pip install databricks-mcp")
    


