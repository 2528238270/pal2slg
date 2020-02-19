"""
战棋战斗系统：
1.判断胜利的条件：敌人全灭获胜，我方全灭失败
2.战斗操作：
    ①玩家可以拖动地图
    ②玩家有移动、攻击、法术、道具、回合结束四个操作
3.攻击：
    ①人物的连击属性就是玩家每回合可以使用攻击指令的次数
    ②攻击是物理单体攻击，会进入战斗动画
4.法术：
    法术分为攻击型法术、恢复型法术和封印型法术
        ①攻击型法术：攻击型法术分为范围攻击和单体攻击，范围攻击不会进入战斗动画，单体攻击会进入战斗动画
        ②恢复型法术：给队友加血，不会进入战斗动画
        ③封印型法术：封印敌人，不会进入战斗动画
5.道具：
    道具一律都是作用单体的，并且都不会进入战斗动画
        ①回血道具
        ②回蓝道具
        ③回蓝回血道具
6.回合结束：
    不论是否还有队友没有行动，都回合结束（会有二次确认），进入敌人操作阶段

create by 狡猾的皮球
qq:871245007
2020年2月15日 13:23:01
"""
import json
import random
from copy import deepcopy

import pygame
from pygame.surface import Surface

from code.engine.a_star import AStar
from code.engine.animation import Animation
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
        self.skill_cell = []  # 施法距离(16*16)
        self.skill_list = []  # 技能列表
        self.current_skill = None  # 选中的技能
        self.show_skill_range = False  # 是否显示选中技能的攻击范围
        self.skill_count = 0  # 施法次数（正常只能一次）
        self.dead = False  # 是否为死者（死了会触发死亡动画）
        self.alpha = 255  # 死亡动画的不透明度
        self.dead_dy = 0  # 死亡y轴偏移量（死了人物会往上飘）
        self.max_dead_dy = 80  # 最大死亡偏移量
        self.current_surface = None  # idle状态下的图片
        self.visible = True  # 是否可见

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

    def set_current_skill(self, skill, fight_map):
        self.current_skill = skill
        total_point = []
        for dx in range(-skill.magic_info['length'], skill.magic_info['length'] + 1):
            for dy in range(-skill.magic_info['length'], skill.magic_info['length'] + 1):
                if dx == 0 and dy == 0:
                    continue
                if abs(dx) + abs(dy) > skill.magic_info['length']:
                    continue
                if 0 < self.mx + dx * 3 < fight_map.w and 0 < self.my + dy * 3 < fight_map.h:
                    total_point.append((self.mx + dx * 3, self.my + dy * 3))
        self.skill_cell = total_point
        self.show_skill_range = True

    def draw_skill_range(self, map_x, map_y):
        """
        渲染当前选中技能的范围
        """
        if not self.show_skill_range:
            return
        # 画格子
        for point in self.skill_cell:
            big_x = int((point[0] - 1) / 3)
            big_y = int((point[1] - 1) / 3)
            Sprite.blit(g.screen, g.magic_len_cell_img, map_x + big_x * 48 + 2, map_y + big_y * 48 + 2)

    def do_skill(self, fight_mgr):
        """
        施法
        """
        if self.skill_count > 0:
            return
        # 小格子
        mx = fight_mgr.mouse_mx * 3 + 1
        my = fight_mgr.mouse_my * 3 + 1
        # 判断施法坐标是不是超出范围
        if abs(int((self.mx - 1) / 3) - fight_mgr.mouse_mx) + abs(int((self.my - 1) / 3) - fight_mgr.mouse_my) > \
                self.current_skill.magic_info['length']:
            return
        # 施法的动画处理
        ani = g.ani_factory.create(self.current_skill.magic_info['ani_id'],
                                   fight_mgr.mouse_mx * 48 + fight_mgr.fight_map.x - 24,
                                   fight_mgr.mouse_my * 48 + fight_mgr.fight_map.y - 24, FightAnimation,
                                   extra={"mx": mx, "my": my, "fight_map": fight_mgr.fight_map})
        fight_mgr.select_skill_target = False
        # 找到技能内所有目标
        cell_list = fight_mgr.calc_range(self.current_skill.magic_info['range'], fight_mgr.mouse_mx,
                                         fight_mgr.mouse_my, fight_mgr.fight_map)
        fighters = fight_mgr.get_range_fighters(cell_list, fight_mgr)
        self.skill_effect(self.current_skill, fighters, ani)
        # TODO:记得打开这里
        # self.skill_count += 1

    def skill_effect(self, skill, fighters, ani):
        """
        技能影响
        """
        callback_extra = []
        for fighter in fighters:
            if skill.magic_info['type'] == '群体攻击':
                if not fighter.is_enemy:
                    continue
                if skill.magic_info['damage_type'] == '魔法伤害':
                    damage = self.skill_damage(skill, fighter)
                    fighter.hp[0] -= damage
                    if fighter.hp[0] <= 0:
                        fighter.hp[0] = 0
                    self.mp[0] -= skill.magic_info['mp']
                    callback_extra.append({
                        'fighter': fighter,
                        'damage': damage
                    })

        def t_cb(frame):
            for e in callback_extra:
                g.fight_mgr.damage_list.append(
                    DamageAnimation('attack', e['damage'], 0, 0, g.fight_mgr.fight_map, e['fighter'].mx,
                                    e['fighter'].my)
                )
                # 死亡处理
                if e['fighter'].hp[0] <= 0:
                    e['fighter'].set_dead()

        ani.done_callback = t_cb

    def skill_damage(self, skill, target):
        """
        计算魔法伤害：
            进攻方灵力*技能加成-被攻方防御，10%的伤害波动
        target:被攻方
        """
        damage = self.magic * skill.magic_info['damage']
        damage += random.randint(-damage / 10, damage / 10)
        if damage <= target.defense:
            damage = random.randint(1, 10)  # 伤害小于对方防御力时，伤害为1~10
        else:
            damage = damage - target.defense
        return int(damage)

    def move_fighter(self, mx, my, fight_map, fighter_list):
        """
        移动战斗者
        fighter_list:地图上所有的战斗者
        mx,my：小格子
        """
        # 深拷贝一份地图行走层，把敌人设置成障碍物，把友军设置为不可寻路（可通过）
        walk_data = deepcopy(fight_map.walk_data)
        for fighter in fighter_list:
            if fighter is self:
                continue
            if fighter.is_enemy == self.is_enemy:  # 是队友的情况,直接取消移动（你不可能跟队友站在同一个格子上吧）
                if fighter.mx == mx and fighter.my == my:
                    return
            # 是敌人的情况，把敌人上下左右斜角设置成障碍（小格子）
            walk_data[fighter.mx][fighter.my] = 1
            if fighter.my - 1 >= 0:
                walk_data[fighter.mx][fighter.my - 1] = 1
            if fighter.my + 1 < walk_data.h:
                walk_data[fighter.mx][fighter.my + 1] = 1
            if fighter.mx - 1 >= 0:
                walk_data[fighter.mx - 1][fighter.my] = 1
            if fighter.mx + 1 < walk_data.w:
                walk_data[fighter.mx + 1][fighter.my] = 1

            if fighter.my - 1 >= 0 and fighter.mx - 1 >= 0:
                walk_data[fighter.mx - 1][fighter.my - 1] = 1
            if fighter.my + 1 < walk_data.h and fighter.mx + 1 < walk_data.w:
                walk_data[fighter.mx + 1][fighter.my + 1] = 1
            if fighter.my + 1 < walk_data.h and fighter.mx - 1 >= 0:
                walk_data[fighter.mx - 1][fighter.my + 1] = 1
            if fighter.my - 1 >= 0 and fighter.mx + 1 < walk_data.w:
                walk_data[fighter.mx + 1][fighter.my - 1] = 1

        for point in self.walk_cell:
            if point[0] == mx and point[1] == my:
                self.find_path(walk_data, [mx, my])
                return

    def logic(self):
        """
        这个逻辑主要是用来处理死亡动画的
        """
        super().logic()
        if self.dead:
            self.dead_dy += 4
            self.alpha -= 8
            if self.dead_dy >= self.max_dead_dy:
                self.dead_dy = self.max_dead_dy
            if self.alpha <= 0:
                self.alpha = 0
        if self.alpha == 0:
            self.visible = False
            # 直接删除敌人
            g.fight_mgr.fighter_list.remove(self)

    def render(self, map_x, map_y):
        """
        死亡动画的渲染扩展
        """
        if not self.visible:
            return
        if not self.dead:
            super().render(map_x, map_y)
        else:
            render_x = map_x + self.render_x
            render_y = map_y + self.render_y - self.dead_dy
            if render_x < -self.cell_w or render_x > 640 or render_y < -self.cell_h or render_y > 480:
                """
                人物在屏幕外，不需要渲染
                """
                return
            Sprite.blit_alpha(g.screen, self.current_surface, render_x, render_y, self.alpha)

    def set_dead(self):
        self.dead = True
        self.current_surface = Sprite.subsurface(self.walker_img, 0, self.face, self.cell_w, self.cell_h)


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
        # 如果正在选择仙术，那么不能使用移动功能
        if self.fight_mgr.select_skill_target:
            return
        if self.fight_mgr.current_fighter.show_walk_cell:
            self.fight_mgr.current_fighter.show_walk_cell = False
        else:
            self.fight_mgr.current_fighter.open_walk_cell(self.fight_mgr.fight_map)

    def magic_click(self):
        # 如果正在移动，那么不能使用仙术功能
        if self.fight_mgr.current_fighter.show_walk_cell:
            return
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


class MagicPlane:
    """
    仙术面板
    """

    def __init__(self, fight_mgr):
        self.bg = pygame.image.load('./resource/PicLib/all_sys/magic_menu.png').convert_alpha()
        self.fight_mgr = fight_mgr
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
            return
        dx = x - 69
        dy = y - 218
        index = int(dx / 172) + int(dy / 26) * 3
        if index >= len(self.fighter.skill_list):
            return
        self.focus_index = index
        self.fighter.set_current_skill(self.fighter.skill_list[index], self.fight_mgr.fight_map)
        self.fight_mgr.select_skill_target = True  # 进入选择施法目标状态
        self.switch = False
        return index

    def mouse_move(self, x, y):
        dx = x - 69
        dy = y - 218
        index = int(dx / 172) + int(dy / 26) * 3
        if index >= 0:
            self.focus_index = index

    def mouse_up(self, x, y, pressed):
        pass


class FightAnimation(Animation):
    """
    为了解决战斗场景的动画使用窗口坐标系的问题，专门写的这个类
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 魔法在地图中的小格子坐标
        self.mx = kwargs['mx']
        self.my = kwargs['my']
        self.fight_map = kwargs['fight_map']

    def draw(self, surface):
        """
        绘制相对于地图坐标系的动画，按中心点绘制
        """
        self.draw_src(surface, self.fight_map.x + self.mx * 16 - self.dw / 2,
                      self.fight_map.y + self.my * 16 - self.dh / 2)


class DamageAnimation:
    """
    伤害动画
    """

    def __init__(self, ani_type, number, x, y, fight_map=None, mx=None, my=None):
        """
        构造伤害动画
        ani_type: 伤害类型：attack普通攻击 cri暴击 heal加血 poison中毒
        """
        width = 0

        self.surface = None
        self.fight_map = fight_map
        # 小格子
        self.mx = mx
        self.my = my

        if ani_type == 'attack':
            width += g.ry_fnt_data['frames']['-']['w']
            height = g.ry_fnt_data['frames']['-']['h']
            number = str(number)
            for n in number:
                width += g.ry_fnt_data['frames'][n]['w']
                if g.ry_fnt_data['frames'][n]['h'] > height:
                    height = g.ry_fnt_data['frames'][n]['h']
            self.surface = Surface((width, height), flags=pygame.SRCALPHA)
            offset_x = 0
            Sprite.draw_rect(
                self.surface,
                g.ry_fnt,
                offset_x, int(height / 2 - g.ry_fnt_data['frames']['-']['h'] / 2),
                g.ry_fnt_data['frames']['-']['x'],
                g.ry_fnt_data['frames']['-']['y'],
                g.ry_fnt_data['frames']['-']['w'],
                g.ry_fnt_data['frames']['-']['h']
            )
            offset_x += g.ry_fnt_data['frames']['-']['w']
            for n in number:
                Sprite.draw_rect(
                    self.surface,
                    g.ry_fnt,
                    offset_x, 0,
                    g.ry_fnt_data['frames'][n]['x'],
                    g.ry_fnt_data['frames'][n]['y'],
                    g.ry_fnt_data['frames'][n]['w'],
                    g.ry_fnt_data['frames'][n]['h']
                )
                offset_x += g.ry_fnt_data['frames'][n]['w']
        elif ani_type == 'cri':
            width += g.ry_fnt_data['frames']['#']['w']
            width += g.ry_fnt_data['frames']['-']['w']
            height = g.ry_fnt_data['frames']['#']['h']
            number = str(number)
            for n in number:
                width += g.ry_fnt_data['frames'][n]['w']
                if g.ry_fnt_data['frames'][n]['h'] > height:
                    height = g.ry_fnt_data['frames'][n]['h']
            self.surface = Surface((width, height), flags=pygame.SRCALPHA)
            offset_x = 0
            Sprite.draw_rect(
                self.surface,
                g.ry_fnt,
                offset_x, int(height / 2 - g.ry_fnt_data['frames']['#']['h'] / 2),
                g.ry_fnt_data['frames']['#']['x'],
                g.ry_fnt_data['frames']['#']['y'],
                g.ry_fnt_data['frames']['#']['w'],
                g.ry_fnt_data['frames']['#']['h']
            )
            offset_x = g.ry_fnt_data['frames']['#']['w']

            Sprite.draw_rect(
                self.surface,
                g.ry_fnt,
                offset_x, int(height / 2 - g.ry_fnt_data['frames']['-']['h'] / 2),
                g.ry_fnt_data['frames']['-']['x'],
                g.ry_fnt_data['frames']['-']['y'],
                g.ry_fnt_data['frames']['-']['w'],
                g.ry_fnt_data['frames']['-']['h']
            )
            offset_x += g.ry_fnt_data['frames']['-']['w']
            for n in number:
                Sprite.draw_rect(
                    self.surface,
                    g.ry_fnt,
                    offset_x, int(height / 2 - g.ry_fnt_data['frames'][n]['h'] / 2),
                    g.ry_fnt_data['frames'][n]['x'],
                    g.ry_fnt_data['frames'][n]['y'],
                    g.ry_fnt_data['frames'][n]['w'],
                    g.ry_fnt_data['frames'][n]['h']
                )
                offset_x += g.ry_fnt_data['frames'][n]['w']
        self.x = int(x - width / 2)
        self.y = y

        self.done = False
        self.move_length = 50
        self.current_length = 0  # 当前移动长度
        self.time = 0.5  # 伤害显示出来之后暂停多久
        self.count = int(g.fps * self.time)  # 1秒需要经过多少帧
        self.counter = 0  # 计数过了多少帧
        self.alpha = 255  # 不透明度

    def render(self):
        """
        绘制
        """
        if self.done:
            return
        if not self.fight_map:
            Sprite.blit_alpha(g.screen, self.surface, self.x, self.y, self.alpha)
        else:
            Sprite.blit_alpha(g.screen, self.surface,
                              self.fight_map.x + self.mx * 16 - int(self.surface.get_width() / 2),
                              self.y + self.fight_map.y + self.my * 16, self.alpha)

    def logic(self):
        if self.done:
            return
        self.counter += 1
        if self.counter < self.count:
            return

        self.y -= 1
        self.current_length += 1
        self.alpha -= 5
        if self.current_length >= self.move_length:
            self.done = True


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
        self.magic_len_cell_img = pygame.image.load('./resource/PicLib/all_sys/magic_len_cell.png').convert_alpha()

        g.move_cell_img = self.move_cell_img
        g.magic_len_cell_img = self.magic_len_cell_img

        self.fight_map = FightMap()  # 战斗地图
        self.fighter_list = []
        self.round = 1  # 当前回合数
        self.state = 1  # 1玩家操作状态 2电脑操作状态
        self.switch = False  # 是否打开战斗
        self.is_down = False  # 鼠标是否按下
        self.select_skill_target = False  # 是否正在选择施法目标
        self.fight_menu = FightMenu(surface, 530, 100, self)
        self.info_plane = FighterInfoPlane()
        self.magic_plane = MagicPlane(self)
        # self.fight_menu.switch = True
        self.current_fighter = None  # 当前选中的fighter
        # 鼠标按下时，地图上的像素坐标
        self.mu_x = 0
        self.mu_y = 0
        # 鼠标在地图上大格子的坐标
        self.mouse_mx = 0
        self.mouse_my = 0
        # 伤害动画列表
        self.damage_list = []

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
        self.damage_logic()
        self.fight_menu.logic()
        # 渲染排序，显示正确的层级
        self.fighter_list.sort(key=lambda fight: fight.y)
        for fight in self.fighter_list:
            fight.logic()

    def damage_logic(self):
        """伤害动画逻辑"""
        for damage in self.damage_list[::-1]:
            if damage.done:
                self.damage_list.remove(damage)
                continue
            damage.logic()

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
        # for x in range(int(self.fight_map.size_w / 48)):
        #     for y in range(int(self.fight_map.size_h / 48)):
        #         pygame.draw.rect(g.screen, (255, 255, 255),
        #                          (self.fight_map.x + x * 48 + 2, self.fight_map.y + y * 48 + 2, 48 - 4, 48 - 4), 1)
        # 绘制可行走区域格子
        if self.current_fighter:
            self.current_fighter.draw_walk_cell(self.fight_map.x, self.fight_map.y)
        if self.select_skill_target:
            # 绘制施法距离
            self.current_fighter.draw_skill_range(self.fight_map.x, self.fight_map.y)
            # 绘制法术范围
            self.draw_skill_cell()
        # 画伤害
        for damage in self.damage_list:
            damage.render()
        self.fight_menu.render()
        self.info_plane.render()
        self.magic_plane.render()

    def mouse_down(self, x, y, pressed):
        # 仙术面板
        if self.magic_plane.switch:
            self.magic_plane.mouse_down(x, y, pressed)
            return
        if pressed[2] == 1:
            # 关闭选择目标
            if self.select_skill_target:
                self.select_skill_target = False
                return
            # 关闭战斗菜单
            if self.fight_menu.switch:
                self.fight_menu.switch = False
                return
        # 左键单击事件
        if self.select_skill_target:
            # TODO：施法
            self.current_fighter.do_skill(self)
            return

        self.is_down = True
        self.mu_x = x - self.fight_map.x
        self.mu_y = y - self.fight_map.y
        self.fight_menu.mouse_down(x, y)

    def mouse_move(self, x, y):
        mx = int((x - self.fight_map.x) / 48) * 3 + 1
        my = int((y - self.fight_map.y) / 48) * 3 + 1
        self.mouse_mx = int((x - self.fight_map.x) / 48)
        self.mouse_my = int((y - self.fight_map.y) / 48)

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
        for fighter in self.fighter_list:
            if fighter.mx == mx and fighter.my == my:
                self.info_plane.show(fighter)
                break
            else:
                self.info_plane.hide()

    def mouse_up(self, x, y, pressed):
        # 小格子
        mx = int((x - self.fight_map.x) / 48) * 3 + 1
        my = int((y - self.fight_map.y) / 48) * 3 + 1
        # 仙术面板
        if self.magic_plane.switch:
            self.magic_plane.mouse_up(x, y, pressed)
            return
        self.is_down = False
        self.fight_menu.mouse_up(x, y)
        # 选中友军
        if self.select_teammate(mx, my):
            return
        # 移动人物
        if self.current_fighter and self.current_fighter.show_walk_cell:
            self.current_fighter.move_fighter(mx, my, self.fight_map, self.fighter_list)
            return

    def select_teammate(self, mx, my):
        """
        选中友军
        """
        print(mx, my)
        for fighter in self.fighter_list:
            if fighter.mx == mx and fighter.my == my:
                if fighter.is_enemy:  # 只能选择友军
                    return True
                # 显示这个人的移动范围
                self.fight_menu.switch = True
                self.current_fighter = fighter
                return True
        return False

    def draw_skill_cell(self):
        """
        绘制当前技能的格子
        """
        skill = self.current_fighter.current_skill
        for dx in range(-skill.magic_info['range'], skill.magic_info['range'] + 1):
            for dy in range(-skill.magic_info['range'], skill.magic_info['range'] + 1):
                if abs(dx) + abs(dy) > skill.magic_info['range']:
                    continue
                if 0 < (self.mouse_mx + dx) * 3 < self.fight_map.w and 0 < (self.mouse_my + dy) * 3 < self.fight_map.h:
                    Sprite.blit(g.screen, g.magic_len_cell_img, self.fight_map.x + (self.mouse_mx + dx) * 48 + 2,
                                self.fight_map.y + (self.mouse_my + dy) * 48 + 2)

    @staticmethod
    def calc_range(length, big_x, big_y, fight_map):
        """
        计算格子覆盖范围(返回的是小格子)
        """
        cell_list = []
        for dx in range(-length, length + 1):
            for dy in range(-length, length + 1):
                if abs(dx) + abs(dy) > length:
                    continue
                if 0 <= big_x + dx < int(fight_map.w / 3) and 0 <= big_y + dy < int(fight_map.h / 3):
                    cell_list.append([(big_x + dx) * 3 + 1, (big_y + dy) * 3 + 1])
        return cell_list

    @staticmethod
    def get_range_fighters(cell_list, fight_mgr):
        """
        获取格子覆盖范围内的fighter
        """
        fighters = []
        for point in cell_list:
            for fighter in fight_mgr.fighter_list:
                if fighter.mx == point[0] and fighter.my == point[1]:
                    fighters.append(fighter)
        return fighters

    @staticmethod
    def get_range_enemies(cell_list, fight_mgr):
        """
        获取范围内的敌人
        """
        fighters = FightManager.get_range_fighters(cell_list, fight_mgr)
        for fighter in fighters[::-1]:
            if not fighter.is_enemy:
                fighters.remove(fighter)

    @staticmethod
    def get_range_teammates(cell_list, fight_mgr):
        """
        获取范围内的友军
        """
        fighters = FightManager.get_range_fighters(cell_list, fight_mgr)
        for fighter in fighters[::-1]:
            if fighter.is_enemy:
                fighters.remove(fighter)

    @staticmethod
    def big2small(big_x, big_y):
        """
        大格子转小格子
        """
        return big_x * 3 + 1, big_y * 3 + 1

    @staticmethod
    def small2big(mx, my):
        """
        小格子转大格子
        """
        return int((mx - 1) / 3), int((my - 1) / 3)
