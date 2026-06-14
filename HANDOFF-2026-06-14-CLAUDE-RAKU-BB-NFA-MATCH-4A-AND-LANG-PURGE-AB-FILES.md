# HANDOFF 2026-06-14 — Raku IR_NFA_MATCH stage-4a + language-prefix purge (Groups A/B/FILES)

## ⚠ PUSH NOT COMPLETED — committed locally, NOT on origin/main. FIRST TASK NEXT SESSION.

Both repos have a local commit that is **committed but unpushed**:
- **SCRIP**: `c17130d` (HEAD, local only). `origin/main` is **18 commits ahead** (peer "scan flip" `bd5f614` + Prolog PL-BB-5 + emit_bb FIXUPs).
- **.github**: `84017cd6` (local). Push it LAST, after SCRIP, per RULES.md.

`git pull --rebase origin main` on SCRIP **conflicts in 3 files** — all files my rename touched that the
peer's scan-dispatch refactor also touched:
- `src/contracts/scrip_ir.c` — I added `IR_NFA_MATCH` to the name table + the `bb_reset` counter-preserve
  exemption list. Peer likely touched nearby. RESOLVE: keep BOTH — my `[IR_NFA_MATCH]` name-table entry and
  my `&& bb->op != IR_NFA_MATCH` in the `bb_reset` counter-zero guard, merged with whatever peer added.
- `src/driver/scrip.c` — I (a) renamed all `icn_*`→CS-neutral (Group A), (b) added the `IR_NFA_MATCH` EXCISE
  guard `if (nd->op == IR_NFA_MATCH) return 0;` at the top of `graph_native_emittable_mode`'s node loop, (c)
  admitted `IR_NFA_MATCH` in `rhs_kind_ok` + `assign_safe_kind`. Peer touched scan dispatch. **CONFLICT RISK:
  the peer may still use the OLD `icn_*` names** — after merge, re-apply the Group-A rename over any peer code
  that reintroduced `icn_*` (grep `icn_` in driver must be 0).
- `src/emitter/emit_bb.c` — I renamed `icn_arg_entry_terminal`/`icn_subchain_node_is_generator`→neutral and the
  emitted asm label `icn_proc_%s`→`proc_%s`. Peer did the big scan-kind dispatch FIXUPs here (`078b901`,
  `edba4d9`). **Heaviest conflict.** RESOLVE by taking peer's scan-dispatch logic AND re-applying my 2 symbol
  renames + the `proc_%s` label rename on top.

### Recommended resolution procedure (full budget)
1. `cd /home/claude/SCRIP && git pull --rebase origin main`
2. For each conflict: take the peer's logic as the base, then re-apply my edits (they are *renames* + 3 small
   `IR_NFA_MATCH` additions — mechanical to layer back on). The semantic intent of my changes:
   - Group A rename: ANY `icn_*` in driver/emitter → CS-neutral (mapping in the GOAL watermark "LANGUAGE-PREFIX
     PURGE" block). After resolving, `grep -rn 'icn_' src/driver src/emitter` MUST be 0.
   - `IR_NFA_MATCH`: enum (IR.h — unlikely to conflict), name table + bb_reset exemption (scrip_ir.c), EXCISE
     guard + rhs/assign admit (scrip.c). m2 arm (IR_interp.c — unlikely to conflict). Lowering (lower_raku.c —
     unlikely to conflict).
3. `git rebase --continue`; rebuild BOTH (`rm -f scrip && make -j4 scrip && make libscrip_rt`).
4. Re-run ALL gates (see below) — they MUST be green before push.
5. **Auth for push**: the remote needs the token. Use:
   `git push https://<TOKEN>@github.com/snobol4ever/SCRIP main` (or set `git remote set-url origin` with the
   token). Same for `.github`. (This session the bare `git push origin main` failed: "could not read Username".)
6. Push SCRIP first, then `.github`. Confirm: `git log origin/main --oneline -1` shows your hash in each.

### Gate suite (must be green before push)
```bash
cd /home/claude/SCRIP
rm -f scrip && make -j4 scrip && make libscrip_rt
bash scripts/test_gate_raku_nfa_oracle.sh      # 5 PASS lines
bash scripts/test_smoke_raku.sh                # m2 35/35 HARD; m3 35/35; m4 35/35
bash scripts/test_smoke_icon.sh                # m2 12/12 HARD
bash scripts/test_smoke_snobol4.sh             # m4 7/7 HARD
grep -rho g_vstack src/ | wc -l                # 0
```

---

## What this commit contains (all VERIFIED green at commit time, pre-rebase)

### 1. Stage-4a `IR_NFA_MATCH` foundation (RK-NFA-4 stage 4a) + verdict-bug fix
- New IR kind `IR_NFA_MATCH` (IR.h after `IR_NFA_ACCEPT`; name table in scrip_ir.c).
- `lower_raku.c` `TT_SMATCH` value arm: `~~ /literal/` mode `"match"` with a `TT_QLIT` pattern now builds
  `raku_nfa_build(pat)` + `raku_nfa_to_bb(nfa)` at LOWER time and emits `IR_NFA_MATCH` carrying: the `Raku_nfa*`
  in `IR_LIT.ival` (for the `RK_NFA_BB=0` oracle arm + group names) and a 2-entry `IR_EXEC.counter` block array
  `{subject_arg_block, pre-built bbg}`. Non-literal / `match_global` / `subst` fall through UNCHANGED to
  `re_match`.
- `IR_interp.c` m2 arm (in `IR_interp_node`): honors `RK_NFA_BB` exactly like `re_match` — env 0 →
  `raku_nfa_exec`, env 1 → `raku_nfa_bb_graph_exec(bbg, ngroups, subj, &g_raku_match)`. Returns γ on match
  (value INTVAL(1)), ω on no-match. Added `#include "../../parser/raku/raku_re.h"`.
- `raku_nfa_bb.c` + `raku_re.h`: factored `raku_nfa_bb_exec(nfa,...)` into a thin wrapper over new
  `raku_nfa_bb_graph_exec(IR_graph_t* bbg, int ngroups, subj, *result)` — oracle behavior byte-identical (the
  nfa wrapper builds the graph then delegates).
- `scrip.c`: m3/m4 EXCISE guard `if (nd->op == IR_NFA_MATCH) return 0;` at the top of
  `graph_native_emittable_mode`'s node loop (was `icn_graph_native_emittable_mode`); `IR_NFA_MATCH` admitted in
  `rhs_kind_ok` + `assign_safe_kind`.
- **THE BUG (fixed):** `bb_reset` (scrip_ir.c) zeroes `IR_EXEC(counter)` for every node except an exemption
  list. `IR_NFA_MATCH` stores its compile-time block-array pointer in `counter`, so `bb_reset` on the condition
  arg-block wiped it → `blks==NULL` → match always FAILed (`'abc123' ~~ /\d+/` wrongly falsy). The oracle gate
  could NOT see this — it only self-compares the RK_NFA_BB=0 vs =1 arms, which were identically wrong. FIX:
  added `&& bb->op != IR_NFA_MATCH` to the `bb_reset` counter-preserve guard. Verified `~~` verdict correct on
  BOTH arms after the fix.
- **GAP (queued as RK-NFA-4a-SMOKE):** the smoke harness has NO `~~` test, so the harness does not guard the m2
  verdict — only the (self-comparing, blind-to-correctness) oracle gate does. Add a `smatch_verdict` smoke next.

### 2. Language-prefix purge — runtime/post-lower must be language-AGNOSTIC (by directive)
Prefixes allowed ONLY in `src/parser/` + `src/lower/`. Everything after lower = CS terminology, no lang tag.
- **Group A (driver+emitter `icn_*`→neutral, 33 syms):** `icn_graph_native_emittable[_mode]`→
  `graph_native_emittable[_mode]`, `icn_rhs_kind_ok`→`rhs_kind_ok`, `icn_assign_safe_kind`→`assign_safe_kind`,
  `icn_scan_*`/`icn_alt_*`/`icn_keyword_*`/`icn_gen_scan_*`→drop `icn_`, `icn_rk_*`→`{arith_operand_ok,
  bool_cond_emittable,bool_truthy_emittable,is_jct_call,jct_marshallable}`, `icn_ring_to_tree`→`ring_to_tree`,
  `icn_rt_arity`→`node_arity`, `icn_root`→`root_node`, emitted asm label `icn_proc_*`→`proc_*` (in BOTH scrip.c
  AND emit_bb.c — must stay byte-identical for the generated .s to link).
- **Group B (interp+runtime `rk_*`/`raku_*` helpers→neutral):** `rk_ir_call_proc`→`ir_call_proc`,
  `rt_rk_is_truthy`→`rt_is_truthy` (incl. emitted `@PLT` symbol in the bool template), `rk_is_truthy`→
  `descr_is_truthy`, `rk_seq_cache_*`/`g_rk_seq_cache*`/`RK_SEQ_CACHE_MAX`→`seq_cache_*`/`g_seq_cache*`/
  `SEQ_CACHE_MAX`, `rk_write_str/descr`→`out_write_str/descr`.
- **RENAME-FILES:** `bb_rk_mapgrep.cpp`→`bb_mapgrep.cpp`, `bb_call_rk_bool.cpp`→`bb_call_bool.cpp` (git mv);
  symbols `bb_rk_mapgrep[_prepare]`→`bb_mapgrep[_prepare]`, `bb_call_rk_bool*`→`bb_call_bool*`,
  `rk_is_jct_call`→`is_jct_call`; Makefile RT_PIC_SRCS + compile rules + `.o` names + diagnostic strings.

### Deliberately LEFT (recorded, not done)
- `__rk_bool` / `__rk_try` / `__rk_jct_*` **builtin-name STRINGS** — these are the lowerer's value-level
  vocabulary matched by `try_call_builtin_by_name` in the runtime (a lower↔runtime *contract*, like an opcode
  name), not file/symbol names. Renaming them is a separate coordinated lower+runtime edit. Queue if wanted.

## Remaining language-prefix queue (GOAL ladder `- [ ]`)
- **RENAME-C** — the NFA/regex engine (`raku_nfa_*`/`Raku_nfa`/`Raku_match`/`g_raku_match`/`g_raku_subject`/
  `raku_re*` → `nfa_*`/`re_*`/`Match`/`g_match`/`g_subject`). Runtime-invoked, ~6 files incl. `raku_re.h`, NOT
  asm-emitted. One commit; gate `test_gate_raku_nfa_oracle.sh` 5/5. (The meatiest; do with full budget.)
- **RENAME-SNO** — `scrip.c` EMITTED labels only (`sno_proc_startup`/`sno_flat`/`.Lsno_*`/`sno_pidx_buf`).
  DO NOT touch `sno_parse_ast`/`sno_add_include_dir` (parser entry points). Audit `pl_*`/`pas_*` emitter labels.
- **RK-NFA-4a-SMOKE** — add a `~~` verdict test to the smoke harness.

## Session Setup (next session)
```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
# FIRST: resolve the rebase + push (see top). THEN normal work.
rm -f scrip && make -j4 scrip && make libscrip_rt
```
