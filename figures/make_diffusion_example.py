"""Make the illustrative clean/noisy thumbnails used in Figure 1.

Source: Espaby, Golden perro.JPG, Wikimedia Commons, public domain.
https://commons.wikimedia.org/wiki/File:Golden_perro.JPG

The thumbnails illustrate x_t = alpha_t*x_0 + sigma_t*epsilon in pixel space.
They are a schematic, not model latents. A shared epsilon is used for both t.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


HERE = Path(__file__).resolve().parent
src = cv2.imread(str(HERE / "example_dog_public_domain.jpg"), cv2.IMREAD_COLOR)
if src is None or src.shape[:2] != (723, 960):
    raise RuntimeError("Expected the 960x723 Wikimedia Commons thumbnail")

# A face-centered square crop remains legible at the small icon size.
crop = src[10:690, 265:945]
clean = cv2.resize(crop, (192, 192), interpolation=cv2.INTER_AREA)
cv2.imwrite(str(HERE / "example_dog_clean.png"), clean)

x0 = clean.astype(np.float32) / 127.5 - 1.0
eps = np.random.default_rng(20261006).standard_normal(x0.shape).astype(np.float32)

for name, alpha in (("student", 0.95), ("ema", 0.86)):
    sigma = np.sqrt(1.0 - alpha * alpha)
    xt = alpha * x0 + sigma * eps
    image = np.clip((xt + 1.0) * 127.5, 0, 255).astype(np.uint8)
    cv2.imwrite(str(HERE / f"example_dog_noisy_{name}.png"), image)
