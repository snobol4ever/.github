# GOAL-UNIFIED-BROKER.md — One Byrd Box Broker for All Five Languages

**Repo:** one4all
**Done when:** All five language frontends (SNOBOL4, Icon, Prolog, Snocone, Rebus) share
a single universal Byrd box type (`univ_box_fn` returning `DESCR_t`), a single box node
type (`bb_node_t`), and a single broker entry point (`bb_broker`), with three drive modes
(SCAN, PUMP, ONCE). Cross-language calls work at the IR level. All existing test gates pass.

---

## Motivation

Three brokers exist today, evolved separately:

| Language | Broker | Value type | Box fn type | Drive mode |
|----------|--------|------------|-------------|------------|
| SNOBOL4 | `stmt_exec.c` Phase 3 | `spec_t` (16 bytes) | `bb_box_fn` = `spec_t(*)(void*,int)` | SCAN: try positions 0..Ω |
| Icon | `icon_gen.c` `icn_broker` | `DESCR_t` (16 bytes) | `icn_box_fn` = `DESCR_t(*)(void*,int)` | PUMP: call body_fn per value |
| Prolog | `pl_broker.c` `pl_exec_goal` | `spec_t` (boolean only) | `bb_box_fn` | ONCE: α only, OR-box retries |

Key facts:
- `spec_t` and `DESCR_t` are both 16 bytes — same ABI, same registers (rax:rdx).
- The four-signal model (α/β/γ/ω) is identical across all three.
- `DESCR_t` strictly subsumes `spec_t`: a substring match is `DT_S` with `.s`/`.slen`.
- Unifying to one type dissolves the language boundary: a SNOBOL4 pattern box and an
  Icon generator box are the same thing to the broker. Cross-language calls fall out
  naturally once the type barrier is gone.

Target architecture:

```
                    ┌─────────────────────────────────────┐
                    │           bb_broker()                │
                    │  mode: BB_SCAN | BB_PUMP | BB_ONCE  │
                    └──────────────┬──────────────────────┘
                                   │  univ_box_fn: DESCR_t(*)(void*, int)
                    ┌──────────────┼──────────────────────┐
                    │              │                       │
              SNOBOL4 boxes   Icon boxes            Prolog boxes
              (27 bb_* fns)   (icn_bb_* fns)        (pl_box_* fns)
```

---

## Steps

### Phase 1 — Define the universal type in bb_box.h (no code changes yet)

- [ ] **U-1** — Add `univ_box_fn` typedef to `bb_box.h`.
  ```c
  typedef DESCR_t (*univ_box_fn)(void *zeta, int entry);
  ```
  Add `BrokerMode` enum:
  ```c
  typedef enum { BB_SCAN, BB_PUMP, BB_ONCE } BrokerMode;
  ```
  Keep `bb_box_fn` (`spec_t` return) and `icn_box_fn` (`DESCR_t` return) as deprecated
  aliases — no callers changed yet. Header compiles clean.
  Gate: `make scrip` clean; `bash test/smoke.sh` passes.

- [ ] **U-2** — Add `descr_from_spec(spec_t s)` and `spec_from_descr(DESCR_t d)` converters.
  ```c
  static inline DESCR_t descr_from_spec(spec_t s) {
      if (spec_is_empty(s)) return FAILDESCR;
      return (DESCR_t){ .v = DT_S, .slen = (uint32_t)s.δ, .s = s.σ };
  }
  static inline spec_t spec_from_descr(DESCR_t d) {
      if (d.v != DT_S || !d.s) return spec_empty;
      return spec(d.s, (int)d.slen);
  }
  ```
  Gate: `make scrip` clean; smoke passes.

---

### Phase 2 — Implement `bb_broker` alongside the three existing brokers

- [ ] **U-3** — Add `bb_broker()` to a new file `src/runtime/x86/bb_broker.c`.
  Signature:
  ```c
  int bb_broker(bb_node_t root, BrokerMode mode,
                void (*body_fn)(DESCR_t val, void *arg), void *arg);
  ```
  Three modes:
  - `BB_SCAN`: scan Δ=0..Ω; call `root.fn(root.ζ, α)`; on γ: body_fn + break; advance scan.
    Mirrors Phase 3 of `stmt_exec.c` exactly.
  - `BB_PUMP`: call `root.fn(root.ζ, α)`; on γ: body_fn; β-loop until ω.
    Mirrors `icn_broker` exactly.
  - `BB_ONCE`: call `root.fn(root.ζ, α)`; on γ: body_fn once; done.
    Mirrors `pl_exec_goal` exactly.
  Returns tick count (values/matches produced).
  Root fn called via `univ_box_fn` cast — caller is responsible for box type match.
  Gate: `make scrip` clean; smoke passes. (No callers yet — just compilation.)

- [ ] **U-4** — Write a self-contained unit test in `test/test_bb_broker.c`.
  Build three hand-wired boxes (one per mode), drive with `bb_broker`, assert tick counts.
  No frontends involved — pure broker test.
  Gate: `gcc test/test_bb_broker.c src/runtime/x86/bb_broker.c ... && ./a.out` exits 0.

---

### Phase 3 — Convert SNOBOL4 boxes to return DESCR_t

- [ ] **U-5** — Convert `bb_box_fn` typedef in `bb_box.h` to return `DESCR_t`.
  Before: `typedef spec_t (*bb_box_fn)(void *zeta, int entry);`
  After:  `typedef DESCR_t (*bb_box_fn)(void *zeta, int entry);`
  This is the breaking change. All 27 `bb_*` functions in `bb_boxes.c` must be updated.
  Internal box state (`seq_t.matched`, `arbno_frame_t`, etc.) that stores `spec_t`
  for cursor bookkeeping stays as `spec_t` — those are internal, not return values.
  Return sites: `return spec(...)` → `return descr_from_spec(spec(...))`.
  Return sites: `return spec_empty` → `return FAILDESCR`.
  Phase 3 in `stmt_exec.c`: reads result as `spec_t` today — switch to `spec_from_descr()`.
  Gate: `make scrip` clean; `bash test/smoke.sh` passes; `bash test/regression.sh` non-regressing.

- [ ] **U-6** — Update `bb_boxes.s` (assembly boxes) to return `DESCR_t`.
  The assembly boxes (`bb_atp`, `bb_nv_set`, `bb_nv_get` etc.) return via rax:rdx.
  `spec_t` layout: rax=σ ptr, rdx=δ int.
  `DESCR_t` layout: rax=low qword {v,slen}, rdx=high qword {s or i}.
  Update each asm box return sequence to pack `DESCR_t` correctly.
  Gate: `make scrip` clean; smoke + regression non-regressing.

---

### Phase 4 — Unify icn_box_fn and Pl_GoalBox into bb_node_t

- [ ] **U-7** — Retire `icn_box_fn` / `icn_gen_t` — replace with `bb_box_fn` / `bb_node_t`.
  In `icon_gen.h`: `icn_box_fn` → `bb_box_fn`; `icn_gen_t` → `bb_node_t`.
  In `icon_gen.c`: update all box constructors to return `bb_node_t`.
  `icn_broker` now calls `bb_broker(root, BB_PUMP, body_fn, arg)` internally — or is
  replaced by a thin wrapper around `bb_broker`.
  Gate: `make scrip` clean; Icon rung01-11 59/59 PASS.

- [ ] **U-8** — Retire `Pl_GoalBox` — replace with `bb_node_t`.
  In `pl_broker.h`: `Pl_GoalBox` → `bb_node_t`; `.fn`/`.zeta` field names already match.
  `pl_exec_goal` now calls `bb_broker(root, BB_ONCE, NULL, NULL)` — returns 1 if ticks>0.
  Gate: `make scrip` clean; Prolog regression non-regressing.

---

### Phase 5 — Wire `bb_broker` as the single call site in all three paths

- [ ] **U-9** — Replace Phase 3 in `stmt_exec.c` with `bb_broker(root, BB_SCAN, ...)`.
  The scan body_fn extracts match start/end from the `DESCR_t` val via `spec_from_descr`.
  Remove the inline scan loop from `stmt_exec.c`.
  Gate: `make scrip` clean; full regression non-regressing; crosscheck passes.

- [ ] **U-10** — Replace `icn_broker` call sites in `scrip.c`/`icon_gen.c` with `bb_broker(..., BB_PUMP, ...)`.
  Remove `icn_broker` function entirely.
  Gate: `make scrip` clean; Icon 59/59 PASS.

- [ ] **U-11** — Replace `pl_exec_goal` call sites with `bb_broker(..., BB_ONCE, ...)`.
  Remove `pl_exec_goal` function entirely (or keep as one-line wrapper if callers are many).
  Gate: `make scrip` clean; Prolog regression non-regressing.

---

### Phase 6 — Cross-language calls

- [ ] **U-12** — Prove cross-language call at IR level: SNOBOL4 pattern calls Icon generator.
  Write a test in `test/test_cross_lang.c`: build an Icon `icn_bb_to` box (1 to 3),
  drive it with `bb_broker(..., BB_PUMP, ...)` from SNOBOL4 context. Assert 3 ticks.
  No new IR nodes needed — this is a direct box construction test.
  Gate: test compiles and exits 0.

- [ ] **U-13** — Prove cross-language call at IR level: Prolog goal drives SNOBOL4 pattern.
  Write a test: build a `bb_lit` box, drive it with `bb_broker(..., BB_ONCE, ...)`.
  Assert 1 tick on match, 0 on mismatch.
  Gate: test compiles and exits 0.

- [ ] **U-14** — Update PLAN.md: add this goal to Active Goals table.
  Update `ARCH-IR.md` or `ARCH-x86.md` to document the unified broker.
  Gate: none — documentation only.

---

## Key files

| File | Role |
|------|------|
| `src/runtime/x86/bb_box.h` | `univ_box_fn`, `BrokerMode`, `bb_node_t`, converters — extended |
| `src/runtime/x86/bb_broker.c` | NEW — `bb_broker()` implementation |
| `src/runtime/x86/bb_boxes.c` | 27 SNOBOL4 boxes — return type `spec_t` → `DESCR_t` |
| `src/runtime/x86/bb_boxes.s` | Assembly boxes — return layout updated |
| `src/runtime/x86/stmt_exec.c` | Phase 3 → calls `bb_broker(..., BB_SCAN, ...)` |
| `src/frontend/icon/icon_gen.h` | `icn_gen_t` → `bb_node_t`; `icn_box_fn` → `bb_box_fn` |
| `src/frontend/icon/icon_gen.c` | `icn_broker` → thin wrapper or removed |
| `src/frontend/prolog/pl_broker.h` | `Pl_GoalBox` → `bb_node_t` |
| `src/frontend/prolog/pl_broker.c` | `pl_exec_goal` → calls `bb_broker(..., BB_ONCE, ...)` |
| `test/test_bb_broker.c` | NEW — unit test for bb_broker all three modes |
| `test/test_cross_lang.c` | NEW — cross-language box composition tests |

---

## Invariants — never break these

- Every step must leave `make scrip` clean (zero errors, zero warnings).
- Smoke gate (`bash test/smoke.sh`) must pass after every step.
- Regression score must not drop after U-5 (the breaking change).
- Internal box state (`seq_t.matched`, `arbno_frame_t.matched`, etc.) may stay `spec_t` — these are private. Only return values and the broker ABI change.
- `Σ/Δ/Ω` globals are unchanged — SNOBOL4 cursor arithmetic is internal to boxes and Phase 3.
- Assembly boxes (bb_boxes.s) must be updated in the same commit as bb_boxes.c (U-6 comes immediately after U-5).

---

## Rules
- Commit identity: LCherryholmes / lcherryh@yahoo.com.
- Build gate: `make scrip` clean + smoke + regression non-regressing after every step.
- One step per commit. Gate before committing.
- Follow RULES.md naming conventions: new C functions in `snake_case`, new types `Xxxx_yyy`.
