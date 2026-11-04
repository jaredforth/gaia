# gaia

A Claude Code plugin that estimates the energy, carbon and water footprint of your AI usage.
It reads the token counts that Claude Code already records in your local transcripts
(`~/.claude/projects/**/*.jsonl`), so it needs no hooks, no network and no setup.

## Install

```
/plugin marketplace add /path/to/gaia
/plugin install gaia@gaia
```

## Use

```
/gaia            # all time
/gaia --days 7   # last week
```

You can also run it directly: `python3 gaia.py --days 1`.

## Accuracy

Anthropic does not publish per-token energy figures. The numbers are rough estimates
from public research, per model tier. Edit the constants at the top of `gaia.py` to
change the energy per token, PUE, grid carbon intensity or water use.

## License

AGPL-3.0-or-later. See `LICENSE`.
