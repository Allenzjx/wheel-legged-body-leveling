"""Export numeric actor/critic tensors and a portable construction record.

Requires PyTorch and NumPy for export. Reading the resulting NPZ requires only
NumPy and uses allow_pickle=False. This utility performs no inference or update.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re

import numpy as np
import torch


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def portable(value):
    if isinstance(value, dict):
        return {key: portable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [portable(item) for item in value]
    if isinstance(value, str) and (re.search(r"[A-Za-z]:[\\/]", value) or value.startswith(("/", "\\\\"))):
        raise ValueError("Machine-specific path in selected configuration")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "model")
    args = parser.parse_args()
    source = torch.load(args.checkpoint, map_location="cpu", weights_only=True)
    sidecar = json.loads(args.manifest.read_text(encoding="utf-8"))
    if sidecar["checkpoint_sha256"] != digest(args.checkpoint):
        raise ValueError("Checkpoint differs from its source manifest")
    arrays = {}
    records = []
    for group in ("actor", "critic"):
        for name, tensor in source[group + "_state_dict"].items():
            array = tensor.detach().cpu().contiguous().numpy()
            if array.dtype.hasobject or not np.isfinite(array).all():
                raise ValueError("Expected finite numeric tensor")
            key = group + "::" + name
            arrays[key] = array
            records.append({"key": key, "group": group, "name": name,
                            "shape": list(array.shape), "dtype": str(array.dtype),
                            "elements": int(array.size),
                            "sha256_raw_c_bytes": hashlib.sha256(array.tobytes(order="C")).hexdigest()})
    args.output.mkdir(parents=True, exist_ok=True)
    archive = args.output / "composite-policy.npz"
    np.savez_compressed(archive, **arrays)
    with np.load(archive, allow_pickle=False) as check:
        if set(check.files) != set(arrays) or any(not np.array_equal(check[k], v) for k, v in arrays.items()):
            raise ValueError("Archive round-trip mismatch")
    provenance = {"checkpoint_name": args.checkpoint.name,
                  "checkpoint_sha256": digest(args.checkpoint),
                  "checkpoint_bytes": args.checkpoint.stat().st_size,
                  "sidecar_name": args.manifest.name,
                  "sidecar_sha256": digest(args.manifest)}
    tensors = {"schema": "wheel-legged-body-leveling.policy-tensors.v1",
               "source": provenance, "archive": archive.name,
               "archive_sha256": digest(archive), "archive_bytes": archive.stat().st_size,
               "array_format": "Numeric NPZ; load with allow_pickle=False",
               "tensor_count": len(records), "tensors": records,
               "scope": "Complete nested actor and critic tensors; optimizer and original metadata omitted."}
    runner = portable(sidecar["runner_config"])
    configuration = {"schema": "wheel-legged-body-leveling.composite-configuration.v1",
                     "checkpoint_sha256": provenance["checkpoint_sha256"],
                     "observation_dimension": 536, "action_dimension": 12,
                     "policy_frequency_hz": 15, "physics_frequency_hz": 120,
                     "actor": runner["actor"], "critic": runner["critic"],
                     "observation_groups": runner["obs_groups"],
                     "saved_stage_optimization": runner["algorithm"],
                     "saved_adam_learning_rate": sidecar["learning_rate"],
                     "saved_rollout_steps_per_environment": runner["num_steps_per_env"],
                     "optimization_scope": "Configuration of the selected package; earlier component training uses its own settings.",
                     "runtime_requirements": ["matching actor classes and rsl_rl interfaces", "observation and control implementation", "recorded reference", "robot assets and Isaac simulation environment"]}
    for name, data in (("tensors.json", tensors), ("configuration.json", configuration)):
        (args.output / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"tensor_count": len(records), "archive_bytes": archive.stat().st_size,
                      "archive_sha256": digest(archive), "numeric_round_trip": True}))


if __name__ == "__main__":
    main()
