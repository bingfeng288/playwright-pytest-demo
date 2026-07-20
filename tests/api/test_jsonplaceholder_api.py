# -*- coding: utf-8 -*-
"""
JSONPlaceholder 公开 REST API 测试套件。

覆盖点：
- CRUD 全流程（GET / POST / PUT / PATCH / DELETE）
- HTTP 状态码断言（200 / 201 / 404）
- 响应体 JSON schema / 字段类型校验
- 查询参数过滤
- 参数化数据驱动
- 响应耗时（性能基线）断言

靶场说明：JSONPlaceholder 为只读模拟 API，写操作（POST/PUT/DELETE）会返回
成功状态码与回显数据，但不会真正持久化——这对演示测试框架的断言能力已足够，
且无需任何鉴权，开箱即跑。
"""
import pytest

from config.settings import settings


# ---------------- GET：读取与查询 ----------------
@pytest.mark.api
@pytest.mark.smoke
def test_get_single_post(api_client):
    """获取单篇 post，校验状态码与字段结构。"""
    resp = api_client.get("/posts/1")
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}"
    data = resp.json()
    # 字段完整性
    for field in ("userId", "id", "title", "body"):
        assert field in data, f"响应缺少字段 {field}"
    # 类型与值校验
    assert data["id"] == 1
    assert isinstance(data["title"], str) and len(data["title"]) > 0
    # 性能基线：单次请求耗时不超过配置的 SLA（默认 8s，公网靶场留冗余）
    assert resp.elapsed.total_seconds() < settings.API_SLA_SECONDS, \
        f"接口响应超过 SLA {settings.API_SLA_SECONDS}s"


@pytest.mark.api
def test_get_nonexistent_post_returns_404(api_client):
    """访问不存在资源应返回 404。"""
    resp = api_client.get("/posts/9999")
    assert resp.status_code == 404


@pytest.mark.api
def test_get_posts_filter_by_userid(api_client):
    """按 userId 过滤，校验返回集合均属于该用户。"""
    resp = api_client.get("/posts", params={"userId": 1})
    assert resp.status_code == 200
    posts = resp.json()
    assert isinstance(posts, list) and len(posts) == 10, "user1 应有 10 篇 post"
    assert all(p["userId"] == 1 for p in posts), "存在不属于 user1 的 post"


@pytest.mark.api
def test_get_user_schema(api_client):
    """校验 user 资源的嵌套结构（address/company）。"""
    resp = api_client.get("/users/1")
    assert resp.status_code == 200
    u = resp.json()
    assert "@" in u["email"], "email 格式异常"
    assert "city" in u["address"], "缺少嵌套 address.city"
    assert "name" in u["company"], "缺少嵌套 company.name"


# ---------------- POST：创建 ----------------
@pytest.mark.api
@pytest.mark.smoke
def test_create_post(api_client):
    """创建 post，应返回 201 且回显提交数据 + 自增 id。"""
    payload = {"title": "SDET Demo", "body": "playwright+pytest", "userId": 99}
    resp = api_client.post("/posts", json=payload)
    assert resp.status_code == 201, f"期望 201，实际 {resp.status_code}"
    data = resp.json()
    assert data["title"] == payload["title"]
    assert data["userId"] == payload["userId"]
    assert "id" in data, "创建后应返回资源 id"


# ---------------- PUT / PATCH：更新 ----------------
@pytest.mark.api
def test_update_post_put(api_client):
    """整体更新（PUT）应返回 200 且字段被替换。"""
    payload = {"id": 1, "title": "updated", "body": "new-body", "userId": 1}
    resp = api_client.put("/posts/1", json=payload)
    assert resp.status_code == 200
    assert resp.json()["title"] == "updated"


@pytest.mark.api
def test_update_post_patch(api_client):
    """局部更新（PATCH）只改单字段。"""
    resp = api_client.patch("/posts/1", json={"title": "patched"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "patched"


# ---------------- DELETE：删除 ----------------
@pytest.mark.api
def test_delete_post(api_client):
    """删除资源应返回 200。"""
    resp = api_client.delete("/posts/1")
    assert resp.status_code == 200


# ---------------- 参数化数据驱动 ----------------
@pytest.mark.api
@pytest.mark.parametrize("post_id,expected_userid", [
    (1, 1),
    (11, 2),
    (21, 3),
    (31, 4),
])
def test_post_belongs_to_expected_user(api_client, post_id, expected_userid):
    """数据驱动：多组 post_id -> 预期 userId 映射校验。"""
    resp = api_client.get(f"/posts/{post_id}")
    assert resp.status_code == 200
    assert resp.json()["userId"] == expected_userid


@pytest.mark.api
@pytest.mark.parametrize("resource,expected_count", [
    ("/posts", 100),
    ("/comments", 500),
    ("/albums", 100),
    ("/users", 10),
])
def test_collection_size(api_client, resource, expected_count):
    """数据驱动：核心资源集合规模校验。"""
    resp = api_client.get(resource)
    assert resp.status_code == 200
    assert len(resp.json()) == expected_count
