"""Selection rules for safely resuming interrupted training/evaluation cycles."""
import json
from pathlib import Path


def find_pending_cycle(cycle_dirs, fingerprint, evaluation_hash):
    """Find the oldest resumable cycle, preserving trained panels as data grows.

    Training without a frozen summary is reusable only against its original
    dataset fingerprint. Once a summary and exported policy exist, evaluation
    is independent of later downloads and must finish before newer cycles.
    """
    for path in sorted((Path(item) for item in cycle_dirs), key=lambda item: int(item.name)):
        meta_path = path / 'cycle.json'
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        if meta.get('evaluation_hash') != evaluation_hash or meta.get('phase') == 'complete':
            continue
        if meta.get('fingerprint') == fingerprint:
            return path, meta
        training = path / 'training'
        candidate = Path(meta.get('candidate', path / 'candidate'))
        if not candidate.is_absolute():
            candidate = path / candidate
        frozen = (meta.get('phase') in ('training', 'trained', 'evaluating') and
                  (training / 'training_summary.json').exists() and
                  ((candidate / 'policy.json').exists() or (training / 'policy.json').exists()))
        if frozen:
            return path, meta
    return None


def fingerprint_after_completion(cycle_meta, current_fingerprint):
    """Record the corpus the frozen candidate actually trained on.

    A resumed evaluation may finish after new replays have been downloaded.
    Marking that newer corpus as trained would suppress the next training
    cycle, even though the completed candidate never saw those games.
    """
    return cycle_meta.get('fingerprint') or current_fingerprint
