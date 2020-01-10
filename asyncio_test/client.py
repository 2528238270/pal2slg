import asyncio
import websockets


async def hello():
    uri = "ws://127.0.0.1:8778/abc"
    async with websockets.connect(uri) as websocket:
        while True:
            # async for msg in websocket:
            #     print(msg)
            s=input("请输入：")
            await websocket.send(s)
            # a=await websocket.recv()
            # print(a)
asyncio.get_event_loop().run_until_complete(hello())
