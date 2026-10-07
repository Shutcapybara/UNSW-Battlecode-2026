"""Small candidate scorers over the audited encoder and legal C++ proposal features."""
import sys
from pathlib import Path
import numpy as np
import torch
from torch import nn

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/learn'))
from encode import N_CH, N_SC, SC

N_X = 49 * N_CH + N_SC

N_FEATURES = 32
HIDDEN = 32


def context_scales():
    scales = np.ones(N_X, dtype=np.float32)
    for cell in range(49):
        scales[cell * N_CH + 10] = 64  # pearl countdown
    for i, name in enumerate(SC):
        if name in ('round', 'rounds_left'):
            value = 500
        elif name in ('length', 'unit_count', 'unit_limit', 'headroom', 'turn_index') or 'age' in name or name.startswith('rounds_since'):
            value = 64
        elif name.endswith(('_f', '_r', '_d')) or name.endswith('_min_d'):
            value = 32
        elif name.startswith(('n_', 'echo_')) or name in ('len_delta', 'units_delta'):
            value = 16
        else:
            value = 1
        scales[49 * N_CH + i] = value
    return scales


class Scorer(nn.Module):
    def __init__(self):
        super().__init__()
        self.register_buffer('scales', torch.tensor(context_scales()))
        self.context = nn.Linear(N_X, HIDDEN)
        self.candidate = nn.Linear(N_FEATURES, HIDDEN, bias=False)
        self.output = nn.Linear(HIDDEN, 1)

    def forward(self, x, features):
        normalized = torch.clamp(x.float() / self.scales, -8, 8)
        context = self.context(normalized)
        while context.ndim < features.ndim:
            context = context.unsqueeze(-2)
        hidden = torch.relu(context + self.candidate(torch.clamp(features.float(), -8, 8)))
        return self.output(hidden).squeeze(-1)

    def sample(self, x, features, rng):
        with torch.no_grad():
            logits = self(torch.as_tensor(x).unsqueeze(0), torch.as_tensor(features).unsqueeze(0))[0]
            probabilities = torch.softmax(logits, dim=0).cpu().numpy().astype(np.float64)
        probabilities /= probabilities.sum()
        selected = int(rng.choice(len(features), p=probabilities))
        return selected, float(np.log(probabilities[selected]))

    def greedy(self, x, features, rng=None):
        with torch.no_grad():
            logits = self(torch.as_tensor(x).unsqueeze(0), torch.as_tensor(features).unsqueeze(0))[0]
        return int(logits.argmax()), 0.0

    def sample_rays(self, x, rays, rng):
        if all(len(ray) == 1 for ray in rays):
            return [(0, 0.0)] * 4
        features = np.zeros((4, 5, N_FEATURES), dtype=np.float32)
        mask = np.zeros((4, 5), dtype=bool)
        for i, ray in enumerate(rays):
            features[i, :len(ray)] = ray
            mask[i, :len(ray)] = True
        with torch.no_grad():
            logits = self(torch.as_tensor(x).unsqueeze(0), torch.as_tensor(features).unsqueeze(0))[0]
            logits = logits.masked_fill(~torch.as_tensor(mask), -1e9)
            probabilities = torch.softmax(logits, dim=-1).cpu().numpy().astype(np.float64)
        selected = []
        for i, ray in enumerate(rays):
            if len(ray) == 1:
                selected.append((0, 0.0))
                continue
            p = probabilities[i, :len(ray)]
            p /= p.sum()
            choice = int(rng.choice(len(ray), p=p))
            selected.append((choice, float(np.log(p[choice]))))
        return selected


def export_header(model, path, prefix):
    """Portable float32 actor; context is evaluated once for all candidates."""
    if prefix not in ('action', 'sonar'):
        raise ValueError('Actor prefix must be action or sonar')
    def numbers(values):
        return ','.join(format(float(v), '.9g') + ('f' if '.' in format(float(v), '.9g') or 'e' in format(float(v), '.9g') else '.0f')
                        for v in np.asarray(values).flat)
    state = {key: value.detach().cpu().numpy() for key, value in model.state_dict().items()}
    lines = ['#pragma once', '#include <algorithm>', '#include <array>', '#include <cstdint>', 'namespace finals::exported {']
    for key, name in [('scales', 'scale'), ('context.weight', 'context'), ('context.bias', 'bias'),
                      ('candidate.weight', 'candidate'), ('output.weight', 'output'), ('output.bias', 'output_bias')]:
        arr = state[key]
        lines.append(f'inline constexpr float {prefix}_{name}[{arr.size}] = {{{numbers(arr)}}};')
    lines += [f'''inline std::array<float, {HIDDEN}> {prefix}_encode(const std::array<int32_t, {N_X}>& x) {{
    std::array<float, {HIDDEN}> hidden{{}};
    for (int h=0; h<{HIDDEN}; h++) {{
        float value={prefix}_bias[h];
        for (int j=0; j<{N_X}; j++) value += {prefix}_context[h*{N_X}+j]*std::clamp(float(x[j])/{prefix}_scale[j],-8.0f,8.0f);
        hidden[h]=value;
    }}
    return hidden;
}}
inline float {prefix}_score(const std::array<float, {HIDDEN}>& context, const std::array<float, {N_FEATURES}>& features) {{
    float result={prefix}_output_bias[0];
    for (int h=0; h<{HIDDEN}; h++) {{
        float value=context[h];
        for (int j=0; j<{N_FEATURES}; j++) value += {prefix}_candidate[h*{N_FEATURES}+j]*std::clamp(features[j],-8.0f,8.0f);
        result += {prefix}_output[h]*std::max(0.0f,value);
    }}
    return result;
}}''', '}  // namespace finals::exported']
    Path(path).write_text('\n'.join(lines) + '\n')
