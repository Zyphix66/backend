import asyncio
import websockets
import json
import os

PORT = int(os.getenv("PORT", 8080))
connected = {}
usernames = set()

async def broadcast(message):
    if connected:
        msg = json.dumps(message)
        await asyncio.gather(*(ws.send(msg) for ws in connected.values()))

async def broadcast_users():
    users = list(connected.keys())
    await broadcast({"type": "users", "list": users})

async def handler(websocket):
    try:
        async for message in websocket:
            data = json.loads(message)
            if data.get("type") == "login":
                user = data.get("user")
                if not user or user in usernames:
                    await websocket.send(json.dumps({"type": "login_denied"}))
                    continue
                usernames.add(user)
                connected[user] = websocket
                await broadcast({"type": "online", "count": len(connected)})
                await broadcast_users()
            elif data.get("type") == "msg":
                user = data.get("user")
                if user in connected:
                    await broadcast({"type": "msg", "text": data.get("text"), "user": user})
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        disconnected_user = None
        for user, ws in list(connected.items()):
            if ws == websocket:
                disconnected_user = user
                break
        if disconnected_user:
            del connected[disconnected_user]
            usernames.discard(disconnected_user)
            await broadcast({"type": "online", "count": len(connected)})
            await broadcast_users()

async def main():
    async with websockets.serve(handler, "0.0.0.0", PORT):
        await asyncio.Future()

asyncio.run(main())
