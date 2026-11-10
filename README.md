# Residual PPO for Body Leveling of Wheel-Legged Robots During Obstacle Traversal

A static research website presenting Recording, the 50 mm Residual PPO control framework, and simulated obstacle-traversal results at 50 mm and 100 mm. The page combines the project's CAD model, actual Recording UI, matched comparison videos, training details, and the original Results figures from the poster.

## Website and source

- [Public website](https://allenzjx.github.io/wheel-legged-body-leveling/)
- [GitHub repository](https://github.com/Allenzjx/wheel-legged-body-leveling)
- [50 mm simulation and PPO training package](research/50mm/code/)

The website and its media are publicly accessible without a GitHub login. The initial GitHub Pages deployment on October 31, 2026 passed the Linux build and 43 anonymous page/media checks; video range requests and browser playback were also checked. Updates pushed to `main` run the deployment workflow again.

The author will supply the UI-operation recording. Its clearly marked space remains on the page. Robot illustrations and comparison videos show the project CAD model and simulation, rather than physical-robot trials.

## Local preview

Install Node.js 20 or newer, then run from this directory:

```sh
node scripts/build.mjs
node scripts/check.mjs
node scripts/serve.mjs
```

Open `http://127.0.0.1:4173`. No additional JavaScript packages are required. The local `/project-preview/` route checks deployment under a repository subpath; it is not a public address.

## GitHub Pages deployment

The workflow is `.github/workflows/pages.yml`. In the repository, select **Settings → Pages → Build and deployment → Source → GitHub Actions**. A push to `main` builds, checks, and publishes the generated `dist/` directory. A deployment can also be started from **Actions → Deploy static research showcase → Run workflow**.

The site uses relative resource paths and supports the `/wheel-legged-body-leveling/` project path. After a deployment, open the public address without signing in and check navigation, images, videos, and downloads. Keep poster QR codes pointed at the verified public address. The existing GitHub Pages address has not changed.

The four supplied comparison MP4 files are complete H.264 videos, each smaller than 20 MB. They are served directly and loaded on demand. Do not replace them with Git LFS pointers or GitHub file-view pages. Larger replacement videos should use stable public media hosting whose playback has been checked without authentication.

## Content and media maintenance

| Location | Purpose |
| --- | --- |
| `content/site.json` | Project identity, video paths, conditions, captions, and the reserved `recordingDemo` |
| `content/method50.json` | Public 50 mm method, observation/action interface, networks, stages, and stage-specific optimization settings |
| `content/results.json` | Current Results figure order, paths, titles, and captions |
| `public/figures/` | Original poster Results images, including the 50 mm and 100 mm nominal plots, wheel-transfer postures, and completion/performance table |
| `public/media/` | CAD images, UI screenshots, comparison videos, and video covers |
| `research/50mm/` | English method report and historical training records; the `code/` package is the runnable implementation |
| `research/README.md` | Results provenance, video interpretation, code scope, and historical archive definitions |
| `research/current-results.json` | Retained 100 mm evaluation and featured-video provenance record; not the source of every current poster figure |
| `scripts/build-report.mjs` | Page structure and extended copy |
| `scripts/render-method50.mjs` | Rendering of the 50 mm method section |
| `public/academic.css`, `public/app.js` | Layout, visual style, and browser interactions |
| `research/archive/2026-10-31/` | Historical CSV exports, figures, method configurations, and source notes; excluded from the website build output |

`scripts/build.mjs` is the build entry point. Rebuild and run the checks after editing. Do not edit generated files in `dist/`. `content/training.json` is a historical organizing record and does not generate the current page.

To add the author's Recording demonstration, place its MP4 and cover in `public/media/`, then set `recordingDemo.title`, `src`, `poster`, `duration`, and `description` in `content/site.json`. Describe only the operations visible in the supplied recording.

## Results and research code

The current Results section reproduces the poster's original figures for both obstacle heights, configured in `content/results.json`. [Figure provenance](research/results-figures.json) records the original PDF identity and figure crops. Preserve their original values, labels, and experimental scope when updating the page; the archived CSV is not a replacement source for all poster figures.

The 50 mm code package includes the actual controller, simulation environment, observation and action interfaces, reward definitions, PPO training loop, robot USD, recording-derived reference, and five model bundles. Its English run guide and dependency instructions describe complete-controller evaluation and independent training continuations of the supplied learned components. Isaac Sim, Isaac Lab, PyTorch, and RSL-RL are installed separately using the documented versions. A new continuation starts with fresh optimizer state and is not an exact historical resume or an automatic reconstruction from random initialization. Refer to the package guide for the precise checks performed and platform limitations.

Historical 100 mm CSV exports contain 94 method–condition rows: two methods across 39 known regression conditions and eight holdout conditions. Their completion rules, model identities, inclusion criteria, and measurement windows remain attached to those archived analyses. They do not define one combined benchmark for the current poster Results. `scripts/generate-research-figures.py` can redraw four historical 100 mm plots from that archive; it requires Python, NumPy, pandas, and Matplotlib and writes back to the archive.

Historical PDFs are retained in the archive. Their embedded QR codes may refer to earlier destinations; use the current public website for new poster QR codes.
