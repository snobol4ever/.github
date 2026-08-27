# FINDING — the digest gate's second blindness: a RECALL miss, structurally distinct from the exemption miss cured two days earlier

**Seat:** hq_C · **Date:** 2026-08-26 · **Instrument:** `SCRIP/scripts/test_gate_digest_matches_rules.sh`
**Found while:** rewriting this root's own `CLAUDE.md` (a `/init` pass), not while auditing the gate.

## Claim

`test_gate_digest_matches_rules.sh` reported **GATE PASS(0) across all 38 checks** while `/home/claude_C/CLAUDE.md` carried a **live, uncorrected NO-O2-EVER violation** — one that printed the forbidden build command verbatim.

The digest's text was:

> **`-O2` is reserved for benchmark and demo runs**, passed explicitly: `RT_OPT="-O2 -g …" make`

The gate's `NO-O2-EVER` retired-text pattern was the single literal string `used ONLY for benchmark`. The violation was a **paraphrase**, so the `grep` never matched and the exemption logic was never reached.

## Why this is not the bug fixed on 2026-08-24

The 2026-08-24 correction (seat15 found, hq_C root-caused, hq_P repaired) cured an **exemption miss**: the gate *saw* a hit and wrongly excused it, because the corrective-signal check used a ±2-line window and two unanchored catch-alls (`correct(ed|ion)?` matching bare `correctness`; bare `csnobol4`).

This is the **other half**:

| | exemption miss (cured 2026-08-24) | recall miss (this finding) |
|---|---|---|
| gate saw the hit? | yes | **no** |
| failure | wrong ANSWER on a real hit | **no question asked** |
| lives in | corrective-signal regex + windowing | **retired-text regex** |
| presents to reader as | `PASS(0)` | `PASS(0)` |

⭐ **They are indistinguishable at the output and a test for one does not cover the other.** The 2026-08-24 addendum named the class exactly right — *"a gate needs a test for every way it can say NOTHING, not only for every way it can say something"* — and then fixed only the exemption path. The retired-text pattern was left as one literal string, which is the **other** way this gate can say nothing.

⛔ **The cost was real and compounding.** hq_P quoted the 38-check `PASS(0)` as evidence the fleet's digests were clean, and reasoned from it. The run was true and unearned — a second time, on the same instrument, two days apart, for a different reason.

## Root cause

A retired FACT RULE has **one** canonical retired wording in RULES.md but **N** paraphrases across 19 hand-maintained, untracked digests. Seeding the table from the canonical wording alone gives recall over exactly one of them. Nineteen seats paraphrase; the gate greps for one phrasing.

⭐ **The generalisation, and it is the reusable part:** for a gate whose input is *prose humans wrote independently*, the retired-text pattern is a **recall problem**, not an identity check — and recall is the arm that fails silently. The strongest available signal is not prose at all: it is the **forbidden command itself** (`RT_OPT=-O2`), which is invariant across every paraphrase because it is the thing a reader would actually copy and run.

## Fix (landed)

1. `retired_re` gains `reserved for benchmark`, `-O2 is (reserved|used only)`, and **`RT_OPT=.?-O2`** — the last matters most: a digest that prints the forbidden build command is instructing a violation no matter how its prose is worded.
2. Signal list gains `never (pass|build|use|quote)` and `NO .?-O2. BUILDS`, so a digest naming the command **in order to forbid it** stays correctly exempt.

**Negative-tested, five arms:** paraphrase alone → VIOLATION · paraphrase + signal same line → exempt · paraphrase + signal on a **neighbouring** line → VIOLATION (hq_P's requested assertion; the 2026-08-24 same-line anchoring preserved) · bare forbidden `RT_OPT` command → VIOLATION · this root's repaired digest → clean.

**Full 19-root run: PASS(0) before and after.** Pure recall gain — no root newly flagged, no verdict moved. The three roots carrying the *literal* retired text (claude13/14/15) were and remain legitimately exempt via same-line `superseded`.

## The other defect this pass cured, same root cause

The violation existed because **`CLAUDE.md` is an untracked plain file in a non-repo root that restates law**. This root's digest was rewritten to carry **mechanics only**, per RULES.md:170's corollary doctrine (*digests never restate law*), and every drifting count was replaced by the command that measures it. Also retracted from it in the same pass: the `corpus/programs/lon/` off-limits section (VOID since Lon's s269 retraction, `RULES.md:44`), the `make test` false-green-trap warning (cured by hq_P s268 — the target now runs the blocking set), `src/parser/` paths (renamed to `src/frontend/` at `cf1f2961`), `/home/claude/x64/bin/sbl` (gone), and a DUO-mode assertion contradicted by `/home/resources/postoffice/MODE` (FLEET-16).

⛔ **The harnesses have NOT caught up to the lon retraction** — `scorecard_snobol4.sh`, `test_gate_argnote_sweep.sh` and `util_oracle_flag_sweep.sh` still prune or refuse `*/programs/lon/*` by construction. That de-exclusion is a separate open row: inclusion moves board denominators and must land as its own attributed commit with re-pinned totals, never mid-wave.
