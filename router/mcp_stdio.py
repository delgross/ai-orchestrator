import sys
import asyncio

async def run_mcp_stdio(handler):
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    while True:
        line = await reader.readline()
        if not line:
            break
        response = await handler(line.decode().strip())
        sys.stdout.write(response + "\n")
        sys.stdout.flush()
