"""Analyze real launcher screen recordings for progression, seams and blank panels.

Requires numpy + imageio-ffmpeg. Pass video, artwork crop bounds, and output JSON.
Matching compares rendered crops to the 96 bundled frames, concentrating on the
moving petal or snow pixels. Compression/scale mismatches make this approximate; the
nearest-frame error is recorded, never used as a claim of universal correctness.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if (ROOT/".temp-python-tools").exists():
    sys.path.insert(0, str(ROOT/".temp-python-tools"))
import imageio_ffmpeg
import numpy as np
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("video", type=Path)
parser.add_argument("--crop", nargs=4, type=int, required=True, metavar=("L", "T", "R", "B"))
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--artwork", choices=["petal", "immortals", "winter"], default="petal")
args = parser.parse_args()
references = np.stack([np.asarray(Image.open(ROOT/f"app/src/main/res/drawable-nodpi/{args.artwork}_frame_{i:03d}_pixels.png").convert("RGB"), dtype=np.int16) for i in range(96)])
canvas=(references.shape[2],references.shape[1])
moving = np.any(references != references[0], axis=(0,3))
# Include neighboring pixels to tolerate subpixel scaling in the host.
moving |= np.roll(moving, 1, 0) | np.roll(moving, -1, 0) | np.roll(moving, 1, 1) | np.roll(moving, -1, 1)
ref_samples = references[:, moving, :]
reader = imageio_ffmpeg.read_frames(str(args.video), pix_fmt="rgb24")
metadata = next(reader)
width, height = metadata["size"]
matches, errors, brightness = [], [], []
for data in reader:
    frame = Image.frombytes("RGB", (width, height), data).crop(args.crop).resize(canvas, Image.Resampling.NEAREST)
    pixels = np.asarray(frame, dtype=np.int16)
    scores = np.mean(np.abs(ref_samples - pixels[moving]), axis=(1,2))
    best = int(np.argmin(scores))
    matches.append(best)
    errors.append(float(scores[best]))
    brightness.append(float(pixels.mean()))
transitions = [(i, value) for i,value in enumerate(matches) if i == 0 or value != matches[i-1]]
steps = [(b[1]-a[1]) % 96 for a,b in zip(transitions, transitions[1:])]
wraps = sum(b[1] < a[1] and (b[1]-a[1]) % 96 <= 3 for a,b in zip(transitions, transitions[1:]))
duration = metadata.get("duration") or len(matches)/metadata["fps"]
result = dict(video=args.video.name, crop=args.crop, reported_video_fps=metadata["fps"], decoded_frames=len(matches),
              duration_seconds=duration, unique_art_frames=len(set(matches)),
              transitions=len(transitions)-1, wraps=wraps,
              observed_transitions_per_second=(len(transitions)-1)/duration,
              forward_steps={str(k):steps.count(k) for k in sorted(set(steps))},
              mean_matching_error=float(np.mean(errors)), max_matching_error=max(errors),
              min_brightness=min(brightness), max_brightness=max(brightness),
              transitions_at_video_frame=transitions)
args.output.write_text(json.dumps(result, indent=2)+"\n")
print(json.dumps({k:v for k,v in result.items() if k != "transitions_at_video_frame"}, indent=2))
