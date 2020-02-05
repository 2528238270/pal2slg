import cv2

# 游戏开始场景
import pygame

from code.engine.gui import Button
from code.engine.scene import Scene
from code.engine.sprite import Sprite
from code.game_global import g


class StartScene(Scene):
    def __init__(self, scene_id):
        super().__init__(scene_id=scene_id)
        self.video_state = 0  # 0开场动画没放完 1开场动画放完了 2正在播放循环动画
        self.video1 = []
        self.video1_speed = 0
        self.video2 = []
        self.video2_speed = 0
        self.count = 0
        self.bg = None
        # 创建按钮
        self.btn_new_game = Button(230, 270, imgNormal=g.btn1, imgMove=g.btn2, callBackFunc=g.fade.start)
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
