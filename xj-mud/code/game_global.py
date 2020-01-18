class Global:
    """
    游戏全局对象
    """
    __instance = None
    fps = None                  # 游戏帧数
    screen = None               # 窗口surface
    fnt_hp = None               # 血量字体
    fnt_battle_name = None      # 战斗名字字体
    bg = None                   # 游戏背景
    bg_title = None             # 标题背景
    bg_battle = None            # 战斗背景
    bg_hero_1 = None            # 英雄正常背景
    bg_hero_2 = None            # 英雄被打背景
    bg_hero_hp = None           # 英雄血条能量条
    hp_bar = None               # 血条
    mp_bar = None               # 能量条
    ry_fnt = None               # 伤害字体
    ry_fnt_data = dict()        # 伤害字体偏移量
    # 战斗数据
    battle_data = {
        'teammates': [],        # 队友
        'enemies': []           # 敌人
    }
    skill_data = []             # 技能数据
    fight_mgr = None            # 战斗管理器

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        pass


g = Global()
