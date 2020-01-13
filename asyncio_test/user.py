import json

from foxy_framework.server import Connection
from foxy_framework.server import Server


@Server.register_cls
class User(Connection):
    """
    用户自定义类
    """

    async def deal_data(self, data):
        """
        我们规定协议格式：
        {
            "protocol":"login",
            "data":"加密的json字符串",
            "sign":"签名"
        }
        """
        py_obj = json.loads(data)
        await self.send(py_obj)

    async def send(self, py_obj):
        """
        发送数据
        """
        json_str = json.dumps(py_obj)
        await self.websocket.send(json_str)
