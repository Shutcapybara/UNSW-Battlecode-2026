"""Explicit target map distribution; raw outcomes remain unweighted in the ledger."""
import json
import math
from pathlib import Path
from benchmark_data import sha


def normalized_weights(manifest):
    maps = manifest['maps']
    raw = manifest.get('map_weights', dict.fromkeys(maps, 1.0))
    if set(raw) != set(maps) or not maps:
        raise ValueError('Map weights must cover exactly the campaign maps')
    values = [float(raw[m]) for m in maps]
    if any(not math.isfinite(v) or v <= 0 for v in values):
        raise ValueError('Map weights must be finite and positive')
    total = sum(values)
    return {m: v / total for m, v in zip(maps, values)}


def configured_distribution(config, maps, config_path):
    """Mix a manifest's recommended suite weights with uniform remaining maps."""
    spec = config.get('map_distribution')
    if spec is None:
        return normalized_weights(dict(maps=list(maps))), {'kind': 'uniform'}
    if set(spec) != {'manifest', 'mass'}:
        raise ValueError('map_distribution requires manifest and mass')
    mass = float(spec['mass'])
    if not math.isfinite(mass) or not 0 < mass < 1:
        raise ValueError('Suite mass must be between zero and one')
    path = (Path(config_path).parent / spec['manifest']).resolve()
    suite = json.loads(path.read_text())
    entries = suite['maps']
    names = [e['name'] for e in entries]
    if len(names) != len(set(names)) or not set(names) < set(maps):
        raise ValueError('Suite must be a unique, proper subset of campaign maps')
    weights = {}
    for entry in entries:
        name = entry['name']
        if sha(maps[name]) != entry['sha256']:
            raise ValueError(f'Weighted map hash mismatch: {name}')
        weights[name] = entry['default_training_map_weight']
    weights = normalized_weights(dict(maps=names, map_weights=weights))
    remaining = set(maps) - set(names)
    combined = {name: mass * weight for name, weight in weights.items()}
    combined.update({name: (1 - mass) / len(remaining) for name in remaining})
    provenance = dict(kind='suite_mixture', manifest=str(path), manifest_sha256=sha(path),
        suite_mass=mass, suite_maps=names, remainder_mass=1-mass,
        weight_field='default_training_map_weight',
        suite_metadata={e['name']: {k: e.get(k) for k in
            ('family_id', 'dataset_split_group', 'plausibility')} for e in entries})
    return normalized_weights(dict(maps=list(maps), map_weights=combined)), provenance
