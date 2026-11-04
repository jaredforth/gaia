import json
import tempfile
from pathlib import Path

import gaia

U = {"input_tokens": 1000, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 1000}


def claude(rid, model):
    return json.dumps({"requestId": rid, "timestamp": "2026-01-01T00:00:00Z", "message": {"model": model, "usage": U}})


def test_reads_claude():
    with tempfile.TemporaryDirectory() as d:
        c = Path(d)
        (c / "s.jsonl").write_text("\n".join([claude("a", "claude-opus-5-5"), claude("a", "claude-opus-5-5"),
                                              claude("b", "claude-haiku-5-5"), "not json"]))
        totals = gaia.load(c)
    opus = totals["claude-opus-5-5"]
    assert opus["requests"] == 1  # duplicate content-block line ignored
    # opus: 1.2 * 3 Wh/1k * (1000 out + 0.02 * 1000 in) = 3.672 Wh
    assert abs(gaia.wh("claude-opus-5-5", opus) - 3.672) < 1e-9
    assert gaia.wh("claude-haiku-5-5", totals["claude-haiku-5-5"]) < gaia.wh("claude-opus-5-5", opus)

if __name__ == "__main__":
    test_reads_claude()
    print("ok")
