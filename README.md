# artgen — 随机生成当代艺术，附论文

一个讽刺项目。它把当代艺术常见的媒介、材料、议题、理论家和行话收集成一个知识库，
然后随机组合出：作品标题、展签、艺术家陈述、策展论文（带脚注）、图片/视频模型的 prompt，以及一个画廊网页。

## 快速开始

```bash
# 打印一件作品到终端（不写文件）
python3 -m artgen show --seed 7

# 生成 6 件作品到 out/，并生成 out/index.html 画廊
python3 -m artgen generate -n 6 --seed 100 --out out
```

没有 API key 时，渲染层使用 `dry` 模式：写出 prompt 并生成一张 SVG 占位图（"THE WORK IS NOT HERE. THIS IS THE POINT."）。

## 接入图片 / 视频模型

设置一个 key 即可自动选择 provider，也可用 `--provider` 强制指定。

| provider | 需要的环境变量 | 默认模型（可用环境变量覆盖） |
|---|---|---|
| `fal` | `FAL_KEY` | 图 `fal-ai/flux/dev`（`ARTGEN_FAL_IMAGE_MODEL`），视频 `ARTGEN_FAL_VIDEO_MODEL` |
| `replicate` | `REPLICATE_API_TOKEN` | 图 `black-forest-labs/flux-dev`（`ARTGEN_REPLICATE_IMAGE_MODEL`），视频 `ARTGEN_REPLICATE_VIDEO_MODEL` |
| `openai` | `OPENAI_API_KEY` | 图 `gpt-image-1`（`ARTGEN_OPENAI_IMAGE_MODEL`），不支持视频 |

```bash
export FAL_KEY=...
python3 -m artgen generate -n 3 --seed 500 --video   # --video 额外渲染一段视频
```

视频模型 ID 变化很快。渲染失败时会自动回退到占位图，并在 stderr 打印原因。请在 `artgen/render.py` 的 `DEFAULTS` 中更新模型 ID。

## 用 Claude 扩写论文

```bash
pip install anthropic
export ANTHROPIC_API_KEY=...
python3 -m artgen generate -n 1 --llm
```

`--llm` 把模板论文交给 Claude 扩写成约 1200 字的画册文章，保留所有事实和脚注。默认模型 `claude-opus-5`，已开启 server-side fallback。

## 目录

```
data/elements.json     知识库：媒介、材料、技法、视频意象、议题、理论家、动词/名词/形容词、标题模板、场地、画廊……
artgen/compose.py      随机组合出作品 spec
artgen/text.py         展签、艺术家陈述、策展论文、简介
artgen/prompts.py      图片 / 视频 prompt
artgen/render.py       dry / fal / replicate / openai
artgen/llm.py          Claude 扩写
artgen/gallery.py      out/index.html
out/<seed>-<slug>/     spec.json, label.md, statement.md, essay.md, bio.md, image_prompt.txt, video_prompt.txt, 媒体文件
video/demo/            demo 视频工程（HyperFrames）
```

## 扩展知识库

直接往 `data/elements.json` 的任意列表里加条目。`techniques` 和 `video_motifs` 里可以用 `{material}` 占位符。
`title_templates` 可用的占位符见 `artgen/compose.py` 里的 `ctx`。

## Demo 视频

```bash
npx hyperframes render video/demo --output video/demo/renders/artgen-demo.mp4 --quality standard --fps 30
```

视频里的所有文字都来自 `python3 -m artgen generate -n 6 --seed 100` 的真实输出。改 `video/demo/index.html` 里的文案即可换一组作品。
音乐由 `video/demo/scripts/make-music.py` 按节拍表合成，音效由 `video/demo/scripts/make-sfx.sh` 合成。
