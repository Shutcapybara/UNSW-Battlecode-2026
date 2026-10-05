#!/usr/bin/env python3
"""Print the Mac's memory, cores and free disk (for lanes sizing heavy jobs; Hinata 5 Oct 00:03Z). Reads no data.

    python tools/asahi/sysinfo.py
"""
import json, os, shutil, subprocess


def sysctl(k):
    try:
        return subprocess.run(['sysctl', '-n', k], capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception as e:  # noqa: BLE001
        return f'error {e}'


out = {k: sysctl(k) for k in ('hw.memsize', 'hw.ncpu', 'hw.perflevel0.physicalcpu', 'hw.perflevel1.physicalcpu',
                              'machdep.cpu.brand_string', 'vm.swapusage')}
try:
    out['memory_pressure'] = subprocess.run(['memory_pressure', '-Q'], capture_output=True, text=True,
                                            timeout=20).stdout.strip()[-300:]
except Exception as e:  # noqa: BLE001
    out['memory_pressure'] = f'error {e}'
try:
    vm = subprocess.run(['vm_stat'], capture_output=True, text=True, timeout=10).stdout
    out['vm_stat'] = vm[:1200]
except Exception as e:  # noqa: BLE001
    out['vm_stat'] = f'error {e}'
du = shutil.disk_usage(os.getcwd())
out['disk_free_gb'] = round(du.free / 2 ** 30, 1)
out['memsize_gib'] = round(int(out['hw.memsize']) / 2 ** 30, 1) if out['hw.memsize'].isdigit() else None
print(json.dumps(out, indent=1))
