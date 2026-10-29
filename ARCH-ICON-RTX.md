# ARCH-ICON-RTX.md — The Icon Runtime in Optimized x86-64 Assembly

**Minted s203-ICN (2026-07-29, Claude + Lon PIVOT directive). READ THIS BEFORE ANY ICON-RTX RUNG.**
It is the register/ABI/build/ownership contract; the ladder lives in `GOAL-ICON-RTX.md`.

**Lon's directive as given:** *"Move all C runtime code into asm code in `*.s` files. Or move code into
mode BB templates, either one will be fine. Just ASM code not C code."* — §6 turns that two-way choice
into a per-family RULING rather than a per-rung coin flip, because the two destinations have
different concurrency costs and different `.s`-regen obligations.

---

## 0. ⛔⛔ THE ONE FACT THAT MAKES THIS LADDER DIFFERENT FROM SN4-RTX — READ IT FIRST

**ICON DOES NOT HAVE ITS OWN RUNTIME. IT SHARES SNOBOL4'S.** Measured s203-ICN, not assumed:
Icon-specific runtime C in the whole tree is **`src/parser/icon/icon_runtime.c`, 67 lines, 3 functions**
(`icon_compile`, `icon_register_program`, `icon_real_str`). Everything else Icon calls at run time is
the SAME `src/runtime/` that SNOBOL4, Prolog, Snocone, Raku and Pascal call.

**THREE CONSEQUENCES, ALL STRUCTURAL:**

1. **ICON-RTX INHERITS SN4-RTX's LANDED WORK FOR FREE.** Nine symbols on Icon's own hot list are
   already assembly: `str_concat_d` · `rt_gcheap_alloc` · `rt_str_alloc` · `rt_agg_alloc` · `rt_cmp_d` ·
   `rt_faildescr` · `rt_is_truthy` · `rt_proc_call_epilogue_γ/ω` · `rt_proc_call_epilogue_slim_γ/ω`
   (`src/runtime/rtx/*.S`), plus `rt_deref` · `to_int` · `rt_sg_member` · `rt_sg_scan_member` ·
   `rt_sg_scan_nonmember` ungated in `src/runtime/rt/rt_asm_helpers.S`. **A rung that ports any of these
   is porting finished work** — ARCH-SNOBOL4-RTX §7 step 0(e) exists precisely because that already
   happened once.

2. **⛔⛔ ICON-RTX AND SN4-RTX CAN COLLIDE ON THE SAME SYMBOL — SN4-RTX's CONCURRENCY CONTRACT DOES NOT
   COVER THIS AND MUST BE AMENDED.** That contract (`GOAL-SNOBOL4-RTX.md` §CONCURRENCY) partitions
   `RTX owns src/runtime/rtx/*.S + rt/*.c + family C sources` against `ζ-storage owns emit.cpp +
   templates + x86_asm.h`. It assumes **ONE** RTX ladder. With two, `rt_call_arr` is simultaneously
   ICON-RTX's #1 target (2157 static sites) and SN4-RTX's open RTX-4 SLICE 3 — **one symbol, one file,
   two ladders, two sessions.** See §7 for the amendment. **This is the single largest structural risk
   of the pivot and it is a Lon-level sequencing call, not a session's.**

3. **THE KILL-SWITCH AND WATERMARK ARE SHARED STATE ACROSS LANGUAGES.** `SCRIP_RTX_<FAM>=0` disables the
   family for SNOBOL4 *and* Icon *and* Prolog. An ICON-RTX landing therefore owes the SNOBOL4 and Prolog
   watermarks as no-regression gates — and, by §7 step 2b's rule, **may not cite them as evidence that
   the asm executes.**

---

## 1. RULINGS OF RECORD — INHERITED FROM ARCH-SNOBOL4-RTX §1, UNCHANGED

1. **SYNTAX: Intel, one project-wide.** GNU `as` + `.intel_syntax noprefix`.
2. **C BOUNDARY: libc only.** No direct `syscall`.
3. **MIGRATION: dual-build, per-family kill-switch, then eradicate.**
4. **REGISTERS: phase-1 blob pins UNCHANGED; RTX owns the volatile nine internally.**

⚠ **Three ungated AT&T-syntax holdouts already violate Ruling 1** (`rt_sg_scan_member`,
`rt_sg_scan_nonmember`, `rt_sg_member`) — inherited debt, recorded in
`GOAL-SNOBOL4-RTX.md` s202. ICON-RTX does not add to it. ⭐ **WAS FOUR: `rk_gram_enter_box` and its
whole file `rt_gram_trampoline.S` were DELETED 2026-09-21 (cto, SCRIP `84a66f65e`) on Lon's order to
delete the dead C->BB code — it was unreachable by construction, because nothing ever registered the
`gram__` procedures whose `fn` it needed. One item of this debt is paid, not re-scoped.

---

## 2. REGISTER CONTRACT — IDENTICAL TO ARCH-SNOBOL4-RTX §2, PLUS ICON'S SUBJECT PINS

The blob pins are the SysV callee-saved set and are the same for every language. **Do not restate them
from memory — `ARCH-SNOBOL4-RTX.md` §2 is the single source, and it was found STALE and load-bearing as
recently as s205.** The corrected facts as of s205, re-verified against `x86_asm.h:347-361` and
`zeta_choices.h:177` at the time of this file's minting:

| reg | role |
|---|---|
| rbx | ⛔ **NOT THE ARENA TOP IN THE TREE — FREE, PRESERVED ONLY (measured by the ceo 2026-09-24 16:2x CDT, Lon: *"If RBX is not used for the frontier, then correct that wrong doc"*; CEO-1243).** The allocation frontier is the MEMORY struct `g_hp_fr` (`.top` at offset 0, `gc_heap.c:25`, 23 references), read through memory by the allocator and by `rt_gc_poll_asm`; today's compiler emits ZERO `rbx` instructions in the arith_loop twin, and across the 195 committed `.s` artifacts rbx appears only as the glue frame's save/reload pair (`mov [rsp+48], rbx` ×11 / `mov rbx, [rsp+48]` ×66, `bb_glue_flat.cpp:140/146`); the hand-written `rtx_*.s` never touch it; the runtime C only saves/restores it (co-expression context `rt_coexpr.c:27`, contract capture `rt.c:1250`, thread entry `rt.c:1173`). The row that stood here (*arena heap top — DESCR mint pointer*) described the RTX DESIGN, never the tree; Lon's 2026-09-19 order to make it so (§ 6.2j of `ARCH-GC-COMPILE-TIME-FRAME-MAPS.md`, CEO-959) is UNEXECUTED at this rewrite, and on 2026-09-24 16:1x Lon asked whether rbx should instead carry the &STLIMIT statement countdown — OPEN WITH LON; until he rules, the countdown uses the granted global (Lon 16:1x: *"Meanwhile use the global."*). |
| r12 | ⛔ **FREE — NOT A PIN.** `ZC_FRAME_R12` DELETED at ZR-RSPRBP-1 (`da8c2347`). ζ basis CLOSED at {RSP,RBP}. |
| r13 | **Σ subject base** |
| r14 | **δ subject cursor** (0-based; `&pos` = δ+1) |
| r15 | **Δ subject length/end** |
| rsp | ζ + C stack (one stack) |
| rbp | ζ frame base **IN PINNED GRAPHS ONLY**; **rsp** for depth-static determinate graphs. ONE selector: `x86_fb_pinned()`. |

⛔⛔ **NEVER hardcode `[rbp+off]` or `[rsp+off]` in ICON-RTX asm or in any template. Use `FR(off)`/`FRQ(off)`.**
A hardcoded base encodes the wrong thing **silently** — `GOAL-ICON-BB.md` s202 measured 9 net new crashes
from exactly one basis mistake.

**⭐ ICON-SPECIFIC AND LOAD-BEARING: R13/R14/R15 ARE LIVE ACROSS THE SCAN FAMILY.** They are not merely
callee-saved bookkeeping for Icon the way they are for a SNOBOL4 arithmetic port — they carry the scan
environment that `bb_gen_scan.cpp` swaps. **Any ICON-RTX routine on the scan path must treat Σ/δ/Δ as
live INPUT, not as scratch it happens to preserve.** This is the axis on which an SN4-derived idiom is
most likely to be wrong for Icon.

**RTX working set (free at entry, zero boundary cost):** rax rcx rdx rsi rdi r8 r9 r10 r11 + xmm0-15.

**DESCRIPTOR-PAIR CONVENTION:** `DESCR_t` = 16 B = `{DTYPE_t v; uint32_t slen}` + `union{...}`; two
INTEGER-class eightbytes ⇒ SysV passes by-value in a register pair and returns in **rdx:rax**. Phase-1
ports keeping C signatures get descriptor-in-registers for free.

---

## 3. BOUNDARY PROTOCOLS

Identical to `ARCH-SNOBOL4-RTX.md` §3. Phase 1 keeps every exported symbol's EXACT current C signature;
speed comes from bodies, not convention ⇒ **no template edits, no `.s` regen, no both-medium work.**
Phase 2 (registerized ABI) fires `.s` regen ×3 and enters the ζ ladder's territory — serialize.

---

## 4. FILE LAYOUT · BUILD · KILL-SWITCH

**ICON-RTX ADDS NO NEW MACHINERY. It reuses SN4-RTX's, which is already proven and already linked.**

- **Source:** `src/runtime/rtx/rtx_<family>.S`, `.intel_syntax noprefix`, macros from `rtx_abi.inc`
  (`RTX_FUNC` / `RTX_ENDF` / `RTX_GATE_DEF` / `RTX_GATE`).
- **Build:** each `.S` → `gcc -c` → linked into BOTH `scrip` (mode 3) and `libscrip_rt.so` (mode 4).
  `scrip` links **dynamically** against `libscrip_rt.so` ⇒ ONE runtime copy serves both modes ⇒ adding a
  `.S` to `RT_PIC_SRCS` gets both modes by construction.
- **Kill-switch:** C body renamed `c_<name>`; asm exports `<name>` and gates
  `cmp byte ptr [rip+rtx_gate_<fam>],0 ; je c_<name>`. Gate bytes are `.hidden`.
- **Existing gates (six, all shared with SNOBOL4):** `SCRIP_RTX_MISC` · `ALLOC` · `STR` · `CALL` ·
  `ARITH` · `LEAF`.
- **⭐ NEW GATES ICON-RTX INTRODUCES:** `SCRIP_RTX_SCAN` (Icon scan/generator family — no SNOBOL4
  analogue) and, if §6 rules it in, `SCRIP_RTX_IO`.

⚠ **`x86_asm.h` IS A HEADER — `make` DOES NOT TRACK IT.** `rm -rf out /tmp/si_objs` or you get a
byte-identical binary and a false negative (`GOAL-ICON-BB.md` s197). ⚠ **The emitter lives in
`out/libscrip_rt.so`, NOT in the 182 KB `scrip` driver** — verify edits against the `.so`.

---

## 5. THE REPLACEMENT INVENTORY — MEASURED s203-ICN, AND THE MEASUREMENT ITSELF HAS A TRAP

**Method (reproduce it; do not trust the table):** static `call` targets across the **265 LIVE** Icon
artifacts in `corpus/programs/icon/` + `corpus/benchmarks/icon/`, where LIVE = first line is
`.intel_syntax noprefix`. ⛔ **PATH STALE, CORRECTED 2026-08-29 (seat16, citation sweep) —
`corpus/programs/icon/` confirmed absent.** `.s` artifacts now live only beside benchmarks and demos
(RULES.md handoff step 4), so the search below should be `benchmarks/icon` + `demos/icon` — **the 265
count itself is NOT re-verified against that new pair**, only the path is corrected; re-run before
trusting a number.

```bash
for f in $(find benchmarks/icon demos/icon -name '*.s'); do
  head -1 "$f" | grep -q intel_syntax && echo "$f"; done > /tmp/live
xargs grep -hoP '^\s*call\s+\K[^\s,]+@PLT' < /tmp/live | sed 's/@PLT//' | sort | uniq -c | sort -rn
```

⛔⛔ **TWO FILTERS ARE MANDATORY AND BOTH WERE LEARNED THE HARD WAY IN THE MINTING SESSION:**

**(i) THE LIVE-MARKER FILTER — reproduces ARCH-SNOBOL4-RTX §5's RTX-2 correction, one language over.**
305 Icon `.s` artifacts exist; **only 265 are live.** The other 40 are legacy `scrip-cc -asm`
nasm-syntax references. Sweeping all 305 manufactures four high-count symbols that the compiler
**cannot emit**: `icn_write_str` (510) · `icn_push` (242) · `icn_pop` (124) · `icn_write_int` (97).
Measured: **0 of the 265 live artifacts reference any of them.**

**(ii) ⭐⭐ THE `@PLT` FILTER — A NEW FAILURE MODE, NOT PREVIOUSLY IN THE PHANTOM TAXONOMY.**
A runtime call into `libscrip_rt.so` is emitted `call sym@PLT`. A **locally emitted label** — the BB
four-port machinery, `main_α`, `proc_report_dcα`, `proc_startup`, `rt_gen_spine_pass_γ` — is emitted
`call sym` with no suffix. **Stripping to `[A-Za-z_0-9]*` collapses the two classes together AND
truncates the Greek codepoints**, so a naive inventory reports emitted-inline asm as if it were a C port
target. **Prior phantoms were DEAD names (RTX-2), INVENTED names (RTX-3), MISRECORDED names (RTX-4),
COLD names (s188) and ALREADY-ASM names (s200). This one is a name that is not a runtime symbol at all.**
⇒ **`@PLT` is the discriminator, it is free, and it is now step 0(f).**

### LIVE C-RUNTIME SURFACE FOR ICON (static call sites, 265 artifacts, s203-ICN)

| rank | symbol | sites | definition | status |
|---|---|---|---|---|
| 1 | `rt_call_arr` | 2157 | `by_name_dispatch.c` | ⚠ **COLD FOR SNOBOL4 (s188). UNKNOWN FOR ICON — step 0(d) DECIDES.** |
| 2 | `rt_arg_stage` | 897 | `rt.c` | unported |
| 3 | `rt_write_any_nl` | 566 | `io_format.c` | unported |
| 4 | `rt_call_proc_descr` | 542 | `rt.c` | unported |
| 5 | `rt_proc_set_fn` | 361 | `rt.c` | unported (proc-setup family) |
| 6 | `to_int` | 286 | `rt_asm_helpers.S` | ✅ **ALREADY ASM** (LEAF gate) |
| 7 | `rt_frame` | 255 | `rt.c` | unported |
| 8 | `rt_bomb` | 215 | `runtime_init.c` | ⛔ error path — cold by design, do not port |
| 9-12 | `rt_proc_set_nparams` · `_jmpentry` · `_frame_bytes` · `_dcfn` | 210/210/209/202 | `rt.c` | unported (proc-setup family) |
| 13 | `rt_jmp_frame_lexprep2` | 209 | `rt.c` | unported |
| 14 | `rt_coerce_num2_d` | 209 | `rt.c` | unported |
| 15 | `rt_num_arith` | 208 | `arithmetic.c` | ⚠ SN4-RTX RTX-6 remainder targets this — **COLLISION** |
| 16 | `rt_pl_dc_prep` | 202 | `rt.c` | unported (dual-entry; see FLATDISP) |
| 17 | `rt_deref` | 193 | `rt_asm_helpers.S` | ✅ **ALREADY ASM** |
| 18 | `rt_subscript_var` | 177 | `pattern_match.c` | unported (SN4-RTX RTX-5 family) |
| 19 | `rt_jct_relop` | 163 | `by_name_dispatch.c` | unported |
| 20 | `rt_assign_var` | 147 | `pattern_match.c` | unported |
| 21 | `rt_binop_overload` | 141 | `arithmetic.c` | unported |
| 22 | `rt_keyword_read` | 136 | `keywords.c` | ⚠ fragile allowlist (`GOAL-ICON-BB.md`) — port ≠ fix |
| 23 | `rt_proc_value` | 126 | `by_name_dispatch.c` | unported |
| 24 | `rt_scan_leave` | 120 | `builtins/gen_runtime.c` | ⭐ **ICON-OWN — SCAN family** |
| 25 | `str_concat_d` | 112 | `rtx_str.S` | ✅ **ALREADY ASM** (STR gate) |
| 26 | `rt_list_bang_at` | 110 | `rt.c` | unported |
| 27 | `rt_substr` | 109 | `builtins/gen_runtime.c` | ⭐ **ICON-OWN — SCAN family** |
| 28 | `NV_GET_fn` | 109 | `rt.c` | ⚠ DB-1 write-barrier choke point — coordinate |
| — | `rt_scan_enter` | 69 | `builtins/gen_runtime.c` | ⭐ **ICON-OWN — SCAN family** |

⚠ **A STATIC COUNT IS A PROPERTY OF PROGRAM TEXT, NOT OF EXECUTION.** This whole table measures the CALL
BOUNDARY. It ranks nothing until step 0(d) counts the symbol dynamically, at two loop counts, and
confirms it SCALES. `rt_call_arr` is the standing proof: **232 static sites for SNOBOL4 and 8 calls flat
across N=1→N=64.** Its 2157 for Icon is a *bigger* static number and therefore *no more* evidence.

**C runtime total: 19,962 LOC** across `src/runtime/`. Icon-specific share of that: **67 lines (0.34%).**

---

## 6. THE FORK LON OPENED — `.S` PORT vs BB TEMPLATE, RULED PER FAMILY

Lon's directive allows either destination. They are **not** interchangeable, and the difference is
concurrency cost, not taste:

| | `.S` port (phase 1) | BB template |
|---|---|---|
| touches | `src/runtime/rtx/*.S`, family C | `src/templates/*.cpp`, `emit.cpp`, `x86_asm.h` |
| `.s` regen | **never** | **×3, always** |
| both-medium (R2/R7/R9/R10) | N/A | **mandatory** |
| concurrency vs the ζ/ICON-BB ladder | **safe** | ⛔ **direct collision** |
| removes the call boundary | no | **yes** |

**RULING (proposed — Lon confirms):**

- **DEFAULT = `.S` PORT.** It is concurrency-safe against the live ICON-BB ζ ladder, owes no `.s` regen,
  and is the destination every landed RTX rung has used.
- **⭐ EXCEPTION = THE SCAN/GENERATOR FAMILY → BB TEMPLATE.** `rt_scan_enter` / `rt_scan_leave` /
  `rt_substr` are **Icon's own**, they have no SNOBOL4 analogue, and they are the one family where the
  call boundary is itself the architectural defect: `ARCH-LANGUAGES.md` specifies scanning as no-software-value-stack BB
  templates with Σ/δ/Δ pinned in r13/r14/r15, so a `call rt_scan_enter@PLT` spills and reloads exactly
  the registers the design pins. **Porting that to `.S` would make the wrong thing faster.** Moving it
  into templates deletes the boundary. ⛔ **But it is template work: `.s` regen ×3, both-medium, and it
  collides head-on with the ICON-BB session. SEQUENCE IT, do not run it concurrently.**
- **`rt_bomb` and the error paths: PORT NOTHING.** Cold by design.

---

## 7. ⛔⛔ CONCURRENCY — THE THREE-WAY AMENDMENT

SN4-RTX's contract is two-way (RTX ‖ ζ). With ICON-RTX there are **three** live ladders over
**two** shared surfaces. The amendment:

| ladder | owns | must not touch |
|---|---|---|
| **ICON-BB (ζ)** | `emit.cpp`, `templates/*.cpp`, `x86_asm.h`, `zeta_storage.c` | `runtime/rtx/*.S` |
| **SN4-RTX** | `runtime/rtx/*.S` + family C — **by SYMBOL, see below** | templates |
| **ICON-RTX** | `runtime/rtx/*.S` + family C — **by SYMBOL, see below** | templates (except a §6-ruled SCAN rung, serialized) |

**⭐ THE SYMBOL-LEVEL RULE, because file-level partition is INSUFFICIENT once two RTX ladders exist:**

1. **A symbol is owned by ONE ladder at a time.** Claim it in that ladder's LIVE CURSOR before editing.
2. **`rt_call_arr`, `rt_num_arith`, `rt_subscript_var` are ALREADY CLAIMED by SN4-RTX** (RTX-4 SLICE 3,
   RTX-6 remainder, RTX-5). ICON-RTX must not open them without Lon re-assigning.
3. **A shared-symbol port owes BOTH languages' watermarks** — and per §7 step 2b may cite neither as
   evidence the asm executes.
4. **`Makefile` link lines and the six gate bytes are shared state.** Small, but real rebase points.

---

## 8. EVERY-RUNG PROTOCOL — SIX CHECKS (INHERITS ARCH-SNOBOL4-RTX §7, ADDS (f))

0. **(a)** live definition exists · **(b)** spelling round-trips byte-identically (Greek codepoints!) ·
   **(c)** `nm` the linkage of every global touched (exported `B`/`D` ⇒ `@GOTPCREL`; hidden ⇒ direct) ·
   **(d)** ⭐⭐ **prove the symbol EXECUTES in the window you intend to move**, at two loop counts,
   confirm it SCALES · **(e)** confirm it is **not already assembly** (grep **with `--include=*.S`**) ·
   **(f)** ⭐⭐ **confirm it is a RUNTIME symbol and not a locally emitted label: it must appear as
   `call sym@PLT` in a LIVE artifact.** See §5(ii).
   **(i)** ⭐ **derive static counts from `scrip --compile`, NEVER from a stored `.s` tree** (s213: 255 of
   265 "live" Icon artifacts are frozen a month stale and RULES.md forbids regenerating them).
   ⭐ **AMENDED s216: the intersection must ALSO scan `src/driver/**` and `src/parser/**`, or better be
   driven by `nm -D out/libscrip_rt.so`.** `dat_field_get` is bodied in `src/driver/driver_data.c`, so a
   sweep restricted to `src/runtime/**/*.c` ranked 67 rows **without it** while the same run's call tally
   showed 117 sites. **Every driver-bodied symbol is invisible to a runtime-only glob.**
   **(d2)** ⭐⭐⭐ **THE WINDOW-DOMINANCE RULE — ADDED s221, AND IT SUPERSEDES "RUN-PHASE-DOMINANT" AS THE
   GRADING CRITERION.** s220 established that a window must be RUN PHASE, not compile. **That is necessary
   and NOT sufficient: the window must additionally be dominated by THE THING BEING PORTED.** Proof, one
   fix measured on two run-phase windows: RTX-16 converted 40,000 bails in `bench_icnstr_concat_table`
   (95% run phase) for a **MEASURED NULL** (198→195 ms, overlapping), and 2,000,000 bails in
   `bench_icnstr_concat_dispatch` for **~2.4–3.3×** (194–231→59–62 ms, disjoint). `concat_table`'s run
   phase is O(n²) byte copy + 119,999 `rt_str_alloc`; its `str_concat_d` bails cost `strlen("x")` — O(1).
   ⇒ **A BAIL COUNT CANNOT PREDICT BENEFIT, exactly as s188 proved a CALL count cannot.** The instrument is
   **bail COST SHARE**: build the grading window from constant-size operands, no growth, no allocation
   scaling, result discarded, so the ported operation's own dispatch IS the measured cost.
   ⛔ **Never grade a dispatch port on an allocation-dominated window; the null is an artifact of the
   window and will be misread as a refusal of the asm.**
   **(j)** ⭐⭐ **THE ARM CHECK — ADOPTED s216 FROM SN4-RTX, WHICH MINTED IT THE SAME DAY.** It is
   `ARCH-SNOBOL4-RTX.md`'s step **(f)**; ⚠ **that letter is ALREADY TAKEN on this ladder by the `@PLT`
   check above, so ICON-RTX files it as (j). Same check, different letter — do not renumber (f).**
   ⛔⛔ **0(d) COUNTS ENTRIES TO A SYMBOL; A GATED PORT IS A SYMBOL WITH ARMS, AND THE ASM COVERS ONLY
   THE ARM THE AUTHOR CHOSE — SO 0(d) CAN PASS IN FULL WHILE THE PORTED ARM IS DEAD.** SN4-RTX's proof:
   `rt_cap_push` took 57,578 dynamic calls, scaled exactly 2.00×, was the hottest unported symbol in its
   family — **and its ported path never executed once.** Run
   `bash scripts/util_rtx_arm_census.sh <prog>` on the workload the rung will be GRADED on, **before
   writing any asm**; it counts `sym` vs `c_sym` and prints `COMMITS = entries − bailed`.
   **`COMMITS == 0` ⇒ the port is unfalsifiable there and MUST NOT be written.**
   ⭐ **The tool is language-agnostic and works on `.icn` unchanged** (verified s216 on
   `bench_icnagg_field_isolate.icn`): its symbol list is derived from the tree every run, so it needs no
   Icon-specific edit. ⭐ **It also discharges s204's ISOLATION ARM for free** — sibling symbols in an
   already-ported family show up with zero entries and are omitted, which is the isolation property
   stated directly rather than inferred from a rebuild.
   ⭐⭐⭐ **AMENDED s224 — TWO PROBE SHAPES THAT LOOK LIKE FALSIFICATION AND ARE NOT, AND THE MEASURED
   REASON THE "and again after" CLAUSE ABOVE IS LOAD-BEARING.** Both found on `rt_subscript_var`:
   **(1) A UNIFORM-OFFSET PROBE IS VACUOUS BY SYMMETRY on any symbol that both READS and WRITES the cell
   it names.** Shifting the computed element address by one — RTX-24's own recorded probe — moved the
   board by ZERO on the `DT_A` arm while the census showed 3/3 commits and `objdump` showed the probe live
   in the `.o`, because `A<i> := v` and `x := A<i>` shift TOGETHER and still agree. RTX-24's version only
   worked by accident of its workload (its list was built by a constructor that bypasses the arm). Use an
   ASYMMETRIC break — make two distinct inputs collide, or push an in-range access out of range. Applies
   to every `NAMETRAP`-minting symbol: `rt_assign_var`, `rt_field_var`, `rt_list_bang_var_at`.
   **(2) A KEY-FORMATTING ERROR IS SELF-CONCEALING UNDER OUTPUT DIFFERENTIAL TESTING.** Corrupting ONE
   byte of RTX-29's key discriminator left gate-ON output **100% identical to gate-OFF on every edge case
   AND both watermarks unmoved**, while the census read **400,008 entries / 400,008 bailed / 0 commits** —
   port entirely dead, program entirely correct. **A wrong key MISSES, the miss BAILS to C, and C
   recomputes the right answer**, so the failure degrades to a bail instead of to a wrong result.
   ⇒ **For ANY port whose commit path is gated on matching a value computed elsewhere — hash key,
   interned string, cache tag, memo lookup — output differential testing is STRUCTURALLY BLIND, and (j)
   MUST be re-run AFTER the port.** Corollary worth having: a nonzero commit count on such a port is
   itself a byte-for-byte correctness proof against the C-side producer, which no output test can
   distinguish from a bail. Full write-up: `FINDING-2026-07-30-CLAUDE-ICN-RTX-28-...-VACUOUS-BY-SYMMETRY.md` §2 and §8.
   ⚠ **PREFER A HARD PROBE (`ud2`/crash) OVER A VALUE PROBE when a silent result would be readable two
   ways** — a value probe conflates "the asm did not run" with "this value does not reach the output".
   A value probe that is NOT silent (it moves the board) remains unambiguous and sufficient.
1. **READ FIRST:** this file → `ARCH-LANGUAGES.md` (register contract + scan semantics) → the family's C
   source in full → **the ICON and JCON sources for every construct the family implements**
   (`refs/icon-master/src/runtime/fstranl.r` + `fscan.r` for scan; `refs/jcon-master/tran/irgen.icn`'s
   43 `ir_a_*` for port topology). ⛔ **NEVER install Java or run the JVM self-host path** (Lon, s121).
2. **PORT** behind the family gate; C renamed `c_*` in the same commit.
2b. ⭐⭐ **RUN THE FALSIFICATION BUILD AGAINST EVERY BATTERY — it is a COVERAGE instrument.** An unmoved
   battery is not a gate; citing it as asm evidence is a **FALSE CLAIM**. For ICON-RTX the shared runtime
   makes this sharper: SNOBOL4/Prolog batteries will often be legitimate no-regression evidence for the
   C-side edit **and simultaneously blind to the asm.**
3. **GATES:** Icon `test_icon_all_rungs.sh` at watermark, re-derived fresh **before** any edit ·
   SNOBOL4 + Prolog watermarks (no-regression) · kill-switch md5 byte-identity vs pristine.
4. **A/B** same-moment, interleaved, first round discarded (hugepage warmup, s201/s202), label every
   number `RTX_<FAM>=on/off, RT_OPT=-O0`. ⛔ **ISOLATION ARM REQUIRED** if the rung lands into an
   already-ported family — a family gate's error has **no known sign and no known bound** (s204).
5. **FINDING** doc + **LIVE CURSOR** move + handoff. `.s` regen ONLY if templates changed.

**Two-sided falsification is not optional:** break the asm body ⇒ gate ON must FAIL (proves the asm
executes); gate OFF must PASS (proves the switch switches). ⛔ **Break a RESULT, not a ROUTE** — breaking
the gate to fall through to C is vacuous, because its output equals the gate-off output (s187).
⚠ **A SILENT PROBE IS A QUESTION, NOT AN ANSWER** (s204): if corrupting the port moves the board by
zero, that names a real coverage gap in the batteries — escalate the probe, do not record a pass.

⚠ **NO `gdb`, `perf`, `valgrind`, `ltrace`, or `strace` IN THIS CONTAINER.** The monitor is dark (s158).
Differential + falsification testing is the working substitute; an LD_PRELOAD interposer is the step-0(d)
counting instrument.

---

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
**Companions:** `GOAL-ICON-RTX.md` (ladder) · `ARCH-LANGUAGES.md` (BB/register/scan) ·
`ARCH-SNOBOL4-RTX.md` (the contract this one inherits) · `GOAL-ICON-BB.md` (the ζ ladder it runs beside)

## 9. ⛔⭐⭐⭐⭐ THE ACTIVATION RECORD IS THE FRAME — ICON'S STACK ELEMENTS, REDESIGNED ON LON'S WORD (ceo, CEO-1542, 2026-10-07 18:0x CDT; replaces `g_icn_act`, deleted at SCRIP `ca33ff82a`; the row is `icon-the-activation-record-is-the-frame-…-ceo-1542`)

**Lon's words, verbatim.** To hq_icon, 16:2x CDT: *"Remove the g_icn_act global variable from the source and replace all it's references with a "* (char *) NULL" construct so it bombs nicely. We like bombs to show where we need code to be fixed."* · *"Not a prolem that ALL Icon programs broke. They will be fixed soon enough."* To the ceo, 17:4x–17:5x: *"I suspect you will need to help Icon re-design the replacement for the global which was removed recently."* · *"Some Icon had not got the memo that global variables holding a stack are not allowed, since we already have a stack."* · *"CEO, you are not seated as Fable 5.1 with xhigh effort so you can re-design Icon's stack elements."* The law is RULES.md § FACT RULE — NO GLOBAL HOLDS A STACK (CEO-1542).

### 9.1 What the global was (measured at `ca33ff82a^`)

`g_icn_act[rt_k_level] = { name, base, np, line, file, args }` (48 bytes), filled by every det procedure prologue after its level increment and by every generator prologue after its carve (`emit.cpp` `icn_act_record_inline`: a GOT load of the level, a cap compare and a `rt_icn_act_reserve` call, `rec = p + level*48`, then six stores: `lea` of a `.rodata` name, `rsp` after the carve, an immediate `np`, loads of `[g_line]` and `[g_file]`, `lea [rsp+aoff]`). Nothing was written at a resume. Its readers: `variable()` through `icn_variable_frame_cell` (the top record: name → `rt_proc_pname/lname/loff`, base + loff for a local, args + 16k for a parameter); `display()` (every level down from the top: name, base, np, args); `core_icn_traceback` (every level up from 1: name, np, the args imaged, and for levels above 1 `" from line %ld in %s"`, interleaved with `icn_tb_builtins_at`); the error voice's traceback guard and `rt_heap_out_of_memory` (only `ICN_ACT(1).name != NULL`, "is Icon running", the latter to choose 306/307 over 204); `rt_trace_resume_hook` (a search down the levels for the record whose name is the resumed generator's, to set `g_line` while printing "resumed"); `icn_act_restore_call_line` at every det γ and ω and every generator suspend and fail (the top record's line and file back into `g_line`/`g_file`).

### 9.2 The finding: every field was a copy — ZERO words are added to any frame

| field | what the record stored | where it already is |
|---|---|---|
| `name` | a `.rodata` string, per activation | a compile-time constant of the PROCEDURE: the frame map's `graph_name` (`gc_frame_map_t`, reached from the per-graph site-table header `{n, map*, ckt}`), or one static word beside it (9.4) |
| `np` | an immediate, per activation | a compile-time constant of the procedure: the registry entry the call jumps through, or one static word in the shape (9.4) |
| `base` | `rsp` after the carve | the frame base the § 13.3 chain computes (`RSP + depth` for a det frame, `rbp` for a generator header) |
| `args` | `lea [rsp+aoff]`, `aoff` static per regime | `base + args_off`: `frame_total` (det, = the map's `frame_bytes`), the carve (generator), 16 (root) — a constant of the shape |
| `line`, `file` | `[g_line]`, `[g_file]` loaded at the callee's entry = the caller's last `IR_LINE_MARK` | a compile-time constant of the CALL SITE, keyed by the γ/ω wire the frame already holds (9.5) — iconx's `findline(pf_ipc − 1)` over its static `ilines` table |

The global was a per-activation copy of four things the frame already holds and two static facts of the call site. The replacement adds no word to any Icon frame, no store to any prologue, and no runtime structure; it deletes the fill, the cap check, `rt_icn_act_reserve` and the record read at every return.

### 9.3 The stack elements, by regime — the layouts stand

- **Det procedure** (`emit.cpp:3807-3877`, the block protocol of `bcps_icn_block_arm`): the caller pushes the ω wire (L4) and the γ wire (L3), writes the level glue record (`bb_glue_act_record`, the SNOBOL4 twin — a second stack of its own, rowed to hq_zetas under CEO-1542's census), builds the argument block with `sub rsp,16n`, jumps through the registry; the callee does `sub rsp, kt` only, no `push rbp`, everything `rsp`-based: `A[i] = [base+kt+16i]`, `γ = [base+kt+16n]`, `ω = [base+kt+16n+8]`; it leaves by `add rsp, kt+16n` then `jmp [rsp]` / `jmp [rsp+8]` (`xa_flat.cpp:699-722, 806-826`). No rbp chain: its link to the caller is the γ wire, a static landing address at a static offset — exactly the § 13.3 `link_pc_off`.
- **Generator** (`emit.cpp:3786-3800`): the caller pushes three zero words, ω, γ, the block, and bumps the level; the callee carves `align16(kt)+72` and sets `rbp = base+kt`; the header is `[rbp]` the caller's rbp, `+8` γ, `+16` ω, `+24` the anchor (the caller's rsp above the entry words), `+32` the resume label, `+40` the resume rsp, `+48/+56` the generator's OWN line and file (`icn_gen_line_save` at suspend); `A[i] = [base+carve+16i]`. A suspend restores `rbp = [rbp]` and jumps γ with `rdx` = the frame, leaving the frame below the caller's continuing spine (§ 13.5 residue); a resume sets `rsp = [h+40]`, `rbp = h`, jumps `[h+32]`; a failure sets `rsp = [rbp+24]`, `rbp = [rbp]`, jumps ω.
- **Root/main**: args at `+16`. **Host-pinned** (`icn_host_pinned`): `rbp = base`, the caller's rbp at `[base+kt-8]`.
- The `DT_MAP` cell each frame stores at `[base+jcon_value_region]` goes with hq_collector's STEP B (§ 13.2); nothing here depends on it.

### 9.4 The static shape — compile time, one per procedure, never per activation

The three static facts a reader needs — the procedure's name, its `np`, its `args_off` — are facts of the SHAPE (§ 13.3: `{ map*, base_rule, link_rbp_off, link_pc_off, enclosing_shape* }`, hq_collector's record, being stated per regime in STEP B now). The lane FIRST MEASURES whether the existing words already give them: `graph_name` (is it the source name or the `FN__` label?), `frame_bytes` / `header_bytes` (do they equal `aoff` for det and generator?), and the registry entry's `np` by name. A fact that is missing becomes ONE static word in the shape record, stated to hq_collector in the same hour and carried by it (one seat edits the struct) — never a word in the frame, never a store in a prologue. A regime flag `PROC` beside `GC_FRAME_MAP_GEN_ANCHOR` says "this frame is a procedure activation": it is a FRAME-REGIME fact, not a language test.

### 9.5 The caller's line and file: a static fact of the landing

- **The table.** One code-map row per Icon call landing — `{ pc = L3, stno, line, file }` and the same for L4 — through the existing `emit_stno_mark` road (`sno_stno_rec_t`, `stno_map.h`, 24 bytes; written today only for `IR_STATEMENT*` / `IR_STMT_MARK`, so Icon has no rows), for every call regime that lands in emitted code: the det block arm, the generator arm, call-by-value (`bb_call_value`), APPLY, by-name and the C roads of `rt.c`. The line is the emitter's last `IR_LINE_MARK` under the node (compile-time state in `g_emit`, or an operand the lowerer pushes on the call node — the PEERS RULE; the lane's choice). The traceback's `" from line N in F"` for a frame is `code_map([base + link_pc_off])` — the floor search `scrip_stno_from_return_addrs` already does over return addresses.
- **The restore.** `xa_icn_act_restore_call_line` (the record read at every det γ/ω and every generator suspend/fail, 4 sites) is REPLACED by two stores in the CALLER at each landing: the landing's own line and file as immediates into `g_line`/`g_file` — the statement mark's own two stores (`bb_stmt_mark.cpp:38-50`), re-issued where control re-enters the caller. A generator's suspend and fail land on the same γ/ω and need nothing of their own; the resume hook's "resumed" line is the generator's own header word `[h+48]`/`[h+56]`, no search; the fail and return hooks restore nothing.
- **The end state (a follow-on row, NOT this landing — LARGE CHUNKS):** a row at every Icon site (the GC site table's CALL/LANDING/RES population, its 24-byte twin), after which `core_error_voice` reads Icon's line from the map as it reads SNOBOL4's `&STNO` today (`core.c:598-600` already prefers `from_map`), the per-statement `g_line` stores and these landing restores go, `&line` is an immediate at its site, and `icon-an-error-in-a-part-of-a-statement-on-a-later-source-line-…` and `icon-line-keyword-on-a-later-line-…` are cured by the same table at iconx's granularity (`findline(ipc)`).

### 9.6 The one reader: the § 13.4 chain walk with a visitor

`rt_frame_walk(pc, R, rbp, visit, ctx)` — hq_collector's walk (`gc_chain_resolve` today) given a visitor: the collector's visitor marks a frame; Icon's visitors read it. Entry facts are the three every poll entry states (the return PC into emitted code, R, rbp); from C (the error voice, `display()`, `variable()`) the C-ROAD unwind of § 13.4 by frame pointer (`-fno-omit-frame-pointer`, Makefile:47) to the first table hit. A det frame is crossed by static constants alone: `pc' = [base+kt+16n]` (γ), the caller's R at that landing is `base+kt+16n`, and the LANDING row's static depth gives the caller's base; a generator frame through `[rbp+8]` and its anchor `[rbp+24]`; a suspended generator below the live chain is not an activation (iconx's `pf_pfp` chain skips it likewise); a co-expression's segment ends at its body's first frame (§ 13.4 step 2, `park_rbp`). The Icon L3/L4 LANDING rows — the one gap measured at `ca33ff82a` (non-Icon arms have them, `bb_call_proc_staged.cpp:456, 625`) — are hq_collector's STEP B, cause one of its own divergence list; hq_icon does not add them twice. The visitors:
- **TRACEBACK** — every `PROC` frame top-down: name, the `np` args imaged at `base+args_off+16k`, `" from line N in F"` from 9.5 for every level but the outermost, interleaved with the builtin chain `g_icn_bi_top` (a chain of nodes ON the machine stack with one head cell: a link word, not a second stack).
- **DISPLAY** — each frame's parameters at `base+args_off` and locals at `base+loff` by `rt_proc_lname/loff` of the name; **VARIABLE** — the first `PROC` frame only.
- **THE GUARDS** — the error voice prints whatever traceback the walk yields; there is no "is Icon running" test. `rt_heap_out_of_memory`'s 306/307 against 204 is chosen the way the voice is already chosen for the program, never by a new language test in the runtime (A LANGUAGE DISCRIMINATOR IN THE RUNTIME IS A DEFECT CLASS).
- **TRACE** — the hooks take their facts as arguments, as `xa_icn_trace_tap(pname, kind, np, r11d)` already does; `rt_trace_resume_hook` reads `[h+48]`/`[h+56]`; `rt_trace_fail_hook` / `rt_trace_return_hook` no longer restore.
- **`&level`** — `rt_k_level` stays: a counter is one cell, not a stack. Counting frames in the walk instead, and retiring the counter, is a later row.

### 9.7 The roll-out (LARGE CHUNKS, CEO-1478..1484) and what it closes

Build 9.4–9.6 whole, every bomb deleted. SMALL: the det regime on the Icon `gc_witnesses` and the smoke (`test_smoke_icon.sh` and the iconx-anchored gates of the row), curing what it finds. MASSIVE: every regime — generators, call-by-value, APPLY, by-name, the C roads, co-expressions — and every consumer, in a few landings reaching the whole Icon population, inside hq_icon's lane; then Lon's ultracode. Per call this deletes the nine-store fill and the cap check at every prologue and the load-compare-store pair at every return (two immediate stores at the landing replace it). It closes the coo's bisect of `test_gate_icn_call_site_parity_at_proc_call_open.sh` to `5f060e20b` (the fill sat ahead of the first call); `test_gate_icn_generator_records_its_activation.sh` is re-cut to the chain and the apply gate's comment to this section. The remaining eleven forbidden second stacks of the census (GOAL-CEO.md CEO-1542) follow the same design, each in its own lane: the record is the frame, the static facts are the shape and the site, the reader is the walk.

### 9.8 AS LANDED (ceo, SCRIP e22bf956b landing 1 and 70dbd0bbb landing 2, 2026-10-07 18:5x–19:4x CDT; CEO-1545/1546)

- **Landing 1 (e22bf956b):** the record fills and the callee-side restore gone; `icn_landing_line_restore` (xa_icn_act_restore.cpp) stores the landing's own line and file at the Icon block arm's L3/L4, the value call's L3/L4 and, since landing 2, at both boxes' β (the resume site), from `g_emit.icn_line_cur`/`icn_file_cur` tracked at every `IR_LINE_MARK`.
- **Landing 2 (70dbd0bbb):** the maps carry `GC_FRAME_MAP_ICN_PROC` / `ICN_BLOCK` / `ICN_PINNED`; every Icon `IR_LINE_MARK` writes a code-map row at its pc (the first half of 9.5's end state — any Icon pc resolves to its statement); the L3/L4 landings are LANDING sites (hq_collector's shape: rsp mark before the wire pushes, `x86_rsp_land(16)`, the site at each label); `rt_icn_frames` (gc_heap.c) walks the live Icon activations innermost first over `gc_chain_resolve` — a det frame steps to its caller through the γ wire at `base+frame_bytes+16*np` (rbp through the pinned host's saved word), a generator through its header; `core_icn_traceback`, the five accessors (`variable()`, `display()`), the error voice's guard and `rt_heap_out_of_memory` read a VLA of frames per call; a level's from-line is the code map at its caller pc. **Two facts the design did not foresee:** (a) the C-road entry from an error raised inside a frameless rtx leaf (`RTX_CCALL`, `sub rsp,8; call`): the return address into emitted code lies among the leaf's first words, not at [fp+8]; the walk tests the return address for an FDE (`_Unwind_Find_FDE`, libgcc) and, when there is none, looks for a CALL-site pc among the leaf's first fourteen words — the interim until the leaves carry CFI (hq_runtime), when `_Unwind_Backtrace` replaces it -- **DONE at SCRIP `83f810283` (CEO-1548): every leaf carries CFI true at every pc (`test_gate_rtx_every_leaf_carries_cfi_true_at_every_pc.sh`), `gc_chain_entry_from_c` unwinds with `_Unwind_Backtrace` to the first return address `gc_site_find` knows, the probe and `gc_pc_is_frameless_leaf` are deleted**; (b) the resume trace prints the RESUMER's line (iconx), but the generator's res label restores the generator's own line before any box runs, and a returned generator passes the res label too: so the res label saves the resumer's `g_line` into the generator header's free pad word (+64, inside the carve) before the restore, and only a SUSPEND box's β hands the header to `rt_trace_resume_hook` — one frame word, written at every resume, read by the trace alone.
- **Measured:** the row's eleven arms green in both modes; preflight 71 green with the area smoke (104/104, tracing.icn equal to its ref); the 41 Icon gc_witnesses under `SCRIP_GC_STRESS=1 SCRIP_GC_CHAIN_CHECK=2` pass in both modes; the five other smokes green. `g_icn_act` is the first stack GONE on the countdown (17 to eradicate, GONE 1, LIVE 16).

---

## 10. ⛔⭐⭐⭐⭐ THE SCANNING ENVIRONMENT IS THREE REGISTERS — r13 Σ, r14 δ, r15 Δ ARE &subject AND &pos, THEIR ONLY HOME; ALL OF SCAN IS EMITTED (the cfo, 2026-10-24 22:5x–23:1x CDT; the row `icon-string-scanning-is-pure-asm-as-snobol4s-match-r13-r14-r15-are-subject-and-pos-their-only-home-ceo-1969`, CEO-1969/1970; Lon 2026-10-24 21:4x–21:5x, in-chat to the ceo, verbatim: *"I'm thinking that ALL of SCAN should be 100% pure ASM. Check. I say this since it same as SNOBOL4, and the MATCH is 100% pure asm. Or rather it should be and could be."* · *"I directed R13, R14, and R15 to be &subject and &pos. Check. Is it true?"*; THIS SECTION IS THE PLACEMENT AUTHORITY FOR &subject AND &pos; hq_icon and hq_runtime build it, CEO-1970)

### 10.1 MEASURED on origin SCRIP 0d3a92f14 (2026-10-24 22:4x CDT): one value, two homes, and the C that carries the second

**THE REGISTERS ARE TRUE INSIDE A BOX AND FALSE AT EVERY BOUNDARY.** Inside the nine scan boxes (`bb_scan_any bal find many match move pos tab upto`) and the environment box `bb_gen_scan`, r13 is Σ (the subject's first byte), r14 is δ (the 0-based cursor; `&pos` = δ+1), r15 is Δ (the length). `bb_keyword_icon` already reads `&pos` as `lea r14+1` and `&subject` as `{DT_S, r15d, r13}` — but ONLY when the emitter's per-node flag `g_scan_regs_live` (emit.cpp:672, set at emit.cpp:2023 from `nd->in_scan`) is on; off it calls `rt_keyword_subject` in C. The SECOND HOME is `g_runtime.abi.{scan_subj, scan_subj_len, scan_subj_ptr, scan_pos, scan_depth}` (g_runtime_abi.h:87-91) plus `g_scan_empty`, plus a `ScanState` record `rt_scan_state_capture` allocates with `ct_zalloc` AT RUN TIME on every co-expression switch (gen_runtime.c:25-45, rt_coexpr.c:126/143 — the compile-time arena in the runtime, the forbidden class). Sites that read or write it: gen_runtime.c 45, by_name_dispatch.c 34 (`bn_icn_tab/move/any/many/upto/pos`, the `BID_ICN_SCAN_PUSH/POP` road and its `scan_pos > 0` gates at 22415-22462), core.c 6 (the `&subject`/`&pos` arms of `rt_keyword_var` and its assign twin, 3722-3817), keywords.c 3, rt_coexpr.c 2 (`pkg->r14`, `sigma_live`), polyglot.c 4 (the init), g_runtime.c 2, gc_heap.c 1 (the shield alias, 3697), emit.cpp 3, x86_asm.h 6 helpers (`x86_scan_sync_out`, `x86_scan_sync_in_rr`, `x86_scan_sync_out_force`, `x86_scan_sync_in_rr_force`, `x86_scan_switch_reload_force`, `x86_scan_sigma_reload`).

**THE BOUNDARY PROTOCOL IS THE DEFECT.** Thirty emitted sync sites in eight templates — `bb_call_proc_staged` 12, `bb_define` 8, `bb_suspend` 2, `bb_call_fn` 5, `bb_call_value` 4, `bb_activate` 2, `bb_coret` 2, `bb_rev_assign_global` 1 — spill `r14` to `scan_pos` BEFORE every call, suspend, return and co-expression switch (`x86_scan_sync_out`: `mov rdi, r14; call rt_scan_sync_out`) and AFTER it reload `r14` from `scan_pos - 1` and `r13` from `scan_subj` (`x86_scan_sync_in_rr`: two calls, `rt_scan_sync_in` and `rt_scan_live_subj`; r15 is NOT reloaded — it rides on SysV preservation). The global is the inter-procedure CARRIER and the register is a per-box working copy: one value, two homes, and a copy at every boundary in both directions. `bb_gen_scan` itself calls C six times per scan (`rt_scan_enter` to coerce the subject and set the global, `rt_scan_leave` to restore it, `rt_scan_live_subj`/`rt_scan_sync_in`/`rt_scan_reenter_live`/`rt_scan_sync_out` around a suspension of the body) although its banks already hold every word the C stores: the outer (Σ, δ, Δ) in the ENTER node's own grant (a DT_S cell at `FRQ(off)`/+8, δ at +16, Δ at +24) and a suspended body's inner environment in the LEAVE node's grant (a DT_S cell at +16/+24, δ at +32; CTO-154's tagging).

**THE COUNT (the row's DONE-WHEN instrument, run on the 17 Icon benchmarks and the keyword witness `kw.icn`, mode 4):** 252 emitted calls to the nine scan functions and `rt_keyword_var` over the 8 programs that scan — by function `rt_scan_live_subj` 64, `rt_scan_leave` 52, `rt_scan_sync_out` 49, `rt_scan_sync_in` 39, `rt_scan_enter` 23, `rt_scan_reenter_live` 17, `rt_scan_needle` 2, `rt_keyword_var` 2, `rt_icn_cset_member_n` 2, `rt_icn_cset_bits_d` 2; by program rsg 91, geddump 41, concord 33, tgrlink 32, ipxref 20, queens 14, deal 14, kw 7 (the ceo's 222 at e59571650 plus the cset road and the witness). The other C the boxes call — `core_icn_argtype_check` 6, `core_icn_to_int_check` 3, `core_icn_int_operand_ok` 3, `rt_substr` 3, `memcmp` 3 — is coercion, error voice and a substring, not the environment; § 10.5 says which of it stays as a slow path.

**THE FORMS THE BOXES REFUSE** (each an `x86_bomb` the lowerer steers around to the by-name C road): a non-literal cset or needle (`bb_scan_any/many/upto/bal/match/find`: "needs literal cset arg"), the explicit-subject forms `any(c, s, i, j)` and their siblings (lowered as `IR_CALL` by name, graded by `bn_icn_*` on the global), a needle longer than 32 bytes (`bb_scan_find`), a bracketed or empty `bal` cset. Every one is a form of the same box with a run-time branch, § 10.5.

**THE SEMANTICS, MEASURED AGAINST iconx (`/home/resources/icon-master/bin`; SCRIP agrees on all three today, in both homes):** (a) a procedure called inside a scan reads and MOVES the caller's environment — `"ab cd" ? { p(); write(&pos) }` with `p` doing `tab(upto(' ')); move(1)` prints 4; (b) a generator's own `? ` restores the outer environment at its suspend and re-enters its own at the resume — `every q()` with `q` suspending from inside `"x" ? {...}` shows `q inside pos=2`, then `main sees pos=3 subj=hello`, then `q resumed pos=3 subj=hello` (q's scan had completed at the resume and restored the outer); (c) co-expressions SHARE ONE ENVIRONMENT, dynamically: a co-expression activated inside a scan sees the activator's `&subject`/`&pos` (`coexpr sees subject=[hello] pos=3`), a `&pos := 4` inside the co-expression is the activator's `&pos` after `@` (`after coexpr set pos=4`), and a co-expression that transfers OUT from inside its own scan LEAKS that scan's environment to the activator (`main after @d pos=2 subj=zzz`), restored only when the co-expression's scan exits (`main after second @d pos=4 subj=abcdef`); (d) `&subject := 42` converts to the string `"42"`, sets `&pos` to 1, and PERSISTS outside any scan (`outside any scan subject=[42] pos=1`): the ROOT environment is mutable state of the program; (e) `&pos := 7` on `"abc"` FAILS and leaves `&pos` (1); `&pos := -1` is 3 and `&pos := 0` is 4 (a non-positive position counts from the end, `Δ + 1 + i`); (f) at program start the environment is `""` and 1.

### 10.2 THE RULING — ONE HOME

**R1 — THE ENVIRONMENT IS (r13, r14, r15) AT EVERY INSTRUCTION OF AN ICON GRAPH.** `&subject` IS the descriptor `{DT_S, r15d, r13}` and `&pos` IS `r14 + 1`, both DERIVED at the read, never stored: there is no `scan_subj`, no `scan_pos`, no `scan_depth`, no `ScanState`, no `g_scan_regs_live`, no per-node `in_scan` read by the emitter. The only MEMORY the environment ever occupies is the two BANKS of a live `s ? e` — the outer environment saved at ENTER and the inner environment of a body suspended out of — and those are the ENTER and LEAVE nodes' OWN CELLS, placed by the planner's PLACEMENT RECORD (ARCH-THREE-ZETAS-EMISSION.md § 6.2: `home[]`/`zeta[]` of those two nodes; the cell-shape table's `IR_SCAN_ENTER 0 home_state` row — ζ-ACT when the body can suspend across a generator callee, Lon's TEST 1 — and `IR_SCAN 48 icn_home`), nothing else: a side table, a global, a thread-local or a C record is a second home and is refused in review.

**R2 — THE REGISTERS ARE LIVE-THROUGH ACROSS EVERY ICON-TO-ICON TRANSFER.** An Icon procedure call delivers the environment to the callee IN the registers and the callee hands it back IN the registers at return, suspend and fail (10.1 (a) and (b) are this rule); a generator resumed at β receives the resumer's CURRENT environment in the registers (it may have moved since the suspend). r13, r14 and r15 are therefore NOT callee-saved for the emitted Icon convention — no prologue saves them, no epilogue restores them — and every one of the 30 sync sites is deleted, with the six `x86_scan_*` helpers. For a C call they are callee-saved by SysV, which is exactly right once no C function reads or writes the environment: the C cannot change it, and the registers come back as they went in. (The C roads that today REACH an emitted Icon procedure through a C frame — `rt_call_arr` by name, APPLY — are the one place SysV would undo a callee's `tab`: § 10.6.)

**R3 — THE CONSTRUCT `s ? e` IS THREE MOVES EACH WAY.** ENTER: evaluate `s`; the DT_S fast path is `mov r13, [s+8]; mov r15d, [s+4]; xor r14, r14` after the bank; an integer, real or cset subject takes the string-coercion body from the emitted site as a slow path (`descr_to_str_fracdigit`, the cto's leaf rule: a C body called from the site is not a scan function and does not read the environment); a non-convertible subject is error 103 through `core_icn_argtype_check` as today. The BANK before the load is `mov [bank+8], r13; mov [bank+16], r14; mov [bank+24], r15` with the cell's tag and length written as the DT_S the collector visits (today's `bb_gen_scan` lines 33-37 unchanged). LEAVE (γ and ω alike): three loads from the bank. SUSPEND OUT OF THE BODY (`leave_succ` with a resumable body): bank the INNER (r13, r14, r15) in the LEAVE node's cell (today's +16/+24/+32), then load the outer from the ENTER bank — three stores, three loads. RESUME (β): the environment arriving in the registers IS the new outer (R2) — bank it in the ENTER cell (three stores; today's `rt_scan_sync_in` + `mov FRQ(off+16), rax` is this one word), then reload the inner from the LEAVE cell (three loads; today's `rt_scan_reenter_live` + `rt_scan_sync_out`). `scan_depth` has no reader left (its three were `rt_scan_active`, the by-name gates and `sigma_live`, all deleted) and goes.

**R4 — THE KEYWORDS ARE EMITTED, UNCONDITIONALLY.** `&pos` read: `mov rax, r14; add rax, 1` → `{DT_I, rax}` (the `bb_keyword_icon` arm that exists, with its `g_scan_regs_live` test deleted: outside any scan r14 is 0 and r13 is `""`, so it reads 1 and `""` as iconx does, 10.1 (f)). `&subject` read: `{DT_S, r15d, r13}` likewise unconditional; the `rt_keyword_subject`/`rt_keyword_pos` arms and the `KI_VARFORM` call to `rt_keyword_var` for these two names are deleted (the var form IS the assign box). `&pos := e` (`bb_keyword_assign`, the arm at line 29, its `scan_pos` store deleted): coerce `e` to integer (DT_I fast path, the integer-coercion body as the slow path); `if (e <= 0) e += r15 + 1`; `if (e < 1 || e > r15 + 1) → ω` (10.1 (e)); `lea r14, [e - 1]`; result `{DT_I, e}`. `&subject := e` (the arm at line 44, its global store and `rt_heap_alloc_c` copy deleted — an Icon string is immutable, the descriptor's bytes ARE the subject): coerce to string as R3's ENTER does, `mov r13, ptr; mov r15, len; xor r14, r14`; result the string; outside any scan this writes the ROOT environment, which persists (10.1 (d)). `bb_rev_swap` already reads and writes r14 directly (lines 74-94): unchanged.

**R5 — EVERY SCAN BUILTIN IS ONE BOX WITH EVERY FORM, AND ITS LEAVES ARE THE MATCH PLANE'S.** (i) A non-literal cset or needle: the box takes the DESCR operand and branches on its tag at run time — a cset VALUE carries its 256-bit table (the bitmap `kw_cset_bits` computes today becomes a field of the cset block, built once when the cset is made, never per call), so membership is `movzx esi, byte [r13+rcx]; bt [bits], esi` inline as `bb_scan_upto` lines 47-50 already emit for the literal case; a STRING used as a set is `rt_sg_member`, and a cset scan over the subject is `rt_sg_scan_member`/`rt_sg_scan_nonmember` (`src/runtime/rt/rt_sg_scan.S`: edi the position, rsi the set bytes, edx their length, r13/r15 the subject, eax the answer — the leaves SNOBOL4's ANY/NOTANY/SPAN/BREAK run on, shared, ARCH-ICON-RTX § 0 consequence 1), so `rt_icn_cset_bits_d` and `rt_icn_cset_member_n` have no caller and go (the latter from `src/parsers/icon/icon_runtime.c`, a runtime function in a parser directory). (ii) `rt_scan_needle` (coerce the needle to `{ptr, len}`): DT_S fast path is two loads; the integer/real slow path is the string-coercion body from the site; a `find` needle longer than 32 bytes is the same `memcmp` loop with a run-time length — the 32 cap and its bomb go. (iii) The explicit-subject forms `f(c, s, i, j)` (2-4 arguments) are the SAME box with a prologue and epilogue: bank (r13, r14, r15) in the box's own cell, load Σ/Δ from `s` and δ from `i` (the `i..j` window as iconx `fstranl.r` bounds it: a position outside `1..Δ+1` after the non-positive conversion FAILS), run the one-argument body, restore the three — the environment being the registers is what makes the 2-4-argument forms a prologue rather than a second implementation; the `bn_icn_*` by-name road and its `scan_pos > 0` gates are deleted with them. (iv) `tab`/`move`'s result string: Icon strings are immutable and `{DT_S, n, r13 + a}` SHARES the subject's bytes — the builder reads `rt_substr`'s body (gen_runtime.c:21 declares it) and replaces a share with three instructions, or a copy with the asm string allocator leaf `rt_str_alloc` already on Icon's hot list (§ 0): in neither case a C scan function. (v) WHAT STAYS AS C, ON THE SLOW PATH ONLY: `core_icn_argtype_check`, `core_icn_to_int_check`, `core_icn_int_operand_ok` and the coercion bodies — the error voice and the conversions, called from the emitted site when the DESCR tag is not the fast one (`cmp dword [slot], DT_I` decides inline). They read no environment word, so a program that scans integers and literal csets emits zero C calls on its scan road.

**R6 — THE COLLECTOR SEES THE SUBJECT PAIR BY DECLARATION, NOT BY ALIAS.** Σ is a heap pointer and the collector moves strings (ARCH-GC § 7, § 13; CTO-154 is the vacated-ground witness). Inside the scan boxes every poll is already `x86_rt_gc_poll_rec_sigma`: `{DT_S, r15d, r13}` spilled as a described cell on the stack for the walker and r13 reloaded after (x86_asm.h:3044-3064); the ENTER/LEAVE banks are DT_S cells the frame map visits. What goes is the ALIAS: the general poll's shield (`x86_rt_gc_poll_res`, gc_heap.c:3695-3698) visits the spilled r13 word only when it equals the SNOBOL4 global `Σ` or `g_runtime.abi.scan_subj` — and the 64 `rt_scan_live_subj` calls exist to re-read the global after such a poll. THE RULE: r13 is NOT a universal register (Prolog's packet header rides in r13, `bb_call_proc_staged.cpp:703-826`, `xa_flat.cpp:292-373`; Pascal's display levels in r13/r14/r15, `xa_flat.cpp:239-284`), so the collector may visit it only where the TREE says what it holds (RULES.md § the collector guesses nothing, clause 2: a register is excluded from or admitted to a root census only by a declaration in the tree). The declaration is a REGISTERED GRAPH FACT, `scan_regs` (ARCH-IR-CARRIES-EVERY-LANGUAGE-VARIANCE.md § 2's registry; the Icon lowerer sets it on EVERY Icon graph, because in Icon the pair is live at every instruction — the root `""` or a subject — and a callee not lexically inside any `?` still holds the caller's, 10.1 (a)); its readers are the poll emitter (in a `scan_regs` graph every poll spills the pair as `rec_sigma` does — three stores, one reload, no compare against any global), the call templates (R2: no save or restore of r13-r15 across an Icon-to-Icon transfer) and the co-expression switch (R7). `nd->in_scan` (IR.h:142) loses its last emitter reader (emit.cpp:2023) and is retired from the IR; gc_heap.c:3697's `scan_subj` alias goes with the global. THE POLL SHAPE, for hq_collector's chain walk (its overlap note of 2026-10-24 22:5x): at every poll of a `scan_regs` graph the pair is spilled as ONE DESCR cell `{DT_S, r15d, r13}` at the poll floor and handed to the poll entry as a described cell the walker sweeps and relocates — `x86_rt_gc_poll_rec_sigma`'s shape, x86_asm.h:3044-3064 — and r13 is reloaded from that cell after; r14 is an integer and needs no visit; the two banks are DT_S cells of the ENTER and LEAVE nodes' own grants, visited through the frame map as today. The three scan-subject gates (`test_gate_gc_scan_subject_saves_are_rooted`, `test_gate_gc_the_scan_enter_poll_never_roots_an_unestablished_subject_base`, `test_gate_gc_the_scan_subject_base_is_reloaded_after_a_call_inside_a_scan`) are run standalone on the builder's tree before each push, and the bare-poll witness table is RE-KEYED AS THE LAST STEP of every landing that moves or deletes a poll in `bb_scan_any.cpp` (lines 69, 91), `bb_scan_bal.cpp` (75, 123), `bb_keyword_assign.cpp` (38, 54) or `bb_scan_match.cpp` (37): from SCRIP, `python3 ../harness/scripts/util_gc_safe_point_contract.py` over the gc_witnesses with `--write-bare-poll-table` (about 70 s); a new bare poll the new asm emits is named as an arrival with a zero-collection witness (`hb_icn_scan_any_and_bal_with_a_cset` and `hb_icn_assign_the_scan_position_and_subject` are the two small programs that print oracle-cut refs); the ceiling of `test_gate_gc_every_credited_bare_poll_site_has_a_zero_collection_witness` (55) may fall by deleted unwitnessed sites and never rises without a named arrival.

**R7 — A CO-EXPRESSION SWITCH CARRIES THE THREE WORDS, AS iconx SHARES THEM.** 10.1 (c) is iconx's law: one environment, shared dynamically across co-expressions, leaking out of a mid-scan transfer and restored by that scan's exit. A co-expression is a thread with its own registers, so the switch TRANSFERS the environment: the activation record `scrip_coexpr_entry_pkg_t` (rt_coexpr.c:22) carries (r13, r14, r15) as three words — today it carries `r14` and a comment saying the subject is read from the rooted global — and `scrip_coexpr_activate`/`scrip_coret`/`cofail` hand the activator's three registers to the activated thread and the activated's three back to the activator through the same record (`bb_activate`/`bb_coret`: three stores before the call, three loads after, replacing `x86_scan_sync_out_force` + `x86_scan_switch_reload_force`). `ScanState`, `rt_scan_state_capture/apply/reset`, `inherit_scan`, `sigma_live` and the `ct_zalloc` in the runtime go. The record is a stack word of the activation (THE LIFETIME RULE), never a global.

**R8 — THE ROOT ENVIRONMENT.** Program entry (`xa_flat`'s main prologue, mode 3 and mode 4 alike) sets `r13 = &""` (the empty string's own byte, rodata), `r14 = 0`, `r15 = 0` — iconx's 10.1 (f) — and nothing else initialises it (polyglot.c:29-32's four stores go). `&subject := e` outside any scan overwrites the root (10.1 (d)) and it stays until the program ends.

### 10.3 WHAT IS DELETED, THE CENSUS THAT READS 0

The nine functions the row names (`rt_scan_enter`, `rt_scan_leave`, `rt_scan_sync_in`, `rt_scan_sync_out`, `rt_scan_live_subj`, `rt_scan_reenter_live`, `rt_scan_needle`, `rt_icn_cset_bits_d`, `rt_icn_cset_member_n`) and with them `rt_scan_live_regs`, `rt_scan_subj_len`/`_set`, `rt_scan_active`, `rt_scan_state_capture/apply/reset`, `ScanState`, `rt_keyword_subject`, `rt_keyword_pos`, `rt_keyword_subject_set(_strict)`, the `&subject`/`&pos` arms of `rt_keyword_var` and its assign twin (core.c), the `bn_icn_*` scan builtins and the `BID_ICN_SCAN_PUSH/POP` road (by_name_dispatch.c, 34 sites), the five `g_runtime.abi.scan_*` members (with `g_runtime_abi_check.inc` regenerated by `util_g_runtime_abi_offsets.py`), `g_scan_empty`, `g_scan_regs_live` and the `in_scan` node field, the six `x86_scan_*` helpers and their 30 sites, `bb_gen_scan`'s six calls, the shield alias (gc_heap.c:3697), polyglot.c's init, rt_coexpr.c's `pkg->r14`/`inherit_scan`/`sigma_live`, and `src/parsers/icon/icon_runtime.c`'s `rt_icn_cset_member_n`. The row's DONE-WHEN is the count: no `call` to any of the nine over `corpus/benchmarks/icon/*.icn` and the keyword witness, `rt_keyword_var` 0 on the witness, `kw.icn` printing `3 def`, the Icon smoke green.

### 10.4 WHO BUILDS, IN WHAT ORDER (LARGE CHUNKS, CEO-1478..1484; the seating of CEO-1970)

hq_icon builds the emitted side (R2-R5, R7's template half, R8: `bb_gen_scan`, the nine scan boxes, `bb_keyword_icon`/`bb_keyword_assign`, the eight boundary templates, `xa_flat`, the lowerer's `scan_regs` fact and the by-name steering removed); hq_runtime builds the runtime side (R5's leaves and the cset block's bitmap field, R6's poll emission and the collector's alias, R7's switch record, § 10.3's deletions). The cfo reviews each landing against this section and runs its witnesses (the three probe programs of 10.1, `kw.icn`, the seven scanning benchmarks) in both modes against iconx before the push is accepted; the builders' per-landing verification is CEO-1928's (the program alone, the Icon smoke, and — `src/templates`, `src/emitter` and the poll being shared code — the eight smokes and the cores of every language at 100 percent). THE SMALL ROLL-OUT: R1-R4 and R8 — the environment itself: `bb_gen_scan` on its banks, the keyword boxes unconditional, the 30 sync sites and `g_scan_regs_live` deleted, the root set at entry — on the Icon smoke and the eight programs of 10.1, the nine C functions left in place UNREFERENCED (`rt_scan_live_subj` 64 → 0 is the first reading). THE MASSIVE ROLL-OUT: R5 every form of the nine boxes, R6's poll and graph fact, R7's switch record, the by-name road and § 10.3's deletions, in a few landings reaching the whole Icon population inside the Icon lane; then Lon runs ultracode. The three probe programs join the Icon rungs with iconx-cut refs in the first landing (CEO-1696: every witness has the oracle's answer; the builder files `s4e_test_request.sh icn-rungs <entry>` for the coo).

### 10.5 THE ONE SEQUENCING FACT WITH THE cto's ROWS

A procedure reached THROUGH A C FRAME — `rt_call_arr` by name (the cto's row `icon-a-builtin-is-called-by-name-through-c-rt-call-arr-bl-strict-322-sites-the-dispatch-becomes-a-box-ceo-1969`), APPLY, the error-voice re-entry — cannot hand its environment back in registers: SysV restores r13-r15 at the C frame's exit, which is why `bb_define` and `bb_suspend` sync through the global today. Until that row deletes the C frame, that one road carries the three words EXPLICITLY in the C activation's own record (`ScanSubjRegs` in and out as arguments and result, stack words of that C frame — THE LIFETIME RULE), never through a global; once the dispatch is a box, the road is R2 like every other. The two designs land in either order; this section does not wait on that one.

### 10.6 WHAT THIS SECTION DOES NOT RULE

SNOBOL4's match plane has the same class of second home — `bb_match_begin` loads Σ/Σlen from the `Σ` GLOBAL at MATCH_BEGIN (lines 40-52) although the pattern-match statement's subject is that statement's own value cell, and gc_heap.c:3700 visits `&Σ` as a root — but SNOBOL4 has no keyword that reads the subject, the global's lifetime is one statement, and the row is hq_snobol4's, named here so the two cures read the same rule: the subject's home before the match is the statement's cell, and inside it the registers. `&level`, `&trace`, the traceback and `display()` read nothing of the environment and are § 9's.

### 10.7 THE BUILDER'S NOTES — the small roll-out (SCRIP 2f4c84124) and road A (SCRIP e2d6a1d85) (hq_icon, 2026-10-25; the cfo's design notes (a)-(d) of its verdict on d5fec4590, written here at its ask, with the measurements beside them)

**WHAT LANDED, AND THE ROAD RULED BETWEEN.** The small roll-out is R1-R4, R6's poll shape and R8, plus ROAD B: the C roads that stay until R5/R7 (the `bn_icn_*` by-name builtins, the co-expression switch) keep one sync call per side, and that call carries all three words by argument — `rt_scan_sync_out(subject, length, cursor)` — because a cursor alone cannot carry a subject and no emitted code feeds `g_runtime.abi.scan_subj` once R3 lands (the cfo's ruling, 10.5's rule applied one landing early). ROAD A is the landing after it: the lowerer emits the nine builtins as their boxes in EVERY Icon graph, not only inside a lexical `?` (10.1 (a) under R1) — measured, a procedure scanning its caller's subject with no `?` of its own lowered `move`/`tab`/`upto` as by-name C calls, so `"abcd" ? { p(); write(&pos) }` read 1 for iconx's 2 once R3 removed the global's writer. The retag that makes a call a box is guarded against a program's own procedure, a reassigned builtin, a local or a global of the same name: the in-scan retag had turned a program's own `tab` into `SCAN_TAB`, now cured (iconx calls the program's `tab`). One emitter predicate followed the retag: a resumed `suspend` chose its operand's β only for a generator kind, `IR_CALL` and `IR_CALL_PROC_STAGED`, so `procedure m(n); suspend move(n); end` re-entered the `SCAN_MOVE` box at α and moved again (`every m(2)` printed 3 5 7 7 for iconx's 3 1; `ladder__rung05_scan_a_suspended_tab_restores_pos_on_backtrack` hung) -- `SCAN_TAB` and `SCAN_MOVE` now take β there too (emit.cpp, `g_suspend_dobody_beta`), found by the feature reps on the first cut.

**(a) A DT_S OF LENGTH 0 TAKES THE COERCION LEAF.** `x86_icn_subject_set` (ENTER, `&subject :=`, `&subject <-`) reads the tag and the length from the descriptor's first qword and takes the three-move fast path only for a DT_S with a non-zero length, because a zero length is how a length-less legacy string is spelled (rt_scan_enter measured it with `strlen`); the empty subject therefore pays one `rt_icn_subject_coerce` call per scan — a known cost, correct and measured (the cfo's p4: an empty literal and an empty variable subject read pos 1, `move(0)` and `tab(0)` succeed). The planner key of an operand covers its two DESCR qwords and never `+4`: a dword read at `sa + 4` aborted with zls_key_unbacked on all seven scanning kernels, so the tag and length come from ONE qword load (`eax`, `rax >> 32`) and a result descriptor is written as ONE composed qword.

**(b) TWO ROOT SUBJECTS, ONE MEANING — NO READER COMPARES r13 TO A SENTINEL.** Mode 4's main sets `r13 = .Lscan_nil` before `jmp main_α` (scrip.c, already so before this section); mode 3's Icon root enters through `rt_outer_call_icn_root` → `rt_outer_call_root`, `r13 = .Lrt_icn_root_nil` (its own rodata byte), while `rt_outer_call` still zeroes r13 for the languages whose templates test it (`bb_match_begin`, `bb_pl_cell.h`, `bb_call_proc_staged`'s Prolog arm). Both read the empty string at `r15 = 0`; therefore no Icon reader may compare r13 to a sentinel address to ask "is a scan active" — the environment is a value, never a mode.

**(c) THE POLL CARVES 64 BYTES UNDER rsp, BALANCED INSIDE THE POLL.** `x86_rt_gc_poll_scan_regs` (under the `scan_regs` graph fact) spills `{DT_S, r15d, r13}` at `[rsp]` and saves `rax rcx rdx rsi rdi` at `+16..+48` — the registers `rt_gc_poll_slow` preserves and RTCC does not — calls `rt_gc_point_arr_c(&cell, 1, NULL, rsp + 64)`, reloads r13 and the five, and gives the 64 back before the next instruction: the planner's declared depth is untouched and the ZSM reading of the probes is identical before and after (the cfo, on p3 and p4). The result poll carries the pair beside `rax:rdx` (two cells, 32 bytes). The bare-poll contract reads that body as its site's call (harness 446c298); `SCRIP_GC_STRESS=1` on p3-p5 and `=50` on concord and rsg read 10/10.

**(d) ONE PER-SHAPE PREDICATE FEWER.** The `in_scan` node field and the `g_scan_regs_live` emitter global are deleted with the 22 Icon-to-Icon sync sites; the templates ask one registered graph fact (`scan_regs`) instead of a per-node flag the emitter flipped as it walked — the programme's direction (CEO-1895: placement and shape decided once, read, never re-derived per node).

**THE REMAINDER, for the massive roll-out (hq_runtime's runtime side, R5/R7/10.5):** census over `corpus/benchmarks/icon` + kw.icn, mode 4 — `rt_scan_live_subj`, `rt_scan_enter`, `rt_scan_leave`, `rt_scan_reenter_live` 0, `rt_keyword_var` 0 on kw; `rt_scan_sync_out` 26 and `rt_scan_sync_in` 18 at the C roads; `rt_scan_needle` 2, `rt_icn_cset_member_n` 2, `rt_icn_cset_bits_d` 2 — 50 of the 252 of 10.1.

## 11. DESIGN-PLAN icon-scanning-asm -- THE SIX LANDINGS THAT FINISH SECTION 10 (the cto, 2026-10-28 12:0x-12:5x CDT; CEO-1996/1997/1998; the row `design-icon-string-scanning-in-pure-asm-ceo-1998`; hq_icon executes steps 1, 2, 5 and 6, hq_runtime steps 3 and 4, the cfo reviews each landing against sections 10 and 11 and builds a step an HQ cannot)

DESIGN-PLAN: icon-scanning-asm

Section 10 is the design and stands; its small roll-out and road A landed (10.7). What is left is measured, not argued, and this section cuts it into six landings each with a witness (`corpus/tests/icon/scanning_asm`, refs from Arizona Icon) and a probe (`harness/scripts/test_design_icon_scanning_asm_steps.sh --step N`: RED until the step lands, GREEN after; `--list` runs nothing). The problem the ceo named (CEO-1998): the cfo's claim stood 71 hours with no landing because the remainder was one row; it is now six, two of them hq_runtime's, in an order the depends column states.

### 11.1 THE MEASUREMENT (SCRIP 40d6d5c50, mode 4 over the 17 Icon benchmarks and the keyword witness is00_kw, 2026-10-28 11:xx CDT)

139 emitted calls into the scanning C, by function: `rt_substr` 85 (the result copy at `bb_scan_tab.cpp:49`, `bb_scan_move.cpp:46`, `bb_scan_alternate.cpp:34`), `rt_scan_sync_out` 28 and `rt_scan_sync_in` 18 (the C roads: `bb_call_fn.cpp` 7 sites, `op_call_scansync` and `op_call_curmov`; `bb_call_value.cpp` 2, `cv_sync_out`/`cv_sync_in`; `bb_activate.cpp:18`; `bb_coret.cpp:17`; `bb_keyword_icon.cpp:33`, `KI_SCANKW`; the helpers `x86_scan_sync_out_force` and `sync_in_rr_force` at `x86_asm.h` 2358-2381), `rt_scan_needle` 2, `rt_icn_cset_member_n` 2, `rt_icn_cset_bits_d` 2, `rt_keyword_var` 2 (is00_kw's `&pos` as a variable). By program: rsg 40, geddump 34, tgrlink 20, ipxref 13, concord 13, queens 7, deal 7, is00_kw 5; the ten non-scanning benchmarks 0. The nine functions of 10.3 alone: 52 (the cfo's 10.7 reading of 50, plus two needle calls). The mirror `g_runtime.abi.scan_*` has 99 reader lines in `src` (the step-6 probe): `gen_runtime.c` 44, `by_name_dispatch.c` 34 (`bn_icn_any` 20320, `bn_icn_tab` 20347, `bn_icn_move` 20364, `BID_ICN_SCAN_PUSH`/`POP` 21760 and 23196-23218), `core.c` 6 (`rt_keyword_var`'s `&subject`/`&pos` read and assign arms, 3730-3822), `polyglot.c` 4 (the root reset at 29-32), `rt_coexpr.c` 2 (133 the r14 package word from `scan_pos`, 398 `sigma_live` from `scan_depth`), `gc_heap.c` 1 (3712, the shield). The co-expression record `scrip_coexpr_entry_pkg_t` carries r14 alone at offset 16 and its static assert says why: the trampoline loads r13/r15 from the rooted global. The collector's DT_S visitor (`gc_visit_one`, `gc_heap.c` 1464-1472) finds the block of a string pointer by `gc_blk_of`, counts an interior pointer under RT_DIAG and registers the slot through `gc_slot_reg_tgt`, so an interior string pointer is marked and relocated with its block today. The placement table (09:32, SCRIP a085fba5a): Icon operands RSP 9,953, RBP 96; locals RSP 121; allocs 98. The six Icon rows: Zona 118/118, Jcon 85/85, IPL 644/644, IcnRungs 936/936, IcnBench 26/26, IcnDemo 7/7. The six witnesses read EQUAL in both modes today: every step is RED by its census alone, and the finish's own reading is 139 calls and 99 readers with the smoke green.

### 11.2 THE RULINGS (CEO-1888; each is one step's law, R1-R6 in step order)

- **R1 -- A tab OR move RESULT SHARES THE SUBJECT'S BYTES.** The result of `tab(i)`, `move(n)` and the scan alternate box is the descriptor `{DT_S, n, r13 + a}` -- three instructions, one composed qword for the tag and length (10.7 (a)), one `lea` -- never a copy: an Icon string is immutable and a value is a (length, pointer) qualifier, so the result may point into the subject as Arizona's does. The collector needs nothing: `gc_visit_one` marks the block an interior pointer lies in and relocates the slot with it (11.1), and a subject whose bytes are rodata (mode 4) or the slab's constant pool (mode 3) is not in the heap, `gc_blk_of` answers null, and the visitor leaves it alone. A subject coerced at ENTER (10.7 (a), the empty or non-string subject through `rt_icn_subject_coerce`) is a heap string and shares the same way. `rt_substr` keeps its other callers (SNOBOL4, Snocone) and loses every Icon scan caller. The witness is01_substr slices, compares, images and measures tab and move results over a 500-byte subject and three one-byte moves.
- **R2 -- EVERY LEXICAL FORM IS THE BOX (10 R5 i-iii, decided).** (i) A non-literal cset (`c := cset("aeiou")`, `&letters`, `c -- 'u'`) reads a 256-bit table in the cset block, built once when the cset is made (hq_runtime's field, 10.4): the box tests `bt [table], al`; a literal cset keeps its inline table. (ii) A string used as a set (`any("abc", s)`) takes the match plane's membership leaf; an empty needle matches at the cursor. (iii) A needle of any length is the same compare loop with a run-time length (`find`, `match` over the 32-byte boundary the witness crosses). (iv) The explicit-subject forms `f(c, s, i, j)` are the same box with a PROLOGUE that banks (r13, r14, r15) in the box's own carve (CTO-349: a box's own state is its own carve; 16 bytes plus the 8 of the cursor), loads the window from `s` (a non-string through the coercion leaf, as ENTER does), converts `i` and `j` by the position rule (a non-positive position is `length + 1 + p`, out of range fails, `i > j` swaps) and an EPILOGUE that restores the three; the result is computed against the window and is R1's shape into `s`'s bytes. A builtin reached BY NAME (a procedure value, is04) is not this step's: it stays on the C road until step 4 carries the words there and the cto's `rt_call_arr` row makes the dispatch a box. The lowerer lowers every lexical scan builtin as its box in every graph (road A, 10.7); `rt_scan_needle`, `rt_icn_cset_bits_d` and `rt_icn_cset_member_n` have no emitted caller after this step.
- **R3 -- THE CO-EXPRESSION SWITCH CARRIES THREE WORDS (10 R7, decided).** `scrip_coexpr_entry_pkg_t` gains `r13` and `r15` beside `r14`, three stores before the switch and three loads after it in `bb_activate`, `bb_coret` and the cofail road, in both directions through the same record; the trampoline loads the three from the record, never from a global. Every co-expression shares the environment of its activator at the moment of activation (10.1 (c), is03: a co-expression reads, assigns and scans the shared environment across three activations and the activator sees the assignment on return): the record is the carrier, not a second home. `ScanState`, `rt_scan_state_capture`, `rt_scan_state_apply`, `rt_scan_state_reset`, `inherit_scan`, `sigma_live` and the `ct_zalloc` behind them are deleted; `rt_coexpr.c` reads no `abi.scan_*`.
- **R4 -- THE C-FRAME ROAD CARRIES THE THREE WORDS EXPLICITLY (10.5, decided).** A procedure reached through a C frame -- a procedure value called by name through `rt_call_arr`, APPLY, the error-voice re-entry -- receives (r13, r14, r15) as arguments of that C activation's own record (`ScanSubjRegs` in and out: stack words of the C frame, THE LIFETIME RULE) and hands them back as its result; the box that called the C road reloads the three from the record. `bb_call_fn`'s seven `op_call_scansync`/`op_call_curmov` sites and `bb_call_value`'s two `cv_sync` sites go with `rt_scan_sync_out` and `rt_scan_sync_in`; `bn_icn_any`, `bn_icn_tab` and `bn_icn_move` read their window from the record; `BID_ICN_SCAN_PUSH`/`POP` go (an environment is entered and left by `bb_gen_scan` alone, never by name). Once the dispatch is a box the road is 10 R2 like every other; the two designs land in either order and this step does not wait.
- **R5 -- THE KEYWORD BOX READS AND WRITES THE REGISTERS; THE ROOT PERSISTS (10 R4 and R8, decided).** `&subject` read is `{DT_S, r15d, r13}` and `&pos` read is `r14 + 1`, in the box. `&subject := e` inside a scan sets the INNER environment (the three registers, through the coercion leaf for a non-string) and the scan's LEAVE restores the outer from the ENTER bank; outside a scan it writes the root environment, which persists to the program's end (is05: `&subject := 42` then `&pos := 3`, read back after a scan that assigned `&subject` inside). `&pos := e` converts a non-positive position by the position rule, FAILS outside `1..length + 1` and leaves `&pos` as it was. THE VARIABLE FORM: a keyword used as a variable is lowered to the keyword box's forms AT THE USE -- a read at the point Icon dereferences it (an argument is dereferenced at the call, after every argument is evaluated: is05's `write(..., &pos, ..., move(1))` prints the position after the move, as iconx does), an assignment, an augmented assignment, a reversible assignment `&subject <- e` that banks the old three in the box's carve and restores them at its beta; no run-time keyword-variable descriptor exists, so `bb_keyword_icon`'s `KI_SCANKW` sync and its `rt_keyword_var` call go for `&subject` and `&pos` and `core.c`'s two arms are deleted. `&subject` and `&pos` are never compared to a sentinel (10.7 (b)).
- **R6 -- THE FINISH IS A CENSUS AT ZERO.** Over the 17 Icon benchmarks and is00_kw in mode 4: no emitted call to the nine functions of 10.3, `rt_keyword_var` or `rt_substr`; the five `g_runtime.abi.scan_*` members, `g_scan_empty` and the `ScanState` record have no reader in `src` (the polyglot driver's root reset becomes the Icon root entry's own three loads, 10.7 (b); the shield at `gc_heap.c:3712` reads the SNOBOL4 subject alone; `harness/scripts/util_g_runtime_abi_offsets.py` regenerated); is00_kw prints `3` and `def`; the Icon smoke green; the six Icon rows not below 100 percent; the placement table's Icon operands on RBP not above 96. Nothing of SNOBOL4's match plane moves (10.6).

### 11.3 THE STEPS (STEPS.tsv beside the witnesses; one landing each; the ceo mints one row per step)

| step | slug | executor | depends | probe (RED today) | witness | files |
|---|---|---|---|---|---|---|
| 1 | tab-and-move-share-the-subject-bytes | hq_icon | - | emitted `rt_substr` calls 85 -> 0 | is01_substr | bb_scan_tab.cpp, bb_scan_move.cpp, bb_scan_alternate.cpp |
| 2 | every-form-is-the-box | hq_icon (the cset field hq_runtime's) | 1 | emitted `rt_scan_needle`, `rt_icn_cset_bits_d`, `rt_icn_cset_member_n` 6 -> 0 | is02_forms | the nine bb_scan_*.cpp, lower_icon.c, keywords.c (the cset block), icon_runtime.c |
| 3 | the-co-expression-switch-carries-three-words | hq_runtime | - | the five ScanState names present in src/runtime 5 -> 0 | is03_coexpr | rt_coexpr.c, bb_activate.cpp, bb_coret.cpp, gen_runtime.c |
| 4 | the-c-frame-road-carries-the-words-explicitly | hq_runtime | 2 | emitted `rt_scan_sync_out` + `rt_scan_sync_in` 46 -> 0 | is04_byname | bb_call_fn.cpp, bb_call_value.cpp, by_name_dispatch.c, gen_runtime.c |
| 5 | the-root-and-the-keyword-assign-inside-a-scan | hq_icon | - | emitted `rt_keyword_var` 2 -> 0 | is05_root | bb_keyword_icon.cpp, bb_keyword_assign.cpp, bb_gen_scan.cpp, core.c |
| 6 | the-finish | hq_icon | 1,2,3,4,5 | census ALL 139 -> 0, mirror readers 99 -> 0, the Icon smoke, the six rows | is00_kw | 10.3's deletion list, g_runtime_abi.h, util_g_runtime_abi_offsets.py |

Steps 1, 3 and 5 are independent and may land in any order or in parallel across the two HQs; 2 follows 1 (the explicit-subject forms produce R1's result shape) and 4 follows 2 (the by-name road hands its window to boxes that exist). A step's landing runs its witness through `--step N`, the Icon smoke, and -- `src/templates` and `src/runtime` being shared code -- the eight smokes (CEO-1928), then pushes and telegrams the coo the parent and new hashes; the coo's tier 1 and the Icon cores are the verdict (CEO-1992). A witness that changes is re-cut with `--cut` (iconx, `icont -s`) in the same landing.

### 11.4 WHAT A BUILDER MUST NOT DO

No reader compares r13 to a sentinel to ask whether a scan is active (10.7 (b)). No result copies the subject (R1) and no box calls C for a membership test, a needle, a position conversion or a result (R2). No global, static or arena word holds the environment or a saved environment: a bank is the box's own carve (CTO-349), a co-expression's is its record (R3), a C road's is its own frame (R4). No new `g_` member and no new side table: the cset bitmap is a field of the cset block, declared to the collector's visitor. The planner key of an operand is its two qwords (10.7 (a)); a dword read at `+4` aborts. No template line edit adds lines (the gates read fixed windows). An Icon suite row that falls is cured or reverted within the tick, never excluded.

### 11.5 Rulings on steps 1 and 2 as hq_icon landed them, the cfo's review of R1, R4 and R5, and the keyword-variable forms measured (the cto, 2026-10-29 11:0x CDT; SCRIP 22e10e4a6, dc20c4d4f, 3e37dce6c; corpus 26e10946b, 52da90df4; harness 1f94609; hq_icon's telegrams of 10-28 23:4x-00:3x, the cfo's of 21:3x)

- **THE CSET BLOCK HEADER IS hq_icon's AND IS R2 (i)'s SHAPE AS LANDED.** Length at `s-40`, magic at `s-36`, the 256-bit table at `s-32`, one definition in `src/ir/cset_block.h`, `.s` still pointing at the chars so every C reader keeps working; the three variable-cset boxes test `bt [s-32]` inline. hq_runtime's 10.4 assignment of the field is AMENDED to this landing (hq_icon owned the creators because they were in its step's landing files and nothing else claimed them; the cfo reviews the collector side of the block as a leaf with a header). Three page facts from the landing: a heap block cached in a static pointer is stale after the first collection (the empty cset lives in static storage); the literal cset in mode 4 carries its header as `.quad` words before the string label through a `.cset_hdr` directive that is empty in the binary medium (mode 3 reads the lowerer's block in place); the mode-4 boxes use the base+index movzx form for the byte compare because they may call only the leaf's registers.
- **R2 (iv) IS ITS OWN ROW, hq_icon's, BEHIND STEP 4.** The explicit-subject forms `f(c, s, i, j)` stay CALLs to the by-name C (icn_retag_scan_body retags one-argument calls only) and `rt_icn_cset_member_n` and `rt_icn_cset_bits_d` stay in the runtime for that road. The ceo mints `icon-scanning-asm-step-2b-the-explicit-subject-forms-are-the-box` for hq_icon, depends 4 (the by-name road hands its window to boxes that exist), probe: the two C names have no emitted caller and `rt_scan_needle`'s census stays 0; witness is02's explicit-subject lines.
- **R1's TWO CONDITIONS (the cfo): A SHARED SUBSTRING IS NOT NUL-TERMINATED AND NO WRITER OWNS d.s.** (a) Every reader of a DT_S's bytes uses the length: the runtime and rtx are audited for strcmp, strlen, atoi, strtod, printf %s and strchr on `d.s` (the copies hid them: step 1 found two, the by-name dispatch now materializes unterminated string arguments and five conversion predicates read `rt_cstr_d`), and a NUL-dependent read bombs under SCRIP_DIAG; the audit is a census script the ceo mints for hq_runtime (`audit_nul_dependent_string_reads.py`, a ratchet from its first reading). (b) An in-place append or overwrite (a concatenation extending at the heap top, a map or replace writing over its argument) first tests that it holds the whole block from its start. (c) The retention cost (a 10-byte token tabbed from a 1 MB line keeps the line alive; iconx compacts string space) is measured by a census of retained interior bytes before anyone acts on it; no IPL program is known to meet the heap cap through it.
- **R4: STRING INVOCATION REACHES THE SAME RECORD.** `"tab"(3)` and `proc("move")` enter through the by-name road and read the three words from the C activation's record like every by-name builtin.
- **R5's VARIABLE FORMS, MEASURED IN THE CORPUS TODAY (grep over every .icn under corpus/).** PRESENT: the exchange `&pos :=: x` and the reversible exchange `&pos <-> x` (arizona_tests scan.icn and subjpos.icn, jcon_tests the same; `&pos :=: &subject` in scan.icn), `&random :=: r` and `&random <-> r` (ipl kaleid.icn). ABSENT: a generator of variables `(&pos | x) := 3`, a subscripted keyword as a target `&subject[1:3] := "xy"`, `!&subject := "a"`, a keyword passed where a procedure needs a variable. RULED: the exchange and the reversible exchange with a register keyword operand are the keyword box's forms AT THE USE -- read both operands, assign both through the keyword box's assign road (the position rule and the coercion leaf apply), the reversible form banks both old values in the box's own carve and restores both at its beta -- so no run-time keyword variable exists for them; `&random` and the other standing-cell keywords exchange through the ordinary variable road, which is not R5's subject. The four absent forms are REFUSED at lowering by name (`&pos is not a variable in this form`) until a corpus program needs one; when one does, the design is ONE descriptor kind DT_KWVAR carrying the keyword id, produced only at those sites and dispatched by the assign-through-variable road (iconx's tvkywd), its witness cut against iconx -- never a general keyword-variable descriptor for the forms above.

### 11.6 R3 AS LANDED: THE THREE WORDS LIVE IN THE CONTEXT RECORD, NOT THE ENTRY PACKAGE; R5 EXTENDED TO suspend AND return (the cto, 2026-10-29 13:3x CDT; hq_icon's telegram of 13:1x; SCRIP b364f719e, a1cdba308)

hq_icon landed the switch words in `scrip_coctx_t` (`env[3]`) rather than in `scrip_coexpr_entry_pkg_t`, for three measured reasons: (a) the root context has no entry package and is03 activates it from inside a co-expression (`@&source`); (b) an activation operand that is not a co-expression (error 118, failure under `&error`) must not be dereferenced by emitted code before the runtime validates it, so the box cannot write the target's package; (c) the departing party needs no destination: it stores the three into the RUNNING context's own record (`rt_co_env`, a leaf) and `scrip_coswitch` copies them to the destination before posting, which makes every activation order right (a non-adjacent activation, `@&main` from a nested co-expression; is03b, is03c cut from iconx). **RULED: the landing stands and R3 reads "the context record is the carrier".** The record is still the carrier and not a second home (10.1 (c) unchanged); the package's slot 16 (the creator's r14) is DEAD and is deleted in hq_icon's step 4 landing, so R6's census finds no dead slot. **R5 EXTENDED:** a keyword variable is dereferenced AT ITS USE, in the environment of the use, whether it reaches the use as an argument, a RETURN or a SUSPEND -- iconx yields `suspend &pos` as the variable and the caller dereferences it in its own scan environment (hq_icon's witness: 3 under iconx, 1 under SCRIP, which dereferences at the suspend); hq_icon lands the two forms in step 5 with the witness cut from iconx, and R6's census counts them.

### 11.7 R4 AS hq_icon PROPOSES IT: THE CONTEXT RECORD IS THE CARRIER AT EVERY TRANSITION, THE C FRAME HOLDS THE THREE ONLY BETWEEN TRANSITIONS (the cto, 2026-10-29 14:3x CDT; hq_icon's telegram of 14:0x; SCRIP b364f719e: 44 emitted C-road calls -- call_value 20, call_byname 16, call_gen 8)

hq_icon measured that the C roads' argument registers are full (`rt_call_value_spine_prep_blk` takes rdi:rsi, rdx, ecx, r8; the apply forms rdx:rcx), so R4's "arguments of the C activation's own record" would be stack arguments, which shift the park-site derivation (the caller's rsp as efp+16) for a thread that switches inside such a road, or three more qwords in every call node's grant (a cell-shape change). **RULED: the step-3 pattern, as hq_icon recommends.** The box stores r13, r14, r15 into the running context's env record (`rt_co_env`, a leaf) before the call and loads the three from it straight after, before any poll; the C road copies the three out of the record at its entry and writes them back before it returns. THE TRANSITION RULE that makes nesting safe, which the letter states and the page now pins: the record is THE TRUTH AT EVERY TRANSITION between a box and a C road, in either direction, and a C road holds the three in its own frame ONLY BETWEEN transitions -- a road that re-enters a box (a procedure value through `rt_call_arr`, APPLY, the error-voice re-entry: CEO-1576's returned-address road) writes the record before the re-entry and re-reads it after, because the box it enters may poll and the collector forwards the subject through the record (the three words of `scrip_coctx_t` are typed roots, `test_gate_the_coexpression_roots_are_typed.sh`), never through a C local. The scan builtins (`bn_icn_tab`, `move`, `any`, `many`, `upto`, `pos`, `match`, `bal`, `find`) re-enter nothing, so entry-copy and exit-write suffice for them. The scan-active sentinel (`scan_pos > 0`) goes: outside a scan the environment is the root's (R5), so `tab`, `move` and `pos` act on it. `BID_ICN_SCAN_PUSH`/`POP` go as R4 says, hq_icon's census confirming no emitter but `bb_gen_scan` names them. R4's "stack words of the C frame" reads, from here, as the road's working copy between transitions; no new argument, no planner change, no global.

### 11.8 Step 4 as built (the hand-back and the dropped guards), step 2b's cell grant and position rule, and step 6's finish line re-keyed off Lon's loadfunc hold (the cto, 2026-10-29 16:1x CDT; hq_icon's telegrams of 15:0x and 15:3x; the ceo's CEO-2010 asks)

- **(a) THE GENERATOR ROAD'S HAND-BACK IS A NAMED DEBT, NOT A ROW.** As built (SCRIP 28cfcade3 and 1459d7445; census 44 to 0; is04_byname, is04b_forms, is04c_collect_in_callee equal iconx at stress 1, 3, 5, 8 under the flip plant in both modes; the probes of steps 1, 2, 3 and 5 green; slot 16 deleted): the post-road load reloads the cursor alone and zeroes the record (hq_collector's stale-subject finding, cured as 11.7 says); the generator road (`rt_proc_call_gen_h`, `rt_proc_resume_frame_h` through `scrip_coexpr_activate`, leaving by `scrip_coret` in C) keeps the caller's three words in the C frame across the switch and restores them after it. NOT built: R4's "hands them back as its result" for a body on that road that moves the caller's cursor, and the body's entry from the record rather than the creation-time registers. MEASURED: no Icon source reaches that road (the value-call prep declines builtins, unregistered names and non-names; genp.spine is unreachable from Icon), and Prolog's and Raku's boxes do not read the record. RULED: a row exists only while a measurement says the problem exists (CEO-1386), so nothing is built until a program reaches it; the thunk hq_icon describes (stores of r13, r14, r15 into the record before the C body on `rt_genp_deliver_gamma`, `rt_genp_deliver_omega` and `rt_genp_deliver_n2_gamma`, the loads after, the entry load in `rt_genp_thread_entry`) is the road's cure when one does, in step 6 or after it, with that program as its witness; 11.7 carries the sentence as debt. The push does not wait.
- **(b) THE DROPPED GUARDS ARE A RECORDED RISK.** The scan_pos-or-two-arguments guards on any, many, upto, match, find, bal, pos, tab and move in the by-name dispatcher are gone as ruled; a one-argument call of those names reaching the dispatcher BY NAME from another frontend takes the Icon scan road, because those names ARE Icon's builtins and the by-name road is theirs (LANGUAGE IDENTITY STOPS AT LOWER: a frontend that means something else lowers its own routine, which the measured corpora already do -- Snocone `pos` and Pascal `find` resolve to the user function). Recorded in the baton as a risk; no finding against the ruling.
- **(c) STEP 2b: THE CELL GRANT AND THE POSITION RULE.** (1) The explicit-subject forms bank the outer environment in the NODE'S OWN CARVE (CTO-349: a box's own state is its own carve; never a field of the context record, whose lifetime is the C transition's): SIX words at `op_off+24 .. op_off+64`, granted in `box_cell_shapes.tsv` by the condition `n_operands >= 2` on the nine scan ops (the TSV's condition column; the .inc regenerated in the landing): three for the outer bank (r13, r14, r15 as the box found them) and three for the window of `s`, `i`, `j` (its base, its end and its cursor's copy; the running cursor stays at `op_off+16`). THE DISCIPLINE: α saves the outer three and installs the window; γ restores the outer three (the result is absolute in `s`); β re-installs the window from the cells and re-saves nothing (the continuation's boxes restore the outer registers on their own ω, so at β they hold what γ left); ω restores the outer three and pops the carve. `icn_retag_scan_body` widens from one argument to 1-4 for the nine names. (2) THE POSITION RULE is as hq_icon reads it: `i` and `j` convert against `*s` (a non-positive p is `*s + 1 + p`; a position outside `1 .. *s + 1` after conversion FAILS at α -- the box's ω, no error; `i > j` swaps); the box computes from `base = s`'s bytes, `end = j - 1` and the start cursor `i - 1`, and the result is absolute in `s` -- the existing arithmetic; the conversion is IN THE BOX, a handful of instructions reading `s`'s length from the descriptor, not a leaf call. hq_icon takes step 6 first (the ceo's order) and lands 2b after it.
- **(d) STEP 6's FINISH LINE RE-KEYED.** The probe token `rows` ("the six Icon suite rows at 100 percent") reads: IcnRungs, IPL, IcnBench and IcnDemo at 100 percent; Zona and Jcon at 100 percent of their entries OUTSIDE Lon's loadfunc hold -- an entry is outside the finish line iff the loadfunc row (`icon-loadfunc-loads-a-c-function-from-a-shared-object-so-the-ipl-cfuncs-units-run-deferred-lon-2026-10-03`, PARKED-LON-HOLD) names it in its baton; the held entries are NAMED, never counted. hq_icon lands the token's reading in `test_design_icon_scanning_asm_steps.sh` with step 6 (STEPS.tsv row 6 cites this section), so step 6 closes on its own measurement.
- **(e) STEP 2b RE-CUT ON hq_icon's READING: THE ENTER WINDOW, NOT SIX CELLS (the cto, 2026-10-29 16:51 CDT; hq_icon's telegram of 16:2x).** The six-word grant of (c)(1) is WITHDRAWN before it is cut. The explicit-subject form `f(c, s, i, j)` of the scanning builtins LOWERS to the composition `(tmp := c) & (s ? f(tmp))` with the window installed by the scan ENTER node, which is already the bank-and-window wrapper (it banks the outer r13, r14, r15 in its own grant, installs r13 and r15 from the subject, its leave nodes restore on succeed and on fail and bank the inner across a suspension in a rooted DT_S cell the walker relocates): `i` and `j` are the ENTER's operands 1 and 2, evaluated in the outer environment, `c` before the ENTER so Icon's argument order holds; after the subject load the ENTER sets r14 = i - 1 and r15 = j - 1 under (c)(2)'s position rule (the conversion against *s IN THE BOX, a handful of instructions, a leaf only for a non-integer i or j; a position outside 1 .. *s + 1 FAILS at the ENTER's ω, no error; i > j swaps); r13 stays s's base, so every result is absolute in s. The nine boxes are untouched; no new planner cell; no raw base pointer in a non-rooted cell. WHY: (c)(1) made nine copies of the ENTER's bank; the bank's discipline (α saves, γ restores, β re-installs, ω restores and pops) is the ENTER's already and steps 4-6 proved it. THE WITNESSES: is02d_explicit_subject and hq_icon's corner cases (out of range, i above j, negative positions, &null defaults, a non-string s, an embedded NUL, a generator resumed after a nested scan), cut from iconx, plus two the composition must answer: (i) &subject and &pos read BETWEEN the results of a suspended `upto(c, s, i, j)` inside an outer scan read the OUTER values (the leave restores at γ, the β re-installs); (ii) `find(s1, &subject, i, j)` inside a scan leaves &pos unchanged. (c)(2) stands as the rule the ENTER computes.

### 11.9 THE ZSM EXPECTATION IS THE PLAN'S COLUMN, NEVER A CONSTANT: hq_icon's row re-cut (the cto, 2026-10-29 17:5x CDT; CEO-1888; hq_icon's measurement of ~17:50 on SCRIP d6d689400: `procedure g(); suspend 1 | 2; end` under `every g() do write("x")` prints 14 ZSM-AEXP/ZSM-DISC rows with the output right, every row delta 240 = g's RETAINED frame; the scan irrelevant)

RULED. (1) hq_icon's reading stands: downstream of a gamma that retains a callee frame the chain runs lower by that frame, the plan places no rsp-relative operand there (the Icon regime reads rbp cells), so the instrument's arithmetic RSP - RSP0 = op_zdepth is the wrong expectation for those nodes, not a defect in the emitted code; the cfo's row is re-cut to this reading. (2) THE CURE IS THE PLANNER'S COLUMN: the row records per node that its chain sits downstream of a retaining gamma (the planner knows the edge: `zd_edge_retains_g`, `zls_callee_is_gen`), and the ZSM event passes -1 for such a node so AEXP is not armed for an operand the plan cannot place. (3) NOT AN ACCESSOR: `x86_rsp_slide_known()` (x86_asm.h:638, the constant 1) is DELETED, not taught the column; its readers (`x86_frame_off`, the r8 load at x86_asm.h:2531, `x86_zsm_ev`) read the row field as a struct field (Lon: deciders deleted, not wrapped; CEO-1988). (4) Declaring the callee's frame a constant after the call is REFUSED by the rule that forbids reserving it (recursion). (5) DONE-WHEN: the three-line witness reads 0 ZSM rows under SCRIP_ZSM=1 SCRIP_ZSM_ALL=1 in both modes; the negative control fires (a planted wrong depth in an rsp-addressed regime, Prolog or SNOBOL4, still prints its rows; the plant in a worktree, never in src, CEO-1680); the Icon smoke green. The ZSM event's immediate changes, so the asm moves: the proof is the coo's identity run under CEO-1992, the lander runs the eight smokes and the census. (6) The rows are not a Prolog-only instrument: the ZSM reads every regime; what changes is that its expectation comes from the plan in every regime. This is the first instance of ARCH-GC-COMPILE-TIME-FRAME-MAPS § 17 (THE PLAN IS THE COLLECTOR'S MAP: every reader of the stack's depth reads the plan's column) and lands ahead of it.
