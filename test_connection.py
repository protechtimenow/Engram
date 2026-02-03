import asyncio
import websockets

async def test():
    uri = 'ws://localhost:18789?token=2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc'
    print(f'Testing {uri}...')
    try:
        ws = await websockets.connect(uri)
        print('Connected!')
        msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
        print(f'Received: {msg}')
        await ws.close()
        print('Test passed!')
    except Exception as e:
        print(f'Error: {e}')

asyncio.run(test())
