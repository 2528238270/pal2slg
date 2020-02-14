class Global:
    """
    游戏全局对象
    """
    __instance = None
    fps = None  # 游戏帧数
    screen = None  # 窗口surface
    fnt_hp = None  # 血量字体
    fnt_battle_name = None  # 战斗名字字体
    fnt_talk = None  # 聊天字体
    bg = None  # 游戏背景
    bg_title = None  # 标题背景
    bg_battle = None  # 战斗背景
    bg_hero_1 = None  # 英雄正常背景
    bg_hero_2 = None  # 英雄被打背景
    bg_hero_hp = None  # 英雄血条能量条
    hp_bar = None  # 血条
    mp_bar = None  # 能量条
    ry_fnt = None  # 伤害字体
    bg_enter = None
    btn1 = None
    btn2 = None
    btn3 = None
    btn4 = None
    btn5 = None
    btn6 = None
    ry_fnt_data = dict()  # 伤害字体偏移量
    # 战斗数据
    battle_data = {
        'teammates': [],  # 队友
        'enemies': []  # 敌人
    }
    skill_data = []  # 技能数据
    fight_mgr = None  # 战斗管理器
    scene_mgr = None  # 场景管理器
    animator = None  # 动画管理器
    talk_mgr = None  # 对话管理器
    camera_mgr = None  # 镜头管理器
    ani_factory = None  # 动画工厂
    npc_mgr = None  # npc管理器
    fade = None  # 淡入淡出功能
    game_map = None  # 游戏地图
    scene_id = 0  # 场景id

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        pass


class ENUM_SCENE:
    """
    场景枚举
    """
    START_SCENE = 1  # 开始界面
    GAME_SCENE = 2  # 游戏界面


g = Global()
