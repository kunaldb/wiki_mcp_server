"""
Main entry point for the Wiki MCP Server
"""
import uvicorn
from app import starlette_app

def main():
    print("Starting Wiki MCP Server...")
    # Get port from environment or use default
    import os
    port = int(os.getenv("DATABRICKS_APP_PORT", 8000))
    
    # Run the Starlette app with uvicorn
    uvicorn.run(
        starlette_app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()
