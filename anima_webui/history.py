from __future__ import annotations

import asyncio
import functools
import json
import logging
import sqlite3
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any

from .persistence import backup_corrupt_file


logger = logging.getLogger(__name__)


DEFAULT_COLLECTION_ID = 1


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _parse_collection_ids(raw: Any) -> list[int]:
    """把 GROUP_CONCAT 得到的 "1,2" 解析为去重升序的整数列表。"""
    if raw is None:
        return []
    if isinstance(raw, (list, tuple, set)):
        values = raw
    else:
        values = str(raw).split(",")
    result: list[int] = []
    for value in values:
        text = str(value).strip()
        if not text:
            continue
        try:
            number = int(text)
        except ValueError:
            continue
        if number not in result:
            result.append(number)
    return sorted(result)


def _normalize_image_ids(raw: Any) -> list[int]:
    """把批量接口传入的图片 id 归一化为去重升序的正整数列表。

    非数组、布尔值、非整数或非正数一律视为非法输入,抛 CollectionError
    (由服务端映射为 400),避免把脏数据带进 SQL。
    """
    if not isinstance(raw, (list, tuple, set)):
        raise CollectionError("image_ids 必须是整数数组")
    result: list[int] = []
    for value in raw:
        if isinstance(value, bool):
            raise CollectionError("image_ids 必须是整数数组")
        try:
            number = int(value)
        except (TypeError, ValueError) as error:
            raise CollectionError("image_ids 必须是整数数组") from error
        if number <= 0:
            raise CollectionError("image_ids 必须是正整数")
        if number not in result:
            result.append(number)
    return sorted(result)


def _normalize_collection_ids(raw: Any) -> list[int]:
    """把收藏夹 id 归一化为去重升序的正整数列表(空数组合法)。"""
    if not isinstance(raw, (list, tuple, set)):
        raise CollectionError("collection_ids 必须是整数数组")
    result: list[int] = []
    for value in raw:
        if isinstance(value, bool):
            raise CollectionError("collection_ids 必须是整数数组")
        try:
            number = int(value)
        except (TypeError, ValueError) as error:
            raise CollectionError("collection_ids 必须是整数数组") from error
        if number <= 0:
            raise CollectionError("collection_ids 必须是正整数")
        if number not in result:
            result.append(number)
    return sorted(result)


class CollectionError(ValueError):
    """收藏夹业务校验失败(名称重复、默认夹不可删等),由服务端映射为 400。"""


class HistoryStore:
    """sqlite 持久化。

    所有数据库操作都在一个专用单线程 executor 上执行:
    - 单线程天然串行化,连接不会被并发使用;
    - commit/fsync 的耗时不再冻结事件循环(批次中每张图都要落库)。
    构造函数在调用方线程完成建表迁移,此后连接只被 executor 线程使用,
    因此 check_same_thread=False 是安全的。
    """

    def __init__(self, path: str | Path):
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        self.load_warnings: list[str] = []
        try:
            self.connection = self._open(destination)
        except sqlite3.DatabaseError as error:
            # 坏数据库不再阻断启动:改名备份后重建,并向界面报告警告。
            backup = backup_corrupt_file(destination)
            logger.warning("历史数据库无法读取(%s),已备份为 %s 并重建", error, backup.name)
            self.load_warnings.append(f"历史数据库无法读取,已备份为 {backup.name} 并重建")
            self.connection = self._open(destination)
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="anima-history")

    @staticmethod
    def _open(destination: Path) -> sqlite3.Connection:
        connection = sqlite3.connect(destination, check_same_thread=False)
        try:
            HistoryStore._initialize(connection)
        except sqlite3.DatabaseError:
            connection.close()
            raise
        return connection

    @staticmethod
    def _initialize(connection: sqlite3.Connection) -> None:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS batches (
                id TEXT PRIMARY KEY,
                total INTEGER NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL,
                error TEXT NOT NULL DEFAULT '',
                settings_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT NOT NULL REFERENCES batches(id) ON DELETE CASCADE,
                sequence INTEGER NOT NULL,
                prompt_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                subfolder TEXT NOT NULL DEFAULT '',
                file_type TEXT NOT NULL DEFAULT 'output',
                positive_prompt TEXT NOT NULL DEFAULT '',
                negative_prompt TEXT NOT NULL DEFAULT '',
                sample_seed INTEGER NOT NULL,
                prompt_seed INTEGER NOT NULL,
                settings_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_images_created ON images(id DESC);
            CREATE INDEX IF NOT EXISTS idx_images_batch ON images(batch_id, sequence);
            CREATE TABLE IF NOT EXISTS gallery_collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                is_default INTEGER NOT NULL DEFAULT 0,
                sort_order INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS image_collection_members (
                collection_id INTEGER NOT NULL REFERENCES gallery_collections(id) ON DELETE CASCADE,
                image_id INTEGER NOT NULL REFERENCES images(id) ON DELETE CASCADE,
                created_at TEXT NOT NULL,
                PRIMARY KEY (collection_id, image_id)
            );
            CREATE INDEX IF NOT EXISTS idx_members_image ON image_collection_members(image_id);
            CREATE INDEX IF NOT EXISTS idx_members_collection ON image_collection_members(collection_id);
            """
        )
        # 系统保留的默认收藏夹:表为空时自动补种,固定 id=1 供前端快捷收藏使用。
        if connection.execute("SELECT COUNT(*) FROM gallery_collections").fetchone()[0] == 0:
            connection.execute(
                "INSERT INTO gallery_collections (id, name, is_default, sort_order, created_at) VALUES (1, '默认收藏', 1, 0, ?)",
                (_now(),),
            )
        image_columns = {
            row[1] for row in connection.execute("PRAGMA table_info(images)").fetchall()
        }
        if "resolved_selection_json" not in image_columns:
            connection.execute(
                "ALTER TABLE images ADD COLUMN resolved_selection_json TEXT NOT NULL DEFAULT '{}'"
            )
        if "resolved_prompt" not in image_columns:
            connection.execute(
                "ALTER TABLE images ADD COLUMN resolved_prompt TEXT NOT NULL DEFAULT ''"
            )
        connection.execute(
            "UPDATE batches SET status = 'interrupted', error = 'WebUI 重启，未完成批次未自动恢复', updated_at = ? WHERE status IN ('running', 'stopping')",
            (_now(),),
        )
        connection.commit()

    async def _call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, functools.partial(func, *args, **kwargs))

    async def create_batch(self, batch_id: str, total: int, settings: dict[str, Any]) -> dict[str, Any]:
        return await self._call(self._create_batch, batch_id, total, settings)

    def _create_batch(self, batch_id: str, total: int, settings: dict[str, Any]) -> dict[str, Any]:
        timestamp = _now()
        self.connection.execute(
            "INSERT INTO batches (id, total, completed, status, error, settings_json, created_at, updated_at) VALUES (?, ?, 0, 'running', '', ?, ?, ?)",
            (batch_id, total, json.dumps(settings, ensure_ascii=False), timestamp, timestamp),
        )
        self.connection.commit()
        return self._get_batch(batch_id)

    async def update_batch(
        self,
        batch_id: str,
        *,
        completed: int | None = None,
        status: str | None = None,
        error: str | None = None,
    ) -> dict[str, Any]:
        return await self._call(
            self._update_batch, batch_id, completed=completed, status=status, error=error
        )

    def _update_batch(
        self,
        batch_id: str,
        *,
        completed: int | None = None,
        status: str | None = None,
        error: str | None = None,
    ) -> dict[str, Any]:
        fields = ["updated_at = ?"]
        values: list[Any] = [_now()]
        if completed is not None:
            fields.append("completed = ?")
            values.append(completed)
        if status is not None:
            fields.append("status = ?")
            values.append(status)
        if error is not None:
            fields.append("error = ?")
            values.append(error)
        values.append(batch_id)
        self.connection.execute(f"UPDATE batches SET {', '.join(fields)} WHERE id = ?", values)
        self.connection.commit()
        return self._get_batch(batch_id)

    async def add_image(self, **kwargs: Any) -> dict[str, Any]:
        return await self._call(self._add_image, **kwargs)

    def _add_image(
        self,
        *,
        batch_id: str,
        sequence: int,
        prompt_id: str,
        image: dict[str, Any],
        positive_prompt: str,
        negative_prompt: str,
        sample_seed: int,
        prompt_seed: int,
        settings: dict[str, Any],
        resolved_selection: dict[str, Any] | None = None,
        resolved_prompt: str = "",
    ) -> dict[str, Any]:
        cursor = self.connection.execute(
            """
            INSERT INTO images (
                batch_id, sequence, prompt_id, filename, subfolder, file_type,
                positive_prompt, negative_prompt, sample_seed, prompt_seed,
                settings_json, created_at, resolved_selection_json, resolved_prompt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                batch_id,
                sequence,
                prompt_id,
                str(image["filename"]),
                str(image.get("subfolder") or ""),
                str(image.get("type") or "output"),
                positive_prompt,
                negative_prompt,
                sample_seed,
                prompt_seed,
                json.dumps(settings, ensure_ascii=False),
                _now(),
                json.dumps(resolved_selection or {}, ensure_ascii=False),
                str(resolved_prompt or ""),
            ),
        )
        self.connection.commit()
        return self._get_image(cursor.lastrowid)

    async def get_batch(self, batch_id: str) -> dict[str, Any]:
        return await self._call(self._get_batch, batch_id)

    def _get_batch(self, batch_id: str) -> dict[str, Any]:
        row = self.connection.execute("SELECT * FROM batches WHERE id = ?", (batch_id,)).fetchone()
        if row is None:
            raise KeyError(batch_id)
        result = dict(row)
        result["settings"] = json.loads(result.pop("settings_json"))
        return result

    async def get_image(self, image_id: int) -> dict[str, Any]:
        return await self._call(self._get_image, image_id)

    def _get_image(self, image_id: int) -> dict[str, Any]:
        row = self.connection.execute(
            """
            SELECT images.*, batches.total AS batch_total,
                (SELECT GROUP_CONCAT(members.collection_id)
                 FROM image_collection_members AS members
                 WHERE members.image_id = images.id) AS collection_ids
            FROM images JOIN batches ON batches.id = images.batch_id
            WHERE images.id = ?
            """,
            (image_id,),
        ).fetchone()
        if row is None:
            raise KeyError(image_id)
        return self._image_row(row)

    def _image_row(self, row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        result["settings"] = json.loads(result.pop("settings_json"))
        result["resolved_selection"] = json.loads(result.pop("resolved_selection_json", "{}") or "{}")
        result["collection_ids"] = _parse_collection_ids(result.pop("collection_ids", None))
        return result

    async def list_images(
        self, page: int = 1, limit: int = 24, collection_id: int | None = None
    ) -> dict[str, Any]:
        return await self._call(self._list_images, page, limit, collection_id)

    def _list_images(
        self, page: int = 1, limit: int = 24, collection_id: int | None = None
    ) -> dict[str, Any]:
        page = max(1, page)
        limit = min(60, max(1, limit))
        # 收藏夹过滤:仅当传入有效正整数时生效,0/None 表示全部作品。
        filter_id: int | None = None
        if collection_id is not None:
            try:
                candidate = int(collection_id)
            except (TypeError, ValueError):
                candidate = 0
            if candidate > 0:
                filter_id = candidate
        if filter_id is None:
            total = int(self.connection.execute("SELECT COUNT(*) FROM images").fetchone()[0])
            rows = self.connection.execute(
                """
                SELECT images.*, batches.total AS batch_total,
                    (SELECT GROUP_CONCAT(members.collection_id)
                     FROM image_collection_members AS members
                     WHERE members.image_id = images.id) AS collection_ids
                FROM images JOIN batches ON batches.id = images.batch_id
                ORDER BY images.id DESC LIMIT ? OFFSET ?
                """,
                (limit, (page - 1) * limit),
            ).fetchall()
        else:
            total = int(
                self.connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM images
                    JOIN image_collection_members AS filter_members
                        ON filter_members.image_id = images.id
                    WHERE filter_members.collection_id = ?
                    """,
                    (filter_id,),
                ).fetchone()[0]
            )
            rows = self.connection.execute(
                """
                SELECT images.*, batches.total AS batch_total,
                    (SELECT GROUP_CONCAT(members.collection_id)
                     FROM image_collection_members AS members
                     WHERE members.image_id = images.id) AS collection_ids
                FROM images
                JOIN batches ON batches.id = images.batch_id
                JOIN image_collection_members AS filter_members
                    ON filter_members.image_id = images.id
                WHERE filter_members.collection_id = ?
                ORDER BY images.id DESC LIMIT ? OFFSET ?
                """,
                (filter_id, limit, (page - 1) * limit),
            ).fetchall()
        return {
            "items": [self._image_row(row) for row in rows],
            "page": page,
            "limit": limit,
            "total": total,
            "pages": max(1, (total + limit - 1) // limit),
        }

    async def delete_image(self, image_id: int) -> bool:
        return await self._call(self._delete_image, image_id)

    def _delete_image(self, image_id: int) -> bool:
        cursor = self.connection.execute("DELETE FROM images WHERE id = ?", (image_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    async def delete_images_batch(self, image_ids: list[int]) -> int:
        """批量删除图片记录,返回实际删除的行数。

        整个批次在 executor 线程内以单条 DELETE + 单次 commit 完成:
        要么全部生效,要么(异常时)整体回滚,不会出现删一半的中间态。
        收藏夹成员关系由外键 ON DELETE CASCADE 自动清理。
        """
        return await self._call(self._delete_images_batch, image_ids)

    def _delete_images_batch(self, image_ids: list[int]) -> int:
        wanted = _normalize_image_ids(image_ids)
        if not wanted:
            return 0
        placeholders = ",".join("?" for _ in wanted)
        try:
            cursor = self.connection.execute(
                f"DELETE FROM images WHERE id IN ({placeholders})", wanted
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        return int(cursor.rowcount or 0)

    async def batch_update_image_collections(
        self, image_ids: list[int], collection_ids: list[int], mode: str
    ) -> list[int]:
        """批量调整图片的收藏夹归属,返回实际被修改的图片 id 列表。

        mode:
        - ``add``:把 collection_ids 追加到每张图(已存在的成员关系跳过);
        - ``remove``:从每张图移除 collection_ids;
        - ``set``:用 collection_ids 全量覆盖每张图的归属。
        全部写入在 executor 线程内以单次事务提交,失败整体回滚。
        """
        return await self._call(
            self._batch_update_image_collections, image_ids, collection_ids, mode
        )

    def _batch_update_image_collections(
        self, image_ids: list[int], collection_ids: list[int], mode: str
    ) -> list[int]:
        if mode not in {"add", "remove", "set"}:
            raise CollectionError("mode 必须是 add、remove 或 set")
        wanted_images = _normalize_image_ids(image_ids)
        if not wanted_images:
            return []
        wanted_collections = _normalize_collection_ids(collection_ids)
        if mode in {"add", "set"} and not wanted_collections:
            raise CollectionError("collection_ids 不能为空")
        if wanted_collections:
            placeholders = ",".join("?" for _ in wanted_collections)
            found = {
                int(row[0])
                for row in self.connection.execute(
                    f"SELECT id FROM gallery_collections WHERE id IN ({placeholders})",
                    wanted_collections,
                ).fetchall()
            }
            missing = [value for value in wanted_collections if value not in found]
            if missing:
                raise CollectionError(
                    f"收藏夹不存在: {', '.join(str(value) for value in missing)}"
                )
        image_placeholders = ",".join("?" for _ in wanted_images)
        existing = [
            int(row[0])
            for row in self.connection.execute(
                f"SELECT id FROM images WHERE id IN ({image_placeholders})",
                wanted_images,
            ).fetchall()
        ]
        if not existing:
            return []
        timestamp = _now()
        try:
            if mode == "set":
                # 全量覆盖:先清空这些图的归属,再按目标集合重建。
                self.connection.execute(
                    f"DELETE FROM image_collection_members WHERE image_id IN ({image_placeholders})",
                    existing,
                )
                self.connection.executemany(
                    "INSERT INTO image_collection_members (collection_id, image_id, created_at) VALUES (?, ?, ?)",
                    [
                        (collection_id, image_id, timestamp)
                        for image_id in existing
                        for collection_id in wanted_collections
                    ],
                )
            elif mode == "add":
                # INSERT OR IGNORE 依赖主键 (collection_id, image_id) 去重。
                self.connection.executemany(
                    "INSERT OR IGNORE INTO image_collection_members (collection_id, image_id, created_at) VALUES (?, ?, ?)",
                    [
                        (collection_id, image_id, timestamp)
                        for image_id in existing
                        for collection_id in wanted_collections
                    ],
                )
            else:
                collection_placeholders = ",".join("?" for _ in wanted_collections)
                self.connection.execute(
                    f"DELETE FROM image_collection_members WHERE image_id IN ({image_placeholders}) "
                    f"AND collection_id IN ({collection_placeholders})",
                    [*existing, *wanted_collections],
                )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        return existing

    # ---------- 收藏夹 ----------
    async def toggle_default_favorite(self, image_id: int) -> dict[str, Any]:
        return await self._call(self._toggle_default_favorite, image_id)

    def _toggle_default_favorite(self, image_id: int) -> dict[str, Any]:
        if self.connection.execute("SELECT 1 FROM images WHERE id = ?", (image_id,)).fetchone() is None:
            raise KeyError(image_id)
        exists = self.connection.execute(
            "SELECT 1 FROM image_collection_members WHERE collection_id = ? AND image_id = ?",
            (DEFAULT_COLLECTION_ID, image_id),
        ).fetchone()
        if exists is None:
            self.connection.execute(
                "INSERT INTO image_collection_members (collection_id, image_id, created_at) VALUES (?, ?, ?)",
                (DEFAULT_COLLECTION_ID, image_id, _now()),
            )
            is_favorite = True
        else:
            self.connection.execute(
                "DELETE FROM image_collection_members WHERE collection_id = ? AND image_id = ?",
                (DEFAULT_COLLECTION_ID, image_id),
            )
            is_favorite = False
        self.connection.commit()
        return {
            "image_id": image_id,
            "is_favorite": is_favorite,
            "collection_ids": self._collection_ids_for_image(image_id),
        }

    def _collection_ids_for_image(self, image_id: int) -> list[int]:
        rows = self.connection.execute(
            "SELECT collection_id FROM image_collection_members WHERE image_id = ? ORDER BY collection_id ASC",
            (image_id,),
        ).fetchall()
        return [int(row[0]) for row in rows]

    async def list_collections(self) -> list[dict[str, Any]]:
        return await self._call(self._list_collections)

    def _list_collections(self) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            """
            SELECT collections.*, COUNT(members.image_id) AS item_count
            FROM gallery_collections AS collections
            LEFT JOIN image_collection_members AS members
                ON members.collection_id = collections.id
            GROUP BY collections.id
            ORDER BY collections.sort_order ASC, collections.id ASC
            """
        ).fetchall()
        return [
            {
                "id": int(row["id"]),
                "name": str(row["name"]),
                "is_default": bool(row["is_default"]),
                "sort_order": int(row["sort_order"]),
                "created_at": str(row["created_at"]),
                "item_count": int(row["item_count"]),
            }
            for row in rows
        ]

    async def count_images(self) -> int:
        """返回全库图片总数（不受收藏夹过滤影响）。"""
        return await self._call(self._count_images)

    def _count_images(self) -> int:
        return int(self.connection.execute("SELECT COUNT(*) FROM images").fetchone()[0])

    async def create_collection(self, name: str) -> dict[str, Any]:
        return await self._call(self._create_collection, name)

    def _create_collection(self, name: str) -> dict[str, Any]:
        cleaned = str(name or "").strip()
        if not cleaned:
            raise CollectionError("收藏夹名称不能为空")
        if len(cleaned) > 40:
            raise CollectionError("收藏夹名称不能超过 40 个字符")
        duplicate = self.connection.execute(
            "SELECT 1 FROM gallery_collections WHERE name = ?", (cleaned,)
        ).fetchone()
        if duplicate is not None:
            raise CollectionError(f"收藏夹已存在: {cleaned}")
        next_order = int(
            self.connection.execute(
                "SELECT COALESCE(MAX(sort_order), 0) + 1 FROM gallery_collections"
            ).fetchone()[0]
        )
        timestamp = _now()
        cursor = self.connection.execute(
            "INSERT INTO gallery_collections (name, is_default, sort_order, created_at) VALUES (?, 0, ?, ?)",
            (cleaned, next_order, timestamp),
        )
        self.connection.commit()
        return {
            "id": int(cursor.lastrowid),
            "name": cleaned,
            "is_default": False,
            "sort_order": next_order,
            "created_at": timestamp,
            "item_count": 0,
        }

    async def delete_collection(self, collection_id: int) -> bool:
        return await self._call(self._delete_collection, collection_id)

    def _delete_collection(self, collection_id: int) -> bool:
        row = self.connection.execute(
            "SELECT is_default FROM gallery_collections WHERE id = ?", (collection_id,)
        ).fetchone()
        if row is None:
            raise KeyError(collection_id)
        if int(row["is_default"]):
            raise CollectionError("默认收藏夹不可删除")
        self.connection.execute("DELETE FROM gallery_collections WHERE id = ?", (collection_id,))
        self.connection.commit()
        return True

    async def set_image_collections(self, image_id: int, collection_ids: list[int]) -> list[int]:
        return await self._call(self._set_image_collections, image_id, collection_ids)

    def _set_image_collections(self, image_id: int, collection_ids: list[int]) -> list[int]:
        if self.connection.execute("SELECT 1 FROM images WHERE id = ?", (image_id,)).fetchone() is None:
            raise KeyError(image_id)
        if not isinstance(collection_ids, (list, tuple, set)):
            raise CollectionError("collection_ids 必须是整数数组")
        wanted: list[int] = []
        for raw in collection_ids:
            if isinstance(raw, bool):
                raise CollectionError("collection_ids 必须是整数数组")
            try:
                value = int(raw)
            except (TypeError, ValueError) as error:
                raise CollectionError("collection_ids 必须是整数数组") from error
            if value not in wanted:
                wanted.append(value)
        if wanted:
            placeholders = ",".join("?" for _ in wanted)
            found = {
                int(row[0])
                for row in self.connection.execute(
                    f"SELECT id FROM gallery_collections WHERE id IN ({placeholders})", wanted
                ).fetchall()
            }
            missing = [value for value in wanted if value not in found]
            if missing:
                raise CollectionError(f"收藏夹不存在: {', '.join(str(value) for value in missing)}")
        # 全量覆盖:先清空该图归属,再按目标集合重建,保证与前端提交一致。
        self.connection.execute(
            "DELETE FROM image_collection_members WHERE image_id = ?", (image_id,)
        )
        timestamp = _now()
        self.connection.executemany(
            "INSERT INTO image_collection_members (collection_id, image_id, created_at) VALUES (?, ?, ?)",
            [(value, image_id, timestamp) for value in wanted],
        )
        self.connection.commit()
        return self._collection_ids_for_image(image_id)

    async def close(self) -> None:
        await self._call(self.connection.close)
        self._executor.shutdown(wait=True)
