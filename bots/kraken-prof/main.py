import cProfile, os

TARGET = "/Users/alik/Documents/Projects/UNSW-Battlecode-2026/bots/kraken-v02-bigmap/main.py"
DST = "/tmp/kprof"
os.makedirs(DST, exist_ok=True)
pr = cProfile.Profile()

def __prof_dump():
    pr.disable()
    pr.dump_stats(os.path.join(DST, "p%d.stats" % os.getpid()))
    pr.enable()

src = open(TARGET).read()
needle = "    del _out[:]\n"
inject = "    del _out[:]\n    if round_now % 25 == 0:\n        __prof_dump()\n"
assert src.count(needle) == 1
code = compile(src.replace(needle, inject), TARGET, "exec")
globals_dict = {"__name__": "__main__", "__prof_dump": __prof_dump}
pr.enable()
try:
    exec(code, globals_dict)
finally:
    pr.disable()
    pr.dump_stats(os.path.join(DST, "p%d-final.stats" % os.getpid()))
