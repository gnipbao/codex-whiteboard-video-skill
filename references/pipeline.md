# Whiteboard Video Pipeline

This Codex skill delegates all commands to the installed
`whiteboard-video-engine` package through `scripts/whiteboard_cli.py`. Install
the engine before using these commands. Always invoke the installed Skill
wrapper rather than a stale project-local copy:

```bash
CLI="${CODEX_HOME:-$HOME/.codex}/skills/whiteboard-video/scripts/whiteboard_cli.py"
```

If the engine lives in a virtual environment, invoke the wrapper with that environment's Python or export `WHITEBOARD_ENGINE_PYTHON=/absolute/path/to/venv/bin/python` before using `python3 "$CLI"`.

## Production Data Flow

```text
script
  -> resolve one of 30 visual styles and optional story theme
  -> scene plan and narration
  -> gpt-image-2 COLOR storyboard PNG
  -> Informative Drawings / Anime2Sketch line art from that same PNG
  -> block-speedpaint: coarse block -> details -> crayon color
  -> optional sparse positioned annotations
  -> silent master or optional Doubao Voice 2 / Edge narration
  -> speech-paced scene clips, editable sidecar SRT, and final MP4
  -> optional FFmpeg/libass subtitle burn-in
```

The color frame and extracted line art must remain pixel-registered. GPT Image
2 is never the production line-art generator, and text is never burned into
generated images. Sparse labels are rendered locally as late scene-video pixels;
they never enter the generated storyboard, extracted line art, or object
grouping. The pipeline always writes an editable SRT and leaves the composed
picture free of narration subtitles by default; `--burn-subtitles` optionally
renders that same SRT into the final delivery MP4 after composition.

## Artifact Layout

```text
work/<project_id>/
  project.json
  images/
    color/scene_01.png
    lineart/scene_01.png
  audio/
  renders/scene_01.mp4
```

The final MP4 path is supplied with `-o`; an SRT with the same basename is
written beside it.

`project.json` stores `visual_style_id`, the complete immutable
`visual_style_snapshot`, `visual_theme`, and the resolved line/fill/block
controls. A resumed job reuses that snapshot when no new style option is
provided, so a later library update cannot silently restyle an existing project.
Changing the selected recipe, its semantic fields, or `--theme` invalidates the
planning fingerprint and affected downstream artifacts.

For timing-capable providers, `audio/scene_NN.alignment.json` stores the exact
sentence and word intervals used by both the renderer and SRT writer. It is a
cache artifact, not authored input, and its fingerprint includes narration,
voice, provider identity, and output-affecting synthesis settings.

## Visual Style Resolution

The engine ships 30 media-named recipes with three whiteboard compatibility
levels: 15 `native`, 9 `adaptive`, and 6 `experimental`. `native` recipes have
clear recoverable outlines and separated color regions. `adaptive` recipes use
style-specific softer, denser, or dry-brush settings and should be previewed.
`experimental` recipes deliberately use features such as dense scribbles,
halftones, solid black masses, collage, weak outlines, or pixel jaggies that can
stress skeleton tracing.

The stable default is `warm-crayon-storybook`, optionally configured through
`WHITEBOARD_STYLE`. Inspect the catalog and locally computed recommendations:

```bash
python3 "$CLI" list-styles
python3 "$CLI" list-styles --compatibility native
python3 "$CLI" list-styles --json
python3 "$CLI" recommend-styles story.md --limit 5
python3 "$CLI" recommend-styles story.md --limit 5 --json
```

Run `recommend-styles` before a new story render, but do not turn it into a
mandatory clarification. Honor an explicit choice; use `--style auto` when the
user delegates selection; otherwise keep the stable default unless a clearly
better native recommendation follows directly from the requested subject. State
the resolved choice briefly and continue.

Style selectors belong only to `plan-script` and `run`. `plan-script` applies
the semantic prompt fields; `run` applies both those fields and the recipe's
renderer defaults. `render-photo` and `render-image` do not load style recipes
and reject `--style`, `--custom-style`, `--custom-style-file`, and `--theme`.

`--style` accepts a stable id, order number, Chinese or English name, registered
alias, or `auto`. An inline description and a reusable file are also supported:

```bash
python3 "$CLI" run story.md -o /tmp/story.mp4 --style auto

python3 "$CLI" run story.md -o /tmp/story.mp4 \
  --custom-style "Loose blue-pencil travel sketch, one warm-orange accent, broad white space"

python3 "$CLI" run story.md -o /tmp/story.mp4 \
  --custom-style-file /absolute/path/to/style.json \
  --theme "Quiet early morning with restrained optimism"
```

`--style`, `--custom-style`, and `--custom-style-file` are mutually exclusive.
`--theme` can accompany any one of them and adds story-specific mood or art
direction. It is capped independently and cannot remove the production contract.
An inline description is capped at 4,000 characters; a custom file is capped at
64 KiB and may contain plain UTF-8 text or a constrained JSON object.

A reusable JSON recipe should inherit a tested built-in base and override only
what the new medium needs:

```json
{
  "extends": "colored-pencil-diary",
  "id": "custom-blue-pencil-travel-diary",
  "name_zh": "蓝铅笔旅行日记",
  "name_en": "Blue-pencil travel diary",
  "family": "自定义彩铅叙事",
  "summary": "松弛蓝铅笔轮廓和少量暖橙点色。",
  "compatibility": "native",
  "planner_guidance": "Stage each beat as one candid travel memory with complete people and naturally separated props.",
  "aesthetic": "Loose blue-pencil contours with visible pressure variation and broad untouched space.",
  "paper": "Clean warm-white drawing paper without a photographed desk or page frame.",
  "palette": "Prussian blue and dusty cyan with one restrained warm-orange accent.",
  "avoid": "photorealism, glossy paint, dense scenery, generated writing, logos, cropped subjects",
  "render": {
    "block_fill_style": "dry-brush",
    "stroke_detail": "rich",
    "line_thickness": 0,
    "line_art_snap": true,
    "line_art_snap_threshold": 236,
    "max_draw_blocks": 5,
    "draw_blocks": 3,
    "block_overlap": 0.18,
    "block_order": "reading"
  }
}
```

Supported custom JSON top-level fields are `extends`, `schema_version`, `id`,
`order`, `name_zh`, `name_en`, `family`, `summary`, `best_for`, `aliases`,
`compatibility`, `planner_guidance`, `aesthetic`, `paper`, `palette`, `avoid`,
and `render`. If supplied, `id` must begin with `custom-`; otherwise the engine
derives a stable custom id. `provenance` is intentionally not accepted from the
file. The engine records the resolved recipe provenance as user-authored.

Supported render values are deliberately bounded: `block_fill_style` is one of
`crayon|clean|soft-wash|dry-brush`; `stroke_detail` is
`balanced|rich|max`; `line_thickness` is `0..16`; snap threshold is
`1..254`; block counts are `1..24` (`draw_blocks` may be `null`); overlap is
`0..0.65`; and block order is `reading|source`.

For `run`, omitting renderer controls inherits these values from the resolved
style snapshot. The complete per-run override surface is:

- `--block-fill-style crayon|clean|soft-wash|dry-brush`
- `--stroke-detail balanced|rich|max`
- `--line-thickness 0..16`, where `0` requests automatic source-aware sizing
- `--line-art-snap` / `--no-line-art-snap` and
  `--line-art-snap-threshold 1..254`
- `--max-draw-blocks N`, `--draw-blocks N` or `0` for automatic
  grouping, `--block-overlap 0..0.65`, and `--block-order reading|source`
- `--block-sequence 1,0,...` for an inspected explicit inferred-block order;
  unlike the preceding fields, this is a run-time instruction rather than a
  style-recipe value

The similarly named single-image controls have fixed command defaults rather
than style inheritance: `render-photo` and `render-image` default to
`--line-thickness 0`, `--stroke-detail rich`, `--block-fill-style crayon`, six
maximum inferred blocks, `0.08` overlap, reading order, and enabled line-art
snap. Their snap spellings are `--no-lineart-snap` and
`--lineart-snap-threshold`; do not substitute the `run` spellings above.

Recipes control both image prompts and real renderer behavior; they are not
cosmetic labels. They contain text and numeric parameters only, use generic
media/production-method names rather than artist names, and do not bundle or
fetch third-party sample images, reference boards, brushes, or textures.

## Offline Mock Preview

Use the mock pipeline to validate scene splitting, timing, block animation, and
composition without API usage. Mock `auto` asset mode resolves to direct line
art; the explicit flag below makes that behavior visible:

```bash
MOCK=1 python3 "$CLI" run examples/ten-second-demo.md \
  -o /tmp/ten-second-demo.mp4 \
  --scenes 2 --fps 30 --width 640 --height 360 \
  --scene-assets direct-lineart \
  --animation-preset block-speedpaint
```

## Real Story Run

Inject credentials with the user's shell or secret manager. Never place values
in command history, prompts, committed files, or generated project metadata.

- OpenAI: `OPENAI_API_KEY`; `IMAGE_MODEL` defaults to `gpt-image-2` and
  `IMAGE_QUALITY` defaults to `low`.
- Doubao new console: `DOUBAO_TTS_API_KEY` (the engine also accepts
  `DOUBAO_API_KEY` or `MODEL_SPEECH_API_KEY`).
- Doubao legacy console: `DOUBAO_TTS_APP_ID` plus
  `DOUBAO_TTS_ACCESS_KEY` instead of the new API key.
- Doubao Voice 2 must use `DOUBAO_TTS_RESOURCE_ID=seed-tts-2.0` and
  `DOUBAO_TTS_ENDPOINT=https://openspeech.bytedance.com/api/v3/tts/unidirectional/sse`.
  Do not redirect credentials to another endpoint. The default speaker is
  `zh_female_vv_uranus_bigtts`; replace it only with a speaker enabled for the
  user's account. The provider requests `audio_params.enable_subtitle=true`;
  valid returned sentence/word timestamps pace drawing and produce the SRT.

Run the complete color-to-line-art path:

```bash
python3 "$CLI" run story.md \
  -o /tmp/story.mp4 \
  --scenes 6 --fps 30 --width 1920 --height 1080 \
  --style warm-crayon-storybook \
  --image-model gpt-image-2 --image-quality low \
  --scene-assets color-to-lineart --lineart-provider auto \
  --animation-preset block-speedpaint \
  --tts-provider none
```

The `run` defaults are 30fps, `gpt-image-2`, `image-quality=low`, no burned narration,
and `block-speedpaint`. Fill, line, snap, and natural-block values inherit the
resolved style snapshot when their `run` overrides are omitted. The stable
`warm-crayon-storybook` recipe currently resolves to automatic line width, rich
stroke detail, crayon fill, at most four preferred natural blocks, and `0.16`
overlap; another style can resolve differently. Connected objects are never
split to reach a count. Use `--draw-blocks 0` for automatic grouping up to the
resolved `max_draw_blocks`. Use `--image-quality medium` for final frames when
needed. Use `--tts-provider none` for a silent master, or select Doubao/Edge and
pass `--voice <speaker-id>`. Both modes produce a sidecar SRT. Add
`--burn-subtitles` to bake that SRT into the final `-o` MP4 while retaining the
sidecar. The legacy `--captions` and `--no-captions` flags are deprecated no-ops
and are mutually exclusive with the new burn-in flag.

For a narrated 16:9 delivery with subtitles already burned in:

```bash
python3 "$CLI" run story.md \
  -o /tmp/story-subtitled.mp4 \
  --scenes 6 --fps 30 --width 1920 --height 1080 \
  --image-model gpt-image-2 --image-quality low \
  --scene-assets color-to-lineart --lineart-provider auto \
  --animation-preset block-speedpaint --draw-blocks 4 --block-overlap 0.16 \
  --tts-provider doubao --voice zh_female_vv_uranus_bigtts \
  --burn-subtitles --subtitle-font "sans-serif" \
  --subtitle-font-size 16 --subtitle-margin-v 22 --subtitle-outline 1.6
```

The burn-in controls are:

- `--burn-subtitles`: burn the generated SRT into the final MP4; off by default.
- `--subtitle-font`: libass font family; default `sans-serif`, with glyph-compatible fallback.
- `--subtitle-font-size`: ASS scale-unit size; default `16` for 16:9 output.
- `--subtitle-margin-v`: lower safe-area margin in ASS scale units; default `22`.
- `--subtitle-outline`: black outline width in ASS scale units; default `1.6`.

Burn-in runs only after clean composition and SRT creation. It uses a temporary
sibling file, copies audio without re-encoding, preserves input frame timing,
and atomically replaces the requested output. If FFmpeg/libass fails, the clean
MP4 and sidecar SRT remain available.

In a narrated run, measured speech duration controls the scene clock; the
scene-plan `duration_sec` is retained for silent renders. Valid provider words
are grouped into short phrase beats. Visual progress is proportional to actual
spoken time, and gaps between phrases hold the drawing briefly. If provider
timing is invalid or absent, valid authored cues are retained; only when neither
source exists are deterministic estimated phrases used for the SRT while the
drawing stays on its continuous clock. The final visual tail remains
subtitle-free. Composition requires one narration file per scene so a missing
middle track can never pull later speech forward.

Additional Doubao controls are available through
`DOUBAO_TTS_FORMAT`, `DOUBAO_TTS_SAMPLE_RATE`,
`DOUBAO_TTS_SPEECH_RATE`, `DOUBAO_TTS_PITCH_RATE`,
`DOUBAO_TTS_LOUDNESS_RATE`, `DOUBAO_TTS_BIT_RATE`, and
`DOUBAO_TTS_TIMEOUT_SEC`. Keep the default MP3/24kHz settings unless the target
workflow needs something else.

## Precomputed Color Storyboards

Color frames produced by Codex image generation or another approved tool can
skip the pipeline's image-generation call. Store them in one directory using
the scene plan's one-based order:

```text
storyboards/
  scene_01.png
  scene_02.png
  scene_03.png
```

PNG, WebP, JPG, and JPEG are accepted. The supplied frames are still processed
by the configured local neural line-art provider. Save the matching approved
scene list as JSON with consecutive ids `1..N` and the fields `id`, `narration`,
`image_prompt`, and `duration_sec`. Each scene may also contain zero to two
`annotations` with short `text` plus normalized `x` and `y` top-left positions.
Most scenes should use none; keep `y <= 0.72` to protect the lower subtitle-safe
area for post-production. An optional ordered `timing_cues` list can contain
`text`, local `start_sec`, local `end_sec`, and an optional cumulative `draw_to`.
If `draw_to` is present, provide it on every cue, keep it increasing, and end at
`1.0`. Passing both inputs prevents initialization
of the OpenAI planning and image providers:

```bash
python3 "$CLI" run story.md \
  -o /tmp/story-from-frames.mp4 \
  --scene-plan /absolute/path/to/scene-plan.json --fps 30 \
  --storyboard-dir /absolute/path/to/storyboards \
  --lineart-provider auto --animation-preset block-speedpaint --draw-blocks 4 \
  --tts-provider none
```

The silent Codex-precomputed path needs no provider credential. The explicit
plan is included in resume fingerprints so changing narration, prompts, order,
duration, annotations, or timing cues invalidates stale downstream artifacts safely.

## Block-Speedpaint Controls

Within each inferred spatial block, the renderer draws a coarse structural
pass, adds local detail, then reveals that block's original crayon color from
left to right. Short annotations reveal character by character with a brief
pencil-like wipe only after the picture is readable. They live on a separate
overlay timeline and never become image strokes. They intentionally become
part of the scene-video pixels, separate from the optional final SRT burn-in.
Phase and block windows overlap slightly to avoid stop-start motion. With timing
cues, cue intervals advance this shared coarse/detail/color/annotation clock and
gaps briefly hold the picture. Without cues, the original continuous clock is
preserved.

`target_blocks` is an upper-bound preference, not a quota. Connected people,
props, buildings, and structural bridges remain indivisible; only objects with
real whitespace between them become separate left-to-right blocks. For raster
line art, the binary skeleton is an invisible motion guide. Cleaned
Anime2Sketch grayscale tones are revealed as the visible pencil layer so line
weight remains natural.

```bash
python3 "$CLI" render-photo scene_01.png \
  -o /tmp/scene-01.mp4 --duration 8 --fps 30 \
  --lineart-provider auto --animation-preset block-speedpaint \
  --draw-text "出发" \
  --max-draw-blocks 6 --block-order reading --block-overlap 0.08 \
  --hand asian
```

- For this standalone `render-photo` example, `--max-draw-blocks` defaults to
  `6`, `--draw-blocks` has no preferred-count override, `--block-order` defaults
  to `reading`, and `--block-overlap` defaults to `0.08`.
- `--draw-blocks`: preferred maximum natural block count; never cuts connected
  objects to reach it.
- `--block-sequence 1,0`: explicit inferred block-ID order; use only after
  inspection because duplicates and unknown IDs are errors.
- `annotations`: preferred scene-plan mechanism for 2–5 character explanatory
  labels. Use at most two and place them in nearby whitespace.
- `--draw-text`: a standalone short annotation for one-off renders.
- `--story-text`: legacy standalone full-caption input for one-off renders;
  full `run` subtitles come only from the generated sidecar SRT and are burned
  only when `--burn-subtitles` is explicit.

Full `run` also accepts these block controls, but omitted values inherit the
selected style rather than the standalone defaults above; use the complete
override list under Visual Style Resolution. Real runs do not accept
`direct-lineart`; that mode is deliberately limited to Mock previews because
the real image provider creates color storyboards.

Before extraction, generated and precomputed color frames are copied or
normalized onto the exact project canvas. Resume state includes content and
parameter fingerprints for the script plan, color sources, line art, narration, and rendered
clips, so changed assets or animation controls invalidate the right downstream
stages instead of reusing stale output.

## Utility Commands

```bash
python3 "$CLI" plan-script examples/ten-second-demo.md -o /tmp/scenes.json --scenes 2
python3 "$CLI" list-styles --compatibility native
python3 "$CLI" recommend-styles examples/ten-second-demo.md --limit 5
python3 "$CLI" analyze-image examples/apple.svg -o /tmp/apple-analysis.json --width 640 --height 360
python3 "$CLI" extract-lineart source.png -o /tmp/lineart.png --provider auto
python3 "$CLI" render-photo source.png -o /tmp/photo.mp4 --duration 15 --fps 30 --lineart-provider auto --hand asian
python3 "$CLI" render-image examples/apple.svg -o /tmp/apple.mp4 --duration 2 --fps 30 --hand asian
python3 "$CLI" list-hands
```

## Rendering Decision Order

1. SVG: parse path/geometric primitives directly into ordered strokes.
2. Raster line art: threshold dark pixels, skeletonize to 1px strokes, trace continuous 8-neighbor paths.
3. Uploaded photo: run local line-art extraction first, then render the extracted line art with the original image as color source.
4. If extraction quality is poor, simplify the source scene or provide a cleaner line-art input; do not switch to edge-only fallback.

## Provider Modes

- `MOCK=1`: deterministic local LLM/image/TTS mocks for tests.
- Real image mode: GPT Image 2 produces a color storyboard, followed by local
  Informative Drawings or Anime2Sketch extraction from the same source.
- `--tts-provider doubao`: Doubao Voice 2 / Seed-TTS 2 narration via the V3 SSE
  API, using either new-console or legacy credentials. Valid Chinese/English
  sentence timing drives the animation and SRT when the selected voice returns it;
  otherwise valid authored cues remain available as the fallback.
- `--tts-provider edge`: Edge TTS narration.
- `--tts-provider none`: no TTS initialization and a silent final MP4 whose
  durations come from the scene plan.
- When exact provider timing is absent, SRT phrases use deterministic punctuation
  and character-weight estimates, while drawing stays on its original smooth clock.
- Missing optional dependencies or credentials fail only when the relevant real
  mode is requested.

## Integration Test Target

Use the bundled 10-second script:

```bash
MOCK=1 python3 "$CLI" run examples/ten-second-demo.md \
  -o /tmp/ten-second-demo.mp4 \
  --scenes 2 --fps 30 --width 640 --height 360 \
  --scene-assets direct-lineart --animation-preset block-speedpaint
```

For uploaded photos or dense illustrations, see `references/local-lineart.md` before rendering.
