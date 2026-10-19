"""本地持久化文件的通用工具。"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def backup_corrupt_file(path: Path) -> Path:
    """把无法读取的数据文件改名备份,让应用可以用空数据继续启动。

    原文件内容不会丢失:用户可以手工检查/修复备份文件后再改回原名。

    正常路径(改名成功)行为与旧版完全一致;仅当改名本身失败时
    (如 Windows 下文件被其他进程独占占用,os.replace 抛 PermissionError),
    才降级为保留原文件并返回原路径,避免异常在 reload() 的 except 块内
    冒泡、反而阻断启动。
    """
    backup = path.with_name(path.name + ".corrupt.bak")
    counter = 1
    while backup.exists():
        backup = path.with_name(f"{path.name}.corrupt-{counter}.bak")
        counter += 1
    try:
        os.replace(path, backup)
    except OSError:
        # 仅在改名失败时进入:保留原文件,调用方以空数据继续启动。
        return path
    return backup


def load_app_settings(storage_dir: Path) -> dict[str, Any]:
    """读取应用级配置(app_settings.json);文件缺失或损坏时返回空字典。"""
    settings_file = Path(storage_dir) / "app_settings.json"
    if not settings_file.is_file():
        return {}
    try:
        value = json.loads(settings_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def save_app_settings(storage_dir: Path, settings: dict[str, Any]) -> None:
    """原子写入应用级配置:先写临时文件再替换,避免写入中断导致配置损坏。"""
    directory = Path(storage_dir)
    directory.mkdir(parents=True, exist_ok=True)
    settings_file = directory / "app_settings.json"
    temp_file = settings_file.with_suffix(".tmp")
    temp_file.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    temp_file.replace(settings_file)
