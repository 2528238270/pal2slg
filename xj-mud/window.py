import tkinter as tk
from threading import Thread


async def login(username, password):
    pass


def create_window():
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


thread = Thread(target=create_window)

thread.start()
