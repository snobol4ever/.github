# FINDING 2026-08-01 CLAUDE SN4 — ARG-NOTE RODE THE 4COL CHOKE POINT, MY OWN SWEEP MISCOUNTED 266 PHANTOM FAILS, AND `hello.sno` IS MALFORMED BY THE MANUAL'S OWN RULE

Session s23d. Directive: Lon, *"Finish annotations. Continue."* then *"All your choices. I'm with you on this."* — the OBJ-NOTE ladder, my pick of rung. Took **ON-3 continuation** (the `call rt_*` argument loads), then **ON-0** (watermark), and settled a scare I raised myself.

---

## 1. ⭐⭐⭐ THE CHOKE POINT WAS THE 4COL PASS — 189 SITES, ZERO TEMPLATE EDITS

s23c's lesson was *"`op_node_kind` at emit.cpp:861 is a CHOKE POINT — find the choke point before batching by family."* ON-3's remaining family looked like it had none.

**Why it looked impossible.** A role term for `mov rdi, [rsp+96]` requires knowing the CALLEE, and the callee is not named until the `call` several instructions later. The templates' `+` chains evaluate in **unspecified order**, so no stateful lookahead is legal — that is precisely why the s23b note mechanism travels in-band in the string rather than through a global. A per-site edit across 163 template files looked like the only route.

**The resolution.** `bb_emit_x86` hands `emit_text_n` the **whole template body in one call** (x86_asm.h:2128). So by the time `x86_4col` runs over that chunk, the argument loads and their `call` are BOTH present in one string. One backward walk (`x86_argnote`) names every one of them.

⭐ **THE GENERALIZATION:** the s23c choke point was structural (one dispatch point staging a field). This one is **temporal** — a pass that runs *later*, when information unavailable at emission time has become available. When a fact cannot be known at emit time, ask which later pass already sees it. That is a second, distinct shape of the same lesson, and it is the one to reach for whenever the blocker is "the templates evaluate in unspecified order."

Walk stops at any label, jump, other call, or non-arg-load instruction, so a role never crosses a control-flow edge. Lines already carrying `#` keep their term — idempotent under the sink's second pass, and the hand-written housekeeping vocabulary (bb_match_head's) wins over the generic role.

## 2. ⛔ PROVENANCE: 124 OF 143 TABLED, 19 REFUSED — AND TWO GENERATOR BUGS THAT WOULD HAVE LIED

`x86_arg_roles.h` is GENERATED (`scripts/gen_callee_arg_roles.py`) from the **real runtime prototypes**. No term is invented. SysV slot arithmetic: `DESCR_t` consumes **TWO** integer slots (16B, both eightbytes INTEGER — verified empirically: `a`→rdi:rsi, `b`→rdx:rcx, `c`→r8), both halves naming the ONE object; floats skip GPRs; a >16B by-value return takes slot 0 as the hidden `sret` pointer.

⛔ **THE RTX ASM PORTS ARE NOT C-ABI.** `rt_sg_scan.S` states it outright — *"LEAN CUSTOM CONVENTION — NOT the C ABI"*. A C-prototype-derived role would have been **wrong** for that whole family. Their roles come from the register contract documented in their own `.S` banner instead. **Any future tooling that maps registers to meaning must special-case the RTX ports; assuming the C ABI tree-wide is a live trap.**

**19 callees are ABSENT rather than guessed** — `rax` (an indirect `call rax`), three with CONFLICTING declarations (`rt_make_list`, `rt_proc_value`, `rt_section_var`), the rest with no reachable prototype. A wrong role term would mislead exactly the reading the annotation exists to serve.

**Two bugs in my own generator, caught before landing:**
- `return foo(a, b);` matched the declaration regex with `return` read as a return type — it would have invented role names out of **local variables at a call site**. Fixed by rejecting keyword-led heads and non-declarative parameter lists.
- Added conflict detection, which is what surfaced the three ambiguous callees. Without it the table would have silently taken whichever declaration `os.walk` happened to reach first — **order-dependent, unreproducible role names**.

## 3. ⛔⭐ MY OWN SWEEP MANUFACTURED 266 FAILURES AND I NEARLY HANDED THEM OFF AS A REGRESSION

The first ARG-NOTE gate sweep read **emit-fail=266/931**, including `hello.sno`. I flagged it rather than assume, which was right — but the number was **my instrument's defect**, not the tree's:

| cause | count | real? |
|---|---|---|
| `cannot open include '…'` | ~120 | ⛔ NO — CWD artifact; a program names its includes relative to a path my sweep did not supply |
| `unexpected char '\r'` | 67 | corpus CRLF files, pre-existing, unrelated to this rung |
| parse error | 21 | see §4 — the programs are malformed, not the parser |
| LOWER SN4-PAT subset | 6 | the known pre-existing class |

⚠ **FACT: A SWEEP OVER `find . -name '*.sno'` IS NOT A WATERMARK AND MUST NEVER BE QUOTED AS ONE.** It walks CRLF files, include fragments, and programs outside the graded set. The watermark is `xc.sh` over `corpus/crosscheck`, `.ref`-anchored, both modes. The gate script now prints `emit-decline` with that warning attached, so the number cannot be misread by the next session — the same defence as the s47 push-status rule: make the misreading structurally hard, not merely discouraged.

## 4. ⛔ `hello.sno` IS MALFORMED — AND SPITBOL SEGFAULTS ON IT

`corpus/programs/snobol4/smoke/hello.sno` is `OUTPUT = 'HELLO WORLD'` with **OUTPUT in column 1**. The SPITBOL manual is unambiguous: *"The label is optional, and is omitted by placing a blank or tab in the first character position"* (p.37) and *"Statement labels — Must begin in first character position"* (p.45). Column 1 therefore makes `OUTPUT` a **label**, leaving the body `= 'HELLO WORLD'` — an assignment with no subject.

**ORACLE-ANCHORED, both directions:**
- corpus `hello.sno` → `sbl -b` prints its banner and **SEGFAULTS**; never emits `HELLO WORLD`.
- the same program with one leading tab → `sbl -b` prints `HELLO WORLD`, rc=0.

**SCRIP's parse-error rejection is CORRECT** — arguably better than the oracle's segfault. These ~21 files are not a parser defect; they are corpus files that lost their leading whitespace. ⚠ They sit in `smoke/` with names (`hello`, `null`, `multi`, `empty_string`) that invite exactly the panic I had. **Do not "fix the parser" to accept them.** The open question for Lon is whether to repair the corpus files (add the leading blank) or mark them `.xfail`; this finding does not presume the answer.

## 5. ON-0 WATERMARK RE-PROVEN (overdue since s23b — three sessions carried)

**m3 279/27/11 · m4 266/39/10/2L**, HEAD-stamped, `xc.sh` over all 318 crosscheck programs in foreground chunks (background jobs die between tool calls, per s22z).

- **m4 is an EXACT match to the carried s23a watermark**, and the LERR set is precisely the named 2L pair (`test_string`, `1017_arg_local`).
- The single m3 delta (280/10 → 279/11) is **`213_gc_exhaustion_churn`** — the harness-only m3 flake the LAWS name *by name*. m4's TIMEOUT set is the same list minus exactly that program. Diffed **BY SET, never by count**, per LAWS.

Behaviour-neutrality of the rung itself is **MEASURED, not merely constructed**: roman.s code-identical modulo comments (3614 → 3614 lines), and the PRE-CHANGE `.s` was assembled and run to confirm identical output. M4 == M3. mode-3 is untouched by construction — `x86_4col` returns early for BINARY before `x86_argnote` runs.

## 7. ⭐⭐⭐ ON-5 LANDED SAME SESSION — AND THE CENSUS WAS WORSE THAN s23c RECORDED

With the ON-0 bracket fresh, ON-5's one-line fix landed (SCRIP `efc11e5f`): CLAIM-ZERO now spells its destination RAW via `x86_zref` (`[rsp# + N]`) so nothing re-resolves.

⚠ **RE-TAKING A CENSUS IS NOT CEREMONY.** s23c recorded ONE witness — 30 stores / 26 distinct, "4 cells never written." Re-running it across roman's twelve claim-zero runs showed the defect **scales with claim size**: **(30,26)**, **(62,40)**, **(78,56)** — 22 collapsed cells in the larger two — with **six of twelve runs collapsed**, not one. Had I trusted the recorded figure I would have under-stated the blast radius by a factor of five. This is the CENSUS SHELF LIFE law (*"re-run, never cite"*) paying for itself inside one session, on a census only one session old.

After: every run is `total == distinct` and monotone; collapsed-runs **6 → 0**.

**All four s23c gates addressed.** Watermark `m3 279/27/11 · m4 266/39/10/2L` — identical to the pre-fix baseline **and diffed BY SET across all 318 programs: zero verdicts moved in either mode.** Equal counts alone would not have shown that; the set diff is what rules out a fixed/broken swap. Witnesses 066 + 053 pass both modes; 165/183 remain m4-SEGV, consistent with s22z/s23a having already proven 165 claim-zero-**independent** by killswitch. Artifact regen ×4 done (crosscheck 482 · demo 20 · benchmark 21 · feature) with **insertions == deletions in every one** — pure in-line destination changes, zero line drift, because the store *count* was always right and only the destinations were wrong.

⚠ Unlike the ON-3 annotation this **changes emitted code in BOTH modes** — the raw spelling bypasses re-resolution for BINARY too, which is correct: both media carried the identical defect.

## 6. NEXT

1. ⭐⭐ **ON-1 operand-kind plumbing** — still blocked on the Lon `op_zkind[]` ruling for the shared params struct. Operand-a remains covered by s23c's `ZOPAN()`.
2. ⭐ **ON-3 remainder** — `[rbp+N]` statement-region slots, then the match_*/pat_*/defer housekeeping. The argument-load family is now CLOSED.
3. **ON-4 srccomment echo repair** — Lon's original readability complaint, still untouched.
4. **Lon ruling:** the ~21 column-1 corpus files (§4) — repair or `.xfail`.
