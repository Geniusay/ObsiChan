#!/usr/bin/env python3
"""Local-first retrieval and governance CLI for the G-Ark Markdown vault."""

from __future__ import annotations

import argparse
import ast
import csv
import datetime as dt
import hashlib
import json
import os
import re
import sqlite3
import sys
import tempfile
import textwrap
import tomllib
import urllib.parse
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


WIKILINK_RE = re.compile(r"\[\[([^\[\]]+?)\]\]")
TOP_LEVEL_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:[ \t]*(.*))?$")
INVALID_FILENAME_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
KNOWLEDGE_TYPES = {"concept", "question", "model", "claim", "note"}
RESERVED_WINDOWS_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


class GarkError(RuntimeError):
    """A user-actionable CLI failure."""


@dataclass(frozen=True)
class Settings:
    config_path: Path
    vault_root: Path
    runtime_dir: Path
    database_path: Path
    observation_log: Path
    schema_path: Path
    include_dirs: tuple[str, ...]
    inbox_dir: str
    default_limit: int
    max_limit: int


@dataclass
class Frontmatter:
    present: bool
    data: dict[str, Any]
    keys: list[str]
    errors: list[str]
    lines: list[str]
    closing_index: int | None
    body: str


@dataclass(frozen=True)
class Note:
    path: Path
    relative_path: str
    title: str
    note_type: str
    summary: str
    properties: dict[str, Any]
    topics: list[str]
    links: list[str]
    body: str
    text: str
    frontmatter: Frontmatter


def _default_config_path() -> Path:
    return Path(__file__).resolve().parents[2] / "config.toml"


def _resolve_from(base: Path, value: str | os.PathLike[str]) -> Path:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = base / candidate
    return candidate.resolve()


def _resolve_restricted_child(base: Path, value: str | os.PathLike[str], label: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise GarkError(f"{label} must be a relative path without '..': {value}")
    if not candidate.parts or str(candidate) in {"", "."}:
        raise GarkError(f"{label} must name a path below {base}")
    base_resolved = base.resolve()
    resolved = (base_resolved / candidate).resolve()
    if not resolved.is_relative_to(base_resolved):
        raise GarkError(f"{label} escaped its allowed directory: {value}")
    return resolved


def _assert_sqlite_or_absent(path: Path) -> None:
    if not path.exists():
        return
    if not path.is_file():
        raise GarkError(f"Index database path is not a file: {path}")
    try:
        with path.open("rb") as handle:
            header = handle.read(16)
    except OSError as exc:
        raise GarkError(f"Cannot inspect index database: {path}") from exc
    if header != b"SQLite format 3\x00":
        raise GarkError(f"Refusing to overwrite a non-SQLite file: {path}")


def load_settings(args: argparse.Namespace) -> Settings:
    config_path = Path(getattr(args, "config", None) or _default_config_path()).expanduser().resolve()
    if not config_path.is_file():
        raise GarkError(f"Config file not found: {config_path}")

    try:
        with config_path.open("rb") as handle:
            config = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise GarkError(f"Cannot read config {config_path}: {exc}") from exc

    config_base = config_path.parent
    vault_value = getattr(args, "vault", None) or config.get("vault_root", "..")
    vault_root = _resolve_from(config_base, vault_value)
    if not vault_root.is_dir():
        raise GarkError(f"Vault root is not a directory: {vault_root}")

    runtime_value = config.get("runtime_dir", "runtime")
    runtime_dir = _resolve_restricted_child(config_base, runtime_value, "runtime_dir")
    gark_root = (vault_root / ".gark").resolve()
    if not runtime_dir.is_relative_to(gark_root):
        raise GarkError(f"runtime_dir must stay inside {gark_root}: {runtime_dir}")
    index_config = config.get("index", {})
    database_path = _resolve_restricted_child(
        runtime_dir, index_config.get("database", "gark-index.sqlite3"), "index.database"
    )
    observe_config = config.get("observe", {})
    observation_log = _resolve_restricted_child(
        runtime_dir, observe_config.get("log", "observations.jsonl"), "observe.log"
    )
    if observation_log.exists() and not observation_log.is_file():
        raise GarkError(f"Observation log path is not a file: {observation_log}")

    schema_value = config.get("schema_path", "00_System/GARK_SCHEMA.json")
    schema_path = _resolve_from(vault_root, schema_value)
    include_dirs = tuple(
        index_config.get(
            "include_dirs",
            ["00_System", "10_Inbox", "20_Sources", "30_Notes", "40_Maps", "50_Projects", "60_Areas", "70_Outputs"],
        )
    )
    capture_config = config.get("capture", {})
    search_config = config.get("search", {})
    return Settings(
        config_path=config_path,
        vault_root=vault_root,
        runtime_dir=runtime_dir,
        database_path=database_path,
        observation_log=observation_log,
        schema_path=schema_path,
        include_dirs=include_dirs,
        inbox_dir=str(capture_config.get("inbox_dir", "10_Inbox")),
        default_limit=int(search_config.get("default_limit", 5)),
        max_limit=int(search_config.get("max_limit", 20)),
    )


def _read_utf8(path: Path) -> tuple[str, bool]:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    try:
        return raw.decode("utf-8-sig"), has_bom
    except UnicodeDecodeError as exc:
        raise GarkError(f"File is not valid UTF-8: {path}") from exc


def _decode_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value.startswith("[[") and value.endswith("]]"):
        return value
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        try:
            parts = next(csv.reader([inner], skipinitialspace=True))
        except csv.Error:
            parts = inner.split(",")
        return [_decode_scalar(part) for part in parts]
    if value.startswith("{") and value.endswith("}"):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    lowered = value.casefold()
    if lowered in {"true", "yes"}:
        return True
    if lowered in {"false", "no"}:
        return False
    if lowered in {"null", "none", "~"}:
        return None
    if value[:1] in {'"', "'"} and value[-1:] == value[:1]:
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value[1:-1]
    return value


def parse_frontmatter(text: str) -> Frontmatter:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return Frontmatter(False, {}, [], [], lines, None, text)

    closing_index = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
    if closing_index is None:
        return Frontmatter(True, {}, [], ["frontmatter closing delimiter is missing"], lines, None, text)

    data: dict[str, Any] = {}
    keys: list[str] = []
    errors: list[str] = []
    content_lines = lines[1:closing_index]
    index = 0
    while index < len(content_lines):
        line = content_lines[index]
        stripped_line = line.rstrip("\r\n")
        if not stripped_line.strip() or stripped_line.lstrip().startswith("#"):
            index += 1
            continue
        if line[:1].isspace():
            errors.append(f"unexpected indentation on frontmatter line {index + 2}")
            index += 1
            continue
        match = TOP_LEVEL_KEY_RE.match(stripped_line)
        if not match:
            errors.append(f"cannot parse frontmatter line {index + 2}")
            index += 1
            continue
        key, raw_value = match.group(1), (match.group(2) or "")
        if key in data:
            errors.append(f"duplicate frontmatter field: {key}")
        keys.append(key)

        nested: list[str] = []
        cursor = index + 1
        while cursor < len(content_lines) and (
            content_lines[cursor][:1].isspace() or not content_lines[cursor].strip()
        ):
            nested.append(content_lines[cursor].rstrip("\r\n"))
            cursor += 1

        if raw_value in {"|", ">"}:
            data[key] = "\n".join(item.strip() for item in nested).strip()
        elif not raw_value and nested:
            list_items = []
            is_list = True
            for item in nested:
                stripped = item.strip()
                if not stripped:
                    continue
                if not stripped.startswith("-"):
                    is_list = False
                    break
                list_items.append(_decode_scalar(stripped[1:].strip()))
            data[key] = list_items if is_list else "\n".join(nested).strip()
        else:
            data[key] = _decode_scalar(raw_value)
        index = cursor if cursor > index + 1 else index + 1

    body = "".join(lines[closing_index + 1 :])
    return Frontmatter(True, data, keys, errors, lines, closing_index, body)


def _as_string_list(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()]


def _extract_links(text: str) -> list[str]:
    links: list[str] = []
    seen: set[str] = set()
    for match in WIKILINK_RE.finditer(text):
        target = match.group(1).split("|", 1)[0].split("#", 1)[0].strip().replace("\\", "/")
        if target and target not in seen:
            links.append(target)
            seen.add(target)
    return links


def _title_from_body(body: str, fallback: str) -> str:
    for line in body.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()
    return fallback


def load_note(path: Path, vault_root: Path) -> Note:
    text, _ = _read_utf8(path)
    frontmatter = parse_frontmatter(text)
    properties = frontmatter.data
    body = frontmatter.body
    title = str(properties.get("title") or _title_from_body(body, path.stem))
    note_type = str(properties.get("type") or "")
    summary = str(properties.get("summary") or "")
    topics = _as_string_list(properties.get("topics") or properties.get("tags"))
    links = _extract_links(text)
    relative_path = path.resolve().relative_to(vault_root.resolve()).as_posix()
    return Note(path, relative_path, title, note_type, summary, properties, topics, links, body, text, frontmatter)


def iter_markdown(settings: Settings) -> Iterable[Path]:
    seen: set[Path] = set()
    root = settings.vault_root.resolve()
    for configured_dir in settings.include_dirs:
        directory = (root / configured_dir).resolve()
        if not directory.is_relative_to(root) or not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*.md"), key=lambda item: item.as_posix().casefold()):
            resolved = path.resolve()
            if resolved.is_relative_to(root) and resolved not in seen and resolved.is_file():
                seen.add(resolved)
                yield resolved


def _flatten_properties(properties: dict[str, Any]) -> str:
    parts: list[str] = []
    for key, value in properties.items():
        if key in {"summary", "topics", "related"}:
            continue
        if isinstance(value, list):
            rendered = " ".join(str(item) for item in value)
        elif isinstance(value, dict):
            rendered = json.dumps(value, ensure_ascii=False, sort_keys=True)
        else:
            rendered = str(value)
        parts.append(f"{key} {rendered}")
    return "\n".join(parts)


def _vault_signature(paths: Iterable[Path], vault_root: Path) -> str:
    digest = hashlib.sha256()
    root = vault_root.resolve()
    for path in paths:
        stat = path.stat()
        relative = path.resolve().relative_to(root).as_posix()
        digest.update(f"{relative}\0{stat.st_size}\0{stat.st_mtime_ns}\n".encode("utf-8"))
    return digest.hexdigest()


def _create_index(database_path: Path, notes: list[Note], vault_signature: str) -> str:
    _assert_sqlite_or_absent(database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = database_path.with_name(f".{database_path.name}.{os.getpid()}.tmp")
    temporary_path.unlink(missing_ok=True)
    tokenizer = "trigram"
    try:
        connection = sqlite3.connect(temporary_path)
        connection.execute("PRAGMA journal_mode=OFF")
        connection.execute("PRAGMA synchronous=OFF")
        connection.executescript(
            """
            CREATE TABLE documents (
                id INTEGER PRIMARY KEY,
                path TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                type TEXT NOT NULL,
                summary TEXT NOT NULL,
                properties TEXT NOT NULL,
                topics TEXT NOT NULL,
                links TEXT NOT NULL,
                body TEXT NOT NULL,
                content_hash TEXT NOT NULL
            );
            CREATE VIRTUAL TABLE documents_fts USING fts5(
                title, properties, topics, summary, body,
                content='documents', content_rowid='id', tokenize='trigram'
            );
            CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            """
        )
    except sqlite3.OperationalError:
        if 'connection' in locals():
            connection.close()
        temporary_path.unlink(missing_ok=True)
        tokenizer = "unicode61"
        connection = sqlite3.connect(temporary_path)
        connection.executescript(
            """
            CREATE TABLE documents (
                id INTEGER PRIMARY KEY,
                path TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                type TEXT NOT NULL,
                summary TEXT NOT NULL,
                properties TEXT NOT NULL,
                topics TEXT NOT NULL,
                links TEXT NOT NULL,
                body TEXT NOT NULL,
                content_hash TEXT NOT NULL
            );
            CREATE VIRTUAL TABLE documents_fts USING fts5(
                title, properties, topics, summary, body,
                content='documents', content_rowid='id', tokenize='unicode61 remove_diacritics 2'
            );
            CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            """
        )

    try:
        with connection:
            for note in notes:
                properties_text = _flatten_properties(note.properties)
                topics_text = " ".join(note.topics)
                content_hash = hashlib.sha256(note.text.encode("utf-8")).hexdigest()
                cursor = connection.execute(
                    """
                    INSERT INTO documents(path, title, type, summary, properties, topics, links, body, content_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        note.relative_path,
                        note.title,
                        note.note_type,
                        note.summary,
                        properties_text,
                        topics_text,
                        json.dumps(note.links, ensure_ascii=False),
                        note.body,
                        content_hash,
                    ),
                )
                connection.execute(
                    "INSERT INTO documents_fts(rowid, title, properties, topics, summary, body) VALUES (?, ?, ?, ?, ?, ?)",
                    (cursor.lastrowid, note.title, properties_text, topics_text, note.summary, note.body),
                )
            connection.executemany(
                "INSERT INTO metadata(key, value) VALUES (?, ?)",
                [
                    ("schema_version", "1"),
                    ("tokenizer", tokenizer),
                    ("indexed_at", dt.datetime.now(dt.timezone.utc).isoformat()),
                    ("document_count", str(len(notes))),
                    ("vault_signature", vault_signature),
                ],
            )
        connection.close()
        _assert_sqlite_or_absent(database_path)
        os.replace(temporary_path, database_path)
    except Exception:
        connection.close()
        temporary_path.unlink(missing_ok=True)
        raise
    return tokenizer


def command_index(args: argparse.Namespace, settings: Settings) -> dict[str, Any]:
    paths = list(iter_markdown(settings))
    notes = [load_note(path, settings.vault_root) for path in paths]
    vault_signature = _vault_signature(paths, settings.vault_root)
    tokenizer = _create_index(settings.database_path, notes, vault_signature)
    return {
        "command": "index",
        "database": str(settings.database_path),
        "documents": len(notes),
        "tokenizer": tokenizer,
        "rebuilt": True,
        "vault_signature": vault_signature,
    }


def _index_is_fresh(settings: Settings, paths: list[Path]) -> bool:
    if not settings.database_path.is_file():
        return False
    try:
        connection = sqlite3.connect(settings.database_path)
        row = connection.execute("SELECT value FROM metadata WHERE key = 'vault_signature'").fetchone()
        connection.close()
    except sqlite3.Error:
        return False
    return bool(row and row[0] == _vault_signature(paths, settings.vault_root))


def _query_terms(query: str) -> list[str]:
    terms: list[str] = []
    for token in re.findall(r"[A-Za-z0-9_+.-]+|[\u3400-\u9fff]+", query.casefold()):
        if re.fullmatch(r"[\u3400-\u9fff]+", token) and len(token) > 2:
            terms.extend(token[index : index + 2] for index in range(len(token) - 1))
        else:
            terms.append(token)
    return list(dict.fromkeys(term for term in terms if term.strip()))


def _fts_candidates(connection: sqlite3.Connection, query: str) -> dict[int, float]:
    if len(query.strip()) < 3:
        return {}
    escaped = query.strip().replace('"', '""')
    try:
        rows = connection.execute(
            "SELECT rowid, bm25(documents_fts, 8.0, 3.0, 5.0, 4.0, 1.0) AS rank "
            "FROM documents_fts WHERE documents_fts MATCH ? LIMIT 200",
            (f'"{escaped}"',),
        ).fetchall()
    except sqlite3.OperationalError:
        return {}
    return {int(row[0]): max(0.0, -float(row[1])) for row in rows}


def _score_document(row: sqlite3.Row, query: str, terms: list[str], fts_bonus: float) -> float:
    query_folded = query.casefold().strip()
    fields = {
        "title": (str(row["title"]).casefold(), 16.0),
        "topics": (str(row["topics"]).casefold(), 9.0),
        "properties": (str(row["properties"]).casefold(), 5.0),
        "summary": (str(row["summary"]).casefold(), 7.0),
        "body": (str(row["body"]).casefold(), 1.5),
    }
    score = min(6.0, fts_bonus) + (2.0 if fts_bonus else 0.0)
    matched_terms: set[str] = set()
    for field_name, (text, weight) in fields.items():
        if query_folded and query_folded in text:
            score += weight * 2.5
            if field_name == "title" and text.strip() == query_folded:
                score += 30.0
        for term in terms:
            if term in text:
                matched_terms.add(term)
                score += weight
    if len(terms) >= 3 and len(matched_terms) < (len(terms) + 1) // 2:
        return 0.0
    if terms and len(matched_terms) == len(terms):
        score += 8.0
    if str(row["type"]) == "moc" or str(row["title"]).startswith("MOC - "):
        if query_folded in str(row["title"]).casefold() or query_folded in str(row["topics"]).casefold():
            score += 5.0
    return score


def _make_snippet(row: sqlite3.Row, query: str, terms: list[str], width: int = 180) -> str:
    candidates = [str(row["summary"]), str(row["body"]), str(row["properties"])]
    needles = [query, *sorted(terms, key=len, reverse=True)]
    for candidate in candidates:
        folded = candidate.casefold()
        position = next((folded.find(needle.casefold()) for needle in needles if needle and folded.find(needle.casefold()) >= 0), -1)
        if position >= 0:
            start = max(0, position - width // 3)
            excerpt = candidate[start : start + width]
            excerpt = re.sub(r"\s+", " ", excerpt).strip()
            if start:
                excerpt = "..." + excerpt
            if start + width < len(candidate):
                excerpt += "..."
            return excerpt
    fallback = str(row["summary"] or row["body"])
    return textwrap.shorten(re.sub(r"\s+", " ", fallback).strip(), width=width, placeholder="...")


def _row_result(row: sqlite3.Row, query: str, terms: list[str], score: float, match: str = "direct") -> dict[str, Any]:
    return {
        "path": str(row["path"]),
        "title": str(row["title"]),
        "type": str(row["type"]),
        "summary": str(row["summary"]),
        "snippet": _make_snippet(row, query, terms),
        "score": round(score, 3),
        "match": match,
    }


def _normalize_link_target(target: str) -> str:
    name = target.replace("\\", "/").rsplit("/", 1)[-1].strip()
    for suffix in (".md", ".canvas", ".txt", ".pdf", ".png", ".jpg", ".jpeg", ".webp", ".gif"):
        if name.casefold().endswith(suffix):
            name = name[: -len(suffix)]
            break
    return name.casefold()


def command_search(args: argparse.Namespace, settings: Settings) -> dict[str, Any]:
    query = args.query.strip()
    if not query:
        raise GarkError("Search query cannot be empty")
    indexed_paths = list(iter_markdown(settings))
    index_state = "fresh"
    if not _index_is_fresh(settings, indexed_paths):
        command_index(args, settings)
        index_state = "rebuilt"

    requested_limit = args.limit if args.limit is not None else settings.default_limit
    limit = max(1, min(int(requested_limit), settings.max_limit))
    terms = _query_terms(query)
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    try:
        fts_scores = _fts_candidates(connection, query)
        rows = connection.execute("SELECT * FROM documents").fetchall()
    finally:
        connection.close()

    scored: list[tuple[float, sqlite3.Row]] = []
    for row in rows:
        score = _score_document(row, query, terms, fts_scores.get(int(row["id"]), 0.0))
        if score > 0:
            scored.append((score, row))
    scored.sort(key=lambda item: (-item[0], str(item[1]["path"]).casefold()))

    direct = [_row_result(row, query, terms, score) for score, row in scored]
    if args.expand_links and direct:
        by_id = {int(row["id"]): row for row in rows}
        by_title = {str(row["title"]).casefold(): row for row in rows}
        by_stem = {_normalize_link_target(str(row["path"])): row for row in rows}
        direct_by_path = {item["path"]: item for item in direct}
        expanded: dict[str, dict[str, Any]] = {}
        seed_results = direct[: min(len(direct), max(3, limit))]
        for seed in seed_results:
            seed_row = next(row for row in rows if str(row["path"]) == seed["path"])
            neighbor_rows: list[sqlite3.Row] = []
            for target in json.loads(str(seed_row["links"])):
                neighbor = by_title.get(str(target).casefold()) or by_stem.get(_normalize_link_target(str(target)))
                if neighbor is not None:
                    neighbor_rows.append(neighbor)
            seed_title = str(seed_row["title"]).casefold()
            for candidate in by_id.values():
                candidate_targets = {_normalize_link_target(item) for item in json.loads(str(candidate["links"]))}
                if seed_title in candidate_targets or _normalize_link_target(str(seed_row["path"])) in candidate_targets:
                    neighbor_rows.append(candidate)
            for neighbor in neighbor_rows:
                path = str(neighbor["path"])
                if path in direct_by_path and direct_by_path[path]["score"] >= seed["score"] * 0.35:
                    continue
                linked_score = round(seed["score"] * 0.35, 3)
                current = expanded.get(path)
                if current is None or current["score"] < linked_score:
                    result = _row_result(neighbor, query, terms, linked_score, "linked")
                    result["linked_from"] = seed["path"]
                    expanded[path] = result
        merged = {item["path"]: item for item in direct}
        for path, item in expanded.items():
            if path not in merged or item["score"] > merged[path]["score"]:
                merged[path] = item
        direct = sorted(merged.values(), key=lambda item: (-item["score"], item["path"].casefold()))

    return {
        "command": "search",
        "query": query,
        "count": min(len(direct), limit),
        "index_state": index_state,
        "results": direct[:limit],
    }


def load_schema(settings: Settings) -> dict[str, Any]:
    if not settings.schema_path.is_file():
        raise GarkError(f"Schema file not found: {settings.schema_path}")
    try:
        with settings.schema_path.open("r", encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise GarkError(f"Cannot read schema {settings.schema_path}: {exc}") from exc
    if not isinstance(schema, dict):
        raise GarkError("Schema root must be a JSON object")
    return schema


def _add_issue(issues: list[dict[str, Any]], severity: str, code: str, path: str, message: str, field: str | None = None) -> None:
    issue = {"severity": severity, "code": code, "path": path, "message": message}
    if field:
        issue["field"] = field
    issues.append(issue)


def _allowed_fields(schema: dict[str, Any], note_type: str) -> set[str]:
    allowed = set(schema.get("fields", {}))
    common_fields = schema.get("common_fields", {})
    if isinstance(common_fields, dict):
        allowed.update(common_fields.get("required", []))
        allowed.update(common_fields.get("optional", []))
    type_spec = schema.get("note_types", {}).get(note_type, {})
    allowed.update(type_spec.get("required", []))
    allowed.update(type_spec.get("optional", []))
    return allowed


def _expected_routes(schema: dict[str, Any], note_type: str) -> list[str]:
    type_spec = schema.get("note_types", {}).get(note_type, {})
    routes = type_spec.get("route")
    if routes is None:
        routes = schema.get("directory_routes", {}).get(note_type)
    if routes is None:
        return []
    if isinstance(routes, str):
        return [routes]
    if isinstance(routes, list):
        return [str(route) for route in routes]
    return []


def _route_matches(relative_path: str, route: str) -> bool:
    normalized_path = relative_path.replace("\\", "/").casefold()
    normalized_route = route.replace("\\", "/").strip("/").casefold()
    normalized_route = normalized_route.split("{", 1)[0].rstrip("/")
    if normalized_route.endswith("/**"):
        normalized_route = normalized_route[:-3]
    if normalized_route.endswith("/*"):
        normalized_route = normalized_route[:-2]
    return normalized_path == normalized_route or normalized_path.startswith(normalized_route + "/")


def _resolve_wikilink(target: str, title_map: dict[str, list[str]], stem_map: dict[str, list[str]]) -> list[str]:
    normalized = target.replace("\\", "/").strip()
    title_key = normalized.casefold()
    stem_key = _normalize_link_target(normalized)
    return list(dict.fromkeys([*title_map.get(title_key, []), *stem_map.get(stem_key, [])]))


def _matches_declared_type(value: Any, declared_type: str) -> bool:
    if declared_type in {"string", "wikilink-or-string"}:
        return isinstance(value, str)
    if declared_type == "wikilink":
        return isinstance(value, str) and WIKILINK_RE.fullmatch(value.strip()) is not None
    if declared_type == "wikilink-or-url":
        if not isinstance(value, str):
            return False
        normalized = value.strip()
        if WIKILINK_RE.fullmatch(normalized) is not None:
            return True
        parsed = urllib.parse.urlsplit(normalized)
        return parsed.scheme.casefold() in {"http", "https"} and bool(parsed.netloc)
    if declared_type == "boolean":
        return isinstance(value, bool)
    if declared_type == "array":
        return isinstance(value, list)
    if declared_type == "object":
        return isinstance(value, dict)
    if declared_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if declared_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if declared_type == "date":
        if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            return False
        try:
            dt.date.fromisoformat(value)
        except ValueError:
            return False
        return True
    return True


def _field_type_error(value: Any, field_spec: dict[str, Any]) -> str | None:
    declared = field_spec.get("type")
    declared_types = [declared] if isinstance(declared, str) else declared if isinstance(declared, list) else []
    if declared_types and not any(_matches_declared_type(value, str(item)) for item in declared_types):
        return f"Expected {' or '.join(str(item) for item in declared_types)}, got {type(value).__name__}"
    if isinstance(value, list) and field_spec.get("items"):
        item_type = str(field_spec["items"])
        invalid_indexes = [index for index, item in enumerate(value) if not _matches_declared_type(item, item_type)]
        if invalid_indexes:
            return f"Expected array items of type {item_type}; invalid indexes: {invalid_indexes}"
    return None


def _required_fields(schema: dict[str, Any], note_type: str) -> list[str]:
    fields = schema.get("fields", {})
    required = list(schema.get("common_fields", {}).get("required", []))
    if not required:
        required = [name for name, spec in fields.items() if isinstance(spec, dict) and spec.get("required")]
    type_spec = schema.get("note_types", {}).get(note_type, {})
    return list(dict.fromkeys([*required, *type_spec.get("required", [])]))


def _validate_schema_values(
    frontmatter: Frontmatter,
    relative_path: str,
    schema: dict[str, Any],
    note_type: str,
    issues: list[dict[str, Any]],
) -> None:
    required_fields = set(_required_fields(schema, note_type))
    for field_name in required_fields:
        if field_name not in frontmatter.data or frontmatter.data[field_name] is None:
            _add_issue(
                issues,
                "error",
                "field.required",
                relative_path,
                f"Required field is missing or null: {field_name}",
                field_name,
            )

    for field_name, field_spec in schema.get("fields", {}).items():
        if field_name not in frontmatter.data or not isinstance(field_spec, dict):
            continue
        value = frontmatter.data[field_name]
        if value is None:
            continue
        if value == "" and field_name not in required_fields:
            continue
        type_error = _field_type_error(value, field_spec)
        if type_error:
            _add_issue(issues, "error", "field.type", relative_path, f"Invalid {field_name}: {type_error}", field_name)
            continue
        enum_values = field_spec.get("enum")
        if enum_values and value not in enum_values:
            _add_issue(
                issues,
                "error",
                "field.enum",
                relative_path,
                f"Invalid {field_name}: {value}",
                field_name,
            )


def _taxonomy_maps(schema: dict[str, Any]) -> tuple[dict[str, str], dict[str, str]]:
    taxonomy = schema.get("taxonomy", {})
    canonical = {
        str(topic).strip().casefold(): str(topic).strip()
        for topic in taxonomy.get("canonical_topics", [])
        if str(topic).strip()
    }
    aliases = {
        str(alias).strip().casefold(): str(target).strip()
        for alias, target in taxonomy.get("aliases", {}).items()
        if str(alias).strip() and str(target).strip()
    }
    return canonical, aliases


def _normalize_capture_topics(schema: dict[str, Any], topics: list[str]) -> list[str]:
    canonical, aliases = _taxonomy_maps(schema)
    if not canonical and not aliases:
        return list(dict.fromkeys(topic.strip() for topic in topics if topic.strip()))
    normalized: list[str] = []
    unknown: list[str] = []
    for raw_topic in topics:
        topic = raw_topic.strip()
        if not topic:
            continue
        key = topic.casefold()
        if key in canonical:
            selected = canonical[key]
        elif key in aliases:
            target = aliases[key]
            selected = canonical.get(target.casefold(), target)
        else:
            unknown.append(topic)
            continue
        if selected not in normalized:
            normalized.append(selected)
    if unknown:
        raise GarkError(f"Unknown topics are not allowed for capture: {', '.join(unknown)}")
    return normalized


def _migration_roots(schema: dict[str, Any]) -> list[dict[str, Any]]:
    roots: list[dict[str, Any]] = []
    for name in ("migrations", "legacy_migrations"):
        candidate = schema.get(name)
        if isinstance(candidate, dict):
            roots.append(candidate)
    return roots


def _source_type_aliases(schema: dict[str, Any]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for root in reversed(_migration_roots(schema)):
        candidate = root.get("source_type_aliases", {})
        if isinstance(candidate, dict):
            aliases.update({str(key): str(value) for key, value in candidate.items()})
    return aliases


def _normalized_source_url(value: str) -> str:
    raw = value.strip()
    if not raw:
        return ""
    try:
        parsed = urllib.parse.urlsplit(raw)
    except ValueError:
        return raw.casefold()
    if not parsed.scheme or not parsed.netloc:
        return raw.casefold()
    scheme = parsed.scheme.casefold()
    hostname = (parsed.hostname or "").casefold()
    try:
        port = parsed.port
    except ValueError:
        return raw.casefold()
    default_port = (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    netloc = hostname if port is None or default_port else f"{hostname}:{port}"
    path = parsed.path or "/"
    return urllib.parse.urlunsplit((scheme, netloc, path, parsed.query, ""))


def command_audit(args: argparse.Namespace, settings: Settings) -> dict[str, Any]:
    schema = load_schema(settings)
    notes: list[Note] = []
    issues: list[dict[str, Any]] = []
    for path in iter_markdown(settings):
        try:
            notes.append(load_note(path, settings.vault_root))
        except GarkError as exc:
            relative = path.resolve().relative_to(settings.vault_root).as_posix()
            _add_issue(issues, "error", "file.encoding", relative, str(exc))

    note_types = schema.get("note_types", {})
    canonical_topics, topic_aliases = _taxonomy_maps(schema)
    source_aliases = _source_type_aliases(schema)

    title_map: dict[str, list[str]] = defaultdict(list)
    stem_map: dict[str, list[str]] = defaultdict(list)
    for note in notes:
        title_map[note.title.casefold()].append(note.relative_path)
        stem_map[note.path.stem.casefold()].append(note.relative_path)

    all_stem_map: dict[str, list[str]] = defaultdict(list)
    excluded_roots = {".git", ".gark", ".obsidian", ".codex", ".claude", ".agents", ".tmlbrain", ".trash"}
    for path in settings.vault_root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.resolve().relative_to(settings.vault_root).as_posix()
        if relative.split("/", 1)[0] in excluded_roots:
            continue
        all_stem_map[path.stem.casefold()].append(relative)

    resolved_links: dict[str, set[str]] = defaultdict(set)
    inbound: dict[str, set[str]] = defaultdict(set)
    source_urls: dict[str, list[str]] = defaultdict(list)
    for note in notes:
        fm = note.frontmatter
        if not fm.present:
            _add_issue(issues, "error", "frontmatter.missing", note.relative_path, "Frontmatter is missing")
            continue
        for error in fm.errors:
            _add_issue(issues, "error", "frontmatter.invalid", note.relative_path, error)
        note_type = str(fm.data.get("type") or "")
        if note_type not in note_types:
            _add_issue(issues, "error", "type.unknown", note.relative_path, f"Unknown note type: {note_type}", "type")

        type_spec = note_types.get(note_type, {})
        _validate_schema_values(fm, note.relative_path, schema, note_type, issues)

        allowed = _allowed_fields(schema, note_type)
        for field_name in fm.keys:
            if allowed and field_name not in allowed:
                _add_issue(issues, "warning", "field.unknown", note.relative_path, f"Unknown frontmatter field: {field_name}", field_name)

        status = fm.data.get("status")
        allowed_statuses = type_spec.get("statuses", [])
        if status is not None and allowed_statuses and status not in allowed_statuses:
            _add_issue(issues, "error", "status.invalid_for_type", note.relative_path, f"Status {status} is invalid for type {note_type}", "status")

        routes = _expected_routes(schema, note_type)
        if note_type == "project":
            status_route = type_spec.get("route_by_status", {}).get(str(status))
            if status_route:
                routes = [str(status_route)]
        if routes and not any(_route_matches(note.relative_path, route) for route in routes):
            _add_issue(
                issues,
                "error",
                "route.type_mismatch",
                note.relative_path,
                f"Type {note_type} belongs under: {', '.join(routes)}",
                "type",
            )

        if note_type == "source":
            source_type = str(fm.data.get("source_type") or "")
            canonical_source_type = source_aliases.get(source_type, source_type)
            source_spec = schema.get("source_types", {}).get(canonical_source_type)
            if source_type in source_aliases:
                _add_issue(
                    issues,
                    "warning",
                    "source_type.alias",
                    note.relative_path,
                    f"Legacy source_type {source_type} should be migrated to {canonical_source_type}",
                    "source_type",
                )
            if source_type and not source_spec:
                _add_issue(issues, "error", "source_type.unknown", note.relative_path, f"Unknown source_type: {source_type}", "source_type")
            elif isinstance(source_spec, dict) and source_spec.get("route"):
                source_route = str(source_spec["route"])
                if not _route_matches(note.relative_path, source_route):
                    _add_issue(
                        issues,
                        "error",
                        "route.source_type_mismatch",
                        note.relative_path,
                        f"source_type {canonical_source_type} belongs under: {source_route}",
                        "source_type",
                    )

        topics_value = fm.data.get("topics")
        if isinstance(topics_value, list) and (canonical_topics or topic_aliases):
            for topic in topics_value:
                if not isinstance(topic, str):
                    continue
                key = topic.strip().casefold()
                if key in canonical_topics:
                    continue
                if key in topic_aliases:
                    _add_issue(
                        issues,
                        "warning",
                        "taxonomy.alias",
                        note.relative_path,
                        f"Topic {topic} should use canonical topic {topic_aliases[key]}",
                        "topics",
                    )
                else:
                    _add_issue(
                        issues,
                        "warning",
                        "taxonomy.unknown",
                        note.relative_path,
                        f"Unknown topic: {topic}",
                        "topics",
                    )

        source_url = fm.data.get("source_url")
        if isinstance(source_url, str) and source_url.strip():
            source_urls[_normalized_source_url(source_url)].append(note.relative_path)

        ai_generated = fm.data.get("ai_generated") is True or str(status) == "ai-draft"
        if ai_generated and fm.data.get("review_status") != "pending" and str(status) == "ai-draft":
            _add_issue(issues, "error", "ai.review_required", note.relative_path, "Legacy AI draft requires review_status: pending", "review_status")
        elif fm.data.get("ai_generated") is True and fm.data.get("review_status") in (None, ""):
            _add_issue(issues, "error", "ai.review_required", note.relative_path, "AI-generated note requires review_status", "review_status")

        for target in note.links:
            note_matches = _resolve_wikilink(target, title_map, stem_map)
            any_matches = list(dict.fromkeys([*note_matches, *all_stem_map.get(_normalize_link_target(target), [])]))
            if not any_matches:
                _add_issue(issues, "warning", "link.broken", note.relative_path, f"Unresolved Wikilink: [[{target}]]")
            else:
                for match in note_matches:
                    resolved_links[note.relative_path].add(match)
                    inbound[match].add(note.relative_path)

    for normalized_url, duplicate_paths in source_urls.items():
        if not normalized_url or len(duplicate_paths) < 2:
            continue
        for duplicate_path in duplicate_paths:
            others = [path for path in duplicate_paths if path != duplicate_path]
            _add_issue(
                issues,
                "warning",
                "source.duplicate_url",
                duplicate_path,
                f"Duplicate source_url is also used by: {', '.join(others)}",
                "source_url",
            )

    moc_paths = {note.relative_path for note in notes if note.note_type == "moc" or note.path.stem.startswith("MOC - ")}
    moc_coverage_types = set(schema.get("policies", {}).get("moc_coverage_types", KNOWLEDGE_TYPES))
    for note in notes:
        if note.note_type not in KNOWLEDGE_TYPES:
            continue
        outgoing = resolved_links.get(note.relative_path, set())
        incoming = inbound.get(note.relative_path, set())
        if not outgoing and not incoming:
            _add_issue(issues, "warning", "graph.orphan", note.relative_path, "Knowledge note has no resolved incoming or outgoing links")
        if note.note_type in moc_coverage_types:
            linked_to_moc = bool(outgoing & moc_paths)
            linked_from_moc = bool(incoming & moc_paths)
            if not linked_to_moc and not linked_from_moc:
                _add_issue(issues, "warning", "moc.uncovered", note.relative_path, "Knowledge note is not covered by a MOC")

    issues.sort(key=lambda issue: (issue["severity"] != "error", issue["code"], issue["path"]))
    severity_counts = Counter(issue["severity"] for issue in issues)
    code_counts = Counter(issue["code"] for issue in issues)
    return {
        "command": "audit",
        "schema_version": schema.get("schema_version"),
        "notes": len(notes),
        "issue_count": len(issues),
        "summary": {
            "by_severity": dict(sorted(severity_counts.items())),
            "by_code": dict(sorted(code_counts.items())),
        },
        "issues": issues,
    }


def _safe_runtime_path(path: Path, runtime_dir: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(runtime_dir.resolve()):
        raise GarkError(f"Runtime output must stay inside {runtime_dir}")
    return resolved


def command_observe(args: argparse.Namespace, settings: Settings) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    if args.metadata_json:
        try:
            parsed = json.loads(args.metadata_json)
        except json.JSONDecodeError as exc:
            raise GarkError(f"--metadata-json is invalid JSON: {exc}") from exc
        if not isinstance(parsed, dict):
            raise GarkError("--metadata-json must contain a JSON object")
        metadata = parsed

    event = {
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        "event": args.event,
        "reason": args.reason,
        "hits": args.hit or [],
        "used": args.used or [],
        "outcome": args.outcome,
        "metadata": metadata,
    }
    if not args.no_query and args.query is not None:
        event["query"] = args.query
    log_path = _safe_runtime_path(settings.observation_log, settings.runtime_dir)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return {"command": "observe", "logged": True, "log": str(log_path), "event": event}


def _safe_filename(title: str) -> str:
    cleaned = INVALID_FILENAME_RE.sub("-", title).strip().rstrip(". ")
    cleaned = re.sub(r"\s+", " ", cleaned)
    if not cleaned or cleaned in {".", ".."}:
        raise GarkError("Title does not produce a safe filename")
    if cleaned.split(".", 1)[0].upper() in RESERVED_WINDOWS_NAMES:
        cleaned = "_" + cleaned
    return cleaned[:180].rstrip(". ")


def _yaml_scalar(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _summary_from_content(content: str) -> str:
    flattened = re.sub(r"\s+", " ", content).strip()
    return flattened[:160] + ("..." if len(flattened) > 160 else "")


def _capture_status(settings: Settings) -> str:
    if settings.schema_path.is_file():
        schema = load_schema(settings)
        return str(schema.get("note_types", {}).get("inbox", {}).get("default_status", "inbox"))
    return "inbox"


def _capture_document(title: str, content: str, topics: list[str], source_session: str | None, status: str) -> str:
    today = dt.date.today().isoformat()
    frontmatter_lines = [
        "---",
        "type: inbox",
        f"status: {_yaml_scalar(status)}",
        f"created: {today}",
        "review_status: pending",
        "ai_generated: true",
        f"topics: {json.dumps(topics, ensure_ascii=False)}",
        f"summary: {_yaml_scalar(_summary_from_content(content))}",
    ]
    if source_session:
        frontmatter_lines.append(f"source_session: {_yaml_scalar(source_session)}")
    frontmatter_lines.extend(["---", "", f"# {title}", "", content.rstrip(), ""])
    return "\n".join(frontmatter_lines)


def _validate_capture_document(document: str, relative_path: str, schema: dict[str, Any]) -> None:
    frontmatter = parse_frontmatter(document)
    issues: list[dict[str, Any]] = []
    if not frontmatter.present or frontmatter.errors:
        raise GarkError(f"Generated AI candidate has invalid frontmatter: {frontmatter.errors}")
    note_type = str(frontmatter.data.get("type") or "")
    if note_type not in schema.get("note_types", {}):
        _add_issue(issues, "error", "type.unknown", relative_path, f"Unknown note type: {note_type}", "type")
    _validate_schema_values(frontmatter, relative_path, schema, note_type, issues)
    type_spec = schema.get("note_types", {}).get(note_type, {})
    status = frontmatter.data.get("status")
    if type_spec.get("statuses") and status not in type_spec["statuses"]:
        _add_issue(
            issues,
            "error",
            "status.invalid_for_type",
            relative_path,
            f"Status {status} is invalid for type {note_type}",
            "status",
        )
    routes = _expected_routes(schema, note_type)
    if routes and not any(_route_matches(relative_path, route) for route in routes):
        _add_issue(
            issues,
            "error",
            "route.type_mismatch",
            relative_path,
            f"Type {note_type} belongs under: {', '.join(routes)}",
            "type",
        )
    errors = [issue for issue in issues if issue["severity"] == "error"]
    if errors:
        details = "; ".join(f"{issue['code']}: {issue['message']}" for issue in errors)
        raise GarkError(f"AI candidate failed Schema validation: {details}")


def _capture_marker(settings: Settings, source_session: str) -> Path:
    session_hash = hashlib.sha256(source_session.encode("utf-8")).hexdigest()
    return _safe_runtime_path(settings.runtime_dir / "captures" / f"{session_hash}.json", settings.runtime_dir)


def command_capture(args: argparse.Namespace, settings: Settings) -> dict[str, Any]:
    if args.content is not None:
        content = args.content
    else:
        content_path = Path(args.content_file).expanduser().resolve()
        content, _ = _read_utf8(content_path)
    if not content.strip():
        raise GarkError("Capture content cannot be empty")

    title = args.title.strip()
    if not title:
        raise GarkError("Capture title cannot be empty")
    source_session = args.source_session.strip() if args.source_session else None
    if args.apply and not source_session:
        raise GarkError("--source-session is required when applying an AI candidate")
    schema = load_schema(settings)
    topics = _normalize_capture_topics(schema, args.topic or [])
    filename = _safe_filename(title) + ".md"
    vault_root = settings.vault_root.resolve()
    inbox = (vault_root / settings.inbox_dir).resolve()
    if not inbox.is_relative_to(vault_root):
        raise GarkError("Configured Inbox must stay inside the vault")
    destination = (inbox / filename).resolve()
    if destination.parent != inbox or not destination.is_relative_to(vault_root):
        raise GarkError("Capture destination escaped the configured Inbox")

    normalized_title = title.casefold()
    duplicates: list[str] = []
    session_duplicates: list[str] = []
    for path in iter_markdown(settings):
        note = load_note(path, settings.vault_root)
        if note.title.strip().casefold() == normalized_title or path.stem.casefold() == Path(filename).stem.casefold():
            duplicates.append(note.relative_path)
        if source_session and str(note.properties.get("source_session") or "").strip() == source_session:
            session_duplicates.append(note.relative_path)
    if duplicates:
        raise GarkError(f"A note with this title already exists: {', '.join(duplicates)}")
    if session_duplicates:
        raise GarkError(f"This source session already has an AI candidate: {', '.join(session_duplicates)}")

    relative_path = destination.relative_to(vault_root).as_posix()
    document = _capture_document(title, content, topics, source_session, _capture_status(settings))
    _validate_capture_document(document, relative_path, schema)
    result = {
        "command": "capture",
        "ai_candidate": True,
        "mode": "apply" if args.apply else "dry-run",
        "path": relative_path,
        "written": False,
        "preview": document,
    }
    if args.apply:
        inbox.mkdir(parents=True, exist_ok=True)
        marker_path = _capture_marker(settings, source_session)
        marker_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with marker_path.open("x", encoding="utf-8", newline="\n") as marker:
                marker.write(
                    json.dumps(
                        {
                            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
                            "session_hash": marker_path.stem,
                            "path": relative_path,
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    )
                    + "\n"
                )
        except FileExistsError as exc:
            raise GarkError("This source session already has an AI candidate") from exc
        try:
            with destination.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(document)
        except FileExistsError as exc:
            marker_path.unlink(missing_ok=True)
            raise GarkError(f"Capture destination already exists: {destination}") from exc
        except Exception:
            marker_path.unlink(missing_ok=True)
            raise
        result["written"] = True
    return result


def _migration_spec(schema: dict[str, Any], old_status: str) -> dict[str, Any] | None:
    for migrations in _migration_roots(schema):
        status_migrations = migrations.get("status", {})
        spec = status_migrations.get(old_status) if isinstance(status_migrations, dict) else None
        if isinstance(spec, dict):
            return spec
    return None


def _missing_review_status_value(schema: dict[str, Any], frontmatter: Frontmatter) -> str | None:
    for migrations in _migration_roots(schema):
        spec = migrations.get("missing_review_status")
        if spec is None and isinstance(migrations.get("defaults"), dict):
            spec = migrations["defaults"].get("missing_review_status")
        if isinstance(spec, str):
            return spec
        if isinstance(spec, dict):
            if frontmatter.data.get("ai_generated") is True:
                value = spec.get("when_ai_generated_true") or spec.get("ai_generated")
            else:
                value = spec.get("otherwise") or spec.get("default")
            return str(value) if value is not None else None
    return None


def _migration_status_for_type(spec: dict[str, Any], note_type: str) -> str | None:
    for key in ("per_type", "by_type", "status_by_type", "map_by_type", "type_defaults"):
        mapping = spec.get(key)
        if isinstance(mapping, dict) and note_type in mapping:
            return str(mapping[note_type])
    set_values = spec.get("set")
    if isinstance(set_values, dict):
        status = set_values.get("status")
        if isinstance(status, str):
            return status
        if isinstance(status, dict) and note_type in status:
            return str(status[note_type])
    direct = spec.get(note_type)
    return str(direct) if isinstance(direct, str) else None


def _migration_set_values(spec: dict[str, Any], old_status: str) -> dict[str, Any]:
    values = spec.get("set", {})
    if not isinstance(values, dict):
        values = {}
    result = {key: value for key, value in values.items() if key != "status"}
    if old_status == "ai-draft":
        result.setdefault("review_status", "pending")
        result.setdefault("ai_generated", True)
    return result


def _render_yaml_value(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return _yaml_scalar(str(value))


def _apply_frontmatter_changes(text: str, changes: dict[str, Any]) -> str:
    fm = parse_frontmatter(text)
    if not fm.present or fm.closing_index is None:
        raise GarkError("Cannot update a file without valid frontmatter")
    lines = list(fm.lines)
    key_indexes: dict[str, int] = {}
    for index in range(1, fm.closing_index):
        candidate = lines[index].rstrip("\r\n")
        match = TOP_LEVEL_KEY_RE.match(candidate) if not lines[index][:1].isspace() else None
        if match:
            key_indexes[match.group(1)] = index
    newline = "\r\n" if any(line.endswith("\r\n") for line in lines[: fm.closing_index + 1]) else "\n"
    existing_changes = {key: value for key, value in changes.items() if key in key_indexes}
    missing_changes = {key: value for key, value in changes.items() if key not in key_indexes}
    for key, value in existing_changes.items():
        rendered = f"{key}: {_render_yaml_value(value)}{newline}"
        original = lines[key_indexes[key]]
        original_newline = "\r\n" if original.endswith("\r\n") else "\n" if original.endswith("\n") else ""
        lines[key_indexes[key]] = rendered.rstrip("\r\n") + original_newline
    insert_at = fm.closing_index
    for key, value in missing_changes.items():
        rendered = f"{key}: {_render_yaml_value(value)}{newline}"
        lines.insert(insert_at, rendered)
        insert_at += 1
    return "".join(lines)


def _atomic_write_utf8(path: Path, text: str, with_bom: bool) -> None:
    prefix = b"\xef\xbb\xbf" if with_bom else b""
    payload = prefix + text.encode("utf-8")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def command_migrate(args: argparse.Namespace, settings: Settings) -> dict[str, Any]:
    schema = load_schema(settings)
    changes: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    apply_mode = bool(args.apply)

    for path in iter_markdown(settings):
        text, with_bom = _read_utf8(path)
        fm = parse_frontmatter(text)
        relative = path.resolve().relative_to(settings.vault_root).as_posix()
        if not fm.present or fm.errors:
            skipped.append({"path": relative, "reason": "missing_or_invalid_frontmatter", "details": fm.errors})
            continue
        old_status = str(fm.data.get("status") or "")
        note_type = str(fm.data.get("type") or "")
        valid_statuses = schema.get("note_types", {}).get(note_type, {}).get("statuses", [])
        planned: dict[str, Any] = {}
        unresolved_status = False

        if old_status not in valid_statuses:
            spec = _migration_spec(schema, old_status)
            if spec is not None:
                new_status = _migration_status_for_type(spec, note_type)
                if new_status:
                    planned["status"] = new_status
                    planned.update(_migration_set_values(spec, old_status))
                else:
                    unresolved_status = True

        if "review_status" not in fm.data or fm.data.get("review_status") is None:
            review_status = _missing_review_status_value(schema, fm)
            if review_status is not None:
                planned.setdefault("review_status", review_status)

        source_type = fm.data.get("source_type")
        source_alias = _source_type_aliases(schema).get(str(source_type)) if source_type is not None else None
        if source_alias is not None:
            planned["source_type"] = source_alias

        if not planned:
            if unresolved_status:
                skipped.append(
                    {"path": relative, "reason": "no_type_status_mapping", "type": note_type, "status": old_status}
                )
            continue

        if note_type not in schema.get("note_types", {}):
            skipped.append({"path": relative, "reason": "unknown_type", "type": note_type})
            continue

        unknown_fields = sorted(set(fm.keys) - _allowed_fields(schema, note_type))
        if unknown_fields:
            skipped.append({"path": relative, "reason": "unknown_fields", "fields": unknown_fields})
            continue

        conflicts = {
            key: {"current": fm.data[key], "requested": value}
            for key, value in planned.items()
            if key not in {"status", "source_type"}
            and key in fm.data
            and fm.data[key] is not None
            and fm.data[key] != value
        }
        if conflicts:
            skipped.append({"path": relative, "reason": "field_conflict", "conflicts": conflicts})
            continue

        updated = _apply_frontmatter_changes(text, planned)
        file_change = {
            "path": relative,
            "from": {key: fm.data.get(key) for key in planned},
            "to": planned,
            "applied": False,
        }
        if unresolved_status:
            file_change["unresolved"] = ["status"]
        if apply_mode:
            _atomic_write_utf8(path, updated, with_bom)
            file_change["applied"] = True
        changes.append(file_change)

    return {
        "command": "migrate",
        "mode": "apply" if apply_mode else "dry-run",
        "change_count": len(changes),
        "skip_count": len(skipped),
        "changes": changes,
        "skipped": skipped,
    }


def _print_text(result: dict[str, Any]) -> None:
    command = result.get("command")
    if command == "index":
        print(f"Indexed {result['documents']} Markdown files into {result['database']} ({result['tokenizer']}).")
    elif command == "search":
        print(f"Search: {result['query']} ({result['count']} results)")
        for index, item in enumerate(result["results"], 1):
            print(f"{index}. {item['title']} [{item['type'] or 'unknown'}] score={item['score']}")
            print(f"   {item['path']}")
            if item.get("snippet"):
                print(f"   {item['snippet']}")
    elif command == "audit":
        print(f"Audited {result['notes']} notes; found {result['issue_count']} issues.")
        for issue in result["issues"]:
            print(f"[{issue['severity']}] {issue['code']} {issue['path']}: {issue['message']}")
    elif command == "observe":
        print(f"Observation appended to {result['log']}")
    elif command == "capture":
        print(f"Capture {result['mode']}: {result['path']}")
        if result["mode"] == "dry-run":
            print(result["preview"])
    elif command == "migrate":
        print(f"Migration {result['mode']}: {result['change_count']} changes, {result['skip_count']} skipped.")
        for change in result["changes"]:
            marker = "applied" if change["applied"] else "planned"
            print(f"[{marker}] {change['path']}: {change['from']} -> {change['to']}")
        for skipped in result["skipped"]:
            print(f"[skipped] {skipped['path']}: {skipped['reason']}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


def _add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", help="Path to .gark/config.toml")
    parser.add_argument("--vault", help="Override the configured vault root")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Emit UTF-8 JSON")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gark", description="Local retrieval and governance for a G-Ark vault")
    subparsers = parser.add_subparsers(dest="command", required=True)

    index_parser = subparsers.add_parser("index", help="Rebuild the local SQLite FTS5 index")
    _add_common_options(index_parser)
    index_parser.add_argument("--rebuild", action="store_true", help="Accepted for explicit full-rebuild workflows")

    search_parser = subparsers.add_parser("search", help="Search titles, properties, MOCs, summaries, and body text")
    search_parser.add_argument("query")
    search_parser.add_argument("--limit", type=int)
    search_parser.add_argument("--expand-links", action="store_true", help="Include one-hop Wikilink neighbors")
    _add_common_options(search_parser)

    audit_parser = subparsers.add_parser("audit", help="Audit Schema, routes, AI review state, links, and graph coverage")
    _add_common_options(audit_parser)

    observe_parser = subparsers.add_parser("observe", help="Append a retrieval or capture observation to JSONL")
    observe_parser.add_argument("--event", required=True)
    observe_parser.add_argument("--reason")
    query_group = observe_parser.add_mutually_exclusive_group()
    query_group.add_argument("--query")
    query_group.add_argument("--no-query", action="store_true", help="Do not persist raw query text")
    observe_parser.add_argument("--hit", action="append")
    observe_parser.add_argument("--used", action="append")
    observe_parser.add_argument("--outcome")
    observe_parser.add_argument("--metadata-json")
    _add_common_options(observe_parser)

    capture_parser = subparsers.add_parser("capture", help="Preview or create one AI candidate in the Inbox")
    capture_parser.add_argument("--title", required=True)
    content_group = capture_parser.add_mutually_exclusive_group(required=True)
    content_group.add_argument("--content")
    content_group.add_argument("--content-file")
    capture_parser.add_argument("--topic", action="append")
    capture_parser.add_argument("--source-session", help="Session ID; required with --apply to enforce one candidate per session")
    capture_parser.add_argument("--apply", action="store_true", help="Write the candidate; default is dry-run")
    _add_common_options(capture_parser)

    migrate_parser = subparsers.add_parser("migrate", help="Preview or apply explicit legacy status mappings")
    migration_mode = migrate_parser.add_mutually_exclusive_group()
    migration_mode.add_argument("--dry-run", action="store_true", help="Preview changes (default)")
    migration_mode.add_argument("--apply", action="store_true", help="Apply safe, explicit changes")
    _add_common_options(migrate_parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        settings = load_settings(args)
        handlers = {
            "index": command_index,
            "search": command_search,
            "audit": command_audit,
            "observe": command_observe,
            "capture": command_capture,
            "migrate": command_migrate,
        }
        result = handlers[args.command](args, settings)
        if args.json_output:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            _print_text(result)
        return 0
    except (GarkError, OSError, sqlite3.Error) as exc:
        print(f"gark: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
