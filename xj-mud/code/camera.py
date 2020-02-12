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
        """
        if self.moving:  # 正在移动
            return
        self.lock_role = False
        self.target_x, self.target_y = self.game_map.calc_roll_pos(x, y)
        self.moving = True
        self.callback = callback
        if args is not None:
            self.args = args

    def logic(self):
        """
        镜头管理逻辑
        """
        # 如果当前是锁定主角状态，直接调用地图滚动逻辑
        if self.lock_role:
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
