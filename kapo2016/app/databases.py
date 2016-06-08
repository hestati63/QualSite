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
        if True:
            for i in xrange(20):
                t = models.Notice("Game Start!")
                db_session.add(t)
                db_session.commit()
        if True:
            t = models.User("admin", "admin", "admin", 1)
            db_session.add(t)
            db_session.commit()
        if True:
            r = config.category
            for i in xrange(16):
                cate = r[0] if i < 4 else (r[1] if i < 8 else (r[2] if i < 12 else (r[3] if i < 15 else r[4])))
                t = models.Problem("prob" + str(i), "AAAA", cate, "flag%d"%i)
                if i == 0: 
                    t.is_open = True
                    t.solver = 1
                    t.fb = "j31d0"
                elif i == 1:
                    t.is_open = True
                elif i == 5: 
                    t.is_open = True
                    t.solver = 5
                    t.fb = "lbh"


                db_session.add(t)
                db_session.commit()


def load_from_conf(f):
    import pickle
    data1 = pickle.load(f)
    print "ADD %s into Database" % data1
    db_session.add(data1)
    db_session.commit()


def dump_conf(f, obj):
    import pickle

    pickle.dump(obj, f)


