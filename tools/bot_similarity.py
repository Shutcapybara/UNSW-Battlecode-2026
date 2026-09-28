#!/usr/bin/env python3
"""Snapshot the ledger and fit strength, map affinity and cyclic matchup effects.

.venv/bin/python tools/bot_similarity.py --output experiment_data/similarity-DATE
Install tools/requirements-similarity.txt once. All computations are local.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tomllib

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/battlecode-matplotlib")
import numpy as np
from scipy.special import expit

from game_stats import ROOT, digest, read_parquet, write_parquet
from performance_model import fit, metrics, predictions, subset, unpack


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def source_aliases(rows):
    """Collapse README-only revisions only when frozen packaging excludes them.

    Preserve all non-Markdown inputs and the bot.toml hash. With no manifest,
    retain the original source ID conservatively. The shared ledger is untouched.
    """
    wanted={(r[k],r[k+'_sha256']) for r in rows for k in ('bot_a','bot_b')}
    aliases={key:key[1] for key in wanted}
    manifests=list((ROOT/'experiment_data').glob('*/manifest.json'))
    manifests+=list((ROOT/'build').glob('*/manifest.json'))
    for path in manifests:
        manifest=json.loads(path.read_text())
        for key,files in manifest.get('hashes',{}).items():
            if not isinstance(files,dict) or 'bot.toml' not in files:
                continue
            name=key.removeprefix('bots/');identity=(name,digest(files))
            if identity not in wanted:
                continue
            config=path.parent/'sources/bots'/name/'bot.toml'
            if not config.exists():
                continue
            content=config.read_bytes()
            if hashlib.sha256(content).hexdigest()!=files['bot.toml']:
                raise ValueError(f'Frozen bot configuration changed: {config}')
            includes=tomllib.loads(content.decode())['project'].get('include',[])
            selected={k:v for k,v in files.items() if not k.lower().endswith('.md') or
                      any(fnmatch.fnmatch(k,pattern) for pattern in includes)}
            aliases[identity]=digest(selected)
    return aliases


def dataset(rows, aliases=None):
    # Analysis strata never mix sandbox/native or toolkits. Identical fixtures
    # contribute once, so repeated deterministic experiments don't gain weight.
    native = [r for r in rows if r['mode'] == 'native' and r['runner_version'] == 'unswbc 1.0.0']
    aliases=aliases or {(r[k],r[k+'_sha256']):r[k+'_sha256'] for r in rows for k in ('bot_a','bot_b')}
    def identity(r,k):
        return r[k],aliases[r[k],r[k+'_sha256']]
    grouped = defaultdict(list)
    for r in native:
        key=(identity(r,'bot_a'),identity(r,'bot_b'),r['map_sha256'],r['mode'],r['runner_version'],r['seed'])
        grouped[digest(key)].append(r)
    games = []
    conflicts = []
    for fixture, copies in grouped.items():
        scores = [1 if r['outcome'] == 'A' else 0 if r['outcome'] == 'B' else .5 for r in copies]
        if len(set(scores)) > 1:
            conflicts.append(fixture)
        # Keep the mean if independent runs actually disagree; expose the count.
        games.append((copies[0], float(np.mean(scores))))
    identities = sorted({identity(r,k) for r,y in games for k in ('bot_a','bot_b')})
    idx = {key:i for i,key in enumerate(identities)}
    maps = sorted({(r['map'], r['map_sha256']) for r,y in games})
    midx = {key:i for i,key in enumerate(maps)}
    counts = Counter(name for name,sha in identities)
    labels = [name + ('@'+sha[:7] if counts[name] > 1 else '') for name,sha in identities]
    a, b, board, target = [], [], [], []
    for r,y in games:
        a.append(idx[identity(r,'bot_a')]); b.append(idx[identity(r,'bot_b')])
        board.append(midx[r['map'],r['map_sha256']]); target.append(y)
    data = (np.array(a), np.array(b), np.array(board), np.array(target))
    core_keys = {identity(r,k) for r in rows if r['source'] == 'bot_field_tournament' for k in ('bot_a','bot_b')}
    core = np.array([idx[key] for key in identities if key in core_keys])
    meta = dict(snapshot_games=len(rows), native_games=len(native), unique_fixtures=len(games),
                excluded_runtime_games=len(rows)-len(native), repeated_fixtures_removed=len(native)-len(games),
                conflicting_fixture_count=len(conflicts), conflicting_fixtures=conflicts,
                labels=labels, identities=identities, maps=maps, core=core.tolist(),
                source_counts=dict(Counter(r['source'] for r in rows)),
                runtime_fault_games=sum(bool(r['runtime_faults']) for r in native))
    meta['source_aliases']=[dict(name=name,source_sha256=sha,analysis_sha256=h) for (name,sha),h in sorted(aliases.items())]
    return data, meta


def fit_models(data, meta, out):
    n,m = len(meta['labels']),len(meta['maps'])
    a,b,board,y = data
    groups = np.minimum(a,b)*n+np.maximum(a,b)
    unique = np.unique(groups)
    shuffled = np.random.default_rng(20260925).permutation(unique)
    test_groups, validation_groups, _ = np.split(shuffled, [len(unique)//10, len(unique)//4])
    test = np.isin(groups,test_groups); val = np.isin(groups,validation_groups)
    train = ~(test|val)
    candidates = []
    for name,q,use_maps,ridge in [('strength',0,False,5.), ('map_strength',0,True,5.),
                                  ('map_cycle_rank2',1,True,5.), ('map_cycle_rank4',2,True,5.),
                                  ('map_cycle_rank8',4,True,5.), ('map_cycle_rank4_ridge20',2,True,20.)]:
        starts = [0,1] if q else [0]
        models = [fit(subset(data,train),n,m,q,use_maps,ridge,seed=42+i,
                      start=candidates[1]['model'] if q else None) for i in starts]
        model = min(models,key=lambda r:r['objective'])
        p = predictions(model,data,n,m)
        result = dict(name=name, model=model, training=metrics(y[train],p[train]),
                      validation=metrics(y[val],p[val]), test=metrics(y[test],p[test]))
        candidates.append(result)
        print(name, 'validation', round(result['validation']['log_loss'],5),
              'test', round(result['test']['log_loss'],5), 'converged',model['success'],flush=True)
    winner = min(candidates,key=lambda r:r['validation']['log_loss'])
    chosen = winner['model']
    # Test was held aside from both optimization and model selection. Compare
    # paired test losses with an unordered-pair block bootstrap.
    base = candidates[1]['model']
    pb,pc = predictions(base,data,n,m), predictions(chosen,data,n,m)
    def losses(p):
        p=np.clip(p,1e-9,1-1e-9)
        return -y*np.log(p)-(1-y)*np.log1p(-p)
    delta = losses(pb)-losses(pc)
    tg = np.unique(groups[test]); sums=np.array([delta[test & (groups==g)].sum() for g in tg])
    counts=np.array([(test & (groups==g)).sum() for g in tg])
    rng=np.random.default_rng(73); draws=rng.integers(0,len(tg),(1000,len(tg)))
    boot=sums[draws].sum(axis=1)/counts[draws].sum(axis=1)
    validations = []
    for result in candidates:
        model_info={k:v for k,v in result['model'].items() if k!='x'}
        validations.append({k:v for k,v in result.items() if k!='model'} | dict(model=model_info))
    report=dict(selected=winner['name'], seed=20260925, split_games=dict(train=int(train.sum()),
                validation=int(val.sum()),test=int(test.sum())),
                split_pairs=dict(train=len(unique)-len(test_groups)-len(validation_groups),
                                 validation=len(validation_groups),test=len(test_groups)),
                models=validations, test_cycle_improvement=float(delta[test].mean()),
                test_cycle_improvement_pair_bootstrap_95=np.quantile(boot,[.025,.975]).tolist())
    save_json(out/'validation.json',report)
    np.savez_compressed(out/'heldout_predictions.npz', target=y[test], groups=groups[test],
                        map_strength=pb[test], selected=pc[test])
    final=fit(data,n,m,chosen['q'],chosen['maps'],chosen['ridge'],start=chosen)
    save_json(out/'model.json',{k:v for k,v in final.items() if k!='x'})
    np.savez_compressed(out/'fit.npz',x=final['x'],a=a,b=b,board=board,target=y)
    print('Selected',winner['name'],'final converged',final['success'],flush=True)
    return final


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--snapshot',type=Path,default=ROOT/'game_stats.parquet')
    parser.add_argument('--reuse-fit',action='store_true',help='Use this output directory\'s frozen data and fitted model')
    parser.add_argument('--fit-only',action='store_true')
    args=parser.parse_args()
    out=args.output.resolve()
    if args.reuse_fit:
        meta=json.loads((out/'snapshot.json').read_text())
        fitted=np.load(out/'fit.npz'); data=tuple(fitted[k] for k in ('a','b','board','target'))
        model=json.loads((out/'model.json').read_text()) | dict(x=fitted['x'])
    else:
        out.mkdir(parents=True,exist_ok=False)
        rows=read_parquet(args.snapshot)
        write_parquet(out/'games.parquet',rows)
        previous=args.snapshot.parent/'snapshot.json'
        saved=json.loads(previous.read_text()) if args.snapshot.name=='games.parquet' and previous.exists() else {}
        aliases=({(r['name'],r['source_sha256']):r['analysis_sha256'] for r in saved['source_aliases']}
                 if saved.get('snapshot_sha256')==digest(rows) and 'source_aliases' in saved else source_aliases(rows))
        data,meta=dataset(rows,aliases)
        meta['snapshot_at']=datetime.now(timezone.utc).isoformat()
        meta['snapshot_sha256']=digest(rows)
        save_json(out/'snapshot.json',meta)
        (out/'analysis_code').mkdir()
        for name in ('bot_similarity.py','performance_model.py','similarity_report.py','import_field_stats.py'):
            shutil.copy2(ROOT/'tools'/name,out/'analysis_code'/name)
        print('Snapshot',len(rows),'games;',len(meta['labels']),'source versions;',len(meta['core']),'original bots',flush=True)
        model=fit_models(data,meta,out)
    if not args.fit_only:
        from similarity_report import report
        report(out,data,meta,model)


if __name__ == '__main__':
    main()
