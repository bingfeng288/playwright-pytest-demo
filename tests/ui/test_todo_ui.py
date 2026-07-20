# -*- coding: utf-8 -*-
"""
TodoMVC UI 自动化测试（Page Object Model）。

覆盖：新增、完成、编辑、删除、过滤、清除已完成、持久化（刷新）等核心流程。
标记：@pytest.mark.ui / smoke / regression
"""
import pytest
from pages.todo_page import TodoPage


@pytest.fixture
def todo(page):
    """返回已打开 TodoMVC 的页面对象。"""
    return TodoPage(page).open()


@pytest.mark.ui
@pytest.mark.smoke
class TestTodoBasic:
    def test_add_single_todo(self, todo):
        """新增一条待办，列表出现该条且计数为 1。"""
        todo.add("Write automation tests")
        todo.expect_item_count(1)
        assert todo.remaining_text() == "1 item left"

    def test_add_multiple_todos(self, todo):
        """批量新增，顺序与数量正确。"""
        items = ["task A", "task B", "task C"]
        todo.add_many(items)
        todo.expect_item_count(3)
        todo.expect_all_texts(items)

    def test_complete_todo(self, todo):
        """勾选完成后该条带 completed class，剩余计数减少。"""
        todo.add_many(["task A", "task B"])
        todo.toggle_at(0)
        todo.expect_completed_at(0)
        assert todo.remaining_text() == "1 item left"


@pytest.mark.ui
@pytest.mark.regression
class TestTodoAdvanced:
    def test_edit_todo(self, todo):
        """双击编辑改写文本。"""
        todo.add("old title")
        todo.edit_at(0, "new title")
        todo.expect_all_texts(["new title"])

    def test_delete_todo(self, todo):
        """删除一条后数量减少。"""
        todo.add_many(["keep me", "delete me"])
        todo.delete_at(1)
        todo.expect_item_count(1)
        todo.expect_all_texts(["keep me"])

    def test_filter_active_and_completed(self, todo):
        """过滤器：Active 只显示未完成，Completed 只显示已完成。"""
        todo.add_many(["active task", "done task"])
        todo.toggle_at(1)               # 完成第二条

        todo.filter_active()
        todo.expect_item_count(1)
        todo.expect_all_texts(["active task"])

        todo.filter_completed()
        todo.expect_item_count(1)
        todo.expect_all_texts(["done task"])

        todo.filter_all()
        todo.expect_item_count(2)

    def test_clear_completed(self, todo):
        """清除已完成后仅保留未完成。"""
        todo.add_many(["a", "b", "c"])
        todo.toggle_at(0)
        todo.toggle_at(2)
        todo.clear_completed()
        todo.expect_item_count(1)
        todo.expect_all_texts(["b"])

    def test_persistence_after_reload(self, todo):
        """TodoMVC 使用 localStorage，刷新后数据应保留。"""
        todo.add_many(["persist 1", "persist 2"])
        todo.reload()
        todo.expect_item_count(2)
