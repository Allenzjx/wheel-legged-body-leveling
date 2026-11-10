# Execution checks — 10 November 2026

The portable package was checked in the documented Windows 11 simulator environment: Python 3.11.15, Isaac Sim 5.1.0.0, Isaac Lab core 0.54.3, PyTorch 2.7.0+cu128, and RSL-RL 5.0.1. The source was also cloned from the public repository without authentication, at commit `7c4dd32a176fc74a1f8d3b08ebdbebe484d5b064`.

| Check | Observed result |
| --- | --- |
| Anonymous public clone, CPU preflight | Exit code 0; 380 package files checked; all five model bundles loaded strictly and produced finite actor outputs. |
| Complete controller, deterministic simulation, seed 4001 | Exit code 0; native `SUCCESS`; 1,404 policy decisions, 11,232 physics ticks, 93.6 simulated seconds; zero policy updates. |
| Early-stage training, seed 1001 | Exit code 0; 128 stored and actor-eligible transitions; one PPO update and 20 Adam steps. The short rollout completed zero episodes. |
| Saved training model | All six actor tensors and all six critic tensors changed. All saved values remained finite. Strict CPU reloading and a finite 12-coordinate forward pass succeeded. |

The maximum absolute parameter change was approximately `2.71422e-4` for the actor and `2.73697e-4` for the critic. These values establish that the training update changed the saved model; they are not measures of motion quality. The continuation used fresh Adam state, and its output did not replace any supplied selected checkpoint.

## Package identities

The complete-controller simulation started under manifest:

`8bce7b291b32f1fcb22ee144917e15a5befa50c774dcb4ee547620513feab095`

The public-clone preflight and early-stage training used the final manifest:

`cd3915a9a079a838d5e8e4e1b73192dfa9232372ce99545333d717032304980d`

Between these seals, the early training entry was corrected to its original measured 439-value environment, its PPO instrumentation tag was set, and manifest coverage was expanded to include retained artifacts and Git byte-preservation attributes. Those edits did not change the complete-controller evaluation path or its model. The full-run receipt nevertheless retains the earlier manifest identity; it is not presented as an end-to-end execution of the final manifest.

## Scope

This records package execution, not reproduction of the poster's evaluation statistics. One complete simulation episode does not establish a success rate. The training check covers one early-stage update; physical training of `rr`, `post_rr` and `fl` was not exercised in this pass. Their numeric state loading and model construction were checked on CPU.

The checks used an existing simulator environment. Installation into a new environment was not executed. The [machine-readable record](verification.json) contains commands, counts, model identities, numerical changes and receipt hashes. Private workstation paths and raw simulator logs are omitted.
