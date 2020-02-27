"""
剧情系统，整个游戏最核心的系统之一
create by 狡猾的皮球
qq:871245007
2020年2月13日 15:43:34
"""
from code.fight import Fighter, Magic
from code.game_global import g
from code.npc import Npc


class Command:
    """
    基本指令
    """

    def __init__(self, cmd_name, cmd_args=None):
        self.cmd_name = cmd_name
        self.cmd_args = cmd_args
        for i in range(len(self.cmd_args)):
            if self.cmd_args[i].isdigit():
                self.cmd_args[i] = int(self.cmd_args[i])
        self.done = False  # 是否执行完成
        self.working = False  # 是否正在执行

    def logic(self):
        """
        逻辑
        """
        if not self.working:
            return
        cmd_logic = getattr(self, self.cmd_name + '_logic')
        if cmd_logic:
            cmd_logic()

    def execute(self):
        """
        开始执行
        """
        if self.working:
            return
        self.working = True
        cmd = getattr(self, self.cmd_name)
        cmd(*self.cmd_args)

    def show_npc(self, *args):
        """
        创建或显示npc
        指令结构：
        show_npc npc_id,mx,my,face,talk_id_list
        """
        npc_id = args[0]
        mx = args[1]
        my = args[2]
        face = args[3]
        if len(args) == 5:
            talk_id_list = args[4]
        else:
            talk_id_list = None
        npc = g.npc_mgr.exists(npc_id)
        if npc:
            npc.set_point(mx, my)
            npc.face = face
            npc.visible = True
        else:
            npc = Npc(npc_id, mx, my, face, talk_id_list)
            g.npc_mgr.add(npc)
        self.done = True
        self.working = False

    def remove_npc(self, *args):
        """
        移除npc
        """
        npc_id = args[0]
        g.npc_mgr.remove(npc_id)
        self.done = True
        self.working = False

    def hide_npc(self, *args):
        """
        隐藏npc
        """
        npc_id = args[0]
        npc = g.npc_mgr.exists(npc_id)
        if npc:
            npc.visible = False
        self.done = True
        self.working = False

    def start_talk(self, *args):
        """
        开始对话
        """
        talk_id = args[0]
        g.talk_mgr.start(talk_id)
        self.talk_id = talk_id
        self.working = True

    def start_talk_logic(self):
        """
        对话逻辑
        """
        if g.talk_mgr.talk_id != self.talk_id or not g.talk_mgr.switch:
            self.working = False
            self.done = True

    def move_npc(self, *args):
        """
        移动npc
        """
        npc_id = args[0]
        mx = args[1]
        my = args[2]
        self.face = args[3]
        npc = g.npc_mgr.exists(npc_id)
        self.npc = npc
        npc.find_path(g.game_map.walk_data, [mx, my])
        self.working = True

    def move_npc_logic(self):
        """
        移动npc逻辑
        """
        if not self.npc.walking:
            self.npc.face = self.face
            self.working = False
            self.done = True

    def move_camera(self, *args):
        """
        移动镜头
        """
        mx = args[0]
        my = args[1]
        g.camera_mgr.move_m_pos(mx, my)
        self.working = True

    def move_camera_logic(self, *args):
        """
        移动镜头逻辑
        """
        if not g.camera_mgr.moving:
            self.working = False
            self.done = True

    def delay(self, *args):
        """
        延迟
        """
        second = args[0]
        self.total_frame = second * g.fps  # 计算second秒需要经过多少个主循环
        self.count = 0
        self.working = True

    def delay_logic(self):
        self.count += 1
        if self.count >= self.total_frame:
            self.working = False
            self.done = True

    def unlock_camera(self, *args):
        """
        解锁镜头
        """
        x = args[0]
        y = args[1]
        g.camera_mgr.unlock(x, y)
        self.working = False
        self.done = True

    def play_ani(self, *args):
        """
        播放动画
        """
        ani_id = args[0]
        x = args[1]
        y = args[2]
        need_blend = bool(args[3])
        self.ani = g.ani_factory.create(ani_id, x, y, need_blend=need_blend)
        self.working = True

    def play_ani_logic(self):
        if self.ani.least_once:
            self.working = False
            self.done = True

    def play_async_ani(self, *args):
        """
        播放异步动画，不会阻塞剧情播放器
        """
        ani_id = args[0]
        x = args[1]
        y = args[2]
        need_blend = bool(args[3])
        self.ani = g.ani_factory.create(ani_id, x, y, need_blend=need_blend)
        self.working = False
        self.done = True

    def play_music(self, *args):
        """
        播放音乐
        """
        music_id = args[0]
        g.audio_player.play_music(music_id)
        self.working = False
        self.done = True

    def start_fight_t(self, *args):
        """
        开始测试战斗
        """
        fighter = Fighter(0, 10, 10, 3)
        fighter.set_attr([500, 500], [100, 100], 70, 10, 10, 4, 10000, 4, 3, 1)
        fighter.set_name('苏媚')
        fighter.set_skill([Magic(1), Magic(2), ])

        fighter_bt = Fighter(0, 10, 11, 3)
        fighter_bt.set_attr([999, 999], [100, 100], 200, 2000, 10, 4, 10000, 4, 3, 1)
        fighter_bt.set_name('变态苏媚')
        fighter_bt.set_skill([Magic(1)])

        fighter_dgt = Fighter(4, 17, 10, 2, True)
        fighter_dgt.set_attr([30000, 30000], [100, 100], 10, 10, 10, 8, 10, 1, 2, 4)
        fighter_dgt.set_name('千叶禅师')
        # fighter_dgt.set_skill([Magic(1)])

        fighter_dgt3 = Fighter(2, 18, 10, 2, True)
        fighter_dgt3.set_attr([100, 100], [100, 100], 10, 10, 10, 8, 10, 10, 2, 5)
        fighter_dgt3.set_name('大光头吴涛3')
        fighter_dgt3.set_skill([Magic(1)])

        fighter_dgt1 = Fighter(2, 34, 9, 2, True)
        fighter_dgt1.set_attr([100, 100], [100, 100], 10, 10, 10, 8, 10, 10, 2, 5)
        fighter_dgt1.set_name('大光头吴涛1')
        fighter_dgt1.set_skill([Magic(1)])

        fighter_dgt2 = Fighter(2, 44, 4, 2, True)
        fighter_dgt2.set_attr([100, 100], [100, 100], 10, 10, 10, 8, 10, 10, 2, 5)
        fighter_dgt2.set_name('大光头吴涛2')
        fighter_dgt2.set_skill([Magic(1)])

        fighter_dgt4 = Fighter(2, 35, 9, 2, True)
        fighter_dgt4.set_attr([100, 100], [100, 100], 10, 10, 10, 8, 10, 10, 2, 5)
        fighter_dgt4.set_name('大光头吴涛4')
        fighter_dgt4.set_skill([Magic(1)])

        fighter_dgt5 = Fighter(2, 36, 9, 2, True)
        fighter_dgt5.set_attr([100, 100], [100, 100], 10, 10, 10, 8, 10, 10, 2, 5)
        fighter_dgt5.set_name('大光头吴涛5')
        fighter_dgt5.set_skill([Magic(1)])

        fighter_dgt6 = Fighter(2, 37, 9, 2, True)
        fighter_dgt6.set_attr([100, 100], [100, 100], 10, 10, 10, 8, 10, 10, 2, 5)
        fighter_dgt6.set_name('大光头吴涛6')
        fighter_dgt6.set_skill([Magic(1)])

        g.fight_mgr.start([fighter, fighter_dgt, fighter_dgt3, fighter_bt, fighter_dgt1, fighter_dgt2,fighter_dgt4,fighter_dgt5,fighter_dgt6], 1)
        g.audio_player.play_music(5013)
        self.working = False
        self.done = True


class StoryPlayer:
    """
    剧情播放器
    """

    def __init__(self):
        self.cmd_list = []  # 指令队列
        self.current_cmd = None  # 当前正在执行的命令

    def load_script(self, script_id):
        """
        加载剧本文件
        """
        with open(f'./resource/story/{script_id}.txt', 'r', encoding='utf8') as file:
            cmd_list = file.readlines()
        for cmd in cmd_list:
            if cmd.startswith('#') or cmd.startswith('//') or cmd.startswith("'"):
                continue
            if cmd.replace('\n', '').replace(' ', '') == '':
                continue
            cmd = cmd.replace('\n', '')
            cmd_name, args = cmd.split(' ')
            args = args.split(',')
            command = Command(cmd_name, args)
            self.cmd_list.append(command)

    def play(self):
        """
        播放剧情
        """
        if len(self.cmd_list) == 0:
            self.current_cmd = None
            return

        while True:
            self.current_cmd = self.cmd_list.pop(0)
            self.current_cmd.execute()
            if not self.current_cmd.done:
                break
            if len(self.cmd_list) == 0:
                break

    def logic(self):
        """
        逻辑
        """
        if self.current_cmd is None:
            return

        if self.current_cmd.done:
            self.play()
            return

        self.current_cmd.logic()
