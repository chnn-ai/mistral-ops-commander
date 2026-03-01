import json
from mistralai import Mistral
from typing import List, Dict, Any

from src.agent.client import get_mistral_client
from src.config import REASONING_MODEL
from src.agent.prompts import ORCHESTRATOR_SYSTEM_PROMPT
from src.agent.coder import generate_patch

class OpsCommander:
    def __init__(self):
        self.client = get_mistral_client()
        self.memory = []

    async def handle_incident_stream(self, alert_payload: Dict[str, Any]):
        yield json.dumps({"type": "info", "model": "System", "content": f"Received alert: {alert_payload.get('title')}"})
        
        self.memory.append({"role": "system", "content": ORCHESTRATOR_SYSTEM_PROMPT})
        self.memory.append({"role": "user", "content": f"New Alert payload received:\n{json.dumps(alert_payload, indent=2)}\nPlease diagnose and handle."})
        from src.agent.tools import tool_definitions, dispatch_tool
        
        for _ in range(5):
            yield json.dumps({"type": "info", "model": "Magistral (Brain)", "content": "Thinking..."})
            
            response = self.client.chat.complete(
                model=REASONING_MODEL,
                messages=self.memory,
                tools=tool_definitions,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            self.memory.append(message)
            
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    # Yield tool intention to UI
                    yield json.dumps({"type": "tool_call", "model": "Magistral (Brain)", "tool": tool_name, "args": tool_args})
                    
                    # Special UI event for Devstral Coder
                    if tool_name == "trigger_patch":
                        yield json.dumps({"type": "info", "model": "Devstral 2 (Coder)", "content": f"Analyzing {tool_args.get('file_path')}..."})
                    
                    tool_result = dispatch_tool(tool_name, tool_args)
                    
                    # Yield tool result
                    preview = tool_result[:500] + "..." if len(tool_result) > 500 else tool_result
                    yield json.dumps({"type": "tool_result", "model": "System", "tool": tool_name, "result": preview})
                    
                    self.memory.append({
                        "role": "tool",
                        "name": tool_name,
                        "content": tool_result,
                        "tool_call_id": tool_call.id
                    })
            else:
                yield json.dumps({"type": "final_plan", "model": "Magistral (Brain)", "content": message.content})
                break
