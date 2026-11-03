from sqlalchemy import create_engine, String, Text, Integer, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from peizhi import shuju_mulu

class Base(DeclarativeBase): pass
class Jilu(Base):
    __tablename__ = 'jilu'
    id: Mapped[int] = mapped_column(primary_key=True)
    leixing: Mapped[str] = mapped_column(String)
    biaoti: Mapped[str] = mapped_column(String)
    neirong: Mapped[str] = mapped_column(Text, default='')
    zan: Mapped[int] = mapped_column(Integer, default=0)
    cang: Mapped[int] = mapped_column(Integer, default=0)
    ping: Mapped[int] = mapped_column(Integer, default=0)
    zhuangtai: Mapped[str] = mapped_column(String, default='待审核')

def engine():
    e = create_engine('sqlite:///' + str(shuju_mulu() / 'insight.db'))
    Base.metadata.create_all(e)
    return e

def liebiao(kind):
    with Session(engine()) as s:
        return [dict(id=r.id, biaoti=r.biaoti, neirong=r.neirong, zan=r.zan, cang=r.cang, ping=r.ping, zhuangtai=r.zhuangtai) for r in s.scalars(select(Jilu).where(Jilu.leixing == kind))]

def baocun(kind, **data):
    with Session(engine()) as s:
        s.add(Jilu(leixing=kind, **data)); s.commit()

def zhuangtai(id, value):
    with Session(engine()) as s:
        r = s.get(Jilu, id)
        if r: r.zhuangtai = value
        s.commit()
