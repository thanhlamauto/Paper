"""Recompute the paper's SiT-XL/2 PCA maps with the SRA visualization code.

Run: modal run --profile thanhlamtba31 scripts/modal_sit_pca.py
"""

from pathlib import Path
import modal

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "measurements" / "sit_xl2_pca"
SRA_REVISION = "1723f85069408f6df7d11db35549575c97bfa5b2"
VAE_REVISION = "31f26fdeee1355a5c34592e401dd41e45d25a493"
CHECKPOINT_SHA256 = "e645b5cd82d1d645cfd9b7c96041b56b2a0aa61faed90c0869e79be02ab55aca"
CHECKPOINT_URL = (
    "https://www.dl.dropboxusercontent.com/scl/fi/as9oeomcbub47de5g4be0/"
    "SiT-XL-2-256.pt?rlkey=uxzxmpicu46coq3msb17b9ofa&dl=0"
)
LAYERS = [1, 3, 8, 13, 18, 23, 28]
NOISE_LEVELS = [0.7, 0.5, 0.3, 0.1]
SEED = 20261011

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch==2.7.1", "torchvision==0.22.1", "timm==1.0.15",
        "diffusers==0.33.1", "transformers==4.51.3", "accelerate==1.6.0",
        "huggingface_hub==0.30.2", "safetensors==0.5.3", "numpy==1.26.4",
        "scikit-learn==1.6.1", "pillow==11.1.0",
    )
    .env({"HF_HOME": "/cache/huggingface", "OMP_NUM_THREADS": "4"})
    .add_local_dir(DATA / "source", "/opt/pca_source")
)
cache = modal.Volume.from_name("lara-sit-pca-cache", create_if_missing=True)
app = modal.App("lara-sit-xl2-pca", image=image)


@app.function(volumes={"/cache": cache}, cpu=2, memory=4096,
              timeout=900, scaledown_window=2)
def prepare_models():
    import hashlib
    import json
    import urllib.request
    from huggingface_hub import snapshot_download

    path = Path("/cache/SiT-XL-2-256.pt")
    if not path.exists():
        print("Downloading official SiT-XL/2 checkpoint", flush=True)
        partial = path.with_suffix(".part")
        with urllib.request.urlopen(CHECKPOINT_URL, timeout=120) as response, partial.open("wb") as out:
            total = 0
            while chunk := response.read(8 * 1024 * 1024):
                out.write(chunk)
                total += len(chunk)
                if total % (256 * 1024 * 1024) == 0:
                    print(f"Checkpoint downloaded: {total // (1024 * 1024)} MiB", flush=True)
        partial.rename(path)
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != CHECKPOINT_SHA256:
        raise ValueError("Official checkpoint differs from the recorded PCA run")
    print("Downloading/caching SD VAE", flush=True)
    vae_path = snapshot_download(
        "stabilityai/sd-vae-ft-mse",
        revision=VAE_REVISION,
        allow_patterns=["config.json", "diffusion_pytorch_model.safetensors"],
        cache_dir="/cache/huggingface/hub",
    )
    info = {"checkpoint_sha256": digest, "checkpoint_bytes": path.stat().st_size,
            "vae_path": vae_path, "vae_revision": Path(vae_path).name}
    Path("/cache/models.json").write_text(json.dumps(info, indent=2))
    cache.commit()
    print("Models cached", flush=True)
    return info


@app.function(gpu="L4", volumes={"/cache": cache}, cpu=4, memory=16384,
              timeout=600, scaledown_window=2)
def extract_maps(input_image: bytes):
    import hashlib
    import importlib.metadata
    import io
    import json
    import sys
    import time
    import zipfile
    import numpy as np
    import torch
    from PIL import Image
    from diffusers import AutoencoderKL

    sys.path.insert(0, "/opt/pca_source")
    from sito import SiT_models
    from getfeature import get_transforms, encode_pixels
    from pcav import pca_v

    start = time.monotonic()
    cache.reload()
    models_info = json.loads(Path("/cache/models.json").read_text())
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.use_deterministic_algorithms(True)
    # CUBLAS requires this for deterministic FP32 matrix multiplication.
    import os
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    state = torch.load("/cache/SiT-XL-2-256.pt", map_location="cpu", weights_only=True)
    if "ema" in state:
        state = state["ema"]
    out_channels = state["final_layer.linear.weight"].shape[0] // 4
    model = SiT_models["SiT-XL/2"](
        input_size=32, num_classes=1000, learn_sigma=(out_channels == 8))
    model.load_state_dict(state, strict=True)
    del state
    model = model.to("cuda").eval().requires_grad_(False)
    vae = AutoencoderKL.from_pretrained(
        models_info["vae_path"], local_files_only=True,
        use_safetensors=True).to("cuda").eval().requires_grad_(False)
    photo = Image.open(io.BytesIO(input_image)).convert("RGB")
    pixels = get_transforms(256)(photo).unsqueeze(0).to("cuda")
    all_features, all_rgbs = [], []
    label = torch.tensor([99], device="cuda")  # ImageNet goose, zero-based.
    with torch.inference_mode():
        # One posterior draw and one Gaussian draw shared across all rows.
        # This removes per-row random variation from the time comparison.
        x0 = encode_pixels(vae, pixels)
        epsilon = torch.randn_like(x0)
        for sigma in NOISE_LEVELS:
            t = 1.0 - sigma  # Official SiT time increases from noise to data.
            xt = t * x0 + sigma * epsilon
            _, features = model(xt, torch.tensor([t], device="cuda"), label, LAYERS)
            assert len(features) == len(LAYERS)
            for feature in features:
                assert feature.shape == (1, 256, 1152)
                assert torch.isfinite(feature).all()
            # Unmodified SRA PCA implementation; each map has its own fit.
            rgbs = np.stack(pca_v(features, 3, 0.0)).astype(np.float32)
            assert np.isfinite(rgbs).all()
            all_features.append(np.stack([f[0].cpu().numpy() for f in features]))
            all_rgbs.append(rgbs)
            print(f"Extracted t={t:.2f}, noise={sigma:.2f}: {len(features)} layers", flush=True)
        decoded = vae.decode(x0 / 0.18215).sample
        reconstruction = ((decoded[0].permute(1, 2, 0).cpu().numpy() + 1) * 127.5).clip(0, 255).astype(np.uint8)
    maps = np.stack(all_rgbs)
    metadata = {
        "model": "SiT-XL/2", "checkpoint_source": CHECKPOINT_URL,
        **models_info, "sra_repository": "https://github.com/vvvvvjdy/SRA",
        "sra_revision": SRA_REVISION, "seed": SEED, "class_id": 99,
        "input_sha256": hashlib.sha256(input_image).hexdigest(),
        "input_size_original": list(photo.size), "image_resolution": 256,
        "layers": LAYERS, "layer_indexing": "one-based, outputs after each block",
        "timesteps": [round(1-s, 2) for s in NOISE_LEVELS],
        "noise_levels": NOISE_LEVELS, "path": "x_t = t*x_0 + (1-t)*epsilon",
        "posterior": "one seeded VAE posterior sample, scale=0.18215",
        "noise": "one seeded Gaussian tensor shared across every timestep",
        "normalization": "SRA sito.norm_feat: spatial min-max per channel, eps=1e-6",
        "pca": "SRA pcav.pca_v: 3 PCs fitted separately per cell; component-wise min-max RGB",
        "pca_color_comparability": "Each cell has its own PCA basis; equal RGB colors need not indicate equal features.",
        "differences_from_sra_main_pca": [
            "Official SiT timestep convention, equivalent to get_f baseline=True legacy=False",
            "Shared posterior latent and Gaussian noise across rows rather than resampling per row",
            "Separate SVG renderer using paper typography; PCA values unchanged",
        ],
        "strict_checkpoint_load": True, "precision": "float32, TF32 disabled",
        "gpu": torch.cuda.get_device_name(),
        "elapsed_gpu_seconds": time.monotonic() - start,
        "versions": {p: importlib.metadata.version(p) for p in
                     ["torch", "torchvision", "timm", "diffusers", "numpy", "scikit-learn", "pillow"]},
    }
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("metadata.json", json.dumps(metadata, indent=2) + "\n")
        buffer = io.BytesIO()
        np.savez_compressed(buffer, normalized_features=np.stack(all_features),
                            pca_rgb=maps, x0=x0.cpu().numpy(), epsilon=epsilon.cpu().numpy())
        archive.writestr("features_and_pca.npz", buffer.getvalue())
        for row, t in enumerate(metadata["timesteps"]):
            for col, layer in enumerate(LAYERS):
                buffer = io.BytesIO()
                Image.fromarray(np.rint(maps[row, col] * 255).clip(0,255).astype(np.uint8)).save(buffer, format="PNG")
                archive.writestr(f"maps/t_{t:.2f}_layer_{layer:02d}.png", buffer.getvalue())
        buffer = io.BytesIO()
        Image.fromarray(reconstruction).save(buffer, format="PNG")
        archive.writestr("vae_reconstruction.png", buffer.getvalue())
    print(f"Completed PCA extraction in {metadata['elapsed_gpu_seconds']:.1f}s", flush=True)
    return stream.getvalue()


@app.local_entrypoint()
def main():
    import io
    import zipfile
    prepare_models.remote()
    result = extract_maps.remote((DATA / "input_goose.png").read_bytes())
    with zipfile.ZipFile(io.BytesIO(result)) as archive:
        for name in archive.namelist():
            target = DATA / name
            if not target.resolve().is_relative_to(DATA.resolve()):
                raise ValueError("Invalid archive path")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(name))
    print(f"Saved real features, 28 PCA maps, and provenance to {DATA}")
