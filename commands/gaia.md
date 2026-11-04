---
description: Show the estimated environmental footprint of your Claude Code usage
argument-hint: "[--days N]"
allowed-tools: Bash(python3:*)
---
!`python3 "${CLAUDE_PLUGIN_ROOT}/gaia.py" $ARGUMENTS`

Show the report above to the user as-is. Do not add commentary unless they ask.
