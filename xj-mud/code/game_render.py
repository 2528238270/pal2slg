import pygame

from code.engine.sprite import Sprite, draw_text, draw_outline_text
from code.game_global import g


def __draw_hero(fighter):
    """
    绘制英雄
    """
    box_x = fighter.x
    box_y = fighter.y
    # 绘制边框
    if fighter.state == 0:
        Sprite.blit(g.screen, g.bg_hero_1, box_x, box_y)
    elif fighter.state == 1:
        Sprite.blit(g.screen, g.bg_hero_2, box_x, box_y)
    # 绘制血量
    hp_percent = fighter.hp[0] / fighter.hp[1]
    Sprite.blit_w(g.screen, g.hp_bar, box_x + 2, box_y + 45, hp_percent)
    # 绘制能量
    Sprite.blit(g.screen, g.mp_bar, box_x + 2, box_y + 59)
    # 绘制血、能量边框
    Sprite.blit(g.screen, g.bg_hero_hp, box_x + 2, box_y + 45)
    # 绘制血量数值
    draw_outline_text(g.screen, box_x + 2 + 60, box_y + 45, str(fighter.hp[0]), g.fnt_hp, (255, 255, 255), (0, 0, 0))
    # 绘制名字
    draw_outline_text(g.screen, box_x + 2 + 60, box_y + 10, fighter.name, g.fnt_battle_name, (255, 0, 0), (0, 0, 0))


def draw_battle():
    """
    绘制战斗场景
    """
    Sprite.blit(g.screen, g.bg_battle, 10, 50)

    for fighter in g.battle_data["teammates"]:
        __draw_hero(fighter)

    for fighter in g.battle_data["enemies"]:
        __draw_hero(fighter)
