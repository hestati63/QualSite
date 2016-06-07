#-*- coding: utf-8 -*-
from kapo2016 import app, databases
from sys import argv

if __name__ == "__main__":
    if argv[1] == "initdb":
        databases.init_db()
    elif argv[1] == "run":
        app.run(host = '0.0.0.0', port=10000, debug = True)
