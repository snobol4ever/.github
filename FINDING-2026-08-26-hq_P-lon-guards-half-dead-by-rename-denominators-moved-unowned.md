# FINDING — the three `lon` guards were keyed on a NAME; the re-grid renamed it, and two of them died silently

**Seat:** `hq_P` (HQ-PERFORMANCE, `/home/claude_P`) · **s273** · 2026-08-26
**Trees:** SCRIP `8e03e1e0` · corpus `b1649085f` · .github `ffa535d4` (all after `merge --ff-only origin/main`)
**Instrument:** the guards' own patterns executed against the live path — not read, not reasoned about.

## The claim I was given, and how it turned out to be one-third true

`hq_C` routed this to me as: *"the corpus/programs/lon/ OFF LIMITS section is VOID (Lon s269, RULES.md:44, 'I retract
all of it') — but ⛔ THE HARNESSES HAVE NOT CAUGHT UP: `scorecard_snobol4.sh`, `test_gate_argnote_sweep.sh` and
`util_oracle_flag_sweep.sh` still prune or refuse `*/programs/lon/*` BY CONSTRUCTION."*

**That is true for one of the three.** The corpus re-grid renamed `programs/lon/` → `programs/lon_cherryholmes/`
(99 `.sno`). All three guards were written against the **old** name, so the rename silently changed what each one
does — and it changed them *differently*, because the three patterns differ in ways that never mattered before:

| harness | guard pattern | behaviour on `programs/lon_cherryholmes/` |
|---|---|---|
| `util_oracle_flag_sweep.sh:66` | `case "$1" in */programs/lon/*)` | ⛔ **DEAD** — no match; files now flow through |
| `test_gate_argnote_sweep.sh:21` | `find … -path '*/programs/lon' -prune -o …` | ⛔ **DEAD** — prune never fires; **99 files now swept** |
| `scorecard_snobol4.sh:66` | `case "$SUITES" in *programs/lon*)` | ✅ **STILL FIRES** — trailing `*` matches the new name |

Verified by running each pattern against the real path, e.g.
`case "$P" in */programs/lon/*) …` → no match, and
`find corpus -path '*/programs/lon' -prune -o -name '*.sno' -print | grep -c lon_cherryholmes` → **99**.

## ⛔ Why this is worse than "not done yet"

**Two boards silently WIDENED their denominators with no attributed commit and no re-pinned totals**, while a third
still refuses the same 99 files. The de-exclusion row exists precisely to make that change *deliberate* — `hq_C`'s
own framing was *"own commit, re-pinned totals, never mid-wave"* — and it was bypassed, not by anyone overriding the
discipline, but by a **rename in a different repo that nobody connected to it**.

Two consequences, and the second is the one that will bite:

1. **The fleet now disagrees with itself about `lon_cherryholmes`** depending on which harness you ask.
2. ⚠️ **Any denominator re-pinned today encodes an accident rather than a decision.** A seat comparing a board across
   the re-grid sees a moved total with no commit explaining it, and the natural reading — "someone finished the
   de-exclusion row" — is wrong.

⭐ The *direction* is not in question: Lon retracted lon's special status outright at s269 (`RULES.md:44`, *"I retract
all of it"*). Only the **manner** is defective — it happened by rename instead of by ruling.

## ⭐ The transferable lesson, and it is the same class `hq_C` found this morning

**A guard keyed on a NAME is not a guard, it is a coincidence.** It changes meaning silently the moment the name
moves, and — the expensive part — **a dead guard and an absent guard are indistinguishable in the output.**

This is the same family as `hq_C`'s digest-gate **recall miss**
(`FINDING-2026-08-26-hq_C-digest-gate-recall-miss-is-a-second-blindness-not-the-same-bug.md`), where a retired-text
grep stopped matching a paraphrase and printed `PASS(0)` — the string that also means "checked and clean". Theirs
went quiet because *prose* was paraphrased; this one went quiet because a *path* was renamed. Both are **recall**
failures, and recall failures are silent **by construction**.

⛔ **So the fix is not a better pattern.** Improving the regex (`hq_C`'s "grep the forbidden command, not the
sentence") makes the next miss less likely without making it any louder. **The property to add is a CANARY: assert
that a known-matching input is still caught, and fail when the canary goes quiet.** That converts recall from a hope
into a tested property. The design question for any filter: *what would have to change in the world for this to go
quiet, and would anything scream?* Here, nothing would have — and nothing did.

## Status — NOT cured, deliberately

⛔ I have not touched the three harnesses. It is `hq_C`'s row, and it **moves board denominators**, so it needs their
sequencing, one owned commit, and re-pinned totals — not an HQ edit landed mid-wave from the performance seat.

**Recommendation routed to `hq_C` and `ceo`:** *finish* the de-exclusion (all three guards off) rather than revert to
consistent-refuse — Lon retracted the status outright and two guards are already de facto off — with the totals
re-pinned in the same commit, and a canary added so the next rename cannot repeat this quietly.

## Also corrected in `/home/claude_P/CLAUDE.md` this session (verified here before editing)

- `src/parser/` → **`src/frontend/`** (`cf1f2961` "srcreorg move 1/3"); **`src/backends/` deleted**. Both dead names
  were live in the pipeline description — a grep pathed into either returns empty and reads as "no such code".
- **SNOBOL4-FIRST CLOSED** (Lon 2026-08-26, `RULES.md:29` § CROSS-LANGUAGE SCOPE) — DO-NOT-RUN prohibition retired,
  per-language smokes are evidence again; SHARED-NODE VERDICT SCOPE, landing-not-starting control arms, and
  rc=2-never-skip-as-success kept and made louder.
- **Corpus board timeout**: `hq_C` re-measured **28 s** against my **32 s** on the *same* tree. ⭐ The spread is the
  result: `timeout 30s` sits *inside* the run-to-run variance, so it fails **intermittently** on a green board and
  prints as a hang. A reliably-broken bound is fixed on day one; a flaky one is blamed on the box and survives for
  months. Moved to **600 s** (`hq_C`'s reasoning, better than my 300: an order of magnitude above, never beside).
  ⚠️ Censused this tree's values (`timeout 8` ×137, `30` ×72, `5` ×45, `15` ×34) but **did not measure durations** —
  which of those sit within ~2× is an **open sweep, not a finding**, and is recorded that way.
