# prompt-injection-benchmark

A scored-case harness for testing a security-review rules pack against
known-vulnerable code — **the harness and the dataset skeleton only**.

> **No detection score is claimed here.** `RESULTS.md` says so explicitly:
> this benchmark has **NOT YET BEEN RUN** against RAILGUARD. No detection
> rate, no "12/12", no claim of any kind is made until a live scored run
> happens in Cursor. See `RESULTS.md`.

## What it is

- **12 scored cases** (`cases/`) mirroring the categories in RAILGUARD's
  `EXPECTED-FINDINGS.md` (8 vulnerable files, 12 expected findings), plus
  **3 clean control cases** that a correct run must *not* flag.
- A **runner** (`run.py`, stdlib only) that takes a rules file, runs it
  against the cases, and produces a score sheet: found / missed /
  false-positive per case.
- A **rules-file format** (`rules/FORMAT.md`): one rule per block, with a
  name, a category, and plain-text / regex patterns. A rules pack is a
  *review* input — the runner checks whether the pack's patterns match the
  vulnerable snippet. It does not execute code and does not itself judge
  security.
- A **dummy rules file** (`rules/dummy-rules.txt`) used only to verify the
  scoring logic. Its results are labeled a harness self-test, never a
  RAILGUARD score.

## What it is NOT

- **Not a scanner.** Nothing here executes the case code or scans a real
  codebase. The companion rules pack, RAILGUARD
  (github.com/Protogrumbles/Rail-Guard), is itself a **review framework,
  not a scanner** — findings come from an AI assistant following the rules,
  verified by a human.
- **Not a RAILGUARD result.** The cases mirror RAILGUARD's expected
  findings so a future live run can be scored against them; mirroring the
  categories is not the same as running the pack.
- **Not a claim about any model.** A score here would describe one run of
  one rules pack in one assistant, on one day — not a general detection rate.

## The 12 scored cases

Mirrored from RAILGUARD's `EXPECTED-FINDINGS.md` (categories only — the
rules were not copied, and the snippets below are short, original,
clearly-marked fictional illustrations of each flaw class, not the demo
app's code):

| Case | Category | Severity |
|---|---|---|
| PI-01 | Direct prompt injection — user input concatenated into system prompt | Critical |
| PI-02 | Indirect prompt injection — untrusted fetched web content in prompt | Critical |
| PI-03 | Tool call triggered by model output with no authorization check | Critical |
| HC-01 | Hardcoded credentials in source | Critical |
| SQ-01 | SQL injection — interpolated email in query | Critical |
| SQ-02 | SQL injection — concatenated term in LIKE clause | Critical |
| AU-01 | Client-trusted role (admin from header / body field) | Critical |
| AU-02 | Forgeable, unsigned session token | Critical |
| PT-01 | Path traversal — unvalidated file path joined into filesystem path | High |
| SS-01 | SSRF — attacker-controlled URL fetched server-side, no allowlist | High |
| LG-01 | Secrets written to logs | High |
| PM-01 | Wildcard admin policy for every authenticated user | High |

Clean controls (must score 0 findings): `CL-01` parameterized query,
`CL-02` secrets from environment variables, `CL-03` structured
system/user message separation.

## Quick start

```bash
# Verify the harness itself with the dummy rules file (self-test only)
python3 run.py --rules rules/dummy-rules.txt --cases cases --out out/score.md

# Score a real rules pack (format in rules/FORMAT.md)
python3 run.py --rules /path/to/your-rules.txt --cases cases --out out/score.md
```

The score sheet lists, per case, `found` / `missed`, and flags any finding
on a clean control as a `false_positive`. A perfect run is 12/12 found,
0 false positives. See `RESULTS.md` for what a real RAILGUARD run still
needs before any score is claimed.

## How to run the real RAILGUARD scored run (not yet done)

1. Copy the RAILGUARD rules into a project containing these cases
   (or the original demo app) in Cursor.
2. Type "Security audit" and let the assistant review.
3. Score each finding against `cases/*.json` (`expected_finding`) and
   record it in `RESULTS.md` — found, missed, or false positive — with
   the date, the assistant, and the rules-pack version.
4. Do **not** edit the case files to fit the result. If a case is missed,
   that is a finding about the rules pack, not about the case.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

Tests verify the scoring logic on the dummy rules file: the dummy pack is
designed to match some cases and miss others, and the runner must report
exactly that — found, missed, and a false positive on a control when a
pattern over-matches. No RAILGUARD score is produced or implied.

## Layout

```
run.py                  Runner (stdlib only)
cases/                  12 scored cases + 3 clean controls (JSON)
rules/FORMAT.md         Rules-file format
rules/dummy-rules.txt   Dummy pack for harness self-test ONLY
RESULTS.md              NOT YET RUN — no detection rate claimed
tests/test_runner.py
```
