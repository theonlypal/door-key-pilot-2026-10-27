#!/usr/bin/env python3
"""Offline classification, table generation, and archive verification."""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODELS = ("gpt-5.4-2026-03-05", "gpt-5.2", "claude-opus-4-6")
ARMS = (("match", "key"), ("mismatch", "lock"))
PILOT = "Exploratory pilot, one trial per cell, no ablation arm, no preregistration."
REPO = "https://github.com/theonlypal/door-key-pilot-2026-10-27"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def decode(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique)


def classify(text, finish, present=True, refusal=False, tools=False):
    if refusal:
        return "RF"
    if finish in ("content_filter", "refusal"):
        return "SB" if finish == "content_filter" else "RF"
    if tools:
        return "TC"
    if text:
        return "R" if any(not c.isspace() for c in text) else "NV"
    if finish in ("stop", "end_turn"):
        return "V0" if present else "V2"
    if finish in ("length", "max_tokens"):
        return "V1"
    return "VU"


def derive():
    rows = []
    systems = set()
    expected_files = set()
    for requested in MODELS:
        for arm, expected_input in ARMS:
            directory = ROOT / "receipts" / arm / requested
            request_path, response_path = directory / "request.json", directory / "response.bin"
            expected_files.update((request_path, response_path))
            request_raw, response_raw = request_path.read_bytes(), response_path.read_bytes()
            request, response = decode(request_raw), decode(response_raw)
            assert request["model"] == requested
            assert "tools" not in request and "temperature" not in request
            if requested.startswith("gpt"):
                assert [m["role"] for m in request["messages"]] == ["system", "user"]
                system, user = [m["content"] for m in request["messages"]]
                assert request["max_completion_tokens"] == 32768
                assert request["reasoning_effort"] == "none" and request["stream"] is False
                assert response["object"] == "chat.completion" and len(response["choices"]) == 1
                choice = response["choices"][0]
                message = choice["message"]
                text = message["content"]
                assert isinstance(text, str)
                finish = choice["finish_reason"]
                usage = response["usage"]
                completion = usage["completion_tokens"]
                reasoning = usage.get("completion_tokens_details", {}).get("reasoning_tokens")
                category = classify(text, finish, refusal=bool(message.get("refusal")), tools=bool(message.get("tool_calls")))
                response_time = datetime.fromtimestamp(response["created"], timezone.utc).isoformat().replace("+00:00", "Z")
                assert response["model"] == ("gpt-5.2-2025-12-11" if requested == "gpt-5.2" else requested)
            else:
                assert len(request["messages"]) == 1 and request["messages"][0]["role"] == "user"
                system, user = request["system"], request["messages"][0]["content"]
                assert request["max_tokens"] == 500 and "thinking" not in request
                assert response["type"] == "message" and response["model"] == requested
                blocks = response["content"]
                assert all(b["type"] == "text" for b in blocks)
                text = "".join(b["text"] for b in blocks)
                finish = response["stop_reason"]
                completion = response["usage"]["output_tokens"]
                reasoning = response["usage"].get("output_tokens_details", {}).get("thinking_tokens")
                category = classify(text, finish, present=bool(blocks))
                response_time = None
            assert user == expected_input
            systems.add(system)
            rows.append({
                "record_type": "derived_response_classification",
                "arm": arm, "requested_model": requested, "returned_model": response["model"],
                "input": user, "class": category, "visible_bytes": len(text.encode("utf-8")),
                "finish_reason": finish, "completion_tokens": completion, "reasoning_tokens": reasoning,
                "response_id": response["id"], "request_time_utc": None,
                "provider_response_created_utc": response_time,
                "request_file": request_path.relative_to(ROOT).as_posix(),
                "request_sha256": sha(request_raw),
                "response_file": response_path.relative_to(ROOT).as_posix(),
                "response_sha256": sha(response_raw),
            })
    assert set(p for p in (ROOT / "receipts").rglob("*") if p.is_file()) == expected_files
    assert len(systems) == 1
    return rows, systems.pop()


def display(value):
    return "not reported" if value is None else str(value)


def table(rows):
    columns = ["returned_model", "input", "class", "visible_bytes", "finish_reason", "completion_tokens", "reasoning_tokens", "response_sha256"]
    header = "| model | input | class | visible bytes | finish_reason | completion_tokens | reasoning_tokens | response SHA-256 |\n"
    header += "|---|---|---|---:|---|---:|---:|---|\n"
    return header + "".join("| " + " | ".join(display(r[k]) for k in columns) + " |\n" for r in rows)


def render(rows):
    return "# Door/Key Prerequisite Pilot: Results\n\n" + table(rows) + "\nEach row represents one archived response. Model identifiers are provider-returned identifiers. Visible bytes are the UTF-8 byte length of the unmodified answer text. Anthropic `output_tokens` is displayed as `completion_tokens`; absent reasoning-token counts are not reported, not zero.\n"


def prompts(system):
    out = "# Prompts\n\nText values have no trailing newline.\n"
    for title, value in (("System", system), ("Matched user input", "key"), ("Mismatched user input", "lock")):
        raw = value.encode("utf-8")
        out += "\n## " + title + "\n\n```text\n" + value + "\n```\n\nUTF-8 hex: `" + raw.hex() + "`\n\nSHA-256: `" + sha(raw) + "`\n"
    return out


def protocol(rows):
    out = """# Protocol

Exploratory pilot, one trial per cell, no ablation arm, no preregistration.

## Requests

Each archived request contains one user message and the system string in PROMPTS.md, with no preceding conversation or tools.

| Endpoint | Requested model | Token ceiling | Reasoning setting | Temperature policy | Stream field |
|---|---|---|---|---|---|
| https://api.openai.com/v1/chat/completions | gpt-5.4-2026-03-05 | max_completion_tokens: 32768 | reasoning_effort: none | omitted, provider default | false |
| https://api.openai.com/v1/chat/completions | gpt-5.2 | max_completion_tokens: 32768 | reasoning_effort: none | omitted, provider default | false |
| https://api.anthropic.com/v1/messages | claude-opus-4-6 | max_tokens: 500 | thinking and reasoning_effort omitted | omitted, provider default | omitted |

Endpoints are specified by the archived source runner, `scripts/newvoids.py`, in source commit `67e2a779244da426838e4db9885b774654903a15`. The Anthropic version header in that runner is `2023-06-01`. The receipt bodies contain no saved HTTP headers or HTTP status metadata.

## Identifiers and UTC metadata

Request dispatch timestamps were not saved. OpenAI `created` values below are provider response creation timestamps, not request dispatch times. Anthropic response bodies contain no timestamp. Filesystem modification times are not used as request timestamps.

| Requested model | Returned model | Input | Request UTC | Provider response created UTC | Response ID |
|---|---|---|---|---|---|
"""
    for r in rows:
        out += "| " + " | ".join(display(r[k]) for k in ("requested_model", "returned_model", "input", "request_time_utc", "provider_response_created_utc", "response_id")) + " |\n"
    out += """
## Measurements

V0 denotes a present empty answer string with normal-stop metadata. R denotes nonempty visible answer text. These six bodies contain no tool calls, refusal payloads, or safety-block termination. The two empty strings are present OpenAI `content` fields, each with `finish_reason: stop`. Provider-reported termination metadata does not expose native EOS token IDs or logits.

Visible bytes are the length of answer text encoded as UTF-8, without stripping whitespace or normalization. Both nonempty Anthropic responses contain ordinary visible text. OpenAI `completion_tokens` and Anthropic `output_tokens` are displayed in the same completion-token column; absent Anthropic reasoning-token counts remain null.

## Evidence integrity

The twelve files in `receipts/` are byte-identical to the N4_door_key subtree of source commit `67e2a779244da426838e4db9885b774654903a15`. Original filenames are `request.json` and `response.bin`. No attempt JSON, per-trial classification JSON, or hash manifest existed in that subtree. `classifications.json` is a derived analysis record, not a provider receipt; every entry binds both raw files by SHA-256. Its six labels agree with the N4 entries in the source run's aggregate summary.

`SHA256SUMS` covers every artifact file except itself and Git's internal metadata. Its digest and the release tar digest are recorded in the publication metadata. Hash agreement establishes byte identity, not independent authentication by the provider.

## Offline verification

```sh
python3 -B results.py --check
shasum -a 256 -c SHA256SUMS
```

`python3 -B results.py` reads `classifications.json`, checks each entry against the raw response, and writes `RESULTS.md`. No network access or provider credentials are used.
"""
    return out


def readme():
    return """# Door/Key Prerequisite Pilot: Raw Receipts, October 27, 2026

Rayan Pal

Observation date: October 27, 2026 (UTC).

GPT-5.4: `key` returned `🚪`; `lock` returned V0, zero answer bytes.  
GPT-5.2: `key` returned `[Door unlocked.]`; `lock` returned V0, zero answer bytes.  
Claude Opus 4.6: both `key` and `lock` returned visible text.

Exploratory pilot, one trial per cell, no ablation arm, no preregistration.

The exact English system prompt is preserved in [PROMPTS.md](PROMPTS.md). The six-row measurements and response hashes are in [RESULTS.md](RESULTS.md). Requested and returned model identities, settings, timestamp availability, and measurement definitions are in [PROTOCOL.md](PROTOCOL.md).

## Layout

```text
receipts/{match,mismatch}/{requested_model}/
  request.json
  response.bin
classifications.json
PROMPTS.md
PROTOCOL.md
RESULTS.md
results.py
SHA256SUMS
LICENSE
```

## Verify

```sh
python3 -B results.py --check
shasum -a 256 -c SHA256SUMS
```

Repository: https://github.com/theonlypal/door-key-pilot-2026-10-27

License: Creative Commons Attribution 4.0 International (CC-BY-4.0).
"""


def artifact_files():
    return sorted(p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.relative_to(ROOT).parts and "__pycache__" not in p.relative_to(ROOT).parts and p.name != "SHA256SUMS")


def manifest():
    return "".join(sha(p.read_bytes()) + "  " + p.relative_to(ROOT).as_posix() + "\n" for p in artifact_files())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--derive", action="store_true", help="Create derived analysis files only when absent.")
    parser.add_argument("--manifest", action="store_true", help="Write SHA256SUMS.")
    parser.add_argument("--check", action="store_true", help="Read-only verification of all artifact files.")
    args = parser.parse_args()
    rows, system = derive()
    files = {"PROMPTS.md": prompts(system), "PROTOCOL.md": protocol(rows), "README.md": readme(), "RESULTS.md": render(rows),
             "classifications.json": json.dumps(rows, ensure_ascii=False, indent=2) + "\n"}
    if args.derive:
        assert all(not (ROOT / name).exists() for name in files), "Derived files already exist"
        for name, value in files.items():
            (ROOT / name).write_text(value, encoding="utf-8")
    else:
        saved = decode((ROOT / "classifications.json").read_bytes())
        assert saved == rows, "Classification or raw receipt mismatch"
        if args.check:
            for name, value in files.items():
                assert (ROOT / name).read_bytes() == value.encode("utf-8"), "Derived file mismatch: " + name
            assert (ROOT / "SHA256SUMS").read_text(encoding="utf-8") == manifest(), "Manifest mismatch"
            print("VERIFIED: 6 responses; 12 raw receipt hashes; classifications, prompts, protocol, results, and manifest match.")
        elif not args.manifest:
            (ROOT / "RESULTS.md").write_text(render(saved), encoding="utf-8")
    if args.manifest:
        (ROOT / "SHA256SUMS").write_text(manifest(), encoding="utf-8")


if __name__ == "__main__":
    main()
