## sales

| System | n | Answer correct | Completed | Detect P | Detect R | Errors handled | Damage | Tool-call OK | Recovery | Approvals (med) | Latency s (med) | Tokens (med) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 stakeholder baseline | 20 | 0% | 95% | 0.80 | 0.61 | 19% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B1 fixed script | 20 | 70% | 100% | 0.74 | 0.80 | 80% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B2 single LLM call | 20 | 30% | 80% | 0.70 | 0.75 | 68% | 195 | n/a | n/a | n/a | 23.4 | 2,327 |
| DataSage (235B) | 20 | 85% | 100% | 0.84 | 0.85 | 89% | 0 | 100% | n/a | 3.0 | 152.3 | 56,024 |
| DataSage (30B) | 20 | 65% | 100% | 0.78 | 0.76 | 75% | 0 | 100% | 100% | 3.0 | 15.5 | 55,358 |
| DataSage, all risky fixes rejected | 10 | 30% | 100% | 0.88 | 0.86 | 47% | 0 | 100% | n/a | 2.5 | 171.4 | 50,410 |
| DataSage, no validator | 10 | 100% | 100% | 0.88 | 0.88 | 95% | 0 | 100% | n/a | 2.5 | 220.7 | 53,786 |
| DataSage (235B) + exclusion rule | 20 | 100% | 100% | 0.87 | 0.87 | 97% | 0 | 100% | n/a | 3.0 | 192.9 | 57,032 |
| DataSage (30B) + exclusion rule | 20 | 95% | 100% | 0.81 | 0.76 | 89% | 0 | 100% | n/a | 2.0 | 15.2 | 56,089 |
| DataSage (30B) + rule, strict approver | 20 | 100% | 100% | 0.83 | 0.79 | 92% | 0 | 100% | n/a | 2.0 | 14.3 | 54,481 |
| DataSage M3 (30B, default) | 20 | 100% | 100% | 0.82 | 0.80 | 91% | 0 | 100% | n/a | 2.0 | 15.1 | 61,636 |
| DataSage M3 (30B), Auto: every risky fix approved | 20 | 100% | 100% | 0.83 | 0.82 | 92% | 0 | 100% | n/a | 2.0 | 30.6 | 60,646 |

## penguins

| System | n | Answer correct | Completed | Detect P | Detect R | Errors handled | Damage | Tool-call OK | Recovery | Approvals (med) | Latency s (med) | Tokens (med) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 stakeholder baseline | 20 | 5% | 80% | 1.00 | 0.60 | 24% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B1 fixed script | 20 | 45% | 100% | 1.00 | 0.81 | 80% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B2 single LLM call | 20 | 45% | 100% | 0.86 | 0.74 | 79% | 25 | n/a | n/a | n/a | 27.9 | 2,478 |
| DataSage (235B) | 20 | 85% | 100% | 0.88 | 0.78 | 84% | 0 | 100% | n/a | 2.0 | 196.9 | 51,990 |
| DataSage (30B) | 20 | 70% | 100% | 0.88 | 0.79 | 85% | 0 | 100% | n/a | 2.0 | 14.9 | 57,050 |
| DataSage, all risky fixes rejected | 10 | 0% | 100% | 0.90 | 0.76 | 55% | 0 | 100% | n/a | 2.0 | 158.3 | 51,284 |
| DataSage, no validator | 10 | 80% | 100% | 0.90 | 0.76 | 83% | 0 | 100% | n/a | 2.0 | 194.3 | 51,371 |
| DataSage (235B) + exclusion rule | 20 | 100% | 100% | 0.88 | 0.77 | 96% | 0 | 100% | n/a | 2.0 | 215.0 | 52,428 |
| DataSage (30B) + exclusion rule | 20 | 85% | 100% | 0.88 | 0.77 | 92% | 0 | 100% | n/a | 2.0 | 15.1 | 55,282 |
| DataSage (30B) + rule, strict approver | 20 | 85% | 100% | 0.88 | 0.77 | 91% | 0 | 100% | n/a | 2.0 | 13.2 | 57,418 |
| DataSage M3 (30B, default) | 20 | 100% | 100% | 0.88 | 0.79 | 94% | 0 | 100% | n/a | 2.0 | 16.6 | 63,755 |
| DataSage M3 (30B), Auto: every risky fix approved | 20 | 90% | 100% | 0.88 | 0.79 | 93% | 0 | 100% | n/a | 2.0 | 41.8 | 62,889 |

## sales-heldout

| System | n | Answer correct | Completed | Detect P | Detect R | Errors handled | Damage | Tool-call OK | Recovery | Approvals (med) | Latency s (med) | Tokens (med) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 stakeholder baseline | 20 | 0% | 95% | 0.89 | 0.70 | 23% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B1 fixed script | 20 | 40% | 100% | 0.79 | 0.86 | 78% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B2 single LLM call | 20 | 85% | 100% | 0.79 | 0.77 | 86% | 2 | n/a | n/a | n/a | 27.3 | 2,214 |
| DataSage (235B) | 20 | 80% | 90% | 0.91 | 0.77 | 81% | 0 | 100% | 100% | 2.0 | 210.5 | 51,404 |
| DataSage (30B) | 20 | 95% | 100% | 0.86 | 0.76 | 84% | 0 | 100% | n/a | 3.0 | 14.8 | 61,856 |
| DataSage (235B) + exclusion rule | 20 | 80% | 95% | 0.89 | 0.77 | 86% | 0 | 99% | 100% | 2.5 | 156.3 | 54,037 |
| DataSage (30B) + exclusion rule | 20 | 90% | 100% | 0.88 | 0.89 | 88% | 0 | 100% | n/a | 2.0 | 15.1 | 65,225 |
| DataSage (30B) + rule, strict approver | 20 | 90% | 100% | 0.88 | 0.89 | 88% | 0 | 100% | n/a | 2.0 | 17.3 | 68,653 |
| DataSage M3 (30B, default) | 20 | 100% | 100% | 0.88 | 0.80 | 89% | 0 | 100% | n/a | 3.0 | 19.0 | 62,978 |
| DataSage M3 (30B), compact memory | 20 | 100% | 100% | 0.90 | 0.74 | 81% | 0 | 98% | 100% | 2.5 | 40.2 | 81,418 |
| DataSage M3 (30B), Auto: every risky fix approved | 20 | 100% | 100% | 0.88 | 0.80 | 89% | 0 | 100% | n/a | 2.0 | 15.9 | 64,388 |
| M3 without coverage check | 20 | 100% | 100% | 0.89 | 0.80 | 88% | 0 | 100% | n/a | 3.0 | 28.8 | 67,619 |
| M3 without validator | 20 | 95% | 100% | 0.88 | 0.83 | 87% | 0 | 100% | n/a | 2.0 | 27.5 | 65,152 |
| M3 without merge rule in prompt | 20 | 100% | 100% | 0.85 | 0.78 | 89% | 0 | 100% | n/a | 2.5 | 32.2 | 72,356 |
| M3, all risky fixes rejected | 20 | 5% | 100% | 0.82 | 0.91 | 35% | 0 | 100% | n/a | 3.0 | 38.4 | 79,004 |
| Model study: DataSage M3 with qwen3-30b-a3b-instruct-2507 | 20 | 100% | 100% | 0.88 | 0.81 | 87% | 0 | 100% | n/a | 2.0 | 31.3 | 61,850 |
| Model study: B2 single call with qwen3-30b-a3b-instruct-2507 | 20 | 65% | 100% | 0.60 | 0.68 | 74% | 135 | n/a | n/a | n/a | 14.3 | 2,330 |
| Model study: DataSage M3 with qwen3-235b-a22b-instruct-2507 | 20 | 100% | 100% | 0.89 | 0.80 | 93% | 0 | 100% | n/a | 2.0 | 171.0 | 53,625 |
| Model study: B2 single call with qwen3-235b-a22b-instruct-2507 | 20 | 75% | 95% | 0.75 | 0.78 | 83% | 3 | n/a | n/a | n/a | 26.8 | 2,240 |
| Model study: DataSage M3 with qwen3-30b-a3b-thinking-2507 | 20 | 100% | 100% | 0.90 | 0.20 | 68% | 0 | 100% | n/a | 2.0 | 123.2 | 37,446 |
| Model study: B2 single call with qwen3-30b-a3b-thinking-2507 | 20 | 75% | 95% | 0.84 | 0.47 | 58% | 39 | n/a | n/a | n/a | 60.7 | 5,598 |
| Model study: DataSage M3 with qwen3-235b-a22b-thinking-2507 | 20 | 100% | 100% | 0.85 | 0.44 | 70% | 0 | 100% | n/a | 2.0 | 804.4 | 47,960 |
| Model study: B2 single call with qwen3-235b-a22b-thinking-2507 | 20 | 35% | 35% | 1.00 | 0.16 | 65% | 1 | n/a | n/a | n/a | 2030.0 | 0 |
| Model study: DataSage M3 with qwen3-coder-30b-a3b-instruct | 20 | 100% | 100% | 0.89 | 0.85 | 94% | 0 | 98% | 100% | 2.5 | 105.0 | 81,036 |
| Model study: B2 single call with qwen3-coder-30b-a3b-instruct | 20 | 65% | 100% | 0.72 | 0.75 | 75% | 15 | n/a | n/a | n/a | 28.7 | 2,290 |
| Model study: DataSage M3 with qwen3-coder-next | 20 | 95% | 100% | 0.86 | 0.84 | 88% | 0 | 100% | n/a | 2.0 | 41.6 | 57,871 |
| Model study: B2 single call with qwen3-coder-next | 20 | 60% | 85% | 0.71 | 0.65 | 70% | 91 | n/a | n/a | n/a | 11.7 | 2,240 |
| Model study: DataSage M3 with qwen3-vl-32b-instruct | 20 | 100% | 100% | 0.87 | 0.77 | 85% | 0 | 100% | n/a | 2.0 | 234.6 | 53,000 |
| Model study: B2 single call with qwen3-vl-32b-instruct | 20 | 45% | 90% | 0.80 | 0.75 | 59% | 118 | n/a | n/a | n/a | 68.6 | 2,372 |
| Model study: DataSage M3 with qwen3-vl-32b-thinking | 14 | 100% | 100% | 0.92 | 0.39 | 64% | 0 | 100% | n/a | 2.0 | 256.3 | 37,550 |
| Model study: DataSage M3 with qwen35-27b | 20 | 95% | 100% | 0.87 | 0.62 | 77% | 0 | 100% | n/a | 2.0 | 66.3 | 62,358 |
| Model study: B2 single call with qwen35-27b | 20 | 75% | 100% | 0.93 | 0.88 | 79% | 11 | n/a | n/a | n/a | 93.5 | 3,654 |
| Model study: DataSage M3 with qwen35-122b-a10b | 20 | 100% | 100% | 0.82 | 0.66 | 88% | 0 | 100% | n/a | 2.0 | 96.5 | 64,662 |
| Model study: B2 single call with qwen35-122b-a10b | 20 | 70% | 95% | 0.89 | 0.81 | 75% | 41 | n/a | n/a | n/a | 78.1 | 3,422 |
| Model study: DataSage M3 with qwen35-397b-a17b | 20 | 100% | 100% | 0.87 | 0.67 | 94% | 0 | 100% | n/a | 2.0 | 103.7 | 45,662 |
| Model study: B2 single call with qwen35-397b-a17b | 20 | 85% | 100% | 0.90 | 0.78 | 69% | 17 | n/a | n/a | n/a | 73.1 | 3,068 |
| Model study: DataSage M3 with qwen36-27b | 20 | 90% | 100% | 0.84 | 0.53 | 71% | 0 | 97% | 100% | 2.0 | 69.0 | 47,742 |
| Model study: B2 single call with qwen36-27b | 20 | 70% | 95% | 0.92 | 0.91 | 68% | 7 | n/a | n/a | n/a | 110.9 | 6,168 |
| Model study: DataSage M3 with qwen36-35b-a3b | 20 | 95% | 100% | 0.83 | 0.74 | 89% | 0 | 100% | n/a | 2.0 | 49.7 | 45,168 |
| Model study: B2 single call with qwen36-35b-a3b | 20 | 75% | 100% | 0.96 | 0.52 | 56% | 93 | n/a | n/a | n/a | 80.7 | 5,660 |
| Model study: DataSage M3 with qwen38-27b | 20 | 90% | 100% | 0.84 | 0.55 | 67% | 0 | 100% | n/a | 2.0 | 37.8 | 24,148 |
| Model study: B2 single call with qwen38-27b | 20 | 90% | 100% | 0.94 | 0.89 | 73% | 6 | n/a | n/a | n/a | 47.0 | 3,150 |
| Model study: DataSage M3 with qwen-agentworld-35b-a3b | 20 | 100% | 100% | 0.81 | 0.48 | 81% | 0 | 100% | n/a | 2.0 | 398.9 | 53,484 |
| Model study: B2 single call with qwen-agentworld-35b-a3b | 20 | 65% | 95% | 0.86 | 0.65 | 71% | 66 | n/a | n/a | n/a | 777.2 | 8,968 |
| Model study: DataSage M3 with hemmingway-1-5 | 20 | 95% | 100% | 0.90 | 0.51 | 68% | 0 | 100% | n/a | 2.0 | 354.6 | 22,284 |
| Model study: B2 single call with hemmingway-1-5 | 20 | 75% | 100% | 0.91 | 0.77 | 66% | 2 | n/a | n/a | n/a | 1038.3 | 2,934 |
| Model study: DataSage M3 with olmo3-7b-instruct | 20 | 35% | 55% | 0.86 | 0.67 | 83% | 0 | 66% | 32% | 2.0 | 26.7 | 117,276 |
| Model study: B2 single call with olmo3-7b-instruct | 20 | 0% | 5% | 0.60 | 0.03 | 33% | 64 | n/a | n/a | n/a | 7.4 | 2,387 |
| Model study: DataSage M3 with olmo3-7b-think | 20 | 25% | 45% | 0.86 | 0.20 | 45% | 0 | 73% | 60% | 1.0 | 513.1 | 32,638 |
| Model study: B2 single call with olmo3-7b-think | 20 | 10% | 40% | 0.58 | 0.44 | 39% | 21 | n/a | n/a | n/a | 159.2 | 11,814 |
| Model study: DataSage M3 with olmo3-32b-instruct | 20 | 65% | 85% | 0.85 | 0.88 | 84% | 0 | 87% | 44% | 3.0 | 27.1 | 86,707 |
| Model study: B2 single call with olmo3-32b-instruct | 20 | 0% | 40% | 0.60 | 0.43 | 63% | 98 | n/a | n/a | n/a | 16.9 | 2,474 |
| Model study: DataSage M3 with olmo3-32b-think | 20 | 60% | 100% | 0.79 | 0.31 | 60% | 0 | 94% | 89% | 2.0 | 890.1 | 17,354 |
| Model study: B2 single call with olmo3-32b-think | 20 | 30% | 60% | 0.98 | 0.51 | 62% | 20 | n/a | n/a | n/a | 1084.0 | 7,793 |
| Model study: DataSage M3 with gpt-oss-120b | 20 | 100% | 100% | 0.95 | 0.70 | 85% | 0 | 90% | 32% | 2.0 | 49.1 | 40,037 |
| Model study: B2 single call with gpt-oss-120b | 20 | 80% | 100% | 0.82 | 0.86 | 82% | 13 | n/a | n/a | n/a | 24.0 | 2,940 |
| Model study: DataSage M3 with llama4-scout-17b | 20 | 95% | 100% | 0.87 | 0.70 | 84% | 0 | 97% | 62% | 2.5 | 17.1 | 57,674 |
| Model study: B2 single call with llama4-scout-17b | 20 | 0% | 0% | 0.00 | 0.00 | 0% | 0 | n/a | n/a | n/a | 6.5 | 2,110 |
| Model study: DataSage M3 with llama4-maverick-17b | 20 | 20% | 25% | 0.82 | 0.32 | 40% | 0 | 99% | 100% | 0.0 | 44.6 | 40,532 |
| Model study: B2 single call with llama4-maverick-17b | 20 | 25% | 55% | 0.96 | 0.77 | 69% | 78 | n/a | n/a | n/a | 5.9 | 1,965 |
| Model study: DataSage M3 with gemma4-31b-it | 20 | 80% | 100% | 0.85 | 0.45 | 65% | 0 | 90% | 86% | 2.0 | 45.6 | 31,766 |
| Model study: B2 single call with gemma4-31b-it | 20 | 80% | 100% | 0.91 | 0.72 | 75% | 3 | n/a | n/a | n/a | 25.8 | 2,320 |
| Model study: DataSage M3 with granite41-30b | 20 | 95% | 100% | 0.81 | 0.44 | 75% | 0 | 100% | n/a | 2.0 | 21.7 | 35,578 |
| Model study: B2 single call with granite41-30b | 20 | 40% | 85% | 0.78 | 0.75 | 63% | 5 | n/a | n/a | n/a | 12.0 | 2,130 |
| Model study: DataSage M3 with devstral2-123b | 20 | 85% | 100% | 0.83 | 0.45 | 62% | 0 | 100% | n/a | 2.0 | 209.6 | 34,456 |
| Model study: B2 single call with devstral2-123b | 20 | 70% | 85% | 0.87 | 0.78 | 83% | 16 | n/a | n/a | n/a | 36.6 | 2,304 |
| Model study: DataSage M3 with mistral-large-4 | 20 | 90% | 100% | 0.82 | 0.56 | 67% | 0 | 100% | 100% | 2.0 | 118.5 | 21,716 |
| Model study: DataSage M3 with glm-5-2 | 20 | 85% | 100% | 0.80 | 0.49 | 67% | 0 | 100% | n/a | 2.0 | 42.5 | 21,821 |
| Model study: B2 single call with glm-5-2 | 20 | 90% | 100% | 0.86 | 0.94 | 75% | 3 | n/a | n/a | n/a | 15.7 | 2,440 |
| Model study: DataSage M3 with glm-5-3 | 20 | 100% | 100% | 0.85 | 0.44 | 71% | 0 | 100% | n/a | 2.0 | 27.4 | 21,034 |
| Model study: B2 single call with glm-5-3 | 20 | 80% | 95% | 0.86 | 0.97 | 86% | 0 | n/a | n/a | n/a | 53.6 | 3,390 |
| Model study: DataSage M3 with glm-5-3-flash | 20 | 100% | 100% | 0.93 | 0.45 | 72% | 0 | 99% | 100% | 2.0 | 98.5 | 18,046 |
| Model study: B2 single call with glm-5-3-flash | 20 | 95% | 100% | 0.89 | 0.97 | 84% | 56 | n/a | n/a | n/a | 62.1 | 2,273 |
| Model study: DataSage M3 with glm-5-3-spec | 20 | 100% | 100% | 0.82 | 0.42 | 72% | 0 | 100% | n/a | 2.0 | 29.3 | 23,293 |
| Model study: B2 single call with glm-5-3-spec | 20 | 95% | 100% | 0.88 | 0.97 | 90% | 0 | n/a | n/a | n/a | 43.0 | 3,236 |
| Model study: DataSage M3 with deepseek-v4-1-flash | 20 | 95% | 100% | 0.87 | 0.55 | 70% | 0 | 100% | n/a | 2.0 | 69.4 | 31,228 |
| Model study: B2 single call with deepseek-v4-1-flash | 20 | 75% | 100% | 0.91 | 0.93 | 88% | 0 | n/a | n/a | n/a | 77.9 | 5,214 |
| Model study: DataSage M3 with kimi-k2-7-code | 20 | 95% | 100% | 0.88 | 0.65 | 76% | 0 | 100% | 100% | 2.0 | 40.1 | 26,462 |
| Model study: B2 single call with kimi-k2-7-code | 20 | 85% | 100% | 0.93 | 0.97 | 87% | 9 | n/a | n/a | n/a | 86.8 | 5,413 |
| Model study: DataSage M3 with minimax-m2-7 | 20 | 85% | 100% | 0.82 | 0.48 | 64% | 0 | 99% | 100% | 2.0 | 91.8 | 23,832 |
| Model study: B2 single call with minimax-m2-7 | 20 | 60% | 75% | 0.93 | 0.43 | 64% | 4 | n/a | n/a | n/a | 376.1 | 2,634 |
| Model study: DataSage M3 with minimax-m3 | 20 | 85% | 100% | 0.92 | 0.61 | 76% | 0 | 100% | n/a | 2.0 | 60.6 | 26,094 |
| Model study: B2 single call with minimax-m3 | 20 | 70% | 95% | 0.87 | 0.83 | 75% | 0 | n/a | n/a | n/a | 88.1 | 3,722 |
| Model study: DataSage M3 with mimo-v2-6-flash | 20 | 100% | 100% | 0.82 | 0.47 | 69% | 0 | 100% | n/a | 2.0 | 40.7 | 18,996 |
| Model study: B2 single call with mimo-v2-6-flash | 20 | 85% | 95% | 0.89 | 0.61 | 61% | 15 | n/a | n/a | n/a | 19.4 | 2,330 |
| Model study: DataSage M3 with mimo-v2-6-pro | 20 | 100% | 100% | 0.85 | 0.53 | 70% | 0 | 100% | n/a | 2.0 | 114.8 | 20,889 |
| Model study: B2 single call with mimo-v2-6-pro | 20 | 100% | 100% | 0.91 | 0.98 | 91% | 12 | n/a | n/a | n/a | 29.4 | 2,700 |
| Model study: DataSage M3 with beam-1-0 | 20 | 95% | 100% | 0.81 | 0.73 | 80% | 0 | 100% | n/a | 2.0 | 149.7 | 32,882 |
| Model study: B2 single call with beam-1-0 | 20 | 45% | 60% | 0.93 | 0.57 | 68% | 4 | n/a | n/a | n/a | 1726.1 | 5,370 |
| Model study: DataSage M3 with inkling-small | 20 | 100% | 100% | 0.93 | 0.81 | 94% | 0 | 100% | 100% | 2.0 | 45.4 | 47,759 |
| Model study: B2 single call with inkling-small | 20 | 80% | 95% | 0.88 | 0.78 | 75% | 4 | n/a | n/a | n/a | 47.8 | 3,762 |
| Model study: DataSage M3 with laguna-s-2-1 | 20 | 85% | 100% | 0.88 | 0.56 | 66% | 0 | 100% | n/a | 2.0 | 122.7 | 25,979 |
| Model study: B2 single call with laguna-s-2-1 | 20 | 10% | 10% | 0.64 | 0.08 | 89% | 0 | n/a | n/a | n/a | 231.2 | 0 |
| Model study: DataSage M3 with muse-glimmer-30b | 20 | 100% | 100% | 0.87 | 0.94 | 98% | 0 | 100% | n/a | 3.0 | 74.9 | 80,140 |
| Model study: B2 single call with muse-glimmer-30b | 20 | 70% | 95% | 0.77 | 0.94 | 76% | 12 | n/a | n/a | n/a | 135.6 | 6,190 |
| Model study: DataSage M3 with muse-spark-open | 20 | 95% | 100% | 0.81 | 0.62 | 68% | 0 | 100% | n/a | 2.0 | 124.0 | 35,408 |
| Model study: B2 single call with muse-spark-open | 20 | 90% | 100% | 0.77 | 0.95 | 84% | 4 | n/a | n/a | n/a | 111.6 | 4,352 |
| Model study: DataSage M3 with ornith-1-5-35b-a3b | 20 | 90% | 95% | 0.81 | 0.58 | 63% | 0 | 98% | 100% | 2.0 | 99.1 | 30,390 |
| Model study: B2 single call with ornith-1-5-35b-a3b | 20 | 65% | 85% | 0.94 | 0.36 | 55% | 7 | n/a | n/a | n/a | 103.5 | 4,078 |

## penguins-heldout

| System | n | Answer correct | Completed | Detect P | Detect R | Errors handled | Damage | Tool-call OK | Recovery | Approvals (med) | Latency s (med) | Tokens (med) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 stakeholder baseline | 20 | 5% | 70% | 1.00 | 0.55 | 23% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B1 fixed script | 20 | 30% | 100% | 1.00 | 0.75 | 76% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B2 single LLM call | 20 | 35% | 100% | 0.87 | 0.81 | 66% | 29 | n/a | n/a | n/a | 30.2 | 2,534 |
| DataSage (235B) | 20 | 45% | 100% | 0.82 | 0.74 | 74% | 0 | 100% | 100% | 2.0 | 222.1 | 52,740 |
| DataSage (30B) | 20 | 40% | 100% | 0.82 | 0.72 | 62% | 0 | 100% | n/a | 2.0 | 14.1 | 55,528 |
| DataSage (235B) + exclusion rule | 20 | 95% | 100% | 0.82 | 0.70 | 97% | 0 | 100% | n/a | 2.0 | 150.8 | 52,608 |
| DataSage (30B) + exclusion rule | 20 | 80% | 100% | 0.79 | 0.61 | 85% | 0 | 100% | 100% | 2.0 | 13.2 | 55,258 |
| DataSage (30B) + rule, strict approver | 20 | 65% | 100% | 0.78 | 0.60 | 83% | 0 | 100% | n/a | 2.0 | 12.7 | 51,670 |
| DataSage M3 (30B, default) | 20 | 85% | 100% | 0.82 | 0.73 | 92% | 0 | 100% | n/a | 2.0 | 16.2 | 58,389 |
| DataSage M3 (30B), compact memory | 20 | 80% | 100% | 0.83 | 0.60 | 84% | 0 | 99% | 100% | 2.0 | 48.2 | 71,104 |
| DataSage M3 (30B), Auto: every risky fix approved | 20 | 85% | 100% | 0.81 | 0.69 | 91% | 0 | 100% | n/a | 2.0 | 23.7 | 57,676 |
| M3 without coverage check | 20 | 75% | 100% | 0.81 | 0.69 | 87% | 0 | 100% | n/a | 2.0 | 22.8 | 54,862 |
| M3 without validator | 20 | 90% | 100% | 0.82 | 0.73 | 90% | 0 | 100% | 100% | 2.0 | 44.2 | 62,010 |
| M3 without merge rule in prompt | 20 | 90% | 100% | 0.80 | 0.64 | 88% | 0 | 100% | n/a | 2.0 | 44.6 | 55,112 |
| M3, all risky fixes rejected | 20 | 5% | 100% | 0.83 | 0.83 | 43% | 0 | 100% | n/a | 2.0 | 45.7 | 69,812 |
| Model study: DataSage M3 with qwen3-30b-a3b-instruct-2507 | 20 | 85% | 100% | 0.81 | 0.68 | 89% | 0 | 100% | n/a | 2.0 | 25.1 | 57,480 |
| Model study: B2 single call with qwen3-30b-a3b-instruct-2507 | 20 | 30% | 95% | 0.58 | 0.56 | 77% | 2 | n/a | n/a | n/a | 15.8 | 2,581 |
| Model study: DataSage M3 with qwen3-235b-a22b-instruct-2507 | 20 | 100% | 100% | 0.82 | 0.74 | 99% | 0 | 100% | n/a | 2.0 | 239.1 | 55,769 |
| Model study: B2 single call with qwen3-235b-a22b-instruct-2507 | 20 | 40% | 100% | 0.88 | 0.80 | 67% | 66 | n/a | n/a | n/a | 19.7 | 2,520 |
| Model study: DataSage M3 with qwen3-30b-a3b-thinking-2507 | 20 | 35% | 100% | 0.83 | 0.17 | 55% | 0 | 100% | n/a | 1.0 | 113.2 | 33,874 |
| Model study: B2 single call with qwen3-30b-a3b-thinking-2507 | 20 | 30% | 100% | 0.85 | 0.38 | 51% | 0 | n/a | n/a | n/a | 38.9 | 5,422 |
| Model study: DataSage M3 with qwen3-235b-a22b-thinking-2507 | 20 | 35% | 100% | 0.93 | 0.31 | 53% | 0 | 100% | n/a | 1.0 | 687.0 | 36,034 |
| Model study: B2 single call with qwen3-235b-a22b-thinking-2507 | 20 | 5% | 25% | 1.00 | 0.11 | 50% | 29 | n/a | n/a | n/a | 2029.8 | 0 |
| Model study: DataSage M3 with qwen3-coder-30b-a3b-instruct | 20 | 85% | 100% | 0.83 | 0.77 | 94% | 0 | 100% | 100% | 2.0 | 75.5 | 66,736 |
| Model study: B2 single call with qwen3-coder-30b-a3b-instruct | 20 | 40% | 85% | 0.78 | 0.75 | 79% | 155 | n/a | n/a | n/a | 33.0 | 2,533 |
| Model study: DataSage M3 with qwen3-coder-next | 20 | 95% | 100% | 0.84 | 0.84 | 97% | 0 | 100% | n/a | 2.0 | 42.0 | 75,640 |
| Model study: B2 single call with qwen3-coder-next | 20 | 55% | 95% | 0.81 | 0.82 | 82% | 84 | n/a | n/a | n/a | 13.2 | 2,596 |
| Model study: DataSage M3 with qwen3-vl-32b-instruct | 20 | 90% | 100% | 0.88 | 0.75 | 95% | 0 | 100% | n/a | 2.0 | 232.6 | 62,304 |
| Model study: B2 single call with qwen3-vl-32b-instruct | 20 | 20% | 75% | 0.70 | 0.81 | 66% | 29 | n/a | n/a | n/a | 48.9 | 2,654 |
| Model study: DataSage M3 with qwen3-vl-32b-thinking | 4 | 25% | 100% | 1.00 | 0.29 | 38% | 0 | 100% | n/a | 0.5 | 655.3 | 30,836 |
| Model study: DataSage M3 with qwen35-27b | 20 | 70% | 100% | 0.80 | 0.55 | 73% | 0 | 100% | n/a | 1.5 | 65.5 | 59,538 |
| Model study: B2 single call with qwen35-27b | 20 | 60% | 95% | 0.80 | 0.83 | 83% | 0 | n/a | n/a | n/a | 295.5 | 3,980 |
| Model study: DataSage M3 with qwen35-122b-a10b | 20 | 85% | 100% | 0.82 | 0.64 | 93% | 0 | 100% | n/a | 2.0 | 123.2 | 74,175 |
| Model study: B2 single call with qwen35-122b-a10b | 20 | 40% | 100% | 0.82 | 0.88 | 70% | 0 | n/a | n/a | n/a | 59.3 | 3,458 |
| Model study: DataSage M3 with qwen35-397b-a17b | 20 | 80% | 100% | 0.80 | 0.65 | 90% | 0 | 100% | n/a | 2.0 | 129.2 | 48,916 |
| Model study: B2 single call with qwen35-397b-a17b | 20 | 50% | 95% | 0.76 | 0.81 | 73% | 0 | n/a | n/a | n/a | 91.9 | 3,732 |
| Model study: DataSage M3 with qwen36-27b | 20 | 40% | 100% | 0.84 | 0.48 | 55% | 0 | 100% | n/a | 1.0 | 59.0 | 37,082 |
| Model study: B2 single call with qwen36-27b | 20 | 35% | 100% | 0.97 | 0.82 | 64% | 0 | n/a | n/a | n/a | 122.2 | 6,716 |
| Model study: DataSage M3 with qwen36-35b-a3b | 20 | 50% | 100% | 0.81 | 0.59 | 73% | 0 | 100% | n/a | 1.5 | 46.1 | 38,885 |
| Model study: B2 single call with qwen36-35b-a3b | 20 | 30% | 100% | 0.88 | 0.43 | 49% | 0 | n/a | n/a | n/a | 81.1 | 5,686 |
| Model study: DataSage M3 with qwen38-27b | 20 | 40% | 100% | 0.88 | 0.40 | 53% | 0 | 100% | n/a | 1.0 | 48.8 | 25,968 |
| Model study: B2 single call with qwen38-27b | 20 | 35% | 100% | 0.92 | 0.80 | 60% | 0 | n/a | n/a | n/a | 50.0 | 3,836 |
| Model study: DataSage M3 with qwen-agentworld-35b-a3b | 20 | 40% | 100% | 0.73 | 0.40 | 66% | 0 | 100% | n/a | 1.0 | 796.3 | 55,733 |
| Model study: B2 single call with qwen-agentworld-35b-a3b | 20 | 25% | 75% | 0.86 | 0.57 | 67% | 0 | n/a | n/a | n/a | 979.7 | 9,778 |
| Model study: DataSage M3 with hemmingway-1-5 | 20 | 35% | 100% | 0.92 | 0.40 | 53% | 0 | 100% | n/a | 1.0 | 565.3 | 25,512 |
| Model study: B2 single call with hemmingway-1-5 | 20 | 25% | 85% | 0.92 | 0.75 | 54% | 0 | n/a | n/a | n/a | 676.9 | 3,228 |
| Model study: DataSage M3 with olmo3-7b-instruct | 20 | 20% | 40% | 0.74 | 0.65 | 63% | 0 | 67% | 38% | 2.0 | 26.7 | 128,320 |
| Model study: B2 single call with olmo3-7b-instruct | 20 | 0% | 0% | 0.00 | 0.00 | 0% | 0 | n/a | n/a | n/a | 6.3 | 2,546 |
| Model study: DataSage M3 with olmo3-7b-think | 20 | 20% | 50% | 0.85 | 0.19 | 43% | 0 | 78% | 61% | 1.0 | 457.4 | 27,916 |
| Model study: B2 single call with olmo3-7b-think | 20 | 30% | 80% | 0.47 | 0.41 | 51% | 157 | n/a | n/a | n/a | 282.4 | 10,064 |
| Model study: DataSage M3 with olmo3-32b-instruct | 20 | 40% | 95% | 0.74 | 0.73 | 77% | 0 | 89% | 57% | 2.0 | 27.7 | 85,708 |
| Model study: B2 single call with olmo3-32b-instruct | 20 | 10% | 25% | 0.53 | 0.30 | 70% | 59 | n/a | n/a | n/a | 18.5 | 2,718 |
| Model study: DataSage M3 with olmo3-32b-think | 20 | 30% | 90% | 0.96 | 0.26 | 48% | 0 | 90% | 67% | 1.0 | 439.2 | 20,134 |
| Model study: B2 single call with olmo3-32b-think | 20 | 10% | 70% | 0.63 | 0.36 | 45% | 64 | n/a | n/a | n/a | 601.1 | 8,466 |
| Model study: DataSage M3 with gpt-oss-120b | 20 | 65% | 100% | 0.82 | 0.53 | 72% | 0 | 94% | 42% | 2.0 | 60.5 | 44,159 |
| Model study: B2 single call with gpt-oss-120b | 20 | 35% | 95% | 0.72 | 0.85 | 68% | 0 | n/a | n/a | n/a | 25.8 | 3,399 |
| Model study: DataSage M3 with llama4-scout-17b | 20 | 75% | 100% | 0.77 | 0.52 | 78% | 0 | 99% | 100% | 2.0 | 13.1 | 55,520 |
| Model study: B2 single call with llama4-scout-17b | 20 | 0% | 0% | 0.00 | 0.00 | 0% | 0 | n/a | n/a | n/a | 6.8 | 2,354 |
| Model study: DataSage M3 with llama4-maverick-17b | 20 | 0% | 0% | 0.96 | 0.30 | 36% | 0 | 100% | n/a | 0.0 | 29.3 | 36,946 |
| Model study: B2 single call with llama4-maverick-17b | 20 | 50% | 75% | 0.85 | 0.76 | 87% | 31 | n/a | n/a | n/a | 7.5 | 2,244 |
| Model study: DataSage M3 with gemma4-31b-it | 20 | 35% | 95% | 1.00 | 0.38 | 52% | 0 | 84% | 10% | 1.0 | 34.8 | 33,080 |
| Model study: B2 single call with gemma4-31b-it | 20 | 25% | 75% | 1.00 | 0.84 | 64% | 0 | n/a | n/a | n/a | 15.9 | 2,758 |
| Model study: DataSage M3 with granite41-30b | 20 | 35% | 100% | 0.84 | 0.36 | 55% | 0 | 100% | n/a | 1.5 | 17.4 | 29,964 |
| Model study: B2 single call with granite41-30b | 20 | 60% | 95% | 0.66 | 0.72 | 73% | 99 | n/a | n/a | n/a | 12.7 | 2,374 |
| Model study: DataSage M3 with devstral2-123b | 20 | 40% | 100% | 0.95 | 0.42 | 55% | 0 | 100% | n/a | 1.0 | 367.1 | 39,492 |
| Model study: B2 single call with devstral2-123b | 20 | 65% | 65% | 0.77 | 0.85 | 94% | 57 | n/a | n/a | n/a | 36.0 | 2,658 |
| Model study: DataSage M3 with mistral-large-4 | 14 | 36% | 100% | 0.91 | 0.34 | 49% | 0 | 99% | 100% | 1.0 | 259.5 | 23,108 |
| Model study: DataSage M3 with glm-5-2 | 20 | 35% | 100% | 0.90 | 0.40 | 52% | 0 | 99% | 100% | 1.0 | 37.8 | 23,304 |
| Model study: B2 single call with glm-5-2 | 20 | 35% | 100% | 0.88 | 0.93 | 63% | 0 | n/a | n/a | n/a | 18.1 | 2,682 |
| Model study: DataSage M3 with glm-5-3 | 20 | 35% | 100% | 0.92 | 0.38 | 53% | 0 | 100% | n/a | 1.0 | 23.3 | 24,296 |
| Model study: B2 single call with glm-5-3 | 20 | 35% | 100% | 0.90 | 0.95 | 68% | 120 | n/a | n/a | n/a | 41.7 | 3,462 |
| Model study: DataSage M3 with glm-5-3-flash | 20 | 35% | 100% | 0.86 | 0.36 | 53% | 0 | 100% | n/a | 1.0 | 96.7 | 20,854 |
| Model study: B2 single call with glm-5-3-flash | 20 | 30% | 95% | 0.69 | 0.90 | 64% | 0 | n/a | n/a | n/a | 101.6 | 2,688 |
| Model study: DataSage M3 with glm-5-3-spec | 20 | 35% | 100% | 0.94 | 0.38 | 53% | 0 | 100% | n/a | 1.0 | 25.6 | 24,342 |
| Model study: B2 single call with glm-5-3-spec | 20 | 35% | 100% | 0.93 | 0.98 | 65% | 0 | n/a | n/a | n/a | 36.2 | 3,394 |
| Model study: DataSage M3 with deepseek-v4-1-flash | 20 | 35% | 100% | 0.93 | 0.42 | 53% | 0 | 100% | n/a | 1.0 | 60.1 | 31,665 |
| Model study: B2 single call with deepseek-v4-1-flash | 20 | 35% | 100% | 0.97 | 0.85 | 64% | 0 | n/a | n/a | n/a | 349.5 | 5,890 |
| Model study: DataSage M3 with kimi-k2-7-code | 20 | 40% | 100% | 0.85 | 0.45 | 57% | 0 | 100% | n/a | 1.0 | 36.2 | 23,051 |
| Model study: B2 single call with kimi-k2-7-code | 20 | 35% | 100% | 0.89 | 0.89 | 56% | 0 | n/a | n/a | n/a | 90.0 | 5,341 |
| Model study: DataSage M3 with minimax-m2-7 | 20 | 40% | 100% | 0.89 | 0.38 | 54% | 0 | 99% | 100% | 1.5 | 197.3 | 23,707 |
| Model study: B2 single call with minimax-m2-7 | 20 | 35% | 90% | 0.92 | 0.65 | 55% | 0 | n/a | n/a | n/a | 259.3 | 2,883 |
| Model study: DataSage M3 with minimax-m3 | 20 | 40% | 100% | 0.89 | 0.58 | 66% | 0 | 99% | 100% | 2.0 | 68.8 | 26,391 |
| Model study: B2 single call with minimax-m3 | 20 | 30% | 95% | 0.79 | 0.88 | 62% | 0 | n/a | n/a | n/a | 121.8 | 4,170 |
| Model study: DataSage M3 with mimo-v2-6-flash | 20 | 35% | 100% | 0.94 | 0.39 | 53% | 0 | 100% | n/a | 1.0 | 56.1 | 24,384 |
| Model study: B2 single call with mimo-v2-6-flash | 20 | 35% | 85% | 0.97 | 0.81 | 59% | 0 | n/a | n/a | n/a | 28.1 | 2,738 |
| Model study: DataSage M3 with mimo-v2-6-pro | 20 | 35% | 100% | 0.95 | 0.40 | 53% | 0 | 99% | 100% | 1.0 | 122.1 | 25,644 |
| Model study: B2 single call with mimo-v2-6-pro | 20 | 35% | 100% | 0.80 | 0.93 | 65% | 0 | n/a | n/a | n/a | 42.7 | 3,058 |
| Model study: DataSage M3 with beam-1-0 | 20 | 50% | 100% | 0.91 | 0.49 | 61% | 0 | 100% | n/a | 1.0 | 137.0 | 24,432 |
| Model study: B2 single call with beam-1-0 | 20 | 5% | 10% | 1.00 | 0.10 | 88% | 0 | n/a | n/a | n/a | 2029.9 | 0 |
| Model study: DataSage M3 with inkling-small | 20 | 95% | 100% | 0.87 | 0.77 | 92% | 0 | 100% | 100% | 2.0 | 44.0 | 46,958 |
| Model study: B2 single call with inkling-small | 20 | 35% | 100% | 0.84 | 0.85 | 64% | 0 | n/a | n/a | n/a | 54.3 | 4,319 |
| Model study: DataSage M3 with laguna-s-2-1 | 20 | 40% | 100% | 0.92 | 0.40 | 55% | 0 | 100% | n/a | 1.0 | 120.6 | 25,760 |
| Model study: B2 single call with laguna-s-2-1 | 20 | 0% | 0% | 0.00 | 0.00 | 0% | 0 | n/a | n/a | n/a | 52.2 | 0 |
| Model study: DataSage M3 with muse-glimmer-30b | 20 | 70% | 100% | 0.84 | 0.81 | 90% | 0 | 100% | n/a | 2.0 | 77.0 | 82,300 |
| Model study: B2 single call with muse-glimmer-30b | 20 | 35% | 100% | 0.71 | 0.93 | 70% | 0 | n/a | n/a | n/a | 139.1 | 7,365 |
| Model study: DataSage M3 with muse-spark-open | 20 | 35% | 100% | 0.89 | 0.48 | 54% | 0 | 100% | n/a | 1.0 | 207.5 | 33,889 |
| Model study: B2 single call with muse-spark-open | 20 | 35% | 100% | 0.76 | 0.98 | 66% | 0 | n/a | n/a | n/a | 133.6 | 5,492 |
| Model study: DataSage M3 with ornith-1-5-35b-a3b | 20 | 35% | 100% | 0.89 | 0.48 | 54% | 0 | 99% | 100% | 1.0 | 98.9 | 33,372 |
| Model study: B2 single call with ornith-1-5-35b-a3b | 20 | 30% | 100% | 0.80 | 0.36 | 47% | 0 | n/a | n/a | n/a | 131.9 | 5,001 |

## sales-test

| System | n | Answer correct | Completed | Detect P | Detect R | Errors handled | Damage | Tool-call OK | Recovery | Approvals (med) | Latency s (med) | Tokens (med) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 stakeholder baseline | 20 | 10% | 85% | 0.82 | 0.51 | 22% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B1 fixed script | 20 | 55% | 100% | 0.78 | 0.78 | 76% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B2 single LLM call | 20 | 45% | 90% | 0.74 | 0.72 | 78% | 4 | n/a | n/a | n/a | 30.0 | 2,283 |
| DataSage (30B) + exclusion rule | 20 | 100% | 100% | 0.84 | 0.84 | 93% | 0 | 100% | n/a | 2.5 | 16.3 | 63,062 |
| DataSage M3 (30B, default) | 20 | 100% | 100% | 0.85 | 0.84 | 91% | 0 | 100% | n/a | 2.0 | 16.1 | 61,980 |
| DataSage M3 (30B), compact memory | 20 | 75% | 85% | 0.91 | 0.76 | 81% | 0 | 99% | 100% | 2.0 | 40.9 | 69,735 |
| DataSage M3 (30B), Auto: every risky fix approved | 20 | 100% | 100% | 0.83 | 0.87 | 91% | 3 | 100% | n/a | 3.0 | 19.1 | 68,304 |
| M3 without coverage check | 20 | 100% | 100% | 0.87 | 0.87 | 92% | 0 | 100% | n/a | 2.5 | 33.5 | 59,505 |
| M3 without validator | 20 | 100% | 100% | 0.87 | 0.89 | 93% | 0 | 100% | n/a | 3.0 | 35.8 | 64,076 |
| M3 without merge rule in prompt | 20 | 100% | 100% | 0.85 | 0.83 | 90% | 0 | 100% | n/a | 2.5 | 39.9 | 65,212 |
| M3, all risky fixes rejected | 20 | 20% | 100% | 0.86 | 0.94 | 40% | 0 | 99% | 50% | 3.0 | 45.4 | 77,943 |
| Model study: DataSage M3 with qwen3-30b-a3b-instruct-2507 | 20 | 100% | 100% | 0.87 | 0.87 | 91% | 0 | 100% | n/a | 2.0 | 31.4 | 61,483 |
| Model study: B2 single call with qwen3-30b-a3b-instruct-2507 | 20 | 45% | 100% | 0.69 | 0.68 | 63% | 156 | n/a | n/a | n/a | 9.7 | 2,342 |
| Model study: DataSage M3 with qwen3-235b-a22b-instruct-2507 | 20 | 100% | 100% | 0.89 | 0.89 | 93% | 0 | 100% | n/a | 2.5 | 257.4 | 57,944 |
| Model study: B2 single call with qwen3-235b-a22b-instruct-2507 | 20 | 40% | 90% | 0.73 | 0.71 | 78% | 1 | n/a | n/a | n/a | 21.1 | 2,288 |
| Model study: DataSage M3 with qwen3-30b-a3b-thinking-2507 | 20 | 90% | 100% | 0.85 | 0.24 | 63% | 0 | 100% | n/a | 2.0 | 145.1 | 40,150 |
| Model study: B2 single call with qwen3-30b-a3b-thinking-2507 | 20 | 55% | 95% | 0.87 | 0.44 | 51% | 10 | n/a | n/a | n/a | 45.3 | 5,470 |
| Model study: DataSage M3 with qwen3-235b-a22b-thinking-2507 | 20 | 100% | 100% | 0.91 | 0.43 | 66% | 0 | 100% | n/a | 2.0 | 892.3 | 47,152 |
| Model study: B2 single call with qwen3-235b-a22b-thinking-2507 | 20 | 30% | 30% | 1.00 | 0.20 | 61% | 3 | n/a | n/a | n/a | 2030.4 | 0 |
| Model study: DataSage M3 with qwen3-coder-30b-a3b-instruct | 20 | 100% | 100% | 0.88 | 0.90 | 93% | 0 | 99% | 100% | 3.0 | 170.2 | 77,216 |
| Model study: B2 single call with qwen3-coder-30b-a3b-instruct | 20 | 50% | 90% | 0.75 | 0.72 | 64% | 9 | n/a | n/a | n/a | 20.2 | 2,321 |
| Model study: DataSage M3 with qwen3-coder-next | 20 | 80% | 100% | 0.90 | 0.91 | 80% | 0 | 100% | n/a | 2.0 | 43.7 | 70,780 |
| Model study: B2 single call with qwen3-coder-next | 20 | 45% | 80% | 0.88 | 0.67 | 71% | 34 | n/a | n/a | n/a | 12.3 | 2,310 |
| Model study: DataSage M3 with qwen3-vl-32b-instruct | 20 | 100% | 100% | 0.88 | 0.92 | 95% | 0 | 100% | n/a | 3.0 | 236.0 | 64,911 |
| Model study: B2 single call with qwen3-vl-32b-instruct | 20 | 30% | 95% | 0.64 | 0.74 | 73% | 18 | n/a | n/a | n/a | 89.7 | 2,465 |
| Model study: DataSage M3 with qwen3-vl-32b-thinking | 3 | 100% | 100% | 0.75 | 0.30 | 58% | 0 | 100% | n/a | 1.0 | 378.8 | 36,772 |
| Model study: DataSage M3 with qwen35-27b | 20 | 75% | 100% | 0.86 | 0.73 | 69% | 0 | 100% | n/a | 2.0 | 78.4 | 64,385 |
| Model study: B2 single call with qwen35-27b | 20 | 55% | 90% | 0.99 | 0.76 | 75% | 4 | n/a | n/a | n/a | 119.4 | 3,410 |
| Model study: DataSage M3 with qwen35-122b-a10b | 20 | 90% | 100% | 0.81 | 0.70 | 82% | 0 | 100% | n/a | 2.0 | 116.2 | 72,214 |
| Model study: B2 single call with qwen35-122b-a10b | 20 | 60% | 95% | 0.89 | 0.74 | 78% | 9 | n/a | n/a | n/a | 82.6 | 3,445 |
| Model study: DataSage M3 with qwen35-397b-a17b | 20 | 100% | 100% | 0.88 | 0.76 | 95% | 0 | 100% | n/a | 3.0 | 120.9 | 54,790 |
| Model study: B2 single call with qwen35-397b-a17b | 20 | 75% | 100% | 0.94 | 0.71 | 65% | 7 | n/a | n/a | n/a | 67.3 | 3,096 |
| Model study: DataSage M3 with qwen36-27b | 20 | 100% | 100% | 0.84 | 0.59 | 76% | 0 | 98% | 100% | 2.0 | 60.4 | 51,972 |
| Model study: B2 single call with qwen36-27b | 20 | 50% | 95% | 0.90 | 0.79 | 57% | 4 | n/a | n/a | n/a | 110.2 | 5,889 |
| Model study: DataSage M3 with qwen36-35b-a3b | 20 | 100% | 100% | 0.83 | 0.76 | 88% | 0 | 99% | 50% | 2.0 | 47.6 | 44,616 |
| Model study: B2 single call with qwen36-35b-a3b | 20 | 70% | 100% | 0.84 | 0.59 | 57% | 9 | n/a | n/a | n/a | 88.4 | 6,262 |
| Model study: DataSage M3 with qwen38-27b | 20 | 100% | 100% | 0.87 | 0.59 | 67% | 0 | 100% | n/a | 2.0 | 66.0 | 25,118 |
| Model study: B2 single call with qwen38-27b | 20 | 70% | 95% | 0.94 | 0.83 | 80% | 3 | n/a | n/a | n/a | 43.1 | 3,288 |
| Model study: DataSage M3 with qwen-agentworld-35b-a3b | 20 | 90% | 100% | 0.83 | 0.50 | 80% | 0 | 100% | n/a | 2.0 | 535.4 | 58,689 |
| Model study: B2 single call with qwen-agentworld-35b-a3b | 20 | 35% | 85% | 0.90 | 0.72 | 73% | 2 | n/a | n/a | n/a | 490.6 | 9,474 |
| Model study: DataSage M3 with hemmingway-1-5 | 20 | 85% | 100% | 0.87 | 0.51 | 60% | 0 | 100% | n/a | 2.0 | 304.3 | 24,912 |
| Model study: B2 single call with hemmingway-1-5 | 20 | 55% | 100% | 0.95 | 0.82 | 63% | 3 | n/a | n/a | n/a | 322.6 | 3,013 |
| Model study: DataSage M3 with olmo3-7b-instruct | 20 | 10% | 25% | 0.82 | 0.74 | 68% | 0 | 65% | 36% | 2.0 | 22.6 | 125,580 |
| Model study: B2 single call with olmo3-7b-instruct | 20 | 0% | 0% | 0.00 | 0.00 | 0% | 0 | n/a | n/a | n/a | 8.9 | 2,526 |
| Model study: DataSage M3 with olmo3-7b-think | 20 | 5% | 15% | 0.75 | 0.27 | 45% | 0 | 70% | 66% | 2.0 | 566.0 | 47,036 |
| Model study: B2 single call with olmo3-7b-think | 20 | 5% | 45% | 0.66 | 0.44 | 43% | 11 | n/a | n/a | n/a | 320.9 | 10,434 |
| Model study: DataSage M3 with olmo3-32b-instruct | 20 | 70% | 90% | 0.86 | 0.90 | 86% | 0 | 90% | 32% | 4.0 | 28.8 | 87,356 |
| Model study: B2 single call with olmo3-32b-instruct | 20 | 5% | 35% | 0.51 | 0.42 | 63% | 3 | n/a | n/a | n/a | 16.7 | 2,502 |
| Model study: DataSage M3 with olmo3-32b-think | 20 | 55% | 95% | 0.83 | 0.28 | 51% | 0 | 97% | 75% | 2.0 | 422.1 | 9,792 |
| Model study: B2 single call with olmo3-32b-think | 20 | 25% | 65% | 0.81 | 0.42 | 61% | 61 | n/a | n/a | n/a | 613.8 | 8,042 |
| Model study: DataSage M3 with gpt-oss-120b | 20 | 85% | 100% | 0.97 | 0.72 | 80% | 0 | 97% | 33% | 2.0 | 55.5 | 44,890 |
| Model study: B2 single call with gpt-oss-120b | 20 | 60% | 100% | 0.91 | 0.89 | 79% | 11 | n/a | n/a | n/a | 21.9 | 3,035 |
| Model study: DataSage M3 with llama4-scout-17b | 20 | 70% | 95% | 0.85 | 0.73 | 85% | 0 | 98% | 80% | 3.0 | 15.2 | 62,050 |
| Model study: B2 single call with llama4-scout-17b | 20 | 0% | 0% | 0.00 | 0.00 | 0% | 0 | n/a | n/a | n/a | 5.9 | 2,139 |
| Model study: DataSage M3 with llama4-maverick-17b | 20 | 0% | 5% | 0.81 | 0.29 | 34% | 0 | 98% | 0% | 0.0 | 41.2 | 35,214 |
| Model study: B2 single call with llama4-maverick-17b | 20 | 40% | 55% | 0.97 | 0.71 | 63% | 113 | n/a | n/a | n/a | 4.7 | 2,038 |
| Model study: DataSage M3 with gemma4-31b-it | 20 | 80% | 100% | 0.90 | 0.50 | 62% | 0 | 96% | 62% | 1.5 | 27.2 | 34,223 |
| Model study: B2 single call with gemma4-31b-it | 20 | 85% | 95% | 0.93 | 0.73 | 75% | 7 | n/a | n/a | n/a | 36.8 | 2,410 |
| Model study: DataSage M3 with granite41-30b | 20 | 85% | 100% | 0.81 | 0.47 | 71% | 0 | 100% | n/a | 2.0 | 20.7 | 41,558 |
| Model study: B2 single call with granite41-30b | 20 | 40% | 80% | 0.83 | 0.70 | 61% | 6 | n/a | n/a | n/a | 11.1 | 2,130 |
| Model study: DataSage M3 with devstral2-123b | 20 | 55% | 100% | 0.90 | 0.52 | 55% | 0 | 100% | n/a | 1.5 | 601.9 | 35,771 |
| Model study: B2 single call with devstral2-123b | 20 | 75% | 80% | 0.84 | 0.79 | 84% | 38 | n/a | n/a | n/a | 37.3 | 2,384 |
| Model study: DataSage M3 with mistral-large-4 | 16 | 75% | 100% | 0.91 | 0.53 | 61% | 0 | 100% | n/a | 2.0 | 193.8 | 22,996 |
| Model study: DataSage M3 with glm-5-2 | 20 | 95% | 100% | 0.85 | 0.58 | 72% | 0 | 100% | 100% | 2.0 | 48.5 | 24,019 |
| Model study: B2 single call with glm-5-2 | 20 | 80% | 100% | 0.88 | 0.94 | 80% | 1 | n/a | n/a | n/a | 14.1 | 2,378 |
| Model study: DataSage M3 with glm-5-3 | 20 | 90% | 100% | 0.89 | 0.56 | 71% | 0 | 100% | n/a | 2.0 | 39.7 | 25,822 |
| Model study: B2 single call with glm-5-3 | 20 | 85% | 95% | 0.90 | 0.98 | 90% | 0 | n/a | n/a | n/a | 51.3 | 3,394 |
| Model study: DataSage M3 with glm-5-3-flash | 20 | 100% | 100% | 0.98 | 0.48 | 70% | 0 | 100% | n/a | 2.0 | 124.4 | 17,739 |
| Model study: B2 single call with glm-5-3-flash | 20 | 95% | 100% | 0.92 | 0.93 | 87% | 23 | n/a | n/a | n/a | 93.3 | 2,304 |
| Model study: DataSage M3 with glm-5-3-spec | 20 | 95% | 100% | 0.87 | 0.50 | 64% | 0 | 100% | n/a | 2.0 | 36.7 | 23,491 |
| Model study: B2 single call with glm-5-3-spec | 20 | 80% | 100% | 0.89 | 0.97 | 85% | 0 | n/a | n/a | n/a | 47.9 | 3,440 |
| Model study: DataSage M3 with deepseek-v4-1-flash | 20 | 95% | 100% | 0.88 | 0.62 | 66% | 0 | 100% | n/a | 2.0 | 90.8 | 31,716 |
| Model study: B2 single call with deepseek-v4-1-flash | 20 | 50% | 100% | 0.89 | 0.89 | 90% | 0 | n/a | n/a | n/a | 216.1 | 4,798 |
| Model study: DataSage M3 with kimi-k2-7-code | 20 | 85% | 100% | 0.81 | 0.67 | 75% | 0 | 100% | 100% | 2.5 | 41.8 | 30,514 |
| Model study: B2 single call with kimi-k2-7-code | 20 | 85% | 100% | 0.89 | 0.93 | 78% | 10 | n/a | n/a | n/a | 76.6 | 5,169 |
| Model study: DataSage M3 with minimax-m2-7 | 20 | 75% | 100% | 0.93 | 0.58 | 69% | 0 | 100% | n/a | 2.0 | 103.9 | 26,330 |
| Model study: B2 single call with minimax-m2-7 | 20 | 35% | 80% | 0.97 | 0.43 | 56% | 1 | n/a | n/a | n/a | 369.4 | 2,593 |
| Model study: DataSage M3 with minimax-m3 | 20 | 90% | 100% | 0.97 | 0.63 | 80% | 0 | 100% | n/a | 2.0 | 62.6 | 25,426 |
| Model study: B2 single call with minimax-m3 | 20 | 55% | 100% | 0.88 | 0.82 | 72% | 0 | n/a | n/a | n/a | 106.8 | 3,998 |
| Model study: DataSage M3 with mimo-v2-6-flash | 20 | 95% | 100% | 0.85 | 0.51 | 63% | 0 | 100% | n/a | 2.0 | 42.2 | 19,692 |
| Model study: B2 single call with mimo-v2-6-flash | 20 | 85% | 100% | 0.94 | 0.67 | 61% | 10 | n/a | n/a | n/a | 17.2 | 2,362 |
| Model study: DataSage M3 with mimo-v2-6-pro | 20 | 100% | 100% | 0.83 | 0.54 | 65% | 0 | 100% | 100% | 2.0 | 102.2 | 20,950 |
| Model study: B2 single call with mimo-v2-6-pro | 20 | 95% | 100% | 0.88 | 0.96 | 90% | 9 | n/a | n/a | n/a | 33.4 | 2,686 |
| Model study: DataSage M3 with beam-1-0 | 20 | 95% | 100% | 0.84 | 0.78 | 74% | 0 | 100% | n/a | 2.0 | 221.1 | 34,336 |
| Model study: B2 single call with beam-1-0 | 20 | 35% | 55% | 0.90 | 0.52 | 59% | 3 | n/a | n/a | n/a | 1827.6 | 5,240 |
| Model study: DataSage M3 with inkling-small | 20 | 100% | 100% | 0.96 | 0.87 | 86% | 0 | 100% | 100% | 2.5 | 41.6 | 45,488 |
| Model study: B2 single call with inkling-small | 20 | 50% | 100% | 0.91 | 0.81 | 78% | 8 | n/a | n/a | n/a | 43.9 | 3,724 |
| Model study: DataSage M3 with laguna-s-2-1 | 20 | 80% | 100% | 0.88 | 0.62 | 66% | 0 | 100% | 100% | 2.0 | 340.1 | 32,498 |
| Model study: B2 single call with laguna-s-2-1 | 20 | 0% | 0% | 0.00 | 0.00 | 0% | 0 | n/a | n/a | n/a | 52.2 | 0 |
| Model study: DataSage M3 with muse-glimmer-30b | 20 | 95% | 100% | 0.88 | 0.90 | 93% | 0 | 100% | n/a | 3.0 | 72.3 | 82,200 |
| Model study: B2 single call with muse-glimmer-30b | 20 | 60% | 95% | 0.75 | 0.86 | 80% | 10 | n/a | n/a | n/a | 134.7 | 6,382 |
| Model study: DataSage M3 with muse-spark-open | 20 | 80% | 100% | 0.82 | 0.73 | 66% | 0 | 100% | n/a | 2.0 | 174.3 | 38,902 |
| Model study: B2 single call with muse-spark-open | 20 | 85% | 100% | 0.76 | 0.97 | 90% | 3 | n/a | n/a | n/a | 111.4 | 4,650 |
| Model study: DataSage M3 with ornith-1-5-35b-a3b | 20 | 85% | 100% | 0.85 | 0.68 | 65% | 0 | 99% | 100% | 2.0 | 167.6 | 34,240 |
| Model study: B2 single call with ornith-1-5-35b-a3b | 20 | 45% | 85% | 0.95 | 0.40 | 49% | 1 | n/a | n/a | n/a | 158.7 | 3,992 |

## penguins-test

| System | n | Answer correct | Completed | Detect P | Detect R | Errors handled | Damage | Tool-call OK | Recovery | Approvals (med) | Latency s (med) | Tokens (med) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 stakeholder baseline | 20 | 0% | 50% | 1.00 | 0.51 | 32% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B1 fixed script | 20 | 35% | 100% | 1.00 | 0.84 | 74% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B2 single LLM call | 20 | 50% | 95% | 0.92 | 0.80 | 82% | 0 | n/a | n/a | n/a | 42.5 | 2,524 |
| DataSage (30B) + exclusion rule | 20 | 85% | 100% | 0.89 | 0.78 | 92% | 0 | 100% | n/a | 2.0 | 14.3 | 53,600 |
| DataSage M3 (30B, default) | 20 | 85% | 100% | 0.89 | 0.74 | 93% | 0 | 100% | n/a | 2.0 | 15.0 | 56,854 |
| DataSage M3 (30B), compact memory | 20 | 80% | 100% | 0.94 | 0.71 | 88% | 0 | 97% | 75% | 2.0 | 34.1 | 58,151 |
| DataSage M3 (30B), Auto: every risky fix approved | 20 | 90% | 100% | 0.89 | 0.76 | 93% | 0 | 100% | n/a | 2.0 | 24.4 | 62,728 |
| M3 without coverage check | 20 | 80% | 100% | 0.90 | 0.81 | 94% | 0 | 100% | n/a | 2.0 | 30.8 | 55,280 |
| M3 without validator | 20 | 90% | 100% | 0.90 | 0.80 | 95% | 0 | 100% | n/a | 2.0 | 32.1 | 60,926 |
| M3 without merge rule in prompt | 20 | 90% | 100% | 0.89 | 0.79 | 93% | 0 | 100% | n/a | 2.0 | 40.4 | 61,152 |
| M3, all risky fixes rejected | 20 | 10% | 95% | 0.90 | 0.85 | 48% | 0 | 100% | n/a | 2.0 | 33.4 | 61,784 |
| Model study: DataSage M3 with qwen3-30b-a3b-instruct-2507 | 20 | 90% | 100% | 0.89 | 0.77 | 94% | 0 | 100% | n/a | 2.0 | 25.2 | 60,132 |
| Model study: B2 single call with qwen3-30b-a3b-instruct-2507 | 20 | 35% | 100% | 0.73 | 0.71 | 75% | 60 | n/a | n/a | n/a | 6.4 | 2,550 |
| Model study: DataSage M3 with qwen3-235b-a22b-instruct-2507 | 20 | 100% | 100% | 0.90 | 0.85 | 98% | 0 | 100% | n/a | 2.0 | 202.0 | 56,550 |
| Model study: B2 single call with qwen3-235b-a22b-instruct-2507 | 20 | 55% | 100% | 0.88 | 0.78 | 84% | 0 | n/a | n/a | n/a | 23.2 | 2,530 |
| Model study: DataSage M3 with qwen3-30b-a3b-thinking-2507 | 20 | 75% | 100% | 1.00 | 0.15 | 72% | 0 | 100% | n/a | 1.0 | 112.2 | 32,554 |
| Model study: B2 single call with qwen3-30b-a3b-thinking-2507 | 20 | 65% | 100% | 0.93 | 0.48 | 65% | 6 | n/a | n/a | n/a | 41.6 | 5,323 |
| Model study: DataSage M3 with qwen3-235b-a22b-thinking-2507 | 20 | 75% | 100% | 0.94 | 0.40 | 72% | 0 | 100% | n/a | 1.0 | 801.5 | 42,984 |
| Model study: B2 single call with qwen3-235b-a22b-thinking-2507 | 20 | 10% | 15% | 0.86 | 0.07 | 88% | 0 | n/a | n/a | n/a | 2030.8 | 0 |
| Model study: DataSage M3 with qwen3-coder-30b-a3b-instruct | 20 | 90% | 100% | 0.90 | 0.80 | 95% | 0 | 99% | 100% | 2.0 | 72.4 | 74,775 |
| Model study: B2 single call with qwen3-coder-30b-a3b-instruct | 20 | 90% | 100% | 0.82 | 0.81 | 95% | 50 | n/a | n/a | n/a | 24.8 | 2,551 |
| Model study: DataSage M3 with qwen3-coder-next | 20 | 100% | 100% | 0.89 | 0.91 | 98% | 0 | 100% | n/a | 2.0 | 45.4 | 80,617 |
| Model study: B2 single call with qwen3-coder-next | 20 | 55% | 85% | 0.89 | 0.77 | 80% | 70 | n/a | n/a | n/a | 11.0 | 2,559 |
| Model study: DataSage M3 with qwen3-vl-32b-instruct | 20 | 95% | 100% | 0.93 | 0.73 | 87% | 0 | 100% | n/a | 2.0 | 188.4 | 56,184 |
| Model study: B2 single call with qwen3-vl-32b-instruct | 20 | 45% | 95% | 0.70 | 0.81 | 76% | 30 | n/a | n/a | n/a | 45.7 | 2,664 |
| Model study: DataSage M3 with qwen3-vl-32b-thinking | 2 | 100% | 100% | 1.00 | 0.50 | 72% | 0 | 100% | n/a | 1.5 | 753.9 | 35,964 |
| Model study: DataSage M3 with qwen35-27b | 20 | 95% | 100% | 0.90 | 0.71 | 87% | 0 | 100% | n/a | 2.0 | 71.1 | 65,271 |
| Model study: B2 single call with qwen35-27b | 20 | 60% | 85% | 0.75 | 0.72 | 87% | 0 | n/a | n/a | n/a | 676.7 | 3,682 |
| Model study: DataSage M3 with qwen35-122b-a10b | 20 | 85% | 100% | 0.87 | 0.56 | 91% | 0 | 100% | n/a | 2.0 | 105.0 | 68,318 |
| Model study: B2 single call with qwen35-122b-a10b | 20 | 65% | 100% | 0.84 | 0.85 | 84% | 2 | n/a | n/a | n/a | 64.2 | 3,526 |
| Model study: DataSage M3 with qwen35-397b-a17b | 20 | 95% | 100% | 0.89 | 0.73 | 97% | 0 | 100% | n/a | 2.0 | 109.3 | 51,902 |
| Model study: B2 single call with qwen35-397b-a17b | 20 | 75% | 100% | 0.86 | 0.88 | 84% | 5 | n/a | n/a | n/a | 97.2 | 3,868 |
| Model study: DataSage M3 with qwen36-27b | 20 | 75% | 100% | 0.93 | 0.47 | 74% | 0 | 100% | n/a | 1.0 | 60.6 | 39,279 |
| Model study: B2 single call with qwen36-27b | 20 | 70% | 100% | 0.99 | 0.85 | 80% | 4 | n/a | n/a | n/a | 131.0 | 6,811 |
| Model study: DataSage M3 with qwen36-35b-a3b | 20 | 85% | 100% | 0.88 | 0.65 | 93% | 0 | 100% | n/a | 2.0 | 53.0 | 41,660 |
| Model study: B2 single call with qwen36-35b-a3b | 20 | 55% | 100% | 0.93 | 0.63 | 70% | 6 | n/a | n/a | n/a | 79.5 | 6,226 |
| Model study: DataSage M3 with qwen38-27b | 20 | 75% | 100% | 0.95 | 0.47 | 72% | 0 | 100% | n/a | 1.0 | 40.0 | 26,756 |
| Model study: B2 single call with qwen38-27b | 20 | 65% | 100% | 0.96 | 0.81 | 78% | 0 | n/a | n/a | n/a | 69.3 | 3,836 |
| Model study: DataSage M3 with qwen-agentworld-35b-a3b | 20 | 75% | 100% | 0.84 | 0.36 | 86% | 0 | 100% | n/a | 2.0 | 584.3 | 55,614 |
| Model study: B2 single call with qwen-agentworld-35b-a3b | 20 | 55% | 90% | 0.88 | 0.70 | 74% | 39 | n/a | n/a | n/a | 875.9 | 10,342 |
| Model study: DataSage M3 with hemmingway-1-5 | 20 | 75% | 100% | 0.98 | 0.48 | 72% | 0 | 100% | n/a | 1.0 | 248.9 | 25,138 |
| Model study: B2 single call with hemmingway-1-5 | 20 | 40% | 75% | 0.90 | 0.76 | 74% | 1 | n/a | n/a | n/a | 311.0 | 3,238 |
| Model study: DataSage M3 with olmo3-7b-instruct | 20 | 5% | 10% | 0.78 | 0.76 | 80% | 0 | 65% | 37% | 2.0 | 24.2 | 136,178 |
| Model study: B2 single call with olmo3-7b-instruct | 20 | 0% | 0% | 0.00 | 0.00 | 0% | 0 | n/a | n/a | n/a | 7.6 | 2,587 |
| Model study: DataSage M3 with olmo3-7b-think | 20 | 20% | 30% | 0.87 | 0.15 | 53% | 0 | 81% | 77% | 0.0 | 607.6 | 29,101 |
| Model study: B2 single call with olmo3-7b-think | 20 | 25% | 65% | 0.55 | 0.40 | 52% | 44 | n/a | n/a | n/a | 314.9 | 9,632 |
| Model study: DataSage M3 with olmo3-32b-instruct | 20 | 60% | 95% | 0.72 | 0.81 | 89% | 0 | 87% | 33% | 2.0 | 30.4 | 93,910 |
| Model study: B2 single call with olmo3-32b-instruct | 20 | 0% | 10% | 0.62 | 0.23 | 69% | 3 | n/a | n/a | n/a | 15.3 | 2,651 |
| Model study: DataSage M3 with olmo3-32b-think | 20 | 55% | 90% | 0.93 | 0.31 | 66% | 0 | 94% | 100% | 1.0 | 511.8 | 22,694 |
| Model study: B2 single call with olmo3-32b-think | 20 | 45% | 65% | 0.67 | 0.40 | 68% | 39 | n/a | n/a | n/a | 703.8 | 8,304 |
| Model study: DataSage M3 with gpt-oss-120b | 20 | 85% | 100% | 0.93 | 0.59 | 86% | 0 | 97% | 43% | 1.5 | 64.8 | 43,900 |
| Model study: B2 single call with gpt-oss-120b | 20 | 65% | 100% | 0.82 | 0.84 | 81% | 0 | n/a | n/a | n/a | 22.5 | 3,328 |
| Model study: DataSage M3 with llama4-scout-17b | 20 | 80% | 95% | 0.86 | 0.59 | 83% | 0 | 94% | 69% | 2.0 | 15.9 | 59,118 |
| Model study: B2 single call with llama4-scout-17b | 20 | 0% | 0% | 0.00 | 0.00 | 0% | 0 | n/a | n/a | n/a | 7.3 | 2,376 |
| Model study: DataSage M3 with llama4-maverick-17b | 20 | 5% | 10% | 0.94 | 0.37 | 54% | 0 | 100% | n/a | 1.0 | 31.3 | 36,442 |
| Model study: B2 single call with llama4-maverick-17b | 20 | 50% | 65% | 0.77 | 0.78 | 88% | 56 | n/a | n/a | n/a | 6.9 | 2,257 |
| Model study: DataSage M3 with gemma4-31b-it | 20 | 75% | 100% | 0.95 | 0.43 | 72% | 0 | 96% | 57% | 1.0 | 43.7 | 38,270 |
| Model study: B2 single call with gemma4-31b-it | 20 | 45% | 60% | 1.00 | 0.87 | 80% | 0 | n/a | n/a | n/a | 79.5 | 2,791 |
| Model study: DataSage M3 with granite41-30b | 20 | 75% | 100% | 0.91 | 0.34 | 69% | 0 | 100% | n/a | 1.0 | 16.1 | 32,352 |
| Model study: B2 single call with granite41-30b | 20 | 45% | 95% | 0.80 | 0.69 | 72% | 113 | n/a | n/a | n/a | 10.7 | 2,291 |
| Model study: DataSage M3 with devstral2-123b | 20 | 70% | 100% | 0.95 | 0.45 | 70% | 0 | 100% | n/a | 1.0 | 322.2 | 39,764 |
| Model study: B2 single call with devstral2-123b | 20 | 55% | 60% | 0.85 | 0.84 | 94% | 0 | n/a | n/a | n/a | 33.7 | 2,630 |
| Model study: DataSage M3 with mistral-large-4 | 4 | 100% | 100% | 1.00 | 0.50 | 68% | 0 | 100% | n/a | 1.0 | 246.1 | 21,168 |
| Model study: DataSage M3 with glm-5-2 | 20 | 75% | 100% | 0.95 | 0.48 | 72% | 0 | 99% | 100% | 1.0 | 36.9 | 23,452 |
| Model study: B2 single call with glm-5-2 | 20 | 55% | 100% | 0.87 | 0.92 | 77% | 0 | n/a | n/a | n/a | 16.2 | 2,752 |
| Model study: DataSage M3 with glm-5-3 | 20 | 80% | 100% | 0.93 | 0.45 | 71% | 0 | 99% | 100% | 1.5 | 41.9 | 24,822 |
| Model study: B2 single call with glm-5-3 | 20 | 65% | 100% | 0.92 | 0.97 | 78% | 54 | n/a | n/a | n/a | 38.4 | 3,456 |
| Model study: DataSage M3 with glm-5-3-flash | 20 | 75% | 100% | 0.95 | 0.49 | 72% | 0 | 100% | n/a | 1.0 | 118.4 | 22,858 |
| Model study: B2 single call with glm-5-3-flash | 20 | 60% | 100% | 0.75 | 0.91 | 80% | 1 | n/a | n/a | n/a | 121.1 | 2,660 |
| Model study: DataSage M3 with glm-5-3-spec | 20 | 75% | 100% | 0.95 | 0.45 | 72% | 0 | 99% | 100% | 1.0 | 36.5 | 25,054 |
| Model study: B2 single call with glm-5-3-spec | 20 | 65% | 100% | 0.89 | 0.95 | 80% | 0 | n/a | n/a | n/a | 45.7 | 3,550 |
| Model study: DataSage M3 with deepseek-v4-1-flash | 20 | 75% | 100% | 0.96 | 0.50 | 72% | 0 | 100% | n/a | 1.0 | 67.1 | 32,573 |
| Model study: B2 single call with deepseek-v4-1-flash | 20 | 60% | 100% | 0.91 | 0.90 | 81% | 0 | n/a | n/a | n/a | 277.4 | 5,364 |
| Model study: DataSage M3 with kimi-k2-7-code | 20 | 90% | 100% | 0.92 | 0.56 | 78% | 0 | 99% | 100% | 1.5 | 36.3 | 26,718 |
| Model study: B2 single call with kimi-k2-7-code | 20 | 70% | 100% | 0.91 | 0.93 | 81% | 0 | n/a | n/a | n/a | 68.1 | 4,562 |
| Model study: DataSage M3 with minimax-m2-7 | 20 | 75% | 100% | 0.96 | 0.51 | 73% | 0 | 97% | 100% | 1.0 | 88.6 | 24,188 |
| Model study: B2 single call with minimax-m2-7 | 20 | 35% | 90% | 0.78 | 0.50 | 63% | 0 | n/a | n/a | n/a | 544.5 | 2,899 |
| Model study: DataSage M3 with minimax-m3 | 20 | 65% | 100% | 0.91 | 0.62 | 69% | 0 | 100% | n/a | 1.0 | 59.4 | 26,760 |
| Model study: B2 single call with minimax-m3 | 20 | 60% | 95% | 0.79 | 0.90 | 79% | 0 | n/a | n/a | n/a | 108.7 | 4,361 |
| Model study: DataSage M3 with mimo-v2-6-flash | 20 | 75% | 100% | 0.93 | 0.50 | 72% | 0 | 99% | 100% | 1.0 | 44.0 | 20,968 |
| Model study: B2 single call with mimo-v2-6-flash | 20 | 45% | 80% | 0.95 | 0.83 | 71% | 2 | n/a | n/a | n/a | 22.6 | 2,747 |
| Model study: DataSage M3 with mimo-v2-6-pro | 20 | 75% | 100% | 0.93 | 0.50 | 72% | 0 | 99% | 100% | 1.0 | 82.4 | 25,674 |
| Model study: B2 single call with mimo-v2-6-pro | 20 | 55% | 100% | 0.80 | 0.91 | 77% | 5 | n/a | n/a | n/a | 42.0 | 3,184 |
| Model study: DataSage M3 with beam-1-0 | 20 | 80% | 100% | 0.94 | 0.59 | 75% | 0 | 100% | n/a | 1.0 | 118.2 | 24,951 |
| Model study: B2 single call with beam-1-0 | 20 | 0% | 5% | 1.00 | 0.03 | 67% | 0 | n/a | n/a | n/a | 2030.7 | 0 |
| Model study: DataSage M3 with inkling-small | 20 | 100% | 100% | 0.91 | 0.79 | 99% | 0 | 99% | 100% | 2.0 | 43.9 | 46,882 |
| Model study: B2 single call with inkling-small | 20 | 60% | 100% | 0.84 | 0.88 | 80% | 0 | n/a | n/a | n/a | 49.0 | 4,053 |
| Model study: DataSage M3 with laguna-s-2-1 | 20 | 75% | 100% | 0.95 | 0.49 | 70% | 0 | 100% | n/a | 1.0 | 343.1 | 26,542 |
| Model study: B2 single call with laguna-s-2-1 | 20 | 5% | 15% | 0.64 | 0.10 | 65% | 0 | n/a | n/a | n/a | 52.8 | 0 |
| Model study: DataSage M3 with muse-glimmer-30b | 20 | 100% | 100% | 0.90 | 0.83 | 99% | 0 | 100% | n/a | 2.0 | 76.4 | 83,062 |
| Model study: B2 single call with muse-glimmer-30b | 20 | 65% | 95% | 0.76 | 0.91 | 84% | 0 | n/a | n/a | n/a | 146.0 | 6,756 |
| Model study: DataSage M3 with muse-spark-open | 20 | 75% | 100% | 0.94 | 0.57 | 72% | 0 | 100% | 100% | 1.0 | 125.0 | 37,119 |
| Model study: B2 single call with muse-spark-open | 20 | 60% | 100% | 0.79 | 0.98 | 81% | 0 | n/a | n/a | n/a | 105.2 | 4,858 |
| Model study: DataSage M3 with ornith-1-5-35b-a3b | 20 | 75% | 100% | 0.94 | 0.52 | 72% | 0 | 99% | 100% | 1.0 | 105.7 | 33,516 |
| Model study: B2 single call with ornith-1-5-35b-a3b | 20 | 70% | 95% | 0.88 | 0.44 | 69% | 5 | n/a | n/a | n/a | 108.4 | 4,450 |

## sales-s303

| System | n | Answer correct | Completed | Detect P | Detect R | Errors handled | Damage | Tool-call OK | Recovery | Approvals (med) | Latency s (med) | Tokens (med) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 stakeholder baseline | 20 | 0% | 95% | 0.76 | 0.50 | 18% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B1 fixed script | 20 | 50% | 100% | 0.74 | 0.80 | 76% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B2 single LLM call | 20 | 30% | 90% | 0.71 | 0.78 | 76% | 4 | n/a | n/a | n/a | 28.5 | 2,342 |
| DataSage M3 (30B, default) | 20 | 100% | 100% | 0.83 | 0.80 | 94% | 0 | 100% | n/a | 3.0 | 34.3 | 59,822 |
| DataSage M3 (30B), compact memory | 20 | 85% | 95% | 0.85 | 0.68 | 83% | 0 | 92% | 48% | 2.0 | 45.2 | 76,418 |
| M3 without coverage check | 20 | 100% | 100% | 0.83 | 0.83 | 96% | 0 | 100% | n/a | 3.0 | 33.7 | 62,452 |
| M3 without validator | 20 | 100% | 100% | 0.84 | 0.83 | 96% | 0 | 100% | n/a | 3.0 | 33.0 | 61,160 |
| M3 without merge rule in prompt | 20 | 100% | 100% | 0.82 | 0.81 | 94% | 0 | 100% | n/a | 3.0 | 38.0 | 58,920 |
| M3, all risky fixes rejected | 20 | 5% | 100% | 0.75 | 0.86 | 27% | 0 | 100% | n/a | 3.0 | 36.8 | 72,927 |

## penguins-s303

| System | n | Answer correct | Completed | Detect P | Detect R | Errors handled | Damage | Tool-call OK | Recovery | Approvals (med) | Latency s (med) | Tokens (med) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 stakeholder baseline | 20 | 5% | 75% | 1.00 | 0.53 | 27% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B1 fixed script | 20 | 60% | 100% | 1.00 | 0.82 | 80% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B2 single LLM call | 20 | 55% | 100% | 0.77 | 0.73 | 76% | 26 | n/a | n/a | n/a | 27.4 | 2,519 |
| DataSage M3 (30B, default) | 20 | 95% | 100% | 0.88 | 0.79 | 92% | 0 | 100% | n/a | 1.5 | 34.1 | 61,680 |
| DataSage M3 (30B), compact memory | 20 | 90% | 100% | 0.93 | 0.72 | 88% | 0 | 96% | 77% | 2.0 | 38.9 | 76,106 |
| M3 without coverage check | 20 | 80% | 100% | 0.86 | 0.77 | 91% | 0 | 100% | n/a | 1.5 | 32.5 | 54,939 |
| M3 without validator | 20 | 95% | 100% | 0.87 | 0.77 | 91% | 0 | 100% | n/a | 1.5 | 35.2 | 57,818 |
| M3 without merge rule in prompt | 20 | 95% | 100% | 0.87 | 0.73 | 89% | 0 | 100% | n/a | 1.0 | 37.9 | 53,794 |
| M3, all risky fixes rejected | 20 | 20% | 100% | 0.88 | 0.86 | 57% | 0 | 100% | n/a | 1.5 | 33.9 | 73,420 |

## sales-s404

| System | n | Answer correct | Completed | Detect P | Detect R | Errors handled | Damage | Tool-call OK | Recovery | Approvals (med) | Latency s (med) | Tokens (med) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 stakeholder baseline | 20 | 10% | 85% | 0.81 | 0.67 | 24% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B1 fixed script | 20 | 45% | 100% | 0.77 | 0.89 | 79% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B2 single LLM call | 20 | 25% | 95% | 0.73 | 0.77 | 80% | 47 | n/a | n/a | n/a | 23.9 | 2,284 |
| DataSage M3 (30B, default) | 20 | 100% | 100% | 0.80 | 0.81 | 94% | 0 | 100% | n/a | 3.0 | 31.4 | 63,680 |
| DataSage M3 (30B), compact memory | 20 | 90% | 95% | 0.85 | 0.71 | 85% | 0 | 97% | 83% | 2.0 | 42.9 | 96,656 |
| M3 without coverage check | 20 | 100% | 100% | 0.80 | 0.79 | 90% | 0 | 100% | n/a | 3.0 | 25.6 | 62,388 |
| M3 without validator | 20 | 100% | 100% | 0.81 | 0.86 | 95% | 0 | 100% | n/a | 3.0 | 26.9 | 65,378 |
| M3 without merge rule in prompt | 20 | 100% | 100% | 0.82 | 0.82 | 91% | 0 | 100% | n/a | 2.5 | 27.1 | 63,230 |
| M3, all risky fixes rejected | 20 | 10% | 100% | 0.73 | 0.92 | 37% | 0 | 100% | 100% | 3.0 | 31.0 | 80,066 |

## penguins-s404

| System | n | Answer correct | Completed | Detect P | Detect R | Errors handled | Damage | Tool-call OK | Recovery | Approvals (med) | Latency s (med) | Tokens (med) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 stakeholder baseline | 20 | 5% | 60% | 1.00 | 0.60 | 32% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B1 fixed script | 20 | 55% | 100% | 1.00 | 0.85 | 82% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B2 single LLM call | 20 | 25% | 85% | 0.83 | 0.74 | 80% | 0 | n/a | n/a | n/a | 33.6 | 2,498 |
| DataSage M3 (30B, default) | 20 | 95% | 100% | 0.87 | 0.82 | 96% | 0 | 100% | 100% | 2.0 | 34.7 | 61,574 |
| DataSage M3 (30B), compact memory | 20 | 85% | 95% | 0.93 | 0.74 | 92% | 0 | 95% | 81% | 2.0 | 34.3 | 83,214 |
| M3 without coverage check | 20 | 85% | 100% | 0.87 | 0.82 | 93% | 0 | 100% | 100% | 2.0 | 26.7 | 60,330 |
| M3 without validator | 20 | 100% | 100% | 0.87 | 0.87 | 97% | 0 | 100% | 100% | 2.0 | 26.9 | 66,834 |
| M3 without merge rule in prompt | 20 | 100% | 100% | 0.86 | 0.79 | 96% | 0 | 100% | n/a | 2.0 | 32.9 | 59,767 |
| M3, all risky fixes rejected | 20 | 10% | 100% | 0.87 | 0.89 | 53% | 0 | 100% | 100% | 2.0 | 30.1 | 67,273 |

## sales-s505

| System | n | Answer correct | Completed | Detect P | Detect R | Errors handled | Damage | Tool-call OK | Recovery | Approvals (med) | Latency s (med) | Tokens (med) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 stakeholder baseline | 20 | 10% | 90% | 0.83 | 0.63 | 22% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B1 fixed script | 20 | 65% | 100% | 0.78 | 0.87 | 78% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B2 single LLM call | 20 | 55% | 95% | 0.70 | 0.77 | 80% | 7 | n/a | n/a | n/a | 29.4 | 2,364 |
| DataSage M3 (30B, default) | 20 | 100% | 100% | 0.82 | 0.85 | 94% | 0 | 100% | n/a | 2.0 | 36.0 | 66,856 |
| DataSage M3 (30B), compact memory | 20 | 85% | 85% | 0.89 | 0.77 | 91% | 0 | 96% | 73% | 2.5 | 38.6 | 92,091 |
| M3 without coverage check | 20 | 95% | 100% | 0.83 | 0.82 | 90% | 0 | 100% | n/a | 2.0 | 26.2 | 62,050 |
| M3 without validator | 20 | 100% | 100% | 0.84 | 0.83 | 93% | 0 | 100% | n/a | 2.0 | 26.0 | 64,728 |
| M3 without merge rule in prompt | 20 | 100% | 100% | 0.85 | 0.84 | 96% | 0 | 100% | n/a | 2.0 | 30.5 | 61,553 |
| M3, all risky fixes rejected | 20 | 20% | 100% | 0.78 | 0.85 | 35% | 0 | 100% | n/a | 3.0 | 29.6 | 73,478 |

## penguins-s505

| System | n | Answer correct | Completed | Detect P | Detect R | Errors handled | Damage | Tool-call OK | Recovery | Approvals (med) | Latency s (med) | Tokens (med) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 stakeholder baseline | 20 | 15% | 80% | 1.00 | 0.65 | 24% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B1 fixed script | 20 | 55% | 100% | 1.00 | 0.84 | 79% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B2 single LLM call | 20 | 60% | 100% | 0.93 | 0.77 | 79% | 0 | n/a | n/a | n/a | 27.2 | 2,502 |
| DataSage M3 (30B, default) | 20 | 95% | 100% | 0.90 | 0.83 | 96% | 0 | 100% | 100% | 2.0 | 34.4 | 56,898 |
| DataSage M3 (30B), compact memory | 20 | 90% | 95% | 0.91 | 0.72 | 94% | 0 | 98% | 100% | 2.0 | 20.3 | 63,864 |
| M3 without coverage check | 20 | 100% | 100% | 0.91 | 0.93 | 97% | 0 | 100% | n/a | 2.0 | 25.2 | 60,062 |
| M3 without validator | 20 | 95% | 100% | 0.90 | 0.88 | 96% | 0 | 100% | 100% | 2.0 | 24.4 | 56,786 |
| M3 without merge rule in prompt | 20 | 95% | 100% | 0.89 | 0.78 | 94% | 0 | 100% | n/a | 2.0 | 25.9 | 61,298 |
| M3, all risky fixes rejected | 20 | 15% | 100% | 0.91 | 0.94 | 55% | 0 | 100% | 100% | 2.0 | 28.0 | 66,395 |

## sales-hard

| System | n | Answer correct | Completed | Detect P | Detect R | Errors handled | Damage | Tool-call OK | Recovery | Approvals (med) | Latency s (med) | Tokens (med) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B1 fixed script | 20 | 20% | 100% | 0.79 | 0.84 | 79% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B2 single LLM call | 20 | 45% | 85% | 0.82 | 0.67 | 73% | 37 | n/a | n/a | n/a | 56.9 | 3,036 |
| DataSage M3 (30B, default) | 20 | 80% | 100% | 0.94 | 0.81 | 89% | 0 | 100% | n/a | 5.0 | 39.8 | 105,546 |
| DataSage M3 (235B) | 20 | 95% | 100% | 0.88 | 0.89 | 94% | 0 | 100% | n/a | 5.0 | 213.3 | 113,134 |
| DataSage M3 (gpt-oss-120b) | 20 | 80% | 100% | 0.92 | 0.62 | 81% | 0 | 82% | 25% | 4.0 | 81.6 | 100,166 |

## penguins-hard

| System | n | Answer correct | Completed | Detect P | Detect R | Errors handled | Damage | Tool-call OK | Recovery | Approvals (med) | Latency s (med) | Tokens (med) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B1 fixed script | 20 | 0% | 100% | 1.00 | 0.89 | 66% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B2 single LLM call | 20 | 65% | 95% | 0.99 | 0.76 | 78% | 600 | n/a | n/a | n/a | 42.2 | 3,052 |
| DataSage M3 (30B, default) | 20 | 100% | 100% | 1.00 | 0.82 | 95% | 0 | 100% | n/a | 5.0 | 43.8 | 94,346 |
| DataSage M3 (235B) | 20 | 100% | 100% | 1.00 | 0.80 | 99% | 0 | 100% | n/a | 4.5 | 134.3 | 92,750 |
| DataSage M3 (gpt-oss-120b) | 20 | 100% | 100% | 1.00 | 0.58 | 81% | 0 | 89% | 30% | 3.5 | 50.0 | 69,716 |

## sales-hard2

| System | n | Answer correct | Completed | Detect P | Detect R | Errors handled | Damage | Tool-call OK | Recovery | Approvals (med) | Latency s (med) | Tokens (med) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B1 fixed script | 20 | 10% | 100% | 0.78 | 0.86 | 83% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| DataSage M3 (30B, default) | 20 | 70% | 100% | 0.89 | 0.81 | 88% | 0 | 100% | n/a | 5.0 | 20.1 | 90,590 |
| DataSage M3 (235B) | 20 | 100% | 100% | 0.86 | 0.86 | 89% | 0 | 100% | n/a | 5.0 | 148.3 | 96,546 |
| DataSage M3 (gpt-oss-120b) | 20 | 100% | 100% | 0.93 | 0.68 | 81% | 0 | 85% | 27% | 4.0 | 81.4 | 88,559 |

## penguins-hard2

| System | n | Answer correct | Completed | Detect P | Detect R | Errors handled | Damage | Tool-call OK | Recovery | Approvals (med) | Latency s (med) | Tokens (med) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B1 fixed script | 20 | 5% | 100% | 1.00 | 0.89 | 64% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| DataSage M3 (30B, default) | 20 | 100% | 100% | 1.00 | 0.84 | 97% | 0 | 100% | n/a | 4.0 | 19.5 | 95,370 |
| DataSage M3 (235B) | 20 | 95% | 100% | 1.00 | 0.79 | 98% | 0 | 100% | n/a | 5.0 | 142.2 | 99,630 |
| DataSage M3 (gpt-oss-120b) | 20 | 100% | 100% | 1.00 | 0.59 | 81% | 0 | 85% | 23% | 3.0 | 57.3 | 72,234 |
