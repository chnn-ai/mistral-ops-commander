from src.agent.client import get_mistral_client
from src.agent.prompts import CODER_SYSTEM_PROMPT
from src.config import CODE_MODEL

def generate_patch(file_path: str, incident_context: str) -> str:
    """Takes a file path and context, asks Codestral to fix it."""
    client = get_mistral_client()
    
    # In a real app we would read `file_path` here using local files or MCP GitHub
    try:
        with open(file_path, 'r') as f:
            file_content = f.read()
    except FileNotFoundError:
        return f"Error: {file_path} not found."

    messages = [
        {"role": "system", "content": CODER_SYSTEM_PROMPT},
        {"role": "user", "content": f"Fix the issue in the following code based on this context:\nContext: {incident_context}\n\nCode:\n```python\n{file_content}\n```"}
    ]
    
    response = client.chat.complete(
        model=CODE_MODEL,
        messages=messages
    )
    
    # Extract code from response
    content = response.choices[0].message.content
    
    # Strip markdown code blocks if the model wrapped it
    if "```python" in content:
        content = content.split("```python")[1].split("```")[0].strip()
    elif "```" in content:
        # Generic code block
        content = content.split("```")[1].split("```")[0].strip()
        
    return content
