"""
镜头管理系统，主要作用是在触发剧情时，移动镜头
create by 狡猾的皮球
qq:871245007
2020年2月12日 14:35:35
"""


class CameraManager:
    """
    游戏镜头管理器
    """

    def __init__(self, game_map, walker):
        """
        game_map:游戏地图对象
        walker:行走者
        """
        self.game_map = game_map
        self.lock_role = True  # 是否锁定镜头
        self.walker = walker  # 锁定镜头的主角
        self.moving = False  # 镜头是否正在移动
        self.step = 4  # 镜头每帧移动的像素
        # 镜头移动的目标坐标
        self.target_x = 0
        self.target_y = 0
        # 移动完成后的回调
        self.callback = None
        self.args = []

    def move(self, x, y, callback=None, args=None):
        """
        镜头移动到目标位置
        x,y:地图坐标系的像素坐标
        """
        if self.moving:  # 正在移动
            return
        self.lock_role = False
        self.target_x, self.target_y = self.game_map.calc_roll_pos(x, y)
        print(self.target_x,self.target_y)
        self.moving = True
        self.callback = callback
        if args is not None:
            self.args = args

    def logic(self):
        """
        镜头管理逻辑
        """
        # 如果当前是锁定主角状态，直接调用地图滚动逻辑
        if self.lock_role and self.walker is not None:
            self.game_map.roll(self.walker.render_x, self.walker.render_y)
            return

        if not self.moving:
            return

        if self.game_map.x > self.target_x:
            self.game_map.x -= self.step
            if self.game_map.x < self.target_x:
                self.game_map.x = self.target_x
        elif self.game_map.x < self.target_x:
            self.game_map.x += self.step
            if self.game_map.x > self.target_x:
                self.game_map.x = self.target_x

        if self.game_map.y > self.target_y:
            self.game_map.y -= self.step
            if self.game_map.y < self.target_y:
                self.game_map.y = self.target_y
        elif self.game_map.y < self.target_y:
            self.game_map.y += self.step
            if self.game_map.y > self.target_y:
                self.game_map.y = self.target_y

        if self.game_map.x == self.target_x and self.game_map.y == self.target_y:
            self.moving = False
            if self.callback:
                self.callback(*self.args)

    def unlock(self, x, y):
        """
        解除镜头锁定并且直接移动镜头到指定位置
        """
        self.lock_role = False
        self.moving = False
        map_x, map_y = self.game_map.calc_roll_pos(x*16, y*16)
        self.game_map.x = map_x
        self.game_map.y = map_y
        print(x, y)
        print(map_x, map_y)

    def lock(self, walker):
        """
        锁定视角到指定walker上，镜头直接移动到指定walker
        """
        self.lock_role = True  # 是否锁定镜头
        self.walker = walker  # 锁定镜头的主角
        self.moving = False  # 镜头是否正在移动

    def move_m_pos(self, mx, my, callback=None, args=None):
        """
        镜头移动到目标位置（mx,my是小格子的坐标，不是像素坐标）
        """
        x = mx * 16
        y = my * 16
        self.move(x, y, callback, args)
