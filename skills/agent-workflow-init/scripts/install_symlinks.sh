#!/bin/bash
# Create symlinks from ~/.codex/skills/ to ~/.claude/skills/ for Claude Code support.
#
# Usage:
#   bash install_symlinks.sh

set -euo pipefail

CODEX_SKILLS_DIR="$HOME/.codex/skills"
CLAUDE_SKILLS_DIR="$HOME/.claude/skills"

SKILLS=("agent-workflow-init" "agent-workflow-start")

# Create Claude skills directory if it doesn't exist
mkdir -p "$CLAUDE_SKILLS_DIR"

for skill in "${SKILLS[@]}"; do
    source="$CODEX_SKILLS_DIR/$skill"
    target="$CLAUDE_SKILLS_DIR/$skill"

    if [ ! -d "$source" ]; then
        echo "SKIP: $source does not exist"
        continue
    fi

    if [ -L "$target" ]; then
        existing=$(readlink "$target")
        if [ "$existing" = "$source" ]; then
            echo "OK: $target already points to $source"
            continue
        else
            echo "UPDATE: $target points to $existing, updating to $source"
            rm "$target"
        fi
    elif [ -d "$target" ]; then
        echo "SKIP: $target exists as a directory (not a symlink). Remove it manually if you want to replace it."
        continue
    fi

    ln -s "$source" "$target"
    echo "LINKED: $target -> $source"
done

echo ""
echo "Done. Restart Claude Code to pick up the new skills."
