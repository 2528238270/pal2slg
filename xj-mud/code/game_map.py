import pygame

from code.engine.common import Array2D


class GameMap:
    """
    游戏地图
    """

    def __init__(self):
        self.btm_img = None  # 地图背景图片
        self.top_img = None  # 地图遮挡层图片
        self.walk_data = None  # 行走层数据
        self.redraw_data = None  # 重绘层数据
        self.enter_point = None  # 地图切换点
        self.w = 0  # 地图的长宽，16*16为一个单位
        self.h = 0
        self.size_w = 0
        self.size_h = 0
        self.x = 0  # 绘图坐标
        self.y = 0
        # self.npc_list = []  # npc列表

    def load(self, map_id):
        """
        加载地图
        """
        self.btm_img = pygame.image.load(f'./resource/PicLib/all_map/{map_id}-1.jpg')
        self.top_img = pygame.image.load(f'./resource/PicLib/all_map/{map_id}-2.png').convert_alpha()
        self.w = int(self.btm_img.get_width() / 16) + 2
        self.h = int(self.btm_img.get_height() / 16) + 2
        self.size_w = self.btm_img.get_width()
        self.size_h = self.btm_img.get_height()
        self.walk_data = Array2D(self.w, self.h)
        self.redraw_data = Array2D(self.w, self.h)
        self.enter_point = Array2D(self.w, self.h)

        with open(f'./resource/PicLib/all_map/{map_id}.Walkmap') as file:
            for x in range(self.w):
                for y in range(self.h):
                    self.walk_data[x][y] = int(file.readline())

        with open(f'./resource/PicLib/all_map/{map_id}.Redrawmap') as file:
            for x in range(self.w):
                for y in range(self.h):
                    self.redraw_data[x][y] = int(file.readline())

        with open(f'./resource/PicLib/all_map/{map_id}.Enterpos', mode='rb') as file:
            data = file.read()
            for i in range(0, len(data), 12):
                chunk = data[i:i + 12]
                x = int.from_bytes(chunk[0:4], 'little')
                y = int.from_bytes(chunk[4:8], 'little')
                v = int.from_bytes(chunk[8:12], 'little')
                self.enter_point[x][y] = v
        pygame.mixer.music.load(f'./resource/music/map{map_id}.mp3')
        pygame.mixer.music.play(-1)

    def roll(self, role_x, role_y, win_width=640, win_height=480):
        """
        地图滚动
        :param role_x: 角色相对于地图的坐标
        :param role_y:
        """
        if role_x < win_width / 2:
            self.x = 0
        elif role_x > self.size_w - win_width / 2:
            self.x = -(self.size_w - win_width)
        else:
            self.x = -(role_x - win_width / 2)

        if role_y < win_height / 2:
            self.y = 0
        elif role_y > self.size_h - win_height / 2:
            self.y = -(self.size_h - win_height)
        else:
            self.y = -(role_y - win_height / 2)

    def calc_roll_pos(self, x, y, win_width=640, win_height=480):
        """
        计算镜头移动到目标点后地图坐标
        """
        if x < win_width / 2:
            map_x = 0
        elif x > self.size_w - win_width / 2:
            map_x = -(self.size_w - win_width)
        else:
            map_x = -(x - win_width / 2)

        if y < win_height / 2:
            map_y = 0
        elif y > self.size_h - win_height / 2:
            map_y = -(self.size_h - win_height)
        else:
            map_y = -(y - win_height / 2)

        return map_x, map_y

    def unload(self):
        pass
