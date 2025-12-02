"""
Wiki MCP Server - Python REST implementation for Databricks Apps

This server provides a simplified REST API for Confluence wiki operations.
"""

import logging
import os
import contextlib
from collections.abc import AsyncIterator
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.routing import Mount
import json
import asyncio
from datetime import datetime
from starlette.applications import Starlette
from atlassian import Confluence

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-wiki-server")

app = Server("mcp-wiki-server")

# Initialize Confluence client
def get_confluence_client():
    """Create and return a Confluence client instance."""
    confluence_url = os.getenv("CONFLUENCE_URL")
    confluence_email = os.getenv("CONFLUENCE_EMAIL")
    confluence_token = os.getenv("CONFLUENCE_API_TOKEN")
    
    if not all([confluence_url, confluence_email, confluence_token]):
        raise ValueError("Confluence credentials not configured. Check environment variables.")
    
    return Confluence(
        url=confluence_url,
        username=confluence_email,
        password=confluence_token,
        cloud=True
    )

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """Define the tools your server exposes."""
    return [
        types.Tool(
            name="search_confluence",
            description="Search for Confluence wiki pages by query text. Returns matching pages with titles, URLs, and excerpts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query text"
                    },
                    "space_key": {
                        "type": "string",
                        "description": "Optional: Limit search to a specific Confluence space (e.g., 'TEAM', 'DOCS')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_wiki_content",
            description="Get the full content of a Confluence wiki page by page ID or URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {
                        "type": "string",
                        "description": "Confluence page ID or URL"
                    },
                    "format": {
                        "type": "string",
                        "description": "Content format: 'storage' (HTML) or 'view' (rendered HTML). Default: 'storage'",
                        "enum": ["storage", "view"],
                        "default": "storage"
                    }
                },
                "required": ["page_id"]
            }
        ),
        types.Tool(
            name="list_confluence_spaces",
            description="List all available Confluence spaces",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of spaces to return (default: 25)",
                        "default": 25
                    }
                }
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls for Confluence operations."""
    ctx = app.request_context
    
    if name == "search_confluence":
        return await handle_search_confluence(arguments, ctx)
    elif name == "get_wiki_content":
        return await handle_get_wiki_content(arguments, ctx)
    elif name == "list_confluence_spaces":
        return await handle_list_spaces(arguments, ctx)
    else:
        raise ValueError(f"Unknown tool: {name}")

async def handle_search_confluence(arguments: dict, ctx) -> list[types.TextContent]:
    """Search Confluence for pages matching the query."""
    query = arguments.get("query")
    space_key = arguments.get("space_key")
    limit = arguments.get("limit", 10)
    
    await ctx.session.send_log_message(
        level="info",
        data=f"Searching Confluence for: '{query}' (space: {space_key or 'all'}, limit: {limit})",
        logger="mcp-wiki-server",
        related_request_id=ctx.request_id,
    )
    
    try:
        confluence = get_confluence_client()
        
        # Build CQL query
        cql = f'text ~ "{query}"'
        if space_key:
            cql += f' AND space = "{space_key}"'
        cql += ' AND type = "page"'
        
        # Search using CQL
        results = await asyncio.to_thread(
            confluence.cql,
            cql=cql,
            limit=limit
        )
        
        # Format results
        pages = []
        for result in results.get('results', []):
            page_info = {
                "id": result.get('content', {}).get('id'),
                "title": result.get('content', {}).get('title'),
                "space": result.get('content', {}).get('space', {}).get('key'),
                "url": f"{os.getenv('CONFLUENCE_URL')}/wiki{result.get('content', {}).get('_links', {}).get('webui', '')}",
                "excerpt": result.get('excerpt', '').replace('<em>', '**').replace('</em>', '**')
            }
            pages.append(page_info)
        
        response = {
            "query": query,
            "total_results": len(pages),
            "results": pages
        }
        
        await ctx.session.send_log_message(
            level="info",
            data=f"Found {len(pages)} results",
            logger="mcp-wiki-server",
            related_request_id=ctx.request_id,
        )
        
        return [types.TextContent(type="text", text=json.dumps(response, indent=2))]
        
    except Exception as e:
        await ctx.session.send_log_message(
            level="error",
            data=f"Error searching Confluence: {str(e)}",
            logger="mcp-wiki-server",
            related_request_id=ctx.request_id,
        )
        raise

async def handle_get_wiki_content(arguments: dict, ctx) -> list[types.TextContent]:
    """Get content from a specific Confluence page."""
    page_id = arguments.get("page_id")
    content_format = arguments.get("format", "storage")
    
    await ctx.session.send_log_message(
        level="info",
        data=f"Getting wiki content for page ID: {page_id}",
        logger="mcp-wiki-server",
        related_request_id=ctx.request_id,
    )
    
    try:
        confluence = get_confluence_client()
        
        # Extract page ID from URL if needed
        if "atlassian.net" in page_id or "/" in page_id:
            # Extract page ID from URL
            parts = page_id.split("/")
            page_id = parts[-1] if parts[-1].isdigit() else page_id
        
        # Get page content
        page = await asyncio.to_thread(
            confluence.get_page_by_id,
            page_id=page_id,
            expand=f'body.{content_format},version,space'
        )
        
        response = {
            "id": page.get('id'),
            "title": page.get('title'),
            "space": page.get('space', {}).get('key'),
            "version": page.get('version', {}).get('number'),
            "url": f"{os.getenv('CONFLUENCE_URL')}/wiki{page.get('_links', {}).get('webui', '')}",
            "content": page.get('body', {}).get(content_format, {}).get('value', ''),
            "last_modified": page.get('version', {}).get('when')
        }
        
        await ctx.session.send_log_message(
            level="info",
            data="Wiki content retrieved successfully",
            logger="mcp-wiki-server",
            related_request_id=ctx.request_id,
        )
        
        return [types.TextContent(type="text", text=json.dumps(response, indent=2))]
        
    except Exception as e:
        await ctx.session.send_log_message(
            level="error",
            data=f"Error getting wiki content: {str(e)}",
            logger="mcp-wiki-server",
            related_request_id=ctx.request_id,
        )
        raise

async def handle_list_spaces(arguments: dict, ctx) -> list[types.TextContent]:
    """List all available Confluence spaces."""
    limit = arguments.get("limit", 25)
    
    await ctx.session.send_log_message(
        level="info",
        data=f"Listing Confluence spaces (limit: {limit})",
        logger="mcp-wiki-server",
        related_request_id=ctx.request_id,
    )
    
    try:
        confluence = get_confluence_client()
        
        spaces = await asyncio.to_thread(
            confluence.get_all_spaces,
            start=0,
            limit=limit,
            expand='description.plain'
        )
        
        space_list = []
        for space in spaces.get('results', []):
            space_info = {
                "key": space.get('key'),
                "name": space.get('name'),
                "type": space.get('type'),
                "description": space.get('description', {}).get('plain', {}).get('value', ''),
                "url": f"{os.getenv('CONFLUENCE_URL')}/wiki{space.get('_links', {}).get('webui', '')}"
            }
            space_list.append(space_info)
        
        response = {
            "total_spaces": len(space_list),
            "spaces": space_list
        }
        
        await ctx.session.send_log_message(
            level="info",
            data=f"Found {len(space_list)} spaces",
            logger="mcp-wiki-server",
            related_request_id=ctx.request_id,
        )
        
        return [types.TextContent(type="text", text=json.dumps(response, indent=2))]
        
    except Exception as e:
        await ctx.session.send_log_message(
            level="error",
            data=f"Error listing spaces: {str(e)}",
            logger="mcp-wiki-server",
            related_request_id=ctx.request_id,
        )
        raise

session_manager = StreamableHTTPSessionManager(
    app=app,
    event_store=None,
    stateless=True,
)

async def handle_streamable_http(scope, receive, send):
    await session_manager.handle_request(scope, receive, send)

@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[None]:
    async with session_manager.run():
        logger.info("MCP Wiki Server started!")
        try:
            yield
        finally:
            logger.info("MCP Wiki Server stopped!")

# Create the Starlette app with routes
starlette_app = Starlette(
    debug=False,
    routes=[
        Mount("/mcp", app=handle_streamable_http)
    ],
    lifespan=lifespan,
)
