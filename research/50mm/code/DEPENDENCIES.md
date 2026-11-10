# Runtime dependencies and robot assets

This document describes the original 50 mm simulation environment and the asset copied into this public package. Versions were checked against the retained environment lock, the original runtime inventory, and the installed package metadata on 10 November 2026. This is a historical reproduction environment, not a claim of compatibility with arbitrary newer Isaac releases.

## Verified environment

| Component | Verified version |
| --- | --- |
| Python | 3.11.15 |
| NVIDIA Isaac Sim distribution | 5.1.0.0 |
| Isaac Lab repository `VERSION` marker | 2.3.2 |
| Isaac Lab core distribution (`isaaclab`) | 0.54.3 |
| Isaac Lab RL distribution (`isaaclab_rl`) | 0.5.1 |
| RSL-RL distribution (`rsl-rl-lib`) | 5.0.1 |
| PyTorch | 2.7.0+cu128 |
| torchvision | 0.22.0+cu128 |
| Gymnasium | 1.2.1 |
| TensorDict | 0.12.2 |
| NumPy | 1.26.0 |
| PyYAML | 6.0.2 |
| imageio-ffmpeg | 0.6.0 |
| PyArrow | 21.0.0 |
| Matplotlib | 3.10.3 |
| pytest | 9.0.3 |

The recorded Isaac Lab source revision is [`090aed18163b2194d5551c7919f7539283677743`](https://github.com/isaac-sim/IsaacLab/commit/090aed18163b2194d5551c7919f7539283677743). Its `source/isaaclab_rl/setup.py` pins `rsl-rl-lib==5.0.1`. This checkout reports `2.3.2` in its `VERSION` file, but it is **not** the `v2.3.2` release tag (that tag resolves to `37ddf626871758333d6ed89cf64ad702aef127d0`). Use the recorded revision below. The core distribution version is a separate identifier. The original implementation uses a CUDA device, 120 Hz physics and 15 Hz policy decisions. Its retained inventory reports an NVIDIA GeForce RTX 4080 Laptop GPU with 12 GiB VRAM; that observation is not a tested minimum hardware requirement.

The public `pyproject.toml` declares lightweight requirements and the `training` and `test` extras. It does not install the complete simulator. Some retained artifact/reporting paths additionally require PyArrow, Matplotlib or ONNX. The simulator supplies `omni`, `carb`, `pxr`, PhysX and `video_encoding` through its initialized runtime; installing a similarly named arbitrary package is not a substitute.

## Windows installation recipe

Use a new Conda environment in Windows PowerShell with Git available. Start in this repository's `research/50mm/code` directory. The commands use NVIDIA's [Isaac Sim 5.1 installation procedure](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/install_python.html), the [Isaac Lab 2.3.2 setup procedure](https://isaac-sim.github.io/IsaacLab/v2.3.2/source/setup/installation/pip_installation.html), and the exact historical source revision above. Python 3.11 is required by this simulator generation. NVIDIA's guide describes the Windows long-path prerequisite if installation encounters path-length errors.

Create an isolated environment and a core-version constraint file. These are the checked project versions, not a complete lock of every transitive dependency:

```powershell
$ResearchCode = (Get-Location).Path
conda create -n wlr50 python=3.11.15 -y
conda activate wlr50
$SoftwareRoot = Join-Path $env:USERPROFILE 'wlr50-dependencies'
New-Item -ItemType Directory -Path $SoftwareRoot -Force | Out-Null
$ConstraintFile = Join-Path $SoftwareRoot 'wlr50-core-constraints.txt'
@'
isaacsim==5.1.0.0
torch==2.7.0+cu128
torchvision==0.22.0+cu128
rsl-rl-lib==5.0.1
tensordict==0.12.2
gymnasium==1.2.1
numpy==1.26.0
PyYAML==6.0.2
imageio-ffmpeg==0.6.0
pyarrow==21.0.0
matplotlib==3.10.3
pytest==9.0.3
setuptools==81.0.0
'@ | Set-Content -LiteralPath $ConstraintFile -Encoding ascii
$env:PIP_CONSTRAINT = $ConstraintFile
python -m pip install 'pip==26.1.1' 'setuptools==81.0.0'
```

Install the pinned simulator and CUDA-enabled PyTorch wheels. The CUDA 12.8 index and PyTorch/torchvision pairing are listed on the [official PyTorch previous-versions page](https://pytorch.org/get-started/previous-versions/). Install Isaac Lab at the recorded commit and request only its RSL-RL framework integration; the [official RSL-RL 5.0.1 package](https://pypi.org/project/rsl-rl-lib/5.0.1/) is selected by the constraints.

```powershell
python -m pip install 'torch==2.7.0' 'torchvision==0.22.0' --index-url https://download.pytorch.org/whl/cu128
python -m pip install 'isaacsim[all,extscache]==5.1.0' --extra-index-url https://pypi.nvidia.com
$IsaacLabCheckout = Join-Path $SoftwareRoot 'IsaacLab-wlr50'
git clone https://github.com/isaac-sim/IsaacLab.git $IsaacLabCheckout
git -C $IsaacLabCheckout checkout --detach 090aed18163b2194d5551c7919f7539283677743
Push-Location $IsaacLabCheckout
.\isaaclab.bat --install rsl_rl
Pop-Location
python -m pip install -e "${ResearchCode}[training,test]"
python -m pip check
python -c "import torch; import importlib.metadata as m; print({n:m.version(n) for n in ['isaacsim','isaaclab','isaaclab_rl','rsl-rl-lib','tensordict','gymnasium']}); print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"
```

For the retained reporting, Parquet and ONNX-export utilities, install their separately observed versions in the same environment:

```powershell
python -m pip install 'pyarrow==21.0.0' 'matplotlib==3.10.3' 'onnx==1.21.0' 'onnxscript==0.7.0'
```

Use `conda activate wlr50` in future terminals. Run project commands with that environment's `python`. Review NVIDIA's normal license prompt on first use; these instructions do not pre-accept it. Do not run an unpinned bulk upgrade or remove version constraints to make a resolver conflict disappear. Investigate the specific conflict in the new environment. A successful metadata check is followed by the project's own CPU and simulator smoke checks; it is not proof of a completed training run.

## Verification scope and platform limits

The existing Windows environment's package versions, historical source revision and USD dependency closure were checked. This fresh-environment installation recipe was checked against official instructions and the exact source checkout, but was **not executed as a new installation**. Linux installation and runtime behavior have not been tested for this public package. Its Python code is not, by itself, evidence that the complete Isaac stack or all historical launch paths work on Linux.

The original broad research environment is not dependency-clean according to `pip check`: FastAPI 0.115.7 expects Starlette below 0.46.0 but has 0.49.1; IPython 9.13.0 expects psutil at least 7 but has 5.9.8; wheel 0.46.3 expects packaging at least 24 but has 23.0. No installed packages were changed during this audit. These existing conflicts are another reason to use a separate environment and inspect its own `pip check` result, rather than treating a full copy of the author's environment as a reproducible lockfile.

The upstream [Isaac Sim 5.1 documentation](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/install_python.html) now labels that release unsupported. This package retains it for historical compatibility; a move to a supported newer release requires separate code and result validation.

## Minimal robot asset

`assets/wlr_robot_drive_test.usd` is copied byte-for-byte from the original hash-locked robot model. It is 45,607,185 bytes (43.49 MiB), below GitHub's 100 MiB per-file limit. Its SHA-256 is:

```text
e8a2a2b1485a32a50e851a07b9dd8ac4945b78ec49b7fada2b61c3eeb1e18892
```

The model contains 40 Mesh prims. OpenUSD opened the stage successfully. A full `UsdUtils.ComputeAllDependencies` scan found no additional project USD layers, external mesh files or textures. It found the standard `OmniPBR.mdl` shader, supplied by the installed Isaac Sim/Kit material library at `kit/mdl/core/Base/OmniPBR.mdl`. With that directory in the resolver context, there were no unresolved dependencies. The shader is not vendored here; use the simulator's own material library. These checks validate the asset dependency closure, not physics behavior or rendered appearance.

The original SolidWorks export also contains a URDF and 13 STL files totaling 31,655,392 bytes. They are not required by this training runtime, which loads the USD directly, and are therefore omitted. No USD path, geometry, joint, physics or material content was rewritten during this copy. See [assets/manifest.json](assets/manifest.json) for the asset receipt.

## Recording reference and retained training state

The original project already includes its `reference/v010/accepted_steps.jsonl` (4,988,513 bytes), `metadata.json` (1,043 bytes), semantic segments, and historical phase snapshots. The accepted reference is `v010_20260806_220745_363972_manual`, with rear-right-first order. Do not replace it with another recording while retaining the original hashes or results.

The original training runtime consumes compact derived contracts; raw recording events are for the designated offline preparation/validation paths. Its source manifest also names a 138,746,819-byte recording video, but that video is absent from the audited `reference/v010` directory. The video is not a robot or training-state asset and is not copied here. Commands that validate that complete legacy video bundle require the separately supplied original media.

Retained policy continuation can require ancestor checkpoints and experiment-specific configuration beyond the robot USD. Use the documented training entry point and its named checkpoint lineage. Historical phase snapshots are provenance data; their presence does not certify every snapshot for a newer runtime or evaluator.

## License status

No explicit project-level license was found for the audited original training code or robot USD. This package does not invent a license or infer redistribution terms from a dependency's license. The old SolidWorks-export `package.xml` contains a generic `BSD` field alongside placeholder author information; that alone does not establish a specific license for the robot USD or this training implementation.

Installed metadata identifies Isaac Sim as NVIDIA proprietary software. The inspected Isaac Lab license is BSD-3-Clause, and RSL-RL 5.0.1 metadata identifies BSD-3-Clause. Third-party simulator, library and material files are not vendored in this asset package; obtain them from their official sources under their own terms.

The asset and dependency audit did not launch a simulator, train a model, change an original source file, or modify the robot model.
