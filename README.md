# Daily Reflection Tree
### DT Fellowship Assignment — Role Simulation

A deterministic, LLM-free end-of-day reflection tool built on three psychological axes.

---

## Repository Structure

```
/tree/
  reflection-tree.json    ← Part A: the complete tree (28 nodes)
  tree-diagram.md         ← Part A: Mermaid visual diagram + node index
/agent/
  agent.py                ← Part B: Python CLI agent (no dependencies)
/transcripts/
  persona-1-transcript.md ← Victor / Contributing / Altrocentric path
  persona-2-transcript.md ← Victim / Entitled / Self-Centric path
write-up.md               ← Design rationale (Part A)
README.md                 ← This file
```

---

## Part A — The Tree

`tree/reflection-tree.json` contains the full tree as structured JSON. Every conversation path can be traced by reading the file — no code required.

**Stats:**
| Node type | Count |
|-----------|-------|
| start | 1 |
| question | 9 |
| decision | 7 |
| reflection | 6 |
| bridge | 2 |
| summary | 1 |
| end | 1 |
| **Total** | **27** |

**Three axes, in sequence:**
1. **Locus of Control** (Rotter) × **Growth Mindset** (Dweck) — *Victim ↔ Victor*
2. **Psychological Entitlement** (Campbell) × **OCB** (Organ) — *Entitlement ↔ Contribution*
3. **Self-Transcendence** (Maslow) × **Perspective-Taking** (Batson) — *Self-Centric ↔ Altrocentric*

There are **8 unique conversation end-states** (2³), each with a distinct summary reflection.

### How to trace a path manually

1. Start at node `START`
2. Follow `target` field to reach the next node
3. At `question` nodes: pick an option, record its `signal`
4. At `decision` nodes: evaluate the `condition` on each option to find the next node
5. At `reflection` / `bridge`: follow `target`
6. Reach `SUMMARY` → use the accumulated axis dominants to select the `summary_reflections` key

---

## Part B — Running the Agent

**Requirements:** Python 3.10+ (standard library only, no pip installs needed)

```bash
# Basic run
python agent.py

# Specify a different tree file
python agent.py --tree path/to/reflection-tree.json

# Save the session as a transcript
python agent.py --transcript
```

The agent:
- Loads the tree from JSON at runtime (not hardcoded)
- Renders each node to the terminal
- Waits for input only at `question` nodes
- Auto-advances through `decision`, `bridge`, `start`, `reflection`, `end`
- Accumulates axis signals and resolves dominant at each decision point
- Interpolates `{node_id.value}` placeholders in reflection text
- Produces an 8-way personalised summary at the end
- Optionally saves the full transcript to `transcripts/`

---

## Key Design Decisions

### No LLM at runtime
The tree is a static data file. The agent reads JSON and follows edges. All "intelligence" is encoded in the question design, the option labels, and the signal tags — by a human, in advance.

### Determinism
Given the same answers, the same path is always walked and the same reflections shown. This makes the tool auditable: a manager could replay any session given the answers.

### No moralising
Every reflection node was written to name a pattern without shaming it. The external/entitlement/self-centric path ("A tough day on every dimension") ends with an honest observation and one small, actionable invitation — not a verdict.

---

## Psychological Grounding

| Axis | Framework | Citation |
|------|-----------|----------|
| Locus | Locus of Control | Rotter (1954) |
| Locus | Growth Mindset | Dweck (2006) |
| Orientation | Psychological Entitlement | Campbell et al. (2004) |
| Orientation | Organizational Citizenship Behavior | Organ (1988) |
| Radius | Self-Transcendence | Maslow (1969) |
| Radius | Perspective-Taking | Batson (2011) |

---

## Guardrails Against AI Hallucination (Build Process)

This tool itself contains zero LLM calls. During the *design* process, AI was used as a sparring partner — but all outputs were manually reviewed against the source psychology before inclusion. Specific controls used:

1. **Fixed options only** — the employee never provides free text, so there is nothing to misclassify
2. **Explicit signal tagging** — every option's `signal` was manually assigned after evaluating whether the response truly reflects that pole of the axis
3. **Pre-written summaries** — all 8 summary reflections were authored by a human and reviewed for tone; no generation at runtime
4. **Condition logic is plain string matching** — no probabilistic inference, no embeddings, no model calls
5. **AI critique pass** — after designing questions, Claude was asked to roleplay both personas and flag any option that felt ambiguous or leading; several options were revised as a result
