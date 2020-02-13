"""
剧情系统，整个游戏最核心的系统之一
create by 狡猾的皮球
qq:871245007
2020年2月13日 15:43:34
"""
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
        print(args)
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
        if not self.working:
            return

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
        if not self.working:
            return
        if not self.npc.walking:
            self.npc.face = self.face
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
        with open(f'./resource/story/{script_id}.txt') as file:
            cmd_list = file.readlines()
        for cmd in cmd_list:
            cmd = cmd.replace('\n', '')
            cmd_name, args = cmd.split(' ')
            args = args.split(',')
            print(cmd_name, args)
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
