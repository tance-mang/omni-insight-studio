from sqlalchemy import create_engine, String, Text, Integer, select, inspect, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from peizhi import shuju_mulu

class Base(DeclarativeBase): pass
class Jilu(Base):
    __tablename__ = 'jilu'
    id: Mapped[int] = mapped_column(primary_key=True)
    leixing: Mapped[str] = mapped_column(String)
    platform: Mapped[str] = mapped_column(String, default='其他')
    biaoti: Mapped[str] = mapped_column(String)
    neirong: Mapped[str] = mapped_column(Text, default='')
    zan: Mapped[int] = mapped_column(Integer, default=0)
    cang: Mapped[int] = mapped_column(Integer, default=0)
    ping: Mapped[int] = mapped_column(Integer, default=0)
    zhuangtai: Mapped[str] = mapped_column(String, default='待审核')
    jiage: Mapped[str] = mapped_column(String, default='')
    maidian: Mapped[str] = mapped_column(Text, default='')
    yonghu: Mapped[str] = mapped_column(Text, default='')
    jinyongci: Mapped[str] = mapped_column(Text, default='')

def engine():
    e = create_engine('sqlite:///' + str(shuju_mulu() / 'insight.db'))
    Base.metadata.create_all(e)
    cols = {c['name'] for c in inspect(e).get_columns('jilu')}
    with e.begin() as conn:
        if 'platform' not in cols:
            conn.execute(text("ALTER TABLE jilu ADD COLUMN platform VARCHAR DEFAULT '其他' NOT NULL"))
        if 'jiage' not in cols:
            conn.execute(text("ALTER TABLE jilu ADD COLUMN jiage VARCHAR DEFAULT '' NOT NULL"))
            conn.execute(text("ALTER TABLE jilu ADD COLUMN maidian TEXT DEFAULT '' NOT NULL"))
            conn.execute(text("ALTER TABLE jilu ADD COLUMN yonghu TEXT DEFAULT '' NOT NULL"))
            conn.execute(text("ALTER TABLE jilu ADD COLUMN jinyongci TEXT DEFAULT '' NOT NULL"))
            conn.execute(text("UPDATE jilu SET maidian = neirong WHERE leixing = '产品' AND COALESCE(neirong, '') != ''"))
            conn.execute(text("UPDATE jilu SET neirong = '' WHERE leixing = '产品'"))
    return e

def liebiao(kind):
    with Session(engine()) as s:
        return [dict(id=r.id, platform=r.platform, biaoti=r.biaoti, neirong=r.neirong,
                     zan=r.zan, cang=r.cang, ping=r.ping, zhuangtai=r.zhuangtai,
                     jiage=r.jiage, maidian=r.maidian, yonghu=r.yonghu, jinyongci=r.jinyongci)
                for r in s.scalars(select(Jilu).where(Jilu.leixing == kind))]

def an_id(id):
    with Session(engine()) as s:
        r = s.get(Jilu, id)
        if not r: return None
        return dict(id=r.id, platform=r.platform, biaoti=r.biaoti, neirong=r.neirong,
                    zan=r.zan, cang=r.cang, ping=r.ping, zhuangtai=r.zhuangtai,
                    jiage=r.jiage, maidian=r.maidian, yonghu=r.yonghu, jinyongci=r.jinyongci)

def baocun(kind, **data):
    if kind == '笔记' and 'biaoti' in data:
        with Session(engine()) as s:
            existing = s.scalars(select(Jilu).where(Jilu.leixing == kind, Jilu.biaoti == data['biaoti'])).first()
            if existing: return False
    with Session(engine()) as s:
        s.add(Jilu(leixing=kind, **data)); s.commit()
    return True

def zhuangtai(id, value):
    with Session(engine()) as s:
        r = s.get(Jilu, id)
        if r: r.zhuangtai = value
        s.commit()
