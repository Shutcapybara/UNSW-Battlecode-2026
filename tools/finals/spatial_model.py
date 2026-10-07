"""Shared two-stream encoder and conditional action/sonar heads."""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import torch
from torch import nn

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/learn'))
from encode import N_CH, N_SC, SC  # noqa: E402
from model import N_FEATURES, context_scales  # noqa: E402

N_OPTION_TYPES = 32
TYPE_CHANNELS = {'action': 6, 'sonar': 3}


class ObservationEncoder(nn.Module):
    """Encoder-v1 grid and scalar contract, encoded into a shared 128-vector."""

    def __init__(self):
        super().__init__()
        self.register_buffer('scales', torch.tensor(context_scales(), dtype=torch.float32))
        self.spatial = nn.Sequential(
            nn.Conv2d(N_CH, 32, kernel_size=3, padding=1), nn.ReLU(),
            nn.Conv2d(32, 32, kernel_size=3, padding=1), nn.ReLU(),
            nn.Flatten(), nn.Linear(49 * 32, 96), nn.ReLU(),
        )
        self.scalar = nn.Sequential(
            nn.Linear(N_SC, 64), nn.ReLU(), nn.Linear(64, 64), nn.ReLU(),
        )
        self.phase_embedding = nn.Embedding(5, 8)
        self.queen_embedding = nn.Embedding(2, 8)
        self.fusion = nn.Sequential(nn.Linear(96 + 64 + 16, 128), nn.ReLU())
        self.phase_ix = 49 * N_CH + SC.index('phase')
        self.queen_ix = 49 * N_CH + SC.index('is_queen')

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x.to(dtype=torch.float32)
        normalized = torch.clamp(x / self.scales, -8.0, 8.0)
        grid_end = 49 * N_CH
        grid = normalized[..., :grid_end].reshape(-1, 7, 7, N_CH).permute(0, 3, 1, 2)
        scalars = normalized[..., grid_end:]
        phase = x[..., self.phase_ix].round().long().clamp(0, 4)
        queen = x[..., self.queen_ix].round().long().clamp(0, 1)
        return self.fusion(torch.cat((
            self.spatial(grid), self.scalar(scalars),
            self.phase_embedding(phase), self.queen_embedding(queen),
        ), dim=-1))


class CandidateHead(nn.Module):
    def __init__(self, kind: str):
        super().__init__()
        if kind not in TYPE_CHANNELS:
            raise ValueError(f'unknown candidate head: {kind}')
        self.kind = kind
        self.type_channels = TYPE_CHANNELS[kind]
        self.option_embedding = nn.Embedding(N_OPTION_TYPES, 16)
        self.parameter_encoder = nn.Sequential(
            nn.Linear(N_FEATURES - self.type_channels, 32), nn.ReLU(),
        )
        self.action_context_encoder = (nn.Sequential(nn.Linear(N_FEATURES, 32), nn.ReLU())
                                       if kind == 'sonar' else None)
        input_width = 128 + 16 + 32 + (32 if kind == 'sonar' else 0)
        self.scorer = nn.Sequential(nn.Linear(input_width, 128), nn.ReLU(), nn.Linear(128, 1))

    def _type_id(self, features: torch.Tensor) -> torch.Tensor:
        return features[..., :self.type_channels].argmax(dim=-1).clamp(0, N_OPTION_TYPES - 1)

    def forward(self, context: torch.Tensor, features: torch.Tensor,
                action_context: torch.Tensor | None = None) -> torch.Tensor:
        features = features.to(dtype=torch.float32)
        while context.ndim < features.ndim:
            context = context.unsqueeze(-2)
        context = context.expand(*features.shape[:-1], context.shape[-1])
        candidate_type = self.option_embedding(self._type_id(features))
        parameters = self.parameter_encoder(torch.clamp(features[..., self.type_channels:], -8.0, 8.0))
        joined = [context, candidate_type, parameters]
        if self.kind == 'sonar':
            if action_context is None:
                action_context = torch.zeros((*features.shape[:-2], N_FEATURES),
                                             dtype=features.dtype, device=features.device)
            action_context = action_context.to(dtype=torch.float32)
            action_features = self.action_context_encoder(action_context)
            while action_features.ndim < features.ndim:
                action_features = action_features.unsqueeze(-2)
            action_features = action_features.expand(*features.shape[:-1], action_features.shape[-1])
            joined.append(action_features)
        return self.scorer(torch.cat(joined, dim=-1)).squeeze(-1)


class SpatialPolicy(nn.Module):
    """One shared state encoder, two candidate heads, and one shared local value head."""

    def __init__(self):
        super().__init__()
        self.encoder = ObservationEncoder()
        self.action_head = CandidateHead('action')
        self.sonar_head = CandidateHead('sonar')
        self.value_head = nn.Linear(128, 1)
        self.action_view = PolicyView(self, 'action')
        self.sonar_view = PolicyView(self, 'sonar')

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        return self.encoder(x)

    def forward(self, x: torch.Tensor, features: torch.Tensor, kind: str,
                action_context: torch.Tensor | None = None) -> torch.Tensor:
        context = self.encode(x)
        head = self.action_head if kind == 'action' else self.sonar_head
        return head(context, features, action_context)

    def value_from_context(self, context: torch.Tensor) -> torch.Tensor:
        return self.value_head(context).squeeze(-1)

    def value(self, x: torch.Tensor) -> torch.Tensor:
        return self.value_from_context(self.encode(x))


class PolicyView:
    """Collector-compatible view of one head; both views update the same policy."""

    def __init__(self, policy: SpatialPolicy, kind: str):
        self.policy = policy
        self.kind = kind

    def _scores(self, x, features, action_context=None):
        return self.policy(torch.as_tensor(x).unsqueeze(0),
                           torch.as_tensor(features, dtype=torch.float32).unsqueeze(0),
                           self.kind,
                           None if action_context is None else
                           torch.as_tensor(action_context, dtype=torch.float32).unsqueeze(0))[0]

    def _choose(self, x, features, rng=None, action_context=None):
        with torch.no_grad():
            logits = self._scores(x, features, action_context)
            probabilities = torch.softmax(logits, dim=-1).cpu().numpy().astype(np.float64)
        if rng is None:
            selected = int(probabilities.argmax())
            return selected, 0.0
        probabilities /= probabilities.sum()
        selected = int(rng.choice(len(features), p=probabilities))
        return selected, float(np.log(probabilities[selected]))

    def sample(self, x, features, rng):
        return self._choose(x, features, rng)

    def greedy(self, x, features, rng=None):
        return self._choose(x, features)

    def sample_conditioned(self, x, features, action_context, rng):
        return self._choose(x, features, rng, action_context)

    def greedy_conditioned(self, x, features, action_context, rng=None):
        return self._choose(x, features, None, action_context)

    def _rays(self, x, rays, action_context=None, rng=None):
        with torch.no_grad():
            xt = torch.as_tensor(x).unsqueeze(0)
            context = self.policy.encode(xt)
            action_ctx = None if action_context is None else torch.as_tensor(
                action_context, dtype=torch.float32).unsqueeze(0)
            choices = []
            for ray in rays:
                if len(ray) == 1:
                    choices.append((0, 0.0))
                    continue
                features = torch.as_tensor(ray, dtype=torch.float32).unsqueeze(0)
                logits = self.policy.sonar_head(context, features, action_ctx)[0]
                probabilities = torch.softmax(logits, dim=-1).cpu().numpy().astype(np.float64)
                if rng is None:
                    choices.append((int(probabilities.argmax()), 0.0))
                else:
                    probabilities /= probabilities.sum()
                    selected = int(rng.choice(len(ray), p=probabilities))
                    choices.append((selected, float(np.log(probabilities[selected]))))
            return choices

    def sample_rays(self, x, rays, rng):
        return self._rays(x, rays, rng=rng)

    def greedy_rays(self, x, rays, rng=None):
        return self._rays(x, rays)

    def sample_rays_conditioned(self, x, rays, action_context, rng):
        return self._rays(x, rays, action_context, rng)

    def greedy_rays_conditioned(self, x, rays, action_context, rng=None):
        return self._rays(x, rays, action_context)
