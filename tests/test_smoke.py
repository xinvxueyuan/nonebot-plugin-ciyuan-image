"""次元图插件冒烟测试：分类解析 + 实际 API 拉取 + 合并转发集成。"""

import asyncio
import json

import httpx
import nonebot
import pytest

nonebot.init()

from nonebot_plugin_ciyuan_image.api import (  # nonebot.init 后才可导入插件包
    CATEGORIES,
    MAX_COUNT,
    Category,
    category_list_text,
    fetch_images,
    resolve_category,
)

# ---- 分类解析 ----


def test_resolve_title() -> None:
    cat = resolve_category("二次元")
    assert cat == Category(title="二次元", slug="ycy", kind="direct")
    assert resolve_category("萌版横图") == Category(
        title="萌版横图", slug="moe", kind="json"
    )


def test_resolve_slug() -> None:
    assert resolve_category("ycy") == Category(
        title="二次元", slug="ycy", kind="direct"
    )
    assert resolve_category("ys") == Category(title="原神横图", slug="ys", kind="json")


def test_resolve_unknown() -> None:
    assert resolve_category("不存在的分类") is None
    assert resolve_category("") is None


def test_category_list() -> None:
    text = category_list_text()
    assert "二次元" in text
    assert "原神" in text
    assert "ycy" in text


def test_resolve_new_miku_categories() -> None:
    """初音系列（上游 2026-10 在册）。"""
    assert resolve_category("初音横图") == Category(
        title="初音横图", slug="miku", kind="json"
    )
    assert resolve_category("mikump") == Category(
        title="初音竖图", slug="mikump", kind="json"
    )
    assert resolve_category("mikuz") == Category(
        title="初音自适应", slug="mikuz", kind="direct"
    )


def test_dead_categories_are_removed() -> None:
    """已下架分类（ai / fjmp / aimp）不在表里 → 用户会得到「未知分类 + 可用列表」。"""
    for word in ("AI", "ai", "风景竖图", "fjmp", "AI竖图", "aimp"):
        assert resolve_category(word) is None


@pytest.mark.asyncio
async def test_json_endpoint_non_json_gives_readable_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """上游对下架分类返回 HTML 占位页时，要报「接口返回的不是 JSON」。"""
    from nonebot_plugin_ciyuan_image import api

    class HtmlClient:
        """模拟 AsyncClient：永远返回 HTML 占位页。"""

        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        async def __aenter__(self) -> "HtmlClient":
            return self

        async def __aexit__(self, *args: object) -> None:
            pass

        async def get(self, _url: str, **_kw: object) -> object:
            class Resp:
                text = "<!doctype html><title>你好世界</title>"

                def raise_for_status(self) -> None:
                    return None

                def json(self) -> object:
                    msg = "Expecting value"
                    raise json.JSONDecodeError(msg, self.text, 0)

            return Resp()

    monkeypatch.setattr(api.httpx, "AsyncClient", HtmlClient)
    with pytest.raises(ValueError) as ei:
        await api._fetch_json("pc", 1)
    assert "不是 JSON" in str(ei.value)
    assert "pc" in str(ei.value)


# ---- 实际 API 拉取（需要网络）----


@pytest.mark.asyncio
async def test_fetch_json_multi() -> None:
    urls = await fetch_images(resolve_category("原神横图"), 4)  # type: ignore[arg-type]
    assert len(urls) == 4
    for u in urls:
        assert u.startswith("http")


@pytest.mark.asyncio
async def test_fetch_direct_endpoint() -> None:
    urls = await fetch_images(resolve_category("二次元"), 2)  # type: ignore[arg-type]
    assert len(urls) == 2
    assert urls[0].startswith("http")


@pytest.mark.asyncio
async def test_fetch_clamp_count() -> None:
    # 服务端按分类资源量截断（小狐狸只有 ~34 张），返回数 ≤ 请求数即可
    urls = await fetch_images(resolve_category("小狐狸"), MAX_COUNT + 10)  # type: ignore[arg-type]
    assert len(urls) >= 1
    assert len(urls) <= MAX_COUNT


@pytest.mark.asyncio
async def test_fetch_retry_on_transient_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """前两次失败（网络抖动）后重试应成功；第三次仍失败才抛错。"""
    from nonebot_plugin_ciyuan_image import api

    calls = {"n": 0}

    class FlakyClient:
        """模拟 AsyncClient：前两次调用抛 ConnectError，第三次抛 AssertionError。"""

        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        async def __aenter__(self) -> "FlakyClient":
            return self

        async def __aexit__(self, *args: object) -> None:
            pass

        async def get(self, _url: str) -> object:
            calls["n"] += 1
            if calls["n"] <= 2:
                raise httpx.ConnectError("jitter", request=None)  # type: ignore[arg-type]
            raise AssertionError("第三次应成功")

    original = api.httpx.AsyncClient
    monkeypatch.setattr(api.httpx, "AsyncClient", FlakyClient)
    try:
        with pytest.raises(AssertionError):
            await fetch_images(resolve_category("原神横图"), 2)  # type: ignore[arg-type]
    finally:
        monkeypatch.setattr(api.httpx, "AsyncClient", original)
    assert calls["n"] == 3, f"应重试 3 次，实际 {calls['n']}"


# ---- 分类列表渲染（nonebot-plugin-htmlkit，可选）----


def test_render_html_contains_categories() -> None:
    """渲染 HTML 应包含全部分类与 slug。"""
    from nonebot_plugin_ciyuan_image.render import _build_html

    html = _build_html()
    for title, info in CATEGORIES.items():
        assert title in html
        assert info["slug"] in html


@pytest.mark.asyncio
async def test_render_category_list_png() -> None:
    """Htmlkit 已安装时应渲染出 PNG。"""
    from nonebot_plugin_ciyuan_image.render import (
        HTMLKIT_AVAILABLE,
        render_category_list,
    )

    if not HTMLKIT_AVAILABLE:
        pytest.skip("nonebot-plugin-htmlkit 未安装")
    png = await render_category_list()
    assert png is not None
    assert png[:8] == b"\x89PNG\r\n\x1a\n"


# ---- 合并转发集成（nonebot-plugin-merge-forward）----


def test_merge_forward_nodes() -> None:
    """确认 >3 张时用的 build_nodes 产出的 node 结构正确。"""
    from nonebot.adapters.onebot.v11 import MessageSegment
    from nonebot_plugin_merge_forward import build_nodes

    urls = [f"https://tc.alcy.cc/tc/{i}.webp" for i in range(5)]
    nodes = build_nodes(
        [MessageSegment.image(u) for u in urls],
        uin="123456",
        name="次元图·原神横图",
    )
    assert len(nodes) == 5
    for node in nodes:
        assert node["type"] == "node"
        assert node["data"]["user_id"] == "123456"
        assert node["data"]["nickname"] == "次元图·原神横图"
        assert node["data"]["content"][0]["type"] == "image"
        assert node["data"]["content"][0]["data"]["file"].startswith("http")


async def _async_main() -> None:
    """手动运行：python -m tests.test_smoke 风格。"""
    for word in ["二次元", "原神", "ycy", "ys", "小狐狸"]:
        cat = resolve_category(word)
        urls = await fetch_images(cat, 2)  # type: ignore[arg-type]
        print(f"{word} -> {cat.title} ({cat.kind}): {urls}")  # noqa: T201


if __name__ == "__main__":
    asyncio.run(_async_main())
