# Codex Whiteboard Video Skill

Codex skill adapter for `whiteboard-video-engine`.

This repository contains only the Codex skill instructions, examples, and a
small CLI wrapper. It does not vendor the engine source code or model weights.

## Repositories

- Engine: `https://github.com/YOUR_ORG/whiteboard-video-engine`
- Skill: `https://github.com/YOUR_ORG/codex-whiteboard-video-skill`

Replace `YOUR_ORG` with your GitHub organization or username after publishing.

## Install

Install the engine first:

```bash
python3 -m pip install "git+https://github.com/YOUR_ORG/whiteboard-video-engine.git"
```

For local development:

```bash
python3 -m pip install -e /path/to/whiteboard-video-engine
```

Install the Codex skill:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/YOUR_ORG/codex-whiteboard-video-skill.git \
  ~/.codex/skills/whiteboard-video
```

For local development without GitHub:

```bash
rsync -a /path/to/codex-whiteboard-video-skill/ \
  ~/.codex/skills/whiteboard-video/
```

Verify:

```bash
python3 ~/.codex/skills/whiteboard-video/scripts/whiteboard_cli.py doctor
```

## Local Line-Art Models

The skill uses the engine's model provider system. Model code and weights are
not included in this skill repository.

For uploaded photos and illustrations, follow the engine model setup guide:

```text
whiteboard-video-engine/docs/MODELS.md
```

Expected model layout when using local auto-discovery:

```text
your-project/
  tools/
    lineart/
      run_informative_drawings.py
      run_anime2sketch.py
    informative-drawings/
    Anime2Sketch/
  .venv-lineart/
```

You can also configure commands with:

```bash
export WHITEBOARD_INFORMATIVE_DRAWINGS_CMD="python /path/to/run_informative_drawings.py {input} {output}"
export WHITEBOARD_ANIME2SKETCH_CMD="python /path/to/run_anime2sketch.py {input} {output}"
```

## Usage

Inside Codex, mention:

```text
[$whiteboard-video](/Users/you/.codex/skills/whiteboard-video/SKILL.md)
```

The skill will call:

```bash
python3 scripts/whiteboard_cli.py render-photo input.jpg -o out/output.mp4 --duration 15
```

The wrapper delegates to the installed engine package.

## What This Repo Contains

- `SKILL.md`: Codex instructions.
- `scripts/whiteboard_cli.py`: wrapper around installed engine CLI.
- `references/`: workflow notes.
- `examples/`: small demo inputs.

## What This Repo Does Not Contain

- engine source code
- PyTorch model code
- model weights
- generated videos
- user uploads

## License

MIT. The upstream line-art models have their own licenses and download terms.
