# 50 mm Traversal: Simulation and PPO Training

This package implements simulated 50 mm obstacle traversal with a recorded motion reference and Residual PPO. It includes the controller, environment, observations, actions, rewards, PPO loop, robot asset, reference motion, and model parameters. Four learned components form the complete traversal policy.

The [execution results](VERIFICATION.md) include a successful complete traversal, one early-motion PPO update, and saved-model reloading.

The entry point is [`scripts/run.py`](scripts/run.py). It loads the actor and critic tensors and connects the physical controller to RSL-RL PPO. Training continues the supplied stage weights with a newly initialized Adam optimizer and the specified random seed.

## Installation

Follow the Windows installation instructions in [`DEPENDENCIES.md`](DEPENDENCIES.md) for Isaac Sim 5.1, Isaac Lab, Python 3.11, PyTorch 2.7.0 with CUDA 12.8, and RSL-RL 5.0.1. The robot USD and reference files are included in this package.

After activating that environment, change to this directory and install the project:

```powershell
cd research/50mm/code
python -m pip install -e ".[training]"
python scripts/run.py preflight --check-models
```

Preflight checks file checksums, model construction, strict tensor loading, and finite 12-coordinate actor output on CPU.

## Evaluate the complete traversal controller

```powershell
python scripts/run.py evaluate --stage full --run-dir runs/full-eval-001 --seed 4001 --max-decisions 3000
```

This launches one headless simulation from the task reset with deterministic policy output and fixed weights. The controller advances at 15 Hz with 120 Hz physics. The 3,000-decision limit covers the 200-second task horizon; success or failure ends the episode earlier. `result.json` records the outcome, including `termination_reason` and `full_task_success`.

Add `--no-headless` to open the simulator window. Run one simulator process at a time. A smaller `--max-decisions` value limits the trial duration and produces `BOUNDED_PREVIEW` if the task is still active when the budget ends.

`full` loads the composite controller shown in the [50 mm nominal comparison](https://allenzjx.github.io/wheel-legged-body-leveling/media/comparison-50mm-nominal.mp4). Its network configuration and model checksum are recorded in [`checkpoints/full/model.json`](checkpoints/full/model.json).

## Continue training a component

Each command below starts an independent continuation from its supplied stage model. Each run uses its own output directory and optimizer state.

| Stage | Learned component | Observation size | Stored decisions per update | Trainable actor |
| --- | --- | ---: | ---: | --- |
| `early` | Retained motion policy | 439 | 128 | 256–256 ELU network, 12 means and 12 log standard deviations |
| `rr` | Rear-right transfer | 465 | 512 | 128–128 ELU residual network; retained predecessor frozen |
| `post_rr` | Following transfer | 490 | 512 | 128–128 ELU residual network; retained composite frozen |
| `fl` | Front-left wheel refinement | 535 | 512 | Two scalar parameters for the active wheel correction distribution; complete predecessor frozen |

The `full` evaluation interface has 536 observations. Each component has its own observation layout and network construction, defined in `checkpoints/<stage>/model.json`. [`stages.json`](stages.json) lists the training and evaluation targets.

Run one command at a time, using a different new output directory for every run:

```powershell
python scripts/run.py train --stage early --run-dir runs/early-001 --seed 1001 --decisions 128
python scripts/run.py train --stage rr --run-dir runs/rr-001 --seed 1001 --decisions 512
python scripts/run.py train --stage post_rr --run-dir runs/post-001 --seed 1001 --decisions 512
python scripts/run.py train --stage fl --run-dir runs/fl-001 --seed 1001 --decisions 512
```

`--decisions` counts newly stored on-policy transitions and must be a positive multiple of the stage's rollout length. Each update uses five epochs and four minibatches. The stage model JSON defines the optimizer's initial learning rate, which is adjusted through adaptive KL scheduling.

The `early` command uses its 439-value observation schema. For the subsequent stages, the preceding controller executes the approach to the activation condition before samples enter PPO storage. This approach receives no actor or critic learning credit. A failure before activation stops the run and records the outcome. The `fl` sampling budget counts all stored rows: eligible rows update the actor, while inactive context rows contribute to critic training.

All policies use a 12-coordinate request interface: eight joint corrections and four wheel-speed corrections. Phase masks, bounds, filtering, contact conditions, and actuator checks constrain execution. PPO stores the sampled raw request and its likelihood; the controller projects that request into the physical command.

To evaluate a newly saved stage model:

```powershell
python scripts/run.py evaluate --stage rr --model runs/rr-001/model-update-0001/model.json --run-dir runs/rr-eval-001 --seed 4001
```

Use the matching `--stage`. The same `--model` option starts another training run with newly initialized Adam state. Stage evaluations use their corresponding task and termination conditions; `--stage full` evaluates the complete traversal controller. New model outputs are saved separately for evaluation before reuse.

## Run outputs

Each run writes under a new subdirectory of `runs/`:

- `run.json`: command, seed, model identity, package-manifest hash, and optimizer initialization.
- `decisions.jsonl`: physical times, raw actions, rewards and episode endings; uncredited prefixes are identified separately during training.
- `result.json`: completed evaluation outcome or training counts. `failure.json` records an interrupted or rejected run.
- `episode-*.json`: native outcomes of completed training episodes.
- `rollouts/rollout-*.npz`: observations, raw actions, old log probabilities, rewards, returns, advantages, and distribution parameters before the update.
- `rollouts/likelihood-*.json` and `updates.jsonl`: action-likelihood checks and optimizer-step counts.
- `model-update-*/model.json` and `weights.npz`: updated actor and critic tensors with their shapes, dtypes and checksums. Optimizer moments are not saved by this portable driver.

Numeric model files load with `numpy.load(path, allow_pickle=False)`. Model JSON files record tensor shapes, dtypes, and checksums. `package-manifest.json` records the source, configuration, asset, and model files used by the launcher.

The [method report](../README.md) and [training record](../training.json) describe the controller and its training stages. Each new run stores its own transition counts, update counts, and episode outcomes.

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

Use `scripts/run.py` for the commands in this guide. The source modules also contain experiment-orchestration utilities with additional record dependencies. [`original-source-manifest.json`](original-source-manifest.json) and [`portability-changes.json`](portability-changes.json) document the source files and path adjustments.

The local `.gitattributes` preserves file bytes when cloning. After editing code or configuration, run `python scripts/seal_package.py`, followed by preflight and the relevant simulation checks, to record and test the modified package.
