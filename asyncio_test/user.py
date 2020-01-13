import json

from foxy_framework.server import Connection
from foxy_framework.server import Server


@Server.register_cls
class User(Connection):
    """
    用户自定义类
    """

    def deal_data(self, data):
        py_obj = json.loads(data)
        print(py_obj)
