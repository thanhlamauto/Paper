"""Measure held-out LARA direction error for prespecified layer pairs."""
import argparse
import csv
import json
from pathlib import Path
import time

import jax
import jax.numpy as jnp
import numpy as np
from flax.training import checkpoints

from train import build_model_config, build_predictor_source, create_train_state, get_arrayrecord_dataloader, sample_timestep_indices
from src.depth_shortcut import DepthShortcutPredictor, l2_normalize_tokens, predictor_config_from_name
from src.model import SelfFlowDiT

PAIRS = ((3, 4), (3, 6), (3, 9), (3, 12), (1, 3), (3, 5), (6, 8), (10, 12))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', required=True)
    parser.add_argument('--data-path', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--batch-size', type=int, default=16)
    parser.add_argument('--max-examples', type=int, default=4096)
    parser.add_argument('--seed', type=int, default=20261005)
    parser.add_argument('--weights', choices=('ema', 'online'), default='ema')
    args = parser.parse_args()
    root = Path(args.checkpoint)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    config = json.loads((root / 'wandb_run_summary.json').read_text())['config']
    assert config['model_size'] == 'B'
    assert config['shortcut_predictor'] == 'hybrid_deep_10'
    assert config['shortcut_predictor_normalize_input'] is False
    assert config['timestep_sampling_mode'] == 'logit_normal'
    assert args.batch_size > 0 and args.max_examples % args.batch_size == 0

    model_config = build_model_config('B', class_dropout_prob=config['cfg_dropout_rate'])
    state, _, _, _ = create_train_state(
        jax.random.PRNGKey(42), model_config, config['learning_rate'],
        config['grad_clip'], weight_decay=config['weight_decay'],
        predictor_variant=config['shortcut_predictor'],
        predictor_lr=config['shortcut_predictor_lr'],
        predictor_weight_decay=config['shortcut_predictor_weight_decay'],
        predictor_grad_clip=config['shortcut_predictor_grad_clip'],
        shortcut_training_mode=config['shortcut_training_mode'],
        shortcut_mag_abs_center=config['shortcut_mag_abs_center'],
        shortcut_mag_abs_scale=config['shortcut_mag_abs_scale'],
        predictor_use_class_input=config['shortcut_predictor_use_class_input'],
        predictor_class_fusion=config['shortcut_predictor_class_fusion'],
    )
    if args.weights == 'ema':
        backbone = checkpoints.restore_checkpoint(str(root / 'ema'), target=state.params['backbone'])
        predictor = checkpoints.restore_checkpoint(str(root / 'predictor_ema'), target=state.params['predictor'])
    else:
        params = checkpoints.restore_checkpoint(str(root), target=state.params)
        backbone, predictor = params['backbone'], params['predictor']
    del state
    print('Restored', args.weights, 'parameters; devices:', jax.devices(), flush=True)

    backbone_model = SelfFlowDiT(**model_config, per_token=False)
    predictor_cfg = predictor_config_from_name('hybrid_deep_10', model_config['hidden_size'])
    predictor_model = DepthShortcutPredictor(
        hidden_size=model_config['hidden_size'], depth=model_config['depth'],
        num_tokens=(model_config['input_size']//model_config['patch_size'])**2,
        gamma_out_init=0.001, mag_abs_center=config['shortcut_mag_abs_center'],
        mag_abs_scale=config['shortcut_mag_abs_scale'],
        num_classes=model_config['num_classes'], class_cond_input=True,
        class_cond_fusion=config['shortcut_predictor_class_fusion'], **predictor_cfg,
    )

    @jax.jit
    def encode(backbone_params, x0, labels, rng):
        tau_rng, noise_rng = jax.random.split(rng)
        q = sample_timestep_indices(
            tau_rng, x0.shape[0], config['shortcut_timesteps'],
            sampling_mode='logit_normal',
            logit_mean=config['timestep_logit_mean'],
            logit_std=config['timestep_logit_std'],
        )
        tau = q.astype(jnp.float32) / (config['shortcut_timesteps'] - 1)
        x1 = jax.random.normal(noise_rng, x0.shape)
        x_tau = (1.0 - tau[:, None, None]) * x1 + tau[:, None, None] * x0
        _, hidden_tuple, t_embed = backbone_model.apply(
            {'params': backbone_params}, x_tau, timesteps=tau, vector=labels,
            deterministic=True, return_hidden_states=True,
        )
        return jnp.stack(hidden_tuple, axis=0), t_embed

    @jax.jit
    def pair_error(predictor_params, hidden, t_embed, labels, source, target):
        source_hidden = hidden[source].astype(jnp.float32)
        target_hidden = hidden[target].astype(jnp.float32)
        predictor_input, source_log_m = build_predictor_source(source_hidden, normalize_input=False)
        predicted, _ = predictor_model.apply(
            {'params': predictor_params}, predictor_input, source, target,
            t_embed, source_log_m, use_timestep_embed=True,
            class_labels=labels,
        )
        predicted_dir = l2_normalize_tokens(predicted)
        target_dir = l2_normalize_tokens(target_hidden)
        return jnp.mean(1.0 - jnp.sum(predicted_dir * target_dir, axis=-1), axis=1)

    # Shuffle the held-out validation records so a subset spans the full class pool.
    iterator = iter(get_arrayrecord_dataloader(
        args.data_path, args.batch_size, is_training=True, seed=args.seed,
    ))
    rng = jax.random.PRNGKey(args.seed)
    rows = {pair: [] for pair in PAIRS}
    class_labels = []
    start = time.time()
    for batch_idx in range(args.max_examples // args.batch_size):
        x0, labels = next(iterator)
        class_labels.extend(np.asarray(labels, dtype=np.int32).tolist())
        x0 = jnp.asarray(x0, dtype=jnp.float32)
        labels = jnp.asarray(labels, dtype=jnp.int32)
        rng, batch_rng = jax.random.split(rng)
        hidden, t_embed = encode(backbone, x0, labels, batch_rng)
        for pair in PAIRS:
            per_image = pair_error(predictor, hidden, t_embed, labels,
                                   jnp.int32(pair[0]), jnp.int32(pair[1]))
            rows[pair].extend(np.asarray(jax.device_get(per_image), dtype=np.float64).tolist())
        if (batch_idx + 1) % 16 == 0:
            print('examples', (batch_idx + 1) * args.batch_size,
                  'elapsed_s', round(time.time() - start, 1), flush=True)

    summary = []
    for (source, target), values in rows.items():
        a = np.asarray(values, dtype=np.float64)
        summary.append(dict(source=source, target=target, gap=target-source,
                            n=len(a), mean=float(a.mean()), sd=float(a.std(ddof=1)),
                            se=float(a.std(ddof=1)/np.sqrt(len(a)))))
    with (output / 'pairs.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0]))
        writer.writeheader(); writer.writerows(summary)
    metadata = dict(checkpoint=str(root), data_path=args.data_path,
                    weights=args.weights, seed=args.seed,
                    max_examples=args.max_examples, batch_size=args.batch_size,
                    metric='mean over images and tokens of 1 - cosine(predicted direction, target hidden-state direction)',
                    timestep_sampling='discrete logit_normal(0,1), 50 bins',
                    data_sampling='fixed-seed shuffled subset of held-out validation latents',
                    unique_classes=len(set(class_labels)),
                    deterministic_backbone=True, elapsed_s=time.time()-start,
                    pairs=summary)
    (output / 'result.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    main()
