#-*- coding: utf-8 -*-
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_login import LoginManager
import config

app = Flask(__name__, static_url_path='')
app.secret_key = config.SECRET
loginmanager = LoginManager(app)
engine = create_engine(config.db, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
    autoflush=False,
    bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

from front import *
app.register_blueprint(frontend, url_prefix='')

def init_db():
    import models
    Base.metadata.create_all(bind=engine)

def create_test_db():
    t = models.Notice("Game Start!")
    db_session.add(t)

    t = models.User("admin", "admin", "admin", 2)
    t.is_admin = True
    db_session.add(t)

    for i in xrange(5):
        t = models.User("guest%d"%i, "guest", "guest", 1)
        db_session.add(t)

    r = config.category
    for i in xrange(16):
        cate = r[0] if i < 4 else (r[1] if i < 8 else (r[2] if i < 12 else (r[3] if i < 15 else r[4])))
        t = models.Problem("prob" + str(i), "AAAA", cate, "flag%d"%i)
        db_session.add(t)

    db_session.commit()



