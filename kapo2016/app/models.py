import datetime
import math
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from werkzeug.security import generate_password_hash, check_password_hash
from databases import Base
from config import *

class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key = True)
    userid = Column(String(32), unique = True)
    password = Column(String(64), unique = False)
    name = Column(String(32), unique = False)

    solved = Column(Integer, unique = False)
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
        return '<User %r>' % (self.userid)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_solved(self):
        c_solved = self.solved
        r = []
        for i in xrange(psize):
            r.append((c_solved >> i) & 1)
        return r

    def solved_list(self):
        r = []
        for i in xrange(psize):
            if ((self.solved >> i) & 1):
                r.append(i)
        return r

    def solve(self, s):
        self.solved |= (1 << s)
        return self.solved

    def calscore(self, s):
        pass

class Problem(Base):
    __tablename__ = 'problems'
    id = Column(Integer, primary_key = True)
    name = Column(String(32), unique = False)
    description = Column(String(512), unique = False)
    fb = Column(String(512), unique = False)
    solver = Column(Integer, unique = False)
    is_open = Column(Boolean, unique = False)

    def __init__(self, name, desc):
        self.name = name
        self.description = desc
        self.solver = 0
        self.is_open = False
        self.scores = 0

    def score(self):
        self.scores = int(score_max * math.log(1.1 * user_num / (self.solver + 1)) / math.log(1.1 * user_num / 2))
        return self.scores


