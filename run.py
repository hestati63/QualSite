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
    elif argv[1] == "sass":
        import codecs, os
        from scss import Scss
        css = Scss()
        src = argv[2]
        dst = argv[3]
        cwd = os.getcwd()
        os.chdir('/'.join(src.split("/")[:-1]))
        source = codecs.open(src.split("/")[-1], 'r', encoding='utf-8').read()
        output = css.compile(source)
        os.chdir(cwd)
        outfile = codecs.open(dst, 'w', encoding='utf-8')
        outfile.write(output)
        outfile.close()
