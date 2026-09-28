import os, sys, runpy
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import trapsplit_guard as G
sys.stdin = G.TapIn(sys.stdin)
sys.stdout = G.FilterOut(sys.stdout)
runpy.run_path(os.path.join(HERE, 'inner_main.py'), run_name='__main__')
