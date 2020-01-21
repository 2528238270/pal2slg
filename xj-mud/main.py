import asyncio
import sys
import json
import time
import tkinter as tk

import pygame
import websockets

from code.engine.sprite import Sprite
from code.game_global import g
from code.fighter import Fighter, FightManager, DamageAnimation


class Game:
    def __init__(self, title, width, height, fps=120, ip='127.0.0.1', port=8778):
        """
        :param title: 游戏窗口的标题
        :param width: 游戏窗口的宽度
        :param height: 游戏窗口的高度
        :param fps: 游戏每秒刷新次数
        """
        self.title = title
        self.width = width
        self.height = height
        self.screen = None
        self.fps = fps
        self.__init_pygame()
        self.__init_game()
        asyncio.get_event_loop().run_until_complete(self.update(ip, port))

    def __init_pygame(self):
        pygame.init()
        pygame.display.set_caption(self.title)
        self.screen = pygame.display.set_mode([self.width, self.height])
        self.clock = pygame.time.Clock()

    def __init_game(self):
        g.fps = self.fps
        g.fnt_hp = pygame.font.Font('./resource/font/font1.TTF', 16)
        g.fnt_battle_name = pygame.font.Font('./resource/font/font1.TTF', 24)
        g.bg = pygame.image.load('./resource/dazhuzai/login_bg_60b2432a.png').convert_alpha()
        g.bg_title = pygame.image.load('./resource/dazhuzai/hero_res_1021_c4e8972d.png').convert_alpha()
        g.bg_battle = pygame.image.load('./resource/dazhuzai/hero_res_battle_bg.png').convert_alpha()
        g.bg_hero_1 = pygame.image.load('./resource/dazhuzai/bg_hero_1.png').convert_alpha()
        g.bg_hero_2 = pygame.image.load('./resource/dazhuzai/bg_hero_2.png').convert_alpha()
        g.bg_hero_hp = pygame.image.load('./resource/dazhuzai/bg_hero_hp.png').convert_alpha()
        g.hp_bar = pygame.image.load('./resource/dazhuzai/hp_bar.png').convert_alpha()
        g.mp_bar = pygame.image.load('./resource/dazhuzai/mp_bar.png').convert_alpha()
        g.ry_fnt = pygame.image.load('./resource/font/ryFont_5a94031e.png').convert_alpha()
        with open('./resource/font/ryFont_f695d33e.fnt', mode='r', encoding='utf8') as file:
            g.ry_fnt_data = json.loads(file.read())
        with open('./resource/skill.json', mode='r', encoding='utf8') as file:
            g.skill_data = json.loads(file.read())
        g.fight_mgr = FightManager()
        g.screen = self.screen
        g.battle_data['teammates'] = [
            Fighter(1, 1, '李逍遥', 1, [9999, 100], 9999, 10, 10000, 8000, 0, 0, 1),
            # Fighter(2, 1, '赵灵儿', 2, [9999, 800], 50, 10, 10000, 2000, 0, 0),
            # Fighter(0, 1, '林月如', 3, [9999, 100], 1000, 10, 10000, 2000, 0, 0, 4),
            # Fighter(3, 1, '阿奴', 4, [800, 800], 50, 10, 10000, 2000, 0, 0),
            # Fighter(4, 1, '赵日天', 5, [9999, 9999], 9999, 10, 10000, 10000, 0, 0)
        ]
        g.battle_data['enemies'] = [
            Fighter(0, 2, '拜月教主', 1, [9999, 9999], 40, 1, 10000, 2000, 0, 0),
            Fighter(1, 2, '石长老', 1, [9999, 9999], 20, 1, 10000, 2000, 0, 0),
            Fighter(2, 2, '水魔兽', 1, [50000, 50000], 30, 1, 10000, 2000, 0, 0),
            Fighter(3, 2, '水魔兽', 1, [50000, 50000], 30, 1, 10000, 2000, 0, 0),
            Fighter(4, 2, '水魔兽', 1, [50000, 50000], 30, 1, 10000, 2000, 0, 0),
            Fighter(5, 2, '水魔兽', 1, [50000, 50000], 30, 1, 10000, 2000, 0, 0),

            # Fighter(3,2,'赵日天13',1,[100,100],10,1,10000,2000,0,0),
            # Fighter(4,2,'赵日天13',1,[100,100],10,1,10000,2000,0,0),
            # Fighter(5,2,'赵日天13',1,[100,100],10,1,10000,2000,0,0),
        ]
        g.fight_mgr.start(g.battle_data['teammates'], g.battle_data['enemies'])
        # 创建登录窗口

    async def update(self, ip, port):
        # task1 = asyncio.create_task(self.logic())
        # task2 = asyncio.create_task(self.recv_data(ip, port))
        # await task1
        # await task2
        uri = f'ws://{ip}:{port}/'
        ws = await websockets.connect(uri)
        task1 = asyncio.create_task(self.recv_data(ws))
        task2 = asyncio.create_task(self.logic())
        await asyncio.gather(task1, task2)

    async def logic(self):
        peer_time = 1 / self.fps
        last_time = time.time()
        while True:
            # print("游戏逻辑循环时间：", peer_time, time.time() - last_time)
            last_time = time.time()
            # self.clock.tick(self.fps)
            await asyncio.sleep(peer_time / 2)
            # 逻辑更新
            self.event_handler()
            g.fight_mgr.logic()
            # 画面更新
            Sprite.blit(g.screen, g.bg, 0, 0)
            Sprite.blit(g.screen, g.bg_title, 0, 0)
            g.fight_mgr.render()
            pygame.display.update()

    async def recv_data(self, websocket):
        """
        接收网络数据
        """
        while True:
            msg = await websocket.recv()
            print(msg)
            # async for msg in websocket:
            #     print(msg)

    def create_window(self):
        window = tk.Tk()
        window.title('仙剑mud')
        # window.geometry('400x400')  # 这里的乘是小x
        l1 = tk.Label(window, text='账号', font=('Arial', 12))
        e1 = tk.Entry(window, show=None, font=('Arial', 14))

        l2 = tk.Label(window, text='密码', font=('Arial', 12))
        e2 = tk.Entry(window, show='●', font=('Arial', 14))

        b_login = tk.Button(window, text='登录', font=('Arial', 12))
        b_register = tk.Button(window, text='注册', font=('Arial', 12))

        l1.grid(row=0, column=0)
        e1.grid(row=0, column=1)
        l2.grid(row=1, column=0)
        e2.grid(row=1, column=1)
        b_login.grid(row=2, column=0)
        b_register.grid(row=2, column=1)
        window.mainloop()

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()


if __name__ == '__main__':
    Game("仙剑", 640, 900)
    # Game("仙剑", 1, 1)
