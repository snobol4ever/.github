# FINDING 2026-08-01 (s165) — THE PROLOG CARVE IS **NOT** DEAD CODE. THE s164 INSTRUMENT COUNTED THE WRONG REGISTER, AND `CARVE-KILL` BROKE PROLOG 22/22.

**SCRIP HEAD at measurement:** `dda156eb` · tracked-modified **0** at every measurement point · all `-O0`, `grep -cE '\-O[12]'` on the build log = **0**.
**Baseline compared against:** `548c5637` (s164) via the **committed** `corpus/benchmarks/prolog/bench/nrev.s`, which s164 itself regenerated as honest HEAD output.

---

## 0. HEADLINE

s164's headline — *"⭐⭐ THE PROLOG CARVE IS DEAD CODE … `[rsp+..]` ref count IDENTICAL (685) both regimes, **proving no instruction ever addressed the carved cells**"* — is **FALSE, and falsified by direct measurement.**

The carve is addressed **through RBP, not RSP**. s164's instrument counted `[rsp+..]` references only, so it was structurally blind to the addressing mode that actually consumes the carved storage. Acting on that conclusion, `ef9a7d2c CARVE-KILL` + `1ba33ea6` deleted the flat prologue **and** epilogue emitters outright — which removed the carve, the RBP establishment, and the argument-binding call together. **Prolog is now 22/22 broken at HEAD.**

---

## 1. MEASURED: PROLOG IS RED AT HEAD

`scripts/test_bench_prolog_modes.sh` → `green(m3&m4)=0 frontier=0 **broken=22** total=22`. Direct repro, `nrev`, mode 3: **SIGSEGV, rc=139, zero bytes of stdout** (verified with `stdbuf -o0`, so this is not lost buffering). Mode 4 fails identically — the compiled binary is a separate process, so this is **not** the in-process RX slab.

⛔ **NOT the NOFC regime.** `SCRIP_NOFC=0` (the new inverted killswitch, restoring the popping regime) segfaults **identically**, rc=139 on all four probed benchmarks. The non-popping default is exonerated.

⚠ **A uniform 22/22 failure is normally a HARNESS TELL** (s152's own rule), so it was checked before being believed: `hello.pl` **prints `hello` correctly and then segfaults at exit**, while `nrev` dies before emitting anything. Two distinct signatures ⇒ a real defect, not a runner artifact.

---

## 2. ⭐⭐ THE CRUX — THE INSTRUMENT COUNTED THE WRONG REGISTER

Measured on the **committed s164 artifact** (`nrev.s`, the regime that was green):

| quantity | value |
|---|---|
| `[rbp + N]` references | **1,414** |
| range of those offsets | **min 0 … max 1,296** |
| emitted carve sizes (`sub rsp, K`) | 512, 1200, 1216, 1232, **1296**, 16 |
| `[rbp+N]` landing **inside** a 512-byte carve | **748** |
| `[rbp+N]` landing beyond 512 (inside the larger carves) | 666 |

**The maximum `[rbp+N]` offset (1,296) is exactly the maximum carve size (1,296).** Every one of the 1,414 references addresses carved storage. The prologue seeds that storage through RSP *before* the base flip — `mov [rsp+488], rcx` · `mov [rsp+496], rdx` · `mov [rsp+504], rbp` — and then executes `mov rbp, rsp`, after which the entire body speaks `[rbp+off]`.

So s164's observation was true but non-probative: holding `[rsp+..]` at 685 across the NOFC toggle proves the toggle didn't disturb *rsp*-based addressing. It says **nothing** about the 1,414 *rbp*-based references, which are the carve's real consumers.

⭐ **AND IT INVERTS s164's OWN SAFETY ARGUMENT.** s164 item (4) reasoned: under NOFC `rbp==rsp` invariantly, therefore every `[rbp+off]` *is* `[rsp+off]`, therefore "the C-style frame is 100% VESTIGIAL." That equality is **manufactured by the very instruction CARVE-KILL deleted** (`mov rbp,rsp`). RBP was redundant *because the establishment kept it equal to RSP* — remove the establishment and the redundancy becomes a live dependency on a register the caller owns. **A proof of redundancy is not a licence to delete the thing that creates the redundancy.**

---

## 3. WHAT THE DELETION ACTUALLY REMOVED (HEAD vs s164 artifact, `nrev.s`)

| | HEAD `dda156eb` | s164 (green) |
|---|---|---|
| `call rt_jmp_frame_lexprep2` | **0** | 7 |
| `sub rsp, …` | 4 | 103 |
| `mov rbp, rsp` | **1** | 8 |
| `[rbp + …]` references | **1,372** | 1,414 |
| `proc_*_α:` entry labels | 17 | 17 |

Three load-bearing things went out with one emitter, not one:
1. the frame **carve**,
2. the **RBP establishment**,
3. the **argument-binding call** `rt_jmp_frame_lexprep2` (7 → 0).

**THE FAULT, EXACTLY:** at HEAD the first two instructions of `proc_reverse$2F2_α` are `lea rax,[rip+n11_suspend_β]` / `mov qword ptr [rbp + 416], rax`. **The first `[rbp+]` consumer is at line 8; the only surviving `mov rbp,rsp` is at line 9,972.** 1,372 references depend on a base established — at best — 9,964 lines later. Every predicate entry stores through the caller's RBP. That is the segfault.

`hello` survives long enough to print because `main`'s graph is the one carrying the single surviving establishment; every *predicate* graph is orphaned.

---

## 4. ⭐⭐ THE DETERMINISTIC INSTRUMENT EXISTS — s164's NEXT (a) IS CLOSED

s164 disqualified wall time and made the whole ladder wait on a deterministic instrument. Two exist in this container; neither needs `perf`, `valgrind`, or `gdb` (all three still **ABSENT**):

- ⭐ **Exact retired-instruction count via `ptrace(PTRACE_SINGLESTEP)`** — `/home/claude/work/stepcount.c`. `/bin/true` = **136,618 instructions, bit-identical across runs.** Throughput **~30.8k insn/s** ⇒ ~5M instructions per tool call. Full benchmarks (billions) are out of reach, but a *structural* codegen A/B does not need them: both regimes run the same program deterministically, so the ratio is structural and a small input suffices.
- **Kernel-emulated software perf events** — `PERF_COUNT_SW_PAGE_FAULTS` / `_MIN` / `CONTEXT_SWITCHES` / `TASK_CLOCK` all **AVAILABLE** at `perf_event_paranoid=2`. Page faults are the right axis for s164 item (6), the per-activation memory complaint.

⛔ **HARDWARE counters are NOT available:** `perf_event_open(PERF_COUNT_HW_INSTRUCTIONS)` fails **ENOENT** — the PMU is not virtualized in this container. Do not plan a rung around hardware counters.

---

## 5. WHAT THIS DOES **NOT** CLAIM

- It does **not** claim NOFC-DEFAULT-ON is wrong. NOFC was exonerated in §1 (both arms fail identically), and s164's NOFC arm was itself gated green at 185/185. The unsafe step was the *later, larger* one: deleting the emitter, not declining to pop.
- It does **not** claim the SNOBOL4 landings are wrong **for SNOBOL4** — SN4 has its own replacement spine and its own gates. This is the fourth independent instance of the standing rule that **the SN4 ladder does not transfer to Prolog**.
- No perf claim of any kind is made. Nothing was measured on wall time.

---

## 6. NEXT — ⛔ LON RULING WANTED, THIS IS CROSS-GOAL

Prolog is red at HEAD because of a landing owned by `GOAL-SNOBOL4-BB.md`. The repair touches `src/emitter/emit.cpp`, which that ladder is actively working, so it is **not** this session's to take unilaterally.

Two candidate repairs, both consistent with the standing directive (*non-popping RSP ζ stack, C-style RBP only when absolutely necessary*):

- **(A) Restore the establishment + arg-binding for the affected graph class.** Cheapest and immediately green. ⚠ Must be expressed as a **kind/shape** predicate, never a language token — NO-LANGUAGE-SENTINEL forbids `is_prolog` past LOWER.
- **(B) ⭐ Respell the consumers, which is the directive's actual end state.** Re-point the 1,372 `[rbp+off]` references at `[rsp+off]` through the single authority `x86_fb()` (`x86_asm.h:374`, per s164 item (5) — the frontier is ONE predicate, not 45,741 sites). ⛔ **This requires the carve to STAY**: the offsets run to 1,296 and are only valid relative to a carved frame. Respelling without carving addresses the caller's frame. Cost is known and must be paid explicitly: `[rsp+disp]` needs a SIB byte ⇒ **+1 byte per reference**, and it is now measurable deterministically per §4.

⛔ **Whichever is chosen, `CARVE-KILL` must not be repeated on the argument that the carve is unaddressed. §2 is the receipt.**

⚠ **The regen scripts must NOT be run while the tree is red** — they commit "honest current output", which would overwrite the last-known-good `.s` artifacts that made this diagnosis possible.

---

## 7. THE RE-LAND — LANDED (s165), AND IT SEPARATES THE THREE ARMS AS ef9a7d2c DEMANDED

`ef9a7d2c`'s own message set the condition: *"any re-land has to separate those three before it can keep the good one."* Done, by **graph shape, never by language**:

`emit_graph_reads_pinned_frame() = flat_jmp_entry || flat_pat || flat_gen` — one predicate, quoting `emit.h:601`'s own stated rule back verbatim. Carve-free main graphs keep s22n's entry unchanged; **that half of CARVE-KILL is correct and is preserved.**

**Change set: 4 files, +595/-3.** `xa_flat.cpp` restored from `548c5637` (verified byte-identical to `ef9a7d2c^`, and the three CARVE-KILL commits are the *only* commits that ever touched it in this range, so the restore is a pure deletion-reversal). Enum members, declarations, and both dispatch cases restored; both call sites gated.

**TWO OWNERSHIP COLLISIONS FOUND AND FIXED BY MEASUREMENT, NOT ARGUMENT:**
1. `lbl_ω` defined twice (glue + epilogue) ⇒ `as`: `symbol proc_reverse$2F2_ω is already defined` ×4 — a graph that cannot assemble.
2. Gating the `lbl_γ` **define** as well as the body ⇒ `proc_flat_γ` unresolved at `bb_emit_end` — a label every edge jumps to and nobody defines.
**RESOLUTION:** `lbl_γ` is defined for every class; only the exit **bodies** and the `lbl_ω` define are class-specific. This restores `548c5637`'s shape verbatim for the pinned class (`emit_label_define_bb(&lbl_γ); xa_dispatch(XA_FLAT_EPILOGUE);` and nothing else).

### MEASURED, before → after

| gate | HEAD `dda156eb` | after re-land | prior green |
|---|---|---|---|
| Prolog bench green(m3&m4) | **0/22** | **10/22** | 22/22 |
| Prolog smoke m2 (**HARD GATE**) | 3/5 | **5/5** | 5/5 |
| Prolog smoke m3 | 3/5 | **5/5** | 5/5 |
| Prolog smoke m4 | 2/5 | 3/5 | 5/5 |
| Icon smoke m3 / m4 | 11/14 | **13/14 / 13/14** | 14/14 |
| all-lang hello `ROWS_DRIFT` | 2 | **1** (rebus recovered) | 0 |
| `test_gate_emit_no_lang.sh` | OK | **OK** | OK |
| SNOBOL4 / Snocone / Raku hello | ROW-MATCH | **ROW-MATCH (unregressed)** | ROW-MATCH |

⭐ **PROLOGUE PARITY IS EXACT:** emitted `nrev.s` vs the last-green artifact — `rt_jmp_frame_lexprep2` **7 = 7**, `mov rbp,rsp` **8 = 8**, `[rbp+…]` refs **1414 = 1414**. (`sub rsp` 11 vs 103 is the NOFC non-popping default, separately gated green at 185/185 — expected, not a defect.)

## 8. ⭐⭐ THE RESIDUAL IS **ONE** DEFECT, NOT TWELVE — AND IT IS **NOT** THIS ONE

Per-benchmark triage of all 22, comparing stdout to `.expected` **and** exit status:

> **clean=0 · correct-output-then-rc=139 = 21 · crash-with-no-output = 0 · other = 1 (`sendmore`)**

**21 of 22 produce byte-correct output and then segfault at teardown. ZERO produce wrong results.** The bench runner scores 10/22 only because output through a pipe is block-buffered and a crash discards it — the computation is correct in 21 cases.

⛔ **THIS SECOND DEFECT IS INDEPENDENT OF CARVE-KILL AND PRE-DATES THIS REPAIR.** `hello.pl` — a main-only program with **no predicates**, hence not in the class this gate touches — printed `hello` then rc=**139** at HEAD *before* any edit here. Icon's one-line hello does the same with rc=**134**. It lives in the **main-graph exit path** (non-pinned), i.e. the `OUTER-EXIT-1` / `EXIT-ALIGN` glue — `e840dfad` deleted the `add rsp, 24` in the outer γ/ω and called it *"WATERMARK-NEUTRAL, taken on ABI grounds."* That neutrality was measured on stdout.

⭐⭐ **WHY NO GATE CAUGHT EITHER DEFECT — THE RULE THIS EARNS:** every runner on this board compares **stdout** and ignores **exit status**. A program that computes perfectly and then dies at teardown is scored PASS wherever its output survives the pipe. **A correctness gate that does not assert `rc == 0` cannot see a teardown fault, and both defects hid in exactly that blind spot.** Proposed: add an `rc==0` assertion to the smoke/bench runners — it is one conjunct and it would have turned both of these red the day they landed.

## 9. NEXT

1. ⭐⭐ **The main-graph exit fault** (§8) — the whole residual. Owned by `OUTER-EXIT-1`/`EXIT-ALIGN`, not by this ladder; `e840dfad` is the first suspect and the deterministic instrument (§4) can now bracket it exactly.
2. **Add `rc==0` to the runners** before anything else lands — otherwise the next teardown defect hides identically.
3. `sendmore` is the only benchmark not in the clean residual class; triage separately.
4. ⛔ **Still do not run the `.s` regen scripts while the tree is red** — they commit "honest current output" and would overwrite the last-known-good artifacts that made this whole diagnosis possible.
