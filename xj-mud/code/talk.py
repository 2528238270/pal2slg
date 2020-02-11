"""
对话系统
create by 狡猾的皮球
2020年2月11日 13:46:55
"""
import pygame

from code.engine.sprite import Sprite, draw_src_outline_text, draw_rect_text
from code.game_global import g
from code.scripts import talk_script


class TalkManager:
    """
    游戏对话管理器
    """

    def __init__(self, surface):
        self.surface = surface  # 渲染对话的surface
        self.switch = False  # 对话系统开关
        self.talk_id = -1  # 对话id
        self.talk_count = -1  # 对话进度
        self.talk_script = None  # 对话脚本
        self.talk_length = -1  # 对话长度
        self.face_img = None  # 头像
        self.current_text = ""  # 当前对话的完整文字
        self.current_show_text = ""  # 当前显示的文字
        # 显示文字的速度，10字/秒
        self.show_speed = 25 / g.fps
        self.show_count = 0
        # 头像绘制坐标
        self.face_x = 0
        self.face_y = 0
        # 对话框绘制坐标
        self.box_x = 0
        self.box_y = 0
        # 对话框宽度尺寸
        self.box_width = 350
        self.box_height = 150

    def reset(self):
        """
        重置对话管理器
        """
        self.switch = False  # 对话系统开关
        self.talk_id = -1  # 对话id
        self.talk_count = -1  # 对话进度
        self.talk_script = None  # 对话脚本
        self.talk_length = -1  # 对话长度
        self.current_text = ""  # 当前对话的完整文字
        self.current_show_text = ""  # 当前显示的文字
        self.show_count = 0  # 逐字计数

    def start(self, talk_id):
        """
        开始一个新对话
        """
        self.talk_id = talk_id
        self.talk_script = talk_script[talk_id]
        self.talk_length = len(self.talk_script)
        self.switch = True
        self.talk()

    def get_cur_info(self):
        """
        获取当前对话框以及头像位置信息
        """
        current_data = self.talk_script[self.talk_count]
        self.current_text = current_data["text"]
        self.current_show_text = ""
        self.show_count = 0
        # 加载头像
        if current_data["face"] != -1:
            self.face_img = pygame.image.load(f'./resource/PicLib/all_face/{current_data["face"]}.png').convert_alpha()
            face_w = self.face_img.get_width()
            face_h = self.face_img.get_height()
        else:
            # 如果没有头像，对话框就在窗口中间显示
            face_w = 200
            face_h = 250

        # 在窗口最底部显示对话框
        self.face_y = 480 - face_h
        self.box_y = 480 - self.box_height

        # 判断头像方向
        if current_data["dir"] == "left":
            self.face_x = 0
            self.box_x = face_w
        elif current_data["dir"] == "right":
            self.face_x = 640 - face_w
            self.box_x = self.face_x - self.box_width

    def talk(self):
        """
        对话
        """
        if not self.switch:
            return

        # 更新对话进度
        self.talk_count += 1
        if self.talk_count >= self.talk_length:
            self.reset()
            return

        # 获取当前对话信息
        self.get_cur_info()

        # TODO:触发事件
        pass

    def logic(self):
        """
        逐字显示逻辑
        """
        if not self.switch:
            return

        if self.current_show_text == self.current_text:
            return

        self.current_show_text = self.current_text[:int(self.show_count) + 1]
        self.show_count += self.show_speed
        if int(self.show_count) >= len(self.current_text):
            self.show_count = len(self.current_text) - 1

    def render(self):
        """
        渲染对话框
        """
        if not self.switch:
            return
        # 画头像
        if self.talk_script[self.talk_count]["face"] != -1:
            Sprite.blit(g.screen, self.face_img, self.face_x, self.face_y)
        # 画对话框
        Sprite.draw_fill_rect(g.screen, self.box_x, self.box_y, self.box_width, self.box_height, (0, 0, 0, 210))
        # 画名字
        draw_src_outline_text(g.screen, self.box_x + 10, self.box_y + 5,
                              self.talk_script[self.talk_count]["name"] + "：",
                              g.fnt_talk, (255, 255, 255), (255, 127, 39))
        # 画文字
        draw_rect_text(g.screen, (255, 255, 255), self.current_show_text, g.fnt_talk, self.box_x + 10, self.box_y + 30,
                       self.box_width - 15)

    def talk_next(self):
        """
        继续对话
        """
        if not self.switch:
            return

        if self.current_show_text != self.current_text:
            self.current_show_text = self.current_text
        else:
            self.talk()
