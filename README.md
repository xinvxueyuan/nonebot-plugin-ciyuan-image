# nonebot-plugin-ciyuan-image

次元图：给 QQ 群用的栗次元（[t.alcy.cc](https://t.alcy.cc)）随机图片插件，18 个分类、单次最多 50 张，超过 3 张自动合并转发。

> **qbot 插件** · 宿主仓库：[xinvxueyuan/qbot](https://github.com/xinvxueyuan/qbot)

> - 子命令就是分类标题（已去掉「自适应」后缀与技术名），也支持直接写 slug（如 `ysmp`）。
> - 1–3 张逐张直接发图；4 张及以上发合并转发（一个卡片，每条一张图）；私聊不支持合并转发，自动退化为逐张发送。
> - 分类列表可选渲染成图片：装了 `nonebot-plugin-htmlkit` 渲染成 PNG，未装回退纯文本。

## 功能特性

- 数据源栗次元 `t.alcy.cc`，共 **18 个分类**：二次元 / 萌版 / 原神 / 横图 / 萌版横图 / 风景横图 / 白底横图 / 原神横图 / ACG动图 / 竖图 / 萌版竖图 / 原神竖图 / 头像方图 / 七濑胡桃 / 小狐狸 / 初音横图 / 初音竖图 / 初音自适应（与下方分类表一致）。
- 分类可用中文标题（`二次元`）或 slug（`ycy`）输入，两种索引互通。
- 单次 1–50 张（省略默认 1）；超过 3 张自动合并转发。
- 接口两种形态：JSON 分类一次请求取 N 张（`GET /json?<slug>=<N>`）；直接端点循环请求（`GET /<slug>` 302 到随机图）。`acg` 是视频端点，按直接端点处理。
- 网络抖动自动重试 3 次（间隔 1s 起指数退避）。
- 不带参数发「次元图」→ 输出全部分类列表（htmlkit 渲染成图片，未装则纯文本）。
- 参数容错：分类与张数之间支持空格 / 逗号 / 顿号分隔；参数过多、分类不存在、张数非数字、张数越界都会给出明确提示。

## 安装

### 依赖

- 运行依赖（以 `pyproject.toml` 为准）：`nonebot2>=2.5.0`、`nonebot-adapter-onebot>=2.4.6`、`httpx>=0.27.0`、`nonebot-plugin-merge-forward>=0.1.0`（合并转发工具库）
- Python：`>=3.10`
- 可选依赖（extra `htmlkit`）：`nonebot-plugin-htmlkit>=0.1.0rc5` —— 分类列表渲染成图片，未装则回退纯文本

### pip 安装

```bash
pip install nonebot-plugin-ciyuan-image
pip install nonebot-plugin-merge-forward            # 运行依赖：合并转发工具库
pip install 'nonebot-plugin-ciyuan-image[htmlkit]'  # 可选：分类列表渲染成图片
```

### 宿主以 git 子模块引入

```bash
git submodule add -b main https://github.com/xinvxueyuan/nonebot-plugin-ciyuan-image.git \
  vendor/nonebot-plugin-ciyuan-image
git -C vendor/nonebot-plugin-ciyuan-image checkout <钉定的 SHA>
```

宿主 `pyproject.toml` 的 `[tool.nonebot]` 加一行：

```toml
plugin_dirs = ["vendor/nonebot-plugin-ciyuan-image/src/plugins"]
```

> ⚠️ Linux 部署 htmlkit 需要中文字体（如 `apt install fonts-noto-cjk`），
> 否则分类图里的中文会渲染成方块；Windows 下自动回退系统字体。

## 配置

本插件**不读取任何配置项**：源码中没有 `get_plugin_config` / `Config` 模型，也没有 `.env` 键或环境变量前缀，安装后即可用。下面这些值都是 `src/plugins/nonebot_plugin_ciyuan_image/` 里的**代码常量**，要改只能改源码后重新部署：

| 常量 | 值 | 位置 | 作用 |
| --- | --- | --- | --- |
| `BASE_URL` | `https://t.alcy.cc` | `api.py` | 栗次元接口根地址 |
| `MAX_COUNT` | `50` | `api.py` | 单次请求张数上限（超过则提示「张数最多 50」） |
| `RETRY_TIMES` | `3` | `api.py` | 单次拉取最多尝试次数 |
| `RETRY_BASE_DELAY` | `1.0` | `api.py` | 重试基础间隔（秒），按 `2**attempt` 指数退避 |
| `TIMEOUT` | `httpx.Timeout(20.0)` | `api.py` | 单次 HTTP 请求超时 |
| `DIRECT_SEND_LIMIT` | `3` | `__init__.py` | 直接发图上限（含）；超过改走合并转发 |

可选的「配置」只有安装层面的一项：是否安装 extra `htmlkit`（决定分类列表是 PNG 还是纯文本）。

## 使用 / 命令

| 命令 | 别名 | 说明 |
|---|---|---|
| `次元图` | `次元图`（与命令同名） | 列出全部分类（htmlkit 渲染成图片，未装则纯文本） |
| `次元图 <分类>` | — | 随机 1 张 |
| `次元图 <分类> <张数>` | — | 随机 <张数> 张（1–50，省略默认 1） |
| `次元图 <slug> <张数>` | — | 分类直接写 slug，如 `次元图 ysmp 10` |

示例：

```
次元图                    查看全部分类（htmlkit 渲染成图片，未装则纯文本）
次元图 二次元             随机 1 张
次元图 原神 5             随机 5 张
次元图 ysmp 10            也可直接用 slug
```

规则：**1–3 张直接发图；4 张及以上用合并转发**（一个转发卡片，每条一张图）。

### 分类表（2026-10-14 实测）

| 子命令 | slug | 接口 | 说明 |
| --- | --- | --- | --- |
| 二次元 | ycy | 直接端点 | 原"二次元自适应" |
| 萌版 | moez | 直接端点 | 原"萌版自适应" |
| 原神 | ysz | 直接端点 | 原"原神自适应" |
| 横图 | pc | JSON | 原"PC横图" |
| 萌版横图 | moe | JSON | |
| 风景横图 | fj | JSON | |
| 白底横图 | bd | JSON | |
| 原神横图 | ys | JSON | |
| ACG动图 | acg | 直接端点(视频) | |
| 竖图 | mp | JSON | 原"移动竖图" |
| 萌版竖图 | moemp | JSON | |
| 原神竖图 | ysmp | JSON | |
| 头像方图 | tx | JSON | |
| 七濑胡桃 | lai | JSON | |
| 小狐狸 | xhl | JSON | |
| 初音横图 | miku | JSON | 2026-10 新上架 |
| 初音竖图 | mikump | JSON | 2026-10 新上架 |
| 初音自适应 | mikuz | 直接端点 | 2026-10 新上架 |

**已下架**（上游 JSON 与直出双 404，本插件表里已剔除）：`ai`（AI）、`fjmp`（风景竖图）、
`aimp`（AI竖图）—— 发这些词会得到「未知分类 + 可用列表」的正常提示，不再报接口异常。
上游对下架分类返回 **HTML 提示页**（不是 JSON 也不是 404），插件会把它转成
「接口返回的不是 JSON（分类 X 可能已下架）」的可读错误。

未收录：`se/semp`（14+，接口 404）、`pixiv`（外部站 piviv.mwm.moe）。

### 合并转发集成

超过 3 张时调用 `nonebot-plugin-merge-forward` 的
`build_nodes` + `send_group_forward_msg`，每个节点一张图，
昵称显示为 `次元图·<分类>`。私聊场景 OneBot V11 不支持合并转发，
自动退化为逐张发送。

## 开发与测试

### 环境准备

```bash
uv sync --extra dev
```

`uv sync --extra dev` 装齐开发依赖（pytest / ruff / pyright / htmlkit / fastapi）；
`pyproject.toml` 的 `[dependency-groups]` 另带 `pytest-asyncio`。

开发时依赖本地 merge-forward：`pyproject.toml` 的 `[tool.uv.sources]` 已把
`nonebot-plugin-merge-forward` 指向 `C:/dev/nonebot-plugin-merge-forward`；
在该目录先 `uv pip install -e .`，或改用
`uv add nonebot-plugin-merge-forward --path ../nonebot-plugin-merge-forward`。

### 测试与门禁

```bash
uv run python -m pytest tests/ -q
uv run ruff check . && uv run ruff format --check .
uv run pyright
```

`tests/` 里既有纯单测（分类解析、slug 解析、重试逻辑、合并转发 node 结构），
也有**需要真实网络**的用例（实际从 t.alcy.cc 拉图）；htmlkit 未装时渲染用例自动 skip。

- `tests/test_smoke.py`：必须先 `nonebot.init()` 再 import 插件包（`api` 模块的用例还断言了 `require` 拿到的 merge-forward 函数可用）。
- `tests/test_require.py`：验证 `require("nonebot_plugin_merge_forward")` 的跨插件访问能取到 `build_nodes` / `send_group_forward_msg`，本身不 `load_plugin` 次元图插件。
- 工具配置：ruff `line-length = 88`、`target-version = "py310"`；pyright `typeCheckingMode = "strict"`、`include = ["src"]`；构建后端 `uv_build`。

## 许可证与相关仓库

- **许可证**：`MIT`（见仓库根目录 `LICENSE` 文件，Copyright (c) 2026 新v学员 (xinvxueyuan)；`pyproject.toml` 的 `license = { text = "MIT" }`）。
- **相关仓库**：
  - [xinvxueyuan/qbot](https://github.com/xinvxueyuan/qbot) —— 宿主，以 `vendor/` 子模块引入本插件。
  - [xinvxueyuan/nonebot-plugin-merge-forward](https://github.com/xinvxueyuan/nonebot-plugin-merge-forward) —— 本插件的运行依赖，提供 `build_nodes` / `send_group_forward_msg`。
