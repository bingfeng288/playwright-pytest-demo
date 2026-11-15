# Playwright + pytest 自动化测试框架（UI + API）

> 一套可直接运行、面向生产的自动化测试演示项目。采用 **Page Object Model（POM）** 设计，覆盖 **UI 端到端测试**、**REST API 测试**、**数据驱动**、**失败自动截图**、**HTML 测试报告** 与 **GitHub Actions CI/CD**，开箱即跑，无需任何鉴权或本地服务。

[![CI](https://github.com/bingfeng288/playwright-pytest-demo/actions/workflows/ci.yml/badge.svg)](https://github.com/bingfeng288/playwright-pytest-demo/actions/workflows/ci.yml) ![tests](https://img.shields.io/badge/tests-28%20passed-brightgreen) ![python](https://img.shields.io/badge/python-3.13-blue) ![framework](https://img.shields.io/badge/playwright%2Bpytest-orange)

---

## ✨ 核心亮点

| 能力 | 实现方式 |
|---|---|
| **POM 分层架构** | `base_page` 封装通用操作，业务页面（`todo_page`）继承；用例只调业务方法，UI 变更只需改定位器 |
| **UI 自动化** | Playwright 驱动 Chromium，覆盖 TodoMVC 增删改查 / 过滤 / 编辑 / 持久化全流程 |
| **API 测试** | 基于 `requests.Session` 的 `ApiClient` 封装，覆盖 CRUD + 状态码 + JSON schema + 查询过滤 + 性能基线 |
| **数据驱动** | `@pytest.mark.parametrize` + 外部 JSON 用例（`data/todo_cases.json`）驱动 |
| **fixture 分层隔离** | `browser`(session) → `context`(function) → `page`，每条用例独立上下文，杜绝状态污染 |
| **失败自动留痕** | `pytest_runtest_makereport` 钩子：用例失败自动全页截图并附加到报告 |
| **可视化报告** | `pytest-html` 生成自包含 HTML 报告（含通过率、耗时、失败截图） |
| **CI/CD** | GitHub Actions：push/PR 自动装浏览器、跑全量测试、上传报告 artifact |
| **多环境配置** | `config/settings.py` 全部支持环境变量覆盖（`UI_BASE_URL` / `API_BASE_URL` / `HEADLESS` / `DEFAULT_TIMEOUT` / `NAVIGATION_TIMEOUT` / `API_SLA_SECONDS`） |
| **用例分级** | `smoke` / `ui` / `api` marker，支持 `-m smoke` 快速冒烟 |

---

## 📁 项目结构

```
playwright_pytest_demo/
├── config/
│   └── settings.py              # 全局配置（环境变量可覆盖）
├── pages/                       # Page Object 层
│   ├── base_page.py             # 通用操作封装（点击/输入/等待/断言）
│   └── todo_page.py             # TodoMVC 页面对象
├── utils/
│   └── api_client.py            # requests.Session API 封装
├── data/
│   └── todo_cases.json          # 数据驱动用例数据
├── tests/
│   ├── ui/
│   │   ├── test_todo_ui.py            # UI 端到端（基础+高级，共 8 类场景）
│   │   └── test_todo_data_driven.py   # 数据驱动 UI 测试
│   └── api/
│       └── test_jsonplaceholder_api.py # API 测试（CRUD/状态码/schema/参数化）
├── conftest.py                  # 全局 fixtures + 失败截图钩子
├── pytest.ini                   # pytest 配置与 marker 注册
├── requirements.txt
├── .github/workflows/ci.yml     # GitHub Actions CI
└── reports/                     # 测试报告与失败截图（自动生成）
```

---

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 安装 Playwright 浏览器
playwright install chromium

# 3. 运行全部测试并生成 HTML 报告
pytest --html=reports/report.html --self-contained-html

# 4. 打开报告
open reports/report.html      # macOS
```

### 常用命令

```bash
pytest -m smoke               # 只跑冒烟用例（快速验证）
pytest -m ui                  # 只跑 UI 测试
pytest -m api                 # 只跑 API 测试
pytest -v                     # 详细输出
HEADLESS=false SLOW_MO=500 pytest -m ui   # 有头模式慢放调试

# 并行执行（需 pytest-xdist）。注意：并行会同时拉起多个浏览器打公网靶场，
# 在弱网或多级代理环境下易出现连接抖动（ERR_CONNECTION_CLOSED / 502），
# 表现为 setup 阶段报错而非断言失败。建议从 -n 4 起步：
pytest -n 4
# 网络确实较慢时，配合放大导航超时（默认 30s）：
NAVIGATION_TIMEOUT=60000 pytest -n auto
```

---

## 🧱 被测对象（靶场）

| 类型 | 目标 | 说明 |
|---|---|---|
| UI | [Playwright 官方 TodoMVC](https://demo.playwright.dev/todomvc) | 公开、稳定、无需登录 |
| API | [JSONPlaceholder](https://jsonplaceholder.typicode.com) | 免费公开 REST API，无需鉴权，支持 CRUD 语义 |

> 均为公网稳定靶场，任何机器 clone 后即可运行，无需自建后端。切换到公司真实环境只需改 `config/settings.py` 或设置环境变量。

---

## 📊 测试覆盖概览

- **UI（16 条）**：单条/批量新增、完成勾选、编辑、删除、过滤（Active/Completed）、清除已完成、刷新持久化、数据驱动新增
- **API（12 条）**：单资源读取、404、按 userId 过滤、嵌套 schema 校验、POST 创建、PUT/PATCH 更新、DELETE 删除、参数化映射校验、集合规模校验、响应耗时 SLA

当前执行结果：**28 passed**。

---

## 🔧 技术栈

`Python 3.13` · `pytest` · `playwright` · `pytest-html` · `requests` · `GitHub Actions`
