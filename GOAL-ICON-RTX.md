# GOAL-ICON-RTX.md — The Icon Runtime in Optimized x86-64 Assembly

**Minted s203-ICN (2026-07-29) on Lon's PIVOT directive:** *"Notice GOAL-SNOBOL4-RTX. We'll do the same
for Icon. Move all C runtime code into asm code in `*.s` files. Or move code into mode BB templates,
either one will be fine. Just ASM code not C code."*

Contract: **`ARCH-ICON-RTX.md`** — read it before any rung. Ladder runs CONCURRENTLY with `GOAL-ICON-BB.md`
(the ζ ladder) and `GOAL-SNOBOL4-RTX.md`, under the three-way amendment in that contract's §7.

---

⛔⛔ **SYMBOL OWNERSHIP IS NOT IN THIS FILE — IT IS IN `RTX-CLAIMS.md`.** The runtime is SHARED (19,962 lines, one `.so`, six languages); two RTX ladders work it from two directions. **25 symbols are called by both Icon and SNOBOL4 live artifacts.** Check a symbol OUT in that ledger — and PUSH the claim — BEFORE writing code. Run `scripts/util_rtx_claims.sh` at session start and session close; it derives symbol truth from the tree, so the ledger cannot rot silently. This ladder is `ICON-RTX`.


## ⛔ LIVE CURSOR — s203-ICN (2026-07-29): **RTX-0a SURVEY LANDED AS MEASUREMENT ONLY. NO CODE. ⭐⭐ AND THE SURVEY FALSIFIED ITS OWN FIRST TWO INVENTORIES BEFORE PRODUCING THE THIRD.**

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

**NEXT:** RTX-0b-ICN (interposer + Icon benchmark famsets) → **RTX-0d-ICN on `rt_call_arr`** — the
measurement that decides whether this ladder's headline target is real or is s188 repeating.
**⛔ BLOCKED PENDING LON: the §7 symbol-ownership amendment, and the SCAN-family template ruling.**
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
  ⚠ `options`/`post`/`shuffle` are compile-err **pre-existing** — exclude, do not investigate.
- [ ] **RTX-0d-ICN — ⭐ THE DECIDING MEASUREMENT: IS `rt_call_arr` HOT FOR ICON?** LD_PRELOAD interposer,
  **validated against a positive control first** (s201 discipline), counted at **two loop counts** with
  scaling confirmed. **Pre-state the expected board so a null is informative** (s188 rule). Outcomes:
  **HOT ⇒** it becomes the ladder's headline and the ownership ruling is urgent. **COLD ⇒** s188 repeats
  at 9× the static count, the finding is worth more than the port, and the ladder re-targets to the
  proc-setup family. ⛔ Either way this is a MEASUREMENT rung — it lands no asm.

### ▶ PHASE 1 — PORTS (each behind a family gate; C body → `c_*` in the same commit)

- [ ] **RTX-1-ICN — PROC-SETUP FAMILY** (`SCRIP_RTX_ICNCALL`). `rt_proc_set_fn` 361 · `rt_proc_set_nparams`
  210 · `rt_proc_set_jmpentry` 210 · `rt_proc_set_frame_bytes` 209 · `rt_proc_set_dcfn` 202 — **five
  symbols, one file (`rt.c`), one shape**: small setters called in a fixed cluster per procedure. ⭐ The
  natural FUSION candidate on the whole board (one entry, five stores) — but ⛔ **fusion changes the call
  sequence and is therefore PHASE 2**, template territory. Phase 1 = five `.S` bodies, signatures
  unchanged. ⚠ Step 0(d) first: per-procedure setup may be **setup-only**, i.e. the `rt_call_arr` trap
  in a different costume.
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
- [ ] **RTX-6-ICN — COERCION: `rt_coerce_num2_d` (209) + `rt_binop_overload` (141) + `rt_jct_relop` (163).**
  ⚠ `rt_cmp_d` is already ported (ARITH gate) — isolation arm required. ⚠ `rt_num_arith` (208) is
  **SN4-RTX's**, excluded pending the ruling.
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
