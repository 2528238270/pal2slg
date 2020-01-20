# 玩家信息
SQL_PLAYER = """
select * from player where user_id=%s
"""

# 创建玩家
SQL_CREATE_PLAYER = """
insert into player(nickname,coupon,role_id,create_time,last_login_time,user_id) values(%s,%s,%s,%s,%s,%s)
"""

# 创建角色
SQL_CREATE_ROLE = """
insert into 
    role(
        name,level,hp,
        atk,dfs,hit,
        cri,dod,rcri,
        create_time,role_type_id,player_id
        ) 
    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""
