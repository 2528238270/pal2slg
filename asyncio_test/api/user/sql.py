# 登录
SQL_LOGIN = """
select * from "user" where username=%s and password=%s
"""
