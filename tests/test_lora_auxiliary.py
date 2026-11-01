import json
import pytest
from pathlib import Path

from anima_webui.lora_auxiliary import LoraAuxiliaryStore, normalize_auxiliary_words
from anima_webui.workflow import WorkflowError


def test_normalize_auxiliary_words():
    assert normalize_auxiliary_words(["  masterpiece  ", "best quality", "masterpiece"]) == [
        "masterpiece",
        "best quality",
    ]
    assert normalize_auxiliary_words([]) == []
    
    with pytest.raises(WorkflowError):
        normalize_auxiliary_words("not a list")

    with pytest.raises(WorkflowError):
        normalize_auxiliary_words([123])

    with pytest.raises(WorkflowError):
        normalize_auxiliary_words(["a" * 501])


@pytest.mark.asyncio
async def test_lora_auxiliary_store(tmp_path: Path):
    store_file = tmp_path / "lora_auxiliary_words.json"
    store = LoraAuxiliaryStore(store_file)

    # 初始状态为空
    assert store.get("test_lora.safetensors") == []
    assert not store.has("test_lora.safetensors")

    # 存储辅助词
    saved = await store.set("test_lora.safetensors", ["flat color", "sharp focus"])
    assert saved == ["flat color", "sharp focus"]
    assert store.has("test_lora.safetensors")
    assert store.get("test_lora.safetensors") == ["flat color", "sharp focus"]

    # 验证磁盘持久化
    store2 = LoraAuxiliaryStore(store_file)
    assert store2.get("test_lora.safetensors") == ["flat color", "sharp focus"]

    # 删除辅助词
    deleted = await store.delete("test_lora.safetensors")
    assert deleted is True
    assert store.get("test_lora.safetensors") == []
    assert not store.has("test_lora.safetensors")

    # 删除不存在的项
    assert await store.delete("non_existent.safetensors") is False

