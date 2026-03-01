import discord
import os
import re
import asyncio
from typing import Dict, Any

from src.agent.orchestrator import OpsCommander

# Initialize the Discord client with intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Regex to find github URLs in messages
GITHUB_URL_PATTERN = re.compile(r'https://github\.com/[\w-]+/[\w-]+/?')

@client.event
async def on_ready():
    print(f'[Discord] Logged in as {client.user}')

@client.event
async def on_message(message: discord.Message):
    # Don't respond to ourselves
    if message.author == client.user:
        return

    # Check if this message looks like a bug report containing a github link
    match = GITHUB_URL_PATTERN.search(message.content)
    if match and ("bug" in message.content.lower() or "fix" in message.content.lower() or "broken" in message.content.lower() or "issue" in message.content.lower()):
        repo_url = match.group(0)
        
        await message.reply(f"🤖 **Mistral OpsCommander** acknowledged. Integrating with {repo_url} to investigate the issue. You can watch my progress on the dashboard...")
        
        # Build a simulated alert payload based on the Discord message
        alert_payload = {
            "alert_id": f"DISCORD-{message.id}",
            "title": f"User reported issue in repository: {repo_url}",
            "severity": "HIGH",
            "service": "discord-bot",
            "timestamp": message.created_at.isoformat(),
            "description": message.content,
            "repository": repo_url
        }
        
        print(f"\n[Discord Bot] Triggering OpsCommander for repository: {repo_url}")
        
        from src.main import trigger_incident, broker
        import json
        
        await trigger_incident(alert_payload)
        
        q = await broker.subscribe()
        final_answer = "Resolution complete."
        
        try:
            while True:
                chunk = await q.get()
                try:
                    data = json.loads(chunk)
                    if data.get("type") == "final_plan":
                        final_answer = data.get("content", final_answer)
                        break
                    if data.get("type") in ("done", "error"):
                        break
                except Exception:
                    pass
        except Exception as e:
            print(f"[Discord Error] {e}")
            final_answer = f"Error during execution: {e}"
        finally:
            broker.unsubscribe(q)
        
        # Reply with the final plan or PR link
        # Discord has a 2000 character limit
        if len(final_answer) > 1900:
            final_answer = final_answer[:1900] + "...\n[Truncated]"
            
        await message.reply(f"✅ **OpsCommander Report:**\n{final_answer}")

async def run_discord_bot():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("[Discord] WARNING: No DISCORD_TOKEN found in environment. Bot will not start.")
        return
    
    try:
        await client.start(token)
    except Exception as e:
        print(f"[Discord] Failed to start bot: {e}")
