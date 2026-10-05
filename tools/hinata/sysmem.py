"""Hinata: report the host's physical memory, CPU count and free disk for D-065 §C's memory statement (no data read, no fit).
Usage (learn queue, not heavy): {"kind": "script", "script": "tools/hinata/sysmem.py", "argv": [], "heavy": false, "by": "hinata"}"""
import json, os, platform, shutil, subprocess


def main():
    out = dict(platform=platform.platform(), machine=platform.machine(), cpu_count=os.cpu_count())
    try:
        out['phys_bytes'] = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
    except (ValueError, OSError, AttributeError):
        out['phys_bytes'] = None
    try:
        out['hw_memsize'] = int(subprocess.run(['sysctl', '-n', 'hw.memsize'], capture_output=True, text=True, timeout=10).stdout.strip())
    except Exception as e:  # noqa: BLE001
        out['hw_memsize'] = f'unavailable: {e}'
    try:
        vm = subprocess.run(['vm_stat'], capture_output=True, text=True, timeout=10).stdout
        out['vm_stat_head'] = vm.splitlines()[:8]
    except Exception:  # noqa: BLE001
        pass
    du = shutil.disk_usage('.'); out['disk_free_gb'] = round(du.free / 1e9, 1)
    gb = (out['hw_memsize'] if isinstance(out['hw_memsize'], int) else out['phys_bytes'] or 0) / 2 ** 30
    out['memory_gib'] = round(gb, 1); out['sixty_pct_gib'] = round(0.6 * gb, 1)
    os.makedirs('build/learn/hinata', exist_ok=True)
    with open('build/learn/hinata/sysmem.json', 'w') as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
