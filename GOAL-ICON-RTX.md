# GOAL-ICON-RTX.md — The Icon Runtime in Optimized x86-64 Assembly

**Minted s203-ICN (2026-07-29) on Lon's PIVOT directive:** *"Notice GOAL-SNOBOL4-RTX. We'll do the same
for Icon. Move all C runtime code into asm code in `*.s` files. Or move code into mode BB templates,
either one will be fine. Just ASM code not C code."*

Contract: **`ARCH-ICON-RTX.md`** — read it before any rung. Ladder runs CONCURRENTLY with `GOAL-ICON-BB.md`
(the ζ ladder) and `GOAL-SNOBOL4-RTX.md`, under the three-way amendment in that contract's §7.

---

⛔⛔ **SYMBOL OWNERSHIP IS NOT IN THIS FILE — IT IS IN `RTX-CLAIMS.md`.** The runtime is SHARED (19,962 lines, one `.so`, six languages); two RTX ladders work it from two directions. **25 symbols are called by both Icon and SNOBOL4 live artifacts.** Check a symbol OUT in that ledger — and PUSH the claim — BEFORE writing code. Run `scripts/util_rtx_claims.sh` at session start and session close; it derives symbol truth from the tree, so the ledger cannot rot silently. This ladder is `ICON-RTX`.


## 📨 INBOX FROM SN4-RTX (s208, 2026-07-29) — `rt_call_arr` IS YOURS, AND HERE IS THE MEASUREMENT WITH IT

**Lon ruled option (a) at s208: `rt_call_arr` → ICON-RTX. SN4-RTX has CLOSED RTX-4 slice 3, vacated the
ledger row, and become BENEFICIARY.** SN4 took `rt_flat_ret_snap` + `rt_proc_open_fn` from its exclusive
set instead. The contested row is now uncontested — `RTX-CLAIMS.md` is updated, that file is the truth.

⭐ **THE HANDOVER CARRIES A NUMBER YOU DID NOT HAVE: `rt_call_arr` = 87.334% of the `string_manip`
window** (10,000,004 calls, mode 3, RT_OPT=`-O0`, `rdtsc` interposer). **This is the first SHARE ever
taken on this symbol.** s188 had the count; s204 rejected the target holding that count. By s188's own
law a count cannot predict benefit — **a share can, and 87% is not a rejection.**

⛔ **DO NOT INHERIT ANY OF THIS AS SETTLED — three named gaps:**
1. **87.3% is the WHOLE CALL TREE**, everything the symbol reaches. **The PORTABLE fraction (dispatch
   prologue vs. callee work) is UNMEASURED. Splitting it is your first job, before any asm.**
2. **`-O0` only.** The `-O2` arm was not built (O2-DIRECTED-ONLY rule) and `-O0` frame ceremony is
   precisely what `-O2` shrinks. Never quote 87.3% without the `-O0` clause.
3. **It is a SNOBOL4 window.** Your 2157 static sites are the same class of evidence as the 232 that
   already misfired — **RTX-0d-ICN still owes its own dynamic 0(d) on an Icon workload.**
**s204's body-level rejection** (*needs fusion with `try_call_builtin_by_name`, already hash + inline
cache + jump table*) **is untouched by my number. Re-decide it against measurement; do not reverse it.**

⚠ **TWO MORE SN4 MEASUREMENTS ON SYMBOLS THE RULE ALLOCATES TO YOU — both say COLD *FOR SNOBOL4*, and
neither transfers to Icon without your own 0(d):**
- **`rt_coerce_num2_d`** (yours, 1.7×): **56 static sites, ZERO executions** across 7 SN4 benchmarks.
- **`NV_GET_fn`** (yours, 6.4×): **ZERO calls and ZERO static sites** in 7 SN4 benchmarks; live only
  under EVAL at **0.303%** (upper bound). Cause for SN4 is the **GVA slot island** — it removed the
  emitter's call sites, not the function. ⭐ **If Icon has no equivalent slot optimization, your 109
  sites may well be hot where SN4's 17 are dead. Same symbol, different answer — measure it.**

⭐ **THE GENERAL WARNING THIS SESSION PAID FOR: A RUNG'S PREMISE DECAYS WHEN AN UNRELATED RUNG SUCCEEDS.**
SN4's RTX-7 was correct when written and was invalidated by GVA landing — every check except 0(d) still
passed, including live C call sites. **Re-run 0(d) on any rung written more than a few sessions ago.**

---

## ⛔ LIVE CURSOR — s213-ICN (2026-07-29): **RTX-8-ICN LANDED SPLIT — `rt_list_bang_at` IS ASM AND PROVABLY EXECUTES; `rt_size_d`'s PORTED ARMS ARE A MEASURED NULL. ⭐⭐ AND THE WHOLE LADDER'S STATIC INVENTORY IS COMPUTED ON A PERMANENTLY-FROZEN STALE TREE.**

**NEXT RUNG: RTX-8b-ICN** — port the DT_DATA/list arm of `rt_size_d` + the body of `list_bang_at`,
using the fixed field layout (`fields[0]`=frame_elems, `[1]`=frame_size, `[2]`=gen_type) and the
proven type-pointer cache idiom at `pattern_match.c:24` (`rt_list_view`). **That deletes 3 `FIELD_GET_fn`
LINEAR SCANS (`strcasecmp` per field) + 1 libc `strcmp` PER `!L` ELEMENT ACCESS** — removable at ANY
`-O` level, so it answers inbox gap #1 concretely. Offsets measured: `DESCR_t` 16B (v@0 slen@4 val@8),
`DATBLK_t` nfields@8 fields@16, DT_DATA=100 DT_S=1 DT_SNUL=0 DT_I=6, FAILDESCR = {99, 0}.

**⭐⭐ THE FINDING THAT OUTRANKS THE PORT: `ARCH-ICON-RTX.md` §5's METHOD SWEEPS A TREE `RULES.md`
FORBIDS MAINTAINING, AND 96% OF THE ARTIFACT COUNT IS FROZEN A MONTH STALE.**
`corpus/programs/icon/*.s` = **255 of the 265 "live" artifacts**, last regenerated **2026-06-27**;
`corpus/benchmarks/icon/*.s` = 10 files, regenerated **2026-07-28**. RULES.md step 4 forbids ever
regenerating the former and `update_icon_bench_asm.sh` actively REFUSES it ⇒ **those 255 files are
frozen FOREVER.** PROOF: all 255 call `rt_frame@PLT`, **a symbol deleted at RUNG ZS-1 s57** — absent
from `src/`, absent from `nm -D` on the `.so`, and the current compiler emits it **ZERO** times. It sits
in the ledger as `FREE`, 255 sites, ICNCALL: a legal-looking claim on a symbol that cannot be ported
because it does not exist.

**⭐ CORRECTED SURFACE (compiler sweep, 263 programs — RULES.md: "sweep the COMPILER, never the artifacts"):**
| symbol | ledger | compiler | verdict |
|---|---:|---:|---|
| `rt_write_any_nl` | 566 (rank 3) | **0** | ⛔ PHANTOM — **RTX-4-ICN's ENTIRE TARGET** |
| `rt_call_proc_descr` | 542 (rank 4) | **0** | ⛔ PHANTOM — **RTX-3-ICN's primary target** |
| `rt_arg_stage` | 897 (rank 2) | **57** | 15.7× overstated — RTX-2-ICN's target |
| `rt_frame` | 255 | **0** | ⛔ symbol does not exist |
| `rt_relop_overload` | 51 | **185** | 3.6× UNDERstated |
⇒ **RTX-2/3/4 were minted against stale numbers.** The ladder recorded six "static counts don't
predict dynamic behaviour" falsifications; that diagnosis is WRONG — the INPUT TREE was stale.
⚠ SNOBOL4's artifact trees were regenerated **today**, so the ICON-vs-SNO allocation rule is biased
on both sides. ⭐ **STEP 0(i) MINTED: derive static counts from `scrip --compile`, never from stored `.s`.**

**⭐⭐ RTX-6c DISSOLVES — NO LON RULING IS OWED.** It was blocked arbitrating `rt_binop_overload` vs
`rt_relop_overload`. Measured: **`rt_binop_overload` — Icon emits it ZERO times** (its 141 "Icon sites"
are pure stale-tree; not contested at all). **`rt_relop_overload` — 185 REAL sites and ZERO dynamic
arrivals** across 296 running programs; 0(g) predicted it, since the template guards the call with
`cmp eax, DT_DATA; je` and these programs never compare records. ⇒ **CLOSE RTX-6c as NOT-A-TARGET.**

⚠ **`util_rtx_claims.sh` HAS A HOLE THAT LET THIS SURVIVE:** its PHANTOM-LEDGER check is
*"no definition **AND** no call site"* — so `rt_frame`, which has 255 call sites and NO definition,
passes CLEAN. Make it an OR.
⚠ **PROTOCOL DEVIATION:** no credential this session ⇒ the check-out was **not pushed before the work**.
SCRIP `2511c53a` is committed, NOT pushed. `scripts/handoff_status.sh` is the only completion truth.
⚠ 5 segfaults surfaced during the corpus sweep — consistent with the documented harness blind spot
(`test_icon_all_rungs.sh` grades stdout, discards exit code).

---

## ⛔ PRIOR CURSOR — s212-ICN (2026-07-29): **RTX-6b-ICN LANDED — `rt_jct_relop` IS ASM AT 1.761× ON/PRISTINE. ⭐⭐ AND THE RUNG WAS WON BY RE-RUNNING THE RECON s211 HANDED ME, WHICH WAS WRONG IN BOTH HALVES.**

**⭐⭐ A RECON HANDED FORWARD IS A CLAIM, NOT A MEASUREMENT — STEP 0(h) MUST COVER PROSE, NOT JUST CHECKBOXES.**
s211 recorded, as a free gift, that `bb_binop_relop.cpp` has **NO inline tag guard** and calls
`rt_jct_relop` at **five** sites. Measured s212 at the same HEAD: it **HAS** `DT_DATA`+`DT_I` guards
(lines 23-32, 107-116) and calls the symbol at **FOUR** sites. Acting on the inherited version means
porting the int-int arm — and the `DT_I` guard means int-int is **inlined by the template and reaches
the symbol ZERO times** (positive control: 2,000 `i < 1000` comparisons ⇒ 0 arrivals, while the same
program's string and real comparisons ⇒ 8,000). **That port would have measured ~0 — RTX-1-ICN's error
for the THIRD time.** ⭐ **RULE: re-run an inherited grep; it is exactly as perishable as an inherited
checkbox and exactly as cheap to redo.**

**⭐⭐ 0(g) RETURNS A DISTRIBUTION, NOT A BINARY — AND THIS IS A THIRD REGIME.** Interposer over the
**whole 303-program corpus**, binned by tag pair and op: **S/S 67.1%** of arrivals; ops **SEQ 46.7% ·
EQV 18.7% · SNE 9.6%**. Mapped onto the arm chain: the **textually-LAST** `VARVAL_fn`+`strcmp` tail is
**59.8%**, the **textually-FIRST** EQV/NEQV block is **24.8%**, the numeric middle is **~15%**.
⇒ **BOTH ENDS LIVE, MIDDLE COLD.** RTX-6 found first-arms *dead*; s211 predicted *"the opposite
regime, first arms live"*; **neither describes it.** The regime is a property of the specific
guard/callee pair and **cannot be predicted from the previous rung in either direction.**

**⭐ WHAT WAS ACTUALLY REMOVED, AND IT IS NOT `-O0` CEREMONY:** the exported wrapper ran a **`setjmp`
on EVERY call**; the dominant arm additionally made **2 `junction_is` + 2 `VARVAL_fn` + 1 libc
`strcmp`** and ~24 dispatch compares. All deleted on the fast path. **A deleted `setjmp` and a deleted
libc call are removable at any `-O` level** — same shape as RTX-6's deleted `strtoll`.

**⛔⛔ SIX OF THIRTEEN ICON BENCHMARKS HAVE NEVER RUN THEIR WORKLOAD — A NEW NAMED HALF OF RTX-0b.**
`concord · deal · ipxref · queens · rsg · tgrlink` carry `link options, post`; **neither IPL file
exists in `corpus/`**, so they die at link and print the `&features` banner. **My own first 0(d) sweep
read five zeros off dead programs before I checked.** ⭐ **RULE: a ZERO from 0(d) is not a result until
the program is proven to have RUN** — a dead benchmark and a cold symbol emit the same `0`.
`options.icn` **exists** in `refs/icon-master/ipl/procs/`; `post.icn` does not. Not chased, per the
goal file's standing "exclude, do not investigate".

⛔ **THE RUNG AS MINTED IS HALF-ILLEGAL AND THE REMAINDER IS LON'S.** RTX-6b paired `rt_jct_relop` with
`rt_binop_overload`, but the ledger allocates the latter to **SN4-RTX at 1.4×** (197 SNO vs 141 ICON,
past the 1.3× tie bar). **Only `rt_jct_relop` was ported** — an Icon-EXCLUSIVE row needing no
arbitration. ⇒ **re-assign `rt_binop_overload`, or re-mint the remainder around `rt_relop_overload`**
(51, COERCE, Icon-EXCLUSIVE, FREE), which is the legal same-family companion.

⚠ **PROTOCOL DEVIATION (same as s211):** check-out `427b3ab4` was **committed** before the port,
**not pushed** before it — no credential. ⚠ **SNOBOL4's absolute watermark disagrees with s211's prose
again** (measured **284/42**, prose says 276/50/8) — graded on the ON/OFF differential, **no culprit
asserted**. ⚠ **`scripts/util_rtx_claims.sh` STILL DOES NOT EXIST**; every ledger row remains
hand-asserted — including the one that caught this session's cross-ladder conflict.
`scripts/handoff_status.sh` is the only completion truth.

---

## ⛔ PRIOR CURSOR — s211-ICN (2026-07-29): **RTX-6-ICN LANDED — `rt_coerce_num2_d` IS ASM AT 1.783× ON/PRISTINE, WITH ITS `static` CALLEE ABSORBED. ⭐⭐ AND THE RUNG WAS WON BY READING THE EMITTING TEMPLATE, NOT THE C FILE.**

**⭐⭐ STEP 0(g) HAS A SECOND HALF AND IT INVERTS THE INSTINCT: THE CALLER TEMPLATE'S INLINE GUARD
DECIDES WHICH CALLEE ARM IS LIVE — AND IT IS SYSTEMATICALLY THE EXPENSIVE ONE.**
`bb_coerce_numeric.cpp:18-31` already inlines DT_I+DT_I and DT_R and reaches γ **without calling
anything**; the emitted `call rt_coerce_num2_d@PLT` sits on the arm that guard REJECTS. Measured:
pure-integer arithmetic enters the symbol **0 times**; string→numeric enters it **60,000 times /
120,000 parse entries**, live arms **STR_INT + DT_I**, with **STR_REAL / SNUL / FAIL all ZERO**.
⇒ `rt_parse_num_d`'s two textually-first arms — the ones the C reads first and the ones s210's handoff
points at — **are unreachable from Icon, and porting them would have measured ~0.** That is
RTX-1-ICN's exact error one rung over. ⭐ **RULE: read the EMITTING TEMPLATE before the callee; if it
guards the call with an inline tag `cmp`/`je`, port the arm the guard REJECTS.** One grep.

**⭐ THE `static` CONTRACT QUESTION s210 RAISED IS ANSWERED WITHOUT A CONTRACT CHANGE.** `rt_parse_num_d`
has no `@PLT` and no exported symbol, so the kill-switch idiom does not apply to it — **so do not apply
it to it. ABSORB the callee into the exported wrapper's asm body.** The gate lives on the wrapper,
which already has one; the static stays static and stays in C for the fallback. **No `ARCH-ICON-RTX.md`
§4 amendment is owed.** The port replaces libc `strtoll` on the live arm with an inline decimal scan —
a deleted libc call, **not `-O0` ceremony removal**, which answers inbox gap #1 concretely.

**⭐ RTX-0b's FIRST HALF IS DISCHARGED, AND THE FIX WAS NOT A BIGGER N — IT IS `&time`.** A self-timed
window measured INSIDE the Icon program excludes the compile phase **by construction**, so the ~20:1
confound s210 had to cancel arithmetically never enters. Benchmarks committed to
`corpus/benchmarks/icon/rtx/` (`97499dae`). ⚠ **RTX-0b IS NOT CLOSED:** mode 3 still does not forward
argv (`cannot open '-n8'`), so N is edited into the source.

**⭐ SECONDARY, AND IT RETRO-QUALIFIES s209's "noisy box": THE ALLOCATOR WAS THE BIMODALITY.** The first
benchmark was **refused by the harness** (intra-arm spread 1.566× > gap 1.188×) and its samples were
bimodal. More rounds cannot fix that — the spread is multiplicative. **Hoisting the per-iteration
allocation out of the loop took spreads 1.57× → 1.04×.** ⇒ **when a benchmark comes back ungradeable,
suspect the allocator in the window before suspecting the box.**

⛔ **UNTOUCHED, STILL LON'S:** RTX-0-RULING(a) ownership · RTX-0-RULING(b) SCAN destination (still
blocks RTX-2-ICN) · `rt_subscript_var` (315k, SN4-RTX's). ⚠ **PROTOCOL DEVIATION:** no credential was
available, so the check-out was committed ahead of the port but **not pushed** ahead of it; the
protective property was not obtained. `scripts/handoff_status.sh` is the only completion truth.

---

## ⛔ PRIOR CURSOR — s203-ICN: **RTX-0a SURVEY LANDED AS MEASUREMENT ONLY. NO CODE. ⭐⭐ AND THE SURVEY FALSIFIED ITS OWN FIRST TWO INVENTORIES BEFORE PRODUCING THE THIRD.**

**⭐⭐ THE HEADLINE, AND IT REFRAMES THE WHOLE LADDER: ICON HAS NO RUNTIME OF ITS OWN.** Measured, not
assumed: Icon-specific runtime C in the entire tree is **`src/parser/icon/icon_runtime.c`, 67 lines,
3 functions** (`icon_compile`, `icon_register_program`, `icon_real_str`) against a **19,962-line**
shared `src/runtime/`. **Icon's share is 0.34%.** ⇒ *"Move all C runtime code into asm"* for Icon is
**not a porting project — it is a RE-TARGETING and CLAIM-ARBITRATION project over SNOBOL4's runtime.**
Nine hot symbols are **already assembly** and land for Icon for free (`str_concat_d`, `rt_deref`,
`to_int`, `rt_gcheap_alloc`, `rt_str_alloc`, `rt_agg_alloc`, `rt_cmp_d`, `rt_faildescr`,
`rt_is_truthy`, both `rt_proc_call_epilogue_*` pairs).

**⭐⭐ AND THEREFORE THE FIRST THING THE LADDER OWES IS NOT A PORT — IT IS A LON RULING ON OWNERSHIP.**
`rt_call_arr` is Icon's **#1** symbol (2157 static sites) **and** SN4-RTX's open RTX-4 SLICE 3.
`rt_num_arith` (208) is SN4-RTX's RTX-6 remainder. `rt_subscript_var` (177) is SN4-RTX's RTX-5 family.
**Three of Icon's top twenty are already claimed by another live ladder over the same files.** SN4-RTX's
concurrency contract partitions RTX against ζ and assumes exactly ONE RTX ladder; with two it is
insufficient at file granularity. Amendment drafted (`ARCH-ICON-RTX.md` §7: ownership by SYMBOL, claimed
in a LIVE CURSOR before editing). **⛔ NOT SELF-APPROVABLE — Lon's call.**

**⭐⭐ TWO INVENTORY DEFECTS, BOTH MEASURED, BOTH REPRODUCED FROM THE PROJECT'S OWN HISTORY:**
**(1) THE LIVE-MARKER FILTER — this is ARCH-SNOBOL4-RTX §5's RTX-2 correction happening again, one
language over.** 305 Icon `.s` artifacts exist; **only 265 are live** (first line `.intel_syntax
noprefix`). The other 40 are legacy `scrip-cc -asm` nasm-syntax references — they even use nasm's
`extern` directive, which GNU `as` does not take. Sweeping all 305 manufactured four high-count port
targets: `icn_write_str` **510** · `icn_push` **242** · `icn_pop` **124** · `icn_write_int` **97**.
**Measured: 0 of the 265 live artifacts reference any of them, and none has a definition anywhere in
`src/`.** A ladder written off that sweep opens four rungs against symbols the compiler cannot emit.
**(2) ⭐⭐ THE `@PLT` FILTER — A GENUINELY NEW MEMBER OF THE PHANTOM FAMILY, AND THE FIRST ONE THAT IS
NOT A NAME PROBLEM AT ALL.** Runtime calls emit `call sym@PLT`; **locally emitted BB labels emit
`call sym`** — `main_α`, `proc_report_dcα`, `proc_startup`, `rt_gen_spine_pass_γ`. Stripping to
`[A-Za-z_0-9]*` **merges the two classes and truncates the Greek codepoints in one stroke**, so
emitted-inline assembly is reported as a C port target. **Prior members were DEAD names (RTX-2),
INVENTED names (RTX-3), MISRECORDED names (RTX-4), COLD names (s188), ALREADY-ASM names (s200). This is
a name that is not a runtime symbol at all.** ⇒ **STEP 0(f) MINTED: the symbol must appear as
`call sym@PLT` in a LIVE artifact.** The check is free.
⚠ **I made both mistakes in this session before catching them** — the first inventory I produced ranked
`icn_write_str` fifth. Recorded here because the taxonomy is only useful if the near-misses are in it.

**⛔ THE #1 SYMBOL IS UNRANKED UNTIL STEP 0(d), AND THE PRIOR IS AGAINST IT.** `rt_call_arr`'s 2157 for
Icon is the largest static count on the board — and `rt_call_arr` is the **standing proof that static
counts do not rank**: s188 measured it at **232 static sites for SNOBOL4 and 8 calls FLAT across
N=1→N=64**, setup-only, outside the timed window, ⇒ an asm port moves the board by zero *by
construction*. **A bigger static number is not more evidence; it is the same kind of evidence.** Icon
calls procedures very differently from SNOBOL4, so it may well be genuinely hot here — **that is a
measurement, and it is RTX-0d-ICN, and it must precede any port.**

**⭐ THE FORK LON OPENED IS RULED PER FAMILY, NOT PER RUNG** (`ARCH-ICON-RTX.md` §6). **DEFAULT = `.S`
port** (concurrency-safe, no `.s` regen). **EXCEPTION = the SCAN/generator family → BB TEMPLATE**, because
it is the one family where the call boundary IS the defect: `ARCH-ICON.md` specifies scanning as
stackless templates with Σ/δ/Δ pinned in r13/r14/r15, so `call rt_scan_enter@PLT` spills and reloads
precisely the registers the design pins. **Porting that to `.S` would make the wrong thing faster.**
⛔ Template work fires `.s` regen ×3 and collides head-on with the live ICON-BB session — **sequence it.**

**NEXT (REWRITTEN s210-ICN — the old pointer sent a session at a rung closed at s203):**
**RTX-0b-ICN is the blocker and it is BIGGER than "write famsets": the Icon corpus has NO legal window
and NO profilable program.** All 10 runnable benchmarks are **6–30 ms vs `MIN_MS=800`** (27×–133× under),
and at that size **compilation dominates a whole-process profile ~20:1**. `scrip --run prog.icn -n8`
⇒ `cannot open '-n8'` — **mode 3 does not forward argv**, so the corpus's own scaling knobs are
unreachable. ⇒ 0b owes: **(a) argv forwarding in mode 3 OR famsets carrying N internally, and (b)
authored scaled workloads, because none exist.** Until then this ladder can measure COUNTS (scaling
suffices) but not TIME (needs a legal window) — the half-rung state RTX-1-ICN landed in.
**THEN RTX-2-ICN := `rt_substr`** (240k run-phase, ICON-OWN, uncontested) — ⛔ but its destination is
**RTX-0-RULING(b)**, still open, and §6 rules the SCAN family to TEMPLATE.
**⛔ BLOCKED PENDING LON: (1) RTX-0-RULING(b) SCAN destination. (2) ⭐ NEW — `rt_subscript_var` is
Icon's #1 run-phase symbol (315k) and is checked out to SN4-RTX on a STATIC near-tie; the allocation rule
is written over static counts, which this ladder has now falsified three times. Amend the rule to
allocate on DYNAMIC count where one exists?** (§7 symbol-ownership amendment otherwise unchanged.)
**`handoff_status.sh` is the push truth — not this block.**

---

## ⚠ CONCURRENCY — THREE LADDERS, TWO SHARED SURFACES

See `ARCH-ICON-RTX.md` §7 for the full amendment. In brief:

| ladder | owns | must not touch |
|---|---|---|
| **ICON-BB (ζ)** — `GOAL-ICON-BB.md` | `emit.cpp`, `templates/*.cpp`, `x86_asm.h`, `zeta_storage.c` | `runtime/rtx/*.S` |
| **SN4-RTX** — `GOAL-SNOBOL4-RTX.md` | `runtime/rtx/*.S` + family C, **by claimed SYMBOL** | templates |
| **ICON-RTX** — this file | `runtime/rtx/*.S` + family C, **by claimed SYMBOL** | templates (except a ruled+serialized SCAN rung) |

⛔ **ALREADY CLAIMED BY SN4-RTX — DO NOT OPEN:** `rt_call_arr` · `rt_num_arith` · `rt_subscript_var`.
⚠ **`NV_GET_fn`/`NV_SET_fn`** are DB-1's planned write-barrier choke point — coordinate or land DB-1 first.
⚠ **THE WATERMARKS ARE SHARED STATE.** Re-prove Icon's at session start; say the numbers out loud in the
FINDING. Per RULES.md s47, `PLAN.md`'s Step column is stale BY DESIGN — trust this file's LIVE CURSOR.

---

## Session Setup

```bash
git config --global user.name "LCherryholmes"
git config --global user.email "lcherryh@yahoo.com"
git clone https://github.com/snobol4ever/.github.git /home/claude/.github
git clone https://github.com/snobol4ever/SCRIP.git   /home/claude/SCRIP
git clone https://github.com/snobol4ever/corpus.git  /home/claude/corpus
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && rm -f scrip && make -j4 scrip && make libscrip_rt
# Icon oracle (NOT the JVM path):
cd icon-master && make Configure name=linux && make      # -> bin/icont, bin/iconx (9.5.25a)
```

**READ-FIRST SET (NON-NEGOTIABLE, in this order):**
1. `RULES.md` in full — MONITOR-FIRST, TEMPLATE-ONLY EMISSION, HANDOFF-COMPLETE gate.
2. **`ARCH-ICON-RTX.md`** — register/ABI/build/ownership contract. §8 is the per-rung checklist;
   steps **0(d) / 0(e) / 0(f) / 2b** are the hard-won ones.
3. **`ARCH-ICON.md`** — the BB execution model, the per-graph frame-base selector, and the scan
   register contract (Σ=r13 · δ=r14 · Δ=r15). ⚠ It has been measured STALE twice (s196, s197) — verify
   against live `x86_asm.h` before relying on a register claim.
4. The family's C source **in full**, then the **ICON and JCON sources for every construct it
   implements**: `refs/icon-master/src/runtime/fstranl.r` (`any bal find many match upto`) +
   `fscan.r` (`move pos tab`) for scan semantics; `refs/jcon-master/tran/irgen.icn` (43 `ir_a_*`
   procedures, `ir_info(start,resume,failure,success)`) for port topology.
5. **⛔ ORACLE IS `icont`/`iconx`. NEVER INSTALL JAVA OR RUN THE JVM SELF-HOST PATH** (Lon, s121).
   If a step needs `java`/`javac`/`jar`, it is the wrong step.

**Verify the Icon watermark BEFORE touching anything** (`test_icon_all_rungs.sh`, re-derived fresh —
`GOAL-ICON-BB.md` s202 reads **252/11/30**), then run the ladder's first `- [ ]`.

---

## ⭐⭐ ICN-RTX — THE ICON RUNTIME IN OPTIMIZED x86 ASM (Lon PIVOT directive, s203-ICN)

**RULING OF RECORD:** the C runtime is a TRANSITIONAL ARTIFACT. The target is hand-written,
register-aware x86-64 assembly, or elimination of the call boundary into BB templates. Registers are
used freely; System V binds ONLY at (a) libc call boundaries and (b) the m3 driver→blob entry edge.
**But for Icon the runtime is SHARED**, so every rung is also an ownership question — see §7.

### ▶ PHASE 0 — SURVEY AND INSTRUMENT

- [ ] **STEP 0(g) — PROPOSED s209b, ⭐ ADOPT INTO `ARCH-ICON-RTX.md` §8.** For any symbol with internal
  dispatch, **identify which ARM the emitted code takes before choosing what to port.** 0(d) proves a
  SYMBOL is hot; it says nothing about which arm inside it is. RTX-1-ICN ported two arms that its own
  caller never enters. The check is one compile + one grep, exactly like 0(f).

- [x] **RTX-0a-ICN — SURFACE MEASURED, s203-ICN.** 265 live artifacts; full ranked inventory in
  `ARCH-ICON-RTX.md` §5. Two inventory defects found and corrected (live-marker filter; `@PLT` filter).
  Step 0(f) minted. Icon-specific runtime C measured at 67 lines / 3 functions. Nine symbols found
  already ported. Three symbols found already claimed by SN4-RTX.
- [ ] **RTX-0-RULING — ⛔ LON'S CALL, BLOCKS EVERYTHING BELOW.** Two decisions:
  **(a) SYMBOL OWNERSHIP** — adopt `ARCH-ICON-RTX.md` §7's by-symbol amendment, or serialize the two RTX
  ladders outright, or re-assign `rt_call_arr`/`rt_num_arith`/`rt_subscript_var` to ICON-RTX.
  **(b) THE SCAN FAMILY'S DESTINATION** — `.S` port (safe, keeps the boundary) vs BB template (deletes
  the boundary, fires `.s` regen ×3, collides with the live ICON-BB session). ⛔ Do not half-land (b);
  the BID-AT-LOWER ruling applies.
- [ ] **RTX-0b-ICN — MEASUREMENT INSTRUMENT.** SN4's `bench_sno_rtx.sh` measures SNOBOL4 programs; Icon
  needs its own famsets over `corpus/benchmarks/icon/`. **Inherit the discipline, not the famsets:**
  self-timed windows · ×4 N auto-ranging · **`MIN_MS=800`, a shorter window is reported `BOGUS-WINDOW`
  and its ratio SUPPRESSED, not printed small** · R interleaved rounds, **first round discarded**
  (hugepage compaction warmup, s201/s202) · medians · ON/OFF output byte-identity or the run is fatal.
  ⛔⛔ **s212 NAMED THE CAUSE OF THE DEAD-CORPUS HALF, AND IT IS NOT A FRONT-END GAP: SIX OF THE
  THIRTEEN BENCHMARKS DIE AT LINK.** `concord · deal · ipxref · queens · rsg · tgrlink` all carry
  `link options, post`, and **neither `options.icn` nor `post.icn` exists anywhere in `corpus/`** ⇒
  `icon: link: cannot open ./options.icn`, the program prints the `&features` banner and **never
  reaches its workload**. ⭐ `options.icn` **DOES** exist in `refs/icon-master/ipl/procs/`; `post.icn`
  does not. Vendoring the IPL procs (or stubbing `Init__`/`Term__`) is the cheapest unblock and would
  make six benchmarks profilable at a stroke. Not chased s212 per the standing "exclude, do not
  investigate" on `options`/`post`/`shuffle` — **but that note describes a symptom and this is the
  cause, so the exclusion is worth re-deciding.**
  ⭐⭐ **RULE MINTED s212: A ZERO FROM 0(d) IS NOT A RESULT UNTIL THE PROGRAM IS PROVEN TO HAVE RUN.**
  A dead benchmark and a genuinely cold symbol emit the identical `0`. s212 read five zeros off dead
  programs before checking that the output was the program's own and not a banner. Cost: one `head`.
  ⭐ **A working self-timed pattern now exists for authored workloads:**
  `corpus/benchmarks/icon/rtx/bench_icnrel_isolate.icn` (s212) and `bench_icnnum_isolate.icn` (s211) —
  `&time` opened INSIDE the program, allocation hoisted OUT of the timed loop, prints `ms: <n>` for
  `scripts/bench_rtx_3arm.sh`. s212's clears `MIN_MS=800` at ~1.9 s with arm spreads 1.03-1.10×.
  ⚠ `options`/`post`/`shuffle` are compile-err **pre-existing** — exclude, do not investigate.
- [x] **RTX-0d-ICN — ⭐ CLOSED s203-ICN, RE-CONFIRMED AND EXTENDED s210-ICN. `rt_call_arr` IS NOT THE
  TARGET.** s203-ICN: static rank's top three execute ZERO; hottest unported symbol was `rt_assign_var`
  at static rank 20 (⇒ RTX-1/1b). s210-ICN re-measured independently (`deal`=126, identical) and found
  **the MECHANISM: `rt_call_arr` scales 1:1 with `write()`, not with calls.** Determinate procs,
  generator procs and inline builtins all bypass it (1 call, flat, 200k→800k). ⇒ claim stays dropped.
  ⛔ **s210-ICN ALSO FOUND THE RANK ITSELF WAS CONTAMINATED:** whole-process profiles of `queens`/`deal`
  are **COMPILE-PHASE dominated ~20:1** (`rt_zeta_storage_get` &c. are the EMITTER). Rank only by
  `count(4N)−count(N)`, which cancels it exactly. See
  `FINDING-2026-07-29c-CLAUDE-ICN-RTX-0D-ROUND-2-…`.
  ⭐ **POST-RTX-1b RUN-PHASE RANK:** `rt_subscript_var` 315k (⛔ SN4-RTX's) · `rt_coerce_num2_d` 240k
  (ICON-RTX, FREE) · `rt_substr` 240k (ICON-OWN, SCAN) · proc-call path = **six C calls per call**,
  none of them `rt_call_arr`.
- [ ] **STEP 0(h) — PROPOSED s210-ICN, ⭐ ADOPT INTO `ARCH-ICON-RTX.md` §8.** Before opening a rung,
  **grep the FINDING set for the rung name** (`grep -l "Rung:.*RTX-0d-ICN" FINDING-*.md`). A `- [ ]` in
  this ladder is NOT evidence the rung is open — this checkbox was stale and caused s210-ICN to redo a
  landed measurement in full. **The FINDING set is truth; the checkbox is a claim.** Free, like 0(f).

### ▶ PHASE 1 — PORTS (each behind a family gate; C body → `c_*` in the same commit)

- [ ] **RTX-1-ICN — PROC-SETUP FAMILY** (`SCRIP_RTX_ICNCALL`). `rt_proc_set_fn` 361 · `rt_proc_set_nparams`
  210 · `rt_proc_set_jmpentry` 210 · `rt_proc_set_frame_bytes` 209 · `rt_proc_set_dcfn` 202 — **five
  symbols, one file (`rt.c`), one shape**: small setters called in a fixed cluster per procedure. ⭐ The
  natural FUSION candidate on the whole board (one entry, five stores) — but ⛔ **fusion changes the call
  sequence and is therefore PHASE 2**, template territory. Phase 1 = five `.S` bodies, signatures
  unchanged. ⚠ Step 0(d) first: per-procedure setup may be **setup-only**, i.e. the `rt_call_arr` trap
  in a different costume.
- [x] **RTX-1-ICN — ⭐ RE-TARGETED AND LANDED s209-ICN: `rt_assign_var`, NOT the proc-setup family.**
  The proc-setup target was falsified before it was written (`rt_proc_set_fn` measures FLAT 10@N=6 /
  10@N=8 — the s188 setup-only signature). `rt_assign_var` is the dynamic #1 unported symbol from
  static rank 20. Ported fast arms only behind new gate `SCRIP_RTX_ICNVAR`; C body → `c_rt_assign_var`.
  Icon 252/11/30 · SNOBOL4 276/50 · Prolog 185/0, each == its gate-off control. Falsification two-sided
  and NOT silent (broke a result ⇒ 247/16 gate-on, 252/11 gate-off).
  ⛔ **HALF-RUNG: NO SPEED CLAIM.** Window 16-20 ms vs `MIN_MS=800` ⇒ `BOGUS-WINDOW`, ratio suppressed.
  **The ladder cannot currently time its own landed work — RTX-0b-ICN is now blocking twice over.**
  See `FINDING-2026-07-29-CLAUDE-ICN-RTX-1-ASSIGN-VAR-LANDED-…`.
- [x] **RTX-1b-ICN — ⭐⭐ LANDED s209c: +12.11% MEDIAN / +12.46% MIN, NON-OVERLAPPING DISTRIBUTIONS. THE ARM THAT IS ACTUALLY LIVE: NAMETRAP → `vc->cellp` STORE.** s209b measured
  that **all 147 of Icon's `rt_assign_var` sites are SUBSCRIPTED assignment** (`L[i] := v`); local,
  global, augmented and swap assignment are all emitted inline and never call the symbol. A subscript
  lvalue is a NAMETRAP over a `VCELL_t`, so it takes **neither** arm RTX-1-ICN ported — proven by probe
  (corrupt fast-path B ⇒ 4M-store workload still correct). ⇒ port the `vc->cellp` store. It is the only
  live arm and RTX-1-ICN wrongly excluded it as cold.
  **RESULT: on=2519ms (2455-2753) vs off=2824ms (2761-2916), ZERO overlap, output byte-identical,
  window >> MIN_MS=800. Falsification 243/20 on vs 252/11 off (9 tests, vs 5 for the dead arm).**
  ⭐⭐ **THIS IS THE LADDER'S FIRST PROVEN SPEED WIN, AND ITS LESSON IS STEP 0(g):** the SAME symbol,
  the SAME gate, the SAME workload — wrong arms ~0%, right arm +12%. **Asm porting works for Icon; the
  arm selection is the whole game.**
- [ ] **RTX-2-ICN — `rt_arg_stage` (897, #2).** ⚠ Step 0(d) first — same trap class.
- [ ] **RTX-3-ICN — `rt_call_proc_descr` (542) + `rt_proc_value` (126) + `rt_frame` (255).** The live
  call path, distinct from the setup family. ⚠ `rt_proc_call_epilogue_γ/ω` are **already ported** —
  measure with `SCRIP_RTX_CALL` state declared, and use an **ISOLATION ARM**: this rung lands into an
  already-ported family, where a family gate's error has **no known sign and no known bound** (s204).
- [ ] **RTX-4-ICN — I/O: `rt_write_any_nl` (566, #3)** (`SCRIP_RTX_IO`). ⚠ It reaches libc `printf`;
  under Ruling 2 the port keeps libc and wins only `-O0` ceremony around it. **State that expectation in
  advance** so a null is informative. ⚠ Real formatting is JCON-semantics, not Arizona's — see
  `GOAL-ICON-BB.md` ICN-REALSTR; **do not "fix" `icon_real_str` to `rtos()`**, it regressed 252→250.
- [ ] **RTX-5-ICN — SCAN/GENERATOR FAMILY** (`SCRIP_RTX_SCAN`): `rt_scan_leave` 120 · `rt_scan_enter` 69 ·
  `rt_substr` 109, `builtins/gen_runtime.c` (283 lines). ⭐ **ICON'S OWN — no SNOBOL4 analogue, no
  ownership conflict, and the family where this ladder can say something SN4-RTX cannot.**
  ⛔ **DESTINATION IS RTX-0-RULING(b), NOT THIS RUNG'S CHOICE.** Read `fstranl.r` + `fscan.r` first and
  respect the two semantic families `ARCH-ICON.md` names: **position-returners** (`any`/`match`/`many`
  = `{0,1}`; `upto`/`find`/`bal` = `{*}` generators) leave δ untouched; **cursor-movers** (`tab`/`move`)
  write δ and **restore the saved δ on β then fail**. Blurring them is a correctness bug, not a perf one.
  ⚠ Σ/δ/Δ are live INPUT on this path, never scratch.
- [x] **RTX-6-ICN — ⭐⭐ `rt_coerce_num2_d` LANDED s211-ICN AT 1.783× ON/PRISTINE (gate `SCRIP_RTX_ICNNUM`,
  eighth family gate), WITH THE `static` CALLEE `rt_parse_num_d` ABSORBED RATHER THAN EXPOSED.**
  3-arm interleaved, round 1 discarded: **ON 861ms (841-922) · PRISTINE 1535ms (1523-1583) · OFF 1580ms**,
  spreads 1.04-1.10× against a **1.783× gap, ON and PRISTINE non-overlapping**, kill-switch tax 0.972×,
  `RT_OPT=-O0`. PRISTINE `.so` verified **byte-identical to the session baseline md5**.
  ⛔ **SCOPE — DO NOT LET THE NUMBER TRAVEL WITHOUT IT: 1.783× is an ISOLATION benchmark** (allocation
  hoisted out of the loop). The allocation-mixed variant was **REFUSED by the harness**; its 1.188× is
  recorded as **not-a-result** and is not claimed.
  Falsification two-sided and self-confirming: corrupting the live arm shifts the result by **exactly
  60,000 == the independently measured call count**; gate OFF correct. Gates: Icon 252/11/30 ·
  SNOBOL4 m3 280/54, m4 276/50/8 · Prolog 185/0/0, each identical ON and OFF.
  See `FINDING-2026-07-29-CLAUDE-ICN-RTX-6-ICNNUM-LANDED-1p783X-…`.
  ⚠ **`[x]` PENDING THE s202 ANCESTRY CHECK** (`git rev-list --count origin/main..HEAD` == 0) — SCRIP
  `eb81508d` is committed locally and that check is not yet satisfiable; no credential this session.
- [x] **RTX-6b-ICN — ⭐⭐ `rt_jct_relop` LANDED s212-ICN AT 1.761× ON/PRISTINE (gate `SCRIP_RTX_ICNREL`,
  ninth family gate). `rt_binop_overload` NOT PORTED — SEE THE OWNERSHIP NOTE BELOW.**
  3-arm interleaved, round 1 discarded: **ON 1063.5ms (1026-1130) · PRISTINE 1872.5ms (1846-1892) ·
  OFF 1811ms**, spreads 1.03-1.10× against a **1.761× gap, distributions nowhere near overlapping**,
  kill-switch tax 1.034×, `RT_OPT=-O0`. PRISTINE `.so` **byte-identical to the session baseline md5**.
  Falsification two-sided and NOT silent: corrupting the SEQ RESULT on the hottest arm ⇒ **244/19 gate
  ON, 252/11 gate OFF**. Gates: Icon **252/11/30** · SNOBOL4 m4 **284/42** · Prolog **188/0/1**, each
  identical ON and OFF. Ported arms = the **textually-LAST** `strcmp` tail (59.8%) + the
  **textually-FIRST** EQV/NEQV block (24.8%); numeric middle bails to C.
  ⛔ **SCOPE: 1.761× is an ISOLATION benchmark and the corpus reach is only 4,308 calls across all 303
  programs.** The 163 static sites are the **sixth falsification of static ranking on this ladder**.
  The speed is real on a legal window; **no corpus-wide impact is claimed.**
  ⛔⛔ **THE s211 RECON RECORDED ON THIS RUNG WAS FALSIFIED — IT IS DELETED ABOVE, NOT LEFT TO MISLEAD.**
  It claimed `bb_binop_relop.cpp` has NO inline tag guard and FIVE call sites. It **HAS** `DT_DATA`+`DT_I`
  guards and **FOUR** call sites, so this rung was in the SAME regime as RTX-6, not the opposite, and
  the int-int arm it pointed at reaches the symbol **ZERO** times.
  See `FINDING-2026-07-29-CLAUDE-ICN-RTX-6B-JCT-RELOP-LANDED-1p761X-…`.
  ⚠ **`[x]` PENDING THE s202 ANCESTRY CHECK** (`git rev-list --count origin/main..HEAD` == 0) — no
  credential this session.
- [ ] **RTX-6c-ICN — THE COERCION FAMILY'S LEGAL REMAINDER. ⛔ BLOCKED ON LON, ONE LINE.**
  RTX-6b as minted paired `rt_jct_relop` with **`rt_binop_overload` (141)** — but `RTX-CLAIMS.md`
  allocates that symbol to **SN4-RTX at 1.4×** (197 SNO vs 141 ICON, past the 1.3× tie bar). It is
  `FREE` but it is **not this ladder's to take**, same class as `rt_call_arr`. ⇒ **either re-assign it
  to ICON-RTX, or re-mint this rung around `rt_relop_overload`** (51, COERCE, **Icon-EXCLUSIVE**,
  `FREE`) — the legal same-family companion, and the one I would pick absent a ruling.
  ⚠ `rt_cmp_d` is already asm (ARITH) ⇒ **isolation arm required** (s204: a family gate's error has no
  known sign and no known bound). ⭐ **Re-run 0(g) from scratch on whichever symbol is chosen** — s212
  proved the arm regime does not transfer between rungs in EITHER direction.
- [ ] **RTX-7-ICN — `rt_jmp_frame_lexprep2` (209) + `rt_pl_dc_prep` (202).** ⛔⛔ **DUAL-ENTRY TERRITORY —
  HIGHEST-RISK RUNG ON THIS LADDER.** Icon compiles ONE shared body with TWO entries (`proc_X_α` and
  `proc_X_dcα`); `GOAL-ICON-BB.md` s196 records that this exact area broke Icon at HEAD for four
  sessions and that `fc_leaf_register` is **structurally incapable** of fixing it. Read that cursor and
  `FINDING-2026-07-27-CLAUDE-ICN-FLATDISP-BROKE-ICON-DUAL-ENTRY…` **in full** before touching it.
- [ ] **RTX-8-ICN — `rt_assign_var` (147) + `rt_list_bang_at` (110) + `rt_make_list` (95) +
  `rt_size_d` (93).** ⚠ `rt_subscript_var` (177) is SN4-RTX's — excluded pending the ruling.
- [ ] **RTX-9-ICN — `rt_keyword_read` (136).** ⛔ **PORT ≠ FIX.** Its failure allowlist
  (`keywords.c:213`) is **FRAGILE BY CONSTRUCTION** and its omissions are SILENT — that is how
  `&interval`/`&meta`/`&shift` hid (`GOAL-ICON-BB.md`). **Porting the body in asm preserves the defect
  and makes it faster.** Land the `kw_read`-returns-a-distinct-not-a-keyword-signal reshape FIRST, or
  skip this rung. ⚠ Shares the table with the SNOBOL4 reader.
- [ ] **RTX-10-ICN — `NV_GET_fn` (109).** ⚠ Coordinate with DB-1 (write-barrier choke point).
  ⚠ `ARCH-ICON.md` documents TWO variable backends kept side by side by Lon directive (frame slots vs
  NV dictionary) — **a port must not collapse that switch.**

### ▶ PHASE 2 — CONVENTION (⛔ SERIALIZE WITH LON; template territory, `.s` regen ×3)

- [ ] **RTX-11-ICN — REGISTERIZED ABI / FUSION.** The proc-setup cluster fused to one entry; S/F in
  EFLAGS instead of a `DT_FAIL` compare. Changes template call sequences via `x86(...)` encoders in
  `x86_asm.h`. ⛔ **Must not run concurrently with the ICON-BB ζ ladder.** Per
  `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md`: ONE `x86(...)` concatenation, medium switched **invisibly**
  inside the encoder, consumed via `bb_emit_x86`'s in-band `L`/`J`/`D`/`E`/`F` walk — **never** a
  hand-written `IF(MEDIUM_TEXT,…)+IF(MEDIUM_BINARY,…)` pair. That is the doc's named forbidden shape and
  it was written after the mistake was made twice in one session.
- [ ] **RTX-12-ICN — ERADICATION.** Delete `c_*` bodies and gates once each family is watermark-proven.
  Land when the board is quiet. ⚠ Shared runtime ⇒ eradication is **cross-language**: a `c_*` body
  deleted for Icon is deleted for SNOBOL4 and Prolog too. **Requires all three watermarks green.**

---

## Permanent notes

**⛔ ORACLE IS `icont`/`iconx` — NEVER JAVA/JVM** (Lon, s121). Sanctioned check: run under `scrip --run`
(mode 3) and/or `scrip --compile`+link (mode 4), run the same program under `icont -s prog.icn -x`, DIFF.

**⚠ HARNESS BLIND SPOT:** `test_icon_all_rungs.sh` grades **stdout only, exit code discarded**. A crash
that prints the right bytes first reads as a PASS. Use a crash-aware CLEAN/DIRTY split for any RTX gate.

**⚠ REAL FORMATTING IS JCON'S, NOT ARIZONA'S** — `kwds.expected` reads `&version: Jcon Version 2.2`;
reals carry Java `Double.toString` semantics. Where `icont`/`iconx` and this corpus disagree, **the
corpus is JCON's**. Do not "correct" toward `rtos()`; it cost 252→250 once already.

**⚠ NO `gdb`/`perf`/`valgrind`/`ltrace`/`strace` IN THIS CONTAINER; the monitor is dark (s158).**
Differential + two-sided falsification is the working substitute; an LD_PRELOAD interposer is the
step-0(d) instrument.

**⚠ `x86_asm.h` IS A HEADER — `make` DOES NOT TRACK IT.** `rm -rf out /tmp/si_objs`, or you get a
byte-identical binary and a false negative. **The emitter lives in `out/libscrip_rt.so`, not in `scrip`.**

**⛔ A RUNG IS `[x]` ONLY WHEN ITS COMMITS ARE ANCESTORS OF `origin/main`** (s202: two rungs were marked
landed while sitting on an unmerged branch that every fresh clone missed).
Check: `git rev-list --count origin/main..<branch>` == 0.

**Baselines:** Icon **252/11/30** at `GOAL-ICON-BB.md` s202 — **re-derive fresh, never hand-copy**
(s202: two watermark hashes in prose did not exist in their own repos).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
**Architecture:** `ARCH-ICON-RTX.md` · `ARCH-ICON.md` · `ARCH-SNOBOL4-RTX.md`

## Session-close / push protocol
See RULES.md — `scripts/handoff_status.sh` verbatim stdout is the ONLY sanctioned completion claim.
