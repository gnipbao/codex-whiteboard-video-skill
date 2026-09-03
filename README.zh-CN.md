<p align="center">
  <img src="docs/assets/hero.png" alt="白板手绘视频引擎" width="960">
</p>

# Codex 白板视频 Skill

[English](README.en.md)

[whiteboard-video-engine](https://github.com/gnipbao/whiteboard-video-engine) 的 Codex Skill 适配层。安装后，Codex 可以直接调用本地引擎，把图片、SVG、线稿或脚本转换成白板手绘视频，并从 30 种内置视觉风格中选择、推荐或扩展配方。

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
python3 "${CODEX_HOME:-$HOME/.codex}/skills/whiteboard-video/scripts/whiteboard_cli.py" render-photo input.jpg \
  -o out/output.mp4 \
  --duration 15 \
  --lineart-provider auto \
  --stroke-detail rich
```

始终使用上面的 Skill 绝对路径。不要调用当前项目中的 `whiteboard-video/scripts/whiteboard_cli.py`；旧副本可能把内置 `src` 放到 Python 路径最前面，从而覆盖已安装 engine 的最新默认值。

## 视觉风格

引擎内置 30 种以媒介、画材和制作方法命名的版本化风格。风格不是只追加
一句提示词：它还会控制实际的填色材质、笔画细节、线宽、line-art snap、
自然分块数量、重叠和顺序。最终配方及可选 `--theme` 会保存到
`project.json` 的 style snapshot，并参与规划与续跑指纹。

风格选择参数只属于 `plan-script` 和 `run`：前者使用提示词语义，后者还会
让渲染参数继承所选配方。`render-photo` / `render-image` 不接受风格选择参数，
也不继承配方；单图命令有自己的固定默认值，包括 `--line-thickness 0`、
`--stroke-detail rich`、`--block-fill-style crayon` 和 `--block-overlap 0.08`。

白板适配等级：

- `native`（15）：`warm-crayon-storybook`、`colored-pencil-diary`、
  `clean-whiteboard`、`minimal-line-explainer`、`marker-whiteboard`、
  `rough-diagram`、`pressure-ink-notes`、`semantic-ink`、`anime-graphite`、
  `bean-doodle-infographic`、`organic-contour-doodle`、`naive-marker-notes`、
  `notebook-pencil-doodle`、`inked-storybook`、`blueprint-pencil`。
- `adaptive`（9）：`kid-crayon`、`raw-kid-crayon`、
  `emotional-watercolor-sketch`、`ink-wash-minimal`、`retro-gouache-concept`、
  `nordic-gouache-storybook`、`sunlit-storybook`、`editorial-portrait`、
  `real-crayon-paper`。
- `experimental`（6）：`ballpoint-scribble`、`warm-flat-storybook`、
  `zine-riso-collage`、`manga-screentone`、`linocut-editorial`、
  `ms-paint-doodle`。

`native` 最适合无人值守的正式生产；`adaptive` 应先看短预览；
`experimental` 的密集纹理、黑色形块或弱轮廓可能挑战骨架追踪。
稳定默认是 `warm-crayon-storybook`，也可通过 `WHITEBOARD_STYLE` 设置。

```bash
CLI="${CODEX_HOME:-$HOME/.codex}/skills/whiteboard-video/scripts/whiteboard_cli.py"
python3 "$CLI" list-styles
python3 "$CLI" list-styles --compatibility native
python3 "$CLI" list-styles --json
python3 "$CLI" recommend-styles story.md --limit 5
python3 "$CLI" recommend-styles story.md --limit 5 --json
```

Skill 在新的文案转故事任务开始时应先查看本地推荐，但无需每次暂停并要求
用户从 30 项中选择。用户点名时直接使用；用户委托自动选择时传
`--style auto`；没有有效美术偏好时保持稳定默认，或在题材明显匹配时采用
一个更合适的 `native` 推荐并简短说明。

```bash
python3 "$CLI" run story.md -o out/story.mp4 --style colored-pencil-diary
python3 "$CLI" run story.md -o out/story.mp4 --style auto
python3 "$CLI" run story.md -o out/story.mp4 \
  --custom-style "松弛蓝铅笔旅行速写，少量暖橙点色，大面积留白"
python3 "$CLI" run story.md -o out/story.mp4 \
  --custom-style-file /absolute/path/to/style.json \
  --theme "清晨、克制、带一点希望"
```

自定义 JSON 可通过 `extends` 继承稳定配方，再只覆盖需要变化的字段：

```json
{
  "extends": "colored-pencil-diary",
  "id": "custom-blue-pencil-travel",
  "name_zh": "蓝铅笔旅行日记",
  "name_en": "Blue-pencil travel diary",
  "palette": "普鲁士蓝和灰青色，只有一处暖橙重点",
  "render": {
    "block_fill_style": "dry-brush",
    "stroke_detail": "rich",
    "draw_blocks": 3
  }
}
```

`--style`、`--custom-style`、`--custom-style-file` 三者互斥；`--theme`
可以叠加在其中任意一种上。风格配方只含文字和数值参数，不内嵌或下载
第三方样图、艺术家参考板或笔刷，也不使用艺术家姓名作为风格名称。完整
工作流和 JSON 边界见 [references/pipeline.md](references/pipeline.md)。

自定义 JSON 若显式提供 `id`，必须以 `custom-` 开头；不要提供
`provenance`，该字段不属于用户可写 schema，引擎会把加载后的来源标记为
user-authored。对于 `run`，以下参数只有在显式传入时才覆盖配方，否则继续
继承 style snapshot：

- `--block-fill-style crayon|clean|soft-wash|dry-brush`
- `--stroke-detail balanced|rich|max`、`--line-thickness 0..16`
- `--line-art-snap` / `--no-line-art-snap`、`--line-art-snap-threshold 1..254`
- `--max-draw-blocks N`、`--draw-blocks N`（或 `0` 自动分组）、
  `--block-overlap 0..0.65`、`--block-order reading|source`
- `--block-sequence 1,0,...`（运行时显式顺序，不是配方字段）

注意单图命令关闭 snap 的拼写是 `--no-lineart-snap`，阈值参数是
`--lineart-snap-threshold`；不要和 `run` 的连字符形式混用。

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
    informative-drawings/              # 必须是完整 clone 的上游项目目录
      test.py
      model.py
      data.py
      util/
      checkpoints/
        model/
          anime_style/
            netG_A_latest.pth
          contour_style/
            netG_A_latest.pth        # 可选
          opensketch_style/
            netG_A_latest.pth        # 可选
    Anime2Sketch/                      # 必须是完整 clone 的上游项目目录
      model.py
      data.py
      utils.py
      weights/
        netG.pth
        improved.bin                 # 可选，有则优先使用
```

注意：`tools/informative-drawings/` 和 `tools/Anime2Sketch/` 不是只放权重的空目录，而是需要完整下载对应上游仓库。Skill 调用的 engine wrapper 会 `import` 这些仓库里的 Python 模块；如果只放 `*.pth` / `*.bin`，模型无法运行。

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
