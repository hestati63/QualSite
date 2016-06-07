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
        for i in xrange(16):
            t = models.Problem(str(i), "AAAA")
            db_session.add(t)
            db_session.commit()
