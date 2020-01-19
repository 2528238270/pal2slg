import copy
import math
import random
import json

import pygame
from pygame import Surface
from code.game_global import g
from code.engine.sprite import Sprite, draw_outline_text


class Fighter:
    """
    战斗者
    """
    attr = ['level', 'hp', 'atk', 'dfs', 'hit', 'cri', 'dod', 'rcri']

    def __init__(self, index, team_type, name, level, hp, atk, dfs, hit, cri, dod, rcri,skill_id=None):
        self.name = name                        # 英雄姓名
        self.level = level                      # 等级
        self.hp = hp                            # 生命值
        self.atk = atk                          # 攻击力
        self.dfs = dfs                          # 防御力
        self.hit = hit                          # 命中率
        self.cri = cri                          # 暴击率
        self.dod = dod                          # 闪避率
        self.rcri = rcri                        # 抗暴击率
        self.debuff = []                        # 减益效果
        self.buff = []                          # 增益效果
        if skill_id is not None:
            self.skill = g.skill_data[skill_id-1]   # 技能
        else:
            self.skill = None

        self.team_type = team_type      # 队伍类型 1我方 2敌方
        self.index = index              # 在队伍中的位置
        if team_type == 1:              # 我方位置
            self.box_x = 160 - int(index / 3) * 140
            self.box_y = 5 + (index % 3 + 1) * 90
        else:                           # 敌方位置
            self.box_x = 350 + int(index / 3) * 140
            self.box_y = 5 + (index % 3 + 1) * 90

        # 绘图坐标
        self.x = self.box_x
        self.y = self.box_y

        # 攻击动画相关参数
        self.move_dir = 1           # 移动方向 1正向 -1反向
        self.speed = 0.18           # 单个方向攻击动画的时长，单位秒
        self.sin = None             # 移动方向的sin值
        self.cos = None             # 移动方向的cos值
        self.length = None          # 两点长度
        self.l = None               # 单位长度
        self.d_l = 0                # 实时长度
        self.flag_x = 1             # x方向
        self.flag_y = 1             # y方向

        # 被攻击动画相关参数
        self.state = 0              # 状态 0普通状态 1被攻击状态 2攻击状态 3技能释放状态
        self.move_len = 10          # 被攻击后退距离
        self.attacked_dir = -1      # 移动方向 -1后退 1前进
        self.current_len = 0        # 已移动长度

        # 技能动画相关
        self.skill_time = 0.5                                 # 显示多久
        self.skill_count = int(g.fps * self.skill_time)     # 需要经过多少帧
        self.skill_counter = 0                              # 计数过了多少帧
        self.skill_alpha = 255                              # 不透明度 
        self.skill_x = None
        self.skill_y = None
        if self.skill:
            self.skill_name = self.skill['name']
        else:
            self.skill_name = ''

    def start_attack(self, d_x, d_y):
        """
        开始攻击
        """
        if self.state != 0:
            return
        self.length = math.sqrt((d_x - self.box_x - 60) ** 2 + (d_y - self.box_y - 30) ** 2)
        self.sin = abs(self.box_y - d_y) / self.length
        self.cos = abs(self.box_x - d_x) / self.length
        self.l = self.length / (self.speed * g.fps)
        self.flag_x = (d_x - self.box_x) / abs(d_x - self.box_x) if abs(d_x - self.box_x) != 0 else 1
        self.flag_y = (d_y - self.box_y) / abs(d_y - self.box_y) if abs(d_y - self.box_y) != 0 else 1
        self.state = 2

    def logic(self):
        """
        处理动画逻辑
        """
        self.attack_logic()
        self.be_attack_logic()
        self.skill_logic()

    def attack(self, target):
        """
        普通攻击
        """
        # 实际暴击率
        cri = self.cri - target.rcri
        if cri < 0:
            cri = 0
        is_cri = random.randint(1, 10000) <= cri
        if target.dfs >= self.atk:
            damage = random.randint(1, 10)  # 攻击力小于对方防御力时，伤害为1~10
        else:
            t = self.atk - target.dfs
            damage = t + random.randint(int(-t / 10), int(t / 10))  # 攻击伤害有10%的波动
        # 暴击伤害翻倍
        if is_cri:
            damage *= 2

        target.hp[0] -= damage

        return is_cri, damage

    def do_skill(self, peer_fighters):
        """
        释放技能，服务端逻辑
        """
        result = {
            'type': self.skill['type'],
            'name': self.skill['name'],
            'data': []
        }
        if self.skill['type'] == 'AOE':  # 群体攻击技能
            for target in peer_fighters:
                if target is None:
                    continue
                is_cri, damage = self.attack(target)    # TODO:攻击加成
                result['data'].append({
                    'is_cri': is_cri,
                    'damage': damage,
                    'target_index': target.index
                })
            # TODO:增益，减益
        return result

    def skill_play(self, data):
        """
        播放技能动画
        """
        self.skill_x = self.box_x + 70
        self.skill_y = self.box_y
        self.current_data = data
        self.state = 3

    def aoe(self):
        """
        aoe技能释放
        """
        for d in self.current_data['data']['data']:
            if self.team_type==1:
                target=g.fight_mgr.render_enemies[d['target_index']]
            else:
                target=g.fight_mgr.render_teammates[d['target_index']]
            target.be_attack(d)

    def skill_logic(self):
        """
        播放技能动画逻辑
        """
        if self.state != 3:
            return

        if self.skill_counter == 0:
            self.aoe()
        
        self.skill_counter += 1

        if self.skill_counter >= self.skill_count:
            self.state = 0
            self.skill_counter = 0
            # 弹出第一个
            g.fight_mgr.fight_result.pop(0)

    def play(self, target, data):
        """
        播放动画
        """
        # 处理两边攻击位置的偏移量
        if self.box_x < target.box_x:
            dx = target.box_x - 70
        else:
            dx = target.box_x + 70
        dy = target.box_y

        self.target = target
        self.current_data = data

        self.start_attack(dx, dy)

    def be_attack(self, data):
        """
        被攻击回调
        """
        self.state = 1
        self.hp[0] -= data['damage']
        if self.hp[0] < 0:
            self.hp[0] = 0
        # 显示扣血动画
        if data['is_cri']:
            t = 'cri'
        else:
            t = 'attack'
        g.fight_mgr.damage_list.append(DamageAnimation(t, data['damage'], self.box_x + 60, self.box_y))

    def attack_logic(self):
        """
        攻击动画逻辑
        """
        if self.state != 2:
            return

        if self.move_dir == 1:  # 正向移动
            self.d_l += self.l
            self.x = self.box_x + self.flag_x * self.d_l * self.cos
            self.y = self.box_y + self.flag_y * self.d_l * self.sin

            if self.d_l >= self.length:
                self.d_l = self.length
                self.move_dir = 3 - self.move_dir
                self.target.be_attack(self.current_data)

        else:  # 反向移动
            self.d_l -= self.l
            self.x = self.box_x + self.flag_x * self.d_l * self.cos
            self.y = self.box_y + self.flag_y * self.d_l * self.sin

            if self.d_l <= 0:
                self.d_l = 0
                self.move_dir = 3 - self.move_dir
                self.state = 0
                self.x = self.box_x
                self.y = self.box_y
                # 弹出第一个
                g.fight_mgr.fight_result.pop(0)

    def be_attack_logic(self):
        """
        被攻击的动画逻辑
        """
        if self.state != 1:
            return
        if self.team_type == 1:
            self.x += self.attacked_dir
        else:
            self.x -= self.attacked_dir
        self.current_len += 1
        if self.current_len == self.move_len:
            self.current_len = 0
            self.attacked_dir *= -1
            if self.attacked_dir == -1:  # 回到初始状态-1就代表已经运动一个来回了
                self.state = 0
                self.x = self.box_x


class FightManager:
    """
    战斗管理器，用于创建战斗、处理战斗逻辑
    """
    total_round = 20  # 最多战斗20个回合，如果20回合内没分出胜负，那么就算输了

    def __init__(self):
        self.teammates = [None] * 6             # 我方阵营
        self.enemies = [None] * 6               # 敌方阵营
        self.render_teammates = [None] * 6      # 渲染用的列表
        self.render_enemies = [None] * 6        # 渲染用的列表
        self.fighting = False                   # 是否正在战斗
        self.fight_result = []                  # 战斗结果，根据战斗结果构建动画
        self.damage_list = []                   # 伤害动画列表

    def start(self, teammates, enemies):
        """
        开始新战斗
        """
        # 清空之前战斗遗留的数据
        self.fight_result = []

        self.teammates = [None] * 6
        self.enemies = [None] * 6

        self.render_teammates = [None] * 6
        self.render_enemies = [None] * 6

        # 装载本次战斗人员
        for fighter in teammates:
            self.teammates[fighter.index] = fighter
            self.render_teammates[fighter.index] = copy.deepcopy(fighter)
        for fighter in enemies:
            self.enemies[fighter.index] = fighter
            self.render_enemies[fighter.index] = copy.deepcopy(fighter)
        # 计算战斗结果
        self.calc_result()
        # 包装战斗数据
        self.wrap_fight_result()
        # 开始战斗（开始处理动画逻辑）
        self.fighting = True

    def stop(self):
        self.fighting = False

    def calc_result(self):
        """
        计算战斗结果
        """
        # 每个回合的逻辑
        for i in range(1, self.total_round + 1):
            # 遍历两边阵营
            for index in range(6):
                # 取当前战斗对象
                teammate = self.teammates[index]
                enemy = self.enemies[index]
                # 判断谁先出手
                if teammate is None and enemy is None:
                    continue
                if teammate is not None and enemy is not None:
                    if teammate.level >= enemy.level:
                        # 队友攻击逻辑
                        self.attack(i, 1, teammate, self.enemies)
                        # 敌人攻击逻辑
                        self.attack(i, 2, enemy, self.teammates)
                    else:
                        # 敌人攻击逻辑
                        self.attack(i, 2, enemy, self.teammates)
                        # 队友攻击逻辑
                        self.attack(i, 1, teammate, self.enemies)
                elif teammate is not None:
                    # 队友攻击逻辑
                    self.attack(i, 1, teammate, self.enemies)
                else:
                    # 敌人攻击逻辑
                    self.attack(i, 2, enemy, self.teammates)

            # TODO:判断战斗是否结束，看看哪边阵营全是空
            if not any(self.teammates):
                # TODO:我方失败
                break
            if not any(self.enemies):
                # TODO:敌方失败
                break

    def attack(self, round, team_type, fighter, peer_fighters):
        """
        攻击，根据fighter的技能、回合数round进行策略选择
        攻击逻辑：
            1.触发身上所有buff
            2.触发身上所有debuff
            3.当前回合可以触发技能时，释放技能
            4.不可以触发技能时，普通攻击
        """
        if fighter.hp[0] <= 0:
            return
        
        # 释放技能
        if fighter.skill is not None and round in fighter.skill['round']:
            result = fighter.do_skill(peer_fighters)
            self.fight_result.append({
                'type': 'skill',
                'team_type': team_type,  # 阵营 1我方 2敌方
                'self_index': fighter.index,
                'data': result
            })
            return
        # 普通攻击
        for peer_fighter in peer_fighters:
            if peer_fighter is not None:
                is_cri, damage = fighter.attack(peer_fighter)  # 普通攻击
                if peer_fighter.hp[0] <= 0:
                    peer_fighter.hp[0] = 0
                    peer_fighters[peer_fighter.index] = None
                self.fight_result.append({
                    'type': 'attack',
                    'team_type': team_type,  # 阵营 1我方 2敌方
                    'self_index': fighter.index,
                    'target_index': peer_fighter.index,
                    'damage': damage,
                    'is_cri': is_cri
                })
                break

    def wrap_fight_result(self):
        """
        包装一层战斗数据（初始化）
        """
        for obj in self.fight_result:
            obj['process'] = 0  # 进度 0未开始 1进行中 2结束

    def logic(self):
        """
        战斗逻辑
        """
        self.damage_logic()

        if not self.fighting:
            return

        if len(self.fight_result) == 0:
            self.fighting = False
            return

        first_data = self.fight_result[0]
        team_list = [None, self.render_teammates, self.render_enemies]
        if first_data['process'] == 0:  # 让第一位进入战斗状态
            first_data['process'] = 1
            source = team_list[first_data['team_type']][first_data['self_index']]
            if first_data['type'] == 'attack':  # 普通攻击
                target = team_list[3 - first_data['team_type']][first_data['target_index']]
                source.play(target, first_data)
            elif first_data['type'] == 'skill':  # 技能攻击
                source.skill_play(first_data)

        for fighter in self.render_teammates:
            if fighter is None:
                continue
            fighter.logic()
        for fighter in self.render_enemies:
            if fighter is None:
                continue
            fighter.logic()

    def damage_logic(self):
        for damage in self.damage_list[::-1]:
            if damage.done:
                self.damage_list.remove(damage)
                continue
            damage.logic()

    def render(self):
        """
        渲染战斗系统
        """
        Sprite.blit(g.screen, g.bg_battle, 10, 50)

        for fighter in self.render_teammates:
            if fighter is None:
                continue
            self.draw_hero(fighter)

        for fighter in self.render_enemies:
            if fighter is None:
                continue
            self.draw_hero(fighter)

        # 画伤害
        for damage in self.damage_list:
            damage.render()

    def draw_hero(self, fighter):
        """
        绘制英雄
        """
        box_x = fighter.x
        box_y = fighter.y
        # 绘制边框
        if fighter.state in [0,2,3]:
            Sprite.blit(g.screen, g.bg_hero_1, box_x, box_y)
        elif fighter.state in [1]:
            Sprite.blit(g.screen, g.bg_hero_2, box_x, box_y)
        # 绘制血量
        hp_percent = fighter.hp[0] / fighter.hp[1]
        Sprite.blit_w(g.screen, g.hp_bar, box_x + 2, box_y + 45, hp_percent)
        # 绘制能量
        Sprite.blit(g.screen, g.mp_bar, box_x + 2, box_y + 59)
        # 绘制血、能量边框
        Sprite.blit(g.screen, g.bg_hero_hp, box_x + 2, box_y + 45)
        # 绘制血量数值
        draw_outline_text(g.screen, box_x + 2 + 60, box_y + 45, str(fighter.hp[0]), g.fnt_hp, (255, 255, 255),
                          (0, 0, 0))
        # 绘制名字
        draw_outline_text(g.screen, box_x + 2 + 60, box_y + 10, fighter.name, g.fnt_battle_name, (255, 0, 0), (0, 0, 0))
        # 绘制技能名 # TODO:技能名称绘制，这里逻辑肯定要改
        if fighter.state == 3:
            draw_outline_text(g.screen, fighter.skill_x, fighter.skill_y-20, fighter.skill_name, g.fnt_battle_name,
                              (255, 0, 0), (0, 0, 0))


class DamageAnimation:
    """
    伤害动画
    """

    def __init__(self, ani_type, number, x, y):
        """
        构造伤害动画
        ani_type: 伤害类型：attack普通攻击 cri暴击 heal加血 poison中毒
        """
        width = 0
        height = 0

        self.surface = None
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
        self.current_length = 0                 # 当前移动长度
        self.time = 0.5                         # 伤害显示出来之后暂停多久
        self.count = int(g.fps * self.time)     # 1秒需要经过多少帧
        self.counter = 0                        # 计数过了多少帧
        self.alpha = 255                        # 不透明度 

    def render(self):
        """
        绘制
        """
        if self.done:
            return
        # Sprite.blit(g.screen, self.surface, self.x, self.y)
        Sprite.blit_alpha(g.screen, self.surface, self.x, self.y, self.alpha)

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
