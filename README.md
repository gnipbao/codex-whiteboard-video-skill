# Codex Whiteboard Video Skill

<p align="center">
  <a href="#中文"><kbd>中文</kbd></a>
  <a href="#english"><kbd>English</kbd></a>
</p>

## 中文

这是 `whiteboard-video-engine` 的 Codex Skill 适配层。它只包含 Skill 指令、示例和一个轻量 CLI wrapper，不包含引擎源码、模型代码或模型权重。

- Engine: <https://github.com/gnipbao/whiteboard-video-engine>
- Skill: <https://github.com/gnipbao/codex-whiteboard-video-skill>
- Author: <https://github.com/gnipbao>
- 个人介绍 / Bio: <https://ycnj2htgnvdy.feishu.cn/wiki/DOYRws0FmizhDAkkKGicvlpzndh?from=from_copylink>

## 安装

先安装引擎：

```bash
python3 -m pip install "git+https://github.com/gnipbao/whiteboard-video-engine.git"
```

本地开发时可以安装本地 engine：

```bash
python3 -m pip install -e /path/to/whiteboard-video-engine
```

再安装 Codex Skill：

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/gnipbao/codex-whiteboard-video-skill.git \
  ~/.codex/skills/whiteboard-video
```

没有 GitHub 远端时，也可以本地同步：

```bash
rsync -a /path/to/codex-whiteboard-video-skill/ \
  ~/.codex/skills/whiteboard-video/
```

验证：

```bash
python3 ~/.codex/skills/whiteboard-video/scripts/whiteboard_cli.py doctor
```

## 使用方式

在 Codex 里触发：

```text
[$whiteboard-video](/Users/you/.codex/skills/whiteboard-video/SKILL.md)
```

示例请求：

```text
[$whiteboard-video](/Users/you/.codex/skills/whiteboard-video/SKILL.md)
把这张图片转成 15s 手绘白板视频，使用 rich 线稿细节和 asian hand。
```

Skill 会调用：

```bash
python3 scripts/whiteboard_cli.py render-photo input.jpg \
  -o out/output.mp4 \
  --duration 15 \
  --lineart-provider auto \
  --stroke-detail rich
```

## Demo

完整媒体文件托管在 engine 仓库，Skill 仓库只引用展示：

<table>
  <tr>
    <td width="50%">
      <strong>输入图 / Input</strong><br>
      <img src="https://raw.githubusercontent.com/gnipbao/whiteboard-video-engine/main/examples/cases/sports-illustration-anime2sketch/input.jpg" alt="Sports illustration input" width="360">
    </td>
    <td width="50%">
      <strong>输出视频 / Output</strong><br>
      <video src="https://raw.githubusercontent.com/gnipbao/whiteboard-video-engine/main/examples/cases/sports-illustration-anime2sketch/output.mp4" controls width="360"></video><br>
      <a href="https://github.com/gnipbao/whiteboard-video-engine/blob/main/examples/cases/sports-illustration-anime2sketch/output.mp4">Open output video</a>
    </td>
  </tr>
</table>

## 本地线稿模型

Skill 使用 engine 的 provider 系统。模型代码和权重不包含在本仓库。

请按 engine 文档安装：

```text
whiteboard-video-engine/docs/MODELS.md
```

常见目录结构：

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

也可以显式配置：

```bash
export WHITEBOARD_INFORMATIVE_DRAWINGS_CMD="python /path/to/run_informative_drawings.py {input} {output}"
export WHITEBOARD_ANIME2SKETCH_CMD="python /path/to/run_anime2sketch.py {input} {output}"
```

## Example Case

案例说明放在：

```text
examples/cases/sports-illustration-anime2sketch/README.md
```

完整输入图和输出视频在 engine 仓库中：

```text
whiteboard-video-engine/examples/cases/sports-illustration-anime2sketch/
```

Skill 仓库保持轻量，避免把视频和上传素材打包进 Codex Skill。

## 仓库包含

- `SKILL.md`：Codex 使用说明。
- `scripts/whiteboard_cli.py`：调用已安装 engine 的 wrapper。
- `references/`：工作流说明。
- `examples/`：轻量示例和案例说明。

## 仓库不包含

- engine source code
- PyTorch model code
- model weights
- generated videos
- user uploads

## License

MIT. 上游线稿模型有各自许可证和下载条款。

---

## English

<p align="center">
  <a href="#中文"><kbd>中文</kbd></a>
  <a href="#english"><kbd>English</kbd></a>
</p>

This repository is the Codex Skill adapter for `whiteboard-video-engine`. It contains only Skill instructions, examples, and a small CLI wrapper. It does not vendor the engine source code, model code, or model weights.

- Engine: <https://github.com/gnipbao/whiteboard-video-engine>
- Skill: <https://github.com/gnipbao/codex-whiteboard-video-skill>
- Author: <https://github.com/gnipbao>
- Bio: <https://ycnj2htgnvdy.feishu.cn/wiki/DOYRws0FmizhDAkkKGicvlpzndh?from=from_copylink>

### Install

Install the engine first:

```bash
python3 -m pip install "git+https://github.com/gnipbao/whiteboard-video-engine.git"
```

Install the Codex Skill:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/gnipbao/codex-whiteboard-video-skill.git \
  ~/.codex/skills/whiteboard-video
```

Verify:

```bash
python3 ~/.codex/skills/whiteboard-video/scripts/whiteboard_cli.py doctor
```

### Usage

Mention this skill inside Codex:

```text
[$whiteboard-video](/Users/you/.codex/skills/whiteboard-video/SKILL.md)
```

The wrapper delegates to the installed engine package:

```bash
python3 scripts/whiteboard_cli.py render-photo input.jpg -o out/output.mp4 --duration 15
```

### Demo

The media files live in the engine repository. This Skill README embeds them by URL:

<table>
  <tr>
    <td width="50%">
      <strong>Input</strong><br>
      <img src="https://raw.githubusercontent.com/gnipbao/whiteboard-video-engine/main/examples/cases/sports-illustration-anime2sketch/input.jpg" alt="Sports illustration input" width="360">
    </td>
    <td width="50%">
      <strong>Output</strong><br>
      <video src="https://raw.githubusercontent.com/gnipbao/whiteboard-video-engine/main/examples/cases/sports-illustration-anime2sketch/output.mp4" controls width="360"></video><br>
      <a href="https://github.com/gnipbao/whiteboard-video-engine/blob/main/examples/cases/sports-illustration-anime2sketch/output.mp4">Open output video</a>
    </td>
  </tr>
</table>

### Local Line-Art Models

Follow the engine model setup guide:

```text
whiteboard-video-engine/docs/MODELS.md
```

The skill repository stays lightweight and does not include videos, user uploads, model repositories, or model weights.
