"""D2 exposure audit summary (report-only). Reads the saved traces; launches nothing; prints no answers.

Usage, from the repository root: python3 exposure_summary.py CODEX_RUN_DIR CLAUDE_RUN_DIR
Prints one JSON object with, per arm: calls with phrase observations, matched lines, lines that do not
contain the task's own `handoff_refs/` folder name, hits on each design word, outside-path requests by kind,
whether any outside request returned a listing of a path outside the workspace, and permission denials."""
import json, re, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from earshot.exposure import tools  # the same tool parser the stage used

DESIGN_WORDS = ('required_memory_refs', 'coalition', 'preferred pair', 'decoded', 'memory ref')


def summarise(run):
    out = Counter(); words = Counter(); kinds = Counter(); returned_outside = 0; denials = 0
    for path in sorted((Path(run) / 'traces').glob('*.json')):
        row = json.loads(path.read_text())
        audit = row.get('exposure_audit') or {}
        phrases = audit.get('phrase_observations', [])
        out['calls'] += 1
        out['calls_with_phrase_observations'] += bool(phrases)
        out['phrase_lines'] += len(phrases)
        out['phrase_lines_without_handoff_refs'] += sum('handoff_refs' not in p['text'] for p in phrases)
        for p in phrases:
            for w in DESIGN_WORDS:
                words[w] += bool(re.search(re.escape(w), p['text'], re.I))
        outside = audit.get('outside_workspace_observations', [])
        out['calls_with_outside_observations'] += bool(outside)
        kinds.update(o.get('kind') for o in outside)
        ids = {o['tool_id'] for o in outside}
        for t in tools(row):
            if t['id'] in ids:
                for line in t['output'].splitlines():
                    s = line.strip()
                    # a returned path outside the workspace would start with '/' or '../' (not '../workspace')
                    if s.startswith('/') or (s.startswith('../') and not s.startswith('../workspace')):
                        returned_outside += 1
        denials += len(audit.get('permission_denials', []))
    return dict(out, design_word_hits=dict((w, words[w]) for w in DESIGN_WORDS),
                outside_kinds=dict(kinds), outside_requests_returning_outside_paths=returned_outside,
                permission_denials=denials)


if __name__ == '__main__':
    codex, claude = sys.argv[1:3]
    print(json.dumps({'codex': summarise(codex), 'claude': summarise(claude)}, indent=2, sort_keys=True))
