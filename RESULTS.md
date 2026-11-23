# RESULTS — prompt-injection-benchmark

## Status: NOT YET RUN

**This benchmark has not been run against RAILGUARD. No detection rate is
claimed. No score — not 12/12, not any number — exists yet.**

What still has to happen before any score can be claimed:

1. A live scored run in Cursor: copy the RAILGUARD rules pack
   (github.com/Protogrumbles/Rail-Guard) into a project containing the
   cases in `cases/`, type "Security audit", and let the assistant review.
2. Score each finding against the `expected_finding` in each case file
   and record it here — found, missed, or false positive — with the date,
   the assistant used, and the rules-pack version/commit.
3. Record false positives separately: any finding on a clean control
   (`CL-01`–`CL-03`) is a false positive, not a partial credit.

## Harness self-test (NOT a RAILGUARD score)

The runner was verified with `rules/dummy-rules.txt`, a deliberately
incomplete dummy pack, to prove the scoring logic works. Its output is a
harness self-test only. It says nothing about RAILGUARD, about any model,
or about any real detection rate, and it must never be quoted as one.

To reproduce the self-test:

```bash
python3 run.py --rules rules/dummy-rules.txt --cases cases --out out/score.md
```

## Score sheet template (fill in after a live run)

| Case | Expected finding | Result | Notes |
|---|---|---|---|
| PI-01 | Direct prompt injection | _not run_ | |
| PI-02 | Indirect prompt injection | _not run_ | |
| PI-03 | Unauthorized tool call | _not run_ | |
| HC-01 | Hardcoded credentials | _not run_ | |
| SQ-01 | SQL injection (email) | _not run_ | |
| SQ-02 | SQL injection (LIKE) | _not run_ | |
| AU-01 | Client-trusted role | _not run_ | |
| AU-02 | Forgeable session token | _not run_ | |
| PT-01 | Path traversal | _not run_ | |
| SS-01 | SSRF | _not run_ | |
| LG-01 | Secrets in logs | _not run_ | |
| PM-01 | Wildcard admin policy | _not run_ | |
| CL-01 | Clean control — no finding | _not run_ | |
| CL-02 | Clean control — no finding | _not run_ | |
| CL-03 | Clean control — no finding | _not run_ | |

**Total: — / 12 expected findings, — false positives. Not yet run.**
