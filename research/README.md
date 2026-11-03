# Results and evidence scope

This directory records the evidence used in the current project website. All reported evaluations are simulations. A selected comparison video illustrates a case; it does not estimate reliability across conditions.

## Current reported result

The known 100 mm regression set contains 39 matched gap/friction conditions. Under the common completion assessment, Recorded Replay completes 31 conditions and the frozen Residual PPO controller completes 37. These conditions were used in diagnosis and development; they are not an unseen generalization test. The counts do not measure body-leveling quality.

The machine-readable record is [current-results.json](current-results.json). The counts can be checked in the [archived per-case CSV](archive/2026-10-31/data/evaluation-100mm.csv): filter `cohort` to `known_regression_39`, group by `method`, and count `common_success == True`. Each method has 39 distinct case IDs. Keep the two methods paired by case ID.

## Video records

The featured video is case `grid_d1_mu1`: a 100 mm obstacle, requested initial gap of 218.5 mm, and friction scale 1.0. The requested gap is rounded for display; startup alignment can produce small differences in the actual measured gap. Both methods finish this selected case.

The video renders retained simulator link poses using the project robot geometry. It preserves both complete native evaluation episodes at 1× physical speed, with a shared camera and scale. When one method ends earlier, its final pose and timestamp remain visible while the other continues; the final pair holds for two seconds. It is a frozen-controller evaluation, not hardware footage or a recording of training.

The video's `Success` labels require both common completion and each controller's native success condition. This is a stricter rule than the common-only counts reported above. The video and the 39-condition result use the same frozen 100 mm checkpoint; its identity and the video checksum are recorded in the JSON.

## Method scope

The website presents the overall 50 mm state-conditioned residual control framework. Recorded commands define the reference; body, joint, contact and task observations inform joint-angle and wheel-speed corrections. The policy operates at 15 Hz and the physical interface at 120 Hz. The 50 mm actor uses a clipped PPO objective with value estimation and generalized advantage estimation during training. Evaluation uses fixed model parameters.

The [archived method record](archive/2026-10-31/methods.json) identifies individual components, historical architectures, reward terms and configurations. Its settings are specific to those components and training stages; they do not define one uniform training run. The 100 mm evaluation retains its own model identity, and the 50 mm optimization description is not an assertion that the 100 mm controller was retrained with the same architecture or settings.

The archived 50 mm comparison depicts an earlier frozen controller. It is a selected demonstration of the reference/residual comparison, not evidence for a newly reported 50 mm completion rate. Completion summaries and plot annotations without reconciled measurement records are excluded from the current website.

## Historical archive

[archive/2026-10-31](archive/2026-10-31/) retains the earlier website's exported data, figures, evidence summary, and method notes for inspection. These files describe distinct evaluation scopes and are not one current, uniform benchmark.

- **Success criteria:** `common_success` is common-assessment completion. `native_success` is the controller's own termination criterion. `both_success` requires both. Counts under these rules are not interchangeable.
- **Evaluation sets:** the known 39-condition regression and the separate eight-condition holdout remain separate. Selected videos are a third, illustrative selection.
- **Models:** historical 50 mm results concern an earlier frozen policy. They do not measure the current 100 mm controller or a later 50 mm policy. Comparing obstacle heights also changes the model.
- **Posture statistics:** some aggregates include only pairs where both methods succeed. Keep that inclusion rule and the paired-case denominator. Excluding failures changes the population being described.
- **Measurement windows:** geometric-completion measurements end at each method's first geometric completion. Full-episode measurements include the remaining native episode. They must not be mixed. Per-wheel event windows are another distinct analysis.
- **Interpretation:** body inclination RMS, peak inclination, pitch, roll, and traversal completion measure different properties. Improvement in one does not establish improvement in all, reduced jitter, or physical-robot robustness.

## Verification checklist

- [x] The 39-condition CSV has 39 distinct cases for each method and reproduces common-completion counts of 31 and 37.
- [x] The featured video checksum matches its retained delivery record.
- [x] The featured case, obstacle height, requested gap, friction, playback speed, and checkpoint are identified.
- [x] The common-only count is distinguished from the stricter labels embedded in the videos.
- [x] Unreconciled summary numbers and claims of uniform improvement are excluded from the current reported result.
- [x] Historical results retain their original cohort, model, outcome rule, and measurement-window context.

The repository provides inspectable exports and provenance identifiers. It does not contain a complete redistributable training environment or every original simulator trace.
