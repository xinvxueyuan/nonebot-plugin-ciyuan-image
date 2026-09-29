# nonebot-plugin-ciyuan-image

次元图：栗次元 ([t.alcy.cc](https://t.alcy.cc)) 随机图片 NoneBot 插件。
子命令 = 分类标题（已去除"自适应"后缀与技术名），超过 3 张自动以
[合并转发](https://github.com/xinvxueyuan/nonebot-plugin-merge-forward) 形式发送。

## 安装

```bash
pip install nonebot-plugin-ciyuan-image
# 依赖 nonebot-plugin-merge-forward（合并转发工具库）
pip install nonebot-plugin-merge-forward
# 可选：nonebot-plugin-htmlkit（分类列表渲染成图片，未装则回退纯文本）
pip install 'nonebot-plugin-ciyuan-image[htmlkit]'
```

本仓库为源码权威（`uv` 工程）。开发时依赖本地 merge-forward：
在 `C:\dev\nonebot-plugin-merge-forward` 下先 `uv pip install -e .` 或直接
`uv add nonebot-plugin-merge-forward --path ../nonebot-plugin-merge-forward`。

> ⚠️ Linux 部署 htmlkit 需要中文字体（如 `apt install fonts-noto-cjk`），
> 否则分类图里的中文会渲染成方块；Windows 下自动回退系统字体。

## 使用

```
次元图                    查看全部分类（htmlkit 渲染成图片，未装则纯文本）
次元图 二次元             随机 1 张
次元图 原神 5             随机 5 张
次元图 ysmp 10            也可直接用 slug
```

规则：**1-3 张直接发图；4 张及以上用合并转发**（一个转发卡片，每条一张图）。

## 分类表（2026-08 实测）

| 子命令 | slug | 接口 | 说明 |
| --- | --- | --- | --- |
| 二次元 | ycy | 直接端点 | 原"二次元自适应" |
| 萌版 | moez | 直接端点 | 原"萌版自适应" |
| AI | ai | JSON | 原"AI自适应" |
| 原神 | ysz | 直接端点 | 原"原神自适应" |
| 横图 | pc | JSON | 原"PC横图" |
| 萌版横图 | moe | JSON | |
| 风景横图 | fj | JSON | |
| 风景竖图 | fjmp | JSON | |
| 白底横图 | bd | JSON | |
| 原神横图 | ys | JSON | |
| ACG动图 | acg | 直接端点(视频) | |
| 竖图 | mp | JSON | 原"移动竖图" |
| 萌版竖图 | moemp | JSON | |
| 原神竖图 | ysmp | JSON | |
| AI竖图 | aimp | JSON | |
| 头像方图 | tx | JSON | |
| 七濑胡桃 | lai | JSON | |
| 小狐狸 | xhl | JSON | |

未收录：`se/semp`（14+，接口 404）、`pixiv`（外部站 pivix.mwm.moe）。

## 合并转发集成

超过 3 张时调用 `nonebot-plugin-merge-forward` 的
`build_nodes` + `send_group_forward_msg`，每个节点一张图，
昵称显示为 `次元图·<分类>`。私聊场景 OneBot V11 不支持合并转发，
自动退化为逐张发送。

## 开发

```bash
uv sync --extra dev
uv run ruff check src/
uv run pyright src/
uv run pytest tests/ -q
```
