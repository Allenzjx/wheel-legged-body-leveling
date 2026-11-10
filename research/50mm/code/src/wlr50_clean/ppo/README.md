# Residual PPO for 50 mm obstacle traversal

This module implements the simulation environment, observations, residual action mapping, rewards, learned components, and PPO updates for the 50 mm wheel-legged traversal controller. A recorded motion reference supplies joint and wheel targets. State-dependent residuals adjust eight leg-joint commands and four wheel-speed commands as support transfers between wheels.

The complete controller receives 536 observation values and issues 12 residual requests at 15 Hz. The physical control interface and simulation operate at 120 Hz. Training develops four learned components: early motion, rear-right transfer, following transfer, and front-left wheel refinement. The preceding components retain fixed weights during local training.

## Running the controller

The [run guide](../../../README.md) and [dependency instructions](../../../DEPENDENCIES.md) describe installation, evaluation, and training. From `research/50mm/code`, the public entry point is:

```powershell
python scripts/run.py preflight --check-models
python scripts/run.py evaluate --stage full --run-dir runs/full-eval-001 --seed 4001 --max-decisions 3000
python scripts/run.py train --stage early --run-dir runs/early-001 --seed 1001 --decisions 128
```

Evaluation uses deterministic actions and fixed model parameters. Stage-specific training continues the supplied weights with a newly initialized Adam optimizer. Each run writes its results, sampled transitions, updates, and model parameters to its own output directory.

## Module map

| Component | Modules |
| --- | --- |
| Simulator and controller interface | `semantic_backend.py`, `semantic_env.py` |
| Observation encoding | `semantic_observation.py` |
| Residual action mapping and actuator limits | `action_projection.py`, `semantic_residual_adapter.py` |
| Early-motion actor and PPO update instrumentation | `semantic_rear_owner_actor.py`, `semantic_training.py` |
| Rear-right transfer | `semantic_rr_capture_local.py`, `semantic_rr_capture_local_actor.py`, `semantic_rr_capture_local_task.py` |
| Following transfer | `semantic_post_rr_front_prep.py`, `semantic_post_rr_front_prep_actor.py`, `semantic_post_rr_front_prep_task.py` |
| Front-left wheel refinement | `semantic_fl_forward.py`, `semantic_fl_forward_actor.py`, `semantic_fl_forward_task.py` |
| Complete-controller evaluation | `semantic_fl_prior_retirement.py`, `semantic_fl_prior_retirement_actor.py`, `semantic_fl_prior_retirement_task.py` |

Stage-specific rewards, observation schemas, and motion settings are stored under [`configs/`](../../../configs/). The [method report](../../../../README.md) describes the controller architecture, training objectives, and optimization settings.
