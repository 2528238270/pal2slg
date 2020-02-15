"""
战斗系统，整个项目中最复杂的系统
create by 狡猾的皮球
qq:871245007
2020年2月15日 13:23:01
"""
from code.engine.sprite import Sprite
from code.game_map import GameMap
from code.walker import Walker


class FightMap(GameMap):
    def __init__(self):
        """
        初始化战斗地图
        """
        super().__init__()


class Fighter(Walker):
    """
    战斗者
    """

    def __init__(self, walker_id, mx, my, face=0):
        super().__init__(walker_id, mx, my, face)
        self.hp = None  # 生命值
        self.mp = None  # 魔法值
        self.atk = None  # 攻击力
        self.magic = None  # 灵力
        self.defense = None  # 防御力
        self.agi = None  # 身法
        self.luk = None  # 吉运
        self.combo = None  # 连击数
        self.name = None  # 姓名
        self.is_enemy = False  # 是否为敌人

    def set_attr(self, hp=None, mp=None, atk=None, magic=None, defense=None, agi=None, luk=None, combo=None):
        """
        设置属性
        """
        self.hp = hp or self.hp  # 生命值
        self.mp = mp or self.mp  # 魔法值
        self.atk = atk or self.atk  # 攻击力
        self.magic = magic or self.magic  # 灵力
        self.defense = defense or self.defense  # 防御力
        self.agi = agi or self.agi  # 身法
        self.luk = luk or self.luk  # 吉运
        self.combo = combo or self.combo  # 连击数

    def set_name(self, name):
        """
        设置名字
        """
        self.name = name


class VictoryCondition:
    """
    胜利条件
    """

    def __init__(self):
        pass


class FightManager:
    """
    战斗管理器
    """

    def __init__(self, surface):
        """
        初始化战斗管理器
        """
        self.surface = surface
        self.fight_map = FightMap()  # 战斗地图
        self.round = 1  # 当前回合数
        self.state = 1  # 1玩家操作状态 2电脑操作状态
        self.switch = False  # 是否打开战斗
        self.is_down = False  # 鼠标是否按下
        # 鼠标按下时，地图上的像素坐标
        self.mu_x = 0
        self.mu_y = 0

    def start(self, fighter_list, map_id):
        """
        开始战斗
        """
        self.fight_map.load(map_id)
        self.switch = True

    def logic(self):
        if not self.switch:
            return

    def render(self):
        if not self.switch:
            return
        Sprite.blit(self.surface, self.fight_map.btm_img, self.fight_map.x, self.fight_map.y)
        # TODO:渲染战斗者
        Sprite.blit(self.surface, self.fight_map.top_img, self.fight_map.x, self.fight_map.y)
        # TODO:重绘战斗者

    def mouse_down(self, x, y):
        self.is_down = True
        self.mu_x = x - self.fight_map.x
        self.mu_y = y - self.fight_map.y

    def mouse_move(self, x, y):
        if self.is_down:
            self.fight_map.x = x - self.mu_x
            self.fight_map.y = y - self.mu_y
            if self.fight_map.x > 0:
                self.fight_map.x = 0
            if self.fight_map.x < -self.fight_map.size_w + 640:
                self.fight_map.x = -self.fight_map.size_w + 640
            if self.fight_map.y > 0:
                self.fight_map.y = 0
            if self.fight_map.y < -self.fight_map.size_h + 480:
                self.fight_map.y = -self.fight_map.size_h + 480

    def mouse_up(self, x, y):
        self.is_down = False
