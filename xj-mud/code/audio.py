"""
整个游戏的声音控制
create by 狡猾的皮球
qq:871245007
2020年2月22日 12:54:31
"""
import pygame


class AudioPlayer:
    """
    音频播放器
    """

    def __init__(self):
        # 音效id与sound的映射
        self.sound_map = dict()
        self.sound_volume = 1
        self.__music_volume = 1

    def __load_sound(self, sound_id):
        """
        加载音效
        """
        if sound_id in self.sound_map:
            return
        self.sound_map[sound_id] = pygame.mixer.Sound(f'./resource/sound/{sound_id}.wav')

    def play_sound(self, sound_id):
        """
        播放音效
        """
        if sound_id not in self.sound_map:
            self.__load_sound(sound_id)
        self.sound_map[sound_id].set_volume(self.sound_volume)
        self.sound_map[sound_id].play()

    def play_music(self, music_id, times=-1):
        """
        播放音乐
        times=-1时无限播放
        """
        pygame.mixer.music.set_volume(self.__music_volume)
        pygame.mixer.music.load(f'./resource/music/{music_id}.mp3')
        pygame.mixer.music.play(times)

    @property
    def music_volume(self):
        return self.__music_volume

    @music_volume.setter
    def music_volume(self, volume):
        self.__music_volume = volume
        pygame.mixer.music.set_volume(self.__music_volume)
