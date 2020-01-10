def f1(cb=None, args=None):
    print("播放动画1")
    if not cb:
        return
    if args is not None:
        cb(*args)
    else:
        cb()


def f2(cb=None, args=None):
    print("播放动画2")
    if not cb:
        return
    if args is not None:
        cb(*args)
    else:
        cb()


def f3(cb=None, args=None):
    print("播放动画3")
    if not cb:
        return
    if args is not None:
        cb(*args)
    else:
        cb()


def f4(cb=None, args=None):
    print("播放动画4")
    if not cb:
        return
    if args is not None:
        cb(*args)
    else:
        cb()
#
#
# data = [f1, f2, f3, f4, f4, f3, f2, f2, f4, f1, f4]
#
#
# def create(data, deep, last):
#     if deep == len(data):
#         return last
#     deep += 1
#     current = [data[deep - 1]]
#     last.append(current)
#     return create(data, deep, current)
#
#
# def run(data):
#     a = []
#     create(data, 0, a)
#     a = a[0]
#     start_f = a[0]
#     if len(data) == 1:
#         start_f()
#     elif len(data) == 2:
#         start_f(a[1][0], [])
#     elif len(data) > 2:
#         start_f(a[1][0], a[1][1])
#
#
# run(data)
# a=[1,2,3,4]
# for index,i in enumerate(a[::-1]):
#     print(index,i)