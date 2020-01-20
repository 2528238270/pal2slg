from foxy_framework.server import Server
from foxy_framework.server_global import g

SQL_ROLE_TYPE = """
select * from role_type where is_player=true
"""


@Server.register_init
class InitGame:
    async def __call__(self, *args, **kwargs):
        """
        初始化相关的操作
        """
        g.role_list = []
        async with g.engine.acquire() as conn:
            # 加载所有种族数据
            result = await conn.execute(SQL_ROLE_TYPE)
            async for row in result:
                g.role_list.append({
                    'id': row[0],
                    'name': row[1],
                    'hp': row[2],
                    'atk': row[3],
                    'hit': row[4],
                    'dfs': row[5],
                    'cri': row[6],
                    'dod': row[7],
                    'rcri': row[8],
                    'd_hp': row[9],
                    'd_atk': row[10],
                    'd_dfs': row[11],
                    'd_hit': row[12],
                    'd_cri': row[13],
                    'd_dod': row[14],
                    'd_rcri': row[15],
                    'description': row[16]
                })
