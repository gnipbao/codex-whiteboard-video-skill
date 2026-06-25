# Whiteboard Video Pipeline

This Codex skill delegates all commands to the installed
`whiteboard-video-engine` package through `scripts/whiteboard_cli.py`. Install
the engine before using these commands.

## Artifact Layout

```text
work/<project_id>/
  project.json
  images/
  audio/
  renders/
```

The final MP4 path is supplied with `-o`.

## Commands

```bash
MOCK=1 python3 scripts/whiteboard_cli.py run examples/ten-second-demo.md -o /tmp/demo.mp4 --scenes 2 --fps 24 --width 640 --height 360
python3 scripts/whiteboard_cli.py plan-script examples/ten-second-demo.md -o /tmp/scenes.json --scenes 2
python3 scripts/whiteboard_cli.py analyze-image examples/apple.svg -o /tmp/apple-analysis.json --width 640 --height 360
python3 scripts/whiteboard_cli.py extract-lineart source.png -o /tmp/lineart.png --provider auto
python3 scripts/whiteboard_cli.py render-photo source.png -o /tmp/photo.mp4 --duration 15 --lineart-provider auto --hand asian
python3 scripts/whiteboard_cli.py render-image examples/apple.svg -o /tmp/apple.mp4 --duration 2 --hand asian
python3 scripts/whiteboard_cli.py list-hands
```

## Rendering Decision Order

1. SVG: parse path/geometric primitives directly into ordered strokes.
2. Raster line art: threshold dark pixels, skeletonize to 1px strokes, trace continuous 8-neighbor paths.
3. Uploaded photo: run local line-art extraction first, then render the extracted line art with the original image as color source.
4. If extraction quality is poor, simplify the source scene or provide a cleaner line-art input; do not switch to edge-only fallback.

## Provider Modes

- `MOCK=1`: deterministic local LLM/image/TTS mocks for tests.
- Real mode: OpenAI-compatible LLM/image generation plus Edge TTS. Missing optional dependencies fail only when real mode is requested.

## Integration Test Target

Use the bundled 10-second script:

```bash
MOCK=1 python3 scripts/whiteboard_cli.py run examples/ten-second-demo.md -o /tmp/ten-second-demo.mp4 --scenes 2 --fps 24 --width 640 --height 360
```

For uploaded photos or dense illustrations, see `references/local-lineart.md` before rendering.
