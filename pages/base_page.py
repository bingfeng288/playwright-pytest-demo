# -*- coding: utf-8 -*-
"""BasePage：所有页面对象的基类，封装通用交互，屏蔽底层 Playwright API 细节。"""
from playwright.sync_api import Page, expect


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    # ---------- 导航 ----------
    def navigate(self, url: str):
        self.page.goto(url, wait_until="domcontentloaded")

    def reload(self):
        self.page.reload()

    @property
    def title(self) -> str:
        return self.page.title()

    # ---------- 通用操作封装 ----------
    def click(self, selector: str):
        self.page.locator(selector).click()

    def fill(self, selector: str, text: str):
        self.page.locator(selector).fill(text)

    def type_and_enter(self, selector: str, text: str):
        loc = self.page.locator(selector)
        loc.fill(text)
        loc.press("Enter")

    def text_of(self, selector: str) -> str:
        return self.page.locator(selector).inner_text()

    def count(self, selector: str) -> int:
        return self.page.locator(selector).count()

    def is_visible(self, selector: str) -> bool:
        return self.page.locator(selector).is_visible()

    # ---------- 断言封装（基于 Playwright 自动等待的 expect）----------
    def expect_visible(self, selector: str):
        expect(self.page.locator(selector)).to_be_visible()

    def expect_count(self, selector: str, n: int):
        expect(self.page.locator(selector)).to_have_count(n)

    def expect_text(self, selector: str, text: str):
        expect(self.page.locator(selector)).to_have_text(text)
