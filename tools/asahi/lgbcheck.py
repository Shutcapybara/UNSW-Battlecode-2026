#!/usr/bin/env python3
"""Check that the learn venv can import and train LightGBM (and import torch) with the environment jobd gives learn
jobs (learn_dyld_env). Tiny synthetic fit, a few seconds. Exit 0 on success. (5 Oct 04:45Z, after libomp failures.)"""
import os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.asahi.jobd import learn_dyld_env  # noqa: E402
main = Path(os.environ.get('ASAHI_MAIN', ROOT.parent / 'UNSW-Battlecode-2026'))
venv = main / 'build/learn/venv'
env = dict(os.environ, **learn_dyld_env(venv))
print('DYLD_LIBRARY_PATH =', env.get('DYLD_LIBRARY_PATH'))
code = ("import numpy as np, lightgbm as lgb, torch;"
        "X=np.random.RandomState(0).rand(2000,10);y=(X[:,0]+X[:,1]>1).astype(int);"
        "m=lgb.train({'objective':'binary','verbose':-1,'num_threads':4},lgb.Dataset(X,y),20);"
        "p=m.predict(X);print('lightgbm',lgb.__version__,'acc',((p>.5)==y).mean(),'torch',torch.__version__,torch.get_num_threads())")
r = subprocess.run([str(venv / 'bin/python'), '-c', code], env=env)
sys.exit(r.returncode)
