# GOAL-RAKU-BB.md — Raku: goal-directed ~20% onto shared BB generators

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
| junctions `any`/`all`/`one`/`none`, infix `\|`/`&` | `BB_ALTERNATE` + Bool-collapse | RK-BB-4 (blocked) |

**STAYS eager SM:** scalar builtins (`uc`/`lc`/`substr`/`trim`/`index`/`rindex`), `say`/`print`, arithmetic, hash/array element ops, class/method dispatch, `sort` (whole-list), `try`/`CATCH`.

**SPLIT OUT to GOAL-RAKU-PAT-BB:** regex / grammar backtracking. Defer until SNOBOL4-BB and PROLOG-BB land more rungs.

## ⛔ Rules

- No C Byrd boxes; no SM/BB walking at runtime in modes 3/4; ports are α/β/γ/ω; X86 arms only.
- No `rt_*`/`raku_*` port-logic helpers. Conversion/effect helpers via `@PLT` are fine.
- **No language sniffing in SM/BB/XA templates.** No `g_lang`/`LANG_*`/`rk_sub_*` branches inside template bodies. Per-language behavior lives in the lowering (choose which SM opcode to emit). Templates emit one fixed sequence per opcode.

## Completed rungs (terse)

- **RK-BB-1** ✅ — `for $a..$b -> $i` → `BB_TO_BY`.
- **RK-BB-2** ✅ — KEYSTONE lazy `Seq`. `gather`/`take` + `…` → `BB_SUSPEND`+`BB_EVERY` PUMP. REUSE `bb_upto.cpp`.
- **RK-BB-3** ✅ — lazy `map`/`grep` as Seq CONSUMERS (eager-drain materialization). 3.0+3a/3b/3c/3d sub-steps all green.
- **RK-BB-SEGFAULT-CLUSTER** ✅ — 4 bugs: polyglot union-clobber, multi-sub structure (lower_stmt/lower_proc_skeletons/build_proc_scope for TT_SUB_DECL), and Raku `lower_return` value preservation.
- **RK-BB-SM-FRAME-MODE4** ✅ — Mode-4 named-sub frame slots: `rt_frame_enter/leave/load/store` in libscrip_rt; SM_LOAD/STORE_FRAME x86 templates.
- **RK-GIVEN-MODE4** ✅ — `given`/`when` rewritten as if-chain over already-templated opcodes (no SM_PUMP_CASE, no thunks).
- **RK-HASH** ✅ — hash builtins (set/get/exists/keys/values/pairs/delete), SOH/STX encoding; polyglot TT_FNC skip fix; SSE alignment fix; stale-frame writeback; rt_acomp string coercion.
- **RK-NAMED-CALL** ✅ (Opus 4.7, 2026-05-28) — **template-pure restoration** of Raku user-sub dispatch after LANG-IGNORANT-SM-TEMPLATES whacked the `rk_sub_lookup` fast-paths. New language-ignorant `SM_NAMED_CALL` opcode (a[0].s=name, a[1].i=nparams) emits `mov edi,nparams; call rt_frame_enter@PLT; call .Lsub_<name>; call rt_frame_leave@PLT`. `sm_label_str` MEDIUM_TEXT now emits `.Lsub_<name>:` symbol when `a[0].s` non-empty (no language gate — named labels emit symbols, that's all). `lower_fnc` for LANG_RAKU emits SM_NAMED_CALL when callee matches a TT_SUB_DECL in proc_table (excluding main/__gather_*). Templates contain zero `g_lang` references. GATE-RK4 restored 17→22.
- **RK-EXCEPTIONS** ✅ (Claude Sonnet 4.6, 2026-05-28, one4all `ed6fec27`) — try/CATCH/die mode-4. Added `raku_exc_clear`, `raku_exc_check`, `raku_exc_get` to `raku_try_call_builtin_by_name` (were referenced by lower.c but never implemented in the rt path). Fixed `raku_die` to use SSE-safe `memcpy` instead of `snprintf` (Q13a). Fixed `raku_try_hash_builtin` to guard `args[0].v == DT_S` before `VARVAL_fn` — was segfaulting when `say(integer)` called inside any sub that had a `my`-decl (hash builtin check was passing integers to `VARVAL_fn` → `snprintf` on garbage pointer). GATE-RK4 22→23, GATE-RK 20→21.

## Open rungs

- [~] **RK-BB-4 substrate audit** — Probe-based audit found goal text's "REUSE bb_gen_alt.cpp/bb_alt.cpp" is unfounded. Seven gaps: lex (no KW_ANY/ALL/ONE/NONE, no single `|`/`&`); TT_ALT overloaded with SNOBOL4 pat-alt; bb_exec.c BB_ALTERNATE mode-2 is no-op; bb_alternate.cpp mode-4 missing; bb_alt.cpp mode-4 stub; bb_gen_alt.cpp stub; Icon TT_ALTERNATE lowers to BB_ALT not BB_ALTERNATE → **BB_ALTERNATE is orphan; reusable substrate is BB_ALT (mode-4 stub)**. `test/raku/rk_junctions.{raku,expected}` committed as probe (`4ee45eb7`); fails at lex.

  **Open Qs for Lon (Q9-Q12, gating any work):**
  - Q9: New TT_LOR/TT_LAND for Raku `||`/`&&` to disentangle from SNOBOL4 patterns?
  - Q10: BB_ALT (n-ary, mode-4 stub) or finish orphan BB_ALTERNATE? Recommend BB_ALT.
  - Q11: Substrate-first or frontend-first? Recommend frontend-first (path b).
  - Q12: Junction value rep: (i) tagged string mirroring `\x01`-arrays, (ii) DT_JUNCT, (iii) DT_DATA. Recommend (i).

- [ ] **RK-BB-4-frontend** — pending Q9-Q12.
- [ ] **RK-BB-5..N** — `reverse`/`tail`/`from-loop` as Seq consumers; `zip`/`cross` = multi-Seq drivers (later).

## Rung methodology

Per rung: (1) lower the Raku construct to the shared BB kind via `lower_raku_*` (parallel `lower_icn_*`); (2) confirm existing `bb_<kind>.cpp` covers it; (3) only if semantics differ, **extend the lowering** — never the template — to match; (4) run GATE-RK4 + GATE-RK (mode-2) + smoke. Commit when goldens match and nothing regresses.

## Test corpus — REUSE

`test/raku/*.{raku,expected}` (33 cases). Job is mode-4 conformance (Prolog GATE-4 pattern). Add NEW flat files only for laziness probes the eager suite can't express.

## Mode-3 (`--run`)

RULES.md sanctions one temporary SM-walk exception (Prolog `--run`, AGW-1c). Do NOT route Raku `--run` through `sm_interp_run` without a Lon directive. Mode-4 is this ladder's target.

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
```

## Gates

```
GATE-RK    test_raku_ir_rungs.sh        # mode-2, must hold/improve
GATE-RK4   test_raku_mode4_rung.sh      # mode-4 vs .expected, must hold/improve
GATE-RK-SM test_smoke_raku.sh           # smoke must hold
```

## Watermark

```
one4all: RK-EXCEPTIONS (try/CATCH/die mode-4; GATE-RK4 22->23; ed6fec27)
.github: HEAD
corpus:  unchanged

GATE-RK mode-2:  21/33  +1
GATE-RK4 mode-4: 23/33  +1 (rk_try_catch25)
Smoke raku:      5/5    HOLD
Smoke prolog:    5/5    HOLD
Smoke snobol4:   13/13  HOLD
Smoke icon:      5/5    HOLD
FACT RULE grep:  0
Templates lang-sniffing grep: 0
Build:           clean
```

## Remaining 10 mode-4 FAILs

- REGEX/NFA (6): rk_re32/33/34/35/37, rk_regex23 — DEFERRED to GOAL-RAKU-PAT-BB.
- I/O (2): rk_fileio38, rk_stdio39 — file handles, $*STDOUT/$*STDERR.
- JUNCTIONS (1): rk_junctions — BLOCKED on Lon Q9-Q12.
- CLASS (1): rk_class26 — OOP class/method dispatch.

Best next target: I/O (self-contained).

## Open questions for Lon

Resolved (2026-05-27): 100% template emission via BB/SM/XA only.

Pending:
- **Q5.** Union-clobber proper fix. TT_SUB_DECL uses `v.ival` for nparams AND wants `v.sval` for name. Move nparams to a side-channel so `v.sval = name` semantics is restored.
- **Q9-Q12.** RK-BB-4 directives — see substrate audit above.
- **Q13.** `rk_try_catch25` — for try/CATCH/die mode-4. Per Lon: no language gates in SM/BB/XA templates. Correct path: (a) SSE-safe `raku_die` byname (replace snprintf with manual byte-copy); (b) per-stmt `raku_exc_check` catches at try-body level; (c) `lower_stmt` for TT_DIE emits SM_RETURN after die-payload when `g_in_proc_body` (pure lowering, no template change).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
