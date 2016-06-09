#-*- coding: utf-8 -*-
from flask.ext.session import Session
from app import *

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

db = databases.engine.connect()
sess = Session(app)
del sys
from sys import argv

if __name__ == "__main__":
    if argv[1] == "initdb":
        databases.init_db()
    elif argv[1] == "run":
        app.run(host = '0.0.0.0', port=10000, debug = True)
    elif argv[1] == "load":
        with open(argv[2]) as f:
            databases.load_from_conf(f)
