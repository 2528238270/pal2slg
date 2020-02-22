import sys
import json

import pygame

from code.audio import AudioPlayer
from code.engine.animation import Animator, Fade
from code.engine.scene import SceneManager
from code.engine.sprite import Sprite, draw_rect_text
from code.game_global import g, ENUM_SCENE
from code.fighter import Fighter, FightManager
from code.scenes import StartScene, GameScene
from code.talk import TalkManager
from code.walker import Walker


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
        g.fnt_magic_plane = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 20)
        g.fnt_magic_plane.set_bold(True)

        g.fnt_talk = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 16)
        g.ry_fnt = pygame.image.load('./resource/font/ryFont_5a94031e.png').convert_alpha()
        g.bg_enter = pygame.image.load('./resource/PicLib/all_sys/login.png').convert_alpha()
        g.btn1 = pygame.image.load('./resource/PicLib/all_sys/btn1.png').convert_alpha()
        g.btn2 = pygame.image.load('./resource/PicLib/all_sys/btn2.png').convert_alpha()
        g.btn3 = pygame.image.load('./resource/PicLib/all_sys/btn3.png').convert_alpha()
        g.btn4 = pygame.image.load('./resource/PicLib/all_sys/btn4.png').convert_alpha()
        g.btn5 = pygame.image.load('./resource/PicLib/all_sys/btn5.png').convert_alpha()
        g.btn6 = pygame.image.load('./resource/PicLib/all_sys/btn6.png').convert_alpha()
        g.sm_walk = pygame.image.load('./resource/PicLib/all_char/0.png').convert_alpha()
        # pygame.mixer.music.load('./resource/music/login.mp3')
        # pygame.mixer.music.play(-1)

        with open('./resource/font/ryFont_f695d33e.fnt', mode='r', encoding='utf8') as file:
            g.ry_fnt_data = json.loads(file.read())
        with open('./resource/skill.json', mode='r', encoding='utf8') as file:
            g.skill_data = json.loads(file.read())
        g.screen = self.screen
        g.fight_mgr = FightManager()
        g.scene_mgr = SceneManager()
        g.animator = Animator(self.screen)
        g.fade = Fade(self.screen)
        g.talk_mgr = TalkManager(self.screen)
        g.audio_player = AudioPlayer()
        g.scene_mgr.add(StartScene(ENUM_SCENE.START_SCENE))
        # g.scene_mgr.add(GameScene(ENUM_SCENE.GAME_SCENE))
        # g.animator.add(100, 100, g.sm_walk, 56, 96, 1000, True, [9, 17])
        # g.scene_id = ENUM_SCENE.GAME_SCENE
        g.scene_id = ENUM_SCENE.START_SCENE
        g.talk_mgr.start(0)
        g.audio_player.play_music('login', -1)

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
            g.talk_mgr.logic()
            g.talk_mgr.render()
            pygame.display.update()

    def event_handler(self):
        x, y = pygame.mouse.get_pos()
        scene = g.scene_mgr.find_scene_by_id(g.scene_id)
        for event in pygame.event.get():
            pressed = pygame.mouse.get_pressed()
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                scene.mouse_move(x, y)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                scene.mouse_down(x, y, pressed)
            elif event.type == pygame.MOUSEBUTTONUP:
                scene.mouse_up(x, y, pressed)


if __name__ == '__main__':
    Game("仙剑奇侠传二", 640, 480, 60)
    # Game("仙剑奇侠传二", 1024, 768, 60)

    # Game("仙剑", 1, 1)
