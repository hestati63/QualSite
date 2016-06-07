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
        if False:
            for i in xrange(16):
                t = models.Problem("prob" + str(i), "AAAA")
                if i == 0: 
                    t.is_open = True
                    t.solver = 1
                elif i == 1:
                    t.is_open = True


                db_session.add(t)
                db_session.commit()
