"""针对本次静态审计发现缺陷的复现测试。

覆盖三项重点:
1. Windows 平台文件锁:mkstemp/os.replace/os.fsync 的句柄关闭时机。
2. 异步与线程池安全:HistoryStore 在 close 后仍被写入时的行为。
3. 坏文件恢复逻辑:backup_corrupt_file 遇到空文件/被占用文件时的降级。

注意:PermissionError 是 OSError 的子类。修复前,backup_corrupt_file 在
os.replace 失败时会把 PermissionError 冒泡出 reload() 的 except 块,
导致启动崩溃;修复后应降级为保留原文件、以空数据继续启动。
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from anima_webui.history import HistoryStore  # noqa: E402
from anima_webui.lora_triggers import LoraTriggerOverrideStore  # noqa: E402
from anima_webui.persistence import backup_corrupt_file  # noqa: E402
from anima_webui.style_presets import StylePresetStore  # noqa: E402


class BackupCorruptFileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.dir = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_backup_empty_file_succeeds(self) -> None:
        # 空文件(0 字节)是常见的损坏形态,备份必须平稳完成。
        path = self.dir / "empty.json"
        path.write_text("", encoding="utf-8")
        backup = backup_corrupt_file(path)
        self.assertTrue(backup.is_file())
        self.assertFalse(path.exists())

    def test_backup_locked_file_degrades_without_raising(self) -> None:
        # Windows 下文件被其他进程独占打开时,os.replace 会抛 PermissionError。
        # 修复后应降级:不抛异常,保留原文件并返回原路径。
        path = self.dir / "locked.json"
        path.write_text("{ broken", encoding="utf-8")
        with mock.patch(
            "anima_webui.persistence.os.replace", side_effect=PermissionError("locked")
        ):
            result = backup_corrupt_file(path)
        self.assertEqual(result, path)
        self.assertTrue(path.exists())


class StylePresetCorruptRecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "style_presets.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_empty_file_is_backed_up_and_store_starts_empty(self) -> None:
        # 空文件触发 json.JSONDecodeError,应被备份并以空数据启动。
        self.path.write_text("", encoding="utf-8")
        store = StylePresetStore(self.path)
        self.assertEqual(store.items, [])
        self.assertEqual(len(store.load_warnings), 1)

    def test_locked_file_does_not_crash_startup(self) -> None:
        # 坏文件被占用导致 os.replace 抛 PermissionError 时,启动不应崩溃。
        # 期望:降级为空数据 + 警告,而不是 PermissionError 冒泡。
        self.path.write_text("{ not valid json", encoding="utf-8")
        with mock.patch(
            "anima_webui.persistence.os.replace", side_effect=PermissionError("locked")
        ):
            store = StylePresetStore(self.path)
        self.assertEqual(store.items, [])
        self.assertTrue(store.load_warnings)


class LoraTriggerCorruptRecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "lora_trigger_overrides.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_empty_file_is_backed_up_and_store_starts_empty(self) -> None:
        self.path.write_text("", encoding="utf-8")
        store = LoraTriggerOverrideStore(self.path)
        self.assertEqual(store.overrides, {})
        self.assertTrue(store.load_warnings)

    def test_locked_file_does_not_crash_startup(self) -> None:
        self.path.write_text("{ not valid json", encoding="utf-8")
        with mock.patch(
            "anima_webui.persistence.os.replace", side_effect=PermissionError("locked")
        ):
            store = LoraTriggerOverrideStore(self.path)
        self.assertEqual(store.overrides, {})
        self.assertTrue(store.load_warnings)


class HistoryStoreLifecycleTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "history.sqlite3"

    def tearDown(self) -> None:
        self.temp.cleanup()

    async def test_write_after_close_raises_instead_of_silently_hanging(self) -> None:
        # close() 后连接已关闭;若仍有在途写入,应抛出明确异常而非静默卡死。
        store = HistoryStore(self.path)
        await store.create_batch("b1", 1, {})
        await store.close()
        with self.assertRaises(Exception):
            await store.update_batch("b1", status="done")


if __name__ == "__main__":
    unittest.main()
