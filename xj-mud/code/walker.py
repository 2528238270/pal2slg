import pygame

from code.engine.animation import Animation
from code.engine.sprite import Sprite
from code.game_global import g


class Walker:
    """
    行走者，8个方向的行走图
    """

    def __init__(self, walker_id, x, y):
        """
        x:人物脚下坐标(不是左上角坐标)
        y:人物脚下坐标(不是左上角坐标)
        """
        self.x = x
        self.y = y
        # TODO:根据walker_id获取不同的cell_w,cell_h的参数
        self.render_x = int(x - 56 / 2)
        self.render_y = y - 96
        self.walker_img = pygame.image.load(f'./resource/PicLib/all_char/{walker_id}.png').convert_alpha()
        self.animations = []
        for i in range(8):
            animation = Animation(self.render_x, self.render_y, self.walker_img, 56, 96, 1000, True,
                                  [9 * i, 9 * (i + 1) - 1])
            self.animations.append(animation)
        self.face = 0  # 0上 1下 2左 3右 4上左 5下右 6下左 7上右
        self.walking = False  # false静止状态 true行走状态

    def logic(self):
        if self.walking:
            self.animations[self.face].update()

    def render(self):
        """
        渲染行走者
        """
        if self.walking:
            self.animations[self.face].draw_src(g.screen, self.render_x, self.render_y)
        else:
            Sprite.draw(g.screen, self.walker_img, self.render_x, self.render_y, self.face, 0, 56, 96)
