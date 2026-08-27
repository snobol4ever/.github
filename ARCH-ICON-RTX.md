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

⚠ **Four ungated AT&T-syntax holdouts already violate Ruling 1** (`rt_sg_scan_member`,
`rt_sg_scan_nonmember`, `rt_sg_member`, `rk_gram_enter_box`) — inherited debt, recorded in
`GOAL-SNOBOL4-RTX.md` s202. ICON-RTX does not add to it.

---

## 2. REGISTER CONTRACT — IDENTICAL TO ARCH-SNOBOL4-RTX §2, PLUS ICON'S SUBJECT PINS

The blob pins are the SysV callee-saved set and are the same for every language. **Do not restate them
from memory — `ARCH-SNOBOL4-RTX.md` §2 is the single source, and it was found STALE and load-bearing as
recently as s205.** The corrected facts as of s205, re-verified against `x86_asm.h:347-361` and
`zeta_choices.h:177` at the time of this file's minting:

| reg | role |
|---|---|
| rbx | arena heap top / WS-GC bump frontier (HEAP arm; dormant under `ZC_PORT_FORTH` default) |
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
`.intel_syntax noprefix`.

```bash
for f in $(find programs/icon benchmarks/icon -name '*.s'); do
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
  call boundary is itself the architectural defect: `ARCH-ICON.md` specifies scanning as no-software-value-stack BB
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
1. **READ FIRST:** this file → `ARCH-ICON.md` (register contract + scan semantics) → the family's C
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
**Companions:** `GOAL-ICON-RTX.md` (ladder) · `ARCH-ICON.md` (BB/register/scan) ·
`ARCH-SNOBOL4-RTX.md` (the contract this one inherits) · `GOAL-ICON-BB.md` (the ζ ladder it runs beside)
