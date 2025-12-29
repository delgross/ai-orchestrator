import asyncio
import httpx
import json

MENU = """
sequential-thinking: sequentialthinking
fetch: fetch
filesystem: read_file, list_directory
tavily-search: tavily-search
"""

PROMPT = (
    "You are the Tool Selector (The Maître d').\n"
    "User Query: 'List the files in the current directory'\n\n"
    "Available Discretionary Tools (Menu):\n"
    f"{MENU}\n\n"
    "Task: Select the 'target_servers' from the menu that are required for this query.\n"
    "Note: Core tools (Memory, Time, Thinking) are ALREADY loaded. Only select from the menu if needed.\n"
    "Response Format: {\"target_servers\": [\"server1\"]}"
)

async def test():
    print(f"Testing Maître d' with model: ollama:llama3.3:70b-instruct-q8_0")
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(
                "http://127.0.0.1:5455/v1/chat/completions",
                headers={"Authorization": "Bearer 9sYBjBLjAHKG8g8ZzzsUeBOvtzgQFHmX7oIeygdpzic"},
                json={
                    "model": "ollama:llama3.3:70b-instruct-q8_0",
                    "messages": [{"role": "user", "content": PROMPT}],
                    "stream": False,
                    "response_format": {"type": "json_object"}
                },
                timeout=30.0
            )
            print(f"Status: {r.status_code}")
            print(f"Response: {r.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
