import asyncio
import websockets
import json

connected_clients = {}

async def handler(websocket, path):
    client_id = f"{websocket.remote_address}"
    connected_clients[client_id] = websocket
    print("Connected:", client_id)

    try:
        await broadcast({"type": "online", "count": len(connected_clients)})

        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "msg":
                await broadcast({
                    "type": "msg",
                    "user": client_id,
                    "text": data["text"]
                })

    except:
        pass
    finally:
        del connected_clients[client_id]
        await broadcast({"type": "online", "count": len(connected_clients)})
        print("Disconnected:", client_id)

async def broadcast(message):
    msg_str = json.dumps(message)
    await asyncio.gather(*(ws.send(msg_str) for ws in connected_clients.values()))

start = websockets.serve(handler, "0.0.0.0", 8765)
print("Server running on port 8765")
asyncio.get_event_loop().run_until_complete(start)
asyncio.get_event_loop().run_forever()
