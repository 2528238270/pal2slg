# 登录
SQL_LOGIN = """
select * from "user" where username=%s and password=%s
"""

# 玩家信息
SQL_PLAYER = """
select * from player where user_id=%s
"""