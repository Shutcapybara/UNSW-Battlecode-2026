"""Compare reconstructed Python v5 rows with HB1's C++ feature mirror.

This validates extraction/mirror consistency, not parity with captured runtime
observations. Gameplay snapshots remain unchanged. All compiler output and JSON
reports go into --out, which should be a directory below build/ or /tmp.
"""
import argparse
import csv
import hashlib
import importlib.metadata
import io
import json
import math
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
RECON = ROOT / 'tools/team_recon_claude'
sys.path.insert(0, str(RECON))
import features_v5

CPP_SOURCE = ROOT / 'tools/hb1/cpp/feat_parity.cpp'
CPP_HEADER = ROOT / 'bots/carthage-05-free-sprint/hb1_features.hpp'
MODEL_HEADER = ROOT / 'bots/hb1-04-deployable/hb1_direction_compact.hpp'
TOLERANCE = 1e-6


def checked(command, **kwargs):
    result = subprocess.run(command, capture_output=True, text=True, **kwargs)
    if result.returncode:
        raise RuntimeError(f'command failed ({result.returncode}): {command}\n{result.stderr}')
    return result.stdout


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def model_features():
    text = MODEL_HEADER.read_text()
    match = re.search(r'dirc_feats\[\]\s*=\s*\{(.*?)\};', text, re.S)
    if match is None:
        raise ValueError(f'dirc_feats[] not found in {MODEL_HEADER}')
    names = re.findall(r'"([^"]+)"', match.group(1))
    expected = re.search(r'dirc_n_feat\s*=\s*(\d+)', text)
    if not names or len(names) != len(set(names)) or expected is None or len(names) != int(expected.group(1)):
        raise ValueError('direction model feature list is empty, duplicated or inconsistent')
    return names


def parity(replay, side, out):
    names = model_features()
    out.mkdir(parents=True, exist_ok=True)
    temporary_source = out / 'feat_parity_precision17.cpp'
    executable = out / 'feat_parity_precision17'
    source = CPP_SOURCE.read_text()
    marker = 'std::ios::sync_with_stdio(false);'
    if source.count(marker) != 1:
        raise ValueError('unexpected feature parity source: main precision insertion is ambiguous')
    source = '#include <iomanip>\n' + source.replace(marker, marker + '\n    std::cout << std::setprecision(17);')
    temporary_source.write_text(source)
    compile_command = ['g++', '-O2', '-std=c++17', '-I', str(CPP_HEADER.parent), str(temporary_source), '-o', str(executable)]
    checked(compile_command)
    dump_command = [sys.executable, str(ROOT / 'tools/hb1/cpp/dump_blocks.py'), str(replay), side]
    dump = checked(dump_command)
    cpp_csv = checked([str(executable)], input=dump)
    del dump
    reader = csv.DictReader(io.StringIO(cpp_csv))
    python_rows, game, descriptor = features_v5.extract(str(replay), side, 0)
    cpp_columns = set(reader.fieldnames or [])
    python_columns = set(python_rows[0]) if python_rows else set()
    for row in python_rows[1:]:
        python_columns.intersection_update(row)
    common = sorted((cpp_columns & python_columns) - {'dragon', 'round'})
    missing_python = sorted(set(names) - python_columns)
    missing_cpp = sorted(set(names) - cpp_columns)
    cpp_keys = []
    python_keys = [(int(row['dragon']), int(row['round'])) for row in python_rows]
    errors, examples = {}, []
    max_difference = 0.0
    # Keep one C++ row at a time: long games already retain the Python rows.
    for row_index, cpp in enumerate(reader):
        key = (int(cpp['dragon']), int(cpp['round']))
        cpp_keys.append(key)
        if row_index >= len(python_rows) or key != python_keys[row_index]:
            continue
        py = python_rows[row_index]
        for name in common:
            a, b = float(py[name]), float(cpp[name])
            equal = (math.isnan(a) and math.isnan(b)) or math.isclose(a, b, rel_tol=0.0, abs_tol=TOLERANCE)
            if math.isfinite(a) and math.isfinite(b):
                max_difference = max(max_difference, abs(a - b))
            if not equal:
                errors[name] = errors.get(name, 0) + 1
                if len(examples) < 20:
                    examples.append({'row': row_index, 'dragon': py['dragon'], 'round': py['round'],
                                     'feature': name, 'python': str(a), 'cpp': str(b)})
    exact_keys = cpp_keys == python_keys
    duplicate_keys = len(set(python_keys)) != len(python_keys) or len(set(cpp_keys)) != len(cpp_keys)
    reconstruction_checks = dict(game.checks)
    bad_checks = {name: value for name, value in reconstruction_checks.items()
                  if value and (name.endswith('_bad') or name.endswith('_mismatch'))}
    required_errors = {name: count for name, count in errors.items() if name in names}
    ok = bool(python_rows) and exact_keys and not duplicate_keys and not missing_python and not missing_cpp and not errors and not bad_checks
    sources = [CPP_SOURCE, CPP_HEADER, MODEL_HEADER, RECON / 'features_v5.py',
               RECON / 'features_view.py', RECON / 'roundblock.py', RECON / 'recon.py',
               ROOT / 'tools/hb1/cpp/dump_blocks.py']
    report = {
        'status': 'PASS' if ok else 'FAIL',
        'scope': 'Python replay-reconstructed v5 rows versus C++ hb1::Proc; not captured runtime observation parity',
        'local_unswbc_version': importlib.metadata.version('unswbc'),
        'replay': str(replay), 'replay_sha256': digest(replay), 'side': side,
        'map': game.board.name, 'rounds': game.round,
        'python_rows': len(python_rows), 'cpp_rows': len(cpp_keys),
        'actor_coverage': {
            'minimum_round': min((row['round'] for row in python_rows), default=None),
            'maximum_round': max((row['round'] for row in python_rows), default=None),
            'round350_plus_turns': sum(row['round'] >= 350 for row in python_rows),
            'queen_turns': sum(row['dragon'] == (0 if side == 'A' else 1) for row in python_rows),
            'child_turns': sum(not row['mem_initial'] for row in python_rows),
            'turns_with_messages': sum(row['n_msgs'] > 0 for row in python_rows),
        },
        'keys_equal_in_order': exact_keys, 'duplicate_dragon_round_keys': duplicate_keys,
        'first_key_mismatches': [{'index': i, 'python': a, 'cpp': b}
                               for i, (a, b) in enumerate(zip(python_keys, cpp_keys)) if a != b][:10],
        'absolute_tolerance': TOLERANCE, 'relative_tolerance': 0.0,
        'cpp_significant_digits': 17, 'model_feature_count': len(names),
        'model_features': names, 'common_numeric_feature_count': len(common),
        'missing_model_features_python': missing_python, 'missing_model_features_cpp': missing_cpp,
        'model_feature_mismatches': required_errors, 'all_common_feature_mismatches': errors,
        'mismatch_examples': examples, 'maximum_absolute_difference': max_difference,
        'reconstruction_checks': reconstruction_checks, 'bad_reconstruction_checks': bad_checks,
        'source_sha256': {str(path.relative_to(ROOT)): digest(path) for path in sources},
        'temporary_cpp_sha256': digest(temporary_source), 'compile_command': compile_command,
        'protocol_reconstruction': 'roundblock.build_block proto3 after first parentless turn, or from first child turn, as existing v5/dump tooling',
        'excluded_python_columns': sorted(python_columns - cpp_columns),
    }
    report_path = out / 'hb1-local-parity.json'
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ('status', 'scope', 'python_rows', 'cpp_rows',
                       'keys_equal_in_order', 'model_feature_count', 'common_numeric_feature_count',
                       'model_feature_mismatches', 'all_common_feature_mismatches',
                       'maximum_absolute_difference', 'reconstruction_checks')} | {'report': str(report_path)}, indent=2))
    return ok


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay', type=Path, required=True)
    parser.add_argument('--side', choices=('A', 'B'), required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    replay, out = args.replay.resolve(), args.out.resolve()
    if not replay.is_file():
        parser.error(f'replay file does not exist: {replay}')
    try:
        ok = parity(replay, args.side, out)
    except (ValueError, RuntimeError, OSError) as error:
        parser.exit(2, f'{error}\n')
    raise SystemExit(0 if ok else 1)


if __name__ == '__main__':
    main()
