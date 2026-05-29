# GOAL-RAKU-BB.md — Raku goal-directed ~20% onto shared BB generators

**Repo:** one4all + corpus + .github
**Sister:** GOAL-ICON-BB.md (kinds REUSED) · GOAL-RAKU-FRONTEND.md
**Prereq:** HEADQUARTERS PP-1..6 ✅. BB-TEMPLATE-LADDER invariants 0..9 apply.

## Two IRs

- **SM** — flat stack-machine spine (`src/include/SM.h`).
- **BB** — four-port Byrd-box graph (`src/include/BB.h`). Kinds are **language-agnostic**. `BB_graph_t.lang` tags origin (`BB_LANG_RKU=6`); node kinds are reused.

SM emits `SM_BB_INVOKE` (language-ignorant BB jump-in/jump-out; split out of the old SM_BB_SWITCH per LANG-IGNORANT-SM-TEMPLATES, 2026-05-28). Raku reuses the ICN_GEN emit-time contract verbatim. Icon/Prolog are ~100% BB. SNOBOL4/Snocone/Rebus are mixed. Raku today is ~100% eager SM in practice; the goal-directed ~20% is what this ladder moves onto shared BB kinds.

## The insight

Per docs.raku.org: almost everything generative in Raku produces a **`Seq`**. `gather`/`take`, `…`, lazy ranges, `map`, `grep` — all "generate a Seq" on demand. ONE four-port pull protocol (yield-one-at-β = Icon `BB_SUSPEND`/`BB_EVERY` PUMP) suffices; every generative construct is a PRODUCER or CONSUMER of it. A 10-kind ladder collapses to ~3 rungs on shared kinds.

## Port semantics (identical to Icon generators)

| Port | Direction | Raku meaning |
|---|---|---|
| γ | inherited DOWN | `take` yield / next Seq element |
| ω | inherited DOWN | exhaustion (Seq drained; junction collapsed; grep all-false) |
| α | synthesized UP | fresh-pull entry (first `.pull-one`) |
| β | synthesized UP | resume entry (next `.pull-one` after a yield) |

Driver = **`BB_PUMP`**. NOT Prolog's `BB_ONCE`.

## Moves to BB vs stays SM

**MOVES (goal-directed, REUSE shared kinds):**

| Raku construct | shared BB kind | rung |
|---|---|---|
| lazy range `$a..$b`, `$a,$b ... $c` | `BB_TO_BY` | RK-BB-1 ✅ |
| `gather { … take … }`, `…` operator | `BB_SUSPEND` + `BB_EVERY` PUMP | RK-BB-2 ✅ |
| lazy `map` / `grep` | `BB_ITERATE` consumer | RK-BB-3 ✅ |
| junctions `any`/`all`/`one`/`none`, infix `\|`/`&` | `BB_ALTERNATE` + Bool-collapse | RK-BB-4 (blocked Q9-Q12) |

**STAYS eager SM:** scalar builtins, `say`/`print`, arithmetic, hash/array element ops, class/method dispatch, `sort` (whole-list), `try`/`CATCH`.

**SPLIT OUT to GOAL-RAKU-PAT-BB:** regex / grammar backtracking. Defer until SNOBOL4-BB and PROLOG-BB land more rungs.

## ⛔ Rules

- No C Byrd boxes; no SM/BB walking at runtime in modes 3/4; ports are α/β/γ/ω; X86 arms only.
- No `rt_*`/`raku_*` port-logic helpers. Conversion/effect helpers via `@PLT` (mode-4) or absolute `movabs+call` (mode-3) are fine.
- **No language sniffing in SM/BB/XA templates.** Per-language behavior lives in lowering.

## Completed rungs

- **RK-BB-1 ✅** `for $a..$b -> $i` → `BB_TO_BY`.
- **RK-BB-2 ✅** KEYSTONE lazy Seq. `gather`/`take`+`…` → `BB_SUSPEND`+`BB_EVERY` PUMP. REUSE `bb_upto.cpp`.
- **RK-BB-3 ✅** lazy `map`/`grep` as Seq CONSUMERS (eager-drain). Sub-steps 3.0/3a/3b/3c/3d green.
- **RK-BB-SEGFAULT-CLUSTER ✅** 4 bugs: polyglot union-clobber, multi-sub structure for TT_SUB_DECL, lower_return value preservation.
- **RK-BB-SM-FRAME-MODE4 ✅** Mode-4 named-sub frame slots: `rt_frame_enter/leave/load/store` + SM_LOAD/STORE_FRAME x86 templates.
- **RK-GIVEN-MODE4 ✅** `given`/`when` as if-chain (no SM_PUMP_CASE, no thunks).
- **RK-HASH ✅** hash builtins (set/get/exists/keys/values/pairs/delete), SOH/STX encoding.
- **RK-IO ✅** `rk_fileio38`+`rk_stdio39` mode-4. `TT_ITERATE(TT_FNC)` arm in `lower_every`; `raku_capture` returns FHVAL; setvbuf line-buffer stdout.
- **RK-EXCEPTIONS ✅** try/CATCH/die mode-4. SSE-safe `raku_die`; exc_clear/check/get; guard hash-builtin on DT_S.
- **RK-CLASS ✅** `rk_class26` modes 2 and 4. `lower_class_decl` emits `RECORD_REGISTER` before `RECORD_MAKE`; handler delegates to idempotent `icn_record_register`.
- **MODE3-NO-INTERP-3 ✅** SM_NAMED_CALL absolute-target patching in sm_run_native Pass 3 closed Cluster 2.
- **M3-RK-NOINTERP-1a ✅** `bb_to_by.cpp` MEDIUM_BINARY r12→rt_push_int (Sonnet 4.6, `55d03444`).
- **M3-RK-NOINTERP-1b ✅** SM_BB_INVOKE MEDIUM_BINARY arm — scratch-buffer-flush w/ sink save/restore, `walk_bb_node` integration, ascending-sites fix in `bb_to_by.cpp:142` (Opus 4.7, `48ca4e21`).
- **M3-RK-NOINTERP-1c ✅** `bb_iterate.cpp` Raku MEDIUM_BINARY arm wired (Opus 4.7, 2026-05-29, one4all `8d3a8cdf`). Mirrored the existing MEDIUM_TEXT arm in raw x86: α zeroes `&pBB->counter`, β-define falls into `NV_GET_fn(name)`, unpacks `rax:rdx` (low32=v, hi32=slen; rdx=base ptr), strlen-fallback when slen=0, bounds-check `jge lω`, scan for SOH separator, `GC_malloc(seg_len+1)` + `rep movsb` + NUL-term, `rt_push_str(ptr,len)` + `jmp lγ`. All four helper calls use absolute `movabs rax,&fn; call rax` (no PLT in mode-3). bin.sites ascending: `{beta_off, fail_off+2, succ_off+1}` paired with `{lβ_p define, lω_p, lγ_p}`. **Mode-3 native: 19→25 PASS** (+6: rk_fileio38, rk_for_array{,_simple,_underscore}, rk_given18, rk_map_grep_sort24 all CRASH→PASS).
- **M3-RK-NOINTERP-1d ✅** `rk_gather` closed (Opus 4.8, 2026-05-29, one4all `a894af4a`). Last Cluster-1 native test. The gather body BB graph is `BB_SEQ(n=4) → SUSPEND·SUSPEND·SUSPEND·FAIL` (NOT the bb_upto path the prior handoff guessed). Three coordinated fixes: **(1) `bb_seq.cpp`** new raw-x86 gather-driver `bb_seq_gather_binary` — the MEDIUM_BINARY arm only walked the `xa_bb_emit_pair_*[]` passthrough, which is UNPOPULATED on the SM_BB_INVOKE → `walk_bb_node` path (no `flat_drive_seq` ran), so outer β (`.Lbbinv%d_β`) was never defined → `bb_emit_end` abort. New driver mirrors the MEDIUM_TEXT gather-driver in raw bytes: α fan-out `jmp s0_α`; define outer β = `movabs rax,&resume_slot; mov rax,[rax]; jmp rax`; per-child: define Lα[k], `walk_bb_node(child,NULL)`, define Lγ[k] fixup (`movabs rax,&resume_slot; lea rcx,[rip+nxt]; mov [rax],rcx; jmp outer_γ`); done trampoline `jmp outer_ω`. resume_slot is a malloc'd quad (scratch page has no .data); intermediate labels malloc'd so pointers survive into the wrapper's `bb_emit_end` (runs after bb_seq returns); rip-relative `lea` patches via standard `bb_emit_patch_rel32` (site+4 = rip). **(2) `bb_suspend.cpp`** MEDIUM_BINARY arm now pushes via `rt_push_int` (movabs+call) not raw `mov [r12]` — `sm_run_native` doesn't init r12 as a value-stack pointer (the SM value stack is the `g_vstack` C global), so the old r12 stores segfaulted; same fix bb_to_by took in 1a; bin sites reordered ascending per 1b. **(3) `lower.c` `lower_every`** new branch for `for gather{} -> $v` (`TT_EVERY(TT_ITERATE(v, TT_FNC(__gather_N)))`) — the generic scaffold routed through `lower_iterate` which emits `SM_BB_INVOKE; STORE_VAR v` BEFORE the scaffold's `JUMP_F`, storing the loop var from an empty value-stack on the exhaustion pull → underflow; new branch mirrors the iterate-array branches (JUMP_F gates the store). **Mode-3 native: 25→26 PASS, CRASH 7→6** (rk_gather CRASH→PASS).

## Open rungs

- [ ] **M3-RK-NOINTERP-1e (regex cluster)** — `rk_re32/33/34/35/37`, `rk_regex23` (6 CRASH). DEFERRED to GOAL-RAKU-PAT-BB (regex/grammar backtracking). These are the only remaining mode-3 native CRASHes.
- [~] **RK-BB-4 substrate audit** — Probe-based audit found "REUSE bb_gen_alt.cpp/bb_alt.cpp" is unfounded. Seven gaps: lex (no KW_ANY/ALL/ONE/NONE, no single `|`/`&`); TT_ALT overloaded with SNOBOL4 pat-alt; bb_exec.c BB_ALTERNATE mode-2 is no-op; bb_alternate.cpp mode-4 missing; bb_alt.cpp mode-4 stub; bb_gen_alt.cpp stub; Icon TT_ALTERNATE lowers to BB_ALT not BB_ALTERNATE → **BB_ALTERNATE is orphan; reusable substrate is BB_ALT (mode-4 stub)**. Probe `test/raku/rk_junctions.{raku,expected}` committed (`4ee45eb7`); fails at lex.
  - **Open Qs for Lon (Q9-Q12, gating any work):** Q9 new TT_LOR/TT_LAND for `||`/`&&`? Q10 BB_ALT (recommend) vs finish orphan BB_ALTERNATE? Q11 substrate-first vs frontend-first? Q12 junction rep: (i) tagged string mirroring `\x01`-arrays (recommend), (ii) DT_JUNCT, (iii) DT_DATA.
- [ ] **RK-BB-4-frontend** — pending Q9-Q12.
- [ ] **RK-BB-5..N** — `reverse`/`tail`/`from-loop` as Seq consumers; `zip`/`cross` = multi-Seq drivers (later).

## Rung methodology

Per rung: (1) lower the Raku construct to the shared BB kind via `lower_raku_*` (parallel `lower_icn_*`); (2) confirm existing `bb_<kind>.cpp` covers it; (3) only if semantics differ, **extend the lowering** — never the template; (4) run GATE-RK4 + GATE-RK + GATE-RK3 + smoke. Commit when goldens match and nothing regresses.

## Test corpus — REUSE

`test/raku/*.{raku,expected}` (33 cases). Job is mode-4 conformance (Prolog GATE-4 pattern). Add NEW flat files only for laziness probes the eager suite can't express.

## Mode-3 (`--run`)

**2026-05-28 Lon directive (3× this session, BINDING):** mode-3 = flat-wired x86 SM AND BB. Interpreters reserved for mode-2. `--run` MUST NOT invoke `sm_interp_run`. Honest mode-3 = `SCRIP_M3_NATIVE=1 ./scrip --run`. Today's default `--run` for Raku silently falls through to `sm_interp_run` (empirically traced); ladder work to flip default tracked in `MODE3-DISPATCH-GAP.md`.

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
cd /home/claude/one4all && make -j4 scrip libscrip_rt > /tmp/build.log 2>&1
[ -x scrip ] || { grep -E "error:" /tmp/build.log | head -5; exit 1; }
for r in /home/claude/one4all /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
bash scripts/test_raku_ir_rungs.sh    # GATE-RK mode-2 baseline
bash scripts/test_raku_mode4_rung.sh  # GATE-RK4 mode-4 baseline
bash scripts/test_smoke_raku.sh       # smoke baseline
bash /tmp/gate_rk3.sh                  # GATE-RK3 mode-3 native (recreate from prior handoff if absent)
```

## Gates

```
GATE-RK    test_raku_ir_rungs.sh        # mode-2, must hold/improve
GATE-RK4   test_raku_mode4_rung.sh      # mode-4 vs .expected, must hold/improve
GATE-RK3   /tmp/gate_rk3.sh             # mode-3 native, must hold/improve
GATE-RK-SM test_smoke_raku.sh           # smoke must hold
```

## Watermark

```
one4all: M3-RK-NOINTERP-1d LANDED — rk_gather closed mode-3 native (Opus 4.8, 2026-05-29,
  one4all `a894af4a`). Gather body graph = BB_SEQ(n=4) → SUSPEND·SUSPEND·SUSPEND·FAIL.
  THREE fixes: (1) bb_seq.cpp new raw-x86 gather-driver bb_seq_gather_binary — MEDIUM_BINARY
  arm only walked the (unpopulated on walk_bb_node path) xa_bb_emit_pair_*[] passthrough,
  leaving outer β undefined → bb_emit_end abort; new driver mirrors the MEDIUM_TEXT gather-
  driver in raw bytes (α fan-out, β indirect-jump via malloc'd resume_slot quad, per-child γ
  fixups w/ rip-relative lea patches, done→outer_ω), interleaving walk_bb_node(child,NULL);
  intermediate labels malloc'd to survive the wrapper's bb_emit_end. (2) bb_suspend.cpp
  MEDIUM_BINARY now pushes via rt_push_int (movabs+call) not raw [r12] — sm_run_native
  doesn't init r12 as the value stack (g_vstack C global is), old stores segfaulted; same
  as bb_to_by 1a; sites reordered ascending per 1b. (3) lower.c lower_every new branch for
  `for gather{} -> $v` (TT_EVERY(TT_ITERATE(v,TT_FNC(__gather_N)))) — generic scaffold via
  lower_iterate emitted SM_BB_INVOKE; STORE_VAR v BEFORE JUMP_F → store from empty value-
  stack on exhaustion → underflow; new branch JUMP_F-gates the store like the iterate-array
  branches.

.github: GOAL-RAKU-BB.md — 1d moved open→completed; open rungs collapsed to the deferred
  regex cluster (1e); watermark + NEXT replaced. HANDOFF-2026-05-29-OPUS-RAKU-BB-M3-NOINTERP-
  1d-LANDED.md added.

corpus:  unchanged

GATE-RK   mode-2:                23/33  HOLD
GATE-RK4  mode-4:                26/33  HOLD
GATE-RK3  mode-3 native:         26/33 PASS, 1 FAIL, 6 CRASH  (was 25/1/7; +1 PASS, −1 CRASH;
                                                                 rk_gather CRASH→PASS)
Smoke raku:       5/5    HOLD
Smoke prolog:     5/5    HOLD
Smoke snobol4:    13/13  HOLD
Smoke icon:       5/5    HOLD
FACT RULE grep:   0
Build:            clean
```

## Remaining mode-3 native (CRASH 6 + FAIL 1)

- CRASH `rk_re32/33/34/35/37`, `rk_regex23` — Cluster 3 regex; DEFERRED to GOAL-RAKU-PAT-BB.
- FAIL `rk_junctions` — BLOCKED on Lon Q9-Q12.

## NEXT — Cluster-1 native COMPLETE

All non-regex, non-junction mode-3 native Raku tests now PASS (26/33). The remaining 7 split into
the regex cluster (6, deferred to GOAL-RAKU-PAT-BB) and rk_junctions (1, blocked on Q9-Q12). Next
substantive Raku-BB work is **RK-BB-4** (junctions) once Lon answers Q9-Q12, or picking up the
mode-2 gather gap (rk_gather FAILs mode-2 — `bb_exec.c` BB_SEQ doesn't drive the multi-yield
loop; mode-2 interp is a separate path from the mode-3 native templates landed here).

## Open questions for Lon

Resolved (2026-05-27): 100% template emission via BB/SM/XA only.

Pending:
- **Q5.** Union-clobber proper fix. TT_SUB_DECL uses `v.ival` for nparams AND wants `v.sval` for name. Move nparams to a side-channel so `v.sval = name` semantics is restored.
- **Q9-Q12.** RK-BB-4 directives — see substrate audit above.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
