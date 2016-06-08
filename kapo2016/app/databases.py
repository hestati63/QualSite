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

def init_db():
        import models
        Base.metadata.create_all(bind=engine)
        if True:
            t = models.User("admin", "admin", "admin", 1)
            db_session.add(t)
            db_session.commit()
        if True:
            r = config.category
            for i in xrange(16):
                t = models.Problem("prob" + str(i), "AAAA", r[i % 5])
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
