# HANDOFF 2026-06-03 (Opus 4.8) — SNOBOL4-BB: define-body `:(RETURN)`/`:(FRETURN)` final-statement DOUBLE-EXECUTION fixed (m3+m4); recursion + all 3 RETURN-goto flavors proven; GT/LE predicate gap found

## Summary

A DEFINE'd function body's FINAL statement — the one carrying `:(RETURN)` or `:(FRETURN)` — executed **TWICE** in
mode-3 AND mode-4. The define smoke (`DOUBLE = X + X`) is idempotent, so m3/m4 6/6 never caught it; an
OUTPUT-in-body probe shows `a b c c done`. Fixed with **one dval-scoped line** in `gvar_chain_arity` (SCRIP
**`591ed37`**, pushed, rebased onto upstream `5091102` ICN-SCAN-2). Stash-proven +1 on broad interp, zero
regressions, all HARD gates hold. Follow-up probes then proved all three RETURN-goto flavors AND recursive DEFINE
green in m3, and surfaced one new LOUD m3 gap (GT/LE predicate builtins).

## Root cause (diff = `src/emitter/emit_bb.c`, +1 line)

`lower_program.c:465/466` creates the SNOBOL goto-RETURN IR nodes with **`α = NULL` by design** (`RET dval=1.0`,
`FRET dval=2.0`) — SNOBOL `:(RETURN)` carries NO expression; the function value lives in the NV store under the
function name. But `gvar_chain_arity` fell through to the shared `descr_chain_arity`, whose `IR_RETURN → 1` is the
**Icon/Pascal `return expr` convention** (dval=0.0). The RPN operand-promotion pass `gvar_stmt_operand_refs` then
did `n->α = stk[sp-1]` — **clobbering RET->α with the body's final statement node** — and `flat_drive_return`,
seeing a non-NULL α, walked it as a "return expression" via `walk_bb_flat`, emitting + executing the final
statement a second time (asm signature: the assign block appears at both `snoch0_n5` and inside `xreturn4_expr`).

FIX in `gvar_chain_arity`:
```c
if (n && n->t == IR_RETURN && (n->dval == 1.0 || n->dval == 2.0)) return 0;
```
Keyed on the SNOBOL goto-RETURN dval markers. Grep-proven the ONLY dval-1.0/2.0 IR_RETURN creators are
`lower_program.c:465/466`; Icon (`lower.c:872`) and Pascal (`lower_program.c:228`) create dval=0.0 and keep
arity 1 — **byte-identical for both** by construction.

## Verification (all == SPITBOL oracle `/home/claude/x64/bin/sbl -b`)

| probe | shape | m2 | m3 | m4 |
|---|---|---|---|---|
| 3-stmt OUTPUT body | `a/b/c` + `:(RETURN)` | ✅ | ✅ (was `a b c c`) | ✅ (was `a b c c`) |
| `N = N + 1` discriminator | one invocation vs doubled stmt | ✅ | ✅ `1/done` | — |
| FRETURN twin | `:(FRETURN)` → `:S/F` goto | ✅ | ✅ `body/no` | ✅ |
| string arg | `G('AB')` → `got:AB` | ✅ | ✅ | LOUD bomb (concat-VAR, expected) |
| mid-body `:S(RETURN)` + `:F(RETURN)` | label-registry path to RET | ✅ | ✅ | — |
| **recursive** `R(S)` 4 deep | pattern-conditioned recursion | ✅ | ✅ `xxx/xx/x//done` | — |

The recursion probe is the **SR-2 prerequisite data point**: the `rt_name_save_push`/`rt_name_restore` LIFO is
recursion-proven across nested activations; VAR-arg recursive call shape is supported; pattern-replace on a PARAM
works in m3; the null-string OUTPUT line matches the oracle exactly.

## Gate state (rebased tree `591ed37`, rebuilt + re-gated)

SNOBOL4 m2 **7/7 HARD** · m3 **6/6** · m4 **6/6** · Icon m2 **12/12 HARD** (m3/m4 5/12 unchanged) ·
prove_lower2 **67** · no_bb_bin_t 0 · concurrency OK · REG-FENCE TIER1=0 (TIER2 r10 info unchanged) · broker 32 ·
Prolog smoke m2 5/5 / m3 4/5 / m4 5/5 unchanged · broad interp **112 → 113 (+1, stash-proven vs clean `40ec5bc`;
the goal's old 105 watermark was STALE — intervening lanes moved it)**. ENV: `apt-get install -y libgc-dev`.

## Items RETIRED this session (goal file updated)

1. **slen string-arg** (SR-1a handoff open item): the `G('AB')` → empty symptom does NOT reproduce at tip — string
   args arrive correctly via the staged path. Retired pending a counter-case.
2. **Compound SUBJECT/REPLACEMENT silent-wrong** (scan-guard handoff item 2): already landed as `f406239`
   (whole-graph `scan_val_is_single_lit` + TEXT-arm bombs); verified behaviorally (m4 bombs LOUD on `'got:' X`).

## Still open (next session)

1. **NEW m3 GAP (LOUD, correct failure mode): GT/LE predicate builtins have no `bb_call` arm** —
   `[IBB] FATAL bb_call: unsupported call shape fn='GT' narg=2 a0=-1`. Blocks any predicate-conditioned define
   body in m3 (`FACT(5)` untestable until it lands). Manual ch.4: the numeric conditionals succeed/fail returning
   the null string. Good small next rung.
2. **PB-RB-4** — m4 ALT + variable/captured CAT native byrd-box graph (`STITCH_ALT`/`STITCH_SEQ`); the bomb names
   it. The frontier's genuine big rock; needs a fresh budget.
3. **Pascal m3 nested-fn segv** — PRE-EXISTING (clean-tree baseline rc=139 identical, stash-proven). Belongs to
   GOAL-PASCAL-BB; flagged, not touched.
4. REG-RO + REG-FENCE TIER2 — still deferred behind PB-RB-CONV per the reconciliation note.

## Build / verify recipe

```bash
cd /home/claude/SCRIP
bash scripts/build_scrip.sh && make libscrip_rt          # emit path lives in BOTH
bash scripts/test_smoke_snobol4.sh                        # m2 7/7 HARD; m3 6/6; m4 6/6
bash scripts/test_smoke_icon.sh                           # m2 12/12 HARD
bash scripts/prove_lower2.sh ; bash scripts/test_gate_sno_pat_reg.sh
cat > /tmp/t.sno <<'EOF'
        DEFINE('G(X)')          :(G_END)
G       OUTPUT = 'a'
        OUTPUT = 'b'
        OUTPUT = 'c'            :(RETURN)
G_END
        G('AB')
        OUTPUT = 'done'
EOF
echo END >> /tmp/t.sno   # m2/m3/m4 must print a b c done (NOT a b c c done)
```

## Watermark

SCRIP tip = **`591ed37`** (pushed; rebased onto `5091102` ICN-SCAN-2, rebuilt + re-gated green). `.github` tip =
this commit. Goal single-source-of-truth updated in `GOAL-SNOBOL4-BB.md` (frontier re-pointed to PB-RB-4 + GT/LE;
watermark + follow-up-probe addendum + two retirements). Detail: this file.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
