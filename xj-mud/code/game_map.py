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
                    self.walk_data[x][y] = int(file.readline())

        with open(f'./resource/PicLib/all_map/{map_id}.Enterpos', mode='rb') as file:
            data = file.read()
            for i in range(0, len(data), 12):
                chunk = data[i:i + 12]
                x = int.from_bytes(chunk[0:4], 'little')
                y = int.from_bytes(chunk[4:8], 'little')
                v = int.from_bytes(chunk[8:12], 'little')
                self.enter_point[x][y] = v

    def unload(self):
        pass
