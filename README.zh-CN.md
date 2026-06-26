<p align="center">
  <img src="docs/assets/hero.png" alt="白板手绘视频引擎" width="960">
</p>

# Codex 白板视频 Skill

[English](README.md)

[whiteboard-video-engine](https://github.com/gnipbao/whiteboard-video-engine) 的 Codex Skill 适配层。安装后，Codex 可以直接调用本地引擎，把图片、SVG、线稿或脚本转换成白板手绘视频。

本仓库只包含 Skill 指令和轻量 wrapper。渲染、模型 provider、笔画追踪和视频合成都在 engine 仓库中维护。

## 仓库分工

| 仓库 | 职责 |
| --- | --- |
| [whiteboard-video-engine](https://github.com/gnipbao/whiteboard-video-engine) | Python 包、渲染器、CLI、模型 wrapper、测试和文档 |
| [codex-whiteboard-video-skill](https://github.com/gnipbao/codex-whiteboard-video-skill) | Codex `SKILL.md`、工作流说明和 wrapper 脚本 |

## 效果演示

完整演示素材维护在 engine 仓库。

<table>
  <tr>
    <td width="50%">
      <strong>输入图</strong><br>
      <img src="https://raw.githubusercontent.com/gnipbao/whiteboard-video-engine/main/examples/cases/sports-illustration-anime2sketch/input.jpg" alt="输入插画" width="360">
    </td>
    <td width="50%">
      <strong>输出预览</strong><br>
      <a href="https://github.com/gnipbao/whiteboard-video-engine/blob/main/examples/cases/sports-illustration-anime2sketch/output.mp4">
        <img src="https://raw.githubusercontent.com/gnipbao/whiteboard-video-engine/main/examples/cases/sports-illustration-anime2sketch/output-preview.gif" alt="白板动画预览" width="360">
      </a><br>
      <a href="https://github.com/gnipbao/whiteboard-video-engine/blob/main/examples/cases/sports-illustration-anime2sketch/output.mp4">查看 MP4</a>
    </td>
  </tr>
</table>

## 安装

先安装引擎：

```bash
python3 -m pip install "git+https://github.com/gnipbao/whiteboard-video-engine.git"
```

再安装 Skill：

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/gnipbao/codex-whiteboard-video-skill.git \
  ~/.codex/skills/whiteboard-video
```

验证 wrapper：

```bash
python3 ~/.codex/skills/whiteboard-video/scripts/whiteboard_cli.py doctor
```

本地开发 engine 时：

```bash
python3 -m pip install -e /path/to/whiteboard-video-engine
```

## 在 Codex 中使用

提及已安装的 Skill：

```text
[$whiteboard-video](/Users/you/.codex/skills/whiteboard-video/SKILL.md)
把这张图片转成 15 秒手绘白板视频，线稿细节使用 rich，手势使用 asian。
```

底层会调用已安装的 engine：

```bash
python3 scripts/whiteboard_cli.py render-photo input.jpg \
  -o out/output.mp4 \
  --duration 15 \
  --lineart-provider auto \
  --stroke-detail rich
```

## 本地模型

Skill 使用 engine 的 provider 系统。本仓库不包含模型代码和权重。

模型应放在 Codex 执行命令的项目目录中，不要放进 `~/.codex/skills/whiteboard-video`。

推荐目录结构：

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
            netG_A_latest.pth        # 可选
          opensketch_style/
            netG_A_latest.pth        # 可选
    Anime2Sketch/
      weights/
        netG.pth
        improved.bin                 # 可选，有则优先使用
```

最小可用目录：

- Informative Drawings：需要 `tools/lineart/run_informative_drawings.py` 和 `tools/informative-drawings/checkpoints/model/anime_style/netG_A_latest.pth`。
- Anime2Sketch：需要 `tools/lineart/run_anime2sketch.py` 和 `tools/Anime2Sketch/weights/netG.pth` 或 `tools/Anime2Sketch/weights/improved.bin`。

也可以显式配置命令：

```bash
export WHITEBOARD_INFORMATIVE_DRAWINGS_CMD="/abs/project/.venv-lineart/bin/python /abs/project/tools/lineart/run_informative_drawings.py {input} {output}"
export WHITEBOARD_ANIME2SKETCH_CMD="/abs/project/.venv-lineart/bin/python /abs/project/tools/lineart/run_anime2sketch.py {input} {output}"
```

模型安装说明见：[whiteboard-video-engine/docs/MODELS.md](https://github.com/gnipbao/whiteboard-video-engine/blob/main/docs/MODELS.md)。

## 仓库内容

- `SKILL.md`：Codex 指令。
- `scripts/whiteboard_cli.py`：调用已安装 engine CLI 的 wrapper。
- `references/`：工作流说明。
- `examples/`：轻量示例和案例说明。

## 不包含

- engine 源码
- 模型仓库
- 模型权重
- 生成视频
- 用户上传素材

## 许可证

MIT。上游模型代码和权重遵循各自许可证。
