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
| M3 without coverage check | 20 | 100% | 100% | 0.89 | 0.80 | 88% | 0 | 100% | n/a | 3.0 | 28.8 | 67,619 |
| M3 without validator | 20 | 95% | 100% | 0.88 | 0.83 | 87% | 0 | 100% | n/a | 2.0 | 27.5 | 65,152 |
| M3 without merge rule in prompt | 20 | 100% | 100% | 0.85 | 0.78 | 89% | 0 | 100% | n/a | 2.5 | 32.2 | 72,356 |
| M3, all risky fixes rejected | 20 | 5% | 100% | 0.82 | 0.91 | 35% | 0 | 100% | n/a | 3.0 | 38.4 | 79,004 |

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
| M3 without coverage check | 20 | 75% | 100% | 0.81 | 0.69 | 87% | 0 | 100% | n/a | 2.0 | 22.8 | 54,862 |
| M3 without validator | 20 | 90% | 100% | 0.82 | 0.73 | 90% | 0 | 100% | 100% | 2.0 | 44.2 | 62,010 |
| M3 without merge rule in prompt | 20 | 90% | 100% | 0.80 | 0.64 | 88% | 0 | 100% | n/a | 2.0 | 44.6 | 55,112 |
| M3, all risky fixes rejected | 20 | 5% | 100% | 0.83 | 0.83 | 43% | 0 | 100% | n/a | 2.0 | 45.7 | 69,812 |

## sales-test

| System | n | Answer correct | Completed | Detect P | Detect R | Errors handled | Damage | Tool-call OK | Recovery | Approvals (med) | Latency s (med) | Tokens (med) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 stakeholder baseline | 20 | 10% | 85% | 0.82 | 0.51 | 22% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B1 fixed script | 20 | 55% | 100% | 0.78 | 0.78 | 76% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B2 single LLM call | 20 | 45% | 90% | 0.74 | 0.72 | 78% | 4 | n/a | n/a | n/a | 30.0 | 2,283 |
| DataSage (30B) + exclusion rule | 20 | 100% | 100% | 0.84 | 0.84 | 93% | 0 | 100% | n/a | 2.5 | 16.3 | 63,062 |
| DataSage M3 (30B, default) | 20 | 100% | 100% | 0.85 | 0.84 | 91% | 0 | 100% | n/a | 2.0 | 16.1 | 61,980 |
| DataSage M3 (30B), compact memory | 20 | 75% | 85% | 0.91 | 0.76 | 81% | 0 | 99% | 100% | 2.0 | 40.9 | 69,735 |
| M3 without coverage check | 20 | 100% | 100% | 0.87 | 0.87 | 92% | 0 | 100% | n/a | 2.5 | 33.5 | 59,505 |
| M3 without validator | 20 | 100% | 100% | 0.87 | 0.89 | 93% | 0 | 100% | n/a | 3.0 | 35.8 | 64,076 |
| M3 without merge rule in prompt | 20 | 100% | 100% | 0.85 | 0.83 | 90% | 0 | 100% | n/a | 2.5 | 39.9 | 65,212 |
| M3, all risky fixes rejected | 20 | 20% | 100% | 0.86 | 0.94 | 40% | 0 | 99% | 50% | 3.0 | 45.4 | 77,943 |

## penguins-test

| System | n | Answer correct | Completed | Detect P | Detect R | Errors handled | Damage | Tool-call OK | Recovery | Approvals (med) | Latency s (med) | Tokens (med) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 stakeholder baseline | 20 | 0% | 50% | 1.00 | 0.51 | 32% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B1 fixed script | 20 | 35% | 100% | 1.00 | 0.84 | 74% | 0 | n/a | n/a | n/a | 0.0 | 0 |
| B2 single LLM call | 20 | 50% | 95% | 0.92 | 0.80 | 82% | 0 | n/a | n/a | n/a | 42.5 | 2,524 |
| DataSage (30B) + exclusion rule | 20 | 85% | 100% | 0.89 | 0.78 | 92% | 0 | 100% | n/a | 2.0 | 14.3 | 53,600 |
| DataSage M3 (30B, default) | 20 | 85% | 100% | 0.89 | 0.74 | 93% | 0 | 100% | n/a | 2.0 | 15.0 | 56,854 |
| DataSage M3 (30B), compact memory | 20 | 80% | 100% | 0.94 | 0.71 | 88% | 0 | 97% | 75% | 2.0 | 34.1 | 58,151 |
| M3 without coverage check | 20 | 80% | 100% | 0.90 | 0.81 | 94% | 0 | 100% | n/a | 2.0 | 30.8 | 55,280 |
| M3 without validator | 20 | 90% | 100% | 0.90 | 0.80 | 95% | 0 | 100% | n/a | 2.0 | 32.1 | 60,926 |
| M3 without merge rule in prompt | 20 | 90% | 100% | 0.89 | 0.79 | 93% | 0 | 100% | n/a | 2.0 | 40.4 | 61,152 |
| M3, all risky fixes rejected | 20 | 10% | 95% | 0.90 | 0.85 | 48% | 0 | 100% | n/a | 2.0 | 33.4 | 61,784 |

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
