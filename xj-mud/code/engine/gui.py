class Button:
    NORMAL = 0
    MOVE = 1
    DOWN = 2

    def __init__(self, x, y, text="", imgNormal=None, imgMove=None, imgDown=None, callBackFunc=None, font=None,
                 rgb=(0, 0, 0)):
        """
        初始化按钮的相关参数
        :param x: 按钮在窗体上的x坐标
        :param y: 按钮在窗体上的y坐标
        :param text: 按钮显示的文本
        :param imgNormal: surface类型,按钮正常情况下显示的图片
        :param imgMove: surface类型,鼠标移动到按钮上显示的图片
        :param imgDown: surface类型,鼠标按下时显示的图片
        :param callBackFunc: 按钮弹起时的回调函数
        :param font: pygame.font.Font类型,显示的字体
        :param rgb: 元组类型,文字的颜色
        """
        # 初始化按钮相关属性
        self.imgs = []
        if not imgNormal:
            raise Exception("请设置普通状态的图片")
        self.imgs.append(imgNormal)  # 普通状态显示的图片
        self.imgs.append(imgMove)  # 被选中时显示的图片
        self.imgs.append(imgDown)  # 被按下时的图片
        for i in range(2, 0, -1):
            if not self.imgs[i]:
                self.imgs[i] = self.imgs[i - 1]

        self.callBackFunc = callBackFunc  # 触发事件
        self.status = Button.NORMAL  # 按钮当前状态
        self.x = x
        self.y = y
        self.w = imgNormal.get_width()
        self.h = imgNormal.get_height()
        self.text = text
        self.font = font
        # 文字表面
        if self.font:
            self.textSur = self.font.render(self.text, True, rgb)

    def draw(self, destSuf):
        # 先画按钮背景
        if self.imgs[self.status]:
            destSuf.blit(self.imgs[self.status], [self.x, self.y])
        # 再画文字
        if self.font:
            dx = (self.w / 2) - (self.textSur.get_width() / 2)
            dy = (self.h / 2) - (self.textSur.get_height() / 2)
            destSuf.blit(self.textSur, [self.x + dx, self.y + dy])

    def colli(self, x, y):
        # 碰撞检测
        if self.x < x < self.x + self.w and self.y < y < self.y + self.h:
            return True
        else:
            return False

    def get_focus(self, x, y):
        # 按钮获得焦点时
        if self.status == Button.DOWN:
            return
        if self.colli(x, y):
            self.status = Button.MOVE
        else:
            self.status = Button.NORMAL

    def mouse_down(self, x, y):
        if self.colli(x, y):
            self.status = Button.DOWN
            return True
        else:
            return False

    def mouse_up(self):
        if self.status == Button.DOWN:  # 如果按钮的当前状态是按下状态,才继续执行下面的代码
            self.status = Button.NORMAL  # 按钮弹起,所以还原成普通状态
            if self.callBackFunc:  # 调用回调函数
                self.callBackFunc()
            return True
        return False