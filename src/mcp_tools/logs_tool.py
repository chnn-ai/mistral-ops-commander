"""
This file uses the Python MCP SDK to define a tool that fetches logs.
"""
from typing import List
from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server for logging tools
mcp_logs_server = FastMCP("OpsCommander-Logs")

@mcp_logs_server.tool()
def fetch_recent_logs(service_name: str, lines: int = 100) -> str:
    """
    Fetches the recent server output logs for a specific service.
    
    Args:
        service_name: Name of the service (e.g. 'auth-service')
        lines: Number of log lines to retrieve
    """
    print(f"[MCP Tool] Fetching {lines} lines for {service_name}...")
    
    # Mocking log output emphasizing a memory leak/crash
    logs = f"""
[INFO] {service_name} starting up...
[INFO] Serving traffic on port 8080
[WARN] Connection pool usage at 80%
[WARN] Connection pool usage at 95%
[ERROR] Memory usage exceeded 2GB limit.
[ERROR] Exception in auth.py: OutOfMemoryError during token parsing.
[FATAL] Worker process crashed.
    """
    return logs.strip()
