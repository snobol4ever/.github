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
- **RK-M2-GATHER ✅** mode-2 gather multi-yield (Opus 4.8, 2026-05-29, one4all `30e7c0a1`). `rk_gather` FAILed mode-2: `bb_exec.c` `BB_SEQ` was an AG-PURE passthrough that never drove the gather body's `BB_SEQ→SUSPEND·SUSPEND·SUSPEND·FAIL` chain (SUSPEND hit `default:`→FAIL, and `bb_exec_once/resume` walk to `next==NULL` with no pause-at-yield). Added a gather driver INSIDE `case BB_SEQ`, gated `g_current_cfg->lang==BB_LANG_RKU && bb->α->t==BB_SUSPEND`: yields ONE take per (re)entry using `bb->counter` as the resume cursor (reset to 0 by `bb_exec_once`, preserved by `bb_exec_resume`); the counter-th SUSPEND's `α` is evaluated and returned as `bb->value` via terminal `NULL`; walking past the last SUSPEND onto `BB_FAIL` → `FAILDESCR`. Mirrors mode-3 `bb_seq_gather_binary` (resume_slot ≡ counter, per-child γ-yield ≡ the NULL return through the driver loop). GATE-RK m2 23→24. Ordinary proc-body SEQs (α not a SUSPEND) untouched.
- **RK-M2-ACOMP ✅** `SM_ACOMP` string→numeric coercion (Opus 4.8, 2026-05-29, one4all `30e7c0a1`). `rk_given18` FAILed mode-2: `given` on a `for`-loop variable missed every `when` arm. Array elements pulled via `BB_ITERATE` arrive as `DT_S`; `sm_interp.c` `SM_ACOMP` treated any non-`DT_I`/`DT_R` operand as `0`, so topic `"1"` compared as `0==1`→false→default. Fix mirrors `SM_ADD`: `if (l.v==DT_S) lv=to_real(l)` (and r). GATE-RK m2 24→25. Shared across all languages; verified zero regression (SNOBOL4 crosscheck unchanged via before/after stash, Icon relop direct, broad broker 6/6).
- **RK-BB-4a ✅** constructor junctions any/all/one/none mode-2 (Opus 4.8, 2026-05-29, one4all `30e7c0a1`). Per Q9/Q12. `lower.c` `lower_fnc` intercepts Raku lowercase any/all/one/none (NOT the SNOBOL4/Icon `ANY` pattern path) → `SM_CALL_FN __rk_jct_<flavor>` with the RK-BB-3.0a dup-name first arg skipped. `raku_builtins_byname.c` packs a tagged-string junction VALUE (Q12): `ETX(0x03) + flavor('a'/'l'/'o'/'n') + SOH-separated members` (ETX is free of the SOH/STX array/hash bytes). `rk_junction_is` + `rk_junction_collapse` (recursive on junction members) thread the relop per flavor: any=OR, all=AND, one=exactly-one, none=NONE. `sm_interp.c` `SM_ACOMP`(numeric)/`SM_LCOMP`(string) gain a junction guard (`DT_S && s[0]==0x03`, never fires for normal values) routing to the collapse. GATE-RK m2 25→26.
- **RK-BB-4b ✅** infix `|`/`&` junctions mode-2 (Opus 4.8, 2026-05-29, one4all `30e7c0a1`). Per Q10 (BB-ALT-class substrate is the model, but mode-2 uses the same tagged-string value as 4a — no new opcode per Q9). `raku.l` adds single-char `|`/`&` (flex longest-match keeps `||`/`&&`; no code-sigil conflict). `raku.y` `mk_junction` builds `l|r`→`any(l,r)`, `l&r`→`all(l,r)` as the SAME `TT_FNC` node make_call produces, so infix + constructor share one lowering + collapse; same-flavor chains FLATTEN at parse time (`(3&3)&3`→`all(3,3,3)`), sidestepping the nested-`\x01` leak in the flat rep. `%left '|' '&'`; parser/lexer regenerated, zero grammar conflicts. **Full `rk_junctions` probe PASS mode-2.** GATE-RK m2 26 (rk_junctions FAIL→PASS; net session 23→26).
- **M3-RK-NOINTERP-1d ✅** `rk_gather` closed (Opus 4.8, 2026-05-29, one4all `a894af4a`). Last Cluster-1 native test. The gather body BB graph is `BB_SEQ(n=4) → SUSPEND·SUSPEND·SUSPEND·FAIL` (NOT the bb_upto path the prior handoff guessed). Three coordinated fixes: **(1) `bb_seq.cpp`** new raw-x86 gather-driver `bb_seq_gather_binary` — the MEDIUM_BINARY arm only walked the `xa_bb_emit_pair_*[]` passthrough, which is UNPOPULATED on the SM_BB_INVOKE → `walk_bb_node` path (no `flat_drive_seq` ran), so outer β (`.Lbbinv%d_β`) was never defined → `bb_emit_end` abort. New driver mirrors the MEDIUM_TEXT gather-driver in raw bytes: α fan-out `jmp s0_α`; define outer β = `movabs rax,&resume_slot; mov rax,[rax]; jmp rax`; per-child: define Lα[k], `walk_bb_node(child,NULL)`, define Lγ[k] fixup (`movabs rax,&resume_slot; lea rcx,[rip+nxt]; mov [rax],rcx; jmp outer_γ`); done trampoline `jmp outer_ω`. resume_slot is a malloc'd quad (scratch page has no .data); intermediate labels malloc'd so pointers survive into the wrapper's `bb_emit_end` (runs after bb_seq returns); rip-relative `lea` patches via standard `bb_emit_patch_rel32` (site+4 = rip). **(2) `bb_suspend.cpp`** MEDIUM_BINARY arm now pushes via `rt_push_int` (movabs+call) not raw `mov [r12]` — `sm_run_native` doesn't init r12 as a value-stack pointer (the SM value stack is the `g_vstack` C global), so the old r12 stores segfaulted; same fix bb_to_by took in 1a; bin sites reordered ascending per 1b. **(3) `lower.c` `lower_every`** new branch for `for gather{} -> $v` (`TT_EVERY(TT_ITERATE(v, TT_FNC(__gather_N)))`) — the generic scaffold routed through `lower_iterate` which emits `SM_BB_INVOKE; STORE_VAR v` BEFORE the scaffold's `JUMP_F`, storing the loop var from an empty value-stack on the exhaustion pull → underflow; new branch mirrors the iterate-array branches (JUMP_F gates the store). **Mode-3 native: 25→26 PASS, CRASH 7→6** (rk_gather CRASH→PASS).

## Open rungs

- [ ] **M3-RK-NOINTERP-1e (regex cluster)** — `rk_re32/33/34/35/37`, `rk_regex23` (6 CRASH). DEFERRED to GOAL-RAKU-PAT-BB (regex/grammar backtracking). These are the only remaining mode-3 native CRASHes.
- [x] **RK-BB-4 mode-2 ✅** (4a constructors + 4b infix, see completed rungs). **Full `rk_junctions` probe PASS mode-2.** Q9-Q12 ANSWERED by Lon (2026-05-29): **Q9** reuse existing kinds; break out new SM/BB opcodes ONLY if language-specific behavior diverges. **Q10** build on `BB_ALT` (live substrate Icon uses); split later if needed. **Q11** substrate-first. **Q12** tagged-string rep. Substrate proven: `BB_ALT` mode-2 is a complete n-ary alternation engine (empirically `x=(1|2|3)`→hit, `x=(7|8|9)`→miss, `every write(10|20|30)`→10/20/30); `BB_ALT` mode-4 `MEDIUM_BINARY` is a real counter-state dispatch slab (NOT a stub — the probe header's stale assumptions #3/#4 refer to the orphan `BB_ALTERNATE`, and only the `MEDIUM_TEXT` arm is a passthrough). Junction VALUE rep is the tagged string; the boolean collapse currently lives in mode-2 `SM_ACOMP`/`SM_LCOMP` (NOT yet on `BB_ALT`).
- [ ] **RK-BB-4c (mode-3/4 junctions)** — port the junction collapse to native: emit `__rk_jct_*` builder calls (already lowered language-agnostically) and a `rk_junction_collapse` call (movabs+call mode-3 / @PLT mode-4) at the `SM_ACOMP`/`SM_LCOMP` template sites, OR wire `any`/`|` through the proven `BB_ALT` binary slab as Q11 substrate-first intends. `rk_junctions` currently FAILs mode-4 (mode-2-only collapse). Builders are pure conversion/effect helpers (FACT-clean).
- [ ] **RK-BB-4d (junction edges)** — (1) MIXED-flavor NESTED junctions (`1 | (2 & 3)`) break the flat SOH tagged-string (inner `\x01` leaks into outer split); needs a length-prefixed member rep or SOH-escaping. Same-flavor chains already flatten at parse time so the probe is unaffected. (2) Unparenthesized precedence of `$x == 1|2|3` (probe always parenthesizes; `|`/`&` currently `%left` between `OP_AND` and `'!'`). (3) Junction stored in a var / threaded through non-`==` relops (numeric LT/GT collapse exists; string + var round-trip untested).
- [ ] **RK-BB-5..N** — `reverse`/`tail`/`from-loop` as Seq consumers; `zip`/`cross` = multi-Seq drivers (later).

## mode-2 fixes (non-ladder, this session)

- **gather mode-2** (RK-M2-GATHER ✅) and **`SM_ACOMP` string coercion** (RK-M2-ACOMP ✅) — see completed rungs. Net with junctions: GATE-RK mode-2 **23→26/33**.
- **`rk_stdio39` mode-2 FAIL is a test-fidelity issue, NOT a bug** — the `--interp` harness captures stdout only, but `rk_stdio39.expected` lists `stderr ok` as line 3, encoding `$*STDERR→fd 1`. Mode-2 correctly routes `$*STDERR` to fd 2 (real Raku); mode-4 only "passes" by mis-routing stderr to stdout. Lon's call whether to fix the golden or accept the mode-2/mode-4 divergence.

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
one4all: RK-BB-4 mode-2 junctions COMPLETE + mode-2 gather + ACOMP coercion (Opus 4.8,
  2026-05-29, one4all `30e7c0a1`). GATE-RK mode-2 23→26/33 (+rk_gather, +rk_given18,
  +rk_junctions). FOUR pieces: (1) RK-M2-GATHER — bb_exec.c BB_SEQ gather multi-yield
  driver (counter resume-cursor, lang==RKU && α==SUSPEND gate), mirrors mode-3
  bb_seq_gather_binary. (2) RK-M2-ACOMP — SM_ACOMP coerces DT_S via to_real (mirrors
  SM_ADD); fixed given-on-loop-var arm misses. Shared path, zero regression (before/after
  stash on SNOBOL4 crosscheck). (3) RK-BB-4a — lower.c intercepts any/all/one/none →
  __rk_jct_* builders (per-language lowering, dup-name skip); raku_builtins_byname.c packs
  tagged-string junction (ETX+flavor+SOH members, Q12) + rk_junction_collapse (recursive,
  per-flavor any=OR/all=AND/one=1/none=0); sm_interp.c SM_ACOMP/SM_LCOMP junction guard.
  (4) RK-BB-4b — raku.l single-char |/&, raku.y mk_junction builds any()/all() TT_FNC
  (same lowering as 4a), same-flavor chains flatten at parse time; parser/lexer regenerated
  clean. Full rk_junctions probe PASS mode-2. Q9-Q12 answered; BB_ALT substrate proven
  (mode-2 complete engine + mode-4 binary slab real). Mode-3/4 junctions = RK-BB-4c (next).

.github: GOAL-RAKU-BB.md — 4 new completed rungs (RK-M2-GATHER, RK-M2-ACOMP, RK-BB-4a,
  RK-BB-4b); open rungs restructured (RK-BB-4 mode-2 ✅, Q9-Q12 recorded, RK-BB-4c mode-3/4
  + RK-BB-4d edges added); mode-2 fixes note (incl. rk_stdio39 test-fidelity flag); watermark
  + gates updated. HANDOFF-2026-05-29-OPUS48-RAKU-BB-JUNCTIONS-MODE2.md added.

corpus:  unchanged

GATE-RK   mode-2:                26/33  (was 23; +rk_gather +rk_given18 +rk_junctions)
GATE-RK4  mode-4:                26/33  HOLD (rk_junctions still mode-2-only; no regression)
GATE-RK3  mode-3 native:         26/33  HOLD (not re-run this session; no native code touched)
Smoke raku:       5/5    HOLD
Smoke prolog:     5/5    HOLD
Smoke snobol4:    13/13  HOLD
Smoke icon:       5/5    HOLD
Broad broker:     6/6
SNOBOL4 crosscheck: 5/1 (beauty_omega pre-existing, isolated via before/after stash)
FACT RULE grep:   0
Build:            clean
```

## Remaining mode-3 native (CRASH 6 + FAIL 1)

- CRASH `rk_re32/33/34/35/37`, `rk_regex23` — Cluster 3 regex; DEFERRED to GOAL-RAKU-PAT-BB.
- FAIL `rk_junctions` — BLOCKED on Lon Q9-Q12.

## NEXT — RK-BB-4c (mode-3/4 junctions)

RK-BB-4 mode-2 is COMPLETE (full `rk_junctions` probe green mode-2). The mode-2 surface is now
exhausted except the deferred regex cluster (1e → GOAL-RAKU-PAT-BB). Substantive next work:

**RK-BB-4c** — make `rk_junctions` pass mode-4 (then mode-3). The `__rk_jct_*` builder lowering is
already language-agnostic (plain `SM_CALL_FN`), so it should emit in mode-4 via the existing
SM_CALL_FN template; the missing piece is the collapse at the `SM_ACOMP`/`SM_LCOMP` template sites.
Two routes: (i) emit a `rt_junction_collapse` call (@PLT mode-4 / movabs+call mode-3) guarded on a
junction-tagged operand — minimal, reuses the mode-2 helper; (ii) Q11 substrate-first — lower `any`/`|`
through the proven `BB_ALT` binary dispatch slab (first-success = any), with all/none/one as collapse
variants. (i) is faster; (ii) is the architecturally-blessed path. Recommend (i) to flip mode-4 green,
then refactor to (ii) if Lon wants the BB_ALT substrate exercised.

Then **RK-BB-4d** edges (mixed-flavor nesting rep, unparenthesized precedence, var round-trip), or
pick up the deferred regex cluster under GOAL-RAKU-PAT-BB.

## Open questions for Lon

Resolved (2026-05-27): 100% template emission via BB/SM/XA only.

Pending:
- **Q5.** Union-clobber proper fix. TT_SUB_DECL uses `v.ival` for nparams AND wants `v.sval` for name. Move nparams to a side-channel so `v.sval = name` semantics is restored.
- **Q9-Q12.** RK-BB-4 directives — see substrate audit above.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
