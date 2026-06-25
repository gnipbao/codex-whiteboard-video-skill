# Local Line-Art Workflow

Use local extraction for uploaded photos and dense illustrations. Do not use image2 for line-art conversion.

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
