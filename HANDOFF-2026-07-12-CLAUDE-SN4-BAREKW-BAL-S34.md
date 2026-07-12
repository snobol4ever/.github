# HANDOFF — 2026-07-12 — Claude Sonnet 4.6 — s34: SN4-BAREKW + SN4-BAL

**AUTHORS:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6
**OPENED:** 2026-07-12
**REPOS at close:** SCRIP `3c30b073` · corpus `f1e13ceb` · .github `81771ec0`
**GATE:** crosscheck m3 302/4, m4 301/3/2, DIVERGE=1(1017); sno 7/7×2, icon 12/12×2, prolog 5/5×2.

---

## What this session did

Lon's directive: "Make complete the entire IR_MATCH_* set of IR opcodes."

The rung resolved into a **parser finding**: the set was never incomplete — it was **unreachable**.

### Root cause (SN4-BAREKW, SCRIP `73b6b154`)

`pat_prim_kind()` (snobol4.y:37) is consulted at **exactly ONE grammar site — snobol4.y:195, `T_FUNCTION T_LPAREN`** — so it only fires when a name is followed by a paren. The seven argument-less keywords `ABORT ARB BAL FAIL FENCE REM SUCCEED` take no arguments, so they never reached it; they fell to snobol4.y:196 (`T_IDENT → TT_VAR`) and arrived at the lowerer as **plain variables**.

Three had been bandaged by `strcmp` inside `sno_pat_node`'s `TT_VAR` arm (ARB/REM/FENCE). The other four were never bandaged and lowered to **`IR_MATCH_DEFER(<name>)` = a deferred read of an unset variable**. Oracle-measured consequences:

| Keyword | Oracle said | SCRIP gave | Mechanism |
|---------|-------------|------------|-----------|
| ABORT   | Failure     | **MATCHED** | DEFER(unset) happened to succeed |
| SUCCEED | null match → succeeded | **failed** | DEFER(unset) failed |
| FAIL    | failed | failed (correct) | DEFER(unset) happened to fail |
| BAL     | `(14-2)` | **FATAL refuse** | at least honest |

`case TT_ABORT:` / `TT_BAL:` / `TT_SUCCEED:` / `TT_FAIL:` in `sno_pat_node` **HAVE NEVER ONCE EXECUTED.** `IR_MATCH_BAL/FENCE/ABORT` and `bb_match_abort`/`bb_match_fence` had rotted for exactly that reason.

**Fix:** ONE normalizer `sno_pat_eff_kind()` (lower_snobol4.c, just above `sno_is_fence`). `sno_pat_node` / `sno_pat_supported` / `sno_is_pattern_rhs` / `sno_is_fence` all switch on it. The three strcmp bandages **deleted**. Grammar NOT touched (REPO-SCRIP.md prohibition on running bison). The promotion is safe: manual Ch.18 p.203 — these are protected built-ins, they cannot shadow a user variable.

### Design split (the s31 rule applied)

A construct earns an IR node iff it owns runtime state. The seven keywords split cleanly:

- **ABORT / FAIL / FENCE** own **no state → EDGES (wiring).** Landed as such. ABORT's existing `GOTO pat_seal` was **already correct**: `pat_seal` bypasses `IR_MATCH_HEAD` while ordinary element-fail routes *through* it, and HEAD is the anchor-advance loop. That one edge distinction **is** the manual's ABORT/FAIL split (p.125: "ABORT stops all pattern matching, while FAIL tells the system to back up and try other alternatives or other subject starting positions").

- **BAL owns EXTENT → it earns a node** (SN4-BAL, SCRIP `b7317175`). It is a generator: manual p.124/p.203 says "matches the shortest string possible" and extends on retry.

### BAL design (bb_match_bal.cpp, `b7317175`)

Structurally ARB + a paren-depth counter, two manual-forced differences:
1. **Non-null:** scan consumes a char BEFORE it may yield — extent 0 is never a result (ARB does yield 0).
2. **Exhausts when depth goes negative:** a `)` that closes nothing can never be rebalanced to its right — `)A+B` is not a non-match *at this extent*, it is the **END of the generator**.

ζ 16B **SPAN shape** (+0 n / +4 entry-δ / +8 depth / +12 pad) — a pure in-frame generator, no ζ push, **no ZLS2 grant** (unlike ARB). α initialises and falls through into the scan; **β re-enters the same scan with n/depth intact** — "resume and extend to the next balanced extent" *is* the loop. One loop serves both ports. **Zero new encoders needed.**

Wiring: `sno_pat_node` TT_BAL arm + admission, `zeta_storage.c` 16B grant + shifted-locals, `emit.cpp` slot-size + drive cases, `ir_is_generator_kind`, `bb_templates.h`, Makefile.

### Gate defect (the s25/F6 shape, third occurrence)

The crosscheck sat green at 294 **while ABORT was a silent wrong answer**, because the corpus had **zero tests** for ABORT / FAIL / keyword FENCE / BAL. Added tests 170–177 (corpus `f1e13ceb`), all refs oracle-generated, all pinning manual examples — including **171**, which pins that ABORT suppresses the *anchor-advance*, not merely the alternatives (the subtle half, and the one that proves the `pat_seal`-bypass is correct).

### .s artifacts

`util_regen_feature_s_artifacts.sh` ran. **One file changed: `057_pat_fail_builtin.s`, shrank 136→19 lines.** That's the fix visible in the artifact: FAIL used to compile to a whole deferred-variable-read machine; it's now a bare edge. Benchmarks/demos byte-unchanged.

---

## Commit trail

| Repo | Hash | Summary |
|------|------|---------|
| SCRIP | `73b6b154` | SN4-BAREKW: 7 argument-less pattern keywords were unreachable from the parser |
| SCRIP | `b7317175` | SN4-BAL: IR_MATCH_BAL LANDED |
| SCRIP | `3c30b073` | feature x86 .s artifacts: regen |
| corpus | `f1e13ceb` | SN4-BAREKW + SN4-BAL crosscheck tests 170-177 |
| .github | `81771ec0` | GOAL-SNOBOL4-BB s34 landing block |

---

## Residue — the OPEN items for the next session

Both constructs below are now **refused loudly** (honest FATAL) rather than silently mis-lowered.

### SUCCEED — needs a β→γ (Lon ruling wanted)

Manual p.126: "if the scanner is backtracking when it encounters SUCCEED, it reverses and starts forward again." It owns **no stored state** (s31 rule says edge) but a bare `IR_GOTO` has **no resume surface**.

This is **SU-E in miniature**: JCON needed explicit gotos because it had no IR graph; SCRIP has a real graph with γ/ω edges. The question Lon has not yet ruled on: does a stateless-but-resumable construct get a **node (zero ζ, live β)**, or does the **edge vocabulary grow a β surface**?

**Manual-forced sequencing:** SUCCEED must land AFTER ABORT. Coppen's rule 2 (p.127): "SUCCEED without an ABORT or FENCE … will either never terminate or it is superfluous." The canonical `SUCCEED … FAIL` oscillator only halts via ABORT. ABORT is now landed, so SUCCEED is unblocked.

**Forward-direction SUCCEED already measures oracle-green** (it's a zero-width match that succeeds unconditionally left-to-right). Only the β is missing.

### FENCE(P) function ≠ keyword FENCE — oracle-measured silent divergence

The manual is explicit (p.222 / p.125):
- **Keyword `FENCE`:** backup **fails the match** entirely.
- **`FENCE(P)` function:** backup **passes through** and does NOT abort — only alternatives *inside* P are hidden.

`sno_is_fence()` treated both identically and sealed both. **The manual's own example diverges:**

```
P = FENCE(BREAK(',') | REM) $ STR *DIFFER(STR)
'abc' ? P   →   oracle: STR=abc   SCRIP: failed
```

The seal must become **direction-sensitive**. `FENCE(P)` stays an edge, just a *different* edge: backup travels through it (cursor is not restored, seal is not hit) but alternatives inside `P` are blocked.

Re-probe at session start:
```
scrip --run /tmp/probe/m_fencefn2.sno   # should match STR=abc; SCRIP currently fails
```

### Orphan opcodes (Lon's call: wire or delete)

| Opcode | Status |
|--------|--------|
| `IR_MATCH_RETRY` | Has template (`bb_match_retry.cpp`). No lowering. References `kw_anchor`; HEAD uses `g_anchor`. Almost certainly a fossil. |
| `IR_MATCH_ADVANCE` | Has template (`bb_match_advance.cpp`). No lowering. Same `kw_anchor` tell. |
| `IR_MATCH_SPAN_VAR` | Has template (`bb_match_span_var.cpp`). No lowering. |
| `IR_MATCH_CALLOUT` | Opcode only. No template, no lowering. |

### TT_SUCCEED / TT_FAIL cross-frontend overload

The **Pascal** parser mints `TT_SUCCEED` as its empty-statement/sequence-terminator node (pascal.y:605, 636, 698). Same kind, two unrelated meanings. Harmless today because the trees never cross frontends, but worth knowing before anyone touches either.

---

## Session setup for next session

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
git clone https://github.com/snobol4ever/x64 /home/claude/x64
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/SCRIP/scripts/test_smoke_snobol4.sh           # PASS=7
bash /home/claude/SCRIP/scripts/test_crosscheck_snobol4.sh      # m3 302/4, m4 301/3/2, DIVERGE=1
```

