# -*- coding: utf-8 -*-
"""TodoPage：TodoMVC 页面对象，封装元素定位与业务动作，测试用例只调业务方法。"""
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from config.settings import settings


class TodoPage(BasePage):
    # ---------- 元素定位（集中管理，UI 变更只需改这里）----------
    NEW_TODO = ".new-todo"                      # 新建输入框
    TODO_ITEMS = ".todo-list li"                # 待办条目
    TODO_LABEL = ".todo-list li label"          # 条目文本
    TOGGLE = ".todo-list li .toggle"            # 单条完成勾选
    TOGGLE_ALL = ".toggle-all"                  # 全部完成
    DELETE_BTN = ".todo-list li .destroy"       # 删除按钮
    TODO_COUNT = ".todo-count"                  # 剩余计数
    CLEAR_COMPLETED = ".clear-completed"        # 清除已完成
    # 用页脚 .filters 容器内的链接精确定位，避免与待办文本（如 "active task"）冲突
    FILTER_ALL = ".filters a[href='#/']"
    FILTER_ACTIVE = ".filters a[href='#/active']"
    FILTER_COMPLETED = ".filters a[href='#/completed']"
    EDIT_INPUT = ".todo-list li.editing .edit"  # 编辑态输入框

    def __init__(self, page: Page):
        super().__init__(page)

    # ---------- 业务动作 ----------
    def open(self):
        self.navigate(settings.UI_BASE_URL)
        # TodoMVC 首屏渲染输入框即视为加载完成
        self.expect_visible(self.NEW_TODO)
        return self

    def add(self, text: str):
        """新增一条待办。"""
        self.type_and_enter(self.NEW_TODO, text)
        return self

    def add_many(self, texts):
        for t in texts:
            self.add(t)
        return self

    def items(self):
        return self.page.locator(self.TODO_ITEMS)

    def item_count(self) -> int:
        return self.items().count()

    def toggle_at(self, index: int):
        """勾选/取消第 index 条（0 起）为完成。"""
        self.page.locator(self.TOGGLE).nth(index).click()
        return self

    def delete_at(self, index: int):
        """删除第 index 条。悬停才显示删除按钮，故先 hover。"""
        self.items().nth(index).hover()
        self.page.locator(self.DELETE_BTN).nth(index).click()
        return self

    def edit_at(self, index: int, new_text: str):
        """双击进入编辑态，改写文本后回车。"""
        self.items().nth(index).locator("label").dblclick()
        edit_box = self.page.locator(self.EDIT_INPUT)
        edit_box.fill(new_text)
        edit_box.press("Enter")
        return self

    def remaining_text(self) -> str:
        """如 '2 items left'。"""
        return self.text_of(self.TODO_COUNT)

    def filter_active(self):
        self.click(self.FILTER_ACTIVE)
        return self

    def filter_completed(self):
        self.click(self.FILTER_COMPLETED)
        return self

    def filter_all(self):
        self.click(self.FILTER_ALL)
        return self

    def clear_completed(self):
        self.click(self.CLEAR_COMPLETED)
        return self

    # ---------- 断言 ----------
    def expect_item_count(self, n: int):
        expect(self.items()).to_have_count(n)

    def expect_completed_at(self, index: int):
        expect(self.items().nth(index)).to_have_class("completed")

    def expect_all_texts(self, texts):
        expect(self.page.locator(self.TODO_LABEL)).to_have_text(texts)
