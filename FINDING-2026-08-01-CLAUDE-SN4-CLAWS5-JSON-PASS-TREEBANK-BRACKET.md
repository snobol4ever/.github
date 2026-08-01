# FINDING-2026-08-01-CLAUDE-SN4-CLAWS5-JSON-PASS-TREEBANK-BRACKET.md
# Session s22m · 2026-08-01 · Claude Sonnet

## Result
CLAWS5 ✅ oracle-match (95/95 lines). JSON ✅ oracle-match (10/10 lines, timer stripped).
Treebank segfault root cause bracketed to the 11th `rt_goto_transfer` call — RSP imbalance
first appears after `Push_item` returns, +104 bytes (non-multiple of 16) → SIGSEGV in
glibc `movaps`. Zero SCRIP commits (concurrent session active in same tree). Three artifact
regens run. `json.input` + `json.ref` committed to corpus.

---

## §1  Setup anomalies

**Detached-build poisoned-tree.** First clone of SCRIP backgrounded without `setsid`; killed
process left `out/rt_pic/bb_match_rtab.o` at 0 bytes. Link failed. Fix: `find out -name "*.o"
-size 0 -delete && make -j4 scrip`.  Per the O2-DIRECTED-ONLY FACT RULE, all builds at `-O0`.

**Concurrent session.** Working-tree HEAD moved from `2e637798` to `db670758` (CAP-SYM) while
this session ran. Unstaged `lower_snobol4.c` CAP-DEFER-FENCE WIP was stashed/popped without
modification. All three regens billed to CAP-SYM (the codegen commit in the tree per the
RULES.md "any codegen commit in the session tree owes the regens" law).

**gdb now available.** `apt-get update && apt-get install -y gdb` rc=0. The s22l NEXT item 2
warning ("gdb IS NOT INSTALLED IN THIS CONTAINER") is stale. RULES.md bracket step 2 is
re-enabled.

---

## §2  Baseline (setarch -R, ASLR off, SCRIP bc3372ca)

| demo | m3 rc | lines | ref | status |
|---|---|---|---|---|
| claws5 | 0 | 95 | 95 | MATCH ✅ |
| treebank-list | 139 | 0 | 24 | segfault |
| treebank-array | 139 | 0 | 24 | segfault |
| json | 0 | 10 | 10 | MATCH ✅ |

The GOAL-SNOBOL4-BB.md note "assembler-rejected codegen" for claws5/json is **stale** — all
four demos compile and assemble cleanly at HEAD. The failures are runtime-only.

---

## §3  Claws5 — CAP-SYM was the fix (verified by independent bisect)

Claws5 failed at the previous HEAD (`2e637798`) with 1691 lines vs 95 expected.
Bisect of the 151-line demo identified the defect independently:

```
w = LEN(2)
'abcd' 'a' (w . tag)   →  SCRIP bc3372ca: tag=[bc] ✅ (was tag=[abc] ✗)
```

Capturing a **variable-held pattern** (`w . tag`) used the overall match start rather than
the cursor where the sub-pattern actually began. Inline groups `((LEN(2)) . tag)` were
correct; only the pattern-variable path was broken.

The concurrent session's CAP-SYM commit (`bc3372ca`, `bb_match_capture.cpp` line 29)
cites the same reproducer and fixes the same defect. My bisect converged identically and
independently confirmed the fix is correct.

Per CAP-SYM's own comment (bb_match_capture.cpp:29): a ZD-spine-armed SAVE node wrote its
delta into the zeta cell while COND read the software array — two different grant paths.
`op_fc_base >= 0` (already the established discriminator at x86_asm.h:282) now gates both
ends to the same path.

---

## §4  JSON — oracle-validated fixture added

`json.sno` had no `.ref` and no stable input fixture. Actions:

1. Created `corpus/programs/snobol4/demo/json.input` — 86-byte RFC-8259 object exercising
   all value types (object, array, string, integer, boolean, null).
2. Generated `corpus/programs/snobol4/demo/json.ref` from `sbl -b json.sno < json.input`
   with the `match_ms=…` timer line stripped (timing is non-reproducible).
3. Verified scrip output (timer-stripped) matches the ref: MATCH ✅.

Committed to corpus as `934cd7b4`. Demo is now gateable.

---

## §5  Treebank — root cause bracketed

Both treebank programs segfault identically in all regimes (default, NOFC, NOFC_CARVE).

### 5a  Fragment-γ NULL jump (min reproducer, MY INSTANCE — killed by NOFC)

Constructed minimal 11-line reproducer:
```
'ab' 'a' Push("'Z'")    ; Push = EVAL("epsilon . *push(" vs ")")
```

gdb: fault at `0x7ffff1c062e6: jmp *%rax` with `rax=NULL` inside EVAL-compiled fragment
`EXPR$0F1`. Fragment entry:
```
sub  $0x80,%rsp
mov  %rcx,0x68(%rsp)   ; save γ landing
mov  %rdx,0x70(%rsp)   ; save ω landing
...
sub  $0x10,%rsp         ; ζ claim NOT released
...
mov  0x68(%rsp),%rax    ; reads [saved_rsp-0x10+0x68] = NULL  ← wrong slot
jmp  *%rax              ; → SIGSEGV
```

The mid-body `sub $0x10` ζ claim (Gen-1 FC grant on a value spine node) is never released,
so the fixed-offset γ epilogue reads 16 bytes past its saved landing. **SCRIP_NOFC=1
fixes this** (non-popping spine, no claim outstanding) and is confirmed in the minimal
reproducer (rc=0, `end n=1` matches oracle). But NOFC does not fix the real treebank
programs — they exercise a different arm of the same class.

### 5b  RSP-misalign arm (treebank's real crash)

gdb scan at `runtime_eval.c:291` across 200 `rt_goto_transfer` calls:

```
H0  Init_list   mod16=0  rsp=0x...7f40
H1  Push_list   mod16=0
H2  Pop_final   mod16=0
H3  Push_list   mod16=0
...
H10 Push_item   mod16=0  rsp=0x...6920
H11 Pop_list    mod16=8  rsp=0x...6988  ← +104 bytes, SIGSEGV in glibc movaps
```

rsp descends monotonically across H0–H10 (ζ claims never fully released). At H11 it
**rises 104 bytes** — a non-multiple-of-16 delta — breaking x86-64 ABI alignment, which
causes the `movaps` in glibc's `__vsnprintf_internal` to fault.

Blob map: the faulting `rt_goto_transfer` call sits inside `IR_GOTO_DEFERRED` (n3),
immediately after `IR_SAVE_RESTORE` (n2), in `proc_flat_α_body`.

**The discriminator is H10 `Push_item`.** Its body is `head(stk) = list(v, head(stk))`
— DATA field-function used as assignment target. The RSP imbalance first appears on
return from that call.

### 5c  Root cause class

Both §5a and §5b are the **SUSPENDED-CELL law (s21x-l) firing on the flat_jmp_entry path**.
A ζ claim made at α is still outstanding when the proc executes `rt_goto_transfer` (a
runtime label jump that bypasses the γ/ω release). The DEFINE-protocol path (`IR_SAVE_RESTORE`
+ `IR_GOTO_DEFERRED`) was admitted to the ζ spine (ZD-SR + ZD-8) but the claim/release
pairing is not net-zero on the `goto_transfer` arm.

**Neither NOFC nor NOFC_CARVE fixes treebank** — confirming this is NOT the carve-bisect
question but the proc-call/goto protocol.

---

## §6  1:1-correspondence break (min reproducer)

The minimal reproducer (`'ab' 'a' Push("'Z'")`) exhibits:

| mode | result |
|---|---|
| m3 `--run` | SIGSEGV |
| m4 `--compile` → link → run | `end n=1` — correct |

m4 escapes because the lookup in `rt_proc_open_fn` happens to succeed (fn pointer valid).
m3 crashes because the ζ claim left outstanding by the FC grant shifts the γ epilogue read
by 16 bytes, landing on a NULL cell.

---

## §7  Artifact regens (all three, per RULES.md step 4)

Run at SCRIP `bc3372ca` (current HEAD, CAP-SYM):
- `util_regen_benchmark_s_artifacts.sh s22m-CAP-SYM` — 21 benchmarks, changes committed to corpus
- `util_regen_feature_s_artifacts.sh s22m-CAP-SYM` — feature tests, changes committed to SCRIP
- `util_regen_demo_s_artifacts.sh s22m-CAP-SYM` — demo programs, changes committed to corpus

---

## §8  Next session entry points

1. **Treebank hunt** — gdb now available. `break runtime_eval.c:291`, `ignore <bpnum> 10`
   (spin past H0–H9), step into the H11 `Pop_list` caller to find which emitted instruction
   leaves the ζ claim outstanding.  The 2-way monitor can bracket further.

2. **FAMILY A** (`bb_call_proc_staged` ZD arm) — five-arm conversion, sized at 590 lines.
   See s22l NEXT item 1.

3. **`151_pat_arbno_inline_fence_backtrack`** — m3 SIGSEGV deterministic with ASLR off;
   gdb was the stated blocker and is now available.

4. **NOFC per-kind carve bisect** — `SCRIP_NOFC_CARVE=1` + `SCRIP_BB_ONLY`/`SCRIP_BB_SKIP`
   to find which match-family node kinds' carve helps vs hurts.
