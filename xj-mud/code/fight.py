"""
战斗系统，整个项目中最复杂的系统
create by 狡猾的皮球
qq:871245007
2020年2月15日 13:23:01
"""
import pygame

from code.engine.a_star import AStar
from code.engine.gui import Button
from code.engine.sprite import Sprite
from code.game_global import g
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
        # 48*48转16*16
        super().__init__(walker_id, mx * 3 + 1, my * 3 + 1, face)
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
        self.show_walk_cell = False  # 是否显示可行走格子
        self.walk_cell = None  # 可行走格子(16*16)

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

    def open_walk_cell(self, fight_map):
        """
        显示可行走的格子
        """
        # 不能操作正在行走的单位
        if self.walking:
            return
        if self.show_walk_cell:
            return
        # 不考虑障碍，能走多少个格子
        total_point = []
        for dx in range(-self.agi, self.agi + 1):
            for dy in range(-self.agi, self.agi + 1):
                if dx == 0 and dy == 0:
                    continue
                if abs(dx) + abs(dy) > self.agi:
                    continue
                if 0 < self.mx + dx * 3 < fight_map.w and 0 < self.my + dy * 3 < fight_map.h:
                    total_point.append((self.mx + dx * 3, self.my + dy * 3))
        # 依次寻轮，删除不可到达的格子
        for point in total_point[::-1]:
            if AStar(fight_map.walk_data, [self.mx, self.my], point, offset=3).start() is None:
                total_point.remove(point)
        self.walk_cell = total_point
        self.show_walk_cell = True
        print(self.walk_cell)

    def draw_walk_cell(self, map_x, map_y):
        if not self.show_walk_cell:
            return
        # 画格子
        for point in self.walk_cell:
            big_x = int((point[0] - 1) / 3)
            big_y = int((point[1] - 1) / 3)
            pygame.draw.rect(g.screen, (0, 255, 0),
                             (map_x + big_x * 48 + 2, map_y + big_y * 48 + 2, 48 - 4, 48 - 4), 0)


class VictoryCondition:
    """
    胜利条件
    """

    def __init__(self):
        pass


class FightMenu:
    """
    战斗操作指令的菜单
    """

    def __init__(self, surface, x, y):
        self.surface = surface
        self.switch = False
        self.x = x
        self.y = y
        self.img_bg = pygame.image.load('./resource/PicLib/all_sys/fight_menu_bg.png').convert_alpha()
        self.img_btn_move_1 = pygame.image.load('./resource/PicLib/all_sys/btn_move_1.png').convert_alpha()
        self.img_btn_move_2 = pygame.image.load('./resource/PicLib/all_sys/btn_move_2.png').convert_alpha()
        self.img_btn_attack_1 = pygame.image.load('./resource/PicLib/all_sys/btn_attack_1.png').convert_alpha()
        self.img_btn_attack_2 = pygame.image.load('./resource/PicLib/all_sys/btn_attack_2.png').convert_alpha()

        self.btn_move = Button(self.x, self.y, imgNormal=self.img_btn_move_1, imgMove=self.img_btn_move_2)
        self.btn_attack = Button(self.x, self.y, imgNormal=self.img_btn_attack_1, imgMove=self.img_btn_attack_2)
        self.btn_list = [self.btn_move, self.btn_attack]

    def logic(self):
        if not self.switch:
            return
        for index, btn in enumerate(self.btn_list):
            btn.x = int(self.x + (self.img_bg.get_width() - self.img_btn_move_1.get_width()) / 2)
            btn.y = self.y + 15 + index * (self.img_btn_move_1.get_height() + 15)

    def render(self):
        Sprite.blit(self.surface, self.img_bg, self.x, self.y)
        for btn in self.btn_list:
            btn.draw(self.surface)

    def mouse_down(self, x, y):
        for btn in self.btn_list:
            btn.mouse_down(x, y)

    def mouse_up(self, x, y):
        for btn in self.btn_list:
            btn.mouse_up()

    def mouse_move(self, x, y):
        for btn in self.btn_list:
            btn.get_focus(x, y)


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
        self.fighter_list = []
        self.round = 1  # 当前回合数
        self.state = 1  # 1玩家操作状态 2电脑操作状态
        self.switch = False  # 是否打开战斗
        self.is_down = False  # 鼠标是否按下
        self.fight_menu = FightMenu(surface, 400, 100)
        self.fight_menu.switch = True
        # 鼠标按下时，地图上的像素坐标
        self.mu_x = 0
        self.mu_y = 0

    def start(self, fighter_list, map_id):
        """
        开始战斗
        """
        self.fighter_list = fighter_list
        self.fight_map.load(map_id)
        self.switch = True

    def logic(self):
        if not self.switch:
            return
        self.fight_menu.logic()
        self.fighter_list.sort(key=lambda fight: fight.y)

    def render(self):
        if not self.switch:
            return
        Sprite.blit(self.surface, self.fight_map.btm_img, self.fight_map.x, self.fight_map.y)
        # 绘制可行走区域格子
        for fight in self.fighter_list:
            fight.draw_walk_cell(self.fight_map.x, self.fight_map.y)
        # 渲染战斗者
        for fight in self.fighter_list:
            fight.render(self.fight_map.x, self.fight_map.y)
        Sprite.blit(self.surface, self.fight_map.top_img, self.fight_map.x, self.fight_map.y)
        # 重绘战斗者
        for fight in self.fighter_list:
            if self.fight_map.redraw_data[fight.mx][fight.my] == 1:
                fight.render(self.fight_map.x, self.fight_map.y)
        # DEBUG
        for x in range(int(self.fight_map.size_w / 48)):
            for y in range(int(self.fight_map.size_h / 48)):
                pygame.draw.rect(g.screen, (255, 255, 255),
                                 (self.fight_map.x + x * 48 + 2, self.fight_map.y + y * 48 + 2, 48 - 4, 48 - 4), 1)

        self.fight_menu.render()

    def mouse_down(self, x, y):
        self.is_down = True
        self.mu_x = x - self.fight_map.x
        self.mu_y = y - self.fight_map.y
        self.fight_menu.mouse_down(x, y)

    def mouse_move(self, x, y):
        # 拖动地图逻辑
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
        self.fight_menu.mouse_move(x, y)

    def mouse_up(self, x, y):
        self.is_down = False
        self.fight_menu.mouse_up(x, y)
        # 选中格子
        mx = int((x - self.fight_map.x) / 48) * 3 + 1
        my = int((y - self.fight_map.y) / 48) * 3 + 1
        # TODO:判断是否选中友军
        print(mx, my)
        for fight in self.fighter_list:
            if fight.mx == mx and fight.my == my:
                # 显示这个人的移动范围
                fight.open_walk_cell(self.fight_map)
