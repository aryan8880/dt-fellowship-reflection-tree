# Write-Up: Daily Reflection Tree — Design Rationale

**Candidate Submission | DT Fellowship Assignment**

---

## Why These Questions

The hardest design problem in this assignment is not structural — it's epistemic. A bad reflection tool asks "were you a good person today?" A good one asks questions that surface the answer without telling you what it should be.

Each question in this tree was chosen because it is **revelatory by proxy**. Instead of asking "Do you have an internal locus of control?", the tree asks: *"When something went well today, what made it happen?"* The employee isn't being assessed — they're simply recounting. But the options they choose reveal their locus pattern.

### Axis 1 — Locus of Control (Rotter, 1954) & Growth Mindset (Dweck, 2006)

The opening question ("one word for today") is not just warmth. It is the first signal. "Productive" and "Mixed" describe the day in terms of output — already slightly internal ("I produced"). "Tough" and "Frustrating" describe the day in terms of what it *did to* the person — already slightly external. This early signal routes the second question appropriately.

The follow-up questions differ by tone. For those who described a good day: *"What drove it?"* — testing whether they attribute success to themselves or to circumstance. For those who had a hard day: *"What was your first instinct?"* — testing whether their default was to seek control or to wait. Both question variants tap the same locus construct, but from the angle most relevant to where the employee actually is.

The third Axis 1 question (A1_Q_CHOICE or A1_Q_MOMENT) increases depth. For internal-scoring employees, the question sharpens the lens: not just "did you have agency" but "what guided your decisions?" For external-scoring employees, it offers a gentle reframe: not "you were passive" but "was there a small choice available — even one you didn't take?"

This follows Dweck's insight that mindset is trainable through specific, directed noticing — not through praise or blame.

### Axis 2 — Psychological Entitlement (Campbell et al., 2004) & OCB (Organ, 1988)

The entitlement literature is careful about one thing: **entitled people do not know they are entitled**. This is the design constraint. The Axis 2 questions cannot use the word "deserve" or frame the employee as a taker. Instead, they describe behaviours and let the employee self-select.

The A2_OPEN options are all surface-plausible. "I felt my effort wasn't seen" is a real, human experience — not a character flaw. But if this is the most salient moment from the day, it is a signal. The branching follows: contribution-leaning employees are asked *why* they gave (probing whether it's genuinely other-directed or still approval-seeking); entitlement-leaning employees are asked *what they did with* the feeling (probing whether they converted it into action or held it as grievance).

### Axis 3 — Self-Transcendence (Maslow, 1969) & Perspective-Taking (Batson, 2011)

Maslow's 1969 paper — less cited than his pyramid — argues that the highest human need is not self-actualisation but transcendence: concern for something beyond the self. Batson's work on perspective-taking shows that even the *act* of noticing another's experience changes behaviour, independent of whether you act on it.

The Axis 3 questions are designed to widen the frame gradually. A3_OPEN asks who came to mind during *today's* challenge — not abstractly, but in a specific moment. The options move from narrow (just me) to wide (the end user). This gradation is intentional: there's no jump from self to altruism. The follow-up questions then test whether the awareness translated into anything, or remained notional.

---

## How I Designed the Branching

### The core trade-off: sensitivity vs. noise

A more fine-grained tree would have 5-6 signal options per question, allowing for nuanced routing. But with 3-4 options per question and 2-3 questions per axis, the signal can be ambiguous — a 1:1 internal:external split is possible.

My approach: **last answer wins in a tie.** The final question in each axis is the deepest and most deliberate. If the accumulated signal is tied, the routing follows the most recent, considered answer rather than averaging. This avoids false precision from a 50/50 split.

### Why bridges are plain, not clever

The bridge nodes are intentionally low-affect. After a reflection node — which asks something of the employee — the brain needs a brief neutral transition. An emotionally loaded bridge competes with the reflection. Plain language ("Now let's look at what you gave") resets the frame cleanly.

### The summary node design

The summary uses **state interpolation**, not LLM generation. There are 8 possible end states (2³ axis outcomes), each with a pre-written two-sentence reflection. This is the hardest piece to write well — each reflection must be honest without shaming, specific without overfitting, and useful without prescribing. I wrote them last, after testing all 8 paths manually.

---

## What I'd Improve With More Time

1. **Cross-axis interpolation.** The current summary tells you your three axis scores side-by-side. A better summary would reference *how they interact* — e.g., "You had high agency today but narrowed your circle. That combination often means you were solving the right problem for the wrong radius." This requires more complex state logic, but is achievable without an LLM.

2. **Longitudinal signals.** The tree currently treats each session as independent. With session history stored locally, the summary could reference "this is the third time this week you've described the day as 'frustrating'" — far more powerful than any single-session insight.

3. **More branching on Axis 2.** The entitlement axis is the hardest to surface without moralising. I would add a question that asks about a *past* interaction this week — because entitlement patterns show up more clearly over time than in a single day.

4. **Confidence calibration.** Each question could ask not just *what* the employee chose but *how confident they are* in their answer (1-3 scale). Low-confidence answers would route to a follow-up; high-confidence answers would advance. This would surface uncertainty as a signal rather than forcing binary paths.

---

## Psychological Sources

- Rotter, J.B. (1954). *Social Learning and Clinical Psychology.* Prentice-Hall.
- Dweck, C. (2006). *Mindset: The New Psychology of Success.* Random House.
- Campbell, W.K., Bonacci, A.M., Shelton, J., Exline, J.J., & Bushman, B.J. (2004). Psychological entitlement: Interpersonal consequences and validation of a self-report measure. *Journal of Personality Assessment.*
- Organ, D.W. (1988). *Organizational Citizenship Behavior: The Good Soldier Syndrome.* Lexington Books.
- Maslow, A.H. (1969). The farther reaches of human nature. *Journal of Transpersonal Psychology.*
- Batson, C.D. (2011). *Altruism in Humans.* Oxford University Press.
