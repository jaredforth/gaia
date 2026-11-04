<p align="center"><img src=".claude-plugin/icon.png" alt="gaia leaf logo" width="128"></p>

# gaia

gaia estimates the energy, carbon and water footprint of your AI coding-agent usage.
It reads the token counts that your agents already save on your computer, so it needs no
hooks, no network access and no API keys.

## Install

gaia is an [Agent Skill](https://agentskills.io), so the same folder (`skills/gaia`) works in
every agent that supports skills.

**Claude Code** (as a plugin):

```
/plugin marketplace add jaredforth/gaia
/plugin install gaia@gaia
```

**Claude Code, Codex, Gemini CLI, Cursor and GitHub Copilot** (as a skill):

```
git clone https://github.com/jaredforth/gaia ~/.gaia && ~/.gaia/install.sh
```

`install.sh` links the skill into each agent it finds. Run `git pull` in `~/.gaia` to update.
If you use the Claude Code plugin, you do not also need the skill link for Claude Code.

## Use

Ask your agent "what is my AI footprint?", or run `/gaia` (`/gaia --days 7` for the last week).
You can also run the script directly: `python3 skills/gaia/gaia.py --days 1`.

## What is counted

| Agent | Counted | Source |
|---|---|---|
| Claude Code | Yes | `~/.claude/projects/**/*.jsonl` |
| Codex CLI | Yes | `~/.codex/sessions`, `~/.codex/archived_sessions` |
| Gemini CLI, Cursor, Copilot | No | These agents do not save token counts on your computer |
| Web chat (claude.ai, ChatGPT, Gemini) | No | No local data |

gaia reports the usage of every agent it can read, no matter which agent runs the skill.

## Accuracy

AI providers do not publish per-token energy figures. The numbers are rough estimates from
public research, set per model size. Edit the constants at the top of `skills/gaia/gaia.py` to
change the energy per token, PUE, grid carbon intensity or water use.

## License

AGPL-3.0-or-later. See `LICENSE`.
