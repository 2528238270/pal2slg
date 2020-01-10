class Sprite:
    @staticmethod
    def draw(dest, source, x, y, cell_x, cell_y, cell_w=32, cell_h=32):
        """
        绘制精灵图中，指定x,y的图像
        :param dest: surface类型，要绘制到的目标surface
        :param source: surface类型，来源surface
        :param x: 绘制图像在dest中的坐标
        :param y: 绘制图像在dest中的坐标
        :param cell_x: 在精灵图中的格子坐标
        :param cell_y: 在精灵图中的格子坐标
        :param cell_w: 单个精灵的宽度
        :param cell_h: 单个精灵的高度
        :return:
        """
        dest.blit(source, (x, y), (cell_x * cell_w, cell_y * cell_h, cell_w, cell_h))

    @staticmethod
    def draw_rect(dest, source, x, y, src_x, src_y, w, h):
        dest.blit(source, (x, y), (src_x, src_y, w, h))

    @staticmethod
    def blit(dest, source, x, y):
        """
        绘制原图
        """
        dest.blit(source, (x, y))

    @staticmethod
    def blit_w(dest, source, x, y, percent):
        """
        按宽度百分比绘制
        percent:[0,1]
        """
        dest.blit(source, (x, y), (0, 0, int(source.get_width() * percent), source.get_height()))


def draw_text(dest, x, y, text, font, rgb):
    """
    绘制文字（取中心点绘制）
    """
    surface = font.render(text, True, rgb)
    w = surface.get_width()
    Sprite.blit(dest, surface, x - int(w / 2), y)


def draw_outline_text(dest, x, y, text, font, inner_rgb, outter_rgb):
    """
    绘制带边框的文字
    """
    sur_inner = font.render(text, True, inner_rgb)
    sur_outter = font.render(text, True, outter_rgb)
    w = sur_inner.get_width()
    Sprite.blit(dest, sur_outter, x - int(w / 2) + 1, y)
    Sprite.blit(dest, sur_outter, x - int(w / 2) - 1, y)
    Sprite.blit(dest, sur_outter, x - int(w / 2), y + 1)
    Sprite.blit(dest, sur_outter, x - int(w / 2), y - 1)
    Sprite.blit(dest, sur_inner, x - int(w / 2), y)
