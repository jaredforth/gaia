import json
import tempfile
from pathlib import Path

import gaia


def test_dedupes_requests_and_estimates():
    u = {"input_tokens": 1000, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 1000}
    rec = lambda rid, model: json.dumps({"requestId": rid, "timestamp": "2026-01-01T00:00:00Z",
                                         "message": {"model": model, "usage": u}})
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "s.jsonl").write_text("\n".join([rec("a", "claude-opus-5-5"), rec("a", "claude-opus-5-5"),
                                                    rec("b", "claude-haiku-5-5"), "not json"]))
        totals = gaia.load(Path(d))
    assert totals["claude-opus-5-5"]["requests"] == 1  # duplicate content-block line ignored
    assert totals["claude-opus-5-5"]["output_tokens"] == 1000
    # opus: 1.2 * 3 Wh/1k * (1000 out + 0.02 * 1000 in) = 3.672 Wh
    assert abs(gaia.wh("claude-opus-5-5", totals["claude-opus-5-5"]) - 3.672) < 1e-9
    assert gaia.wh("claude-haiku-5-5", totals["claude-haiku-5-5"]) < gaia.wh("claude-opus-5-5", totals["claude-opus-5-5"])


if __name__ == "__main__":
    test_dedupes_requests_and_estimates()
    print("ok")
