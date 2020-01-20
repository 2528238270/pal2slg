from foxy_framework.server import Server


@Server.register_init
class InitGame:
    async def __call__(self, *args, **kwargs):
        """
        初始化相关的操作
        """
        print("初始化")
