import pygame

from code.engine.a_star import AStar
from code.engine.animation import Animation
from code.engine.sprite import Sprite
from code.game_global import g


class Walker:
    """
    行走者，8个方向的行走图
    """
    config = {
        0: [56, 96, 6, 9],
        1: [40, 68, 6, 4],
        2: [36, 64, 6, 4]
    }

    def __init__(self, walker_id, mx, my, face=0):
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
        self.offset_y = self.config[walker_id][2]
        self.column = self.config[walker_id][3]
        # 渲染坐标
        self.render_x = int(self.x - self.cell_w / 2) + 8
        self.render_y = self.y - self.cell_h + self.offset_y + 16
        # 加载动画
        self.walker_img = pygame.image.load(f'./resource/PicLib/all_char/{walker_id}.png').convert_alpha()
        self.animations = []
        for i in range(8):
            animation = Animation(self.render_x, self.render_y, self.walker_img, self.cell_w, self.cell_h, 700, True,
                                  [self.column * i, self.column * (i + 1) - 1])
            self.animations.append(animation)
        # 初始化面向
        self.face = face  # 0上 1下 2左 3右 4上左 5下右 6下左 7上右
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
        # 更新动画
        if self.walking:
            self.animations[self.face].update()
        # 移动
        self.move()
        # 自动走下一步
        self.auto_goto()

    def render(self, map_x, map_y):
        """
        渲染行走者
        """
        render_x = map_x + self.render_x
        render_y = map_y + self.render_y
        if render_x < -self.cell_w or render_x > 640 or render_y < -self.cell_h or render_y > 480:
            """
            人物在屏幕外，不需要渲染
            """
            return

        if self.walking:
            self.animations[self.face].draw_src(g.screen, render_x, render_y)
        else:
            Sprite.draw(g.screen, self.walker_img, render_x, render_y, 0, self.face, self.cell_w, self.cell_h)

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
        if not self.walking:
            return
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
        self.render_x = int(self.x - self.cell_w / 2) + 8
        self.render_y = self.y - self.cell_h + self.offset_y + 16

        # 角色当前位置
        self.mx = int(self.x / 16)
        self.my = int(self.y / 16)

        # 到达了目标点
        if self.x == dest_x and self.y == dest_y:
            self.walking = False

    def find_path(self, map2d, end_point):
        """
        :param map2d: 地图
        :param end_point: 寻路终点
        """
        if end_point[0] == self.mx and end_point[1] == self.my:
            return

        start_point = (self.mx, self.my)
        path = AStar(map2d, start_point, end_point).start()
        if path is None:
            return

        self.path = path
        self.path_index = 0

    def auto_goto(self):
        """
        自动寻路
        """
        if self.walking:
            return
        # 如果寻路走到终点了
        if self.path_index == len(self.path):
            self.path = []
            self.path_index = 0
            # self.walking = False
        # 如果没走到终点，就往下一个格子走
        else:
            self.goto(self.path[self.path_index].x, self.path[self.path_index].y)
            self.path_index += 1
            # self.walking = True

    def set_point(self, mx, my):
        """
        设置位置
        """
        self.mx = mx
        self.my = my
        self.x = mx * 16
        self.y = my * 16
        # 渲染坐标
        self.render_x = int(self.x - self.cell_w / 2) + 8
        self.render_y = self.y - self.cell_h + self.offset_y + 16
