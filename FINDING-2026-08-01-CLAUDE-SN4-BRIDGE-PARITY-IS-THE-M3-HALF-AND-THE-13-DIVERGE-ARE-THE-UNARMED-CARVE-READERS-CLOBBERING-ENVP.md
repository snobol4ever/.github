# FINDING s22q — THE BRIDGE'S m3 HALF IS ARRIVAL PARITY, AND THE 13 REMAINING DIVERGE ARE THE UNARMED CARVE READERS CLOBBERING `envp`

**Session:** s22q, 2026-08-01, Claude (Opus 5)
**Goal:** `GOAL-SNOBOL4-BB.md` — s22p NEXT(1) (m3 DIVERGE sweep)
**Commits:** SCRIP `150e903e` (ONE-SHOT-BRIDGE-M3) · `e840dfad` (EXIT-ALIGN) · `19f54aac` (feature artifacts) · corpus `2f99acba` + `98ee1ad9` (benchmark/demo artifacts) · `.github` cursor
**Watermark:** m3 **73/244 → 199/118** · m4 **186/130/1** (unchanged, identical by set) · **DIVERGE 125 → 13**

---

## 1. ⭐⭐⭐ s22p's NEXT(1) NAMED THE WRONG END OF THE BRIDGE

s22p left the rung as: *"The fix is landing the same one-shot bridge in mode-3 (a `call exit` via `x86_call_ro` using the runtime's own exit symbol, or a raw syscall)."* That is the **exit** side. **It would not have moved a single program.**

The one-shot bridge changed the rsp parity at which the graph's α is **ENTERED**, and only mode-4 was updated:

| mode | how α is entered | α arrives at |
|------|------------------|--------------|
| m4 | `main` moves 24B (`sub rsp,8` + `push rdi` + `push rsi`), then **`jmp main_α`** | rsp ≡ **0** (mod 16) |
| m3 | `rt_outer_call` does `sub $8`, then **`call *%rax`** (pushes 8 more) | rsp ≡ **8** (mod 16) |

Both modes then run the **same** α preamble — `bb_glue_framed_enter`'s `push rbp` + `sub rsp,8`. So mode-3 carried an **8-byte skew into every C call the graph makes**, and died in the first glibc routine touching an aligned SSE op.

**THE 244 m3 FAILURES WERE ONE AUTHORITY, NOT 244 DEFECTS** — the same shape as s22n's "311 m4 failures is ONE missing authority."

**FIX = ONE CONSTANT.** `rt_outer_call`'s adjuster is **16, not 8** (`src/runtime/rt/rt.c`). The 8 was correct only for the pre-bridge parity; its own comment names it the alignment adjuster, sized when the deleted prologue owned α. Mode-3 **keeps `ret`** (correct — no PLT in the JIT slab) and now agrees with mode-4 on arrival.

**Result: m3 73/244 → 199/118, +126 programs, ZERO regressions (diffed by set), m4 identical by set, DIVERGE 125 → 13.** Emitted `.s` byte-identical, verified by diff → no artifact regen owed for that commit.

---

## 2. ⭐⭐ THE INSTRUMENT — PARITY IS A DIFFERENTIAL MEASUREMENT, IN ONE PROCESS

Do this before touching a spine bug again. Break on the C sink the graph calls; read `rsp % 16` at entry, **in both modes**:

```
break NV_SET_fn ; run ; printf "%ld\n", ((long)$rsp) % 16
```

Witness `002_output_integer_literal` / `NV_SET_fn`: **m3 = 8 → SIGSEGV in `dl_iterate_phdr` via `gc_static_segs_init`; m4 = 0 → prints 42.**

⭐ **WHAT MAKES IT DECISIVE:** the **C-side `core_lib_init` calls in that same m3 process measured 0.** That is what separates *"the graph is skewed"* from *"the runtime is broken"* — without the in-process control, a misalignment looks like a runtime bug and sends the hunt into the wrong tree.

⚠ **gdb needs `apt-get update` FIRST.** A bare `apt-get install -y gdb` returns rc=100, 404 on `libc6-dbg`. The goal file's "gdb IS AVAILABLE" note is correct but incomplete. Also: `$rsp` is a pointer type — `$rsp % 16` errors with *"Argument to arithmetic operation not a number"*; cast it: `((long)$rsp) % 16`. And `break *SYMBOL` **cannot be made pending**, so a symbol living in `libscrip_rt.so` needs the function-form breakpoint (which lands after the prologue — fine, because a **differential** across modes at the same breakpoint is still valid).

---

## 3. ⭐ EXIT-ALIGN — WATERMARK-NEUTRAL, TAKEN ON ABI GROUNDS, AND SAID SO

s22p called `add rsp, 24` in the outer γ/ω "the one fragile constant." It is worse than fragile: it was **wrong on every mode-4 program**. It restored rsp to main's CRT entry value before `call exit@PLT` — but **exit() never returns**, so the restoration buys nothing, while **entry parity is precisely the wrong parity to call from**. After `bb_glue_framed_leave` rsp is already ≡ 0 (mod 16), which is call-correct; `+24` moved it to ≡ 8.

**MEASURED** at `rt_rspd_report` (the `.so` destructor `exit()` runs), `rsp % 16`:
- `W06_pos` (crashes) = **8**
- `002_output_integer_literal` (passes) = **8**

**Every m4 program was misaligned; the passing ones were LUCKY.** That is why the m4 fail set looked arbitrary — the fault lands wherever glibc first touches an aligned SSE op on a spilled local (`getenv` via `_dl_call_fini`), **never in the graph**, so it reads as a pattern defect.

⭐ Deleted rather than retuned to 16: nothing downstream of the whack needs rsp restored, so the coupling to the driver preamble is **removed outright instead of re-sized** — one less cross-file constant to drift.

⛔ **HONESTY ON THE LICENCE:** crosscheck is **IDENTICAL BY SET** in both modes before and after. s21x-y's law applies and is honored, not dodged — *neutrality proves a change breaks nothing, never that it belongs.* What licenses this is the measured ABI violation, **not** the watermark. It fixed zero programs. Recorded as such.

---

## 4. ⭐⭐⭐ THE 13 REMAINING DIVERGE ARE ONE AUTHORITY: UNARMED CARVE READERS WRITING THROUGH `envp`

All 13 are the **same shape — m3 PASSES, m4 FAILS** (11 of them rc=139):

```
098_keyword_anchor  064_replace_multi_arm  142_pat_arbno_fence_arbno
153_pat_operand_edge_matrix  170_pat_abort_kills_match
177_pat_bal_unbalanced_rejected  1016_eval
W06_pos  W06_rpos  W06_tab  W07_capt_cond  W07_capt_cur  W07_capt_imm
```

⚠ **`170` and `177` are the stdout-only artifact class** the s22l-B cursor named: m3 "PASS" **with rc=139** — correct output flushed, then death. A crosscheck ignoring exit status cannot see them, so both the DIVERGE count and the m3 PASS count are slightly optimistic.

### The measurement

Witness `W06_pos`, m4. The crash is **not in the graph** — it is `main_γ` → `exit()` → destructor `rt_rspd_report()` → `getenv` → SEGV. With EXIT-ALIGN landed, `rsp % 16 = 0` there, so **alignment is not the cause**. Then:

```
AT_GAMMA rsp=0x7fffffffe960 rbp=0x7fffffffe968
p (char**)__environ      -> 0x7fffffffeab8          (CORRECT: argv+16, argc==1)
p ((char**)__environ)[0] -> 0x3  <error: Cannot access memory at address 0x3>
```

**`__environ` is right; the array it points at has been OVERWRITTEN.** `0x7fffffffeab8` is `rbp + 0x150` = **`[rbp + 336]`** — inside the **deleted** whole-graph carve. And `0x3` is not garbage, it is a **descriptor type tag** (cf. `mov qword ptr [rsp+0], 6` in ordinary emitted code): a box wrote its descriptor cell straight into the envp array.

Confirming from the emitted `.s` for `W06_pos`: **zero `[rbp + N]` sites**, but `[rsp + N]` reaching **568**. At α, `rsp = 0x7fffffffe960` and envp sits at **`rsp + 344`**. Offsets past 344 write through argv/envp and everything above.

### What it means

This is exactly the debt the LIVE CURSOR already names — *"`emit.cpp:2587` still computes `flat_frame_bytes = 48 + jcon_value_region`. Nothing allocates it now, but ~1054 `FR`/`FRQ`/`FRQB` readers still address into it — overwhelmingly the pattern-blob family, which has zero ZD arms"* — but it had **no witness**. It does now, and the witness upgrades the debt's status:

⭐⭐ **THE UNARMED READERS ARE NOT MERELY READING A DEAD REGION — THEY ARE WRITING THROUGH LIVE PROCESS STATE.** s22n predicted the class (*"those 150 instructions address the CALLER's live frame — silent corruption, not clean faults"*) and predicted it correctly. The specific casualty is `envp`, which is why the symptom surfaces in `getenv` inside an **exit-time destructor**, arbitrarily far from the box that did the damage.

⛔ **DO NOT RE-CARVE.** THE MODEL forbids it and the fix is not a bigger backing store. The job stays what it has been: **convert the readers to their own per-BB cells until the carve has no customers.** The pattern-blob family (`IR_MATCH_LIT..IR_MATCH_ADVANCE`, `IR_MATCH_HEAD`, `IR_CALL`) is the unarmed mass and is the next rung.

⭐ **WHY THIS DIAGNOSIS WAS CHEAP AND SHOULD BE REUSED:** the useful question was not *"why does `getenv` crash"* but *"is `__environ` valid, and if so what is AT it."* One `p ((char**)__environ)[0]` separated a runtime bug from a stack-overwrite, and one offset subtraction against `rbp` named the region. **Do this before bisecting templates.**

---

## 5. ⛔ PARITY IS NOW A CONTRACT WITH TWO SIGNATORIES

Anything that changes how α is reached — a new dynamic-glue entry, the DYNAMIC BOX, a `jmp`-entry flavor, or moving `framed_enter` — **must state which parity it delivers, and be checked in BOTH modes.** The bridge made α's arrival parity a cross-mode invariant; nothing enforces it but this rule and the crosscheck.

⭐ The TREEBANK H11 `Pop_list` finding (`mod16=8`, rsp rose +104) belongs to this class. **That hunt may now be a parity question rather than a release-accounting one** — re-read it before spending a rung on release accounting.

---

## 6. ⭐ m4 IS NOW THE LAGGING MODE

m3 **199** vs m4 **186**. The inversion is new — every prior cursor has m4 ahead or level. The m4-only fail set is a work order that did not exist before this session, and §4 says most of it is likely **one** authority, not 130.

---

## 7. NEXT — ORDERED

1. ⭐⭐⭐ **Pattern-blob ZD family** (~1054 `FR`/`FRQ`/`FRQB` readers, zero ZD arms). §4 gives the witness and the failure mode. This is THE MODEL's stated job and it now has a reproducible casualty (`W06_pos`, `[rsp+568]` vs a 344-byte headroom).
2. **A cheap tripwire for the class:** assert at γ that `((char**)__environ)[0]` is still a readable pointer, or checkpoint the envp word at α and compare at γ. Turns a silent exit-time corruption into a loud, localized failure. Costs two instructions in a debug arm.
3. **NOFC symmetric default-ON** (s22l: +32/+33) — still Lon's call, still one line, and the s22l-B attribution correction (the win is carve suppression, not the non-popping read) should be re-measured at this HEAD now that both bridge halves are in.
4. **`170` / `177`** — make the crosscheck see exit status, or these keep counting as m3 PASS while crashing.
5. **JOIN-POINT RULE** — δ_out well-defined only if every path into a box arrives at the same accumulated depth; the FAIL edge out of a deep pattern is still unnamed.

---

## 8. HOUSEKEEPING

- `.s` artifact regens run at HEAD after EXIT-ALIGN (benchmark, feature, demo) — SCRIP `19f54aac`, corpus `2f99acba` + `98ee1ad9`. The ONE-SHOT-BRIDGE-M3 commit owed none (runtime-thunk only; emitted `.s` proven byte-identical by diff, not assumed).
- Both `.github` and `corpus` needed `git config user.name/email` set locally before their first commit (`root@vm.(none)` otherwise). Only SCRIP's was pre-set.
- ⚠ **`bb_glue_outer_γ/ω` still carries the `IF(MEDIUM_TEXT,…) + IF(MEDIUM_BINARY,…)` split**, which RULES.md calls an absolute violation and `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` names as the forbidden shape. s22p took it knowingly for the PLT/preamble asymmetry. **The preamble half of that justification is now GONE** (EXIT-ALIGN deleted the `add rsp,24`), so the only remaining asymmetry is `exit@PLT` vs `ret` — a genuine medium difference that belongs **inside** an encoder. Collapsing it is now a smaller job than when s22p wrote it. Not attempted this session.
