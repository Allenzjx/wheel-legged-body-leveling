# 50 mm Residual PPO training

The controller combines a recorded obstacle-traversal reference with state-dependent corrections. Its learned components cover the crossing sequence from the initial approach through successive wheel-support transfers. Earlier actors remain responsive to measured state while their weights are held fixed during subsequent local training.

This directory describes the composite policy used in the [50 mm nominal comparison](https://allenzjx.github.io/wheel-legged-body-leveling/media/comparison-50mm-nominal.mp4). The model is identified by checkpoint `CP233547`, SHA256 `34537113f574361df736a1aafb15bca1ef5afb01614d3a79998b35b0fea102e6`. The recorded comparison uses case `grid_d1_mu1`, a 50 mm step, a requested initial gap of 218.5 mm and friction multiplier 1.0.

## Run the training code

The complete [simulation and PPO code package](code/) includes the robot asset, recorded motion reference, controller, environment, observation and action interfaces, stage-specific rewards, training loop and five model bundles. Begin with the [installation instructions](code/DEPENDENCIES.md) and [English run guide](code/README.md).

After installing the documented simulator environment, run these commands from `research/50mm/code`:

```powershell
python -m pip install -e ".[training]"
python scripts/run.py preflight --check-models
python scripts/run.py evaluate --stage full --run-dir runs/full-eval-001 --seed 4001 --max-decisions 3000
python scripts/run.py train --stage early --run-dir runs/early-001 --seed 1001 --decisions 128
```

The evaluation starts the complete selected controller at the native task reset. Training commands continue the supplied learned components with a fresh Adam optimizer. The guide also covers rear-right transfer, following transfer and front-left wheel refinement. These are independent continuations, not an exact reconstruction of historical training from random initialization. New outputs are kept in separate run directories.

## State, actions and control

The evaluated interface contains 536 observation values. Its semantic groups include body orientation and motion; joint and wheel state; contacts, loads and support geometry; obstacle-relative geometry; traversal phase and physical progress; and finite command history. The layout contains extensions and padded fields inherited from earlier components. The groups are not an additive dimension partition. Actor and critic receive the same simulator-derived observation vector.

The composite actor produces 12 raw request coordinates: eight leg-joint corrections and four wheel-speed corrections. The joint order is front-left hip/knee, front-right hip/knee, rear-left hip/knee and rear-right hip/knee; wheel order is front-left, front-right, rear-left and rear-right. Raw Gaussian requests are transformed by tanh, phase-dependent physical scales and command constraints. Joint requests use degrees in controller coordinates; wheel requests use rad/s. The policy operates at 15 Hz, and the physical controller and simulator operate at 120 Hz.

Recorded commands supply the motion reference. Learned requests pass through contact coordination, feasible command limits and actuator constraints before becoming joint-position and wheel-velocity targets. The actor observes the motion phase; it does not choose phase labels. Request magnitude is distinct from the final actuator-target change.

## Network composition

| Learned component | Actor structure | Role |
|---|---|---|
| Retained early-motion actor | 439 → 256 → 256 → 24; ELU hidden activations | Twelve Gaussian mean and twelve log-standard-deviation outputs; learned motion from the initial approach |
| Rear-right transfer actor | 465 → 128 → 128 → 24; ELU | Local corrections around the retained early actor |
| Following-transfer actor | 490 → 128 → 128 → 24; ELU | Front-leg preparation and continued support transfer around the preceding composite |
| Front-left wheel refinement | Two learned scalars: conditional mean offset and log standard deviation | One eligible wheel correction while the other coordinates retain the preceding actor |

The first early-training network used 324 inputs, two 256-unit ELU layers, twelve Gaussian means and a separate standard-deviation vector. Its architecture evolved before the retained 439-input component. The evaluated 536-value interface therefore does not denote a single newly trained 536-input MLP. The final critic has 536 → 128 → 128 → 1 units with ELU hidden activations. Interface changes without optimizer updates are not additional learned stages.

## Four learned stages

| Stage | Training objective and execution | Selected training record |
|---|---|---|
| Early motion | Develop forward task progress and the motion required to reach later support transfers; posture and obstacle-gap terms change during development | 225,280 cumulative policy decisions; 1,725 PPO updates; 34,500 Adam steps |
| Rear-right transfer | Execute the retained motion to the activation interval; learn rear-right contact and continued rear-left transfer toward completion | 6,656 locally credited decisions; 13 PPO updates; 260 Adam steps |
| Following transfer | Retain the preceding composite; learn front-leg preparation, support transfer and rear-left lift and placement | 512 new decisions; 1 PPO update; 20 Adam steps |
| Front-left wheel refinement | Adjust the eligible front-left wheel coordinate to encourage forward progress and reduce reverse or loaded counter-rotation commands | 2,048 stored decisions: 587 actor-eligible and 1,461 value-only; 4 PPO updates; 80 Adam steps, including 60 with actor eligibility |

The stage counts have different scopes. The early total is cumulative; later counts describe their local data. Physically executed frozen prefixes are excluded from local learning credit. A separate 512-decision branch supplied a critic initialization and is not an additional update to the selected rear-right actor. Historical auxiliary fitting and interface migrations are not counted as PPO updates. These records are not stage success rates or a single stationary learning curve.

## PPO optimization

Training stores sampled raw actions and their log probabilities before physical projection. The actor uses the clipped PPO likelihood-ratio objective. A critic estimates returns, and generalized advantage estimation supplies the advantage signal. The value and entropy losses accompany the actor objective. Inactive front-left rows have no actor gradient but remain in the minibatch denominator and value-learning context.

| Setting | Early training | Local transfer and front-left training |
|---|---|---|
| Rollout length | 128 decisions per environment | 512 decisions; one environment |
| Probability-ratio clip | 0.2 | 0.2 |
| Epochs / minibatches | 5 / 4 | 5 / 4 |
| Discount / GAE | Initially 0.995 / 0.95; later 0.9985 / 0.99 | 0.9985 / 0.99 |
| Optimizer | Adam with adaptive learning rate | Adam with adaptive learning rate |
| Adaptive-rate target KL | 0.01 | 0.01 |
| Gradient-norm limit | 1.0 | 1.0 |
| Value-loss coefficient | 1.0 | 1.0 |
| Entropy coefficient | 0.005 | 0.001 |

Most early runs use one environment; the recorded semantic-v2 history also includes eight-environment runs. The KL target adjusts the learning rate and is not a universal early-stop threshold. Saved learning-rate snapshots differ by selected component: early 1e-5, rear-right 3.375e-5, following transfer 1e-5 and front-left 0.01. These snapshots are not constant rates across each stage.

Rewards combine task progress, completion and stage-specific posture, contact and motion-quality terms. Transfer objectives distinguish wheel contact, lift, crossing and placement from task completion. The front-left objective includes measured forward displacement and reverse-command or counterdrive costs. Objective changes prevent a single invariant reward formula or a directly comparable reward curve across all stages.

## Evaluation and media

Evaluation uses deterministic actions and fixed weights. The nominal video preserves the complete native episodes at 1× physical speed with a shared camera and scale. The PPO episode lasts 93.6 s and Recorded Replay lasts 88.7333 s; the earlier-ending view holds its final measured pose, followed by a two-second final paired hold. The encoded video lasts 95.6667 s at 15 fps. Its SHA256 is `38eeafd24db66fdbcc319ab5a7a2ed3cc4bb1967e140f5ac15d18125ef77e892`.

The video illustrates one selected condition. It is separate from training rollouts and does not estimate generalization or a completion rate. The comparison evaluates the complete implemented controllers; it does not isolate a causal contribution from PPO alone.

## Files and model reuse

- [Runnable source and environment](code/): complete local training and evaluation package, including the robot USD and motion reference.
- [Run guide](code/README.md): installation, full traversal evaluation, component training, outputs and source map.
- [Model weights](model/composite-policy.npz): actor and critic tensors, including all nested retained actor weights, stored as numeric NumPy arrays.
- [Tensor manifest](model/tensors.json): archive keys, tensor names, shapes, dtypes and checksums.
- [Model configuration](model/configuration.json): the selected actor/critic construction and optimizer configuration, without machine-specific paths.
- [Training record](training.json): component identities, counts and stage-specific settings.
- [Source record](sources.json): source filenames, project-relative locations and content hashes.
- [Export provenance](provenance.json): original model identity, archive checks and file hashes.
- [Export utility](export_model.py): produces the numeric archive from the original checkpoint and sidecar; performs no inference or training.

The numeric archive contains the complete composite policy weights; separate ancestor checkpoint files are not required to recover the tensors. The accompanying [code package](code/) supplies the observation construction, reference motion, command mapping and robot asset; Isaac Sim and Isaac Lab are installed separately. Historical optimizer state is omitted, so training starts a new optimizer rather than restoring old Adam moments.

The arrays can be inspected without PyTorch or pickle:

```python
import numpy as np

with np.load("model/composite-policy.npz", allow_pickle=False) as model:
    for key in model.files:
        print(key, model[key].shape, model[key].dtype)
```
