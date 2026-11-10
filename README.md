# Residual PPO for Body Leveling of Wheel-Legged Robots During Obstacle Traversal

**Junxian Zhu · Duke University**

This project investigates body leveling during wheel-legged obstacle traversal. A four-legged, wheeled robot uses a recorded motion sequence to cross a step, while Residual Proximal Policy Optimization (PPO) learns state-dependent corrections to joint and wheel commands. Experiments in Isaac Sim compare Recorded Replay and Residual PPO on 50 mm and 100 mm obstacles.

[Project website](https://allenzjx.github.io/wheel-legged-body-leveling/) · [Project report](research/README.md) · [50 mm training code](research/50mm/code/)

## Recording and residual control

The Recording interface sets joint and wheel targets, captures movement steps, and saves a replayable reference sequence. Each step includes command events, duration, boundary states, and task metadata.

Residual PPO combines this reference motion with feedback from body posture, joint and wheel state, contacts, support geometry, and obstacle-relative position. The controller requests eight joint-angle corrections and four wheel-speed corrections. Policy decisions run at 15 Hz, with actuator control and physics at 120 Hz.

The 50 mm training procedure develops early motion, rear-right transfer, following transfer, and front-left wheel refinement. Each component learns its part of the crossing while preceding components retain their weights.

## Experimental results

Evaluation covers 39 approach-distance and friction conditions at each obstacle height. Residual PPO completed 39/39 conditions on the 50 mm step and 37/39 on the 100 mm step; Recorded Replay completed 34/39 and 31/39, respectively. Nominal comparisons show lower phase-wise body roll and pitch RMS with Residual PPO.

The [results and video collection](https://allenzjx.github.io/wheel-legged-body-leveling/#evidence) report body inclination, wheel-transfer postures, traversal time, and completion. Comparison videos include nominal traversals, a longer approach distance, and a body-collision case, using matched camera views and 1× physical playback speed.

## Simulation and training

The [50 mm code package](research/50mm/code/) includes the controller, environment, observations, actions, rewards, PPO update loop, robot USD, recording reference, configurations, and model weights. The [run guide](research/50mm/code/README.md) covers full-controller evaluation and training continuations from the supplied stage models. The [installation guide](research/50mm/code/DEPENDENCIES.md) specifies the simulator environment.

## Website development

With Node.js 20 or newer, run:

```sh
node scripts/build.mjs
node scripts/check.mjs
node scripts/serve.mjs
```

Open `http://127.0.0.1:4173`. The `/project-preview/` route provides a local check of repository-relative URLs. The site requires no additional JavaScript packages.

| Location | Contents |
| --- | --- |
| `content/site.json` | Project information, video conditions, media paths, and Recording demonstration configuration |
| `content/method50.json` | 50 mm control method and training procedure |
| `content/results.json` | Results figure titles, captions, and display order |
| `public/figures/` | Body-inclination plots, posture comparisons, and performance table |
| `public/media/` | CAD views, UI screenshots, videos, and video covers |
| `research/50mm/` | Method report, training code, models, and execution records |
| `scripts/build-report.mjs`, `scripts/render-method50.mjs` | Page generation |
| `public/academic.css`, `public/app.js` | Layout and browser interactions |

The build writes the site to `dist/`. Content and asset updates are made in the source directories, followed by the build and check commands. The Recording UI demonstration slot accepts a video and cover through `recordingDemo` in `content/site.json`.

## Deployment

GitHub Actions builds and deploys the site on pushes to `main`, using `.github/workflows/pages.yml`. GitHub Pages uses **GitHub Actions** as its deployment source. Relative asset paths support the `/wheel-legged-body-leveling/` project URL.

Images and H.264 videos are served directly without login. Video players load media on demand and support range requests. The public address is [allenzjx.github.io/wheel-legged-body-leveling](https://allenzjx.github.io/wheel-legged-body-leveling/).
