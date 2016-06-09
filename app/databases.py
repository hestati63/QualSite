#-*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import config

engine = create_engine('sqlite:///' + config.dbfile, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
    autoflush=False,
    bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

import models
def init_db():
        Base.metadata.create_all(bind=engine)
        rules = [u"키공유 금지",
        u"각 분야(pwn, web, rev, forensic, misc)중 3분야에서 1문제 이상 풀이, 1분야에서 2문제 이상 풀이",
        u"카포전 출전 인원은 20%는 회장 재량 40%는 15이상에서 40%는 16에서 선출",
        u"문제의 점수는 600 * log(1.1 * user_num / (solver_num + 1)) / log(0.55 * user_num)의 식을 따름",
        u"문제를 첫번째로 푼사람은 다른 문제를 열 수 있음",
        u"문제에 관련된 질문은 호이장에게",
        u"진행 기간은 9/1 ~ 9/5까지",
        u"원래 퀄에 인증을 위해 익스 혹은 키를 가지고 있을 것",
        u"첫번째로 푼 문제가 가장 많은 사람, 15이상의 1등, 16의 1등에게 상품수여 예정"]

        for i in rules:
            t = models.Rule(i)
            db_session.add(t)
            db_session.commit()

        if True:
            for i in xrange(1):
                t = models.Notice("Game Start!")
                db_session.add(t)
                db_session.commit()
        if True:
            import datetime,time
            t = models.User("admin", "admin", "admin", 2)
            t.is_admin = True

            db_session.add(t)
            t = models.User("guest", "guest", "guest", 1)
            t.score = 100
            t.last_auth_success = datetime.datetime.now()
            db_session.add(t)
            time.sleep(1)
            t = models.User("guest2", "guest", "guest", 1)
            t.score = 100
            t.last_auth_success = datetime.datetime.now()
            db_session.add(t)
            t = models.User("guest3", "guest", "guest", 0)
            t.score = 150
            db_session.add(t)
            t = models.User("guest4", "guest", "guest", 0)
            t.score = 300
            db_session.add(t)
            db_session.commit()

        if True:
            r = config.category
            for i in xrange(16):
                cate = r[0] if i < 4 else (r[1] if i < 8 else (r[2] if i < 12 else (r[3] if i < 15 else r[4])))
                t = models.Problem("prob" + str(i), "AAAA", cate, "flag%d"%i)
                if i == 0: 
                    t.open()


                db_session.add(t)
                db_session.commit()


def load_from_conf(f):
    import pickle
    data = pickle.load(f)
    print "ADD %s into Database" % data
    db_session.add(data)
    db_session.commit()

def dump_conf(f, obj):
    import pickle
    pickle.dump(obj, f)


