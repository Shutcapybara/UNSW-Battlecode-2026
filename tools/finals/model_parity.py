"""Check exported float32 C++ candidate scores and argmax against the trained actor."""
import argparse
import json
from pathlib import Path
import subprocess
import numpy as np
import torch
from model import Scorer, export_header


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--checkpoint', type=Path, required=True)
    ap.add_argument('--data', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--rows', type=int, default=1000)
    args = ap.parse_args()
    torch.set_num_threads(1)
    checkpoint = torch.load(args.checkpoint, map_location='cpu', weights_only=True)
    actor = checkpoint['actor']
    model = Scorer(); model.load_state_dict(checkpoint['state']); model.eval()
    args.output.mkdir(parents=True, exist_ok=True)
    header = args.output / 'model.hpp'
    export_header(model, header, actor)
    cpp = f'''#include "model.hpp"
#include <iostream>
#include <iomanip>
int main() {{
    int count;
    std::cout << std::setprecision(9);
    while(std::cin>>count) {{
        std::array<int32_t,1193> x{{}};for(auto& v:x)std::cin>>v;
        auto encoded=finals::exported::{actor}_encode(x);
        for(int i=0;i<count;i++) {{
            std::array<float,32> f{{}};for(auto& v:f)std::cin>>v;
            if(i)std::cout<<' ';std::cout<<finals::exported::{actor}_score(encoded,f);
        }}
        std::cout<<'\\n';
    }}
}}'''
    source = args.output / 'test.cpp'; source.write_text(cpp)
    exe = args.output / 'test'
    subprocess.run(['g++', '-std=c++20', '-O2', str(source), '-o', str(exe)], check=True, timeout=120)
    data = np.load(args.data)
    x = data['x']
    features, mask = data[actor + '_features'], data[actor + '_mask']
    if actor == 'sonar':
        x = np.repeat(x, 4, axis=0)
        features, mask = features.reshape(-1, 5, 32), mask.reshape(-1, 5)
    eligible = np.flatnonzero(mask.sum(axis=1) > 1)
    indices = eligible[np.linspace(0, len(eligible) - 1, min(args.rows, len(eligible))).astype(int)]
    inputs, expected = [], []
    with torch.no_grad():
        for i in indices:
            feats = features[i][mask[i]]
            expected.append(model(torch.as_tensor(x[i]).unsqueeze(0), torch.as_tensor(feats).unsqueeze(0))[0].numpy())
            inputs.append(str(len(feats)) + ' ' + ' '.join(map(str, x[i])) + ' ' +
                          ' '.join(format(float(v), '.9g') for v in feats.flat))
    proc = subprocess.run([str(exe.resolve())], input='\n'.join(inputs) + '\n',
                          capture_output=True, text=True, check=True, timeout=60)
    actual = [np.fromstring(line, sep=' ') for line in proc.stdout.splitlines()]
    if len(actual) != len(expected):
        raise ValueError('Missing C++ replies')
    error = max(float(np.max(np.abs(a - b))) for a, b in zip(actual, expected))
    choices = sum(np.argmax(a) != np.argmax(b) for a, b in zip(actual, expected))
    report = dict(actor=actor, rows=len(indices), max_absolute_score_error=error,
                  argmax_mismatches=int(choices), score_tolerance=2e-5)
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return int(choices > 0 or error > 2e-5)


if __name__ == '__main__':
    raise SystemExit(main())
