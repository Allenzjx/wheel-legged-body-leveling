# Simulation and Training Execution Results

Execution tests ran on Windows 11 with Python 3.11.15, Isaac Sim 5.1.0.0, Isaac Lab core 0.54.3, PyTorch 2.7.0+cu128, and RSL-RL 5.0.1.

| Test | Result |
| --- | --- |
| Public repository download and CPU preflight | Package files passed checksum checks. All five model bundles loaded strictly and produced finite actor outputs. |
| Complete traversal, deterministic policy, seed 4001 | `SUCCESS`; 1,404 policy decisions, 11,232 physics ticks, 93.6 simulated seconds; zero policy updates. |
| Early-motion training, seed 1001 | 128 stored and actor-eligible transitions; one PPO update and 20 Adam steps. The rollout ended at its sampling budget with zero completed episodes. |
| Saved training model | All six actor tensors and all six critic tensors changed. Saved values were finite, and strict CPU reloading produced a finite 12-coordinate action output. |

All commands exited with code 0. The maximum absolute parameter change was approximately `2.71422e-4` for the actor and `2.73697e-4` for the critic. Training used a newly initialized Adam optimizer and wrote the updated weights to a separate run directory.

## Commands

```powershell
python scripts/run.py preflight --check-models
python scripts/run.py evaluate --stage full --run-dir runs/full-eval-001 --seed 4001 --max-decisions 3000
python scripts/run.py train --stage early --run-dir runs/early-smoke-001 --seed 1001 --decisions 128
```

## Test coverage

The simulation test covers one complete 50 mm traversal. The training test covers one early-motion update and saved-model reloading. The rear-right, following-transfer, and front-left models received CPU construction and state-loading checks. Tests used an existing Windows simulator environment; fresh-environment installation and Linux execution remain untested.

The [execution record](verification.json) contains commands, individual run and package identifiers, tensor changes, and receipt checksums. The [installation guide](DEPENDENCIES.md) specifies the runtime dependencies.
