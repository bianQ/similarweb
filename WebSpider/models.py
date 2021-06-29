"""
Author   : Alan
Date     : 2021/6/29 14:56
Email    : vagaab@foxmail.com
"""
from datetime import datetime

from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from settings import DATABASE


Base = declarative_base()
# 初始化数据库连接:
engine = create_engine(f"mysql+pymysql://{DATABASE['user']}:{DATABASE['password']}@{DATABASE['host']}:"
                       f"{DATABASE['port']}/{DATABASE['db']}")
DBSession = sessionmaker(bind=engine)


__all__ = ['CoinLog']


class CoinLog(Base):

    __tablename__ = 'coinlog'
    id = Column(Integer, primary_key=True)
    symbols = Column(String)
    timestamp = Column(Integer, onupdate=datetime.now())
    remarks = Column(String)

    @classmethod
    def add_log(cls, **kwargs):
        session = DBSession()
        new_log = cls(**kwargs)
        session.add(new_log)
        session.commit()
        session.close()
