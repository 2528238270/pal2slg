import cv2

# 游戏开始场景
import pygame

from code.engine.gui import Button
from code.engine.scene import Scene
from code.engine.sprite import Sprite
from code.game_global import g, ENUM_SCENE
from code.game_map import GameMap
from code.walker import Walker


class StartScene(Scene):
    def __init__(self, scene_id):
        super().__init__(scene_id=scene_id)
        self.video_state = 1  # 0开场动画没放完 1开场动画放完了 2正在播放循环动画
        self.video1 = []
        self.video1_speed = 0
        self.video2 = []
        self.video2_speed = 0
        self.count = 0
        self.bg = None
        # 创建按钮
        self.btn_new_game = Button(230, 270, imgNormal=g.btn1, imgMove=g.btn2, callBackFunc=self.new_game)
        self.btn_old_game = Button(230, 320, imgNormal=g.btn3, imgMove=g.btn4, callBackFunc=g.fade.start)
        self.btn_exit_game = Button(230, 370, imgNormal=g.btn5, imgMove=g.btn6, callBackFunc=g.fade.start)

        cap1 = cv2.VideoCapture("./resource/Video/StartMenu.avi")
        cap2 = cv2.VideoCapture("./resource/Video/MenuLoop.avi")

        while cap1.isOpened():
            ret, frame = cap1.read()
            if ret:
                self.video1.append(cv2.transpose(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            else:
                break
        cap1.release()

        while cap2.isOpened():
            ret, frame = cap2.read()
            if ret:
                self.video2.append(cv2.transpose(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            else:
                break
        cap2.release()

        self.video1_speed = 1 / (11 / len(self.video1) * g.fps)
        self.video2_speed = 1 / (15 / len(self.video2) * g.fps)

    def logic(self):
        """
        开始界面逻辑
        """
        if g.scene_id != self.scene_id:  # 在切换场景时，会有一帧用上一次的场景，所以一定要判断一下当前场景值是不是正确的
            return

        if self.video_state == 0:
            self.count += self.video1_speed
            if int(self.count) >= len(self.video1):
                self.video_state = 1
                self.count = 0
            else:
                self.bg = self.video1[int(self.count)]

        if self.video_state == 1:
            self.count += self.video2_speed
            if int(self.count) >= len(self.video2):
                self.count = 0
            self.bg = self.video2[int(self.count)]

    def render(self):
        """
        渲染
        """
        if g.scene_id != self.scene_id:  # 在切换场景时，会有一帧用上一次的场景，所以一定要判断一下当前场景值是不是正确的
            return

        # 播放背景视频
        pygame.surfarray.blit_array(g.screen, self.bg)
        # 绘制背景、按钮
        if self.video_state == 1:
            Sprite.blit(g.screen, g.bg_enter, 0, 0)
            self.btn_new_game.draw(g.screen)
            self.btn_old_game.draw(g.screen)
            self.btn_exit_game.draw(g.screen)

    def mouse_down(self, x, y):
        self.btn_new_game.mouse_down(x, y)
        self.btn_old_game.mouse_down(x, y)
        self.btn_exit_game.mouse_down(x, y)

    def mouse_up(self, x, y):
        self.btn_new_game.mouse_up()
        self.btn_old_game.mouse_up()
        self.btn_exit_game.mouse_up()

    def mouse_move(self, x, y):
        self.btn_new_game.get_focus(x, y)
        self.btn_old_game.get_focus(x, y)
        self.btn_exit_game.get_focus(x, y)

    def new_game(self):
        """
        开始新游戏
        """

        def temp():
            g.scene_mgr.add(GameScene(ENUM_SCENE.GAME_SCENE))
            g.scene_id = ENUM_SCENE.GAME_SCENE
            # 释放视频内存
            start_scene = g.scene_mgr.find_scene_by_id(ENUM_SCENE.START_SCENE)
            del start_scene.video1
            del start_scene.video2
            print("释放内存成功")

        g.fade.start(temp)


class GameScene(Scene):
    """
    游戏场景
    """

    def __init__(self, scene_id, load_save=False):
        super().__init__(scene_id=scene_id)
        self.game_map = GameMap()
        if not load_save:
            # 新游戏
            self.game_map.load(1)
            self.sm_walker = Walker(0, 25, 25)

    def logic(self):
        self.game_map.roll(self.sm_walker.render_x, self.sm_walker.render_y)
        self.sm_walker.logic()

    def render(self):
        Sprite.blit(g.screen, self.game_map.btm_img, self.game_map.x, self.game_map.y)
        self.sm_walker.render(self.game_map.x, self.game_map.y)
        Sprite.blit(g.screen, self.game_map.top_img, self.game_map.x, self.game_map.y)
        # 人物重绘
        if self.game_map.redraw_data[self.sm_walker.mx][self.sm_walker.my] == 1:
            self.sm_walker.render(self.game_map.x, self.game_map.y)

        # debug
        # for x in range(self.game_map.w):
        #     for y in range(self.game_map.h):
        #         if self.game_map.walk_data[x][y] == 0:  # 不是障碍，画空心的矩形
        #             # pygame.draw.rect(g.screen, (255, 255, 255),
        #             #                  (self.game_map.x + x * 16, self.game_map.y + y * 16, 16, 16), 1)
        #             pass
        #         else:  # 是障碍，画黑色实心的矩形
        #             pygame.draw.rect(g.screen, (255, 255, 255),
        #                              (self.game_map.x + x * 16 + 1, self.game_map.y + y * 16 + 1, 14, 14), 1)

    def mouse_down(self, x, y):
        mx = int((x - self.game_map.x) / 16)
        my = int((y - self.game_map.y) / 16)
        # print(mx, my)
        self.sm_walker.find_path(self.game_map.walk_data, [mx, my])

    def mouse_move(self, x, y):
        pass

    def mouse_up(self, x, y):
        pass
