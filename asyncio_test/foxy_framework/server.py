import asyncio
import datetime
import time
import traceback

import websockets

from foxy_framework.server_global import g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Connection:
    """
    连接类，每个websocket连接都是一个connection
    """

    def __init__(self, websocket):
        self.websocket = websocket

    def deal_data(self, data):
        """
        处理客户端的数据，需要子类实现
        """
        raise NotImplementedError


class Server:
    """
    服务端主类
    """
    __user_cls = None

    @staticmethod
    def print_log(msg):
        cur_time = datetime.datetime.now()
        s = "[" + str(cur_time) + "] " + msg
        print(s)

    @staticmethod
    def write_log(msg):
        """
        把一些重要的信息写入日志文件
        """
        with open('./' + time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.log', mode='a+',
                  encoding='utf8') as file:
            cur_time = datetime.datetime.now()
            s = "[" + str(cur_time) + "] " + msg
            file.write(s)

    @classmethod
    def register_cls(cls, sub_cls):
        """
        注册自定义类
        """
        if not issubclass(sub_cls, Connection):
            cls.print_log('注册用户自定义类失败，{}不是{}的子类'.format(sub_cls.__name__, Connection.__name__))
            return

        cls.__user_cls = sub_cls

    def __init__(self, ip, port):
        """
        启动服务端
        """
        # 初始化数据库
        # TODO:在这里初始化数据库连接
        g.engine = create_engine('postgresql://postgres:123456@47.100.44.206:5432/mud')
        g.Session = sessionmaker(bind=g.engine)
        # 检测自定义cls
        if self.__user_cls is None:
            self.print_log('服务器启动失败，未注册用户自定义类')
            return
        # 启动服务端
        asyncio.get_event_loop().run_until_complete(self.init_server(ip, port))
        asyncio.get_event_loop().run_forever()

    async def init_server(self, ip, port):
        start_server = websockets.serve(self.accept, ip, port)
        self.print_log("服务端启动成功！")
        await asyncio.wait([start_server, self.producer_handler()])

    async def accept(self, websocket, path):
        """
        每当有新连接进入时，就会触发这里
        """
        self.print_log('有新的连接：{}'.format(websocket.remote_address))
        try:
            user = self.__user_cls(websocket)
            g.clients.append(user)
            await self.consumer_handler(user, path)
        except:
            self.print_log('客户端处理异常：\n{}'.format(traceback.format_exc()))

    async def consumer_handler(self, user, path):
        """
        处理客户端数据
        """
        try:
            async for msg in user.websocket:
                await user.deal_data(msg)
        except:
            g.clients.remove(user)
            traceback.print_exc()
            # TODO:在这里编写客户端异常处理逻辑

    async def producer_handler(self):
        """
        服务端主逻辑
        """
        while True:
            # TODO:在这里编写循环逻辑
            await asyncio.sleep(1)
            # for client in g.clients:
            #     # session = g.Session()
            #     # users = session.query(User.name).all()
            #     await client.send("当前在线人数："+str(len(g.clients)))
