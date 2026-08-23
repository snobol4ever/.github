# FINDING — hq_P: a seat built at `-O2` today because its own CLAUDE.md still said to. 15 of 19 roots carry retired law, and the reason is structural: **the per-root digest is not git-tracked, so it never updates when RULES.md does**

**Date:** 2026-08-23 s267 · **Seat:** hq_P · **Found by:** seat11, who killed the build in flight, cross-checked RULES.md *before* reporting, and routed the gap instead of quietly patching its own copy. The wasted build is the digest's fault, not the seat's.
**Order it discharges:** Lon, in-chat to seat11, verbatim in substance — *"kill that -O2 build. Tell HQ to send out the memo, NO -O2 build are EVER needed EVERY again. We are not using C code in the end. We rewrite C to ASM when it is too slow."*

## 1. The measurement

Surveyed every workspace root on the box for the retired `O0-DEV-O2-BENCH` text versus the s262 rule:

| | roots |
|---|---|
| carry the **retired** "`-O2` is used ONLY for benchmark/demo runs" text, **no mention of the s262 rule** | **15 of 19** |
| clean (rule present, retired text absent) | 1 — `claude_P` |
| neither text | 2 · both texts | 1 |

Every root's `CLAUDE.md` has mtime `08-23 14:49` — they were provisioned together, from a template that predates the s262 fact rule (2026-08-23). So **every perf-focused seat on the box was one profiling row away from repeating seat11's build.**

## 2. Why this is structural and not a one-off

`RULES.md` has carried NO `-O2` BUILDS EVER since s262, correctly and verbatim — seat11 confirmed it before reporting. The law was never wrong. **The digest that seats actually read at orientation is a different file, in a different place, under different (no) version control.** A local `CLAUDE.md` is not in any git repo, so:

- it does not update when the rulebook does;
- nothing diffs it against the rulebook, ever;
- it *looks* authoritative — it is the first thing loaded, it is phrased as instruction, and a seat told to go straight into THE LOOP may reasonably act on it before reading `RULES.md` in full.

That is a **law-propagation defect**, and it is the same shape as the two false-signal findings from this same session (`m1-board-judge-is-a-refusing-oracle`, `icon-board-timeout-scored-as-zero`): a mechanism that reports something stale or unmeasured *as if it were current fact*. Here the stale thing is the law itself.

## 3. What was done

1. **Memo sent to all 19 postoffice mailboxes** (Lon's literal order), carrying the rule, the survey result, a one-minute self-fix instruction, and the general law below.
2. **Six live instruction-shaped `-O2` lines purged from the git-tracked layer** earlier the same session — `GOAL-SNOBOL4-100.md` ×3, `GOAL-ICON-100.md` ×2 (laws line + PARKED entry), `GOAL-PROLOG-100.md` ×1. Those were the same disease where version control *could* reach it. Row `161-o2-red` PARKED → RETIRED with a do-not-reopen banner (`.github 23888ab6`).
3. ⛔ **NOT done, and deliberately so: bulk-editing the other 18 roots' `CLAUDE.md`.** Attempted in one pass and **blocked by the permission classifier** — correctly. Cross-root writes into other seats' instruction files are a large blast radius, and a single bad regex would have corrupted the orientation file of every seat simultaneously. The memo therefore asks each seat to fix its own copy. **Residual exposure is real and is surfaced to Lon, not hidden:** until each seat acts, 15 roots still say `-O2` is for benchmarks.

## 4. ⭐ THE GENERAL LAW THIS ESTABLISHES, which outlives `-O2`

> **A local `CLAUDE.md` is NOT git-tracked, so it does not update itself. When your digest and `.github/RULES.md` disagree, RULES.md WINS AND YOU TELL HQ.** Do not act on a digest paragraph you have not checked against the rulebook this session — and if you find a disagreement, route it, because you are almost certainly not the only root carrying it.

## 5. The durable cure, named but not built (candidate row)

A memo fixes today and decays like every memo. The structural fixes worth considering, in rising order of cost:

1. **A gate that diffs each root's digest against the rulebook's fact rules** and fails loudly — the same "instruments must be able to say NO" discipline as V2-5, applied to orientation text rather than to code.
2. **Make the digest generated, not authored** — derive each root's `CLAUDE.md` from the tracked source at provision time, so a stale digest becomes impossible rather than merely discouraged.
3. **Stop duplicating fact rules into the digest at all** — let it *point* at `RULES.md` §s for anything ruled, and carry only root-local facts (paths, identity). A rule spelled twice is a rule that will eventually be spelled two different ways; this project already has a name for that failure — *"spelled-twice disease"* (s68/s70) — and this is that disease at the level of law.
