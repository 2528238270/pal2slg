import asyncio
import datetime
import time
import traceback

import websockets

from foxy_framework.server_global import g
from aiopg.sa import create_engine


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

    def offline(self, msg):
        """
        离线处理，需要子类实现
        """
        raise NotImplementedError


class Server:
    """
    服务端主类
    """
    __user_cls = None
    __main_loop = None
    __main_loop_obj = None
    __init = None
    __init_obj = None

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

    @classmethod
    def register_main_loop(cls, sub_cls):
        """
        注册主循环对象
        """
        cls.__main_loop = sub_cls

    @classmethod
    def register_init(cls, sub_cls):
        """
        注册初始化对象
        """
        cls.__init = sub_cls


    def __init__(self, ip, port):
        """
        启动服务端
        """
        # 检测自定义cls
        if self.__user_cls is None:
            self.print_log('服务器启动失败，未注册用户自定义类')
            return
        if self.__main_loop is not None:
            self.__main_loop_obj = self.__main_loop()
        if self.__init is not None:
            self.__init_obj = self.__init()
        # 启动服务端
        asyncio.get_event_loop().run_until_complete(self.init_server(ip, port))
        asyncio.get_event_loop().run_forever()

    async def init_server(self, ip, port):
        """
        初始化服务端
        """
        g.engine = await create_engine('postgresql://postgres:123456@47.100.44.206:5432/mud')
        start_server = websockets.serve(self.accept, ip, port)
        if self.__init_obj:
            await self.__init_obj()
            self.print_log("初始化服务端数据成功！")
        self.print_log("服务端启动成功！")
        await asyncio.wait([start_server, self.producer_handler()])

    async def accept(self, websocket, path):
        """
        每当有新连接进入时，就会触发这里
        """
        try:
            if len(g.clients) >= g.MAX_ONLINE_NUMBER:
                await websocket.close()
                self.print_log('服务器爆满，无法接收新连接！')
                return
            user = self.__user_cls(websocket)
            g.clients.append(user)
            self.print_log(
                '有新的连接：{}，当前在线人数：{}/{}'.format(websocket.remote_address, len(g.clients), g.MAX_ONLINE_NUMBER)
            )
            await self.consumer_handler(user, path)
        except:
            self.print_log('理论上来说，这里不会异常，客户端处理异常：\n{}'.format(traceback.format_exc()))
            websocket.close()

    async def consumer_handler(self, user, path):
        """
        处理客户端数据
        """
        m = None
        try:
            async for msg in user.websocket:
                m = msg
                await user.deal_data(msg)
        except:
            await user.offline('数据异常！')
            self.print_log("客户端数据异常，已强制下线。客户端原始数据:{}".format(m))
            traceback.print_exc()

    async def producer_handler(self):
        """
        服务端主逻辑
        """
        while True:
            await asyncio.sleep(1)
            await self.__main_loop_obj()

