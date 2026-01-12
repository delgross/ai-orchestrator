
import asyncio
from agent_runner.state import AgentState
from agent_runner.db_utils import run_query

async def main():
    state = AgentState()
    # We must initialize to connect to DB
    await state.initialize()
    # Query Current Config
    print("--- Current Sovereign Configuration ---")
    cfg_query = "SELECT key, value FROM config_state WHERE key CONTAINS 'MODEL';"
    try:
        results = await run_query(state, cfg_query)
        if not results:
            print("No active configuration found.")
        else:
            for item in results:
                print(f"{item.get('key'):<25} : {item.get('value')}")
    except Exception as e:
        print(f"Error querying config: {e}")

    # Query Presets
    print("\n--- Saved Model Presets ---")
    query = "SELECT * FROM model_preset ORDER BY name;"
    try:
        results = await run_query(state, query)
        print("--- Saved Model Presets ---")
        if not results:
            print("No presets found in database.")
        else:
            for item in results:
                name = item.get('name')
                desc = item.get('description', '')
                created = item.get('created_at', 'N/A')
                updated = item.get('updated_at', 'N/A')
                print(f"\nPreset: {name}")
                print(f"Description: {desc}")
                print(f"Created: {created} | Updated: {updated}")
                print("Models:")
                for role, model in item.get('models', {}).items():
                    print(f"  {role:<20} : {model}")
    except Exception as e:
        print(f"Error querying DB: {e}")

if __name__ == "__main__":
    asyncio.run(main())
