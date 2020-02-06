import pygame

from code.engine.animation import Animation
from code.engine.sprite import Sprite
from code.game_global import g


class Walker:
    """
    行走者，8个方向的行走图
    """
    config = {
        0: [56, 96]
    }

    def __init__(self, walker_id, mx, my):
        """
        mx:人物在地图小格子里的坐标
        my:人物在地图小格子里的坐标
        """
        self.mx = mx
        self.my = my
        self.x = mx * 16
        self.y = my * 16
        # 根据walker_id获取不同的cell_w,cell_h的参数
        self.cell_w = self.config[walker_id][0]
        self.cell_h = self.config[walker_id][1]
        # 渲染坐标
        self.render_x = int(self.x - self.cell_w / 2)
        self.render_y = self.y - self.cell_h
        # 加载动画
        self.walker_img = pygame.image.load(f'./resource/PicLib/all_char/{walker_id}.png').convert_alpha()
        self.animations = []
        for i in range(8):
            animation = Animation(self.render_x, self.render_y, self.walker_img, self.cell_w, self.cell_h, 1000, True,
                                  [9 * i, 9 * (i + 1) - 1])
            self.animations.append(animation)
        # 初始化面向
        self.face = 0  # 0上 1下 2左 3右 4上左 5下右 6下左 7上右
        self.walking = False  # false静止状态 true行走状态
        # 角色下一步需要去的格子
        self.next_mx = 0
        self.next_my = 0
        self.step = 2  # 每帧移动的像素
        # 寻路路径
        self.path = []
        # 当前路径下标
        self.path_index = 0

    def logic(self):
        if not self.walking:
            return
        # 更新动画
        self.animations[self.face].update()
        # 移动
        self.move()

    def render(self):
        """
        渲染行走者
        """
        if self.walking:
            self.animations[self.face].draw_src(g.screen, self.render_x, self.render_y)
        else:
            Sprite.draw(g.screen, self.walker_img, self.render_x, self.render_y, 0, self.face, 56, 96)

    def goto(self, mx, my):
        """
        :param mx: 地图小格子中的目标点
        :param my: 地图小格子中的目标点
        """
        self.next_mx = mx
        self.next_my = my

        self.walking = True
        # 设置人物面向
        if self.next_mx == self.mx and self.next_my < self.my:  # 上
            self.face = 0
        elif self.next_mx == self.mx and self.next_my > self.my:  # 下
            self.face = 1
        elif self.next_mx < self.mx and self.next_my == self.my:  # 左
            self.face = 2
        elif self.next_mx > self.mx and self.next_my == self.my:  # 右
            self.face = 3
        elif self.next_mx < self.mx and self.next_my < self.my:  # 上左
            self.face = 4
        elif self.next_mx > self.mx and self.next_my > self.my:  # 下右
            self.face = 5
        elif self.next_mx < self.mx and self.next_my > self.my:  # 下左
            self.face = 6
        elif self.next_mx > self.mx and self.next_my < self.my:  # 上右
            self.face = 7
        else:
            self.walking = False

    def move(self):
        dest_x = self.next_mx * 16
        dest_y = self.next_my * 16

        # 向目标位置靠近
        if self.x < dest_x:
            self.x += self.step
            if self.x >= dest_x:
                self.x = dest_x
        elif self.x > dest_x:
            self.x -= self.step
            if self.x <= dest_x:
                self.x = dest_x

        if self.y < dest_y:
            self.y += self.step
            if self.y >= dest_y:
                self.y = dest_y
        elif self.y > dest_y:
            self.y -= self.step
            if self.y <= dest_y:
                self.y = dest_y

        # 更新渲染坐标
        self.render_x = int(self.x - self.cell_w / 2)
        self.render_y = self.y - self.cell_h

        # 角色当前位置
        self.mx = int(self.x / 16)
        self.my = int(self.y / 16)

        # 到达了目标点
        if self.x == dest_x and self.y == dest_y:
            self.walking = False
