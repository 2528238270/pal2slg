import sys
import json

import pygame

from code.engine.sprite import Sprite
from code.game_global import g
from code.fighter import Fighter, FightManager, DamageAnimation


class Game:
    def __init__(self, title, width, height, fps=60):
        """
        :param title: 游戏窗口的标题
        :param width: 游戏窗口的宽度
        :param height: 游戏窗口的高度
        :param fps: 游戏每秒刷新次数
        """
        self.title = title
        self.width = width
        self.height = height
        self.screen = None
        self.fps = fps
        self.__init_pygame()
        self.__init_game()
        self.update()

    def __init_pygame(self):
        pygame.init()
        pygame.display.set_caption(self.title)
        self.screen = pygame.display.set_mode([self.width, self.height])
        self.clock = pygame.time.Clock()

    def __init_game(self):
        g.fps = self.fps
        g.fnt_hp = pygame.font.Font('./resource/font/font1.TTF', 16)
        g.fnt_battle_name = pygame.font.Font('./resource/font/font1.TTF', 24)
        g.bg = pygame.image.load('./resource/dazhuzai/login_bg_60b2432a.png').convert_alpha()
        g.bg_title = pygame.image.load('./resource/dazhuzai/hero_res_1021_c4e8972d.png').convert_alpha()
        g.bg_battle = pygame.image.load('./resource/dazhuzai/hero_res_battle_bg.png').convert_alpha()
        g.bg_hero_1 = pygame.image.load('./resource/dazhuzai/bg_hero_1.png').convert_alpha()
        g.bg_hero_2 = pygame.image.load('./resource/dazhuzai/bg_hero_2.png').convert_alpha()
        g.bg_hero_hp = pygame.image.load('./resource/dazhuzai/bg_hero_hp.png').convert_alpha()
        g.hp_bar = pygame.image.load('./resource/dazhuzai/hp_bar.png').convert_alpha()
        g.mp_bar = pygame.image.load('./resource/dazhuzai/mp_bar.png').convert_alpha()
        g.ry_fnt = pygame.image.load('./resource/font/ryFont_5a94031e.png').convert_alpha()
        with open('./resource/font/ryFont_f695d33e.fnt', mode='r', encoding='utf8') as file:
            g.ry_fnt_data = json.loads(file.read())
        print(g.ry_fnt_data)
        g.fight_mgr = FightManager()
        g.screen = self.screen
        g.battle_data['teammates'] = [
            Fighter(0, 1, '李逍遥', 1, [1000, 1000], 99999, 100, 10000, 8000, 0, 0),
            Fighter(1, 1, '赵灵儿', 2, [800, 800], 50, 10, 10000, 2000, 0, 0),
            Fighter(2, 1, '林月如', 3, [850, 850], 50, 10, 10000, 2000, 0, 0),
            Fighter(4, 1, '阿奴', 4, [800, 800], 50, 10, 10000, 2000, 0, 0)
        ]
        g.battle_data['enemies'] = [
            Fighter(0, 2, '拜月教主', 1, [30000, 30000], 40, 1, 10000, 2000, 0, 0),
            Fighter(1, 2, '石长老', 1, [10000, 10000], 20, 1, 10000, 2000, 0, 0),
            Fighter(2, 2, '水魔兽', 1, [50000, 50000], 30, 1, 10000, 2000, 0, 0),
            # Fighter(3,2,'赵日天13',1,[100,100],10,1,10000,2000,0,0),
            # Fighter(4,2,'赵日天13',1,[100,100],10,1,10000,2000,0,0),
            # Fighter(5,2,'赵日天13',1,[100,100],10,1,10000,2000,0,0),
        ]
        g.fight_mgr.start(g.battle_data['teammates'], g.battle_data['enemies'])

    def update(self):
        while True:
            self.clock.tick(self.fps)
            # 逻辑更新
            self.event_handler()
            g.fight_mgr.logic()
            # 画面更新
            Sprite.blit(g.screen, g.bg, 0, 0)
            Sprite.blit(g.screen, g.bg_title, 0, 0)
            g.fight_mgr.render()
            pygame.display.update()

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()


if __name__ == '__main__':
    # Game("仙剑", 640, 900)
    Game("仙剑", 1, 1)
