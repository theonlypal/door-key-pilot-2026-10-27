# Protocol

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
| gpt-5.4-2026-03-05 | gpt-5.4-2026-03-05 | key | not reported | 2026-10-27T06:33:08Z | chatcmpl-EdV24QsfMxKjTCgTW4N3y1YP6UmIY |
| gpt-5.4-2026-03-05 | gpt-5.4-2026-03-05 | lock | not reported | 2026-10-27T06:33:09Z | chatcmpl-EdV25lP4pzdd4Pfsus2H7Y99dXawv |
| gpt-5.2 | gpt-5.2-2025-12-11 | key | not reported | 2026-10-27T06:33:10Z | chatcmpl-EdV26DarQ8iOkhUaaUCp2oswLKJkf |
| gpt-5.2 | gpt-5.2-2025-12-11 | lock | not reported | 2026-10-27T06:33:10Z | chatcmpl-EdV26zC8cNAIXcRf8lqM694mBZRlJ |
| claude-opus-4-6 | claude-opus-4-6 | key | not reported | not reported | msg_011CgSGtpYbQpaGZvrsT6GTS |
| claude-opus-4-6 | claude-opus-4-6 | lock | not reported | not reported | msg_011CgSGtuNoeB21r1FDcgaMW |

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
