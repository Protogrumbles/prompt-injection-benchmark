# Rules-file format

A rules file is plain text. One rule per block, separated by a blank line.
Each block has three fields:

```
rule: <rule-id>
category: <case category this rule targets, e.g. prompt-injection>
patterns:
  - <plain substring or /regex/>
  - <another pattern>
```

- `rule` — a short id, e.g. `04-llm-prompt-injection`. Free text; it is
  reported in the score sheet so a miss can be traced to a rule.
- `category` — the case category the rule is meant to catch. A rule only
  scores against cases whose `category` matches.
- `patterns` — one per line, each starting with `- `. A pattern is either
  a plain substring (matched case-insensitively against the case snippet)
  or a regex wrapped in `/.../` (matched with `re.search`, case-insensitive).

A case is **found** if any rule with a matching `category` has any pattern
that matches the case's `snippet`. A finding on a clean control case is a
**false positive** — and for controls, *any* rule matching counts, whatever
its category, because a rule that flags clean code is over-matching.

This format is deliberately minimal: it exists so the harness can be
tested and so a rules pack can be *represented* for scoring. It is not
RAILGUARD itself. RAILGUARD's real rules are Markdown rule files for an
AI assistant (github.com/Protogrumbles/Rail-Guard); converting them to
this format by hand is a lossy approximation, and any score produced that
way must say so.

## Example

```
rule: 04-llm-prompt-injection
category: prompt-injection
patterns:
  - SYSTEM_PROMPT +
  - /concatenat.*prompt/i
```
