"""
战斗系统，整个项目中最复杂的系统
create by 狡猾的皮球
qq:871245007
2020年2月15日 13:23:01
"""
import json

import pygame

from code.engine.a_star import AStar
from code.engine.gui import Button
from code.engine.sprite import Sprite, draw_src_text, draw_src_outline_text, draw_rect_text
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

    def __init__(self, walker_id, mx, my, face=0, is_enemy=False):
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
        self.combo_count = 0  # 本回合连击数
        self.move_times = None  # 每回合可以移动的次数
        self.move_count = 0  # 本回合移动次数
        self.name = None  # 姓名
        self.is_enemy = is_enemy  # 是否为敌人
        self.show_walk_cell = False  # 是否显示可行走格子
        self.walk_cell = None  # 可行走格子(16*16)
        self.skill_list = []  # 技能列表

    def set_attr(self, hp=None, mp=None, atk=None, magic=None, defense=None, agi=None, luk=None, combo=None,
                 move_times=None):
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
        self.move_times = move_times or self.move_times  # 每回合可以移动的次数

    def set_name(self, name):
        """
        设置名字
        """
        self.name = name

    def set_skill(self, skill_list):
        self.skill_list = skill_list

    def add_skill(self, magic):
        self.skill_list.append(magic)

    def open_walk_cell(self, fight_map):
        """
        显示可行走的格子
        """
        # 不能操作正在行走的单位
        if self.walking:
            return
        if self.show_walk_cell:
            return
        if self.move_count >= self.move_times:
            return  # 没有可移动次数了
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
        # 删除不可到达的格子
        for point in total_point[::-1]:
            if AStar(fight_map.walk_data, [self.mx, self.my], point, offset=3).start() is None:
                total_point.remove(point)
        self.walk_cell = total_point
        self.show_walk_cell = True
        self.move_count += 1

    def draw_walk_cell(self, map_x, map_y):
        if not self.show_walk_cell:
            return
        # 画格子
        for point in self.walk_cell:
            big_x = int((point[0] - 1) / 3)
            big_y = int((point[1] - 1) / 3)
            Sprite.blit(g.screen, g.move_cell_img, map_x + big_x * 48 + 2, map_y + big_y * 48 + 2)


class FightMenu:
    """
    战斗操作指令的菜单
    """

    def __init__(self, surface, x, y, fight_mgr=None):
        self.surface = surface
        self.switch = False
        self.fight_mgr = fight_mgr
        self.x = x
        self.y = y
        self.img_bg = pygame.image.load('./resource/PicLib/all_sys/fight_menu_bg.png').convert_alpha()
        self.img_btn_move_1 = pygame.image.load('./resource/PicLib/all_sys/btn_move_1.png').convert_alpha()
        self.img_btn_move_2 = pygame.image.load('./resource/PicLib/all_sys/btn_move_2.png').convert_alpha()
        self.img_btn_attack_1 = pygame.image.load('./resource/PicLib/all_sys/btn_attack_1.png').convert_alpha()
        self.img_btn_attack_2 = pygame.image.load('./resource/PicLib/all_sys/btn_attack_2.png').convert_alpha()
        self.img_btn_magic_1 = pygame.image.load('./resource/PicLib/all_sys/btn_magic_1.png').convert_alpha()
        self.img_btn_magic_2 = pygame.image.load('./resource/PicLib/all_sys/btn_magic_2.png').convert_alpha()
        self.btn_move = Button(self.x, self.y, imgNormal=self.img_btn_move_1, imgMove=self.img_btn_move_2,
                               callBackFunc=self.move_click)
        self.btn_attack = Button(self.x, self.y, imgNormal=self.img_btn_attack_1, imgMove=self.img_btn_attack_2)
        self.btn_magic = Button(self.x, self.y, imgNormal=self.img_btn_magic_1, imgMove=self.img_btn_magic_2,
                                callBackFunc=self.magic_click)

        self.btn_list = [self.btn_move, self.btn_attack, self.btn_magic]

    def logic(self):
        if not self.switch:
            return
        for index, btn in enumerate(self.btn_list):
            btn.x = int(self.x + (self.img_bg.get_width() - self.img_btn_move_1.get_width()) / 2)
            btn.y = self.y + 15 + index * (self.img_btn_move_1.get_height() + 15)

    def render(self):
        if not self.switch:
            return
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

    def move_click(self):
        """
        移动点击事件
        """
        if self.fight_mgr.current_fighter.show_walk_cell:
            self.fight_mgr.current_fighter.show_walk_cell = False
        else:
            self.fight_mgr.current_fighter.open_walk_cell(self.fight_mgr.fight_map)

    def magic_click(self):
        if self.fight_mgr.current_fighter:
            if not self.fight_mgr.magic_plane.switch:
                self.fight_mgr.magic_plane.show(self.fight_mgr.current_fighter)
            else:
                self.fight_mgr.magic_plane.hide()


class FighterInfoPlane:
    """
    战斗人员信息面板
    """

    def __init__(self):
        self.fight_info_img = pygame.image.load('./resource/PicLib/all_sys/fight_info_bg.png').convert_alpha()
        self.switch = False
        self.fighter = None

    def show(self, fighter):
        self.fighter = fighter
        self.switch = True

    def hide(self):
        self.switch = False

    def render(self):
        if not self.switch:
            return
        Sprite.blit(g.screen, self.fight_info_img, 0, 320)
        color = (0, 0, 0)
        if self.fighter.is_enemy:
            color = (255, 0, 0)
        draw_src_text(g.screen, 10, 335, self.fighter.name, g.fnt_battle_name, color)
        draw_src_outline_text(g.screen, 10, 360, "体力  {}/{}".format(self.fighter.hp[0], self.fighter.hp[1]), g.fnt_talk,
                              (255, 0, 0), (0, 0, 0))
        draw_src_outline_text(g.screen, 10, 378, "真气  {}/{}".format(self.fighter.mp[0], self.fighter.mp[1]), g.fnt_talk,
                              (0, 0, 255), (0, 0, 0))
        draw_src_outline_text(g.screen, 10, 396, "武术  {}".format(self.fighter.atk), g.fnt_talk, (0, 255, 0), (0, 0, 0))
        draw_src_outline_text(g.screen, 10, 414, "灵力  {}".format(self.fighter.magic), g.fnt_talk, (0, 255, 0),
                              (0, 0, 0))
        draw_src_outline_text(g.screen, 10, 432, "防御  {}".format(self.fighter.defense), g.fnt_talk, (0, 255, 0),
                              (0, 0, 0))
        draw_src_outline_text(g.screen, 10, 450, "身法  {}".format(self.fighter.agi), g.fnt_talk, (0, 255, 0),
                              (0, 0, 0))
        draw_src_outline_text(g.screen, 170, 360, "吉运  {}".format(self.fighter.luk), g.fnt_talk, (0, 255, 0),
                              (0, 0, 0))
        draw_src_outline_text(g.screen, 170, 378, "连招  {}".format(self.fighter.combo), g.fnt_talk, (0, 255, 0),
                              (0, 0, 0))
        draw_src_outline_text(g.screen, 170, 396,
                              "剩余移动次数  {}".format(self.fighter.move_times - self.fighter.move_count), g.fnt_talk,
                              (0, 255, 0), (0, 0, 0))


class Magic:
    """
    法术
    """

    def __init__(self, magic_id):
        self.magic_id = magic_id  # 法术id
        with open(f'./resource/magic/{magic_id}.json', 'r', encoding='utf8') as file:
            self.magic_info = json.load(file)
        print(self.magic_info)


class MagicPlane:
    """
    仙术面板
    """

    def __init__(self):
        self.bg = pygame.image.load('./resource/PicLib/all_sys/magic_menu.png').convert_alpha()
        self.switch = False
        self.fighter = None
        self.focus_index = 0  # 选中的技能

    def show(self, fighter):
        self.fighter = fighter
        self.switch = True

    def hide(self):
        self.switch = False

    def render(self):
        if not self.switch:
            return
        Sprite.blit(g.screen, self.bg, 0, 0)
        # 渲染仙术列表
        for index, magic in enumerate(self.fighter.skill_list):
            row = int(index / 3)  # 行
            col = index % 3  # 列
            magic = self.fighter.skill_list[index]
            if not self.focus_index == index:
                # 名称
                draw_src_text(g.screen, 69 + col * 172, 215 + row * 26, magic.magic_info['name'], g.fnt_magic_plane,
                              rgb=(66, 121, 8))
                # 魔法值
                draw_src_text(g.screen, 207 + col * 172, 215 + row * 26, str(magic.magic_info['mp']), g.fnt_magic_plane,
                              rgb=(66, 121, 8))
            else:
                draw_src_outline_text(g.screen, 69 + col * 172, 215 + row * 26, magic.magic_info['name'],
                                      g.fnt_magic_plane, (0, 170, 0), (255, 255, 255))
                draw_src_outline_text(g.screen, 207 + col * 172, 215 + row * 26, str(magic.magic_info['mp']),
                                      g.fnt_magic_plane, (0, 170, 0), (255, 255, 255))
        # 仙术描述
        if self.focus_index >= len(self.fighter.skill_list):
            return
        magic = self.fighter.skill_list[self.focus_index]
        draw_rect_text(g.screen, (66, 121, 8), magic.magic_info['description'], g.fnt_magic_plane, 186, 84, 400)
        draw_rect_text(g.screen, (66, 121, 8), magic.magic_info['tip'], g.fnt_magic_plane, 186, 163, 400)

    def mouse_down(self, x, y, pressed):
        if pressed[2] == 1:
            self.hide()

    def mouse_move(self, x, y):
        dx = x - 69
        dy = y - 218
        index = int(dx / 172) + int(dy / 26) * 3
        if index >= 0:
            self.focus_index = index

    def mouse_up(self, x, y, pressed):
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
        self.move_cell_img = pygame.image.load('./resource/PicLib/all_sys/move_cell.png').convert_alpha()
        g.move_cell_img = self.move_cell_img
        self.fight_map = FightMap()  # 战斗地图
        self.fighter_list = []
        self.round = 1  # 当前回合数
        self.state = 1  # 1玩家操作状态 2电脑操作状态
        self.switch = False  # 是否打开战斗
        self.is_down = False  # 鼠标是否按下
        self.fight_menu = FightMenu(surface, 530, 100, self)
        self.info_plane = FighterInfoPlane()
        self.magic_plane = MagicPlane()
        # self.fight_menu.switch = True
        self.current_fighter = None  # 当前选中的fighter
        # 鼠标按下时，地图上的像素坐标
        self.mu_x = 0
        self.mu_y = 0
        Magic(1)

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
        # 渲染排序，显示正确的层级
        self.fighter_list.sort(key=lambda fight: fight.y)
        for fight in self.fighter_list:
            fight.logic()

    def render(self):
        if not self.switch:
            return
        Sprite.blit(self.surface, self.fight_map.btm_img, self.fight_map.x, self.fight_map.y)
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
        # 绘制可行走区域格子
        for fight in self.fighter_list:
            fight.draw_walk_cell(self.fight_map.x, self.fight_map.y)
        self.fight_menu.render()
        self.info_plane.render()
        self.magic_plane.render()

    def mouse_down(self, x, y, pressed):
        # 仙术面板
        if self.magic_plane.switch:
            self.magic_plane.mouse_down(x, y, pressed)
            return
        if pressed[2] == 1:
            self.fight_menu.switch = False
            return
        self.is_down = True
        self.mu_x = x - self.fight_map.x
        self.mu_y = y - self.fight_map.y
        self.fight_menu.mouse_down(x, y)

    def mouse_move(self, x, y):
        # 仙术面板
        if self.magic_plane.switch:
            self.magic_plane.mouse_move(x, y)
            return
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
            return
        # 操作菜单
        self.fight_menu.mouse_move(x, y)
        # 信息面板
        mx = int((x - self.fight_map.x) / 48) * 3 + 1
        my = int((y - self.fight_map.y) / 48) * 3 + 1
        for fighter in self.fighter_list:
            if fighter.mx == mx and fighter.my == my:
                self.info_plane.show(fighter)
                break
            else:
                self.info_plane.hide()

    def mouse_up(self, x, y, pressed):
        # 仙术面板
        if self.magic_plane.switch:
            self.magic_plane.mouse_up(x, y, pressed)
            return
        self.is_down = False
        self.fight_menu.mouse_up(x, y)
        # 选中格子
        mx = int((x - self.fight_map.x) / 48) * 3 + 1
        my = int((y - self.fight_map.y) / 48) * 3 + 1
        print(mx, my)
        for fighter in self.fighter_list:
            if fighter.mx == mx and fighter.my == my:
                if fighter.is_enemy:  # 只能选择友军
                    return
                # 显示这个人的移动范围
                self.fight_menu.switch = True
                self.current_fighter = fighter
                return
        # 移动
        if self.current_fighter and self.current_fighter.show_walk_cell:
            for point in self.current_fighter.walk_cell:
                if point[0] == mx and point[1] == my:
                    self.current_fighter.find_path(self.fight_map.walk_data, [mx, my])
                    return
