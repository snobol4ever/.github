# HANDOFF — 2026-06-07 — BB-FIXUP 18th attended run (Opus 4.8)

**Goal:** GOAL-BB-FIXUP.md · **Lap:** 2 · **Lon attending** ("your choice, continue" ×2, context checks at ~33% and ~55%, handoff word ~63%).
**Repos at close:** SCRIP @ `5ea8581` (verified local==origin) · .github this commit.
**All stops fully closed. No LADDER rungs closed (FIX-1 standing; nothing deleted per handoff rule 1).**

---

## 1. SESSION-OPEN FINDING — TRACKER CLOBBER, REPAIRED (`9b1e7d1`)

**What:** PIVOT `da96b66` (Lon's bb_pat_*→bb_match_* rename, landed after the 17th run's three fixup commits) was prepared from a STALE tracker base. Its tracker sweep silently reverted the entire 17th-run state:
- `- [x] bb_subject.cpp` (full ✅ v2 annotation) → bare unticked
- `- [x] bb_succeed.cpp` (object-byte-identity proof annotation) → bare unticked
- `bb_succ_plus.cpp` RB CONVERSION clause (rb 25→0, 45→20) → reverted to the stale pre-conversion `[S] rb=25 owner GOAL-PROLOG-BB` text
- `# CURSOR: bb_term_inspect.cpp` → reverted to `bb_subject.cpp`

**Evidence chain (run before any repair):**
1. `git show --stat` on `9c14a1d` / `c9e018e` / `4bfe09b`: each carried a 4-line `BB-REVAMP-TRACKER.md` change — the 17th run DID commit its tracker cargo per law 3.
2. `git show da96b66 -- BB-REVAMP-TRACKER.md`: the diff's `-` side IS the 17th-run text verbatim; the `+` side IS the pre-17th text. Direct proof of the revert.
3. Full-diff audit `git diff 4bfe09b da96b66 -- BB-REVAMP-TRACKER.md` filtered of rename + the 4 known hunks: EMPTY — nothing else lost.

**Repair:** the 4 hunks restored VERBATIM from `4bfe09b:BB-REVAMP-TRACKER.md` (python exact-match replace, assert count==1 each); a `# RESTORE` header note added documenting cause + audit; the bb_match_* rename entries untouched. Committed `9b1e7d1`, pushed, before entering THE LOOP.

**⛔ LESSON FOR THE RING (recorded in tracker + goal watermark):** pivot/rename/bulk-sweep commits MUST `git pull --rebase` onto the live head before sweeping the tracker. Cursor + ticks travel per-commit (law 3); a stale-base sweep undoes them silently and every gate stays green — same family as the attended-run rationale: gates verify behavior, not state truth.

**Arithmetic note:** post-restore tick count = 73 (71 + subject + succeed), vs the 17th-run watermark's "74 clean". The delta is the PIVOT's own legitimate entry reshuffle (bb_match retire/birth consolidation, 106→103 tracker entries) — folded into the standing RECONCILE verdict, not chased (law 5).

---

## 2. STOP `bb_term_inspect.cpp` (`5ea8581`) — rb 50→6, TOTAL 84→40

**The recipe's FIFTH application** (after aggregate_nb / atom_string / findall / succ_plus). Arrival counts matched the 17th-run note exactly: eb=12 nw=22 rb=50, ef/pe/lv already 0 from the 5th-run TIER H. HOT check: COLD (no non-fixup commits in 6h window touching it; the IRD-3-CHAIN-2 window on bb_call/bb_call_write_slot to ~02:50 UTC 06-08 doesn't touch this file).

### The conversion
ALL FIVE bin helpers — `bti_bin_functor` / `bti_bin_arg` / `bti_bin_univ_tt` / `bti_bin_univ_t1` / `bti_bin_univ_1t` — converted `bytes()`→`x86()` under the corrected rule. Whole-blob `x86_lit_bytes(...)` wraps DROPPED at the 3 `_str` call sites (helpers self-Lrec; 1-Lrec→N-Lrec framing payload-identical per bb_findall precedent). Casts copied verbatim from bb_succ_plus's landed forms.

**ZERO NEW ENCODERS NEEDED** — the run-7/8/17 set covers the whole shape. Every form re-byte-verified at source THIS HEAD:

| x86() form | BINARY bytes | matches original |
|---|---|---|
| `x86("sub","rsp",16L/8L)` | `48 83 EC 10/08` | ✓ |
| `x86("add","rsp",16L/8L)` | `48 83 C4 10/08` | ✓ |
| `x86("mov","rdi/rcx/rsi","rax")` | `48 89 C7/C1/C6` | ✓ |
| `x86("mov32","esi/edi",imm)` | `BE/BF imm32` | ✓ |
| `x86("mov32","r8d",imm)` | `41 B8 imm32` (REX.B via rnum) | ✓ |
| `x86("movabs","rdx/rcx/rsi/rax",u64)` | `48 BA/B9/BE/B8 imm64` | ✓ |
| `x86("movabs","r9",u64)` | `49 B9 imm64` (REX.B) | ✓ |
| `x86("xor","ecx/edx/eax",same)` | `31 C9/D2/C0` (no REX, e-regs) | ✓ |
| `x86("mov",RSP(0),"rax")` | `48 89 04 24` (off=0 no-disp branch) | ✓ |
| `x86("mov","rdi",RSP(0))` | `48 8B 3C 24` — **FIRST LANDED USE of the rsp-load dispatch arm** | ✓ |
| `x86("call",sym,u64)` → x86_call_ro | `48 B8 imm64 FF D0` | ✓ |
| `x86("test","eax","eax")` | `85 C0` | ✓ |

Parse path verified: `RSP(0)` → `"qword ptr [rsp + 0]"` → parser line 466 `atoi(s+17)` = 0 → XK_RSP64 off=0.

**Residual rb=6** = `x86_lit_bytes(` bridges around `[S] emit_term_from_node_bin` (lines 17/35/51/53/64/77) — audit substring artifact, honest markers, removable only with LOWER term plumbing (the pinned dedicated-session item shared with bb_resolve). **[S] eb=12 nw=22 STAND** (functor/arg/=.. shape admission + operand fusion → LOWER `_.op_*`/ζ-slot plumbing, design not pinned).

### Proof set
**(a) Standalone A/B harness — ALL 13 BRANCH SHAPES BYTE-IDENTICAL, FIRST PASS.**
- Shapes: functor ×4 (s1×s2 present/NULL), arg ×4 (s0×s2), univ_tt ×1, univ_t1 ×2 (s1), univ_1t ×2 (s0).
- Pattern (17th-run transplant): harness TU `#include "x86_asm.h"` (the REAL one); OLD side = pre-edit byte chains transcribed verbatim, operands parameterized (t/ival/sval/fn as plain args through the SAME cast chains); NEW side = post-edit x86() chains transcribed verbatim, same parameterization. `emit_term_from_node_bin` stubbed as `TERM()` = fixed 5-byte marker, IDENTICAL both sides (new side wraps it in x86_lit_bytes whose framing the comparator strips, so the bridge contributes equal payload). Fixed fake pointers/fn addrs (>4GB values exercised). Comparator `stripL()` walks the NEW side's `'L'+len+payload` records; OLD side is already raw.
- Link line: `g++ -O0 -std=c++17 -I src/emitter/BB_templates -I src/emitter -I src/contracts -I src/machine -I src/include -I src/interp -I src/lower -I src/runtime{,/rt,/core,/builtins} -I src/driver -I src harness.cpp stubs.cpp src/emitter/emit_str.cpp`. Stubs: `bb_medium_t g_medium = BB_MEDIUM_BINARY; sm_emit_t g_emit; extern "C" void rt_bomb(const char*){__builtin_trap();}` — exactly the 17th-run stub set; `src/include` is the non-obvious -I (XA.h lives there).
- No framing artifacts this run (the 17th run's first-pass artifact came from an unframed OLD side; parameterizing both sides identically avoided the rerun).

**(b) asm-diff EMPTY ×3** — stash A (da96b66+restore) vs B, three-pattern normalizer (`bb[0-9]+`→bbN, `RESOLVE(name/<int>)`→N, `.Lcall<int>`→.LcallN). TEXT arms untouched by the edit → expected and confirmed EMPTY.

**(c) LIVE probes** — 3 distinct TEXT arms fire (`rt_functor_term` / `rt_arg_term` / `rt_univ_term` @PLT, one per .s). Probe texts (the accepted `initialization` shape — bare `:- Goal.` rejected by the m3/m4 drivers):
```
p1: :- initialization(main, main).  main :- functor(foo(a,b), N, A), write(N), write(A), nl.   → foo2
p2: :- initialization(main, main).  main :- arg(2, foo(a,b,c), X), write(X), nl.               → b
p3: :- initialization(main, main).  main :- foo(a,b) =.. L, write(L), nl.                      → [foo,a,b]
```
m4 pipeline = the smoke recipe: `scrip --compile --target=x86 → as → gcc -no-pie -L out -lscrip_rt -Wl,-rpath,out -Wl,--allow-shlib-undefined -lm`.

**(d) behavior A/B identical ×9** (3 probes × m2/m3/m4). m2/m4 print the expected outputs; m3 = PL-GZ-1b LOUD interp-fallback (`[PBB] FATAL: --run: program not admitted by pl_gz_admit...`) IDENTICAL both sides — these builtins are m3-silent, the harness byte-map is the binary-arm proof per the XK_SYM honesty standard. The remaining 5 TEXT arms (functor_s/arg_s/univ_tt/univ_t1's lea-arm variants/univ_ss) and the bin arms are corpus-silent on this probe set; the 5th-run TIER H pass previously fired all 8 TEXT arms LIVE and this edit did not touch TEXT — asm-diff EMPTY is their proof.

**(e) medium-invisible DELISTED**: bb_term_inspect 47→0.

### Practice note
Mid-stop tooling erratum, self-caught: a `git pull --rebase` placed BEFORE the tracker edit failed on the dirty template (unstaged) and the `&&` chain silently skipped the edit — the POST-EDIT CURSOR VERIFY (15th-run erratum lesson) caught it; correct order is edit → commit → rebase → push. Also: the runner is `sh` not `bash` — process substitution needs an explicit `bash` script file.

---

## 3. GATES (at floors, every commit)

smoke m4 7/7 HARD · pat M4=18 FAIL=0 (053 pre-existing SKIP) · icon m2 12/12 HARD, m3=m4 10/12 (proc_zeroarg + proc_recursion pre-existing) · purity 2-floor (bb_call_write_slot + bb_every) · bin_t 0 · vstack 3 · sno_pat_reg TIER1+TIER2 HARD · handencoded 0 · prove_lower 68 PASS + 3 inherited FAIL (law-5 trio: PL-GZ-7 ITE pair + PL-GZ-8 arith-is) · emit-blind steady 235.

**Close rank 841→797** (open at restore-corrected baseline 106 files / 32 dirty / 74 clean → close 32/74; fixup −44 in one stop). Tracker line-count (30 dirty / 73 clean) differs from the rank scan by the untracked-files gap — folded into RECONCILE (now **110 dir vs 103 tracker entries vs 106 rank-scanned**).

---

## 4. CURSOR + NEXT SESSION

`# CURSOR: bb_term_io.cpp` — **the BIG one**: TOTAL=115 = ef=23 pe=3 lv=26 TIER H **plus** rb=43 conversion. History: the 6th run's stop-19 built it once (115→67, asm-diff EMPTY, 5 TEXT arms LIVE) but it was **RESET TO A uncommitted on Lon's word** for the corrected rule — REDO WHOLE under corrected rule. bb_term_inspect is its near-twin (same generator heritage, same rt_* marshal shapes); the conversion recipe is now FIVE-times proven and this run's harness transplants directly (swap the rt_* names + shapes). **Plan it as the next run's FIRST SUBSTANTIAL stop with full headroom** — this run declined to start it at ~58% precisely because law 7 commits the session to finishing any file it opens.

Behind it: bb_to (9) / bb_type_test (40, rb=15 — recipe applies) / bb_unify (8) / bb_unop (25) / bb_var* family close the lap. Then per the standing priority queue: FIX-4 (gvar 3c capture) → FIX-3 family (bb_return op_sa-relocation is the landed model, per-member design calls stated in-run) → bb_resolve + emit_term_from_node_bin LOWER term plumbing as a dedicated TIER S session (also retires this stop's rb=6 bridges and atom_string's rb=4).

---

## 5. OUTSTANDING LON VERDICTS (6, unchanged)

1. x86_movimm uint32-truncation (bb_call_fn BINARY arm, >4GB fn pointers)
2. RING/DIRECTORY RECONCILE — 110 dir vs 103 tracker vs 106 rank-scanned
3. prove_lower rc=0-on-FAIL hardening
4. PL-GZ-8 arith-is 2-vs-5 node count (owner PL-GZ)
5. m2 disj-backtrack silent-empty (owner PROLOG-BB)
6. IRD-2b IR_t.own backpointer DEVIATION ratification
