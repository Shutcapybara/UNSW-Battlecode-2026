import sys
sys.path.insert(0,'tools/ouroboros')
from mapview import load_map
m=load_map(open(sys.argv[1]).read())
print({k:(type(v).__name__, (len(v) if hasattr(v,'__len__') else v)) for k,v in m.items()})
