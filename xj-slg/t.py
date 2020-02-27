def qh(base, level):
    # 强化公式
    print(base * 1.1 ** level)


def cri(luk1, luk2):
    """
    暴击公式,TODO:需要修正
    """
    if luk1 >= luk2:
        c = (luk1 - luk2) / luk2
    else:
        c = (luk1 - luk2) / luk2

    if c > 1:
        c = 1
    if c < 0:
        c = 0
    print("自己：" + str(luk1), "敌人：" + str(luk2), "暴击率：" + str(c))


def fy(dh1, dh2):
    if dh1 >= dh2:
        c = 0.5 + (dh1 - dh2) / dh2
    else:
        c = 0.5 - (dh2 - dh1) / dh1
    if c > 1:
        c = 1
    if c < 0:
        c = 0
    print(c)


#
#
# for i in range(20):
#     print(i, end=' ')
#     qh(10, i)

# cri(70, 200)
# fy(2000, 1300)
for my in range(1, 11):
    for enemy in range(1, 11):
        cri(my, enemy)
