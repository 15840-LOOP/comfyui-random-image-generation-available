"""阶段一:风格预设收藏夹母子两级分类的核心逻辑测试。

覆盖旧版单级数据平滑迁移、母子层级创建规则、级联删除与解绑、
聚合计数与智能查询等关键行为。
"""

import json
from pathlib import Path

import pytest

from anima_webui.style_presets import (
    DEFAULT_COLLECTION_ID,
    StylePresetStore,
)
from anima_webui.workflow import WorkflowError


@pytest.fixture
def store_path(tmp_path: Path) -> Path:
    return tmp_path / "style_presets.json"


@pytest.mark.asyncio
async def test_legacy_data_migration(store_path: Path) -> None:
    """验证旧版单级分类 JSON 文件能够自动平滑迁移至两级分类,且预设关联不丢失。"""
    legacy_payload = {
        "version": 1,
        "collections": [
            {"id": 1, "name": "默认收藏", "is_default": True},
            {"id": 2, "name": "后入式", "is_default": False},
            {"id": 3, "name": "骑乘式", "is_default": False},
        ],
        "items": [
            {
                "id": "preset_001",
                "name": "旧预设1",
                "favorite": True,
                "collection_ids": [1, 2],
                "settings": {},
                "created_at": "2026-10-21T00:00:00Z",
                "updated_at": "2026-10-21T00:00:00Z",
            }
        ],
    }
    store_path.write_text(json.dumps(legacy_payload), encoding="utf-8")

    store = StylePresetStore(store_path)
    cols = store.list_collections()["collections"]

    # 验证母文件夹存在
    parent_col = next((c for c in cols if c["id"] == 2), None)
    assert parent_col is not None
    assert parent_col["name"] == "后入式"
    assert parent_col["parent_id"] is None

    # 验证自动派生了子文件夹
    sub_col = next((c for c in cols if c.get("parent_id") == 2), None)
    assert sub_col is not None
    assert sub_col["name"] == "默认"

    # 验证预设 collection_ids 已自动映射到子文件夹 ID
    preset = store.list()["items"][0]
    assert 1 in preset["collection_ids"]  # 默认收藏仍在
    assert sub_col["id"] in preset["collection_ids"]  # 成功映射至派生子类
    assert 2 not in preset["collection_ids"]  # 旧母类 ID 已被替换


@pytest.mark.asyncio
async def test_parent_and_child_creation(store_path: Path) -> None:
    """验证创建母文件夹与子文件夹,以及防重名与层级规则。"""
    store = StylePresetStore(store_path)

    # 1. 创建母文件夹
    parent = await store.create_collection("姿势库")
    assert parent["parent_id"] is None

    # 2. 创建子文件夹
    child1 = await store.create_collection("站姿", parent_id=parent["id"])
    assert child1["parent_id"] == parent["id"]

    # 3. 验证同母类下防重名
    with pytest.raises(WorkflowError, match="已存在同名子分类"):
        await store.create_collection("站姿", parent_id=parent["id"])

    # 4. 验证不同母类下子分类允许同名
    parent2 = await store.create_collection("场景库")
    child2 = await store.create_collection("站姿", parent_id=parent2["id"])
    assert child2["id"] != child1["id"]

    # 5. 验证禁止为子分类创建三级分类
    with pytest.raises(WorkflowError, match="子文件夹下不能再创建子文件夹"):
        await store.create_collection("三级分类", parent_id=child1["id"])

    # 6. 验证禁止为默认收藏创建子分类
    with pytest.raises(WorkflowError, match="默认收藏夹不支持创建子文件夹"):
        await store.create_collection("子类", parent_id=DEFAULT_COLLECTION_ID)


@pytest.mark.asyncio
async def test_cascade_delete_and_disassociation(store_path: Path) -> None:
    """验证删除子分类仅解绑,删除母分类级联清理子类并解绑。"""
    store = StylePresetStore(store_path)

    parent = await store.create_collection("姿势库")
    child = await store.create_collection("跪姿", parent_id=parent["id"])

    # 创建关联该子类的预设
    preset = await store.create(
        {
            "name": "测试预设",
            "collection_ids": [child["id"]],
            "settings": {},
        }
    )
    assert child["id"] in preset["collection_ids"]

    # 聚合计数验证:母类与子类此时 count 均为 1
    cols = store.list_collections()["collections"]
    assert next(c for c in cols if c["id"] == parent["id"])["count"] == 1
    assert next(c for c in cols if c["id"] == child["id"])["count"] == 1

    # 智能查询验证:传母类 ID 能查出,传子类 ID 也能查出
    assert len(store.list(collection_id=parent["id"])["items"]) == 1
    assert len(store.list(collection_id=child["id"])["items"]) == 1

    # 删除母文件夹
    res = await store.delete_collection(parent["id"])
    assert res["deleted"] is True
    assert child["id"] in res["deleted_sub_ids"]

    # 验证分类已清空,但预设本身完好存在且解绑
    assert len(store.list_collections()["collections"]) == 1  # 仅剩默认收藏
    updated_preset = store.list()["items"][0]
    assert updated_preset["collection_ids"] == []
