"""Deterministic 320x180 pixel scene + 96-frame / 12-second petal loop.

Run with Python 3.11+ and Pillow 12.2.0. Original plate is bundled in art/source.
No asset generation occurs on Android. All resampling is nearest-neighbor.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "app/src/main/res"
WIDTH, HEIGHT, FRAME_COUNT, INTERVAL_MS = 320, 180, 96, 125
TAU = math.tau
PETAL_COLORS = ["#ffe0c8", "#ffc4c9", "#f9a9bd", "#ec87aa", "#cd6e98"]


def petal_specs() -> list[dict]:
    rng = random.Random(58321)
    # Hand-positioned release sites on the lower/right blossom sprays of the plate.
    sites = [(80, 91), (96, 75), (133, 92), (148, 61), (165, 77),
             (179, 98), (190, 76), (147, 102), (118, 42), (163, 52), (194, 90)]
    petals = []
    for i in range(27):
        sx, sy = sites[i % len(sites)]
        petals.append(dict(x=sx + rng.uniform(-4, 4), y=sy + rng.uniform(-3, 3),
                           phase=(i * FRAME_COUNT / 27 + rng.uniform(-1, 1)) % FRAME_COUNT,
                           dx=WIDTH + rng.uniform(8, 47) - sx,
                           dy=rng.uniform(36, 100), amplitude=rng.uniform(1.5, 5.5),
                           waves=rng.choice([1, 2]), swirl=rng.uniform(0, TAU),
                           size=2 if i % 5 == 0 else 1, color=i % len(PETAL_COLORS)))
    return petals


def position(petal: dict, frame: float) -> tuple[float, float, float]:
    t = ((frame + petal["phase"]) % FRAME_COUNT) / FRAME_COUNT
    # Linear prevailing wind plus bounded gusts: derivative remains predominantly rightward.
    x = petal["x"] + petal["dx"] * t + 3 * math.sin(TAU * t)
    y = petal["y"] + petal["dy"] * t
    y += petal["amplitude"] * (math.sin(TAU * petal["waves"] * t + petal["swirl"])
                               - math.sin(petal["swirl"]))
    return x, y, t


def corner_mask() -> Image.Image:
    mask = Image.new("L", (WIDTH, HEIGHT))
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, WIDTH-1, HEIGHT-1), radius=5, fill=255)
    return mask


def render_frame(base: Image.Image, frame: float) -> Image.Image:
    result = base.copy().convert("RGBA")
    draw = ImageDraw.Draw(result)
    for p in petal_specs():
        fx, fy, t = position(p, frame)
        x, y = round(fx), round(fy)
        if not (-3 <= x <= WIDTH+3 and -3 <= y <= HEIGHT+3):
            continue
        # Grow from a single blossom pixel over the first 0.4 s; no bright pop in open sky.
        if t < 0.012:
            continue
        color = PETAL_COLORS[p["color"]]
        turn = int(t * 16 + p["swirl"]) % 4
        draw.point((x, y), fill=color)
        if t > 0.035 and turn != 0:
            draw.point((x+1, y + (1 if turn == 1 else 0)), fill=color)
        if p["size"] == 2 and t > 0.035:
            draw.point((x, y+1), fill=PETAL_COLORS[max(0, p["color"]-1)])
            if turn == 2:
                draw.point((x-1, y+1), fill=color)
    result.putalpha(corner_mask())
    return result


def bitmap_xml(name: str) -> str:
    return (f'<bitmap xmlns:android="http://schemas.android.com/apk/res/android"\n'
            f'    android:src="@drawable/{name}" android:filter="false"\n'
            f'    android:antialias="false" android:dither="false" />\n')


def indexed_frame(im: Image.Image, base: Image.Image) -> Image.Image:
    """Lossless fixed-palette PNG: all original colors, one transparent index."""
    colors = sorted(set(base.get_flattened_data()))
    colors += [tuple(bytes.fromhex(c[1:])) for c in PETAL_COLORS]
    lookup = {color: index for index, color in enumerate(colors)}
    indices = bytes(lookup[(r,g,b)] if a else 255 for r,g,b,a in im.get_flattened_data())
    result = Image.frombytes("P", im.size, indices)
    result.putpalette([channel for color in colors for channel in color] + [0]*(768-3*len(colors)))
    result.info["transparency"] = 255
    return result


def main() -> None:
    for path in [RES/"drawable-nodpi", RES/"drawable", RES/"mipmap-nodpi", ROOT/"art/previews"]:
        path.mkdir(parents=True, exist_ok=True)
    source = Image.open(ROOT/"art/source/sakura-landscape.png").convert("RGB")
    base = source.resize((WIDTH, HEIGHT), Image.Resampling.NEAREST)
    # A fixed 96-color palette keeps the tiny scene readable and stable through every frame.
    base = base.quantize(colors=96, method=Image.Quantize.MEDIANCUT,
                         dither=Image.Dither.NONE).convert("RGB")
    base.save(ROOT/"art/scene-base.png", optimize=True)
    frame_images = []
    hashes = []
    for i in range(FRAME_COUNT):
        im = render_frame(base, i)
        name = f"petal_frame_{i:03d}"
        path = RES/f"drawable-nodpi/{name}_pixels.png"
        indexed_frame(im, base).save(path, optimize=True)
        (RES/f"drawable/{name}.xml").write_text(bitmap_xml(name+"_pixels"), encoding="utf-8")
        hashes.append(hashlib.sha256(path.read_bytes()).hexdigest())
        frame_images.append(im)
    (RES/"drawable/scene_preview.xml").write_text(bitmap_xml("petal_frame_000_pixels"), encoding="utf-8")
    frame_images[0].resize((960, 540), Image.Resampling.NEAREST).save(ROOT/"art/previews/painting.png")
    preview_frames = [im.convert("RGB").resize((640, 360), Image.Resampling.NEAREST) for im in frame_images]
    # GIF duration is in centiseconds, so alternate 120/130 ms to retain the 12 s loop.
    preview_frames[0].save(ROOT/"art/previews/sakura-loop.gif", save_all=True,
                           append_images=preview_frames[1:], duration=[120, 130]*48,
                           loop=0, optimize=True, disposal=1)
    source.crop((150, 110, 1060, 1020) if source.height >= 1020 else (120, 40, 980, 900)).resize(
        (192, 192), Image.Resampling.NEAREST).save(RES/"mipmap-nodpi/ic_launcher.png")
    catalog = ROOT/"app/src/main/java/com/sakurasunset/widget/FrameCatalog.kt"
    catalog.write_text('package com.sakurasunset.widget\n\n'
        '// Generated by tools/generate_assets.py. Do not reorder: frame 95 wraps to frame 0.\n'
        'object FrameCatalog {\n    const val INTERVAL_MS = 125\n'
        '    const val LOOP_MS = 12000\n    val resources = intArrayOf(\n' +
        ''.join(f'        R.drawable.petal_frame_{i:03d},\n' for i in range(FRAME_COUNT)) +
        '    )\n}\n', encoding="utf-8")
    metrics = dict(canvas=[WIDTH, HEIGHT], frames=FRAME_COUNT, fps=1000/INTERVAL_MS,
                   loop_ms=FRAME_COUNT*INTERVAL_MS, petals=len(petal_specs()),
                   rgba_bytes_per_frame=WIDTH*HEIGHT*4,
                   all_frames_decoded_upper_bound_bytes=WIDTH*HEIGHT*4*FRAME_COUNT,
                   png_bytes=sum(p.stat().st_size for p in (RES/"drawable-nodpi").glob("petal_frame*png")),
                   source_sha256=hashlib.sha256((ROOT/"art/source/sakura-landscape.png").read_bytes()).hexdigest(),
                   frame_sha256=hashes)
    (ROOT/"art/asset-manifest.json").write_text(json.dumps(metrics, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in metrics.items() if k != "frame_sha256"}, indent=2))


if __name__ == "__main__":
    main()
