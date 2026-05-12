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

info "Updating vault-level Codex skills in $VAULT_PATH"

for skill in g-ark-vault-steward g-ark-source-distiller; do
  mkdir -p "$VAULT_PATH/.codex/skills/$skill"
  download_file "$RAW_BASE/setup/skills/$skill/SKILL.md" "$VAULT_PATH/.codex/skills/$skill/SKILL.md"
  info "Updated $skill"
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

info "Done. Restart Obsidian or refresh Claudian Codex Skills."
