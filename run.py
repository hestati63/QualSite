#-*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
del sys

from app import *
db = engine.connect()

if __name__ == "__main__":
    from sys import argv
    if argv[1] == "initdb":
        init_db()
    elif argv[1] == "run":
        app.run(host = '0.0.0.0', port=10000, debug = True)
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
    elif argv[1] == "start":
        start()
    elif argv[1] == 'rebuild':
        rebuild()
