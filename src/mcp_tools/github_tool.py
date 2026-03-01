"""
This file uses the Python MCP SDK to define a tool to interact with GitHub/Git.
"""
from mcp.server.fastmcp import FastMCP

mcp_github_server = FastMCP("OpsCommander-GitHub")

@mcp_github_server.tool()
def create_pull_request(repo_name: str, branch_name: str, title: str, description: str, diff_content: str) -> str:
    """
    Creates a new branch, applies the diff, and opens a Pull Request.
    
    Args:
        repo_name: target repository e.g., 'user/repo'
        branch_name: new branch to create
        title: PR title
        description: PR description
        diff_content: the requested code changes
    """
    print(f"[MCP Tool] Opening PR on {repo_name}...")
    print(f"[TCP Tool] Branch: {branch_name}, Title: {title}")
    
    # Mocking PR creation logic
    return f"Success! Pull request '{title}' created at https://github.com/{repo_name}/pull/104"
