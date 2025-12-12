import asyncio

async def run_mcp_socket(port, handler):
    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, handler), "127.0.0.1", port
    )
    async with server:
        await server.serve_forever()

async def handle_client(reader, writer, handler):
    while True:
        data = await reader.readline()
        if not data:
            break
        response = await handler(data.decode().strip())
        writer.write((response + "\n").encode())
        await writer.drain()
    writer.close()
