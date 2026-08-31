#!/usr/bin/env bash
set -euo pipefail

VAULT_PATH="${VAULT_PATH:-$HOME/Documents/G-Ark}"
BRANCH="${BRANCH:-main}"
REPO_RAW_BASE="${REPO_RAW_BASE:-https://raw.githubusercontent.com/Geniusay/ObsiChan}"
CLAUDIAN_VERSION="${CLAUDIAN_VERSION:-2.0.11}"
UPDATE_CLAUDIAN="${UPDATE_CLAUDIAN:-0}"

RAW_BASE="$REPO_RAW_BASE/$BRANCH"

info() {
  printf '[ObsiChan Update] %s\n' "$1"
}

download_file() {
  local url="$1"
  local out="$2"
  mkdir -p "$(dirname "$out")"
  curl -fsSL "$url" -o "$out"
}

case "$VAULT_PATH" in
  "~") VAULT_PATH="$HOME" ;;
  "~/"*) VAULT_PATH="$HOME/${VAULT_PATH#~/}" ;;
esac

if [ ! -d "$VAULT_PATH" ]; then
  printf 'Vault path does not exist: %s\n' "$VAULT_PATH" >&2
  exit 1
fi

VAULT_PATH="$(cd "$VAULT_PATH" && pwd -P)"

info "Updating the unified G-Ark Codex skill in $VAULT_PATH"

GARK_ROOT="$VAULT_PATH/.gark"
SKILL_ROOT="$GARK_ROOT/skill"
SKILL_FILES=(
  "SKILL.md"
  "agents/openai.yaml"
  "references/archive.md"
  "references/audit.md"
  "references/capture.md"
  "references/connect.md"
  "references/distill.md"
  "references/retrieve.md"
  "references/review.md"
  "references/session.md"
  "references/write-safety.md"
  "scripts/gark.py"
  "scripts/install-global.ps1"
)
for relative_path in "${SKILL_FILES[@]}"; do
  download_file "$RAW_BASE/setup/skills/g-ark/$relative_path" "$SKILL_ROOT/$relative_path"
done
info "Updated g-ark"

if [ ! -f "$GARK_ROOT/config.toml" ]; then
  download_file "$RAW_BASE/setup/gark/config.toml" "$GARK_ROOT/config.toml"
  info "Created the default relative .gark/config.toml"
fi

if [ ! -f "$VAULT_PATH/00_System/GARK_SCHEMA.json" ]; then
  download_file "$RAW_BASE/setup/gark/GARK_SCHEMA.json" "$VAULT_PATH/00_System/GARK_SCHEMA.json"
  info "Installed the canonical GARK_SCHEMA.json"
fi

mkdir -p "$VAULT_PATH/.codex/skills"
SKILL_LINK="$VAULT_PATH/.codex/skills/g-ark"
if [ ! -e "$SKILL_LINK" ] && [ ! -L "$SKILL_LINK" ]; then
  ln -s ../../.gark/skill "$SKILL_LINK"
elif [ ! -L "$SKILL_LINK" ]; then
  printf 'Cannot enable g-ark because a non-link path already exists: %s\n' "$SKILL_LINK" >&2
  exit 1
else
  ln -sfn ../../.gark/skill "$SKILL_LINK"
fi

LEGACY_ROOT="$GARK_ROOT/legacy-skills"
for legacy_name in g-ark-vault-steward g-ark-source-distiller g-ark-session-distiller; do
  legacy_path="$VAULT_PATH/.codex/skills/$legacy_name"
  if [ -e "$legacy_path" ] || [ -L "$legacy_path" ]; then
    mkdir -p "$LEGACY_ROOT"
    backup_path="$LEGACY_ROOT/$legacy_name"
    if [ -e "$backup_path" ] || [ -L "$backup_path" ]; then
      printf 'Legacy backup already exists; leaving %s unchanged.\n' "$legacy_name" >&2
    else
      mv "$legacy_path" "$backup_path"
      info "Disabled legacy skill $legacy_name and preserved it under .gark/legacy-skills"
    fi
  fi
done

if [ ! -d "$VAULT_PATH/20_Sources/Collections" ]; then
  mkdir -p "$VAULT_PATH/20_Sources/Collections"
  info "Created 20_Sources/Collections for resource-list sources"
fi

if [ "$UPDATE_CLAUDIAN" = "1" ]; then
  info "Updating Claudian plugin to $CLAUDIAN_VERSION"
  CLAUDIAN_BASE="https://github.com/YishenTu/claudian/releases/download/$CLAUDIAN_VERSION"
  download_file "$CLAUDIAN_BASE/main.js" "$VAULT_PATH/.obsidian/plugins/claudian/main.js"
  download_file "$CLAUDIAN_BASE/manifest.json" "$VAULT_PATH/.obsidian/plugins/claudian/manifest.json"
  download_file "$CLAUDIAN_BASE/styles.css" "$VAULT_PATH/.obsidian/plugins/claudian/styles.css"
fi

info "Done. Existing configuration was preserved. Restart Obsidian or refresh Claudian Codex Skills."
