# Door/Key Prerequisite Pilot: Raw Receipts, October 27, 2026

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
