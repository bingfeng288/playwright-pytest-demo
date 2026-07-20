# -*- coding: utf-8 -*-
"""
全局 pytest fixtures 与钩子。

设计要点：
1. browser/context/page 分层 fixture，保证用例间隔离（每条用例独立 context）。
2. 失败时自动截图 + 记录，附到 HTML 报告，便于定位。
3. api_client 会话级复用，减少连接开销。
"""
import os
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
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    用例失败时，若上下文中存在 page，则自动截图并附加到 HTML 报告。
    """
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page", None)
        if page is not None:
            os.makedirs(settings.SCREENSHOT_DIR, exist_ok=True)
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = item.name.replace("/", "_").replace("[", "_").replace("]", "_")
            path = os.path.join(settings.SCREENSHOT_DIR, f"{safe_name}_{ts}.png")
            try:
                page.screenshot(path=path, full_page=True)
                print(f"\n[失败截图] {path}")
            except Exception as e:  # noqa
                print(f"\n[截图失败] {e}")
