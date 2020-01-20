import time

from api.player.sql import *
from foxy_framework.server_global import g


async def create_player(player, data):
    """
    创建玩家
    {
     "role_type_id":1,
     "nickname":"昵称"
    }
    """
    if not player.is_login:
        await player.send('error', {'msg': '未登录'})
        return
    role_type_id = data['role_type_id']
    nickname = str(data['nickname'])
    if not 3 <= len(nickname) <= 8:
        await player.send('error', {'msg': '昵称长度为3~8个字符'})
        return

    # 首先判断玩家是否有角色
    async with g.engine.acquire() as conn:
        result = await (await conn.execute(SQL_PLAYER, player.user_id)).first()
        if result:
            await player.send('error', {'msg': '已有角色'})
            return
        now = int(time.time())
        # 找到对应角色
        for d in g.role_list:
            if d['id'] == role_type_id:
                # 创建player
                await conn.execute(SQL_CREATE_PLAYER, nickname, 0, role_type_id, now, now, player.user_id)
                # player_id
                player_id = await conn.scalar(SQL_PLAYER, player.user_id)
                # 创建角色
                await conn.execute(SQL_CREATE_ROLE, nickname, 1, d['hp'], d['atk'], d['dfs'], d['hit'], d['cri'],
                                   d['dod'], d['rcri'], now, d['id'], player_id)
                return
        # 没找到对应角色
        await player.send('error', {'msg': '参数错误'})
