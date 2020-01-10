import sys

import pygame

from code.engine.sprite import Sprite


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
        self.image = pygame.image.load('./resource/font/ryFont_5a94031e.png').convert_alpha()
        # self.image=self.image.convert()
        # self.image.set_alpha(100)

    def update(self):
        while True:
            self.clock.tick(self.fps)
            self.screen.fill((255, 255, 255))
            # 逻辑更新
            self.event_handler()
            # 画面更新
            # self.screen.blit(self.image, (0, 0))
            Sprite.blit_alpha(self.screen, self.image, 0, 0, 255)
            Sprite.blit_alpha(self.screen, self.image, 0, 200, 100)
            pygame.display.update()

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()


if __name__ == '__main__':
    # Game("仙剑", 640, 900)
    Game("仙剑", 320, 500)
