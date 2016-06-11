import datetime, math
from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, ForeignKey, desc, asc
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
from . import Base, db_session
import config

solves = Table('solves',
         Base.metadata,
         Column('user_id', Integer, ForeignKey('User.id')),
         Column('problem_id',Integer, ForeignKey('Problem.id'))
        )

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

    fbs = relationship("Problem", backref = "fb")
    _type = Column(Integer, unique = False)
    last_auth_success = Column(DateTime, unique = False)
    last_auth_failed  = Column(DateTime, unique = False)
    admin = Column(Boolean, unique = False)
    openable = Column(Integer, unique = False)
    score = Column(Integer, unique = False)
    solves = relationship('Problem', secondary=solves, backref=backref('solvers', lazy='dynamic'), lazy='dynamic')


    def __init__(self, userid=None, passwd=None, name=None, _type = 0):
        self.userid = userid
        self.set_password(passwd)
        self.name = name

        self.solved = 0
        self._type = _type
        self.last_auth_success = None
        self.last_auth_failed = None
        self.admin = False
        self.openable = 0
        self.score = 0

    def rebuild_score(self):
        self.score = 0
        for problem in self.solves:
            self.score += problem.scores
        db_session.commit()

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

    def get_rank(self):
        if self.admin: 
            return 0
        else:
            return User.query.filter_by(admin = False).order_by(desc(User.score), asc(User.last_auth_success)).all().index(self) + 1



class Problem(Base):
    __tablename__ = 'Problem'
    id = Column(Integer, primary_key = True)
    name = Column(String(32), unique = True)
    description = Column(String(512), unique = False)
    category = Column(String(512), unique = False)
    flag = Column(String(512), unique = False)
    scores = Column(Integer, unique = False)

    open = Column(Boolean, unique = False)
    openat = Column(DateTime, unique = False)
    hot = Column(Boolean, unique = False)
    user_id = Column(Integer, ForeignKey('User.id'))
    solver = Column(Integer, unique = False)


    def __init__(self, name, desc, category, flag):
        self.name = name
        self.description = desc
        self.solver = 0
        self.open = False
        assert(category in config.category)
        self.category = category
        self.flag = flag
        self.hot = True
        self.set_score(update_score(0))

    def open(self, user = None):
        info = ""
        if user:
            if user.openable <= 0:
                return False
            user.openable -= 1
            info = "<a href=\"%s\">%s</a> open <a href=\"%s\"><b>[%s]</b>%s</a>!" %(url_for('frontend.show_user', _id=current_user.id), current_user.userid, url_for('frontend.show', _id = problem.id), problem.category, problem.name)
        else:
            info = "<a href=\"%s\"><b>[%s]</b>%s</a> open!" %(url_for('frontend.show', _id = problem.id), problem.category, problem.name)
        self.open = True
        self.openat = datetime.datetime.now()
        db_session.add(Notice(info))
        db_session.commit()
        return True


    def __repr__(self):
        return '<Problem: %s>' % (self.name)

    def check_flag(self, submit):
        return self.flag == submit

    def add_solver(self, user):
        msg = "good!"
        if user.admin:
            return "admin cannot auth"

        elif self in user.solves:
            return "already authed"

        elif self.solver == 0:
            self.fb = user
            notice = Notice("Wow! <a href=\"%s\">%s</a> <span class=\"red-text\">break</span> <a href=\"%s\"><b>[%s]</b>%s</a>!!!!" %(url_for('frontend.show_user', _id=current_user.id), current_user.userid, url_for('frontend.show', _id = problem.id), problem.category, problem.name))
            db_session.add(notice)
            msg = "U got Breakthrough!!! Plz open new problem!!!"

        score_before = self.scores

        for solver in self.solvers:
            solver.score -= score_before
        user.solves.append(self)

        if self.is_hot:
            self.hot = False
            user.openable += 1
        self.solver += 1

        score_now = update_score(self.solver)
        self.scores = score_now

        for solver in self.solvers:
            solver.score += score_now
        user.score += score_now
        user.last_auth_success = datetime.datetime.now()
        db_session.commit()
        return msg

    def set_score(self, score):
        self.scores = score

def update_score(count):
    user_num = User.query.count()
    return int(config.score_max * math.log(1.1 * user_num / (count + 1)) / math.log(0.55 * user_num))


