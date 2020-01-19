from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa

# Base = declarative_base()
#
#
# class User(Base):
#     __tablename__ = 'user'
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String(64))  # 昵称
#     username = Column(String(32), nullable=False)  # 账号
#     password = Column(String(32), nullable=False)  # 密码


metadata = sa.MetaData()

User = sa.Table(
    'user',
    metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('username', sa.String(32)),
    sa.Column('password', sa.String(32)),
    sa.Column('create_time', sa.Integer),
    sa.Column('mobile', sa.String(32)),
    sa.Column('last_login_time', sa.Integer),
)

Player = sa.Table(
    'player',
    metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('role_id', sa.Integer),
    sa.Column('user_id', sa.Integer),
    sa.Column('nickname', sa.String(32)),
    sa.Column('coupon', sa.Integer),
    sa.Column('create_time', sa.Integer),
    sa.Column('last_login_time', sa.Integer),
)