# Results, implementation, and evidence scope

This directory accompanies the [project website](https://allenzjx.github.io/wheel-legged-body-leveling/) with method documentation, the 50 mm implementation, model identities, and figure and video provenance. The reported experiments concern simulated obstacle traversal. A selected comparison video illustrates one case; it does not estimate reliability across conditions.

## Current poster Results

The website presents the original Results figures from the poster for both 50 mm and 100 mm obstacles. The figure list, captions, and display order are maintained in [content/results.json](../content/results.json), and the original images are in [public/figures/](../public/figures/). [results-figures.json](results-figures.json) records the original PDF identity and figure crops.

The Results section includes:

- Nominal total body-inclination traces and phase-wise roll and pitch RMS at both obstacle heights, using a requested initial gap of 218.5 mm and friction multiplier of 1.0.
- Wheel-transfer posture comparisons with the corresponding angles and timestamps.
- The poster's completion and traversal-performance table across 39 test conditions at each obstacle height.

Keep each figure's original labels, values, and scope. Nominal traces, phase-wise statistics, posture snapshots, and condition-level completion counts answer different questions. Code verification has its own scope: packaging or running the code does not by itself reproduce all poster results.

## 50 mm method and runnable code

The [50 mm method report](50mm/README.md) describes the overall state-conditioned residual controller, its four learned components, and its selected training history. Recorded commands supply the motion reference; body, joint, contact, and task observations inform eight joint-angle and four wheel-speed correction requests. The policy operates at 15 Hz, with a 120 Hz physical interface. Stage-specific model architectures and optimization settings retain their individual scopes.

The complete [50 mm simulation and PPO training package](50mm/code/) contains the actual source, native controller and simulation environment, observations, actions, rewards, PPO update instrumentation, robot USD, recording-derived reference, configurations, and five model bundles. Its README and `DEPENDENCIES.md` provide the English installation and run instructions. Isaac Sim and Isaac Lab remain external runtime dependencies installed from their official distributions.

The public launcher supports evaluation of the complete selected controller and independent training continuations of the supplied learned components. Each continuation uses fresh Adam state and an explicit seed. It is not an exact historical resume, and the commands do not automatically reconstruct the selected composite from random initialization. Evaluation outcomes and new training records are written to separate run directories. Consult the code package's verification record for the checks actually performed; an import check, a PPO update, and a completed traversal are distinct outcomes.

The 100 mm evaluations retain their own model identities. The 50 mm implementation and optimization description do not imply that the 100 mm controller was trained with identical networks or settings.

## Comparison videos

The featured 100 mm video is the nominal case `grid_d1_mu1`, with a requested initial gap of 218.5 mm and friction multiplier of 1.0. The displayed requested gap is rounded; startup alignment can produce small differences in the measured gap. Both methods finish this selected case. Its controller and media identities are retained in [current-results.json](current-results.json), the comparison-video provenance record.

The supplied comparisons render retained simulator link poses with the project robot geometry. They preserve complete native evaluation episodes at 1× physical speed, with a shared camera and scale. When one method ends earlier, its final pose and timestamp remain visible while the other continues; the final pair holds for two seconds. These are frozen-controller evaluations, not physical-robot footage or recordings of training.

The embedded `Success` labels require both the common completion assessment and the controller's native success condition. This differs from a count using `common_success` alone. The 50 mm nominal comparison is identified in the 50 mm method report and tied to its supplied full-controller model. Keep each video's obstacle height, model, task conditions, and outcome rule with the video rather than combining selected clips into a success-rate estimate.

The author will provide the Recording UI-operation video. Its reserved area on the website is explicitly marked; screenshots and simulated comparison videos do not stand in for that missing operation recording.
