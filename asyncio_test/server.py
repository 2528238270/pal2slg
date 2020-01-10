import asyncio
import websockets

from models import User
from server_global import g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Server:
    def __init__(self, ip, port):
        """
        启动服务端
        """
        # 初始化数据库
        # TODO:在这里初始化数据库连接
        g.engine = create_engine('postgresql://postgres:123456@47.100.44.206:5432/mud', echo=True)
        g.Session = sessionmaker(bind=g.engine)
        # 启动服务端
        asyncio.get_event_loop().run_until_complete(self.init_server(ip, port))
        asyncio.get_event_loop().run_forever()

    async def init_server(self, ip, port):
        start_server = websockets.serve(self.accept, ip, port)
        await asyncio.wait([start_server, self.producer_handler()])

    async def accept(self, websocket, path):
        """
        每当有新连接进入时，就会触发这里
        """
        print("有新连接了")
        try:
            g.clients.add(websocket)
            await self.consumer_handler(websocket, path)
        except:
            print("异常了")
            # traceback.print_exc()

    async def consumer_handler(self, websocket, path):
        """
        处理客户端数据
        """
        try:
            print("进入客户端处理逻辑")
            async for msg in websocket:
                print(msg, type(msg))
                # TODO:在这里编写自己处理客户端消息的逻辑
                for client in g.clients:
                    await client.send(msg)
        except:
            g.clients.remove(websocket)
            print("退出客户端处理逻辑")
            # TODO:在这里编写客户端异常处理逻辑

    async def producer_handler(self):
        """
        服务端主逻辑
        """
        while True:
            # TODO:在这里编写循环逻辑
            await asyncio.sleep(1)
            print("当前在线人数：", len(g.clients))
            # for client in g.clients:
            #     # session = g.Session()
            #     # users = session.query(User.name).all()
            #     await client.send("当前在线人数："+str(len(g.clients)))


if __name__ == '__main__':
    Server('0.0.0.0', 8778)
