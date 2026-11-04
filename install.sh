#!/bin/sh
# Link the gaia skill into every installed agent that supports Agent Skills.
# Claude Code users can instead install it as a plugin (see README).
set -e
src="$(cd "$(dirname "$0")" && pwd)/skills/gaia"
found=0
for home in "$HOME/.claude" "${CODEX_HOME:-$HOME/.codex}" "$HOME/.gemini" "$HOME/.cursor" "$HOME/.copilot"; do
  [ -d "$home" ] || continue
  mkdir -p "$home/skills"
  ln -sfn "$src" "$home/skills/gaia"
  echo "linked $home/skills/gaia"
  found=1
done
[ "$found" = 1 ] || echo "No supported agent found (Claude Code, Codex, Gemini CLI, Cursor, Copilot)."
