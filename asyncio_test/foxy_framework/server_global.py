class Global:
    """
    服务端全局对象
    """
    __instance = None

    engine = None  # sqlalchemy数据库引擎
    Session = None  # 数据库session
    pool = None  # 数据库连接池
    clients = []  # 在线客户端
    MAX_ONLINE_NUMBER = 3000  # 最大在线人数

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        pass


g = Global()
