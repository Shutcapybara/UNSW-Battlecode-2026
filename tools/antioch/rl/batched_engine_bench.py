"""Bounded in-process engine benchmark with shared batched PyTorch inference.

Each engine has one synchronous outstanding callback. Independent engine processes
or threads send features to a shared inference server, which batches across games.
The seeded MLP is a workload probe, not a learned policy. The optional H-Q8-v1
encoder uses the same actor-local Python features as the encoder parity check.
Neither game strength nor readiness of a training algorithm follows from this
benchmark. Use --device cuda on a host where the NVIDIA devices are accessible.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import importlib.metadata
import json
import multiprocessing
import os
from pathlib import Path
import queue
import sys
import threading
import time

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
DIRECTIONS = (b"N", b"E", b"S", b"W")
OFFSETS = ((0, -1), (1, 0), (0, 1), (-1, 0))
FEATURE_COUNT = 32
TARGET_PER_HOUR = 20_000_000


def encode_probe(dragon_id: int, observation: bytes, width: int, height: int):
    """Encode actual callback data; no rollout/replay data are precomputed."""
    tiles = {}
    occupied = set()
    head = None
    round_num = length = unit_count = 0
    facing = b"N"
    for line in observation.splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[0].lstrip(b"-").isdigit():
            x, y, terrain, value = map(int, parts)
            tiles[(x, y)] = (terrain, value)
        elif len(parts) == 6 and parts[0] in (b"A", b"B"):
            x, y = int(parts[2]), int(parts[3])
            occupied.add((x, y))
            if int(parts[1]) == dragon_id and parts[5] == b"1":
                head = (x, y)
        elif len(parts) == 2:
            if parts[0] == b"ROUND":
                round_num = int(parts[1])
            elif parts[0] == b"DIR":
                facing = parts[1]
            elif parts[0] == b"LENGTH":
                length = int(parts[1])
            elif parts[0] == b"UNIT_COUNT":
                unit_count = int(parts[1])
    features = np.zeros(FEATURE_COUNT, dtype=np.float32)
    blocked = np.zeros(4, dtype=np.bool_)
    if head is None:
        return features, blocked
    for i, (dx, dy) in enumerate(OFFSETS):
        pos = ((head[0] + dx) % width, (head[1] + dy) % height)
        terrain, value = tiles.get(pos, (0, 0))
        blocked[i] = pos in occupied
        features[8 * i : 8 * i + 8] = (
            pos in tiles, terrain / 8, value / 4096,
            pos in occupied, DIRECTIONS[i] == facing,
            round_num / 500, length / 100, unit_count / 40,
        )
    return features, blocked


@dataclass
class Request:
    features: np.ndarray
    blocked: np.ndarray
    done: threading.Event = field(default_factory=threading.Event)
    action: int = 0
    error: BaseException | None = None


class BatchInference:
    """One inference thread, bounded wait, explicit propagation of failures."""

    def __init__(self, torch, model, device, batch_size: int, wait_ms: float):
        self.torch = torch
        self.model = model
        self.device = device
        self.batch_size = batch_size
        self.wait_seconds = wait_ms / 1000
        self.requests = queue.Queue()
        self.stopping = threading.Event()
        self.failure = None
        self.batch_histogram = {}
        self.inference_seconds = 0.0
        self.thread = threading.Thread(target=self._serve, name="inference")

    def start(self):
        self.thread.start()

    def reply(self, features: np.ndarray, blocked: np.ndarray) -> bytes:
        if self.failure is not None:
            raise RuntimeError("inference server failed") from self.failure
        request = Request(features, blocked)
        self.requests.put(request)
        while not request.done.wait(timeout=1):
            if not self.thread.is_alive():
                raise RuntimeError("inference server stopped") from self.failure
        if request.error is not None:
            raise RuntimeError("inference request failed") from request.error
        return b"MOVE " + DIRECTIONS[request.action] + b"\n"

    def close(self):
        self.stopping.set()
        self.thread.join()

    def _serve(self):
        current = []
        try:
            with self.torch.inference_mode():
                while not self.stopping.is_set() or not self.requests.empty():
                    try:
                        first = self.requests.get(timeout=0.05)
                    except queue.Empty:
                        continue
                    current = [first]
                    deadline = time.perf_counter() + self.wait_seconds
                    while len(current) < self.batch_size:
                        remaining = deadline - time.perf_counter()
                        try:
                            request = self.requests.get(timeout=max(remaining, 0))
                        except queue.Empty:
                            break
                        current.append(request)
                    start = time.perf_counter()
                    data = np.stack([request.features for request in current])
                    scores = self.model(self.torch.from_numpy(data).to(self.device))
                    scores = scores.cpu().numpy()
                    self.inference_seconds += time.perf_counter() - start
                    n = len(current)
                    self.batch_histogram[n] = self.batch_histogram.get(n, 0) + 1
                    for request, row in zip(current, scores):
                        # This only prevents moving onto observed dragon parts.
                        # It deliberately makes no claim to legal-action parity.
                        if not request.blocked.all():
                            row[request.blocked] = -np.inf
                        request.action = int(np.argmax(row))
                        request.done.set()
                    current = []
        except BaseException as error:
            self.failure = error
            while True:
                try:
                    current.append(self.requests.get_nowait())
                except queue.Empty:
                    break
            for request in current:
                request.error = error
                request.done.set()


class ObservationEncoder:
    """Actor memories belong to one engine game, never to the GPU service."""

    def __init__(self, name, width, height):
        self.name, self.width, self.height = name, width, height
        self.actors = {}
        if name == "hq8":
            from hq8_features import Encoder
            from tools.team_recon_claude.features_view import parse_block
            self.encoder_class, self.parse_block = Encoder, parse_block

    def spawn(self, dragon_id, initialization):
        if self.name == "hq8":
            init = dict(line.split(maxsplit=1) for line in initialization.decode().splitlines())
            self.actors[dragon_id] = self.encoder_class(
                dragon_id, init["TEAM"], self.width, self.height, int(init["UNIT_LIMIT"]))

    def encode(self, dragon_id, observation):
        if self.name == "probe":
            return encode_probe(dragon_id, observation, self.width, self.height)
        block, _ = self.parse_block(observation.decode().splitlines())
        features = np.asarray(self.actors[dragon_id].features(block), dtype=np.float32)
        head = block["tiles"][24][:2]
        occupied = {body[2:4] for body in block["bodies"]}
        blocked = np.asarray([
            ((head[0] + dx) % self.width, (head[1] + dy) % self.height) in occupied
            for dx, dy in OFFSETS], dtype=np.bool_)
        return features, blocked


def process_engine_worker(index, connection, maps, encoder_name, seed, worker_count,
                          ready, start_signal, stop, reports):
    """A CPU engine process sends each decision to its parent inference server."""
    from unswbc.engine import EngineModule
    count = {"games": 0, "decisions": 0, "encoding_seconds": 0.0,
             "maps": {}, "errors": [], "cpu_seconds": 0.0}
    try:
        engine = EngineModule()
    except Exception as error:
        count["errors"].append(repr(error))
        ready.put((index, False))
        reports.put((index, count))
        connection.close()
        return
    ready.put((index, True))
    start_signal.wait()
    cpu_start = time.process_time()
    try:
        while not stop.is_set():
            map_name, data, width, height = maps[(index + count["games"]) % len(maps)]
            encoder = ObservationEncoder(encoder_name, width, height)

            def callback(dragon_id, observation):
                start = time.perf_counter()
                features, blocked = encoder.encode(dragon_id, observation)
                count["encoding_seconds"] += time.perf_counter() - start
                connection.send((features, blocked))
                response = connection.recv()
                if isinstance(response, Exception):
                    raise response
                count["decisions"] += 1
                return response

            engine.run(data, callback, debug=0, bot_spawn=encoder.spawn,
                       seed=seed + index + count["games"] * worker_count)
            count["games"] += 1
            count["maps"][map_name] = count["maps"].get(map_name, 0) + 1
    except Exception as error:
        count["errors"].append(repr(error))
        stop.set()
    finally:
        count["cpu_seconds"] = time.process_time() - cpu_start
        reports.put((index, count))
        try:
            connection.send(None)
        except (BrokenPipeError, EOFError):
            pass
        connection.close()


def run_process_engines(args, maps, server):
    """Use spawn, so CPU workers never inherit a live CUDA context."""
    context = multiprocessing.get_context("spawn")
    ready, reports = context.Queue(), context.Queue()
    start_signal, stop = context.Event(), context.Event()
    workers, bridges = [], []
    for index in range(args.workers):
        parent_connection, child_connection = context.Pipe()
        worker = context.Process(target=process_engine_worker, args=(
            index, child_connection, maps, args.encoder, args.seed, args.workers,
            ready, start_signal, stop, reports))

        def bridge(connection=parent_connection):
            try:
                while True:
                    request = connection.recv()
                    if request is None:
                        break
                    try:
                        connection.send(server.reply(*request))
                    except Exception as error:
                        connection.send(RuntimeError(str(error)))
                        break
            except (EOFError, BrokenPipeError):
                pass
            finally:
                connection.close()

        worker.start()
        child_connection.close()
        bridge_thread = threading.Thread(target=bridge, name=f"bridge-{index}")
        bridge_thread.start()
        workers.append(worker)
        bridges.append(bridge_thread)
    try:
        setup = [ready.get(timeout=60) for _ in workers]
    except BaseException:
        stop.set()
        start_signal.set()
        for worker in workers:
            worker.join(timeout=5)
            if worker.is_alive():
                worker.terminate()
                worker.join()
        for bridge_thread in bridges:
            bridge_thread.join()
        raise
    if any(not ok for _, ok in setup):
        stop.set()
    start = time.perf_counter()
    cpu_start = time.process_time()
    start_signal.set()
    stop.wait(timeout=args.seconds)
    stop.set()
    for worker in workers:
        worker.join()
    for bridge_thread in bridges:
        bridge_thread.join()
    elapsed = time.perf_counter() - start
    indexed_reports = [reports.get(timeout=5) for _ in workers]
    counters = [count for _, count in sorted(indexed_reports)]
    cpu_elapsed = time.process_time() - cpu_start + sum(c["cpu_seconds"] for c in counters)
    return counters, elapsed, cpu_elapsed


def build_model(torch, device, feature_count):
    torch.manual_seed(1000)
    model = torch.nn.Sequential(
        torch.nn.Linear(feature_count, 128), torch.nn.ReLU(),
        torch.nn.Linear(128, 128), torch.nn.ReLU(),
        torch.nn.Linear(128, 4),
    ).to(device).eval()
    with torch.inference_mode():
        model(torch.zeros((8, feature_count), device=device)).cpu()
    return model


def inference_microbench(torch, model, device, seconds: float, feature_count: int):
    results = []
    for batch_size in (1, 8, 32, 128, 512):
        # Include CPU -> device -> CPU transfer, as the server does.
        data = torch.zeros((batch_size, feature_count))
        iterations = 0
        start = time.perf_counter()
        with torch.inference_mode():
            while time.perf_counter() - start < seconds:
                model(data.to(device)).cpu()
                iterations += 1
        elapsed = time.perf_counter() - start
        results.append({"batch_size": batch_size, "iterations": iterations,
                        "seconds": elapsed,
                        "decisions_per_second": iterations * batch_size / elapsed})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seconds", type=float, default=30)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cuda")
    parser.add_argument("--encoder", choices=("probe", "hq8"), default="probe")
    parser.add_argument("--backend", choices=("threads", "processes"), default="processes")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--wait-ms", type=float, default=0.25)
    parser.add_argument("--maps", default="default,trophy,big_empty,portals,trauma,schooltime")
    parser.add_argument("--seed", type=int, default=1000)
    parser.add_argument("--cpu-limit", type=int, default=8)
    parser.add_argument("--inference-only", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 1 <= args.workers <= 64 or not 1 <= args.cpu_limit <= 8:
        parser.error("workers must be 1..64 and CPU affinity limit must be 1..8")
    if args.seconds <= 0 or args.batch_size < 1 or args.wait_ms < 0:
        parser.error("seconds/batch size must be positive; wait must be nonnegative")
    if hasattr(os, "sched_getaffinity"):
        available = sorted(os.sched_getaffinity(0))
        os.sched_setaffinity(0, available[:args.cpu_limit])
    # Set thread bounds before importing the tensor runtime.
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    import torch
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    if args.device == "cuda" and not torch.cuda.is_available():
        parser.error("CUDA is unavailable; use a GPU-enabled host or explicit --device cpu")
    device = torch.device(args.device)
    feature_count = FEATURE_COUNT
    if args.encoder == "hq8":
        from hq8_features import NAMES
        feature_count = len(NAMES)
    model = build_model(torch, device, feature_count)
    output = {"unswbc": importlib.metadata.version("unswbc"),
              "torch": torch.__version__, "cuda_runtime": torch.version.cuda,
              "device": str(device),
              "gpu": torch.cuda.get_device_name(0) if device.type == "cuda" else None,
              "cpu_affinity": sorted(os.sched_getaffinity(0)),
              "model": f"seeded untrained MLP {feature_count}->128->128->4",
              "parameters": sum(p.numel() for p in model.parameters()),
              "encoder": "H-Q8-v1 conservative subset" if args.encoder == "hq8"
                         else "local-direction probe (not H-Q8)",
              "requested_seconds": args.seconds}
    if args.inference_only:
        output["inference_only"] = inference_microbench(torch, model, device, args.seconds, feature_count)
    else:
        from unswbc.engine import EngineModule
        maps = []
        for name in args.maps.split(","):
            path = ROOT / "maps" / f"{name}.map"
            data = path.read_bytes()
            header = data.splitlines()[0].split()
            maps.append((name, data, int(header[1]), int(header[2])))
        server = BatchInference(torch, model, device, args.batch_size, args.wait_ms)
        server.start()
        try:
            if args.backend == "processes":
                counters, elapsed, cpu_elapsed = run_process_engines(args, maps, server)
            else:
                # Compile engines before the measured steady-state interval.
                engines = [EngineModule() for _ in range(args.workers)]
                counters, elapsed, cpu_elapsed = run_thread_engines(args, maps, engines, server)
        finally:
            server.close()
        decisions = sum(c["decisions"] for c in counters)
        games = sum(c["games"] for c in counters)
        batches = sum(server.batch_histogram.values())
        output.update({"workers": args.workers, "backend": args.backend, "seconds": elapsed,
                       "cpu_seconds": cpu_elapsed, "mean_cpu_cores": cpu_elapsed / elapsed,
                       "games": games, "decisions": decisions,
                       "decisions_per_second": decisions / elapsed,
                       "decisions_per_hour": decisions / elapsed * 3600,
                       "g1_throughput_target_met": decisions / elapsed * 3600 >= TARGET_PER_HOUR,
                       "batch_size_limit": args.batch_size, "wait_ms": args.wait_ms,
                       "batch_histogram": server.batch_histogram,
                       "mean_batch_size": decisions / batches if batches else 0,
                       "inference_seconds": server.inference_seconds,
                       "workers_detail": counters,
                       "server_error": repr(server.failure) if server.failure else None,
                       "includes_compile_startup": False,
                       "interpretation": "throughput workload only; not a trained policy or full H-Q8 readiness"})
        if server.failure or any(c["errors"] for c in counters):
            output["g1_throughput_target_met"] = False
    rendered = json.dumps(output, indent=2) + "\n"
    print(rendered, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    return 1 if output.get("server_error") or any(c["errors"] for c in output.get("workers_detail", [])) else 0


def run_thread_engines(args, maps, engines, server):
    counters = [{"games": 0, "decisions": 0, "encoding_seconds": 0.0,
                 "maps": {}, "errors": []} for _ in engines]
    stop = threading.Event()
    barrier = threading.Barrier(args.workers + 1)

    def worker(index):
        count = counters[index]
        engine = engines[index]
        barrier.wait()
        while not stop.is_set():
            map_name, map_data, width, height = maps[(index + count["games"]) % len(maps)]
            encoder = ObservationEncoder(args.encoder, width, height)

            def callback(dragon_id, observation):
                start = time.perf_counter()
                features, blocked = encoder.encode(dragon_id, observation)
                count["encoding_seconds"] += time.perf_counter() - start
                result = server.reply(features, blocked)
                count["decisions"] += 1
                return result
            try:
                engine.run(map_data, callback, debug=0, bot_spawn=encoder.spawn,
                           seed=args.seed + index + count["games"] * args.workers)
                count["games"] += 1
                count["maps"][map_name] = count["maps"].get(map_name, 0) + 1
            except Exception as error:
                count["errors"].append(repr(error))
                stop.set()
    threads = [threading.Thread(target=worker, args=(i,), name=f"engine-{i}")
               for i in range(args.workers)]
    for thread in threads:
        thread.start()
    start = time.perf_counter()
    cpu_start = time.process_time()
    barrier.wait()
    stop.wait(timeout=args.seconds)
    stop.set()
    for thread in threads:
        thread.join()
    elapsed = time.perf_counter() - start
    cpu_elapsed = time.process_time() - cpu_start
    return counters, elapsed, cpu_elapsed

if __name__ == "__main__":
    raise SystemExit(main())
