# GOAL-SN4-JVM-EMIT.md — SNOBOL4 → JVM (IR_t-based, beauty self-host)

⛔ **No AST walking in modes 2/3/4** — see RULES.md.
⛔ **Zero C Byrd boxes** — see RULES.md. BBs are emitted, not C functions.
⛔ **Read before any source file:** ARCH-IR.md, ARCH-JVM.md, ARCH-EMITTER.md.

**Repo:** one4all + .github
**Goal:** `scrip --sm-emit --target=jvm file.sno` emits Jasmin; assembled + run by java produces correct output.
**Done when:** beauty.sno byte-identical to SPITBOL oracle (md5 `abfd19a7a834484a96e824851caee159`, 646 lines).

---

## Pipeline

```
tree_t → lower → IR_t → emit_jvm → Jasmin .j → jasmin.jar → .class → java
```

Reads IR_t (generator nodes) and SM_Program (scalar walk). Two outputs:
- BB Jasmin classes for IR_PAT_* (alpha/beta methods).
- Per-method Jasmin for scalar SM opcodes (one method per DEFINE'd function + sno_body for top-level).

---

## BB reference (19 kinds, all pre-implemented in Jasmin)

| IR_t node | Reference class | git single-file |
|---|---|---|
| IR_PAT_LIT | bb/bb_lit | `git show 660339cd:src/runtime/boxes/lit/bb_lit.j` |
| IR_PAT_SPAN | bb/bb_span | `…/boxes/span/bb_span.j` |
| IR_PAT_BREAK | bb/bb_brk | `…/boxes/brk/bb_brk.j` |
| IR_PAT_ANY | bb/bb_any | `…/boxes/any/bb_any.j` |
| IR_PAT_NOTANY | bb/bb_notany | `…/boxes/notany/bb_notany.j` |
| IR_PAT_LEN | bb/bb_len | `…/boxes/len/bb_len.j` |
| IR_PAT_POS / rpos | bb/bb_pos, bb/bb_rpos | `…/boxes/pos/bb_pos.j`, `…/boxes/rpos/bb_rpos.j` |
| IR_PAT_TAB / rtab | bb/bb_tab, bb/bb_rtab | `…/boxes/tab/bb_tab.j`, `…/boxes/rtab/bb_rtab.j` |
| IR_PAT_REM | bb/bb_rem | `…/boxes/rem/bb_rem.j` |
| IR_PAT_ARB | bb/bb_arb | `…/boxes/arb/bb_arb.j` |
| IR_PAT_ARBNO | bb/bb_arbno | `…/boxes/arbno/bb_arbno.j` |
| IR_PAT_CAT | bb/bb_seq | `…/boxes/seq/bb_seq.j` |
| IR_PAT_ALT | bb/bb_alt | `…/boxes/alt/bb_alt.j` |
| IR_PAT_ASSIGN_IMM/COND | bb/bb_capture | `…/boxes/capture/bb_capture.j` |
| IR_PAT_FENCE | bb/bb_fence | `…/boxes/fence/bb_fence.j` |
| IR_PAT_ABORT | bb/bb_abort | `…/boxes/abort/bb_abort.j` |

Also read `src/lower/ir_exec.c` `IR_exec_node()` — authoritative semantics per kind.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
apt-get install -y default-jdk   # provides javac (NOT in install_system_packages.sh)
bash /home/claude/one4all/scripts/build_scrip.sh
java -jar /home/claude/one4all/src/backend/jasmin.jar 2>&1 | head -1
```

---

## Steps

### SJ4-JVM-1..3.5 ✅ — BB emitters, SnoRt runtime, smoke 7/7, scalar SM walker
All closed in prior sessions. See "Closed rungs trail" below.

### SJ4-JVM-4 — Beauty self-host 🔄

**Status:** Method-split landed; beauty assembles and starts executing on JVM. Hits a runtime "Parse Error" partway through (semantic, not structural).

- [x] **SM_PAT_* + SM_EXEC_STMT emission** (sess 2026-05-15h, Opus 4.7) — 20 opcode handlers; new `SnoPat.java` (~340 lines, recursive backtracking matcher); JVM smoke 7→13. Cross-runtime pattern parity hand-validated vs C interp.
- [x] **User function dispatch** (sess 2026-05-15, Sonnet 4.6) — SM_LABEL define_entry pre-scan; SM_CALL_FN/SUSPEND_VALUE → fn dispatch; SM_RETURN/FRETURN/NRETURN + _S/_F variants.
- [x] **Method-split refactor** (sess 2026-05-16, Opus 4.7) — `main()` was 112,465 bytes > JVM 65535. Split into `sno_body()` + one `sno_fn_NAME()` per DEFINE (78 fns in beauty). `SM_CALL_FN` user-fn → `invokestatic Prog/sno_fn_NAME()V`. `SM_RETURN/*` → JVM `return`. Function ranges via preceding SM_JUMP-over target + group inheritance for adjacent DEFINEs sharing an end label (counter family). Cross-method SM_JUMP/JUMP_S/JUMP_F → `halt_tos(); System.exit(0)`. **JVM smoke 13/13 retained.** beauty.sno: emits 38,310 lines / 80 methods, assembles cleanly, runs and produces output until hitting "Parse Error".

- [ ] **Diagnose beauty's "Parse Error"** — runs to a print of "Parse Error" then halts. Likely an unhandled SM opcode (check stderr for [NO-AST] stubs), runtime semantic gap (`call_external` / `call_returning` are still stubs — see invariants), or `&ANCHOR` / pattern-callback gap. Bisect by capturing C interp output for the same input and diffing where they diverge.
- [ ] **Complete beauty self-host** — output byte-identical to oracle (md5 `abfd19a7a834484a96e824851caee159`).

**Gate:** Smoke 13/13 PASS; beauty.sno output byte-identical to oracle.

---

## Demo JVM Artifacts (`corpus/programs/snobol4/demo/`)

`hello.j`, `counter.j`, `pattern_test.j`, `arithmetic.j`, `beauty.j`.

Regenerate: `for prog in hello counter pattern_test arithmetic beauty; do scrip --sm-emit --target=jvm $prog.sno > $prog.j; done`
Verify: `jasmin.jar *.j` produces .class without errors; `md5sum *.j` and update checksums.

**Current checksums** (will change after sess 2026-05-16 method-split; not yet regenerated):
```
hello.j:        1e25de83489d43eda42675de8a063394
counter.j:      ed263fcc8075520b8f42b06928d7720c
pattern_test.j: 8a95286a856ce38b8e28609772f9729b
arithmetic.j:   849210cc9fdf374b757c87bf9d82224c
beauty.j:       (stale — 23618 lines pre-split; new is ~38310 lines / 80 methods post-split)
```

---

## State

```
watermark: SJ4-JVM-4 IN PROGRESS — method-split landed sess 2026-05-16 (Opus 4.7);
           beauty.sno emits + assembles + runs; halts at runtime "Parse Error".

Sess 2026-05-16 (Opus 4.7) changes (uncommitted):
  - emit_jvm.c refactored: emit_jvm_one_instr() + emit_jvm_sm_range() helpers;
    new emit_jvm_from_sm() splits SM_Program into sno_body + sno_fn_<NAME>.
  - Function end via preceding SM_JUMP-over with group_end inheritance.
  - Cross-method jumps → halt_tos + System.exit(0).
  - JDK install required: apt-get install -y default-jdk (added to session setup).

Test suite this session:
  ✅ C smoke:       7/7 PASS
  ✅ JVM smoke:    13/13 PASS (no regressions from method-split)
  🟡 Beauty.sno:   emits 38310 lines / 80 methods; assembles ✅; runs ✅;
                   halts mid-execution at printed "Parse Error".

Remaining for SJ4-JVM-4:
  1. Diagnose "Parse Error" — likely [NO-AST] stub for some SM opcode in beauty,
     or pattern-userfn callback (call_external/call_returning still stubs).
  2. Verify byte-identical to SPITBOL oracle.
  3. SM_BB_* generator opcodes (PUMP, EVAL, ONCE) — not exercised by smoke;
     check if beauty needs them once Parse Error is resolved.
  4. Regenerate demo .j artifacts; update checksums above.

head: c2a2f498 (one4all, pre-session — sess 2026-05-16 changes uncommitted);
      4aaf4c5 (corpus); 94e86ca (.github, pre-session)
```

---

## Key invariants

- **IR_t only** for generator nodes; SM_Program for scalar walk.
- **19 BB kinds, all pre-implemented in Jasmin.** Read `bb_boxes.j` first.
- **Jasmin labels: no leading dot.** Use `L0`, `Lalpha`, `Lbeta`.
- **`.limit stack` and `.limit locals` required** in every method (16/4 for sno_body/sno_fn_*).
- **Flag:** `--sm-emit --target=jvm`.
- **JVM 65535-byte method limit** is the reason for method-split — every emitted method must stay under it.
- **`call_external` / `call_returning` are stubs** in SnoRt for `. *fn()` and bare `*fn()` in pattern position. Real DEFINE'd user-fn dispatch through pattern callbacks not yet wired.

---

## Closed rungs trail

- **SJ4-JVM-1** — All 19 BB template emitters for JVM (in emit_jvm.c).
- **SJ4-JVM-2** — SnoRt.j runtime class complete (push_*, store_var, concat, arith, MatchState, INPUT/OUTPUT trap).
- **SJ4-JVM-3** — `scripts/test_smoke_snobol4_jvm.sh` smoke gate.
- **SJ4-JVM-3.5** — `emit_jvm_from_sm()` SM_Program walker + `emit_jvm_program()` entry; scalar SM → Jasmin invokestatic.
