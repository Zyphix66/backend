import asyncio
import websockets
import json
import os

PORT = int(os.getenv("PORT", 8080))
connected = {}

async def broadcast(message):
    if connected:
        msg = json.dumps(message)
        await asyncio.gather(*(ws.send(msg) for ws in connected.values()))

async def handler(websocket):
    user = None
    try:
        async for message in websocket:
            data = json.loads(message)
            if data.get("type") == "login":
                user = data.get("user")
                if not user or user in connected:
                    await websocket.send(json.dumps({"type": "login_denied"}))
                    continue
                connected[user] = websocket
                await broadcast({"type": "online", "users": list(connected.keys())})
            elif data.get("type") == "msg":
                user = data.get("user")
                if user in connected:
                    await broadcast({
                        "type": "msg",
                        "text": data.get("text"),
                        "user": user,
                        "time": data.get("time")
                    })
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if user and user in connected:
            del connected[user]
            await broadcast({"type": "online", "users": list(connected.keys())})

async def main():
    async with websockets.serve(handler, "0.0.0.0", PORT):
        await asyncio.Future()

asyncio.run(main())
