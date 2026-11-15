# -*- coding: utf-8 -*-
"""全局配置：支持通过环境变量覆盖，方便多环境（dev/test/prod）与 CI 切换。"""
import os


class Settings:
    # ---------- 被测系统地址 ----------
    # UI 靶场：Playwright 官方 TodoMVC 演示站（公开、稳定、无需登录）
    UI_BASE_URL: str = os.getenv("UI_BASE_URL", "https://demo.playwright.dev/todomvc")
    # API 靶场：JSONPlaceholder 公开 REST API（免费、无需鉴权、支持增删改查）
    API_BASE_URL: str = os.getenv("API_BASE_URL", "https://jsonplaceholder.typicode.com")
    # JSONPlaceholder 无需 API key；保留字段以便切换到需鉴权的环境
    API_KEY: str = os.getenv("API_KEY", "")
    # API 单请求响应耗时基线（秒），公网靶场留足冗余，可用环境变量收紧
    API_SLA_SECONDS: float = float(os.getenv("API_SLA_SECONDS", "8"))

    # ---------- 浏览器行为 ----------
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"
    SLOW_MO: int = int(os.getenv("SLOW_MO", "0"))          # 毫秒，调试时可调大
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "10000"))  # 元素等待超时
    # 导航超时与元素等待超时分开配置。
    # Playwright 在未显式设置 navigation timeout 时，page.goto 会沿用 default_timeout；
    # 10s 在并行执行 + 公网靶站场景下不足以完成首次导航，会造成 goto 超时误判。
    NAVIGATION_TIMEOUT: int = int(os.getenv("NAVIGATION_TIMEOUT", "30000"))
    VIEWPORT = {"width": 1280, "height": 800}

    # ---------- 失败留痕 ----------
    SCREENSHOT_DIR: str = os.getenv("SCREENSHOT_DIR", "reports/screenshots")


settings = Settings()
