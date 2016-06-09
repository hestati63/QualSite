import datetime, math
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from werkzeug.security import generate_password_hash, check_password_hash
from databases import Base, db_session
import config

class Notice(Base):
    __tablename__ = "Notice"
    id = Column(Integer, primary_key = True)
    body = Column(String(512), unique = False)
    upload = Column(DateTime, unique = False)

    def __init__(self, body):
        self.body = body
        self.upload = datetime.datetime.now()

    def __repr__(self):
        return "<post: %d>" % (self.id)

class Rule(Base):
    __tablename__ = "Rule"
    id = Column(Integer, primary_key = True)
    body = Column(String(512), unique = False)

    def __init__(self, body):
        self.body = body

    def __repr__(self):
        return "<rule: %d>" % (self.id)


class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key = True)
    userid = Column(String(32), unique = True)
    password = Column(String(64), unique = False)
    name = Column(String(32), unique = False)

    _type = Column(Integer, unique = False)
    last_auth_success = Column(DateTime, unique = False)
    last_auth_failed  = Column(DateTime, unique = False)
    is_admin = Column(Boolean, unique = False)
    is_open_able = Column(Integer, unique = False)

    def __init__(self, userid=None, passwd=None, name=None, _type = 0):
        self.userid = userid
        self.set_password(passwd)
        self.name = name

        self.solved = 0
        self._type = _type
        self.last_auth_success = None
        self.last_auth_failed = None
        self.is_admin = False
        self.is_open_able = 0

    def __repr__(self):
        return '<User: %s>' % (self.userid)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def calscore(self, s):
        pass

class Problem(Base):
    __tablename__ = 'problems'
    id = Column(Integer, primary_key = True)
    name = Column(String(32), unique = True)
    description = Column(String(512), unique = False)
    flag = Column(String(512), unique = False)
    fb = Column(String(512), unique = False)
    solver = Column(Integer, unique = False)
    is_open = Column(Boolean, unique = False)
    is_hot = Column(Boolean, unique = False)
    openat = Column(DateTime, unique = False)
    dirty = Column(Boolean, unique = False)
    category = Column(String(512), unique = False)

    def __init__(self, name, desc, category, flag):
        self.name = name
        self.description = desc
        self.solver = 0
        self.is_open = False
        self.scores = 0
        self.fb = ""
        self.dirty = True
        assert(category in config.category)
        self.category = category
        self.flag = flag
        self.is_hot = True

    def open(self):
        self.is_open = True
        self.openat = datetime.datetime.now()

    def __repr__(self):
        return '<Problem: %s>' % (self.name)

    def check_flag(self, submit):
        return self.flag == submit

    def add_solver(self, user):
        if self.solver == 0:
            self.fb = user.userid
        if self.is_hot:
            self.is_hot = False
            user.is_open_able += 1
        self.solver += 1
        self.dirty = True
        db_session.commit()

    def update_score(self):
        if self.dirty :
            self.scores = int(config.score_max * math.log(1.1 * config.user_num / (self.solver + 1)) / math.log(0.55 * config.user_num))
        return self.scores


