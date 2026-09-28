"""Wrap any text-protocol Python bot in the Jet frame wrapper.

usage: make_frame.py HOST_BOT_DIR OUT_BOT_DIR [FRAME_CONFIG_PY]
Copies HOST's *.py into OUT/host/, the wrapper main.py (template: bots/jet-v06-* or the path in JET_FRAME_MAIN)
and a frame_config.py (default: seat B plays in seat A's frame on the ten live-pool sizes).
The host's main.py must expose main() and read stdin via sys.stdin.readline (all protocol.py-family bots do).
"""
import os, shutil, sys
from pathlib import Path
host, out = Path(sys.argv[1]), Path(sys.argv[2])
tmpl = Path(os.environ.get('JET_FRAME_MAIN', Path(__file__).with_name('frame_wrapper_main.py')))
if out.exists(): sys.exit(f'{out} exists')
(out / 'host').mkdir(parents=True)
for f in host.glob('*.py'): shutil.copy(f, out / 'host' / f.name)
if not (out / 'host' / 'main.py').exists(): sys.exit('host has no main.py')
shutil.copy(tmpl, out / 'main.py')
cfg = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(__file__).with_name('frame_config_P.py')
shutil.copy(cfg, out / 'frame_config.py')
(out / 'bot.toml').write_text('[project]\nlanguage = "py"\ninclude = ["*.py"]\n')
print('built', out, 'host', host.name)
