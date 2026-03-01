def fetch_logs(service_name: str) -> str:
    """Wrapper for the MCP logs tool"""
    from src.mcp_tools.logs_tool import fetch_recent_logs
    return fetch_recent_logs(service_name=service_name)

def trigger_patch(file_path: str, context: str) -> str:
    """Wrapper to trigger the Coder agent and save the result."""
    from src.agent.coder import generate_patch
    patched_code = generate_patch(file_path=file_path, incident_context=context)
    if patched_code.startswith("Error:"):
        return patched_code
        
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(patched_code)
        return f"Successfully generated patch and overwrote {file_path}. You may now create a pull request."
    except Exception as e:
        return f"Patch generated, but failed to write to file: {str(e)}"

def report_status(message: str) -> str:
    """Mock for Voxtral Realtime"""
    print(f"\n[Voxtral Audio Output]: '{message}'")
    return "Status reported to voice channel."

def list_files(directory: str) -> str:
    """Lists files in a directory to help the agent find code."""
    import os
    try:
        files = os.listdir(directory)
        return f"Files in {directory}: {', '.join(files)}"
    except FileNotFoundError:
        return f"Error: Directory {directory} not found."
    except Exception as e:
        return f"Error listing files: {str(e)}"

def clone_repo(repo_url: str) -> str:
    """Clones a GitHub repository to a local temp folder."""
    import os
    import git
    import uuid
    from urllib.parse import urlparse
    
    # Simple extraction of repo name
    parsed = urlparse(repo_url)
    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) >= 2:
        repo_name = path_parts[1]
    else:
        repo_name = "cloned_repo"
        
    unique_id = uuid.uuid4().hex[:6]
    target_dir = os.path.join(os.getcwd(), "tmp_repos", f"{repo_name}_{unique_id}")
    
    try:
        print(f"[Git] Cloning {repo_url} into {target_dir}...")
        git.Repo.clone_from(repo_url, target_dir)
        return f"Successfully cloned repository to '{target_dir}'. You can now use list_files, read_file, and write_file here."
    except Exception as e:
        return f"Failed to clone repository: {str(e)}"

def read_file(file_path: str) -> str:
    """Reads the content of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"

def write_file(file_path: str, content: str) -> str:
    """Writes content to a file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing to file {file_path}: {str(e)}"

def create_pull_request(repo_path: str, branch_name: str, commit_message: str, pr_title: str, pr_body: str) -> str:
    """Creates a real Pull Request using the provided GitHub Token."""
    import git
    import os
    import re
    import httpx
    try:
        repo = git.Repo(repo_path)
        
        try:
            origin = repo.remotes.origin
            remote_url = list(origin.urls)[0]
            match = re.search(r'github\.com[:/](.+?)/(.+?)(\.git)?$', remote_url)
            if not match:
                return "Failed to parse GitHub repository owner/name from remote URL."
            owner = match.group(1)
            repo_name = match.group(2).replace(".git", "")
        except Exception as e:
            return f"Failed to parse GitHub repository owner/name: {e}"
        
        # Check if branch exists, if not create and checkout, otherwise just checkout
        if branch_name not in [h.name for h in repo.heads]:
            repo.git.checkout('-b', branch_name)
        else:
            repo.git.checkout(branch_name)
        
        repo.git.add(A=True)
        # Check if anything to commit
        if not repo.index.diff("HEAD") and not repo.untracked_files:
            return "No changes to commit. The patch might have been identical to the original."
            
        repo.config_writer().set_value("user", "name", "Mistral OpsCommander").release()
        repo.config_writer().set_value("user", "email", "bot@mistral.ai").release()
        
        repo.index.commit(commit_message)
        
        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token:
            return "Error: No GITHUB_TOKEN environment variable found. Cannot push PR."
            
        # Push using authenticated URL
        auth_url = f"https://x-access-token:{github_token}@github.com/{owner}/{repo_name}.git"
        
        # Update the origin URL to the authenticated one
        origin.set_url(auth_url)
        
        print(f"[GitHub] Pushing branch {branch_name}...")
        try:
            origin.push(f"{branch_name}:{branch_name}", force=True)
        except Exception as e:
            # Restore URL before failing
            origin.set_url(remote_url)
            return f"Error pushing branch to remote: {str(e)}"
            
        # Restore URL so we don't leak token globally in local git config
        origin.set_url(remote_url)
        
        # Create PR via GitHub API
        api_url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        data = {
            "title": f"[Devstral] {pr_title}",
            "body": f"This PR was automatically generated by **Mistral OpsCommander** using Devstral 2 (Codestral).\n\n### Details:\n{pr_body}",
            "head": branch_name,
            "base": "main"  # Assume main for now, could be passed as arg
        }
        
        res = httpx.post(api_url, headers=headers, json=data)
        if res.status_code == 201:
            pr_url = res.json().get("html_url")
            print(f"[GitHub] PR Created: {pr_url}")
            return f"Pull Request successfully created by Devstral 2! [View PR here]({pr_url})"
        elif res.status_code == 422 and "A pull request already exists" in res.text:
             return f"Branch pushed successfully. A pull request for this branch already exists."
        else:
            return f"Branch pushed successfully to '{branch_name}', but failed to open PR: {res.text}"
            
    except Exception as e:
        return f"Failed to create pull request: {str(e)}"

tool_definitions = [
    {
        "type": "function",
        "function": {
            "name": "fetch_logs",
            "description": "Fetches recent application logs for a specific service to diagnose crashes.",
            "parameters": {
                "type": "object",
                "properties": {"service_name": {"type": "string"}},
                "required": ["service_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_patch",
            "description": "Delegates to the Coder Agent to generate a fix.",
            "parameters": {
                "type": "object",
                "properties": {"file_path": {"type": "string"}, "context": {"type": "string"}},
                "required": ["file_path", "context"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "report_status",
            "description": "Broadacasts status to voice.",
            "parameters": {
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Lists files in a given directory.",
            "parameters": {
                "type": "object",
                "properties": {"directory": {"type": "string"}},
                "required": ["directory"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "clone_repo",
            "description": "Clones a remote GitHub repository to a local Temp folder.",
            "parameters": {
                "type": "object",
                "properties": {"repo_url": {"type": "string"}},
                "required": ["repo_url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads the entire contents of a file.",
            "parameters": {
                "type": "object",
                "properties": {"file_path": {"type": "string"}},
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Overwrites the entire contents of a file.",
            "parameters": {
                "type": "object",
                "properties": {"file_path": {"type": "string"}, "content": {"type": "string"}},
                "required": ["file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_pull_request",
            "description": "Commits all changes in the repo path and simulates opening a Pull Request.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string"},
                    "branch_name": {"type": "string"},
                    "commit_message": {"type": "string"},
                    "pr_title": {"type": "string"},
                    "pr_body": {"type": "string"}
                },
                "required": ["repo_path", "branch_name", "commit_message", "pr_title", "pr_body"]
            }
        }
    }
]

def dispatch_tool(tool_name: str, tool_args: dict) -> str:
    """Executes the corresponding function based on tool name"""
    dispatch_map = {
        "fetch_logs": fetch_logs,
        "trigger_patch": trigger_patch,
        "report_status": report_status,
        "list_files": list_files,
        "clone_repo": clone_repo,
        "read_file": read_file,
        "write_file": write_file,
        "create_pull_request": create_pull_request
    }
    
    func = dispatch_map.get(tool_name)
    if func:
        return func(**tool_args)
    return f"Error: Tool {tool_name} not found."
