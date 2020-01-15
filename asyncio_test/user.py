import json
import time
import traceback

from foxy_framework.server import Connection
from foxy_framework.server import Server

import api
from foxy_framework.server_global import g


@Server.register_cls
class Player(Connection):
    """
    用户自定义类
    """
    user_data = None
    user_last_beat = 0  # 上一次心跳时间
    user_timeout = 600  # 心跳超时时间，秒

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_last_beat = time.time()

    async def deal_data(self, data):
        """
        处理客户端发送过来的消息:
        {
           "protocol_name":"login",
           "data":data
        }
        """
        py_obj = json.loads(data)
        protocol_name = py_obj['protocol_name']
        method = getattr(api, protocol_name)
        if method is None:
            print("协议非法")
        await method(self, py_obj['data'])

    async def send(self, py_obj):
        """
        发送数据
        """
        try:
            json_str = json.dumps(py_obj, ensure_ascii=False)
            print(json_str)
            await self.websocket.send(json_str)
            self.user_last_beat = time.time()
        except:
            print('发送数据失败')
            traceback.print_exc()
            await self.offline('连接异常')

    async def offline(self, msg):
        """
        强制下线
        """
        await self.websocket.close()
        g.clients.remove(self)


@Server.register_main_loop
class MainLoop:
    async def __call__(self, *args, **kwargs):
        """
        此处代码会每秒执行一次
        """
        # 心跳检测
        now = time.time()
        for player in g.clients:
            if now - player.user_last_beat > player.user_timeout:
                await player.offline('心跳超时')
                continue

        g.count += 1
        if g.count == 15:
            Server.print_log('当前在线人数：{}'.format(len(g.clients)))
            g.count = 0

    def __init__(self):
        g.count = 0
