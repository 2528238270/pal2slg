class Global:
    """
    游戏全局对象
    """
    __instance = None

    engine = None
    Session = None
    clients = set()

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        pass


g = Global()
