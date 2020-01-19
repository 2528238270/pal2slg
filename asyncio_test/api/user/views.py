import time

from api.user.sql import SQL_LOGIN
from foxy_framework.server_global import g
from models import User
import sqlalchemy as sa


async def login(player, data):
    """
    登录
    {
        "username":"账号",
        "password":"密码"
    }
    """
    username = str(data['username'])
    password = str(data['password'])

    async with g.engine.acquire() as conn:
        s = SQL_LOGIN
        result = await conn.scalar(s, username, password)
        if result is None:
            await player.send('error', {'msg': '用户名或密码错误'})
            return


async def register(player, data):
    """
    注册账号：
    {
     "protocol_name":"register",
     "data":{
            "username":"账号",
            "password":"密码",
        }
    }
    """
    username = str(data['username'])
    password = str(data['password'])

    # 账号8~16位，密码8~16位
    if not username or not password:
        await player.send('error', {'msg': '账号或密码不能为空'})
        return

    if not 8 <= len(username) <= 16 or not 8 <= len(password) <= 16:
        await player.send('error', {'msg': '账号或密码长度必须为8~16个字符'})
        return

    async with g.engine.acquire() as conn:
        q = sa.select([sa.func.count(User.c.username)]).select_from(User).where(User.c.username == username)
        result = await conn.scalar(q)
        if result:
            await player.send('error', {'msg': '帐号已存在！'})
            return

        q = User.insert().values(username=username, password=password, create_time=int(time.time()))
        await conn.execute(q)

    await player.send('success', {'msg': '注册成功！'})
