"""Build a Jet income-density dispatcher bot around any Python host bot.

usage: make_dispatch.py HOST_BOT_DIR OUT_BOT_DIR [--ladder LADDER_DIR]
The dispatcher (main.py) and ladder/ (v13 + light-veto params) are copied from
bots/jet-v02-richladder; HOST_BOT_DIR's *.py files become host/ verbatim.
The host must be a Python bot whose main.py exposes main() (all current
sinbad/fafnir/gavroche/witten/newton/serre derivatives do).
"""
import shutil, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
host, out = Path(sys.argv[1]), Path(sys.argv[2])
ladder = Path(sys.argv[sys.argv.index('--ladder') + 1]) if '--ladder' in sys.argv else REPO / 'bots/jet-v02-richladder/ladder'
tmpl = REPO / 'bots/jet-v02-richladder'
if out.exists(): sys.exit(f'{out} exists')
(out / 'host').mkdir(parents=True)
for f in host.glob('*.py'): shutil.copy(f, out / 'host' / f.name)
shutil.copytree(ladder, out / 'ladder', ignore=shutil.ignore_patterns('__pycache__'))
shutil.copy(tmpl / 'main.py', out / 'main.py'); shutil.copy(tmpl / 'bot.toml', out / 'bot.toml')
src = (out / 'main.py').read_text()
(out / 'main.py').write_text(src.replace('Doctrines: host/ = gavroche-v32-supported-divecap (verbatim);', f'Doctrines: host/ = {host.name} (verbatim; built by tools/jet/make_dispatch.py);'))
if not (out / 'host' / 'main.py').exists(): sys.exit('host has no main.py')
print('built', out)
