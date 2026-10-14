"""本地持久化文件的通用工具。"""

from __future__ import annotations

import os
from pathlib import Path


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
