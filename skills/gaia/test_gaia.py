import json
import tempfile
from pathlib import Path

import gaia

U = {"input_tokens": 1000, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 1000}


def claude(rid, model):
    return json.dumps({"requestId": rid, "timestamp": "2026-01-01T00:00:00Z", "message": {"model": model, "usage": U}})


def codex_tokens(total, last):
    return json.dumps({"timestamp": "2026-01-01T00:00:00Z", "type": "event_msg",
                       "payload": {"type": "token_count", "info": {"total_token_usage": total, "last_token_usage": last}}})


def test_reads_claude_and_codex():
    with tempfile.TemporaryDirectory() as d:
        c, x = Path(d) / "claude", Path(d) / "codex" / "sessions"
        c.mkdir(); x.mkdir(parents=True)
        (c / "s.jsonl").write_text("\n".join([claude("a", "claude-opus-5-5"), claude("a", "claude-opus-5-5"),
                                              claude("b", "claude-haiku-5-5"), "not json"]))
        turn = {"input_tokens": 1000, "cached_input_tokens": 400, "output_tokens": 100}
        (x / "r.jsonl").write_text("\n".join([
            json.dumps({"type": "turn_context", "payload": {"model": "gpt-5.4"}}),
            json.dumps({"type": "event_msg", "payload": {"type": "token_count", "info": None}}),
            codex_tokens(turn, turn), codex_tokens(turn, turn)]))  # repeated event counted once
        totals = gaia.load(c, Path(d) / "codex")
    opus = totals["claude-opus-5-5"]
    assert opus["requests"] == 1  # duplicate content-block line ignored
    # opus: 1.2 * 3 Wh/1k * (1000 out + 0.02 * 1000 in) = 3.672 Wh
    assert abs(gaia.wh("claude-opus-5-5", opus) - 3.672) < 1e-9
    assert gaia.wh("claude-haiku-5-5", totals["claude-haiku-5-5"]) < gaia.wh("claude-opus-5-5", opus)
    g = totals["gpt-5.4"]
    assert (g["requests"], g["input_tokens"], g["cache_read_input_tokens"], g["output_tokens"]) == (1, 600, 400, 100)
    assert gaia.wh_per_1k("gemini-2.5-pro") == gaia.DEFAULT_WH_PER_1K_OUTPUT  # "mini" must not match "gemini"


if __name__ == "__main__":
    test_reads_claude_and_codex()
    print("ok")
