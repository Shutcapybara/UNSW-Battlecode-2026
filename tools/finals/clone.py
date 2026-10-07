"""Warm-start one actor from instrumented incumbent selections; parity is not strength."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import numpy as np
import torch
from torch.nn import functional as F
from model import Scorer, export_header


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data', type=Path, nargs='+', required=True)
    ap.add_argument('--actor', choices=['action', 'sonar'], required=True)
    ap.add_argument('--epochs', type=int, default=5)
    ap.add_argument('--batch-size', type=int, default=256)
    ap.add_argument('--seed', type=int, default=61006)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    torch.set_num_threads(1)
    torch.manual_seed(args.seed)
    rng = np.random.default_rng(args.seed)
    args.output.mkdir(parents=True, exist_ok=True)
    loaded = [dict(np.load(p)) for p in args.data]
    if args.actor == 'action':
        x = np.concatenate([d['x'] for d in loaded])
        features = np.concatenate([d['action_features'] for d in loaded])
        mask = np.concatenate([d['action_mask'] for d in loaded])
        labels = np.concatenate([d['action'] for d in loaded])
        valid = np.concatenate([d['actor_valid'] for d in loaded])
    else:
        x = np.concatenate([np.repeat(d['x'], 4, axis=0) for d in loaded])
        features = np.concatenate([d['sonar_features'].reshape(-1, 5, 32) for d in loaded])
        mask = np.concatenate([d['sonar_mask'].reshape(-1, 5) for d in loaded])
        labels = np.concatenate([d['sonar'].reshape(-1) for d in loaded])
        valid = np.concatenate([np.repeat(d['actor_valid'], 4) for d in loaded])
    if np.any(labels != 0):
        raise ValueError('Warm-start inputs must be incumbent BASELINE labels')
    # Fixed singleton menus have no choice loss; avoid inflating clone accuracy with them.
    keep = valid & (mask.sum(axis=1) > 1)
    x, features, mask, labels = [torch.as_tensor(a[keep]) for a in (x, features, mask, labels)]
    if not len(x):
        raise ValueError('No selectable decisions to clone')
    model = Scorer()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    started = time.monotonic()
    losses = []
    for epoch in range(args.epochs):
        order = rng.permutation(len(x))
        loss_sum = 0
        for begin in range(0, len(x), args.batch_size):
            idx = order[begin:begin + args.batch_size]
            logits = model(x[idx], features[idx]).masked_fill(~mask[idx], -1e9)
            loss = F.cross_entropy(logits, labels[idx])
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            loss_sum += float(loss.detach()) * len(idx)
        losses.append(loss_sum / len(x))
        print(args.actor, 'epoch', epoch + 1, 'loss', losses[-1], flush=True)
    correct = 0
    with torch.no_grad():
        for begin in range(0, len(x), args.batch_size):
            idx = slice(begin, begin + args.batch_size)
            pred = model(x[idx], features[idx]).masked_fill(~mask[idx], -1e9).argmax(dim=1)
            correct += int((pred == labels[idx]).sum())
    checkpoint = args.output / f'{args.actor}.pt'
    torch.save(dict(actor=args.actor, state=model.state_dict(), seed=args.seed), checkpoint)
    export_header(model, args.output / f'{args.actor}_model.hpp', args.actor)
    report = dict(actor=args.actor, rows=len(x), accuracy=correct / len(x), loss=losses,
                  optimization_seconds=time.monotonic() - started, epochs=args.epochs,
                  checkpoint_sha256=hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
                  data=[dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in args.data],
                  verdict='Incumbent clone on training rows only; no held-out strength claim')
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
