# Sports Illustration Case

中文 | [English](#english)

这个案例对应 engine 仓库里的完整 demo：

```text
whiteboard-video-engine/examples/cases/sports-illustration-anime2sketch/
```

在 Codex 中可以这样请求：

```text
[$whiteboard-video](/Users/you/.codex/skills/whiteboard-video/SKILL.md)
把这张白底运动插画转成 15s 手绘白板视频，使用 Anime2Sketch，stroke-detail rich，长短线结合，最后轮廓感上色。
```

底层命令等价于：

```bash
python3 scripts/whiteboard_cli.py render-photo input.jpg \
  -o out/sports-illustration-anime2sketch-longmix-15s.mp4 \
  --duration 15 \
  --fps 30 \
  --lineart-provider anime2sketch \
  --stroke-detail rich \
  --hand asian \
  --tail-color 4.5 \
  --color-fill contour-wipe
```

Skill 仓库不保存视频和上传图片，避免 Codex Skill 安装包过大。完整演示素材由 engine 仓库维护。

---

## English

This case points to the full demo in the engine repository:

```text
whiteboard-video-engine/examples/cases/sports-illustration-anime2sketch/
```

Example Codex request:

```text
[$whiteboard-video](/Users/you/.codex/skills/whiteboard-video/SKILL.md)
Convert this clean sports illustration into a 15-second whiteboard animation using Anime2Sketch, rich stroke detail, mixed long/short strokes, and contour-aware color fill.
```

Equivalent command:

```bash
python3 scripts/whiteboard_cli.py render-photo input.jpg \
  -o out/sports-illustration-anime2sketch-longmix-15s.mp4 \
  --duration 15 \
  --fps 30 \
  --lineart-provider anime2sketch \
  --stroke-detail rich \
  --hand asian \
  --tail-color 4.5 \
  --color-fill contour-wipe
```

This skill repository intentionally does not include videos or uploaded images. The full demo assets live in the engine repository.
