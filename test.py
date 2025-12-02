"""
Test script for the Wiki MCP Server deployed on Databricks Apps

This script demonstrates how to connect to and test your deployed MCP server.
"""

from databricks_mcp import DatabricksMCPClient
from databricks.sdk import WorkspaceClient

# Replace with your deployed app URL
# Example: https://custom-mcp-server-6051921418418893.staging.aws.databricksapps.com/mcp
mcp_server_url = "https://mcp-wiki-test-kunal-1444828305810485.aws.databricksapps.com/mcp/"

# Set your Databricks CLI profile (usually "DEFAULT")
databricks_cli_profile = "DEFAULT"

# Initialize the Databricks workspace client
workspace_client = WorkspaceClient(profile=databricks_cli_profile)

# Create the MCP client
mcp_client = DatabricksMCPClient(
    server_url=mcp_server_url, 
    workspace_client=workspace_client
)

print("=" * 60)
print("Testing Wiki MCP Server")
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
    


