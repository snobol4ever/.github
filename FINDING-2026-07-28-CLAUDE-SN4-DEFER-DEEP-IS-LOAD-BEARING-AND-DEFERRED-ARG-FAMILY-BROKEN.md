# FINDING 2026-07-28 — SN4: DEFER's deep-arrival classification is LOAD-BEARING (a seductive false green), and the DEFERRED-ARGUMENT family is broken in BOTH modes

**Session:** s197 (Claude). **Tree:** SCRIP `a0e83fe2` (s196 SCANBASE). **Nothing landed — the one change tried was REVERTED on manual evidence.**

---

## 1. THE FALSE GREEN — do not re-run this experiment and believe it

**The experiment:** remove `case IR_MATCH_DEFER:` from `emit_graph_has_deep_arrival()` (emit.cpp), the FLATDISP-6 narrowing shape.

**The measurement, HEAD-stamped both sides:**

| | census NET | m3 | m4 | DIVERGE |
|---|---|---|---|---|
| `a0e83fe2` baseline | 113 | 221/94 | 219/94 | 1 (W06_tab) |
| + DEFER removed | **48** (−57.5%) | 221/94 | 219/94 | 1 (W06_tab) |

Watermark held EXACTLY. Census dropped 65. Three PASSING programs (`111_pat_fence_via_var_falls_to_outer`, `123_pat_regex_alt_class`, `125_pat_json_literal`) carry `match_defer` with NO other deep kind, so their classification genuinely flipped deep→depth-static and they still passed both modes. **It looks landable. IT IS NOT.**

**WHY IT IS WRONG (SPITBOL manual v3.7, "Recursive Patterns", p.122-123):** pattern recursion exists ONLY through the unevaluated-expression operator — *"The unevaluated expression operator makes the definition possible."* Its depth is genuinely unbounded: *"SPITBOL saves information on a stack during the pattern match process. Heavily recursive patterns and long subject strings can sometimes result in stack overflow"* (tunable with `-s`). `EXPRESSION = *EXPRESSION | "(" TERM ")"` produces *"a recursive plunge and stack overflow immediately."* So a DEFER transfer CAN arrive below the activation base. The classifier's conservatism is exactly right.

**WHY THE TRIPWIRE WAS BLIND — the important part.** The three passing witnesses are all **bounded** transfers (one level into a PAT$ blob, returns to base). Every program that exercises RECURSIVE re-entry is already in the pre-existing 94-FAIL set — and they are the manual's own examples verbatim:
- `179_pat_arbno_defer_recursive_list` = `ITEM = SPAN('0123456789') | *LIST` (manual p.122)
- `183_pat_arbno_defer_recursive_carry` = `G = "<" SPAN("ab") ARBNO(*G) ">"`

**The trap:** the change measures perfectly clean TODAY *because the only witnesses are already broken*. Land it and it becomes a live bug the instant the ARBNO/recursive-defer dig succeeds — and it will present as an ARBNO regression, not a classifier regression, because the instrument that should have caught it was dark. **A green watermark over a 94-FAIL baseline is not evidence for a change whose witnesses are inside those 94.**

## 2. NO Use-A NARROWING EXISTS (proposed, then falsified in-session)

The manual splits `*` into two uses: **A** = deferred scalar argument (`LEN(*N)`, `TAB(*I)`) to one of ANY/BREAK/BREAKX/LEN/NOTANY/POS/RPOS/RTAB/SPAN/TAB — a load, no re-entry; **B** = deferred pattern reference (`*LIST`, or a bare pattern-valued variable) — the recursive plunge. Splitting the classifier on that line looked like the sound rung.

**It is not available.** Measured: inline `LEN(*N)` (no pattern variable) emits NO `match_defer` at all — kinds are `match_len_`/`match_head_`/`match_assign_*`. Use A is handled INSIDE the box and never becomes `IR_MATCH_DEFER`. Both emission sites in `sno_pat_node` are pattern-ELEMENT position (`case TT_DEFER` and `case TT_VAR`, lower_snobol4.c ~1210-1218), i.e. 100% Use B. **The entire IR_MATCH_DEFER population is pattern transfer. There is no scalar subset to peel off.**

⚠ A first probe used `S ? PAT` with `PAT = LEN(*N) . ITEM` and DID show `match_defer` — that came from the bare pattern-variable `PAT` (Use B), not from `LEN(*N)`. Contaminated probe; the clean inline test is the one to trust.

## 3. NEW BUG FAMILY — DEFERRED ARGUMENTS ARE BROKEN IN BOTH MODES

Found while probing §2. Literal control passes; every deferred form fails, three DIFFERENT ways, m3 and m4 identically:

| program | SPITBOL oracle | SCRIP m3 | SCRIP m4 |
|---|---|---|---|
| `LEN(3) . X` (control) | `X=abc` | `X=abc` ✅ | — |
| `LEN(*N) . X`, N=3 | `X=abc` | `X=` (empty capture) | `X=` |
| `TAB(*I) . X`, I=4 | `X=123A` | **SIGSEGV** | **SIGSEGV** |
| `SPAN(*C) . X`, C='AB' | `X=ABBA` | `fail` | `fail` |

**LOCALIZATION** (lower_snobol4.c, TT_ANY/TT_NOTANY ~1163, TT_SPAN ~1176, and the TT_LEN/TAB/RTAB/POS/RPOS arm ~260):
```c
const char * cs = sno_cset_fold(t->c[0]);
if (cs) IR_LIT(nd).sval = (char *) cs;   /* static cset — baked, WORKS */
else    sno_pre_req(cx, t, nd);          /* runtime/deferred arg — THE BROKEN ARM */
```
`sno_pat_invariant()` (~line 915) correctly returns 0 for a deferred arg (`t->c[0]->t == TT_ILIT` fails; `sno_cset_fold` returns NULL), so the fork is taken correctly — the fault is in `sno_pre_req`'s handling, or in the box's consumption of its result. **Start the monitor there** (RULES.md MONITOR-FIRST; `LEN(*N)` is the cheapest reproducer — deterministic wrong VALUE rather than a crash).

**⛔ METHODOLOGICAL: the DIVERGE metric is STRUCTURALLY BLIND to this class.** Both modes are wrong IDENTICALLY, so mode-3/mode-4 parity stays perfect and DIVERGE stays 1. Only the SPITBOL oracle catches it. **A clean DIVERGE is not evidence of correctness for any shared-lowering bug.**

## 4. TRIAGE NOTE FOR THE NEXT DIG

s195 directs the next dig at ARBNO. Several names in the 94 are `*`-bearing (`056_pat_star_deref`, `070_pat_arbno_star_var_digits`, `071_pat_star_var_concat`, `072_pat_star_var_alt_backtrack`, `073/074/075_pat_star_*`). **Some fraction of the "ARBNO" FAIL population may be this deferred-argument root cause, not ARBNO.** Check the deferred-arg family FIRST — it is cheaper (a wrong scalar, not a depth-protocol bug) and may retire tests currently charged to ARBNO.

## 5. CEILING — "finish RSP/RBP" does not reach zero

Of the 113: **~65 is DEFER conservatism** (correctly held; static detection of pattern recursion is undecidable here — `*LIST` resolves to a runtime variable value, which is precisely WHY SPITBOL just uses a stack and lets it overflow); **~22 is `flat_gen`** (the suspend-record protocol reads a pinned rbp by design — `emit_jmp_pin_rbp`'s comment predicts only that `flat_pat` fires less after 5a, never that `flat_gen` retires); **~6 is marshal** `mov rcx,rbp` (a register read, not a frame ref — can never reach zero). Honest floor ≈ 90 of 113 unless the suspend protocol itself is redesigned.

⚠ Also: the census sweeps `--compile` output, so it counts programs that SEGV at runtime. All four census-heavy benchmarks (pattern_bt, string_pattern, mixed_workload, roman) SEGV identically before AND after any change measured this session. **The ratchet has been ratcheting on programs that do not run.**

## 6. ⚠ CONCURRENT WRITER IN THE CONTAINER — UNEXPLAINED, AFFECTS MEASUREMENT INTEGRITY

Mid-session HEAD moved `62aaf9ff` → `a0e83fe2` with NO action by this session. Reflog says **`commit:`**, not `pull`/`merge`/`fetch` — authored as LCherryholmes inside this container at 00:16:41, touching `scripts/test_gate_rbp_census_ratchet.sh` (baseline 119→113) and `src/emitter/emit.cpp`. No script this session ran contains a git write (`install_system_packages.sh`, `test_crosscheck_snobol4.sh`, `test_gate_rbp_census_ratchet.sh` are all clean of `git commit`).

**It silently invalidated the first measurement of the session** (the reported "119→48" conflated s196's SCANBASE rebase with the DEFER experiment; true attribution is 113→48). Every measurement after that point is HEAD-stamped before and after. **If parallel sessions share this volume, HEAD-STAMP EVERY MEASUREMENT** — and note that a session which does not stamp will silently publish a conflated number, exactly as this one nearly did.
