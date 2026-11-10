# Results, implementation, and evidence scope

This directory accompanies the [project website](https://allenzjx.github.io/wheel-legged-body-leveling/) with method documentation, the 50 mm implementation, model identities, and historical evaluation records. The reported experiments concern simulated obstacle traversal. A selected comparison video illustrates one case; it does not estimate reliability across conditions.

## Current poster Results

The website presents the original Results figures from the poster for both 50 mm and 100 mm obstacles. The figure list, captions, and display order are maintained in [content/results.json](../content/results.json), and the original images are in [public/figures/](../public/figures/). [results-figures.json](results-figures.json) records the original PDF identity and figure crops.

The Results section includes:

- Nominal total body-inclination traces and phase-wise roll and pitch RMS at both obstacle heights, using a requested initial gap of 218.5 mm and friction multiplier of 1.0.
- Wheel-transfer posture comparisons with the corresponding angles and timestamps.
- The poster's completion and traversal-performance table across 39 test conditions at each obstacle height.

Keep each figure's original labels, values, and scope. Nominal traces, phase-wise statistics, posture snapshots, and condition-level completion counts answer different questions. The historical CSV described below is an archive of a particular evaluation export, not the source of every poster figure or a replacement for the current Results section. Code verification has its own scope: packaging or running the code does not by itself reproduce all poster results.

## 50 mm method and runnable code

The [50 mm method report](50mm/README.md) describes the overall state-conditioned residual controller, its four learned components, and its selected training history. Recorded commands supply the motion reference; body, joint, contact, and task observations inform eight joint-angle and four wheel-speed correction requests. The policy operates at 15 Hz, with a 120 Hz physical interface. Stage-specific model architectures and optimization settings retain their individual scopes.

The complete [50 mm simulation and PPO training package](50mm/code/) contains the actual source, native controller and simulation environment, observations, actions, rewards, PPO update instrumentation, robot USD, recording-derived reference, configurations, and five model bundles. Its README and `DEPENDENCIES.md` provide the English installation and run instructions. Isaac Sim and Isaac Lab remain external runtime dependencies installed from their official distributions.

The public launcher supports evaluation of the complete selected controller and independent training continuations of the supplied learned components. Each continuation uses fresh Adam state and an explicit seed. It is not an exact historical resume, and the commands do not automatically reconstruct the selected composite from random initialization. Evaluation outcomes and new training records are written to separate run directories. Consult the code package's verification record for the checks actually performed; an import check, a PPO update, and a completed traversal are distinct outcomes.

The 100 mm evaluations retain their own model identities. The 50 mm implementation and optimization description do not imply that the 100 mm controller was trained with identical networks or settings.

## Comparison videos

The featured 100 mm video is the nominal case `grid_d1_mu1`, with a requested initial gap of 218.5 mm and friction multiplier of 1.0. The displayed requested gap is rounded; startup alignment can produce small differences in the measured gap. Both methods finish this selected case. Its controller and media identities are retained in [current-results.json](current-results.json), a record of that 100 mm evaluation scope.

The supplied comparisons render retained simulator link poses with the project robot geometry. They preserve complete native evaluation episodes at 1× physical speed, with a shared camera and scale. When one method ends earlier, its final pose and timestamp remain visible while the other continues; the final pair holds for two seconds. These are frozen-controller evaluations, not physical-robot footage or recordings of training.

The embedded `Success` labels require both the common completion assessment and the controller's native success condition. This differs from a count using `common_success` alone. The 50 mm nominal comparison is identified in the 50 mm method report and tied to its supplied full-controller model. Keep each video's obstacle height, model, task conditions, and outcome rule with the video rather than combining selected clips into a success-rate estimate.

The author will provide the Recording UI-operation video. Its reserved area on the website is explicitly marked; screenshots and simulated comparison videos do not stand in for that missing operation recording.

## Historical evaluation archive

[archive/2026-10-31/](archive/2026-10-31/) retains earlier exported data, plots, evidence summaries, and method notes. The 100 mm CSV has 94 method–condition rows: two methods across 39 known regression conditions and eight separate holdout conditions. These exports describe distinct evaluation scopes and are not a single current benchmark for all poster Results.

Within that archived CSV only, filtering `cohort` to `known_regression_39` and counting `common_success == True` gives Recorded Replay 31/39 and Residual PPO 37/39. Each method has 39 distinct case IDs. The conditions were used in diagnosis and development, rather than an unseen generalization test. These are common-completion counts, not body-leveling measurements or the stricter success labels embedded in the videos.

When reusing archived data, retain these distinctions:

- **Success criteria:** `common_success` is common-assessment completion; `native_success` is the controller's own termination criterion; `both_success` requires both. Their counts are not interchangeable.
- **Evaluation sets:** keep the known 39-condition regression, the eight-condition holdout, and selected demonstration cases separate.
- **Models:** retain the original checkpoint identity for every analysis. Earlier 50 mm policies, the selected full 50 mm composite, and the 100 mm controller are not interchangeable; changing obstacle height can also change the model.
- **Inclusion rules:** some posture aggregates include only paired cases in which both methods succeed. Retain that selection and its denominator; excluding failures changes the population described.
- **Measurement windows:** geometric-completion measurements end at each method's first geometric completion. Full-episode measurements include the remaining native episode. Per-wheel event windows are a further, distinct analysis.
- **Interpretation:** body inclination RMS, peak inclination, pitch, roll, and traversal completion measure different properties. Improvement in one does not establish improvement in all, reduced jitter, or physical-robot robustness.

The archived method configurations are specific to their components and training stages. They do not establish a uniform architecture, reward, or training schedule for every experiment. Historical plotting scripts can reproduce the plots supported by their archived inputs; they are not presented as a reproduction pipeline for all original poster figures.
