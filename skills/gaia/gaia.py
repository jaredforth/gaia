#!/usr/bin/env python3
"""gaia: estimate the environmental footprint of Claude Code usage from local transcripts."""
import argparse
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Calibration knobs. Anthropic publishes no per-token energy data, so these are rough
# public-literature estimates (Epoch AI, Google's Gemini disclosure, Luccioni et al.).
# ponytail: tier-level guesses; replace with real per-model figures if they get published.
# First matching substring wins; anything unmatched is treated as a mid-size model.
WH_PER_1K_OUTPUT = {"haiku": 0.3, "opus": 3.0, "fable": 3.0, "sonnet": 1.0}
DEFAULT_WH_PER_1K_OUTPUT = 1.0
INPUT_FACTOR = 0.02       # one fresh input token ~ 1/50 of an output token (prefill is batched)
CACHE_READ_FACTOR = 0.1   # cached input skips most prefill compute
PUE = 1.2                 # datacenter overhead (cooling, power conversion)
G_CO2_PER_KWH = 400       # rough global grid average
L_WATER_PER_KWH = 1.1     # on-site cooling water
PHONE_CHARGE_WH = 15
CAR_G_CO2_PER_KM = 170


def wh_per_1k(model):
    return next((v for k, v in WH_PER_1K_OUTPUT.items() if k in model), DEFAULT_WH_PER_1K_OUTPUT)


def ts(s):
    return datetime.fromisoformat((s or "1970-01-01T00:00:00Z").replace("Z", "+00:00"))


def new_totals():
    return defaultdict(lambda: defaultdict(int))


def add(totals, model, fresh_in, cache_write, cache_read, out):
    t = totals[model]
    t["requests"] += 1
    t["input_tokens"] += fresh_in
    t["cache_creation_input_tokens"] += cache_write
    t["cache_read_input_tokens"] += cache_read
    t["output_tokens"] += out


def load_claude(root, totals, since=None):
    """Claude Code transcripts; one response spans several lines, so dedupe by request."""
    seen = set()
    for path in root.rglob("*.jsonl"):
        with open(path, errors="ignore") as f:
            for line in f:
                if '"usage"' not in line:
                    continue
                try:
                    d = json.loads(line)
                    msg, usage = d["message"], d["message"]["usage"]
                except (ValueError, KeyError, TypeError):
                    continue
                key = d.get("requestId") or msg.get("id")
                if key in seen:
                    continue
                seen.add(key)
                if since and ts(d.get("timestamp")) < since:
                    continue
                g = lambda k: usage.get(k) or 0
                add(totals, msg.get("model", "unknown"), g("input_tokens"), g("cache_creation_input_tokens"),
                    g("cache_read_input_tokens"), g("output_tokens"))


def load(claude_dir, since=None):
    totals = new_totals()
    load_claude(claude_dir, totals, since)
    return totals


def wh(model, t):
    out_rate = wh_per_1k(model) / 1000
    fresh_in = t["input_tokens"] + t["cache_creation_input_tokens"]
    return PUE * out_rate * (t["output_tokens"] + INPUT_FACTOR * fresh_in + INPUT_FACTOR * CACHE_READ_FACTOR * t["cache_read_input_tokens"])


def report(totals, label):
    rows = [(m, t, wh(m, t)) for m, t in totals.items() if t["requests"] and m != "<synthetic>"]
    if not rows:
        return f"gaia: no Claude Code usage found ({label})."
    rows.sort(key=lambda r: -r[2])
    lines = [f"🌍 gaia — Claude Code footprint ({label})", "",
             f"{'model':<28}{'requests':>10}{'in tokens':>14}{'out tokens':>13}{'energy Wh':>12}"]
    for m, t, e in rows:
        tin = t["input_tokens"] + t["cache_creation_input_tokens"] + t["cache_read_input_tokens"]
        lines.append(f"{m:<28}{t['requests']:>10,}{tin:>14,}{t['output_tokens']:>13,}{e:>12.1f}")
    total = sum(r[2] for r in rows)
    co2 = total / 1000 * G_CO2_PER_KWH
    lines += ["",
              f"Energy  {total:,.1f} Wh  (~{total / PHONE_CHARGE_WH:,.1f} phone charges)",
              f"Carbon  {co2:,.1f} g CO2e  (~{co2 / CAR_G_CO2_PER_KM:,.2f} km driven)",
              f"Water   {total / 1000 * L_WATER_PER_KWH * 1000:,.0f} mL",
              "", "Rough estimates; Anthropic does not publish per-token energy data. Tune constants in gaia.py."]
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--days", type=float, help="only count the last N days (default: all time)")
    claude = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
    p.add_argument("--claude-dir", type=Path, default=claude / "projects", help="Claude Code transcripts")
    a = p.parse_args(argv)
    since = datetime.now(timezone.utc) - timedelta(days=a.days) if a.days else None
    print(report(load(a.claude_dir, since), f"last {a.days:g} days" if a.days else "all time"))


if __name__ == "__main__":
    main()
