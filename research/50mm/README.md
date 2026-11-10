# Residual PPO for 50 mm Obstacle Traversal

The wheel-legged robot traverses a 50 mm step by combining rolling motion with sequential wheel lifting. A recorded joint-and-wheel trajectory supplies the reference motion. Residual PPO uses measured robot state to adjust joint targets and wheel speeds as the support configuration changes, with body leveling and traversal progress incorporated into the training objectives.

The controller combines four learned components: early motion, rear-right transfer, following transfer, and front-left wheel refinement. During each local training stage, preceding components retain their weights and continue responding to measured state. The resulting composite controls the complete crossing sequence.

[Project website](https://allenzjx.github.io/wheel-legged-body-leveling/) · [50 mm comparison video](https://allenzjx.github.io/wheel-legged-body-leveling/media/comparison-50mm-nominal.mp4) · [Training code](code/) · [Installation](code/DEPENDENCIES.md)

## State and control interface

The complete controller receives 536 observation values covering body orientation and motion, joint and wheel state, contact loads and support geometry, obstacle-relative geometry, traversal phase, physical progress, and finite command history. The actor and critic receive the same simulator-derived observation vector.

The actor produces twelve raw requests: eight leg-joint corrections and four wheel-speed corrections. Joint order is front-left hip/knee, front-right hip/knee, rear-left hip/knee, and rear-right hip/knee; wheel order is front-left, front-right, rear-left, and rear-right. Gaussian sampling supplies exploration during training. The requests pass through tanh, phase-dependent scales, contact coordination, joint-range limits, and actuator constraints to form joint-position and wheel-velocity targets.

Joint corrections use degrees in controller coordinates; wheel corrections use rad/s. Policy decisions run at 15 Hz, with physical control and simulation at 120 Hz. Motion phase is part of the observation, while phase transitions follow the task controller.

## Network composition

| Component | Actor structure | Function |
| --- | --- | --- |
| Early motion | 439 → 256 → 256 → 24; ELU hidden activations | Twelve Gaussian means and twelve log standard deviations for motion from the initial approach |
| Rear-right transfer | 465 → 128 → 128 → 24; ELU | Local corrections around the early-motion actor |
| Following transfer | 490 → 128 → 128 → 24; ELU | Front-leg preparation and continued support transfer |
| Front-left wheel refinement | Learned conditional mean offset and log standard deviation | One eligible wheel-speed correction around the preceding composite |

The 536-value interface supplies the composite actor. Its critic uses a 536 → 128 → 128 → 1 ELU network. Each actor component uses its corresponding observation layout.

## Training across the crossing sequence

| Stage | Objective and execution | Training record |
| --- | --- | --- |
| Early motion | Learn forward progress and the motion needed to reach later support transfers; introduce posture and obstacle-gap terms | 225,280 cumulative policy decisions; 1,725 PPO updates; 34,500 Adam steps |
| Rear-right transfer | Execute the preceding motion to the activation interval, then learn rear-right contact and continued rear-left transfer | 6,656 local decisions; 13 PPO updates; 260 Adam steps |
| Following transfer | Learn front-leg preparation, support transfer, and rear-left lift and placement while retaining the preceding composite | 512 local decisions; 1 PPO update; 20 Adam steps |
| Front-left wheel refinement | Encourage forward travel and reduce reverse commands or loaded counter-rotation | 2,048 stored decisions: 587 actor-eligible and 1,461 value-only; 4 PPO updates; 80 Adam steps, including 60 with actor eligibility |

The early-motion counts are cumulative. Subsequent rows count data collected for their local objectives. The physical approach to each local activation interval is executed with fixed preceding actors and excluded from local learning credit. Front-left refinement uses an eligibility mask for actor updates; inactive context rows contribute to value learning.

## PPO optimization and reward

Training stores sampled raw actions and their log probabilities before physical projection. PPO applies a clipped likelihood-ratio objective, with a critic estimating returns and generalized advantage estimation providing the advantage signal. The loss also includes value estimation and entropy terms.

| Setting | Early motion | Local transfer and wheel refinement |
| --- | --- | --- |
| Rollout length | 128 decisions per environment | 512 decisions; one environment |
| Probability-ratio clip | 0.2 | 0.2 |
| Epochs / minibatches | 5 / 4 | 5 / 4 |
| Discount / GAE | Initial rollouts: 0.995 / 0.95; subsequent rollouts: 0.9985 / 0.99 | 0.9985 / 0.99 |
| Optimizer | Adam with adaptive learning rate | Adam with adaptive learning rate |
| Target KL for rate adaptation | 0.01 | 0.01 |
| Gradient-norm limit | 1.0 | 1.0 |
| Value-loss coefficient | 1.0 | 1.0 |
| Entropy coefficient | 0.005 | 0.001 |

Early-motion training includes one- and eight-environment rollouts. The continuation learning rates stored with the model bundles are 1e-5 for early motion, 3.375e-5 for rear-right transfer, 1e-5 for following transfer, and 0.01 for front-left refinement. Adaptive KL scheduling adjusts the rate during optimization.

Rewards combine task progress and completion with stage-specific posture, contact, and motion-quality terms. Transfer objectives include wheel lift, crossing, and placement. Front-left refinement adds forward-displacement reward and reverse-command or counterdrive penalties. The [training record](training.json) contains the component-specific settings and counts.

## Evaluation

Evaluation uses deterministic actions and fixed model weights. The nominal comparison uses a 50 mm step, an initial gap of 218.5 mm, and a friction multiplier of 1.0. Recorded Replay and Residual PPO complete the traversal in 88.7333 s and 93.6 s, respectively. The paired video preserves both full episodes at 1× physical speed with a shared camera and scale; the earlier-ending view holds its final measured pose.

A complete-controller execution test also returned `SUCCESS` after 1,404 policy decisions and 11,232 physics ticks, corresponding to 93.6 s of simulated motion. A separate early-motion training test completed one PPO update and 20 Adam steps from 128 transitions, and its saved model passed strict reloading. [Execution results](code/VERIFICATION.md) report the test commands and coverage.

## Run the code

The [code package](code/) contains the environment, controller, observation and action interfaces, rewards, PPO loop, robot USD, recorded reference, configurations, and five model bundles. Follow the [installation instructions](code/DEPENDENCIES.md), then run from `research/50mm/code`:

```powershell
python -m pip install -e ".[training]"
python scripts/run.py preflight --check-models
python scripts/run.py evaluate --stage full --run-dir runs/full-eval-001 --seed 4001 --max-decisions 3000
python scripts/run.py train --stage early --run-dir runs/early-001 --seed 1001 --decisions 128
```

Training continues the supplied stage weights with a newly initialized Adam optimizer. Each stage command starts an independent run and writes its outputs to a new directory. The [run guide](code/README.md) provides the commands for all four stages, model evaluation, and output files.

## Research files

| File or directory | Contents |
| --- | --- |
| [code/](code/) | Simulation and training implementation, assets, reference motion, and model bundles |
| [model/composite-policy.npz](model/composite-policy.npz) | Composite actor and critic tensors |
| [model/configuration.json](model/configuration.json) | Actor, critic, and optimization configuration |
| [model/tensors.json](model/tensors.json) | Tensor names, shapes, dtypes, and checksums |
| [training.json](training.json) | Stage objectives, training counts, and optimization settings |
| [sources.json](sources.json) and [provenance.json](provenance.json) | Source and model identifiers |
| [export_model.py](export_model.py) | Numeric model export utility |

Model tensors can be inspected with `numpy.load("model/composite-policy.npz", allow_pickle=False)`.
