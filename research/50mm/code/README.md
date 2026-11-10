# 50 mm traversal: simulation and PPO training code

This package contains the controller, simulation environment, observation and action interfaces, reward definitions, PPO update instrumentation, recording reference, robot asset, and model parameters used by the 50 mm traversal system. Four learned components form the composite policy. The complete controller can be evaluated from the start of the obstacle traversal; each supplied component can also start a new training continuation.

The [execution-check record](VERIFICATION.md) reports the public-clone preflight, one complete simulation episode, and one early-stage PPO update with saved-model reloading.

The portable entry point is [`scripts/run.py`](scripts/run.py). It constructs the original actor and critic classes, loads the supplied numeric tensors, and uses the accompanying physical controller and RSL-RL PPO update. It creates a **fresh Adam optimizer** and an explicit random seed. Historical Adam moments, random-number-generator states, and old experiment receipts are not restored. Consequently, a new run is not an exact historical resume and is not an automatic reconstruction of the selected controller from random initialization.

## Installation

Follow the Windows environment recipe in [`DEPENDENCIES.md`](DEPENDENCIES.md), including the recorded Isaac Lab revision, Isaac Sim 5.1, Python 3.11, PyTorch 2.7.0 with CUDA 12.8, and RSL-RL 5.0.1. Isaac Sim and Isaac Lab are external runtime dependencies. The robot USD and project reference files are included here.

After activating that environment, change to this directory and install the project:

```powershell
cd research/50mm/code
python -m pip install -e ".[training]"
python scripts/run.py preflight --check-models
```

If already in this directory, omit the `cd` command. Preflight checks the package manifest, numeric tensor archives, exact state loading, model construction, and finite 12-coordinate actor output. It does not launch a physics scene or establish traversal success. The published manifest is already supplied; readers do not need to generate it.

## Evaluate the complete traversal controller

```powershell
python scripts/run.py evaluate --stage full --run-dir runs/full-eval-001 --seed 4001 --max-decisions 3000
```

This launches one headless simulation from the native reset and uses deterministic policy output, with no policy updates. The controller advances at 15 Hz with 120 Hz physics. A maximum of 3,000 policy decisions covers the 200-second native task horizon; native success or failure ends the episode earlier. `result.json` records the observed outcome. Completion of the command is not itself a success label.

For a brief startup check, use a new directory and `--max-decisions 128`. Such a budget-limited run is reported as `BOUNDED_PREVIEW` unless the native task has already ended. Add `--no-headless` to open the simulator window. Run one simulator process at a time.

`full` loads the complete selected composite, originally named `CP233547_FL000587_data002048_ret000000_ga2e6cc5fef6d`. Its original checkpoint SHA-256 is `34537113f574361df736a1aafb15bca1ef5afb01614d3a79998b35b0fea102e6`. This is the policy associated with the [50 mm nominal comparison](https://allenzjx.github.io/wheel-legged-body-leveling/media/comparison-50mm-nominal.mp4). A new local evaluation is a separate trial, not a regeneration of that recorded result.

## Continue training a component

The supplied stage models are already trained starting points. The commands below are **independent continuations**, not a sequential script that automatically transfers newly trained weights into the next stage.

| Stage | Learned component | Observation size | Stored decisions per update | Trainable actor |
| --- | --- | ---: | ---: | --- |
| `early` | Retained motion policy | 439 | 128 | 256–256 ELU network, 12 means and 12 log standard deviations |
| `rr` | Rear-right transfer | 465 | 512 | 128–128 ELU residual network; retained predecessor frozen |
| `post_rr` | Following transfer | 490 | 512 | 128–128 ELU residual network; retained composite frozen |
| `fl` | Front-left wheel refinement | 535 | 512 | Two scalar parameters for the active wheel correction distribution; complete predecessor frozen |

The deployed `full` interface has 536 observations and is an evaluation target. Its final interface change added no policy updates. The observation size is a controller interface size, not the width of one common neural network. Each model's complete construction recipe is in `checkpoints/<stage>/model.json`; [`stages.json`](stages.json) identifies the corresponding starting checkpoint.

Run one command at a time, using a different new output directory for every run:

```powershell
python scripts/run.py train --stage early --run-dir runs/early-001 --seed 1001 --decisions 128
python scripts/run.py train --stage rr --run-dir runs/rr-001 --seed 1001 --decisions 512
python scripts/run.py train --stage post_rr --run-dir runs/post-001 --seed 1001 --decisions 512
python scripts/run.py train --stage fl --run-dir runs/fl-001 --seed 1001 --decisions 512
```

`--decisions` counts newly stored on-policy transitions and must be a positive multiple of the stage's rollout length. Each update uses five epochs and four minibatches. The initial learning rate of the fresh optimizer is explicitly recorded in the stage model JSON; adaptive KL scheduling can then change it. These starting rates are checkpoint snapshots, not a claim that every historical phase used one learning rate.

The `early` command uses its 439-value measured observation schema and native controller configuration. For the three subsequent stages, a deterministic retained controller physically reaches the stage's activation condition before new samples enter PPO storage. This prefix receives no actor or critic learning credit. If it fails before activation, the run stops and records the outcome rather than relocating the robot to a manufactured training state. In the `fl` stage, the subsequent continuous rollout also contains inactive context rows: these update the critic, while actor updates retain the original eligibility mask. Its portable budget counts **all stored rows**, whereas the historical `semantic_fl_forward` CLI used an active-row threshold checked at complete rollout boundaries.

All policies use a 12-coordinate request interface: eight joint corrections and four wheel-speed corrections. The original phase masks, bounds, filtering, contact conditions, controller state, and native actuator checks remain in the execution path. PPO stores the sampled raw request and its original likelihood. The controller projects that request to its physical command; it does not let the policy select arbitrary phase transitions.

To evaluate a newly saved stage model:

```powershell
python scripts/run.py evaluate --stage rr --model runs/rr-001/model-update-0001/model.json --run-dir runs/rr-eval-001 --seed 4001
```

Use the matching `--stage`. The same `--model` option can start another training run, again with fresh Adam state. A stage-specific evaluation retains that stage's task and termination semantics; only `--stage full` is the selected complete-controller evaluation. New training may reduce performance and does not overwrite the supplied checkpoints.

## Outputs and interpretation

Each run writes under a new subdirectory of `runs/`:

- `run.json`: command, seed, model identity, package-manifest hash, and optimizer initialization.
- `decisions.jsonl`: physical times, raw actions, rewards and episode endings; uncredited prefixes are identified separately during training.
- `result.json`: completed evaluation outcome or training counts. `failure.json` records an interrupted or rejected run.
- `episode-*.json`: native outcomes of completed training episodes.
- `rollouts/rollout-*.npz`: observations, raw actions, old log probabilities, rewards, returns, advantages, and distribution parameters before the update.
- `rollouts/likelihood-*.json` and `updates.jsonl`: the original PPO instrumentation and observed optimizer-step counts.
- `model-update-*/model.json` and `weights.npz`: updated actor and critic tensors with their shapes, dtypes and checksums. Optimizer moments are not saved by this portable driver.

Numeric archives load with `numpy.load(path, allow_pickle=False)`. Actor and critic tensors were exported without changing their values. Optimizer state, arbitrary serialized objects and private workstation paths were removed from the model bundles. Each bundle retains its original checkpoint hash as provenance, while `package-manifest.json` describes the relocated public package. These are distinct identities.

The [method description](../README.md) and [historical training record](../training.json) describe the selected controller. New continuation counts remain separate from those records. Trial outcomes, success rates, and comparisons must be computed from the resulting episodes under explicitly matched conditions; this launcher does not convert a successful import, PPO update, or short preview into a performance claim.

## Source map

| Purpose | Source |
| --- | --- |
| Portable loading, evaluation and training loop | `scripts/run.py` |
| Physics and native controller interface | `src/wlr50_clean/ppo/semantic_backend.py`, `semantic_env.py` |
| Action projection and observation encoding | `src/wlr50_clean/ppo/action_projection.py`, `semantic_observation.py` |
| Early-stage training and PPO instrumentation | `src/wlr50_clean/ppo/semantic_training.py`, `semantic_rear_owner_actor.py` |
| Rear-right transfer | `src/wlr50_clean/ppo/semantic_rr_capture_local.py`, `semantic_rr_capture_local_actor.py` |
| Following transfer | `src/wlr50_clean/ppo/semantic_post_rr_front_prep.py`, `semantic_post_rr_front_prep_actor.py` |
| Front-left wheel refinement | `src/wlr50_clean/ppo/semantic_fl_forward.py`, `semantic_fl_forward_actor.py` |
| Complete controller interface | `src/wlr50_clean/ppo/semantic_fl_prior_retirement.py`, `semantic_fl_prior_retirement_task.py` |
| Recording-derived motion and FSM parameters | `configs/recording_motion_contract.json`, `configs/fsm_states.yaml` |
| Stage-specific rewards, schemas and settings | `configs/ppo_rr_rl_timing_policy_learning_v1/`, `configs/ppo_rr_capture_first_cp225280_v1/`, `configs/ppo_post_rr_front_pair_rl_v1/`, `configs/ppo_finish_advance_fl_forward_v1/` |

The original historical CLIs are retained in the source for inspection. Their `train`, `eval`, migration and strict-resume commands depend on original experiment receipts and Git history; they are not the portable commands documented above. The public launcher changes packaging and run bookkeeping, without fabricating those historical receipts or removing physical runtime checks. [`original-source-manifest.json`](original-source-manifest.json) and [`portability-changes.json`](portability-changes.json) record the source identities and relocation changes.

The local `.gitattributes` disables Git newline conversion so package checksums remain valid after cloning on another platform. For a deliberate local code or configuration change, review the modification, run `python scripts/seal_package.py`, then repeat preflight and the relevant simulation checks. The new manifest represents the modified package; it does not claim identity with the published package or with an old experiment.
