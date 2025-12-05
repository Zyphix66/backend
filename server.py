import asyncio
import websockets
import json
import os

PORT = int(os.getenv("PORT", 8765))
connected = set()

async def broadcast(message):
    if connected:
        msg = json.dumps(message)
        await asyncio.gather(*(ws.send(msg) for ws in connected))

async def handler(websocket):
    connected.add(websocket)
    await broadcast({"type": "online", "count": len(connected)})
    try:
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "msg":
                await broadcast({
                    "type": "msg",
                    "text": data["text"],
                    "user": str(websocket.remote_address)
                })
    except:
        pass
    finally:
        connected.remove(websocket)
        await broadcast({"type": "online", "count": len(connected)})

async def main():
    async with websockets.serve(handler, "0.0.0.0", PORT):
        await asyncio.Future()

asyncio.run(main())
