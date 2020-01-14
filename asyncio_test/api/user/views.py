from foxy_framework.server_global import g
from models import User
import sqlalchemy as sa


async def login(player, data):
    """
    登录
    """
    print(data)


async def register(player, data):
    """
    注册账号：
    {
     "protocol_name":"register",
     "data":{
            "username":"账号",
            "password":"密码",
            "name":"昵称"
        }
    }
    """
    username = data['username']
    password = data['password']
    name = data['name']

    async with g.engine.acquire() as conn:
        q = sa.select([sa.func.count(User.c.username)]).select_from(User).where(User.c.username == username)
        result = await conn.scalar(q)
        if result:
            await player.send({
                'protocol_name': 'error',
                'data': {'msg': '账号已存在！'}
            })
            return

        q = User.insert().values(username=username, password=password, name=name)
        await conn.execute(q)

    await player.send({
        'protocol_name': 'success',
        'data': {'msg': '注册成功！'}
    })
