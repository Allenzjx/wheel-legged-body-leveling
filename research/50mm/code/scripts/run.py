"""Portable entry point for the supplied full-traversal 50 mm models.

The physical core, action projection, actor classes and PPO implementation are
the accompanying project code. This driver starts a new run with a fresh Adam
optimizer; it does not recreate historical provenance or resume historical RNG.
"""
from pathlib import Path
from types import SimpleNamespace
import argparse
import copy
import hashlib
import importlib
import importlib.metadata
import json
import math
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def checked_path(relative):
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("Package path escapes its root")
    return path


def verify_package():
    manifest = ROOT / "package-manifest.json"
    if not manifest.is_file():
        raise RuntimeError("Missing package-manifest.json. A maintainer must seal the package before use.")
    records = read(manifest)["files"]
    for record in records:
        path = checked_path(record["path"])
        if not path.is_file() or sha(path) != record["sha256"]:
            raise RuntimeError("Package file differs from its manifest: " + record["path"])
    return {"manifest_sha256": sha(manifest), "checked_files": len(records)}


def stage_record(stage):
    return read(ROOT / "stages.json")["stages"][stage]


def model_record(stage, override=None):
    path = Path(override).resolve() if override else checked_path(stage_record(stage)["model"])
    model = read(path)
    if model["stage"] != stage:
        raise ValueError("Model stage does not match the requested stage")
    weights = path.parent / model["weights"]["file"]
    if sha(weights) != model["weights"]["sha256"]:
        raise ValueError("Model archive checksum mismatch")
    return model, weights


def observations(values, device):
    import torch
    from tensordict import TensorDict
    tensor = torch.as_tensor([values], dtype=torch.float32, device=device)
    if not torch.isfinite(tensor).all():
        raise ValueError("Nonfinite measured observation")
    return TensorDict({"policy": tensor, "critic": tensor.clone()}, batch_size=[1], device=device)


def construction_observation(dimension):
    """A schema-valid inactive state for tensor construction, not a rollout."""
    values = [0.] * dimension
    values[0] = 1.  # Exactly one phase bit is required by the recorded layout.
    return values


def make_runner(stage, device, model_path=None, seed=1001):
    import numpy as np
    import torch
    from wlr50_clean.ppo.rl_library_wrapper import construct_runner, seed_training_rngs
    model, archive = model_record(stage, model_path)
    seed_training_rngs(seed)
    config = copy.deepcopy(model["runner_config"])
    config["device"] = device
    config["seed"] = seed
    dim = model["observation_dimension"]
    env = SimpleNamespace(num_envs=1, num_actions=12, device=device, cfg={"portable_stage": stage},
                          get_observations=lambda: observations(construction_observation(dim), device))
    runner = construct_runner(env, config, log_dir=None)
    with np.load(archive, allow_pickle=False) as data:
        for group in ("actor", "critic"):
            prefix = group + "::"
            state = {key[len(prefix):]: torch.from_numpy(data[key].copy()).to(device)
                     for key in data.files if key.startswith(prefix)}
            module = getattr(runner.alg, group)
            module.load_state_dict(state, strict=True)
            if any(not torch.equal(value, module.state_dict()[key]) for key, value in state.items()):
                raise ValueError("Loaded model tensor differs from its archive")
    actor = runner.alg.actor
    actor_parameters = list(actor.trainable_parameters()) if hasattr(actor, "trainable_parameters") else [p for p in actor.parameters() if p.requires_grad]
    rate = float(model["fresh_optimizer_learning_rate"])
    runner.alg.optimizer = torch.optim.Adam(actor_parameters + list(runner.alg.critic.parameters()), lr=rate)
    runner.alg.learning_rate = rate
    runner.logger.writer = None
    runner._semantic_policy_version = getattr(actor, "policy_version", None)
    if stage == "early":
        from wlr50_clean.ppo.semantic_rear_owner_profile import REAR_OWNER_POLICY
        runner._semantic_policy_version = REAR_OWNER_POLICY
    runner._semantic_front_replay = None
    runner.current_learning_iteration = 0
    runner.local_configuration = config
    if hasattr(actor, "assert_frozen_state"):
        actor.assert_frozen_state(runner.alg.optimizer)
    return runner, model


def preflight(check_models=False):
    import numpy as np
    package = verify_package()
    versions = {}
    for name in ("numpy", "PyYAML", "torch", "tensordict", "rsl-rl-lib", "isaacsim", "isaaclab"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    if versions["rsl-rl-lib"] != "5.0.1":
        raise RuntimeError("This package requires rsl-rl-lib 5.0.1")
    counts = {}
    for stage in read(ROOT / "stages.json")["stages"]:
        model, archive = model_record(stage)
        with np.load(archive, allow_pickle=False) as data:
            for item in model["weights"]["tensors"]:
                array = data[item["key"]]
                if list(array.shape) != item["shape"] or str(array.dtype) != item["dtype"] or not np.isfinite(array).all():
                    raise RuntimeError("Invalid numeric tensor in " + stage)
            counts[stage] = len(data.files)
        if check_models:
            import torch
            runner, _ = make_runner(stage, "cpu")
            runner.alg.eval_mode()
            with torch.inference_mode():
                action = runner.alg.actor(observations(construction_observation(model["observation_dimension"]), "cpu"), stochastic_output=False)
            if action.shape != (1, 12) or not torch.isfinite(action).all():
                raise RuntimeError("Invalid actor output")
            del runner
    return {"status": "PASS", "package": package, "versions": versions, "numeric_tensors": counts,
            "model_construction_checked": check_models, "physics_started": False}


def build_core(stage, app):
    if stage in ("rr", "post_rr"):
        name = "semantic_rr_capture_local" if stage == "rr" else "semantic_post_rr_front_prep"
        return importlib.import_module("wlr50_clean.ppo." + name).build_core(app)
    if stage in ("fl", "full"):
        from dataclasses import replace
        from wlr50_clean.ppo import semantic_fl_forward
        from wlr50_clean.ppo.semantic_fl_forward_task import config_from_sources, build_core as build_fl
        config = replace(config_from_sources(ROOT / "configs/recording_motion_contract.json", ROOT / "configs/fsm_states.yaml"),
                         **semantic_fl_forward.settings()["window_reward"])
        if stage == "fl":
            return build_fl(app, config=config)
        from wlr50_clean.ppo.semantic_fl_prior_retirement_task import build_core as build_full
        ramp = read(ROOT / "configs/ppo_fl_forward_prior_retirement_v1/local_training.json")["retirement_ramp_duration_s"]
        return build_full(app, config=config, ramp_duration_s=ramp)
    # Use the early stage's original measured 439-value interface, including
    # its owner state. The later RR prior uses a distinct explicit adapter.
    from wlr50_clean.ppo.semantic_backend import SemanticIsaacBackend
    from wlr50_clean.ppo.semantic_env import SemanticEpisodeEnv
    folder = ROOT / "configs/ppo_rr_rl_timing_policy_learning_v1"
    backend = SemanticIsaacBackend(app, audit_actuator_target_effect=True,
                                  execution_profile=folder / "execution_profile.yaml",
                                  task_spec_path=folder / "stage_task_spec.yaml")
    return SemanticEpisodeEnv(backend, collect_trace=False, action_config=folder / "execution_profile.yaml",
                              reward_config_path=folder / "reward_config.yaml", observation_schema_path=folder / "observation_schema.json")


def request(stage, runner, values, stochastic):
    obs = observations(values, runner.device)
    names = {"rr": "semantic_rr_capture_local", "post_rr": "semantic_post_rr_front_prep",
             "fl": "semantic_fl_forward", "full": "semantic_fl_prior_retirement"}
    if stage in names:
        module = importlib.import_module("wlr50_clean.ppo." + names[stage])
        return module.request(runner, obs, stochastic=stochastic)
    raw = runner.alg.act(obs) if stochastic else runner.alg.actor(obs, stochastic_output=False)
    return raw, {"raw_action_coordinates": 12}


def actor_active(stage, values):
    index = {"rr": 439, "post_rr": 465, "fl": 531}.get(stage)
    return True if index is None else bool(values[index])


def checked_step(core, raw):
    from wlr50_clean.ppo.semantic_training import verified_native_effect
    action = raw[0].detach().cpu().tolist()
    step = core.step(action)
    issued = step.info.get("applied_raw_full12", action)
    if list(issued) != action:
        raise RuntimeError("Applied raw action differs from the sampled policy request")
    verified_native_effect(step.info, tuple(issued))
    if step.truncated or not math.isfinite(float(step.reward)):
        raise RuntimeError("Unexpected truncation or nonfinite reward")
    return step


def episode_summary(core, step):
    return {"duration_seconds": float(core.frame.sim_time_s), "physics_tick": int(core.frame.physics_tick),
            "termination_reason": step.info.get("termination_reason"),
            "task_success": bool(step.info.get("task_success", False)),
            "full_task_success": bool(step.info.get("full_task_success", step.info.get("task_success", False)))}


def evaluate(core, runner, stage, args, run):
    import torch
    runner.alg.eval_mode()
    core.reset(seed=args.seed)
    decision = 0
    completed = False
    with (run / "decisions.jsonl").open("x", encoding="utf-8") as stream:
        while decision < args.max_decisions:
            with torch.inference_mode():
                raw, _ = request(stage, runner, core.observation, False)
                step = checked_step(core, raw)
            decision += 1
            stream.write(json.dumps({"decision": decision, "time_seconds": float(core.frame.sim_time_s),
                                     "phase": str(core.frame.state_id), "reward": float(step.reward),
                                     "terminated": bool(step.terminated), "raw_action": raw[0].cpu().tolist()}) + "\n")
            if decision % 128 == 0:
                stream.flush()
                print(json.dumps({"decisions": decision, "time_seconds": float(core.frame.sim_time_s), "phase": str(core.frame.state_id)}), flush=True)
            if step.terminated:
                completed = True
                break
    return {"status": "EPISODE_COMPLETE" if completed else "BOUNDED_PREVIEW", "policy_updates": 0,
            "decisions": decision, "episode": episode_summary(core, step),
            "scope": "One native full-traversal episode" if completed else "Stopped by the requested preview budget; not a completed trial"}


def save_model(runner, model, folder, update):
    import numpy as np
    folder.mkdir(parents=True, exist_ok=False)
    arrays = {group + "::" + name: tensor.detach().cpu().numpy()
              for group in ("actor", "critic") for name, tensor in getattr(runner.alg, group).state_dict().items()}
    np.savez_compressed(folder / "weights.npz", **arrays)
    result = copy.deepcopy(model)
    result["weights"] = {"file": "weights.npz", "sha256": sha(folder / "weights.npz"),
                         "tensors": [{"key": key, "shape": list(value.shape), "dtype": str(value.dtype)} for key, value in arrays.items()]}
    result["fresh_optimizer_learning_rate"] = float(runner.alg.learning_rate)
    result["new_training"] = {"updates_this_run": update, "optimizer_state_saved": False,
                              "scope": "New on-policy continuation; not an extension of the historical selected counters"}
    write(folder / "model.json", result)


def train(core, runner, model, stage, args, run):
    import numpy as np
    import torch
    from wlr50_clean.ppo.semantic_training import audited_ppo_update
    from wlr50_clean.ppo.semantic_fl_forward_actor import audited_fl_ppo_update
    horizon = int(stage_record(stage)["rollout_steps"])
    if args.decisions <= 0 or args.decisions % horizon:
        raise ValueError("--decisions must be a positive multiple of " + str(horizon))
    runner.alg.train_mode()
    counts = {"stored_decisions": 0, "actor_eligible_decisions": 0, "uncredited_prefix_decisions": 0,
              "ppo_updates": 0, "optimizer_steps": 0, "completed_episodes": 0}
    need_reset = True
    (run / "rollouts").mkdir()
    def prefix(stream):
        core.reset(seed=args.seed)
        for _ in range(3000):
            if actor_active(stage, core.observation):
                return
            with torch.inference_mode():
                raw, _ = request(stage, runner, core.observation, False)
                step = checked_step(core, raw)
            counts["uncredited_prefix_decisions"] += 1
            stream.write(json.dumps({"kind": "uncredited_prefix", "time_seconds": float(core.frame.sim_time_s),
                                     "raw_action": raw[0].cpu().tolist(), "terminated": bool(step.terminated)}) + "\n")
            if step.terminated:
                write(run / "prefix-outcome.json", episode_summary(core, step))
                raise RuntimeError("The retained prefix ended before this stage's learning interval")
        raise RuntimeError("Prefix exceeded the native 200-second task horizon")
    with (run / "decisions.jsonl").open("x", encoding="utf-8") as stream, (run / "updates.jsonl").open("x", encoding="utf-8") as updates:
        for iteration in range(args.decisions // horizon):
            for index in range(horizon):
                if need_reset:
                    prefix(stream)
                    need_reset = False
                active = actor_active(stage, core.observation)
                if stage in ("rr", "post_rr") and not active:
                    raise RuntimeError("Inactive transfer prefix entered PPO storage")
                with torch.inference_mode():
                    raw, _ = request(stage, runner, core.observation, True)
                    selected = raw.detach().clone()
                    old_logp = runner.alg.transition.actions_log_prob.detach().clone()
                    step = checked_step(core, raw)
                    nxt = observations(step.observation, runner.device)
                    done = torch.tensor([step.terminated], dtype=torch.bool, device=runner.device)
                    runner.alg.process_env_step(nxt, torch.tensor([step.reward], device=runner.device), done,
                                                {"time_outs": torch.zeros_like(done)})
                    if not torch.equal(runner.alg.storage.actions[index], selected) or not torch.equal(runner.alg.storage.actions_log_prob[index].view(-1), old_logp.view(-1)):
                        raise RuntimeError("Stored action or likelihood differs from the sampled request")
                counts["stored_decisions"] += 1
                counts["actor_eligible_decisions"] += int(active)
                stream.write(json.dumps({"kind": "on_policy", "decision": counts["stored_decisions"],
                                         "actor_eligible": active, "time_seconds": float(core.frame.sim_time_s),
                                         "reward": float(step.reward), "terminated": bool(step.terminated),
                                         "raw_action": raw[0].cpu().tolist()}) + "\n")
                if step.terminated:
                    counts["completed_episodes"] += 1
                    write(run / ("episode-%04d.json" % counts["completed_episodes"]), episode_summary(core, step))
                    need_reset = True
                if (index + 1) % 128 == 0:
                    stream.flush()
                    print(json.dumps({"counts": counts, "time_seconds": float(core.frame.sim_time_s)}), flush=True)
            with torch.inference_mode():
                runner.alg.compute_returns(nxt)
            storage = runner.alg.storage
            arrays = {key: getattr(storage, key).detach().cpu().numpy() for key in
                      ("actions", "actions_log_prob", "rewards", "dones", "values", "returns", "advantages")}
            arrays.update({"observations::" + key: value.detach().cpu().numpy() for key, value in storage.observations.items()})
            arrays.update({"distribution::" + str(i): value.detach().cpu().numpy() for i, value in enumerate(storage.distribution_params)})
            np.savez_compressed(run / "rollouts" / ("rollout-%04d.npz" % (iteration + 1)), **arrays)
            updater = audited_fl_ppo_update if stage == "fl" else audited_ppo_update
            report = updater(runner, likelihood_audit_path=run / "rollouts" / ("likelihood-%04d.json" % (iteration + 1)))
            if hasattr(runner.alg.actor, "assert_frozen_state"):
                runner.alg.actor.assert_frozen_state(runner.alg.optimizer)
            counts["ppo_updates"] += 1
            counts["optimizer_steps"] += report["optimizer_steps"]
            runner.current_learning_iteration = counts["ppo_updates"]
            updates.write(json.dumps(report) + "\n")
            updates.flush()
            save_model(runner, model, run / ("model-update-%04d" % counts["ppo_updates"]), counts["ppo_updates"])
    return {"status": "TRAINING_COMPLETE", "counts": counts,
            "scope": "Fresh-optimizer continuation from the supplied stage model; historical training is unchanged"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("preflight", "evaluate", "train"))
    parser.add_argument("--stage", choices=("early", "rr", "post_rr", "fl", "full"), default="full")
    parser.add_argument("--check-models", action="store_true")
    parser.add_argument("--model", type=Path, help="model.json from a previous portable run; still starts fresh Adam")
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--decisions", type=int, default=512)
    parser.add_argument("--max-decisions", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=1001)
    parser.add_argument("--device", default="cuda:0", choices=("cpu", "cuda:0"))
    parser.add_argument("--headless", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()
    if args.command == "preflight":
        print(json.dumps(preflight(args.check_models), indent=2))
        return
    if args.command == "train" and not stage_record(args.stage)["trainable"]:
        parser.error("The complete selected controller is an evaluation target; choose early, rr, post_rr or fl for new training")
    if args.run_dir is None:
        parser.error("--run-dir is required and must name a new directory under code/runs")
    if not 1 <= args.max_decisions <= 3000:
        parser.error("--max-decisions must be between 1 and 3000")
    run = args.run_dir.resolve()
    if not run.is_relative_to((ROOT / "runs").resolve()) or run == (ROOT / "runs").resolve():
        parser.error("Use a new subdirectory under code/runs")
    package = verify_package()
    run.mkdir(parents=True, exist_ok=False)
    app = None
    try:
        import torch
        import tensordict
        from isaaclab.app import AppLauncher
        app = AppLauncher(headless=args.headless, enable_cameras=False).app
        app.update()
        runner, model = make_runner(args.stage, args.device, args.model, args.seed)
        write(run / "run.json", {"status": "RUNNING", "command": args.command, "stage": args.stage,
                                 "seed": args.seed, "package": package, "source_model_sha256": model["weights"]["sha256"],
                                 "optimizer_initialization": "fresh Adam; no restored moments or historical RNG"})
        core = build_core(args.stage, app)
        result = evaluate(core, runner, args.stage, args, run) if args.command == "evaluate" else train(core, runner, model, args.stage, args, run)
        write(run / "result.json", result)
        print(json.dumps(result, indent=2), flush=True)
    except BaseException as exc:
        write(run / "failure.json", {"status": "FAILED", "error": str(exc), "traceback": traceback.format_exc()})
        raise
    finally:
        if app is not None:
            app.close(wait_for_replicator=False, skip_cleanup=True)


if __name__ == "__main__":
    main()
