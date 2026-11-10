# Runtime Installation and Robot Assets

The 50 mm controller runs in Isaac Sim and Isaac Lab with CUDA-enabled PyTorch and RSL-RL. The package includes the robot USD, recorded motion reference, controller configurations, and trained actor and critic parameters.

## Runtime environment

| Component | Version |
| --- | --- |
| Python | 3.11.15 |
| NVIDIA Isaac Sim distribution | 5.1.0.0 |
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

Isaac Lab is installed at source revision [`090aed18163b2194d5551c7919f7539283677743`](https://github.com/isaac-sim/IsaacLab/commit/090aed18163b2194d5551c7919f7539283677743), which specifies RSL-RL 5.0.1. The commands below pin this revision and the corresponding runtime packages. Execution tests used Windows 11 and an NVIDIA GeForce RTX 4080 Laptop GPU with 12 GiB VRAM, with 120 Hz physics and 15 Hz policy decisions.

`pyproject.toml` defines the project requirements and the `training` and `test` extras. Isaac Sim and Isaac Lab are installed separately. The initialized simulator supplies `omni`, `carb`, `pxr`, PhysX, and `video_encoding`. Reporting and export utilities additionally use PyArrow, Matplotlib, or ONNX.

## Windows installation

Start in `research/50mm/code` using Windows PowerShell with Conda and Git available. Installation follows the [Isaac Sim Python setup](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/install_python.html) and [Isaac Lab setup](https://isaac-sim.github.io/IsaacLab/v2.3.2/source/setup/installation/pip_installation.html), with the source revision specified above. The simulator requires Python 3.11. NVIDIA's guide includes the Windows long-path prerequisite.

Create an isolated environment and a constraint file for the core dependencies:

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

Install the simulator and CUDA-enabled PyTorch wheels, followed by Isaac Lab and its RSL-RL integration. The [PyTorch installation index](https://pytorch.org/get-started/previous-versions/) specifies the CUDA 12.8 wheel pairing; the constraints select [RSL-RL 5.0.1](https://pypi.org/project/rsl-rl-lib/5.0.1/).

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

For reporting, Parquet, and ONNX export, install the additional packages:

```powershell
python -m pip install 'pyarrow==21.0.0' 'matplotlib==3.10.3' 'onnx==1.21.0' 'onnxscript==0.7.0'
```

Activate the environment with `conda activate wlr50` in each terminal, then follow the [run guide](README.md). NVIDIA presents its license prompt on first use. Run `python -m pip check` to inspect the installed dependency set and `python scripts/run.py preflight --check-models` to check the project files and models.

## Execution coverage

The [execution results](VERIFICATION.md) document a complete 50 mm traversal, one early-motion PPO update, model reloading, and CPU checks of all model bundles in the environment above. Fresh-environment installation and Linux execution remain untested.

## Robot asset and motion reference

The simulator loads `assets/wlr_robot_drive_test.usd` directly. The asset contains 40 mesh primitives and requires no additional project USD layers, external meshes, or textures. Its standard `OmniPBR.mdl` material is supplied by Isaac Sim at `kit/mdl/core/Base/OmniPBR.mdl`. [assets/manifest.json](assets/manifest.json) records the model's file size and checksum.

The runtime reads the motion contract and FSM configuration from `configs/`. Recorded command events and metadata are included in `reference/v010/`, alongside semantic segments and phase snapshots. The trained stage parameters and their network configurations are in `checkpoints/`.

## Licenses

The project code and robot USD have no specified project-level license. Isaac Sim is distributed under NVIDIA's terms; Isaac Lab and RSL-RL use BSD-3-Clause. Third-party simulator, library, and material files are obtained from their official distributions under those terms.
