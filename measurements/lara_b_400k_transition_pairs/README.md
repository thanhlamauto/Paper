# LARA-B transition error for explicit layer pairs

The two panels in Figure 2(b,c) use `pairs.csv`. The eight pairs were selected before evaluating the checkpoint: panel (b) holds source layer 3 fixed and varies the gap; panel (c) holds the gap at two blocks and varies the source depth. Layer index 1 is the output after block 1; index 12 is the output after block 12.

- Checkpoint: `LamTNguyen/selfflow-checkpoints-20260510`, revision `cfaab90aae7f6cb30c8f559ebca6fd47253da223`, directory `depth-shortcut-B-hybrid-deep10-outputdistill-r010-l005-classcond-centered-logitnormal-mag-full`, step 400,000.
- Evaluation code: `Self-Flow` commit `a9e539824ff45043d21260002e4d53a1bd368839` on branch `codex/lara-pair-diagnostic`, based on `feat/lara-anonymous-review` commit `3986a08e6d27a77a7f26b8e5ee78ba83d333dfb6`. A copy is in `../../scripts/eval_transition_pairs.py`.
- Weights: EMA backbone and EMA predictor, no parameter updates; deterministic backbone forward.
- Data: all 49,920 records in the held-out ImageNet latent validation dataset `imagenet-vae-latents-train-v3`, including all 1,000 classes.
- Timestep and noise: one 50-bin logit-normal(0,1) timestep and Gaussian noise draw per image, reused for all pairs. Seed 20261005 controls the shuffled record order, timesteps, and noise.
- Metric: per-image mean over tokens of `1 - cosine(predicted target direction, actual target hidden-state direction)`, then mean over images. `se` is the sample standard deviation of image-level scores divided by sqrt(49,920); the largest normal-approximation 95% half-width is 0.00021.

The initial 16-image smoke run and 4,096-image pilot preceded the full-validation measurement. The paper reports only the full-validation results. `result.json` contains the unrounded values and protocol metadata, and `command.txt` records the VM invocation.
