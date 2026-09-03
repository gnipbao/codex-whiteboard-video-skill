---
name: whiteboard-video
description: Generate smooth hand-drawn whiteboard and story videos directly inside Codex from text scripts, GPT Image 2 color storyboards, scene plans, SVGs, line art, or local images. Use when the user asks for SpeedPaint-like videos, block-by-block coarse/detail/crayon animation, local image-to-line-art extraction, stroke/path drawing, hand/pen-tip following, narration/TTS including Doubao Voice 2, FFmpeg composition, or script-to-video whiteboard workflows.
---

# Whiteboard Video

Use this skill to create local-first whiteboard videos without Canva. This skill is an adapter for the separately installed `whiteboard-video-engine` Python package. Uploaded photos and dense illustrations are converted to line art locally; do not use GPT Image 2 to generate final line art. For script-driven story videos, keep one registered asset pair per scene: GPT Image 2 creates the **color storyboard**, then a local neural extractor derives line art from that exact color file. The preferred stack is:

1. `gpt-image-2` for full-color storyboard frames only, never production line art or embedded captions.
2. `Informative Drawings` local model, preferably `anime_style`, for registered line-art extraction.
3. `Anime2Sketch` local model for illustration/anime-like sources or as the neural fallback.
4. Optional `vtracer` SVG vectorization when installed.
5. Optional Doubao Voice 2 (`seed-tts-2.0`) or Edge TTS for narration. Keep the default sidecar SRT for editing, or explicitly use `--burn-subtitles` for a ready-to-publish subtitled MP4.

There is no edge-detection fallback. If neither neural model is installed, `extract-lineart` and `render-photo` must fail instead of silently producing a weak outline.

## Quick Start

Install the engine before using this skill:

```bash
python3 -m pip install "git+https://github.com/gnipbao/whiteboard-video-engine.git"
```

For local engine development:

```bash
python3 -m pip install -e /path/to/whiteboard-video-engine
```

When the engine is installed in a virtual environment, invoke the wrapper with that environment's Python, or set `WHITEBOARD_ENGINE_PYTHON=/absolute/path/to/venv/bin/python`. The wrapper will re-exec only the explicitly configured interpreter.

Run commands from the project root that contains `tools/lineart`, but always call the installed Skill wrapper by absolute path. The wrapper delegates to the installed engine package while local model wrappers are auto-discovered from the current working directory.

Never call a project-local `whiteboard-video/scripts/whiteboard_cli.py`. Old project copies may prepend a bundled `src` directory and silently shadow the installed engine, causing stale defaults such as the procedural hand cursor to reappear.

```bash
MOCK=1 python3 "${CODEX_HOME:-$HOME/.codex}/skills/whiteboard-video/scripts/whiteboard_cli.py" run examples/ten-second-demo.md -o /tmp/whiteboard-demo.mp4 --scenes 2 --fps 30 --width 640 --height 360 --scene-assets direct-lineart --animation-preset block-speedpaint
python3 "${CODEX_HOME:-$HOME/.codex}/skills/whiteboard-video/scripts/whiteboard_cli.py" extract-lineart photo.png -o lineart.png --provider auto
python3 "${CODEX_HOME:-$HOME/.codex}/skills/whiteboard-video/scripts/whiteboard_cli.py" render-photo photo.png -o /tmp/photo-whiteboard.mp4 --duration 15 --fps 30 --lineart-provider auto --stroke-detail rich --hand asian
python3 "${CODEX_HOME:-$HOME/.codex}/skills/whiteboard-video/scripts/whiteboard_cli.py" render-image lineart.png --source-image photo.png --source-fit exact --size-from-image --color-fill contour-wipe -o /tmp/color-fill-whiteboard.mp4 --duration 15 --fps 30 --tail-color 4.5 --hand asian
python3 "${CODEX_HOME:-$HOME/.codex}/skills/whiteboard-video/scripts/whiteboard_cli.py" render-image examples/apple.svg -o /tmp/apple-whiteboard.mp4 --duration 2 --fps 24 --width 640 --height 360 --hand asian
python3 "${CODEX_HOME:-$HOME/.codex}/skills/whiteboard-video/scripts/whiteboard_cli.py" render-image examples/apple.svg -o /tmp/multiline-text.mp4 --duration 6 --fps 24 --width 720 --height 960 --draw-text-file caption.txt --draw-text-position top --draw-text-align left --draw-text-reveal line-wipe --draw-text-order before --hand none
python3 "${CODEX_HOME:-$HOME/.codex}/skills/whiteboard-video/scripts/whiteboard_cli.py" list-hands
python3 "${CODEX_HOME:-$HOME/.codex}/skills/whiteboard-video/scripts/whiteboard_cli.py" doctor
```

## Script to Story Video

The production scene pipeline is:

```text
script -> scene plan -> GPT Image 2 color frame -> local neural line art
       -> coarse local block -> local details -> local crayon color
       -> optional sparse handwritten annotations -> silent or narrated MP4
       -> editable sidecar SRT -> optional final subtitle burn-in
```

`block-speedpaint` infers spatial drawing blocks and runs the coarse/detail/color phases inside each block. Adjacent blocks and phases overlap slightly so the motion stays continuous. A narrated run can use phrase timing cues to pace this same drawing clock: active speech advances the picture and meaningful pauses briefly hold it. The pipeline always writes an editable SRT beside the MP4 and leaves the picture clean by default; pass `--burn-subtitles` only when the requested deliverable needs narration subtitles baked into the final MP4. Optional annotations are short, positioned labels that never enter the GPT storyboard, extracted line art, or object grouping; the renderer intentionally adds them as late scene-video pixels, independently of the final SRT subtitle layer.

Configure credentials through the shell or a secret manager, never in scripts, prompts, `project.json`, or committed `.env` files:

- Images and automatic scene planning: `OPENAI_API_KEY`; optional `OPENAI_BASE_URL` must point to the intended trusted OpenAI-compatible endpoint. It is not required when both `--scene-plan` and `--storyboard-dir` are supplied.
- Silent master: use `--tts-provider none`; no speech credential is initialized or required.
- Doubao new console: `DOUBAO_TTS_API_KEY` (aliases: `DOUBAO_API_KEY`, `MODEL_SPEECH_API_KEY`).
- Doubao legacy console: set both `DOUBAO_TTS_APP_ID` and `DOUBAO_TTS_ACCESS_KEY` instead of the API key.
- Doubao defaults: `DOUBAO_TTS_RESOURCE_ID=seed-tts-2.0`, `DOUBAO_TTS_ENDPOINT=https://openspeech.bytedance.com/api/v3/tts/unidirectional/sse`, `DOUBAO_TTS_VOICE=zh_female_vv_uranus_bigtts`, MP3 at 24 kHz. The provider requests Seed-TTS 2.0 subtitle timing and uses its sentence/word timestamps for animation and SRT timing. Use only a speaker ID enabled for the user's account and do not redirect credentials to another endpoint.

Run the real color-storyboard pipeline:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/whiteboard-video/scripts/whiteboard_cli.py" run story.md \
  -o /tmp/story.mp4 \
  --scenes 6 --fps 30 --width 1920 --height 1080 \
  --image-model gpt-image-2 --image-quality low \
  --scene-assets color-to-lineart --lineart-provider auto \
  --animation-preset block-speedpaint --draw-blocks 4 --block-overlap 0.16 \
  --tts-provider none
```

Use `--image-quality low` for drafts and `medium` for a final render when the visual gain justifies the extra cost. The full `run` command defaults to 30 fps, `gpt-image-2`, no burned narration, `block-speedpaint`, a preference of at most four natural spatial blocks, and `0.16` block overlap. Connected objects are never split merely to reach four; use `--draw-blocks 0` for uncapped automatic grouping up to `--max-draw-blocks`. Use `--tts-provider none` for a silent edit master, or select Doubao/Edge and pass `--voice <speaker-id>`. Both narrated and silent runs write `<video-name>.srt`. Add `--burn-subtitles` to render that SRT into the final `-o` MP4 while retaining the sidecar; style it with `--subtitle-font`, `--subtitle-font-size`, `--subtitle-margin-v`, and `--subtitle-outline`. The legacy `--captions` and `--no-captions` flags are deprecated no-ops and are mutually exclusive with `--burn-subtitles`. Scene annotations remain independent.

For a 16:9 Doubao Voice 2 delivery with burned narration subtitles:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/whiteboard-video/scripts/whiteboard_cli.py" run story.md \
  -o /tmp/story-subtitled.mp4 \
  --scenes 6 --fps 30 --width 1920 --height 1080 \
  --image-model gpt-image-2 --image-quality low \
  --scene-assets color-to-lineart --lineart-provider auto \
  --animation-preset block-speedpaint --draw-blocks 4 --block-overlap 0.16 \
  --tts-provider doubao --voice zh_female_vv_uranus_bigtts \
  --burn-subtitles --subtitle-font "sans-serif" \
  --subtitle-font-size 16 --subtitle-margin-v 22 --subtitle-outline 1.6
```

FFmpeg/libass burns subtitles only after the clean scene composition and SRT have succeeded. The engine renders to a temporary sibling file and atomically replaces the requested MP4, so a subtitle-filter failure leaves the clean MP4 and SRT available for recovery.

With Doubao Voice 2, use valid provider subtitle timing as the preferred narration clock. Group returned word timestamps into short readable phrase beats; drawing advances at a steady rate while a phrase is spoken and briefly holds across real punctuation pauses. The measured narration duration, not the estimated scene-plan duration, controls a narrated scene; `duration_sec` remains the silent-render fallback. Persist provider timing beside cached audio as `scene_NN.alignment.json`, and clamp every SRT cue to the real audio endpoint so no subtitle leaks into the visual tail hold. If Doubao returns no valid timing, retain valid authored `timing_cues`; only when neither exists should the SRT use deterministic estimated phrases while drawing keeps its continuous clock. Narrated composition must have one audio file for every scene; never compact a partial audio list because that shifts later voices into earlier scenes.

If Codex or another tool already generated the color storyboards, preserve their scene order and name them `scene_01.png`, `scene_02.png`, and so on (`.webp`, `.jpg`, and `.jpeg` also work). Save the approved scene list as JSON with `id`, `narration`, `image_prompt`, and positive `duration_sec` fields. An optional `annotations` list may contain at most two objects with `text`, `x`, and `y`; coordinates are normalized top-left positions. Keep each label to 2–5 Chinese characters when possible, leave most scenes empty, and keep `y <= 0.72` so the lower area remains available for post-production subtitles. An optional ordered `timing_cues` list accepts `text`, local `start_sec`, local `end_sec`, and optionally cumulative `draw_to` progress ending at `1.0`; use it for a pre-aligned silent or imported-audio workflow. In a Doubao run, valid official timestamps replace authored cues; authored cues remain the fallback if the provider returns no usable timing. Then supply both assets to bypass OpenAI scene planning and image generation entirely:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/whiteboard-video/scripts/whiteboard_cli.py" run story.md \
  -o /tmp/story-from-frames.mp4 \
  --scene-plan /absolute/path/to/scene-plan.json --fps 30 \
  --storyboard-dir /absolute/path/to/storyboards \
  --lineart-provider auto --animation-preset block-speedpaint --draw-blocks 4 \
  --tts-provider none
```

The scene-plan ids must be consecutive `1..N`; this locks each narration to `scene_01..scene_N` and makes `--scenes` unnecessary. In silent mode the engine initializes neither OpenAI nor a TTS provider when both the plan and storyboard directory are supplied.

For one color frame, inspect and tune block drawing independently:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/whiteboard-video/scripts/whiteboard_cli.py" render-photo scene_01.png \
  -o /tmp/scene-01.mp4 --duration 8 --fps 30 \
  --lineart-provider auto --animation-preset block-speedpaint \
  --draw-text "出发" \
  --max-draw-blocks 6 --block-order reading --block-overlap 0.08 \
  --hand asian
```

Use `--draw-blocks <count>` as a preferred maximum when a scene contains many independent islands; it never authorizes cutting a connected person or prop. Use `--block-sequence 1,0` only after inspecting inferred block IDs; it reorders blocks and rejects duplicates or unknown IDs.

## Workflow

1. Use `render-photo` for uploaded photos or dense illustrations. It extracts local line art first, then renders with the original image as the color-fill source.
2. Use `extract-lineart` when you want to inspect or reuse the line-art PNG before rendering.
3. Use `render-image` when the user already has a clean SVG or line-art PNG.
4. Use `plan-script` and `run` for script-driven scenes. In real `auto` mode, `run` generates a color scene with `gpt-image-2`, then extracts pixel-registered line art locally from that same file. Use `--scene-assets color-to-lineart` to make this choice explicit.
5. Use `analyze-image` to estimate stroke count and foreground density.
6. Use `compose` to concatenate rendered scene clips.
7. Use `--lineart-provider auto|informative|anime2sketch|anime|manga`. `auto` tries Informative Drawings first, then Anime2Sketch. `manga` is kept only as a compatibility alias for Anime2Sketch.
8. Configure external deep extractors through environment variables:
   - `WHITEBOARD_INFORMATIVE_DRAWINGS_CMD`
   - `WHITEBOARD_ANIME2SKETCH_CMD`
   Commands may include `{input}` and `{output}` placeholders; otherwise input and output are appended as positional arguments.
9. Use `--svg-output <line.svg>` with `extract-lineart` or `render-photo` when `vtracer` is installed and you want SVG paths instead of raster skeleton tracing.
10. Use `--hand asian|black|children|white|procedural|none` to select the hand cursor. Built-in PNG hands keep a fixed orientation and only translate with the pen tip.
11. Use a color source with the exact same pixel size/aspect/crop as the line art whenever possible, then render with `--source-image <source> --source-fit exact --size-from-image --color-fill contour-wipe`.
12. Before final color fill, the renderer snaps missing registered line-art pixels back to the redrawn canvas so small extracted-stroke omissions do not look unfinished. The default guide threshold is `235`: its binary mask is used only for tracing, grouping, and reveal coverage, while cleaned Anime2Sketch grayscale tones remain the visible pencil layer. Use `--no-lineart-snap` only for debugging.
13. Use `--stroke-detail rich` by default; use `--stroke-detail max` only when faces/logos/badges still lose too many short strokes.
14. Treat narration, subtitles, and annotations as separate roles. Narration controls story/audio timing; the editable sidecar SRT is always preserved and may either stay on the post-production track or be burned into the final MP4 with `--burn-subtitles`; annotations are optional scene-plan labels and never copy narration.
15. For `block-speedpaint`, positioned annotations appear late using a per-character left-to-right pencil/typewriter reveal. They are not added to image strokes, so they cannot change inferred object blocks. Use standalone `--draw-text` only for a deliberate short label or title. Use `--burn-subtitles`, not the deprecated `--captions`, when narration subtitles must be baked into the deliverable.
16. For crayon drawings that should begin as an uncolored sketch, do not animate traced strokes. Use `--line-reveal detail-wipe --hand none`; the initial layer keeps heavy outer contours plus dense neutral-black areas such as hair, while leaving colored surfaces and fine internal texture blank. Remaining details arrive through a soft left-to-right mask.
17. Pair that mode with `--color-fill left-to-right-gradient` to restore the original crayon color from left to right. A strong 10-second default is `--tail-color 4 --base-line-opacity 0.76`.
18. Prefer `--animation-preset block-speedpaint` for story scenes. Each natural object block progresses through coarse contours, local details, and left-to-right crayon color. Sparse annotations overlay late, during roughly the final 15% of the scene, and may overlap the drawing's last beats; they never delay the first stroke. Only the legacy standalone full-caption role may add a short pre-draw lead-in.
19. Use `--scene-plan <json> --storyboard-dir <dir>` for externally generated color frames named `scene_01.*`, `scene_02.*`, and so on. This skips OpenAI planning/image clients; the engine still extracts line art locally from every supplied frame.
20. Use `--tts-provider none` for a silent master, `--tts-provider doubao` for Doubao Voice 2, or `--tts-provider edge` for Edge TTS. Valid Doubao word timestamps are grouped into phrase beats that pace coarse lines, details, block color, and sparse annotations through one shared clock. Without valid provider timing, retain authored cues when present; only the no-provider-cue/no-authored-cue case uses estimated SRT phrases while preserving continuous drawing motion. `--burn-subtitles` consumes that same SRT after composition, so sidecar and picture timings stay identical. Cache provider timing in `audio/scene_NN.alignment.json`; invalidate it with changed narration, voice, or synthesis settings. Do not log, print, or commit provider credentials.
21. Real runs reject `--scene-assets direct-lineart`; it exists only for deterministic Mock previews. Production always keeps a GPT color source and locally extracted registered line art.
22. The pipeline normalizes color storyboards onto the project canvas before extraction and fingerprints the script plan, source, line art, audio, and render parameters so `--resume` cannot silently pair new content with stale layers.

Prefer `MOCK=1` for integration tests and low-cost previews. Real providers are lazy-loaded and require configured provider credentials only for script-to-scene image or narration generation, not for uploaded-photo line-art extraction.

## Local Line-Art Step

For uploaded photos:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/whiteboard-video/scripts/whiteboard_cli.py" extract-lineart source.png \
  --provider auto \
  -o lineart.png
```

Then render:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/whiteboard-video/scripts/whiteboard_cli.py" render-image lineart.png \
  --source-image source.png \
  --source-fit exact \
  --size-from-image \
  --color-fill contour-wipe \
  --stroke-detail rich \
  --line-thickness 1 \
  -o output.mp4 \
  --duration 15 --fps 30 --tail-color 4.5 --hand asian
```

Or use the one-step shortcut:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/whiteboard-video/scripts/whiteboard_cli.py" render-photo source.png \
  -o output.mp4 \
  --duration 15 --fps 30 \
  --lineart-provider auto \
  --stroke-detail rich \
  --hand asian
```

## Quality Rules

- Do not use GPT Image 2 for line-art conversion. `gpt-image-2` produces the color source only; local line-art extraction from that exact source is the source of truth.
- Prefer `Informative Drawings` `anime_style` for quality when installed.
- Prefer `Anime2Sketch` for illustration/anime-like inputs or when Informative Drawings is unavailable.
- Preserve Anime2Sketch tonal output: use its cleaned binary mask as the invisible motion guide and its surviving grayscale values as the visible line art. Do not flatten the presentation layer to solid black.
- Do not use Canny/XDoG/edge-only fallback for production outputs.
- Optional `vtracer` can convert extracted line-art bitmaps to SVG paths for smoother path sampling.
- Keep the original uploaded image as the color-fill source when dimensions match. Because the line art is extracted from that same image, no anti-shrink or source-alignment correction should be needed.
- Render quick previews at 640x360 and 12-24fps when speed matters; the full story pipeline defaults to 30fps, and final output should normally stay at 30fps unless 60fps is specifically needed.

## Implementation Notes

This skill does not vendor engine code. `scripts/whiteboard_cli.py` imports `whiteboard_skill.cli` from the installed `whiteboard-video-engine` package. Core engine modules live in the engine repository:

- `providers/lineart.py`: local line-art providers, Informative Drawings and Anime2Sketch wrappers, optional vtracer integration.
- `preprocess.py`: SVG parsing, raster binarization, Zhang-Suen skeletonization, 8-neighbor stroke tracing.
- `whiteboard.py`: classic stroke renderer plus `block-speedpaint`, hand/pen-tip cursor, line-art snap completion, separate text reveal, and crayon color fill.
- `pipeline.py`: resumable `work/<project_id>/` orchestration.
- `compose.py`: scene composition plus optional atomic FFmpeg/libass subtitle burn-in.
- `providers/`: mock, GPT Image 2/OpenAI, Edge TTS, and Doubao Voice 2 provider interfaces.

Read `references/pipeline.md` only when modifying or extending the full script pipeline.
