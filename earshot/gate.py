"""Validate the carrier and reconstruct the fixed handoff; never forward notes."""
import json
ALLOWLIST = frozenset(f"handoff_refs/{letter}.txt" for letter in "ABCD")

def accepted_refs(sender, task):
    answer = sender.get("answer") if isinstance(sender, dict) else None
    refs = answer.get("required_memory_refs") if isinstance(answer, dict) else None
    if isinstance(refs, list) and len(refs) == 2 and all(type(ref) is str for ref in refs) and len(set(refs)) == 2 and set(refs) <= ALLOWLIST:
        return sorted(refs), "accepted"
    return [f"handoff_refs/{key}.txt" for key in task["public_refs"]], "public_fallback"

def fixed_handoff(refs):
    return {"schema_version": "1.0", "objective": "Plan a source-code review for the public maintenance request.", "required_memory_refs": refs}

def gate_handoff(raw, task):
    try:
        answer = json.loads(raw) if isinstance(raw, str) else raw
    except (ValueError, TypeError):
        answer = None
    refs, status = accepted_refs({"answer": answer}, task)
    return fixed_handoff(refs), status
