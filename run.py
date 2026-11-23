#!/usr/bin/env python3
"""prompt-injection-benchmark runner. Stdlib only.

Runs a rules file (see rules/FORMAT.md) against the scored cases in
cases/ and produces a score sheet: found / missed per case, and
false positives on clean controls.

This runner scores a *rules representation*, not a live assistant run.
A score from this runner — especially with the dummy rules — is a harness
self-test, never a RAILGUARD detection score. See RESULTS.md.
"""
import argparse, json, re, sys
from pathlib import Path

VERSION = "0.1.0"

def parse_rules(path):
    """Parse a rules file into [{rule, category, patterns:[(kind, value)]}]."""
    text = Path(path).read_text()
    rules, cur = [], None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("rule:"):
            cur = {"rule": line.split(":", 1)[1].strip(), "category": "", "patterns": []}
            rules.append(cur)
        elif line.startswith("category:") and cur is not None:
            cur["category"] = line.split(":", 1)[1].strip()
        elif line.startswith("- ") and cur is not None:
            pat = line[2:].strip()
            if pat.startswith("/") and pat.rstrip("/").endswith("/") or (pat.startswith("/") and pat.count("/") >= 2):
                body = pat[1:pat.rfind("/")]
                cur["patterns"].append(("regex", body))
            else:
                cur["patterns"].append(("substr", pat))
        elif cur is None:
            raise ValueError(f"rules file: line outside a rule block: {raw!r}")
    for r in rules:
        if not r["category"] or not r["patterns"]:
            raise ValueError(f"rules file: rule {r['rule']!r} is missing a category or patterns")
    if not rules:
        raise ValueError("rules file contains no rules")
    return rules

def pattern_matches(kind, value, snippet):
    if kind == "substr":
        return value.lower() in snippet.lower()
    try:
        return re.search(value, snippet, re.IGNORECASE) is not None
    except re.error as e:
        raise ValueError(f"invalid regex {value!r}: {e}")

def load_cases(cases_dir):
    cases = []
    for p in sorted(Path(cases_dir).glob("*.json")):
        cases.append(json.loads(p.read_text()))
    if not cases:
        raise ValueError(f"no case files found in {cases_dir}")
    return cases

def score(rules, cases):
    """Return per-case results + totals."""
    results = []
    for case in cases:
        matched = []
        for rule in rules:
            # Scored cases: only a rule in the case's category can find it.
            # Clean controls: ANY rule matching is a false positive, whatever
            # its category — a rule that flags clean code is over-matching.
            if not case.get("is_control") and rule["category"] != case["category"]:
                continue
            for kind, value in rule["patterns"]:
                if pattern_matches(kind, value, case["snippet"]):
                    matched.append(rule["rule"])
                    break
        if case.get("is_control"):
            result = "false_positive" if matched else "clean"
        else:
            result = "found" if matched else "missed"
        results.append({"id": case["id"], "category": case["category"],
                        "severity": case["severity"], "title": case["title"],
                        "result": result, "matched_rules": sorted(set(matched)),
                        "expected_finding": case["expected_finding"]})
    scored = [r for r in results if not r["id"].startswith("CL-")]
    controls = [r for r in results if r["id"].startswith("CL-")]
    totals = {"found": sum(1 for r in scored if r["result"] == "found"),
              "missed": sum(1 for r in scored if r["result"] == "missed"),
              "total_scored": len(scored),
              "false_positives": sum(1 for r in controls if r["result"] == "false_positive"),
              "controls_clean": sum(1 for r in controls if r["result"] == "clean"),
              "total_controls": len(controls)}
    return results, totals

def build_score_md(results, totals, rules_path):
    lines = ["# Score sheet", "",
             f"Rules file: `{rules_path}`",
             f"**Found: {totals['found']} / {totals['total_scored']}** · "
             f"Missed: {totals['missed']} · "
             f"False positives (clean controls flagged): {totals['false_positives']} / {totals['total_controls']}",
             "",
             "> This score sheet describes one run of one rules file against "
             "these cases. It is not a RAILGUARD detection score unless the run "
             "was the live scored run described in RESULTS.md.",
             "",
             "| Case | Category | Severity | Result | Matched rules |",
             "|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['id']} | {r['category']} | {r['severity']} | **{r['result']}** | {', '.join(r['matched_rules']) or '—'} |")
    lines += ["", "## Per-case detail", ""]
    for r in results:
        lines.append(f"### {r['id']} — {r['result']}")
        lines.append("")
        lines.append(f"{r['title']}")
        lines.append("")
        lines.append(f"Expected: {r['expected_finding']}")
        lines.append("")
    return "\n".join(lines)

def main(argv=None):
    p = argparse.ArgumentParser(prog="run.py", description="Score a rules file against the benchmark cases.")
    p.add_argument("--version", action="version", version=VERSION)
    p.add_argument("--rules", required=True)
    p.add_argument("--cases", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--json-out")
    args = p.parse_args(argv)
    try:
        rules = parse_rules(args.rules)
        cases = load_cases(args.cases)
        results, totals = score(rules, cases)
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_score_md(results, totals, args.rules))
    if args.json_out:
        j = Path(args.json_out); j.parent.mkdir(parents=True, exist_ok=True)
        j.write_text(json.dumps({"totals": totals, "results": results}, indent=2) + "\n")
    print(f"Found {totals['found']}/{totals['total_scored']} · missed {totals['missed']} · "
          f"false positives {totals['false_positives']}/{totals['total_controls']}")
    print(f"Wrote {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
