<p align="center"><img src=".claude-plugin/icon.png" alt="gaia leaf logo" width="128"></p>

# gaia

gaia is a Claude Code plugin that estimates the energy, carbon and water footprint of your
Claude Code usage. It reads the token counts that Claude Code already saves in your local
transcripts (`~/.claude/projects/**/*.jsonl`), so it needs no hooks, no network access and no setup.

## Install

```
/plugin marketplace add jaredforth/gaia
/plugin install gaia@gaia
```

## Use

Ask Claude "what is my AI footprint?", or run `/gaia` (`/gaia --days 7` for the last week).
You can also run the script directly: `python3 skills/gaia/gaia.py --days 1`.

## Accuracy

Anthropic does not publish per-token energy figures. The numbers are rough estimates from
public research, set per model tier. Edit the constants at the top of `skills/gaia/gaia.py` to
change the energy per token, PUE, grid carbon intensity or water use.

## License

AGPL-3.0-or-later. See `LICENSE`.
