# HANDOFF-2026-06-13-OPUS48-RAKU-BB-CLASS-METHOD-M3-LANDED.md

## Session: GOAL-RAKU-BB — `class_method` m3 freed-IR fix + class-only m4 robustness; clean checkpoint

**SCRIP HEAD at open: `9baaf64`. At close: `a6f9d65` (2 code commits landed; clean rebases over peer
commits `9c524af` and `e089608`). `.github` at close: `590cd4dd` (watermark current + GROUP A blocker
corrected + this doc).**

**Gates at close — Raku m2 31/31 (HARD ✓); m3 26 PASS / 0 FAIL / 5 EXCISED; m4 26 PASS / 0 FAIL /
5 EXCISED.** Peers invariant: Icon m2/m3/m4 = 12/12/12, SNOBOL4 m2 7/7 (HARD ✓), NFA oracle 5/5,
`g_vstack`=0. The only EXCISED = GROUP A (gather_take / map_range / grep_range / map_over_gather /
grep_over_gather). Concurrency audit = 5 VIOLATIONs (the documented pre-existing FACT-RULE md5 drift +
stale `src/lower/lower.c` path baseline — identical stash-clean vs change, NOT introduced this session).

---

## LANDED 1 — commit `738b950` (+16 lines, 3 runtime files): `class_method` m3 EXCISED→PASS

Session 9 (prior) had landed the full `class_method` EMIT path (FIELD_GET template, obj_new N-ary operand
marshalling, the gate admitting `IR_CALL dval==1.0` + `IR_FIELD_GET` as ASSIGN rhs, m4 class-registration,
meth_call m4 dispatch), and **m4 already PASSed**. But m3 (`--run`) still exited silently after the first
two `say`s — it printed `3\n4` then stopped.

**ROOT CAUSE (a freed-IR read, NOT an emit bug).** In `script_try_call_builtin_by_name`'s `meth_call` arm
(`src/runtime/by_name_dispatch.c` ~1411): when the resolved method name (`Point__sum` etc.) IS found in
`g_stage2.proc_table` with `bb_idx >= 0`, the code unconditionally took the `rk_ir_call_proc(pi, …)` path —
which runs `IR_interp_once(fg)` over the IR graph (the mode-2 interpreter). In m3, `ir_delete_all(s2)` has
ALREADY physically freed every `IR_t` before the native `main` runs (the IR-NEVER-TOUCHED tripwire,
2026-06-13), so `rk_ir_call_proc` walked freed memory → silent corrupt exit at the first method call
(`$p.sum()`). m4 dodged this only because its standalone binary never calls `lower_stage2`, so
`g_stage2.proc_count == 0` → `pi >= proc_count` → it already fell through to the native `rt_call_proc_descr`
path (session 9's fix #6).

**FIX — prefer the native slab whenever one is registered.**
- New `int rt_proc_has_native_fn(const char *name)` in `src/runtime/rt/rt.c` (declared in `rt.h`): returns 1
  iff the proc is in `g_rt_gen_procs[]` with a non-NULL `fn`. Mirrors `rt_proc_is_registered` but checks the
  fn pointer, not mere presence.
- In the `meth_call` `bb_idx >= 0` arm: `if (rt_proc_has_native_fn(procname)) { stage args into g_call_args[];
  *out = rt_call_proc_descr(procname, total); return 1; }` BEFORE the `rk_ir_call_proc` fallback.
- Net: **m2** — no native fn registered → `rk_ir_call_proc` (interpreter, IR live) → correct & unchanged.
  **m3** — native fn registered → `rt_call_proc_descr` (native, IR-free) → no freed-IR read → fixed.
  **m4** — never reaches this branch → unchanged.

**WIN-WIN (shared-runtime fix, like session-8's Layer B).** `rt_proc_has_native_fn` lives in the shared
runtime, so ANY language whose post-`ir_delete_all` dispatch could route a registered native proc back into
`rk_ir_call_proc` is now protected — the native slab wins over the freed IR by construction. (Today only
`meth_call` reaches that path.)

**Compliance:** no templates, no IR/AST walking on the run path, no value stack, no language guards — clean
against all the FACT RULES. **Mechanism proof:** `/tmp/class_method.raku` (the smoke body) →
`3 4 7 14 Rex Woof from Rex` in BOTH m3 (`--run`) and m4 (`--compile` → `gcc -no-pie … -Lout -lscrip_rt`).

**Files:** `src/runtime/rt/rt.h` (decl), `src/runtime/rt/rt.c` (`rt_proc_has_native_fn`),
`src/runtime/by_name_dispatch.c` (`meth_call` native-fn priority).

---

## LANDED 2 — commit `a6f9d65` (+4/−2 in `src/driver/scrip.c`): class-only m4 (robustness item #1)

A class-only Raku program (classes declared but NO `sub`/`main` body proc) printed nothing in m4 while m2/m3
printed correctly. CAUSE: the m4 `record_register(...)` class-registration loop AND the `call
icn_proc_startup` were both nested inside `if (n_procs > 0)`, so a zero-proc program got an EMPTY dat registry
in its standalone binary → `Point.new` failed → no output. FIX: compute `n_cls_emit = dat_type_count()` up
front; gate the `icn_proc_startup` emission block + its call on `(n_procs > 0 || n_cls_emit > 0)`; the
proc-fn-registration loop keeps its own internal `n_procs` guard (so the class loop runs whenever classes
exist, independent of procs).

**Proven across all four cases:**
- Raku class-only, no sub (`n_procs==0`, `n_cls>0`): now prints `3 4` in m4 (matches m2/m3) — the gap closed.
- Icon procs, no classes (`n_procs>0`, `n_cls==0`): startup still emitted + called, ZERO spurious
  `record_register`, runs → `42`.
- Raku class with methods (`n_procs>0`, `n_cls>0`): `class_method` unchanged.
- Neither: both halves of the OR are 0 → no startup, byte-identical to before.

**File:** `src/driver/scrip.c`.

---

## DOC — `.github` `590cd4dd`: GROUP A blocker corrected (probed, not trusted)

The watermark previously said GROUP A was "blocked on Icon GZ-7 (IR_ASSIGN ζ-slot store)." I PROBED the
actual failure (`for map {$_*2} 1..3 -> $v` — m2 prints 2/4/6/done; m3 prints the `[SMX] … no MEDIUM_BINARY
arm — EXCISED` banner) and found the PRIMARY blocker is different: `IR_MAP`/`IR_GREP`/`IR_GATHER` have NO
`bb_rk_map.cpp`/`bb_rk_grep.cpp` MEDIUM_BINARY template at all, so `icn_graph_native_emittable` EXCISES the
whole program at the `[SMX] --run` gate BEFORE emit. That is the RK-EMIT-MAP/GREP rung. The Icon named-slot
store the loop variable `$v` would need is a SECONDARY dependency, and the named-slot law itself already works
for plain Icon assigns (`febef10`: `x:=42;write(x)` m2==m3==m4; GOAL-ICON-BB GZ ladder shows GZ-0…GZ-SCAN
DONE). **Conclusion: GROUP A == RK-EMIT-MAP/GREP. Do them together in a fresh session.** Watermark NEXT-list
line updated accordingly.

---

## PRE-EXISTING BASELINES (verified NOT introduced this session — do not chase)

- **SNOBOL4 `define` m3/m4 6/1** — owned by the SNOBOL4 DEFINE-CARVE session, not this Raku work. Confirmed
  IDENTICAL on a `git stash` clean rebuild. SNOBOL4 m2 stays 7/7 HARD.
- **`audit_concurrency_invariants.sh` = 5 VIOLATIONs** — LOWER+EMITTER FACT-RULE block md5 drift in
  GOAL-ICON-BB / GOAL-PROLOG-BB + a stale `src/lower/lower.c` path the audit greps for. Identical
  baseline-vs-change.
- **`prove_lower.sh` = "0 cases — DEAD GATE"** pending NL-shaped prove-case authoring (IR-REDESIGN era;
  `prove_lower2.sh` referenced in the goal file is not present in this checkout).
- **`util_template_purity_audit.sh` = 1 site** in `bb_call_write_slot.cpp` (a SNOBOL4/Icon box; untouched).

---

## ORDER OF WORK for next session (fresh budget recommended for any of these)

1. **GROUP A == RK-EMIT-MAP/GREP (large rung).** Write `bb_rk_map.cpp` / `bb_rk_grep.cpp`: closure emitted as
   native, invoked per element, driven by the Icon generator PUMP (SUSPEND/EVERY). The loop var `$v` stores
   to a ζ-slot via the already-working named-slot law. When the templates land, remove `IR_MAP`/`IR_GREP`/
   `IR_GATHER` from `icn_kind_native_stub` (the EXCISE gate) and expect m3/m4 to go 31/31. This unblocks all 5
   GROUP A tests at once (gather_take/map_range/grep_range/map_over_gather/grep_over_gather).
2. **RK-GRAM-3 (THE SEAM, large rung)** — subrule `<name>` backtracking via the generator PUMP; resume-and-
   yield-next across the subrule call boundary; Match-tree build. Routes through IR_* SUSPEND/ALT/PUMP (exist).
3. **Minor non-blocking follow-ups (do NOT do unless in lane):** the `gvar_chain` postfix loop
   (`emit_bb.c` ~3370) N-ary generalization is in the SHARED SNOBOL4/Icon emitter path (out of Raku lane, no
   Raku test — leave to the owning session); the `rt_proc_has_native_fn` guard generalization has no second
   call site today (no-op).

## Session Setup (unchanged)

```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
rm -f scrip && make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_raku.sh      # m2 31/31 HARD; m3 26/0/5; m4 26/0/5
bash scripts/test_smoke_icon.sh      # 12/12/12 HARD
bash scripts/test_smoke_snobol4.sh   # m2 7/7 HARD (define m3/m4 6/1 = peer baseline)
bash scripts/test_gate_raku_nfa_oracle.sh   # 5/5
```

## Commits this session (all pushed + verified on origin/main)

| Commit | Repo | What |
|---|---|---|
| `738b950` | SCRIP | meth_call m3 prefers native slab over rk_ir_call_proc when registered — class_method EXCISED→PASS |
| `a6f9d65` | SCRIP | class-only m4 — register classes at startup even with zero procs |
| `f750d1dd` → `590cd4dd` | .github | watermark current; GROUP A blocker corrected; this handoff doc |
