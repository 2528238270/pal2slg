import sys
import json

import pygame

from code import scenes
from code.engine.animation import Animator, Fade
from code.engine.scene import SceneManager
from code.engine.sprite import Sprite
from code.game_global import g, ENUM_SCENE
from code.fighter import Fighter, FightManager
from code.game_map import GameMap
from code.scenes import StartScene


class Game:
    def __init__(self, title, width, height, fps=120):
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
        pygame.mixer.init()
        self.screen = pygame.display.set_mode([self.width, self.height])
        self.clock = pygame.time.Clock()

    def __init_game(self):
        g.fps = self.fps  # 设置fps
        # 加载所需资源
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
        g.bg_enter = pygame.image.load('./resource/PicLib/all_sys/login.png').convert_alpha()
        g.btn1 = pygame.image.load('./resource/PicLib/all_sys/btn1.png').convert_alpha()
        g.btn2 = pygame.image.load('./resource/PicLib/all_sys/btn2.png').convert_alpha()
        g.btn3 = pygame.image.load('./resource/PicLib/all_sys/btn3.png').convert_alpha()
        g.btn4 = pygame.image.load('./resource/PicLib/all_sys/btn4.png').convert_alpha()
        g.btn5 = pygame.image.load('./resource/PicLib/all_sys/btn5.png').convert_alpha()
        g.btn6 = pygame.image.load('./resource/PicLib/all_sys/btn6.png').convert_alpha()
        g.sm_walk = pygame.image.load('./resource/PicLib/all_char/0.png').convert_alpha()
        pygame.mixer.music.load('./resource/music/login.mp3')
        pygame.mixer.music.play(-1)
        with open('./resource/font/ryFont_f695d33e.fnt', mode='r', encoding='utf8') as file:
            g.ry_fnt_data = json.loads(file.read())
        with open('./resource/skill.json', mode='r', encoding='utf8') as file:
            g.skill_data = json.loads(file.read())
        g.screen = self.screen
        g.fight_mgr = FightManager()
        g.scene_mgr = SceneManager()
        g.animator = Animator(self.screen)
        g.fade = Fade(self.screen)
        g.scene_mgr.add(StartScene(ENUM_SCENE.START_SCENE))
        g.animator.add(100, 100, g.sm_walk, 56, 96, 1000, True, [9, 17])
        g.scene_id = ENUM_SCENE.START_SCENE
        # g.game_map = GameMap()
        # g.game_map.load(1)
        # g.game_map.enter_point.debug_show()
        # g.battle_data['teammates'] = [
        #     Fighter(1, 1, '沈欺霜', 1, [999, 999], 1000, 10, 10000, 8000, 0, 0),
        #     Fighter(2, 1, '王小虎', 2, [999, 999], 1500, 10, 10000, 2000, 0, 0, 1),
        #     Fighter(0, 1, '苏媚', 3, [999, 999], 1500, 10, 10000, 2000, 0, 0, 4),
        #     Fighter(4, 1, '李忆如', 4, [999, 999], 800, 10, 10000, 2000, 0, 0, 4),
        # ]
        # g.battle_data['enemies'] = [
        #     Fighter(1, 2, '千叶禅师', 1, [99999, 99999], 40, 1, 10000, 2000, 0, 0),
        #     Fighter(2, 2, '喻南松', 1, [20000, 20000], 20, 1, 10000, 2000, 0, 0),
        # ]
        # g.fight_mgr.start(g.battle_data['teammates'], g.battle_data['enemies'])

    def update(self):
        while True:
            self.clock.tick(self.fps)
            scene = g.scene_mgr.find_scene_by_id(g.scene_id)
            g.fade.logic()
            self.event_handler()
            g.animator.update()
            scene.logic()
            scene.render()
            g.animator.draw()
            g.fade.draw()
            # if g.scene_id == ENUM_SCENE.START_SCENE:
            #     scenes.logic()
            #     self.event_handler()
            #     scenes.render()
            # elif g.scene_id == ENUM_SCENE.GAME_SCENE:
            #     # 逻辑更新
            #     g.fight_mgr.logic()
            #     # 画面更新
            #     Sprite.blit(g.screen, g.bg, 0, 0)
            #     Sprite.blit(g.screen, g.bg_title, 0, 0)
            #     g.fight_mgr.render()

            pygame.display.update()

    def event_handler(self):
        x, y = pygame.mouse.get_pos()
        scene = g.scene_mgr.find_scene_by_id(g.scene_id)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                scene.mouse_move(x, y)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                scene.mouse_down(x, y)
            elif event.type == pygame.MOUSEBUTTONUP:
                scene.mouse_up(x, y)


if __name__ == '__main__':
    Game("仙剑奇侠传二", 640, 480, 60)
    # Game("仙剑", 1, 1)
