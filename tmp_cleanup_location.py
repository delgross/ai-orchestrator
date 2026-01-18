import asyncio
from agent_runner.state import AgentState
from agent_runner.db_utils import run_query

async def main():
    state = AgentState()
    await state.memory.initialize()

    records = await run_query(state, "SELECT id, key FROM config_state WHERE key = 'location'")
    print('Existing location records:', records)
    if records:
        for rec in records:
            rid = rec.get('id')
            if rid:
                await run_query(state, f"DELETE {rid};")
                print('Deleted', rid)
    remaining = await run_query(state, "SELECT id, key FROM config_state WHERE key = 'location'")
    print('Remaining location records:', remaining)

    keys = [
        "AGENT_MODEL","ROUTER_MODEL","TASK_MODEL","SUMMARIZATION_MODEL",
        "MCP_MODEL","FINALIZER_MODEL","CRITIC_MODEL","HEALER_MODEL",
        "FALLBACK_MODEL","INTENT_MODEL","PRUNER_MODEL","QUERY_REFINEMENT_MODEL"
    ]
    formatted = '[' + ', '.join([f"'{k}'" for k in keys]) + ']'
    res = await run_query(state, f"SELECT key, value FROM config_state WHERE key IN {formatted}")
    print('Model rows:', res)

if __name__ == '__main__':
    asyncio.run(main())
