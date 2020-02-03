import cv2

# 游戏开始场景
import pygame

from code.engine.gui import Button
from code.engine.sprite import Sprite
from code.game_global import g

video_state = 0  # 0开场动画没放完 1开场动画放完了 2正在播放循环动画
init = False  # 场景是否初始化

video1 = []
video1_speed = 0

video2 = []
video2_speed = 0

count = 0

bg = None
btn_new_game = None
btn_old_game = None
btn_exit_game = None


def logic():
    """
    开始界面逻辑
    """
    global init, video1, video2, bg, video_state, count, video1_speed, video2_speed, btn_new_game, btn_old_game, btn_exit_game

    if not init:
        # 初始化
        init = True
        # 创建按钮
        btn_new_game = Button(230, 270, imgNormal=g.btn1, imgMove=g.btn2)
        btn_old_game = Button(230, 320, imgNormal=g.btn3, imgMove=g.btn4)
        btn_exit_game = Button(230, 370, imgNormal=g.btn5, imgMove=g.btn6)

        cap1 = cv2.VideoCapture("./resource/Video/StartMenu.avi")
        cap2 = cv2.VideoCapture("./resource/Video/MenuLoop.avi")

        while cap1.isOpened():
            ret, frame = cap1.read()
            if ret:
                video1.append(cv2.transpose(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            else:
                break
        cap1.release()

        while cap2.isOpened():
            ret, frame = cap2.read()
            if ret:
                video2.append(cv2.transpose(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            else:
                break
        cap2.release()

        video1_speed = 1 / (11 / len(video1) * g.fps)  # g.fps
        video2_speed = 1 / (15 / len(video2) * g.fps)  # g.fps

    if video_state == 0:
        count += video1_speed
        if int(count) >= len(video1):
            video_state = 1
            count = 0
        else:
            bg = video1[int(count)]

    if video_state == 1:
        count += video2_speed
        if int(count) >= len(video2):
            count = 0
        bg = video2[int(count)]


def render():
    """
    渲染
    """
    # 播放背景视频
    pygame.surfarray.blit_array(g.screen, bg)
    # Sprite.blit(g.screen, bg, 0, 0)
    # 绘制背景、按钮
    if video_state == 1:
        Sprite.blit(g.screen, g.bg_enter, 0, 0)
        btn_new_game.draw(g.screen)
        btn_old_game.draw(g.screen)
        btn_exit_game.draw(g.screen)


def mouse_down(x, y):
    btn_new_game.muose_down(x, y)
    btn_old_game.muose_down(x, y)
    btn_exit_game.muose_down(x, y)


def mouse_up(x, y):
    btn_new_game.muose_up()
    btn_old_game.muose_up()
    btn_exit_game.muose_up()


def mouse_move(x, y):
    btn_new_game.get_focus(x, y)
    btn_old_game.get_focus(x, y)
    btn_exit_game.get_focus(x, y)
