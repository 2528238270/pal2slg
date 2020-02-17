import cv2

# 游戏开始场景
import pygame

from code.animation import PalAnimationFactory
from code.camera import CameraManager
from code.engine.gui import Button
from code.engine.scene import Scene
from code.engine.sprite import Sprite
from code.fight import FightManager, Fighter, Magic
from code.game_global import g, ENUM_SCENE
from code.game_map import GameMap
from code.npc import NpcManager, Npc
from code.story import StoryPlayer
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

    def mouse_down(self, x, y, pressed):
        if g.talk_mgr.switch:
            return
        self.btn_new_game.mouse_down(x, y)
        self.btn_old_game.mouse_down(x, y)
        self.btn_exit_game.mouse_down(x, y)

    def mouse_up(self, x, y, pressed):
        if g.talk_mgr.switch:
            g.talk_mgr.talk_next()
            return
        self.btn_new_game.mouse_up()
        self.btn_old_game.mouse_up()
        self.btn_exit_game.mouse_up()

    def mouse_move(self, x, y):
        if g.talk_mgr.switch:
            return
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
            self.sm_walker = Walker(0, 35, 40)
        self.camera_mgr = CameraManager(self.game_map, self.sm_walker)  # 镜头管理器
        self.npc_mgr = NpcManager(g.screen)  # npc管理器
        self.story_player = StoryPlayer()  # 剧情播放器
        self.ani_factory = PalAnimationFactory(g.animator)  # 动画工厂，为剧情播放器提供动画功能
        self.fight_mgr = FightManager(g.screen)  # 战斗管理器
        g.camera_mgr = self.camera_mgr
        g.npc_mgr = self.npc_mgr
        g.game_map = self.game_map
        g.ani_factory = self.ani_factory
        g.fight_mgr = self.fight_mgr
        self.story_player.load_script(1)
        self.story_player.play()
        fighter = Fighter(0, 10, 10, 3)
        fighter.set_attr([100, 100], [100, 100], 10, 10, 10, 3, 10, 10, 3)
        fighter.set_name('苏媚')
        fighter.add_skill(Magic(1))

        fighter_dgt = Fighter(2, 15, 10, 2, True)
        fighter_dgt.set_attr([100, 100], [100, 100], 10, 10, 10, 1, 10, 10, 2)
        fighter_dgt.set_name('大光头吴涛')

        self.fight_mgr.start([fighter, fighter_dgt], 1)
        # self.test_npc = Npc(1, 30, 30, 3, [1000, 1001])
        # self.npc_mgr.add(self.test_npc)

    def logic(self):
        if self.fight_mgr.switch:
            self.fight_mgr.logic()
            return
        self.camera_mgr.logic()
        self.npc_mgr.logic()
        self.sm_walker.logic()
        self.story_player.logic()

    def render(self):
        """
        渲染
        """
        if self.fight_mgr.switch:
            self.fight_mgr.render()
            return
        # 创建渲染列表并排序
        render_list = []
        render_list.append(self.sm_walker)
        render_list.extend(self.npc_mgr.npc_list)
        render_list.sort(key=lambda obj: obj.y)
        Sprite.blit(g.screen, self.game_map.btm_img, self.game_map.x, self.game_map.y)
        for render_obj in render_list:
            render_obj.render(self.game_map.x, self.game_map.y)
        Sprite.blit(g.screen, self.game_map.top_img, self.game_map.x, self.game_map.y)
        # 人物重绘
        for render_obj in render_list:
            if self.game_map.redraw_data[render_obj.mx][render_obj.my] == 1:
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

    def mouse_down(self, x, y, pressed):
        if g.talk_mgr.switch:
            g.talk_mgr.talk_next()
            return
        if self.fight_mgr.switch:
            self.fight_mgr.mouse_down(x, y, pressed)
            return
        mx = int((x - self.game_map.x) / 16)
        my = int((y - self.game_map.y) / 16)
        # print(mx, my)
        # self.camera_mgr.move((x - self.game_map.x), (y - self.game_map.y))
        ret = self.npc_mgr.mouse_down(x, y, self.game_map.x, self.game_map.y)
        if ret:
            return
        self.sm_walker.find_path(self.game_map.walk_data, [mx, my])

    def mouse_move(self, x, y):
        if self.fight_mgr.switch:
            self.fight_mgr.mouse_move(x, y)
            return

    def mouse_up(self, x, y, pressed):
        if self.fight_mgr.switch:
            self.fight_mgr.mouse_up(x, y, pressed)
            return
