# Door/Key Prerequisite Pilot: Results

| model | input | class | visible bytes | finish_reason | completion_tokens | reasoning_tokens | response SHA-256 |
|---|---|---|---:|---|---:|---:|---|
| gpt-5.4-2026-03-05 | key | R | 4 | stop | 5 | 0 | bfca30232fb3f1597344ac29835fa75f83d69a505d5a8d41e80b781c231ea1fb |
| gpt-5.4-2026-03-05 | lock | V0 | 0 | stop | 3 | 0 | 52a17f8562c28382458cea535e91dbc14790ce8c7d1c00198f2cd58b46c45a28 |
| gpt-5.2-2025-12-11 | key | R | 16 | stop | 7 | 0 | 6822dd40e274d23a2955ec30cf39abf822c5c322ea3bceae2fe83ad0c8fe9205 |
| gpt-5.2-2025-12-11 | lock | V0 | 0 | stop | 3 | 0 | 0a5ee7e7c8e103f11bb95783fbf68ae9663b22087ba0494018135ae87f11f5b5 |
| claude-opus-4-6 | key | R | 1338 | end_turn | 296 | not reported | b38ef1774479fea956c1230c958467c2e56321aa17b88b281a4d7e1063961fca |
| claude-opus-4-6 | lock | R | 1291 | end_turn | 378 | not reported | dae96ae39b6055904857167baa9004eeb4840afce01f85e1a11e3c45f907e13f |

Each row represents one archived response. Model identifiers are provider-returned identifiers. Visible bytes are the UTF-8 byte length of the unmodified answer text. Anthropic `output_tokens` is displayed as `completion_tokens`; absent reasoning-token counts are not reported, not zero.
