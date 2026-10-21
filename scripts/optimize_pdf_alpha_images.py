"""Crop transparent padding in PDF images without changing their placement.

Cairo's SVG filters can produce page-sized image/mask pairs for tiny shadows.
Wrap each cropped image in a unit-square Form XObject, so existing image Do
operators, vector content, text, and page geometry remain unchanged.

Usage: python scripts/optimize_pdf_alpha_images.py input.pdf [output.pdf]
Requires PyMuPDF and Pillow.
"""

import argparse
from io import BytesIO
from pathlib import Path

import pymupdf
from PIL import Image


def optimize(source, target):
    document = pymupdf.open(source)
    images = {item[0]: item for page in document for item in page.get_images(full=True)}
    cropped_count = 0
    before_pixels = after_pixels = 0
    for xref, item in images.items():
        _, mask_xref, width, height, bits, colorspace, *_ = item
        if not mask_xref or bits != 8 or colorspace != "DeviceRGB":
            continue
        # Only handle ordinary 8-bit RGB + gray alpha, without decode transforms
        # or a matte color that would require additional color correction.
        if (document.xref_get_key(mask_xref, "BitsPerComponent")[1] != "8"
                or document.xref_get_key(mask_xref, "ColorSpace")[1] != "/DeviceGray"
                or any(document.xref_get_key(ref, key)[0] != "null"
                       for ref, key in ((xref, "Decode"), (mask_xref, "Decode"),
                                        (mask_xref, "Matte")))):
            continue
        mask_info = document.extract_image(mask_xref)
        mask = Image.open(BytesIO(mask_info["image"])).convert("L")
        if mask.size != (width, height):
            continue
        bbox = mask.getbbox()
        if bbox is None:
            continue
        # Retain transparent border pixels for identical bilinear interpolation.
        left, top, right, bottom = bbox
        box = (max(0, left - 2), max(0, top - 2),
               min(width, right + 2), min(height, bottom + 2))
        crop_width, crop_height = box[2] - box[0], box[3] - box[1]
        if crop_width * crop_height >= width * height / 2:
            continue
        color = Image.open(BytesIO(document.extract_image(xref)["image"])).convert("RGB")
        crop = color.crop(box)
        crop_mask = mask.crop(box)

        new_mask = document.get_new_xref()
        mask_interpolation = document.xref_get_key(mask_xref, "Interpolate")[1]
        mask_interpolation = "true" if mask_interpolation == "true" else "false"
        document.update_object(new_mask, (
            f"<< /Type /XObject /Subtype /Image /Width {crop_width} "
            f"/Height {crop_height} /ColorSpace /DeviceGray /BitsPerComponent 8 "
            f"/Interpolate {mask_interpolation} >>"
        ))
        document.update_stream(new_mask, crop_mask.tobytes(), compress=True)

        new_image = document.get_new_xref()
        interpolation = document.xref_get_key(xref, "Interpolate")[1]
        interpolation = "true" if interpolation == "true" else "false"
        document.update_object(new_image, (
            f"<< /Type /XObject /Subtype /Image /Width {crop_width} "
            f"/Height {crop_height} /ColorSpace /DeviceRGB /BitsPerComponent 8 "
            f"/SMask {new_mask} 0 R /Interpolate {interpolation} >>"
        ))
        document.update_stream(new_image, crop.tobytes(), compress=True)

        # PDF image coordinates run from bottom to top; PIL rows run top down.
        sx, sy = crop_width / width, crop_height / height
        tx, ty = box[0] / width, (height - box[3]) / height
        document.update_object(xref, (
            "<< /Type /XObject /Subtype /Form /FormType 1 /BBox [0 0 1 1] "
            f"/Resources << /XObject << /CroppedImage {new_image} 0 R >> >> >>"
        ))
        document.update_stream(xref, (
            f"q {sx:.12g} 0 0 {sy:.12g} {tx:.12g} {ty:.12g} cm "
            "/CroppedImage Do Q\n"
        ).encode("ascii"), compress=True)
        cropped_count += 1
        before_pixels += width * height
        after_pixels += crop_width * crop_height

    # Write beside the target, so in-place optimization is also safe.
    temporary = target.with_name(target.name + ".optimizing")
    document.save(temporary, garbage=4, deflate=True)
    document.close()
    temporary.replace(target)
    print(f"Cropped {cropped_count} transparent image canvases: "
          f"{before_pixels:,} -> {after_pixels:,} pixels; "
          f"saved {target.stat().st_size:,} bytes to {target}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path, nargs="?")
    arguments = parser.parse_args()
    optimize(arguments.source, arguments.target or arguments.source)
