# Local Line-Art Workflow

Use local extraction for uploaded photos and dense illustrations. Do not use image2 for line-art conversion.

## Flat Illustrations With Existing Ink

For white/light-background artwork with dark outlines and flat fills, select the
existing dark ink before skeleton tracing. This is thresholded ink selection,
not an edge-detection fallback.

Never use the color original as the positional `render-image` input. Solid
color regions produce medial-axis spiderwebs when skeletonized.

Prepare a guarded binary line-art PNG:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/whiteboard-video/scripts/prepare_flat_lineart.py" input.png \
  -o work/lineart.png \
  --width 960 \
  --report work/lineart-report.json
```

The script searches thresholds 45-85 and chooses the darkest-ink cutoff that
keeps foreground density at or below 5.5%. It fails when even the lowest cutoff
is too dense; route that source to a neural line-art provider instead of forcing
the threshold.

Then analyze and render with geometry/color separation:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/whiteboard-video/scripts/whiteboard_cli.py" analyze-image \
  work/lineart.png -o work/analysis.json --stroke-detail rich

python3 "${CODEX_HOME:-$HOME/.codex}/skills/whiteboard-video/scripts/whiteboard_cli.py" render-image \
  work/lineart.png \
  --source-image input.png \
  --source-fit exact \
  --size-from-image \
  --stroke-detail rich \
  --hand none \
  -o output.mp4 \
  --duration 14 --fps 24 --tail-color 3.5
```

Inspect the binary PNG and a mid-draw video frame. The line-art foreground
should contain outlines and intentional hatching only, with no filled face,
clothing, or background regions. Colored lettering may be absent during the
drawing phase and return during final color fill.

The model wrappers and setup guide live in the engine repository:
`whiteboard-video-engine/docs/MODELS.md`.

## Provider Order

`--lineart-provider auto` resolves in this order:

1. `WHITEBOARD_INFORMATIVE_DRAWINGS_CMD`, `informative-drawings` on PATH, or `tools/lineart/run_informative_drawings.py` with installed weights.
2. `WHITEBOARD_ANIME2SKETCH_CMD`, `anime2sketch-lineart` on PATH, or `tools/lineart/run_anime2sketch.py` with installed weights.

There is no edge-detection fallback. Missing neural weights should fail loudly.

External commands may contain `{input}` and `{output}` placeholders:

```bash
export WHITEBOARD_INFORMATIVE_DRAWINGS_CMD="python /path/to/run_informative_drawings.py {input} {output}"
export WHITEBOARD_ANIME2SKETCH_CMD="python /path/to/run_anime2sketch.py {input} {output}"
```

If placeholders are omitted, the CLI appends input and output paths.

## Commands

Extract line art:

```bash
python3 scripts/whiteboard_cli.py extract-lineart source.png \
  --provider auto \
  -o lineart.png
```

Optionally vectorize with vtracer:

```bash
python3 scripts/whiteboard_cli.py extract-lineart source.png \
  --provider auto \
  -o lineart.png \
  --svg-output lineart.svg
```

Render in one step:

```bash
python3 scripts/whiteboard_cli.py render-photo source.png \
  -o output.mp4 \
  --duration 15 --fps 30 \
  --lineart-provider auto \
  --stroke-detail rich \
  --hand asian
```

## Notes

- `Informative Drawings` `anime_style` should be the production default when weights are installed.
- `Anime2Sketch` is the second choice for illustration/anime-like sources.
- Do not use Canny/XDoG/edge-only fallback for production outputs.
- Keep the original color image as the fill source. Since line art is extracted locally from that same image, the final color fill should be spatially consistent without shrink/offset alignment fixes.
