"""
基于engine.animation动画系统的再封装
主要作用是根据预制文件加载、创建动画
create by 狡猾的皮球
qq:871245007
2020年2月14日 14:31:26
"""
import pygame

from code.engine.animation import Animation
from code.game_global import g


class PalAnimationFactory:
    """
    游戏动画管理类
    """

    def __init__(self, animator):
        """
        依赖注入原生动画管理器
        """
        self.animator = animator

    def create(self, ani_id, x, y, ani_cls=Animation, add=True, extra=None):
        """
        加载动画文件，向ani_mrg新增animation对象
        """
        cfg_base = {
            'pic_id': None,
            'loop': None,
            'dw': None,
            'dh': None,
            'time': None,
            'frame_range': None,
            'frame_callback': None
        }
        with open(f'./resource/animation/{ani_id}.txt', 'r', encoding='utf8') as file:
            config_list = file.readlines()
        for config in config_list:
            if config.startswith('#') or config.startswith('//') or config.startswith("'"):
                continue
            if config.replace('\n', '').replace(' ', '') == '':
                continue
            config = config.replace('\n', '')
            name, args = config.split(' ')
            args = args.split(',')
            cfg_base[name] = args
        cfg_base['loop'] = bool(int(cfg_base['loop'][0]))
        cfg_base['time'] = int(cfg_base['time'][0])
        cfg_base['dw'] = int(cfg_base['dw'][0])
        cfg_base['dh'] = int(cfg_base['dh'][0])
        cfg_base['frame_range'] = [int(x) for x in cfg_base['frame_range']]
        # 处理回调事件
        callback = None
        if cfg_base['frame_callback']:
            arguments = cfg_base['frame_callback']
            if arguments[1] == 'sound':
                callback = self.play_sound(int(arguments[0]), int(arguments[2]))

        # 创建animation
        pic_id = cfg_base["pic_id"][0]
        img = pygame.image.load(f'./resource/animation/{pic_id}.png')
        # 额外参数
        e = extra or dict()
        ani = ani_cls(x, y, img, cfg_base['dw'], cfg_base['dh'], cfg_base['time'],
                      cfg_base['loop'], cfg_base['frame_range'], callback, fps=g.fps, **e)
        if add:
            self.animator.add_ani(ani)
        return ani

    def play_sound(self, target_frame, sound_id):
        """
        播放音效
        """

        def inner(frame):
            # TODO:这里应该建立缓存，每次加载音效太慢了
            sound = pygame.mixer.Sound(f'./resource/sound/{sound_id}.wav')
            if frame == target_frame:
                sound.play()

        return inner
