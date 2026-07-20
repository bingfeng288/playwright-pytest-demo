# -*- coding: utf-8 -*-
"""
数据驱动测试：从 data/todo_cases.json 读取用例，用 pytest.mark.parametrize 参数化。

演示"一套脚本 + 多组数据"的可维护测试设计，覆盖中英文、特殊字符、边界。
"""
import json
import pathlib
import pytest
from pages.todo_page import TodoPage

# 读取外部数据文件（相对项目根）
DATA_FILE = pathlib.Path(__file__).parents[2] / "data" / "todo_cases.json"
CASES = json.loads(DATA_FILE.read_text(encoding="utf-8"))


@pytest.mark.ui
@pytest.mark.data_driven
@pytest.mark.parametrize("case", CASES, ids=[c["case_id"] for c in CASES])
def test_add_todos_data_driven(page, case):
    """按数据集新增待办，校验数量与剩余计数文案。"""
    todo = TodoPage(page).open()
    todo.add_many(case["todos"])
    todo.expect_item_count(len(case["todos"]))
    assert todo.remaining_text() == case["expected_remaining"], (
        f"{case['case_id']} ({case['desc']}) 剩余计数不符"
    )
