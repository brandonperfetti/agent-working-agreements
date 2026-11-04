#!/usr/bin/python3
"""SessionStart hook (matcher: compact): restate what compaction must not lose.

The working agreements are read into the thread at session start, not into the
cached prefix, so a compaction can reduce them to a summary. This puts the
lines that matter most back into context after every compaction.
"""
import json

AGREEMENTS = "~/dev/sansfaux/agent-working-agreements"

CONTEXT = """Context was just compacted. The working agreements you read at session start may survive only as a summary. Still binding:
- RULE ZERO: every commit you make carries the author email brandon@brandonperfetti.com, exactly. No Co-Authored-By or session trailer, generated-with footer or crediting line on any commit, PR body, issue or thread reply.
- Mode: autonomous by default for Claude Code, as B0's pickup guard decides. Only Brandon merges develop, main and master.
- If the summary does not carry what your next delivery, dispatch, repository write or GitHub action needs, re-read {0}/AGENT-WORKING-AGREEMENTS.md, {0}/profiles/sansfaux.md and {0}/clients/claude-code.md.""".format(AGREEMENTS)

print(
    json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": CONTEXT,
            }
        }
    )
)
