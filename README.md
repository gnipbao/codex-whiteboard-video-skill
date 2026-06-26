<p align="center">
  <img src="docs/assets/hero.png" alt="Whiteboard Video Engine" width="960">
</p>

# Codex Whiteboard Video Skill

[中文](README.zh-CN.md)

<p>
  <img alt="Codex Skill" src="https://img.shields.io/badge/codex-skill-111827">
  <img alt="Engine dependency" src="https://img.shields.io/badge/engine-whiteboard--video--engine-blue">
  <img alt="License MIT" src="https://img.shields.io/badge/license-MIT-green">
</p>

Codex Skill adapter for [whiteboard-video-engine](https://github.com/gnipbao/whiteboard-video-engine). It lets Codex call the installed engine to generate local whiteboard animation videos from images, SVGs, line art, or scripts.

This repository contains the Skill instructions and a thin CLI wrapper only. Rendering, model providers, stroke tracing, and video composition live in the engine repository.

## Repository Split

| Repository | Responsibility |
| --- | --- |
| [whiteboard-video-engine](https://github.com/gnipbao/whiteboard-video-engine) | Python package, renderer, CLI, model wrappers, tests, docs |
| [codex-whiteboard-video-skill](https://github.com/gnipbao/codex-whiteboard-video-skill) | Codex `SKILL.md`, workflow references, wrapper script |

## Demo

The full demo assets are maintained in the engine repository.

<table>
  <tr>
    <td width="50%">
      <strong>Input</strong><br>
      <img src="https://raw.githubusercontent.com/gnipbao/whiteboard-video-engine/main/examples/cases/sports-illustration-anime2sketch/input.jpg" alt="Sports illustration input" width="360">
    </td>
    <td width="50%">
      <strong>Output Preview</strong><br>
      <a href="https://github.com/gnipbao/whiteboard-video-engine/blob/main/examples/cases/sports-illustration-anime2sketch/output.mp4">
        <img src="https://raw.githubusercontent.com/gnipbao/whiteboard-video-engine/main/examples/cases/sports-illustration-anime2sketch/output-preview.gif" alt="Whiteboard animation output preview" width="360">
      </a><br>
      <a href="https://github.com/gnipbao/whiteboard-video-engine/blob/main/examples/cases/sports-illustration-anime2sketch/output.mp4">Open MP4</a>
    </td>
  </tr>
</table>

## Installation

Install the engine first:

```bash
python3 -m pip install "git+https://github.com/gnipbao/whiteboard-video-engine.git"
```

Install the Skill:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/gnipbao/codex-whiteboard-video-skill.git \
  ~/.codex/skills/whiteboard-video
```

Verify the wrapper:

```bash
python3 ~/.codex/skills/whiteboard-video/scripts/whiteboard_cli.py doctor
```

For local engine development:

```bash
python3 -m pip install -e /path/to/whiteboard-video-engine
```

## Usage in Codex

Mention the installed Skill:

```text
[$whiteboard-video](/Users/you/.codex/skills/whiteboard-video/SKILL.md)
Convert this image into a 15-second whiteboard animation with rich stroke detail and the asian hand cursor.
```

The wrapper delegates to the installed engine:

```bash
python3 scripts/whiteboard_cli.py render-photo input.jpg \
  -o out/output.mp4 \
  --duration 15 \
  --lineart-provider auto \
  --stroke-detail rich
```

## Local Models

The Skill uses the engine provider system. Model code and weights are not included here.

Put models in the project directory where Codex runs the command. Do not put model repositories or weights inside `~/.codex/skills/whiteboard-video`.

Recommended layout:

```text
my-whiteboard-project/
  .venv-lineart/
    bin/
      python
  tools/
    lineart/
      run_informative_drawings.py
      run_anime2sketch.py
    informative-drawings/
      checkpoints/
        model/
          anime_style/
            netG_A_latest.pth
          contour_style/
            netG_A_latest.pth        # optional
          opensketch_style/
            netG_A_latest.pth        # optional
    Anime2Sketch/
      weights/
        netG.pth
        improved.bin                 # optional; preferred when available
```

Minimum valid setups:

- Informative Drawings: `tools/lineart/run_informative_drawings.py` plus `tools/informative-drawings/checkpoints/model/anime_style/netG_A_latest.pth`.
- Anime2Sketch: `tools/lineart/run_anime2sketch.py` plus `tools/Anime2Sketch/weights/netG.pth` or `tools/Anime2Sketch/weights/improved.bin`.

You can also set explicit commands:

```bash
export WHITEBOARD_INFORMATIVE_DRAWINGS_CMD="/abs/project/.venv-lineart/bin/python /abs/project/tools/lineart/run_informative_drawings.py {input} {output}"
export WHITEBOARD_ANIME2SKETCH_CMD="/abs/project/.venv-lineart/bin/python /abs/project/tools/lineart/run_anime2sketch.py {input} {output}"
```

See the engine model guide: [whiteboard-video-engine/docs/MODELS.md](https://github.com/gnipbao/whiteboard-video-engine/blob/main/docs/MODELS.md).

## Contents

- `SKILL.md`: Codex instructions.
- `scripts/whiteboard_cli.py`: wrapper around the installed engine CLI.
- `references/`: workflow notes.
- `examples/`: lightweight examples and case notes.

## Not Included

- engine source code
- model repositories
- model weights
- generated videos
- user uploads

## License

MIT. Upstream model code and weights keep their own licenses.
