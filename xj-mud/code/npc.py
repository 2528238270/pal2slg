"""
npc系统
create by 狡猾的皮球
qq:871245007
2020年2月13日 13:21:54
"""
import random

from code.game_global import g
from code.walker import Walker


class Npc(Walker):
    """
    npc系统
    """

    def __init__(self, npc_id, mx, my, face=0, talk_id_list=None):
        self.npc_id = npc_id
        self.visible = True  # 是否可见
        self.talk_id_list = talk_id_list  # 对话id列表（因为同一个npc可能并不是固定的对话）
        # TODO:这里npc_id和walker_id应该设计一个映射表
        super().__init__(npc_id, mx, my, face)

    def logic(self):
        super().logic()

    def render(self, map_x, map_y):
        if not self.visible:
            return
        super().render(map_x, map_y)

    def talk(self):
        """
        与npc对话
        """
        if not self.talk_id_list:
            return
        talk_id = random.choice(self.talk_id_list)
        g.talk_mgr.start(talk_id)

    def hit(self, x, y, map_x, map_y):
        """
        判断是否点中npc
        """
        render_x = map_x + self.render_x
        render_y = map_y + self.render_y
        return render_x < x < render_x + self.cell_w and render_y < y < render_y + self.cell_h


class NpcManager:
    """
    npc管理器
    """

    def __init__(self, surface):
        self.surface = surface
        self.npc_list = []  # npc列表

    def sort_npc_list(self):
        """
        根据y坐标排序npc
        """
        self.npc_list.sort(key=lambda npc: npc.y)

    def logic(self):
        """
        逻辑
        """
        # self.sort_npc_list()
        for npc in self.npc_list:
            npc.logic()

    def render(self, map_x, map_y):
        """
        渲染
        """
        for npc in self.npc_list:
            if not npc.visible:
                continue
            npc.render(map_x, map_y)

    def add(self, npc):
        """
        添加npc
        """
        # 如果npc已经存在，那么不能重复添加
        for n in self.npc_list:
            if npc.npc_id == n.npc_id:
                return

        self.npc_list.append(npc)

    def mouse_down(self, x, y, map_x, map_y):
        """
        鼠标点击npc
        """
        for npc in self.npc_list:
            if npc.hit(x, y, map_x, map_y):
                npc.talk()
                return True
        return False
