"""Pure graph counterexamples for the peer entry-contract query; no engine or bot runs.
Extract only the named pure functions from pinned Git blobs. All examples are synthetic,
so their counts are correctness checks, not corpus rates or counterfactual win estimates.
"""
import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path


def read_functions(ref, path, names, env):
    source = subprocess.check_output(['git', 'show', f'{ref}:{path}'], text=True)
    tree = ast.parse(source)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {f.name for f in functions} == set(names)
    exec(compile(ast.Module(body=functions, type_ignores=[]), path, 'exec'), env)
    return hashlib.sha256(source.encode()).hexdigest()


def grid(cells):
    return {p: [q if q in cells else None for q in
                [(p[0], p[1]-1), (p[0]+1, p[1]), (p[0], p[1]+1), (p[0]-1, p[1])]]
            for p in cells}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    env = {'CAP': 16}
    ref = '9b0da8f7848458ebcf2b77aeab293355df741b36'
    hashes = {
        'q_dose.py': read_functions(ref, 'tools/kanazawa/q_dose.py', ['reach', 'occupied'], env),
        'q_cycle.py': read_functions(ref, 'tools/kanazawa/q_cycle.py', ['longest_cycle'], env),
    }
    reach, occupied, cycle = [env[n] for n in ['reach', 'occupied', 'longest_cycle']]
    # Legal alternative leads into a four-cycle. q_dose's chosen-action orbit exemption
    # accepts it, but its alternative count (capacity >= k only) rejects it.
    u, v, w = (0, 0), (1, 0), (-1, 0)
    cells = {u, v, w, (-2, 0), (-2, 1), (-1, 1)}
    nbr = grid(cells)
    chosen = reach(nbr, u, v, set())
    alt = reach(nbr, u, w, set())
    k, length = 8, 2
    orbit = len(alt) >= 3 and cycle(alt + [u], nbr) >= length + 1
    assert len(chosen) == 1 and len(alt) == 4 and orbit
    assert not (len(alt) >= k)
    cases = [dict(name='alternative_orbit_omitted', dose=k, queen_length=length,
                  chosen_capacity=len(chosen), alternative_capacity=len(alt),
                  alternative_cycle=cycle(alt + [u], nbr),
                  peer_alt_count=False, same_predicate_accepts_alternative=True)]
    # The alternative eats while the observed move does not. Even under the peer's
    # relaxed-tail feature, its candidate body leaves a different blocked neck cell.
    u, v, w = (0, 0), (1, 0), (-1, 0)
    neck, tail = (0, -1), (1, -1)
    nbr = grid({u, v, w, (-1, -1), neck, tail, (2, -1), (3, -1), (4, -1)})
    actual_body = [v, u, neck]       # observed non-growing move from [u,neck,tail]
    alternative_body = [w, u, neck, tail]  # alternative eats, retains old tail
    actual_occ = occupied({1: ('A', actual_body)}) - {v}
    alt_occ = occupied({1: ('A', alternative_body)}) - {w}
    wrong = len(reach(nbr, u, w, actual_occ - {w}))
    right = len(reach(nbr, u, w, alt_occ))
    assert wrong >= 4 and right == 2
    cases.append(dict(name='candidate_growth_changes_occupancy', dose=4,
                      actual_body=actual_body, alternative_body=alternative_body,
                      capacity_using_actual_body=wrong, capacity_using_candidate_body=right,
                      peer_alt_accepted=True, candidate_specific_alt_accepted=False))
    # A snapshot containing an occupied tail does not prove that cell has vacated
    # before this queen's action. This is a state/feature discrepancy, not an engine claim.
    body = [(2, 0), (1, 0)]
    assert (1, 0) not in occupied({2: ('A', body)})
    cases.append(dict(name='tail_removal_is_optimistic_assumption', body=body,
                      tail_present_in_snapshot=True, tail_present_in_peer_occupancy=False,
                      interpretation='Tail-vacancy timing/growth/action remains unknown; do not use relaxed feature as immediate-legality proof.'))
    assert all(not (c < 0) for c in range(17))
    assert not (4 < 4) and (4 < 8)
    cases.append(dict(name='strict_thresholds', capacity=4,
                      veto_by_dose={str(k): 4 < k for k in [0, 4, 8, 16]}))
    args.out.write_text(json.dumps(dict(peer_commit=ref, source_sha256=hashes,
        scope='Four synthetic graph/state checks; no simulator, corpus re-count, bot or actual death prevention claim.',
        cases=cases), indent=2) + '\n')
    print(json.dumps(cases, indent=2))


if __name__ == '__main__':
    main()
