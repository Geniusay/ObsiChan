from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "gark.py"


SCHEMA = {
    "schema_version": "test-1",
    "fields": {
        "type": {"type": "string", "required": True},
        "status": {"type": "string", "required": True},
        "review_status": {
            "type": "string",
            "required": True,
            "enum": ["not-required", "pending", "approved", "needs-revision", "rejected"],
        },
        "ai_generated": {"type": "boolean"},
        "created": {"type": "date", "required": True},
        "updated": {"type": "date"},
        "topics": {"type": "array", "required": True},
        "summary": {"type": "string", "required": True},
        "source_type": {"type": "string"},
        "source_url": {"type": "string"},
        "related": {"type": "array", "items": "wikilink"},
        "source": {"type": "array"},
        "source_session": {"type": "string"},
    },
    "common_fields": {
        "required": ["type", "status", "review_status", "created", "topics", "summary"],
        "optional": ["updated", "ai_generated", "related", "source", "source_session"],
    },
    "note_types": {
        "inbox": {
            "route": "10_Inbox",
            "statuses": ["inbox", "processed", "discarded"],
            "default_status": "inbox",
            "required": [],
            "optional": ["source_session"],
        },
        "source": {
            "route": "20_Sources",
            "statuses": ["raw", "distilled", "archived"],
            "default_status": "raw",
            "required": ["source_type"],
            "optional": ["related"],
        },
        "concept": {
            "route": "30_Notes/Concepts",
            "statuses": ["seed", "evergreen", "retired"],
            "default_status": "seed",
            "required": [],
            "optional": ["related", "source"],
        },
        "model": {
            "route": "30_Notes/Models",
            "statuses": ["seed", "evergreen", "retired"],
            "default_status": "seed",
            "required": [],
            "optional": ["related", "source"],
        },
        "moc": {
            "route": "40_Maps",
            "statuses": ["active", "retired"],
            "default_status": "active",
            "required": [],
            "optional": ["related"],
        },
    },
    "source_types": {
        "article": {"route": "20_Sources/Articles"},
        "social-post": {"route": "20_Sources/Articles"},
    },
    "taxonomy": {
        "canonical_topics": ["AI", "测试", "个人知识管理"],
        "aliases": {"PKM": "个人知识管理"},
    },
    "policies": {"moc_coverage_types": ["concept", "model"]},
    "migrations": {
        "missing_review_status": {
            "when_ai_generated_true": "pending",
            "otherwise": "not-required",
        }
    },
    "legacy_migrations": {
        "unknown_policy": "report-and-leave-unchanged",
        "status": {
            "ai-draft": {
                "per_type": {"concept": "seed", "model": "seed"},
                "set": {"review_status": "pending", "ai_generated": True},
            }
        },
        "source_type_aliases": {"x_note_tweet": "social-post"},
    },
}


def note_text(
    note_type: str,
    status: str,
    title: str,
    body: str,
    *,
    review_status: str = "not-required",
    extra: str = "",
) -> str:
    summary = " ".join(body.splitlines())
    return (
        "---\n"
        f"type: {note_type}\n"
        f"status: {status}\n"
        f"review_status: {review_status}\n"
        "created: 2026-08-16\n"
        "topics: [测试]\n"
        f"summary: \"{summary}\"\n"
        f"{extra}"
        "---\n\n"
        f"# {title}\n\n"
        f"{body}\n"
    )


class GarkCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.vault = Path(self.temporary.name) / "vault"
        for directory in (
            ".gark",
            "00_System",
            "10_Inbox",
            "20_Sources/Articles",
            "30_Notes/Concepts",
            "30_Notes/Models",
            "40_Maps",
        ):
            (self.vault / directory).mkdir(parents=True, exist_ok=True)
        (self.vault / "00_System" / "GARK_SCHEMA.json").write_text(
            json.dumps(SCHEMA, ensure_ascii=False), encoding="utf-8"
        )
        self.config = self.vault / ".gark" / "config.toml"
        self.config.write_text(
            """
version = 1
vault_root = ".."
runtime_dir = "runtime"
schema_path = "00_System/GARK_SCHEMA.json"

[index]
database = "index.sqlite3"
include_dirs = ["10_Inbox", "20_Sources", "30_Notes", "40_Maps"]

[search]
default_limit = 5
max_limit = 10

[observe]
log = "observations.jsonl"

[capture]
inbox_dir = "10_Inbox"
""".lstrip(),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_cli(self, *arguments: str, success: bool = True) -> subprocess.CompletedProcess[str]:
        process = subprocess.run(
            [sys.executable, str(SCRIPT), *arguments, "--config", str(self.config), "--json"],
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        if success and process.returncode != 0:
            self.fail(f"CLI failed ({process.returncode}): {process.stderr}\n{process.stdout}")
        return process

    def test_search_auto_indexes_chinese_and_refreshes(self) -> None:
        source = self.vault / "20_Sources" / "Articles" / "游戏设计.md"
        source.write_text(
            note_text(
                "source",
                "distilled",
                "游戏设计",
                "奇观机制通过注意力和信息缺口引导玩家探索。",
                extra="source_type: article\nrelated: [\"[[MOC - 游戏设计]]\"]\n",
            ),
            encoding="utf-8",
        )
        moc = self.vault / "40_Maps" / "MOC - 游戏设计.md"
        moc.write_text(
            note_text("moc", "active", "MOC - 游戏设计", "导航 [[游戏设计]]。"),
            encoding="utf-8",
        )

        first = json.loads(self.run_cli("search", "奇观机制", "--limit", "3").stdout)
        self.assertEqual(first["index_state"], "rebuilt")
        self.assertEqual(first["results"][0]["path"], "20_Sources/Articles/游戏设计.md")
        self.assertIn("奇观机制", first["results"][0]["snippet"])

        second = json.loads(self.run_cli("search", "奇观机制").stdout)
        self.assertEqual(second["index_state"], "fresh")

        new_note = self.vault / "30_Notes" / "Models" / "探索循环.md"
        new_note.write_text(
            note_text("model", "seed", "探索循环", "奇观机制需要价值兑现。", review_status="pending", extra="ai_generated: true\n"),
            encoding="utf-8",
        )
        refreshed = json.loads(self.run_cli("search", "价值兑现").stdout)
        self.assertEqual(refreshed["index_state"], "rebuilt")
        self.assertEqual(refreshed["results"][0]["title"], "探索循环")

    def test_audit_checks_routes_links_ai_review_and_moc_coverage(self) -> None:
        dotted = self.vault / "30_Notes" / "Concepts" / "Brik.space 平台.md"
        dotted.write_text(
            note_text("concept", "seed", "Brik.space 平台", "由地图引用。"), encoding="utf-8"
        )
        orphan = self.vault / "30_Notes" / "Concepts" / "孤立概念.md"
        orphan.write_text(
            note_text("concept", "seed", "孤立概念", "没有连接。", review_status="pending", extra="ai_generated: true\n"),
            encoding="utf-8",
        )
        moc = self.vault / "40_Maps" / "MOC - 平台.md"
        moc.write_text(
            note_text("moc", "active", "MOC - 平台", "收录 [[Brik.space 平台]] 和 [[不存在的笔记]]。"),
            encoding="utf-8",
        )
        wrong_route = self.vault / "30_Notes" / "Concepts" / "错位来源.md"
        wrong_route.write_text(
            note_text("source", "raw", "错位来源", "目录错误。", extra="source_type: article\n"),
            encoding="utf-8",
        )
        missing = self.vault / "10_Inbox" / "无属性.md"
        missing.write_text("# 无属性\n", encoding="utf-8")

        audit = json.loads(self.run_cli("audit").stdout)
        codes = [issue["code"] for issue in audit["issues"]]
        self.assertIn("frontmatter.missing", codes)
        self.assertIn("route.type_mismatch", codes)
        self.assertIn("route.source_type_mismatch", codes)
        self.assertIn("graph.orphan", codes)
        self.assertIn("moc.uncovered", codes)
        broken_messages = [issue["message"] for issue in audit["issues"] if issue["code"] == "link.broken"]
        self.assertEqual(broken_messages, ["Unresolved Wikilink: [[不存在的笔记]]"])

    def test_audit_validates_types_taxonomy_and_duplicate_sources_without_rejecting_empty_values(self) -> None:
        empty_values = self.vault / "30_Notes" / "Concepts" / "允许空值.md"
        empty_values.write_text(
            note_text(
                "concept",
                "seed",
                "允许空值",
                "空摘要与空主题仍然存在。",
                extra='updated:\nrelated: ["[[允许空值]]"]\n',
            )
            .replace("topics: [测试]", "topics: []")
            .replace('summary: "空摘要与空主题仍然存在。"', 'summary: ""'),
            encoding="utf-8",
        )
        invalid_types = self.vault / "30_Notes" / "Concepts" / "属性类型错误.md"
        invalid_types.write_text(
            note_text(
                "concept",
                "seed",
                "属性类型错误",
                "属性声明应被检查。",
                extra='ai_generated: "true"\nrelated: [not-a-wikilink]\n',
            )
            .replace("created: 2026-08-16", "created: 2026-02-30")
            .replace("topics: [测试]", "topics: 测试"),
            encoding="utf-8",
        )
        source_one = self.vault / "20_Sources" / "Articles" / "重复来源一.md"
        source_one.write_text(
            note_text(
                "source",
                "distilled",
                "重复来源一",
                "第一个来源。",
                extra="source_type: article\nsource_url: https://EXAMPLE.com/item#section\n",
            ).replace("topics: [测试]", "topics: [PKM, 新主题]"),
            encoding="utf-8",
        )
        source_two = self.vault / "20_Sources" / "Articles" / "重复来源二.md"
        source_two.write_text(
            note_text(
                "source",
                "distilled",
                "重复来源二",
                "第二个来源。",
                extra="source_type: x_note_tweet\nsource_url: https://example.com/item\n",
            ),
            encoding="utf-8",
        )

        audit = json.loads(self.run_cli("audit").stdout)
        issues = audit["issues"]
        codes = [issue["code"] for issue in issues]
        self.assertIn("field.type", codes)
        self.assertIn("taxonomy.alias", codes)
        self.assertIn("taxonomy.unknown", codes)
        self.assertIn("source_type.alias", codes)
        self.assertEqual(codes.count("source.duplicate_url"), 2)

        invalid_fields = {
            issue.get("field")
            for issue in issues
            if issue["path"] == "30_Notes/Concepts/属性类型错误.md" and issue["code"] == "field.type"
        }
        self.assertEqual(invalid_fields, {"created", "topics", "ai_generated", "related"})
        empty_required = [
            issue
            for issue in issues
            if issue["path"] == "30_Notes/Concepts/允许空值.md"
            and issue["code"] == "field.required"
            and issue.get("field") in {"topics", "summary"}
        ]
        self.assertEqual(empty_required, [])
        empty_type_errors = [
            issue
            for issue in issues
            if issue["path"] == "30_Notes/Concepts/允许空值.md" and issue["code"] == "field.type"
        ]
        self.assertEqual(empty_type_errors, [])

    def test_capture_is_dry_run_by_default_applies_once_and_stays_in_inbox(self) -> None:
        dry = json.loads(
            self.run_cli(
                "capture",
                "--title",
                "稳定结论",
                "--content",
                "这是可复用的结论。",
                "--topic",
                "AI",
                "--source-session",
                "task-123",
            ).stdout
        )
        destination = self.vault / dry["path"]
        self.assertEqual(dry["mode"], "dry-run")
        self.assertTrue(dry["ai_candidate"])
        self.assertFalse(destination.exists())
        self.assertIn("review_status: pending", dry["preview"])
        self.assertIn("ai_generated: true", dry["preview"])

        applied = json.loads(
            self.run_cli(
                "capture",
                "--title",
                "稳定结论",
                "--content",
                "这是可复用的结论。",
                "--topic",
                "PKM",
                "--source-session",
                "task-123",
                "--apply",
            ).stdout
        )
        self.assertTrue(applied["written"])
        self.assertEqual(destination.parent, self.vault / "10_Inbox")
        self.assertTrue(destination.exists())
        self.assertIn("个人知识管理", destination.read_text(encoding="utf-8"))

        duplicate = self.run_cli(
            "capture",
            "--title",
            "另一条结论",
            "--content",
            "另一个版本。",
            "--source-session",
            "task-123",
            "--apply",
            success=False,
        )
        self.assertEqual(duplicate.returncode, 2)
        self.assertIn("already has an AI candidate", duplicate.stderr)

        unknown_topic = self.run_cli(
            "capture",
            "--title",
            "未知主题候选",
            "--content",
            "内容。",
            "--topic",
            "临时新主题",
            success=False,
        )
        self.assertEqual(unknown_topic.returncode, 2)
        self.assertIn("Unknown topics", unknown_topic.stderr)

        missing_session = self.run_cli(
            "capture",
            "--title",
            "缺少会话",
            "--content",
            "内容。",
            "--apply",
            success=False,
        )
        self.assertEqual(missing_session.returncode, 2)
        self.assertIn("--source-session is required", missing_session.stderr)

    def test_capture_validates_generated_candidate_before_apply(self) -> None:
        schema = json.loads((self.vault / "00_System" / "GARK_SCHEMA.json").read_text(encoding="utf-8"))
        schema["note_types"]["inbox"]["required"] = ["source_url"]
        (self.vault / "00_System" / "GARK_SCHEMA.json").write_text(
            json.dumps(schema, ensure_ascii=False), encoding="utf-8"
        )
        rejected = self.run_cli(
            "capture",
            "--title",
            "不符合 Schema",
            "--content",
            "不会写入。",
            "--source-session",
            "schema-check",
            "--apply",
            success=False,
        )
        self.assertEqual(rejected.returncode, 2)
        self.assertIn("failed Schema validation", rejected.stderr)
        self.assertFalse((self.vault / "10_Inbox" / "不符合 Schema.md").exists())

    def test_runtime_paths_cannot_escape_and_non_sqlite_database_is_preserved(self) -> None:
        original_config = self.config.read_text(encoding="utf-8")
        outside = (Path(self.temporary.name) / "outside").as_posix()
        invalid_configs = [
            original_config.replace('runtime_dir = "runtime"', f'runtime_dir = "{outside}"'),
            original_config.replace('runtime_dir = "runtime"', 'runtime_dir = "../outside"'),
            original_config.replace('database = "index.sqlite3"', 'database = "../victim.txt"'),
            original_config.replace('log = "observations.jsonl"', f'log = "{outside}/observations.jsonl"'),
        ]
        for invalid_config in invalid_configs:
            with self.subTest(config=invalid_config.splitlines()[2:5]):
                self.config.write_text(invalid_config, encoding="utf-8")
                rejected = self.run_cli("index", success=False)
                self.assertEqual(rejected.returncode, 2)

        self.config.write_text(original_config, encoding="utf-8")
        database = self.vault / ".gark" / "runtime" / "index.sqlite3"
        database.parent.mkdir(parents=True, exist_ok=True)
        database.write_text("do not overwrite", encoding="utf-8")
        rejected = self.run_cli("index", success=False)
        self.assertEqual(rejected.returncode, 2)
        self.assertIn("non-SQLite", rejected.stderr)
        self.assertEqual(database.read_text(encoding="utf-8"), "do not overwrite")

    def test_observe_appends_utf8_jsonl(self) -> None:
        logged = json.loads(
            self.run_cli(
                "observe",
                "--event",
                "retrieve",
                "--query",
                "知识库",
                "--hit",
                "30_Notes/Concepts/示例.md",
                "--used",
                "30_Notes/Concepts/示例.md",
                "--metadata-json",
                '{"helpful":true}',
            ).stdout
        )
        log = Path(logged["log"])
        line = json.loads(log.read_text(encoding="utf-8").strip())
        self.assertEqual(line["query"], "知识库")
        self.assertTrue(line["metadata"]["helpful"])

        no_query = json.loads(self.run_cli("observe", "--event", "sensitive-retrieve", "--no-query").stdout)
        self.assertNotIn("query", no_query["event"])
        lines = [json.loads(item) for item in log.read_text(encoding="utf-8").splitlines()]
        self.assertNotIn("query", lines[-1])

    def test_migrate_preserves_body_skips_unknown_and_is_idempotent(self) -> None:
        candidate = self.vault / "30_Notes" / "Concepts" / "待迁移.md"
        original = note_text(
            "concept",
            "ai-draft",
            "待迁移",
            "正文不得变化。\n\n第二段。",
            review_status="pending",
        ).replace("review_status: pending\n", "")
        candidate.write_text(original, encoding="utf-8")
        unknown = self.vault / "30_Notes" / "Models" / "未知字段.md"
        unknown.write_text(
            note_text(
                "model",
                "ai-draft",
                "未知字段",
                "保持不动。",
                review_status="pending",
                extra="ai_generated: true\ncustom_field: value\n",
            ),
            encoding="utf-8",
        )
        valid_status = self.vault / "30_Notes" / "Concepts" / "合法状态缺审核.md"
        valid_status_original = note_text(
            "concept", "seed", "合法状态缺审核", "只补审核字段。"
        ).replace("review_status: not-required\n", "")
        valid_status.write_text(valid_status_original, encoding="utf-8")
        valid_ai = self.vault / "30_Notes" / "Concepts" / "合法 AI 状态缺审核.md"
        valid_ai_original = note_text(
            "concept",
            "seed",
            "合法 AI 状态缺审核",
            "合法状态仍按 AI 来源补审核。",
            extra="ai_generated: true\n",
        ).replace("review_status: not-required\n", "")
        valid_ai.write_text(valid_ai_original, encoding="utf-8")
        aliased_source = self.vault / "20_Sources" / "Articles" / "旧来源类型.md"
        aliased_source.write_text(
            note_text(
                "source",
                "distilled",
                "旧来源类型",
                "显式迁移别名。",
                extra="source_type: x_note_tweet\n",
            ),
            encoding="utf-8",
        )

        dry = json.loads(self.run_cli("migrate", "--dry-run").stdout)
        self.assertEqual(dry["change_count"], 4)
        self.assertEqual(dry["skip_count"], 1)
        self.assertEqual(candidate.read_text(encoding="utf-8"), original)

        applied = json.loads(self.run_cli("migrate", "--apply").stdout)
        self.assertEqual(applied["change_count"], 4)
        migrated = candidate.read_text(encoding="utf-8")
        self.assertIn('status: "seed"', migrated)
        self.assertIn('review_status: "pending"', migrated)
        self.assertIn("ai_generated: true", migrated)
        self.assertTrue(migrated.endswith("正文不得变化。\n\n第二段。\n"))
        self.assertIn("status: ai-draft", unknown.read_text(encoding="utf-8"))
        self.assertIn('review_status: "not-required"', valid_status.read_text(encoding="utf-8"))
        self.assertIn("status: seed", valid_status.read_text(encoding="utf-8"))
        self.assertIn('review_status: "pending"', valid_ai.read_text(encoding="utf-8"))
        self.assertIn("status: seed", valid_ai.read_text(encoding="utf-8"))
        self.assertIn('source_type: "social-post"', aliased_source.read_text(encoding="utf-8"))

        again = json.loads(self.run_cli("migrate", "--apply").stdout)
        self.assertEqual(again["change_count"], 0)
        self.assertEqual(candidate.read_text(encoding="utf-8"), migrated)


if __name__ == "__main__":
    unittest.main()
