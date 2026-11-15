# -*- coding: utf-8 -*-
"""
全局 pytest fixtures 与钩子。

设计要点：
1. browser/context/page 分层 fixture，保证用例间隔离（每条用例独立 context）。
2. 失败时自动截图 + 记录，附到 HTML 报告，便于定位。
3. api_client 会话级复用，减少连接开销。
"""
import os
import base64
import datetime
import pytest
from playwright.sync_api import sync_playwright

from config.settings import settings
from utils.api_client import ApiClient


# ---------------- 浏览器层 fixtures ----------------
@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance):
    browser = playwright_instance.chromium.launch(
        headless=settings.HEADLESS,
        slow_mo=settings.SLOW_MO,
    )
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser):
    """每条用例独立浏览器上下文，实现 cookie/storage 隔离。"""
    context = browser.new_context(viewport=settings.VIEWPORT)
    context.set_default_timeout(settings.DEFAULT_TIMEOUT)
    # 显式设置导航超时，避免 page.goto 沿用元素等待的 10s 而误判超时
    context.set_default_navigation_timeout(settings.NAVIGATION_TIMEOUT)
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context):
    page = context.new_page()
    yield page
    page.close()


# ---------------- API 层 fixture ----------------
@pytest.fixture(scope="session")
def api_client():
    client = ApiClient(base_url=settings.API_BASE_URL, api_key=settings.API_KEY)
    yield client
    client.close()


# ---------------- 失败自动截图钩子 ----------------
def _attach_screenshot(report, path: str, self_contained: bool) -> None:
    """把截图附加到 HTML 报告。

    pytest-html 的 self-contained 转换并不会去读本地文件：它把 extras 的 content
    直接当作 base64 字符串解码，非 base64 时只打一条 "external resource" 警告、图片
    仍然保持外链。所以该模式下必须自己先读文件转 base64；非自包含模式才传路径。
    """
    try:
        from pytest_html import extras
    except ImportError:  # 未安装 pytest-html 时静默跳过，不影响测试结果
        return

    if self_contained:
        with open(path, "rb") as f:
            content = base64.b64encode(f.read()).decode("ascii")
    else:
        content = path

    if not hasattr(report, "extras"):
        report.extras = []
    report.extras.append(extras.image(content, name="失败截图", mime_type="image/png"))


def _is_self_contained(config) -> bool:
    try:
        return bool(config.getoption("self_contained_html"))
    except (ValueError, AttributeError):
        return False


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    用例失败时自动留痕：
    1. 截图落盘到 reports/screenshots/，便于单独查看与归档；
    2. 通过 report.extras 内嵌进 pytest-html 报告，不用另开目录翻文件。

    同时覆盖 setup 阶段：fixture 内部（如页面导航）失败也留痕，
    这类失败原先只在 call 阶段才截图，会漏掉。
    """
    outcome = yield
    report = outcome.get_result()
    if report.when not in ("setup", "call") or not report.failed:
        return

    page = item.funcargs.get("page", None)
    if page is None:
        return

    os.makedirs(settings.SCREENSHOT_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = item.name.replace("/", "_").replace("[", "_").replace("]", "_")
    path = os.path.join(settings.SCREENSHOT_DIR, f"{safe_name}_{ts}.png")
    try:
        page.screenshot(path=path, full_page=True)
        print(f"\n[失败截图] {path}")
        _attach_screenshot(report, path, _is_self_contained(item.config))
    except Exception as e:  # noqa
        print(f"\n[截图失败] {e}")
