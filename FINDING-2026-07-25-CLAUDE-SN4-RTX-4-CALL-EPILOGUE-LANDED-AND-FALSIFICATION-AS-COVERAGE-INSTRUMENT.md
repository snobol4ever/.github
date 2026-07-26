# FINDING — RTX-4 CALL slice 1: the γ/ω landings are ported, and the falsification probe turns out to be a COVERAGE INSTRUMENT

**Session s165, 2026-07-25. Claude. Goal: `GOAL-SNOBOL4-BB.md` §SN4-RTX, rung RTX-4 CALL PATH.**
**Contract: `ARCH-SNOBOL4-RTX.md` (read first, per its own §7).**

---

## 1. WHAT LANDED

`src/runtime/rtx/rtx_call.S` — hand-written Intel-syntax asm ports of:

| symbol | role (manual Ch.8) |
|---|---|
| `rt_proc_call_epilogue_γ` | the RETURN landing (and NRETURN, a γ citizen — its by-name flag rides in `rt_g_ret_by_name`) |
| `rt_proc_call_epilogue_ω` | the FRETURN landing — *"returns from a function signaling failure to the caller. No value is returned as the function result."* |

Behind `SCRIP_RTX_CALL`, **defaulting OFF** (a new family is not defaulted on until slice 2 covers the slim landings and the visibility changes below have had a human look).

C bodies renamed `c_rt_proc_call_epilogue_γ`/`_ω` in the same commit, per the kill-switch protocol.

### Gates (all green)
- Watermark re-proven BEFORE touching anything and again after: **m3 314/1 · m4 309/4 · DIVERGE=3**, same three `21{4,5,6}_indirect_goto`.
- Smokes **7/7 × 2 modes**.
- Kill-switch byte-identity: pristine baseline, gate-off and gate-on crosscheck logs are **all md5-identical** (`0cc898346d1ad83e1b89d87a7342147a`).
- Prolog **189/0**, Icon **4/0**, Snocone **8/0** — both arms. ⚠ See §4: these are evidence about the C refactor, NOT about the asm.

### Falsification (two-sided, per ARCH §7 / RTX-1)
γ deliberately broken to report `failed=1` (every RETURN behaves like FRETURN), rebuilt:
- **gate ON ⇒ 310/5 · 305/8** — the asm really executes.
- **gate OFF ⇒ 314/1 · 309/4** — the switch really switches.
Reverted, rebuilt, re-proven. **Do not land an RTX family without this.**

---

## 2. ⭐⭐ THE METHODOLOGICAL FINDING: FALSIFICATION IS A COVERAGE INSTRUMENT, NOT JUST AN ON/OFF PROOF

RTX-1/2/3 used the falsification probe as a **binary**: break the asm, confirm the test goes red, conclude "the asm executes." Correct, but it leaves the far more useful reading on the table.

Run the SAME broken build against **every** battery and the pattern of what moves tells you **which batteries are evidence at all**:

| battery | pristine | asm deliberately broken | verdict |
|---|---|---|---|
| snobol4 | 314/1 · 309/4 | **310/5 · 305/8** | ✅ real evidence |
| prolog | 189/0 | **189/0 — unchanged** | ⛔ VACUOUS: never reaches the landing |
| icon | 4/0 | **4/0 — unchanged** | ⛔ VACUOUS |
| snocone | 8/0 | **8/0 — unchanged** | ⛔ VACUOUS |

**Three of the four batteries I ran as "gates" prove exactly nothing about the ported code.** They remain legitimate no-regression evidence for the C refactor and the visibility changes (both of which are compile/link-level and do reach every language) — but quoting "Prolog 189/0 green" as support for an asm port would have been a false claim, and I would have made it had I not run this.

**RULE PROPOSED FOR ARCH §7 step 3:** run the falsification build against the FULL battery set, not just the family's own. Record which batteries move. A battery that does not move is not a gate for this rung, and must not be cited as one. Cost: one extra rebuild. It converts an unknown into a measured coverage map.

---

## 3. ⭐ THE PORTED LANDING IS NOT THE HOT ORDINARY-CALL PATH — SLICE 2 SHOULD RETARGET

The falsification probe named the exact coverage set. Four programs in a 315-program corpus reach `rt_proc_call_epilogue_γ`:

`expr_eval` · `140_pat_eval_double_fn_trick` · `141_pat_eval_double_fn_arbno` · `161_pat_defer_fn_nested_match`

**All four are EVAL / deferred-pattern-function programs.** Ordinary `DEFINE` calls do NOT come here — they route through the slim arm (`rt_proc_call_epilogue_slim_γ/ω`, BP-7 static-save-set) or the PL-DC direct-call stubs.

So the classic γ/ω landing is the **EVAL/defer path**, and its 24 static references badly overstate its dynamic weight. This is a concrete instance of the caveat ARCH §5 already carries in the abstract — *"a static blob→runtime call count CANNOT see families the blob reaches indirectly... this table ranks the CALL BOUNDARY, not the hot path"* — and it should now be read as a worked example, not a warning.

**⇒ RTX-4 slice 2 should target `rt_proc_call_epilogue_slim_γ/ω` + the PL-DC direct-call stubs**, which is where ordinary calls actually go. Slice 1's value is the scaffold, the ABI proof, and the coverage map — not the speed.

---

## 4. THE MEASURED DEFECT, AND WHY THE ATTRIBUTION IS SPLIT THREE WAYS

`objdump` of the -O0 C of record (not a reading of the source — the source understates it):
- the popped `rt_pcall_t` copied as **16 separate scalar memory ops** (64-byte struct; the stride is visible as `shl $0x6`);
- `g_pcall_top` **loaded three times** to perform one decrement;
- `rt_k_level` reached through a **GOT indirection loaded twice** for one decrement, because the symbol was visible and therefore interposable.

~25 instructions of bookkeeping before any semantic work.

**Deliberately split into three arms so the effects can never be conflated** — this is the RTX-3 attribution lesson applied in advance rather than in hindsight:

| arm | what it isolates | γ code size |
|---|---|---|
| A — pristine C | baseline | 342 B |
| B — by-pointer C (gate OFF) | the redundant second struct copy | 307 B (−10%) |
| C — asm (gate ON) | asm over well-formed C | **178 B (−48% vs A, −42% vs B)** |

### The subtlety that must NOT be optimized away
The private 64-byte copy of the pcall record is **not** redundant. The record is popped (`g_pcall_top` decremented) BEFORE the body runs, so anything the body re-enters that pushes a new call lands on **exactly the slot still being read**. The copy is what makes that safe. It is **preserved** in the asm — merely done as 4 SSE 16-byte moves instead of 16 scalar ones.

What *was* redundant is the **second** copy: the C passed that already-private local to `rt_proc_epilogue_body` **by value**, copying 64 bytes again. Provably safe to eliminate — the body is `static` with exactly two callers, each already owning a private copy. It now takes `const rt_pcall_t *`.

---

## 5. ⛔ THIRD DOC-vs-TREE DIVERGENCE IN THREE RUNGS — AND STEP 0 DOES NOT CATCH THIS ONE

RTX-2's phantoms were **dead names** (`blk_alloc`/`blk_free`). RTX-3's were **invented names** (`rt_concat`/`rt_lcomp`/`rt_acomp`, declaration-only). RTX-4's are a new species: **live names recorded WRONG.**

`ARCH-SNOBOL4-RTX.md` §5 read `rt_proc_call_epilogue_(slim_)`. That trailing underscore is a **truncation**. The real exports are:

`rt_proc_call_epilogue_γ` · `rt_proc_call_epilogue_ω` · `rt_proc_call_epilogue_slim_γ` · `rt_proc_call_epilogue_slim_ω`

— carrying **literal UTF-8 Greek codepoints in the identifier**. The Greek character was dropped somewhere between the tree and the table, leaving the prefix.

**Step 0 as written would NOT have caught this.** It greps whether a symbol has a live definition; a truncated name simply fails to match and looks like a dead symbol, which is the wrong diagnosis and sends the rung to the wrong place. **Step 0 must be strengthened: verify names ROUND-TRIP — grep the tree, take the symbol as the tree spells it, and confirm the doc's spelling is byte-identical.** Existence is not correctness.

Also corrected in the same commit (ARCH §5 CALL row, per §7's own same-commit rule):
- **`rt/rt.c` (1667 lines) is the call spine.** The cell pointed at `invocation.c` (80 lines) + `core/name_save.c` (36) + `core/argval.c` (32). ARCH §7 tells the session to read those three IN FULL and budget a whole session for it — 148 lines that are not where the work is.
- `rt_call`, `rt_do_return`, `rt_define(_entry)` — **no live definition** (header-declaration-only). `rt_frame` is a **prefix** (`rt_frame_prep`, `rt_frame_bind_args`), not a symbol. Struck.

### GNU `as` accepts UTF-8 identifiers — settled empirically, not assumed
This was the rung's scariest unknown (an asm port must export symbols whose names contain non-ASCII bytes). It was already answered by shipping code: `rt.c`'s pre-existing inline asm does `jmp rt_proc_call_epilogue_γ` and has assembled for many sessions. Confirmed in the symbol table of the built `.so`. **No new convention was needed.**

---

## 6. C CHANGES OUTSIDE THE PORT (a human should look at these before the gate is defaulted on)

- `g_pcall`, `g_pcall_top`: de-`static`'d, `visibility("hidden")` — the asm cannot reach file-scope statics. `g_pcall_cap` stays `static` (asm never touches it).
- `rt_k_level`: marked `hidden`. It was a plain exported global, so every access in the `.so` went through the GOT. Hidden makes it `[rip+sym]`-direct **for the C as well as the asm** — an unmeasured side benefit that is deliberately NOT claimed as part of the asm win.
- `rt_proc_epilogue_body`: de-`static`'d + `hidden`, parameter by pointer.

**Verified no emitted `.s` and no template references any of these** (`corpus/**/*.s`, `src/templates/`, `src/emitter/` — only one prose comment mention). Hidden symbols bind locally in the final `.so`, which is why `nm` now shows `rt_proc_epilogue_body` as `t`; the cross-TU reference from `rtx_call.S` resolves at static-link time before that.

---

## 7. HONEST SCOPE — WHAT THIS RUNG DOES *NOT* SHOW

- **NO rail number, and none should be quoted.** Evidence here is instruction-count and code-size, not time. Combined with RTX-3's finding that the relevant benchmarks run ~20ms — an order of magnitude under this container's resolvable floor — a wall-clock claim would not be supportable. **Code size is not speed; it is offered as a proxy and labelled as one.**
- **Corpus coverage of this landing is 4 programs.** The green 315-program crosscheck is a strong *no-regression* result and a weak *correctness-of-port* result. A targeted canary battery for the EVAL/defer path is owed.
- The `-O0`-vs-`-O2` question remains **OPEN** and still needs a Lon directive (O2-DIRECTED-ONLY). All arms here are `-O0`, which is what ships.
- ⚠ NO `gdb` in this container; monitor still dark. Differential + falsification remain the working substitute.

---

## 8. NEXT

1. **RTX-4 slice 2 — retarget to `rt_proc_call_epilogue_slim_γ/ω` + PL-DC direct-call stubs** (§3). That is the ordinary-call path.
2. Add the EVAL/defer canary battery for the four named programs (§7).
3. Adopt the ARCH §7 amendments: falsification-across-all-batteries (§2), and round-trip symbol verification in step 0 (§5).
4. Default `SCRIP_RTX_CALL=1` only after 1–2, and after review of §6.
