# HANDOFF 2026-06-03-b — Claude Opus 4.8 — ICON-BB: three-mode baseline, vacuous-pass discovery, coverage funnel

**Goal:** GOAL-ICON-BB.md — measurement session (Lon: "how much Icon runs today / what % of TT and IR is implemented").
**SCRIP HEAD:** `d46b943` (local == origin/main, clean — NO code commits).
**.github HEAD:** this commit.

---

## One-line summary

Built `d46b943`, ran the full three-mode ladder, and measured the TT→IR→BB coverage funnel. Found and
documented a **vacuous-pass hole** in `test_icon_rung_suite.sh` (stdout-only compare, exit-code blind:
`rung36_jcon_proto` aborts rc=134 yet counts PASS in all three modes against its empty `.expected`).
Fix queued as the **SUITE-HONESTY** step now at the top of the ICN-SCAN ladder.

## Fresh baseline (at `d46b943`)

- Smoke: m2 **12/12 HARD** · m3 5/12 · m4 5/12
- Corpus: m2 **130**/117F/36X · m3 **14**/81F/**152 EXCISED** · m4 **21**/135F/91 EXCISED
- m4 > m3 by exactly the global/proc cluster (known m3 pool-blob user-proc segv → declines)
- All columns include ≥1 phantom (the vacuous pass below)

## ⚠ Vacuous-pass hole (the actionable finding)

`run_corpus` (test_icon_rung_suite.sh:106–142) compares `$got` stdout to `.expected` and never reads the
exit code. `rung36_jcon_proto.icn` — the 158-line V9 syntax sampler, the "most complicated program" by
every ranking, with an EMPTY `.expected` — parse-errors at line 18 (`();` → "expected expression"),
aborts rc=134, emits nothing, and is counted **PASS in m2, m3, AND m4**. Crash-with-no-output is
indistinguishable from ran-and-printed-nothing. **FIX (one line):** capture `run_prog` rc; `rc≠0`
without `[SMX]` ⇒ FAIL (m2 included). Then re-baseline and record honest columns. Gate: proto flips
PASS→FAIL ×3; no genuine passer regresses.

## Genuine champions (run live, byte-verified this session)

- **m2:** `rung37_file_io` (32 lines) — `&output` as FH, `write/writes(fh,…)`, open→write→close→open→read
  round-trip via /tmp, `write(fh,42)` int-vs-slot. Output matches expected exactly.
- **m3:** single-construct 4–6-liners only — `every write("a"|"b"|"c")` (bb_alt+every),
  `("foo"||"bar") ? write(&subject)` (bb_gen_scan+bb_keyword+concat), `every write(1 to 5)` (bb_to),
  multi-write. Nothing compound passes m3.
- **m4:** `rung25_global_global_three_procs` (15 lines) — reset/bump×5/write over an NV global → `5`,
  compiled standalone, linked, correct.

## Coverage funnel (measured: greps + full-corpus --dump-bb, not recall)

- **TT:** shared enum 156 kinds; Icon parser emits **79**; lower.c case exists for **76/79 = 96%**.
  Gaps: `TT_BANG_BINARY`, `TT_PROC_DECL`, `TT_STMT` (latter two likely consumed pre-switch; `x!y` apply
  looks genuinely unhandled). Caveat: case label ≠ Icon arm built (lower_unhandled routing possible).
- **IR (Icon vocabulary):** 283-program dump union = **26 kinds**. Frequency top: CALL 1858, SUCCEED 450,
  FAIL 375, VAR 291, LIT_I 261, LIT_S 243, ASSIGN 224, BINOP 202, EVERY 121, IF 84, RETURN 70, ALT 43,
  LIT_F 40, GEN_SCAN 40, TO 38, UNOP 35, CONJ 25, WHILE 16, TO_BY 8, SUSPEND 7, LIST_BANG 7, LIT_NUL 6,
  UNTIL 5, NOT 5, REPEAT 1, NEXT 1.
- **m2 arms: 26/26 = 100%** (why m2 reaches 46% of whole programs — misses are semantic depth, not
  missing opcodes). Native dispatch case exists 26/26, but **≥1 working native shape ≈ 18/26 (69%)**;
  **ZERO native shape (8): IF, CONJ, WHILE, UNTIL, REPEAT, NEXT, SUSPEND, LIST_BANG** — the control
  cluster, the largest dead native block (same bb_var-slot + relop tier already named). Most of the 18
  are shape-partial (BINOP: no relops; ASSIGN: no locals; CALL: no builtins; ALT: ≤5 lit arms;
  GEN_SCAN: safe shapes) — per-node shape coverage multiplies, collapsing 69%/kind to 5–7%/program.

## NEXT

1. **SUITE-HONESTY** (top of ICN-SCAN ladder) — the one-line rc fix + re-baseline.
2. **ICN-SCAN-0** — registerize the `?` env (fscan.r + bb_gen_scan.cpp + gen_runtime.c:59–89 first).

## Session setup for next session

```bash
git clone https://TOKEN@github.com/snobol4ever/.github.git /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/SCRIP.git   /home/claude/SCRIP
git clone https://TOKEN@github.com/snobol4ever/corpus.git  /home/claude/corpus
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh && bash scripts/build_scrip.sh && make libscrip_rt
bash scripts/test_smoke_icon.sh          # m2 12/12 HARD; m3/m4 5/12
bash scripts/test_icon_rung_suite.sh     # m2 130 / m3 14+152E / m4 21+91E (pre-SUITE-HONESTY numbers)
# canonical sources: unzip uploaded icon-master.zip / jcon-master.zip into refs/
# then: GOAL-ICON-BB.md → ICN-SCAN LADDER → SUITE-HONESTY, then ICN-SCAN-0
```
