"""验证 require 跨插件访问：依赖方 require 能拿到 merge_forward 的函数。

注意：本测试不 load_plugin ciyuan_image —— test_smoke.py 的模块级 import
已将其加载为插件（pytest 按文件名序收集，test_smoke 先执行）。
"""

import nonebot
from nonebot import require

nonebot.init()


def test_require_merge_forward() -> None:
    """require('nonebot_plugin_merge_forward') 应返回模块且函数可调用。"""
    mf = require("nonebot_plugin_merge_forward")
    assert callable(mf.build_nodes)
    assert callable(mf.send_group_forward_msg)
