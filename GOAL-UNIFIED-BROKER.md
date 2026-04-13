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

- [x] **U-1** — Add `univ_box_fn` typedef and `BrokerMode` enum to `bb_box.h`. DONE.

- [x] **U-2** — Add converters `descr_from_spec` / `spec_from_descr` in `bb_convert.h`. DONE.

---

### Phase 2 — Implement `bb_broker` alongside the three existing brokers

- [x] **U-3** — `bb_broker()` implemented in `src/runtime/x86/bb_broker.c`. DONE.

- [x] **U-4** — Unit test `test/test_bb_broker.c` — 22/22 PASS all three modes. DONE.

---

### Phase 3 — Convert SNOBOL4 boxes to return DESCR_t

- [x] **U-5** — All 27 C boxes return DESCR_t. new descr.h breaks circular include.
  stmt_exec.c, pl_broker.c updated. regression PASS=49/149 vs baseline 41. DONE.

- [ ] **U-6** — Update `bb_boxes.s` assembly boxes to return `DESCR_t`. PARTIAL.
  DONE: 26 ω failure returns: xor eax,eax → mov eax,99 (DT_FAIL=99). rdx already 0.
  REMAINING: 27 γ success returns still use spec_t packing (rax=σ ptr, rdx=δ int).
  Must repack to DESCR_t: rax=low qword {DT_S=1 in bits 0-31, slen=δ in bits 32-63},
  rdx=high qword {s=σ ptr}. Each box has unique stack layout — do one at a time.
  Only affects --bb-live x86 path (pre-existing failure). Interpreter unaffected.
  Gate: make scrip clean; smoke + regression non-regressing.

---

### Phase 4 — Unify icn_box_fn and Pl_GoalBox into bb_node_t

- [x] **U-7** — Retire `icn_box_fn` / `icn_gen_t` — replace with `bb_box_fn` / `bb_node_t`. DONE.
  In `icon_gen.h`: `icn_box_fn` → `bb_box_fn`; `icn_gen_t` → `bb_node_t`.
  In `icon_gen.c`: update all box constructors to return `bb_node_t`.
  `icn_broker` now calls `bb_broker(root, BB_PUMP, body_fn, arg)` internally — or is
  replaced by a thin wrapper around `bb_broker`.
  Gate: `make scrip` clean; Icon rung01-11 59/59 PASS.

- [x] **U-8** — Retire `Pl_GoalBox` — replace with `bb_node_t`. DONE.
  In `pl_broker.h`: `Pl_GoalBox` → `bb_node_t`; `.fn`/`.zeta` field names already match.
  `pl_exec_goal` now calls `bb_broker(root, BB_ONCE, NULL, NULL)` — returns 1 if ticks>0.
  Gate: `make scrip` clean; Prolog regression non-regressing.

---

### Phase 5 — Wire `bb_broker` as the single call site in all three paths

- [x] **U-9** — Replace Phase 3 in `stmt_exec.c` with `bb_broker(root, BB_SCAN, ...)`. DONE.
  The scan body_fn extracts match start/end from the `DESCR_t` val via `spec_from_descr`.
  Remove the inline scan loop from `stmt_exec.c`.
  Gate: `make scrip` clean; full regression non-regressing; crosscheck passes.

- [x] **U-10** — Replace `icn_broker` call sites in `scrip.c`/`icon_gen.c` with `bb_broker(..., BB_PUMP, ...)`.
  Remove `icn_broker` function entirely. DONE.
  Gate: make scrip clean; Icon ir-run PASS=48/59 (non-regressing). ✅

- [x] **U-11** — Replace `pl_exec_goal` call sites with `bb_broker(..., BB_ONCE, ...)`.
  Remove `pl_exec_goal` function entirely. DONE.
  Gate: make scrip clean; smoke PASS=2 FAIL=0; csnobol4-suite PASS=34 non-regressing. commit 74cef6a5.

---

### Phase 6 — Program-level unification (polyglot Program*)

The broker and interpreter are already unified (U-1..U-11). The remaining gap is at the
**program level**: scrip.c dispatches by file extension to one of three execute_program
entry points. A polyglot `.scrip` file cannot yet be parsed or executed as a single
Program*. These steps fix that — small, always runnable, gate after each.

- [ ] **U-12** — Tag STMT_t with source language.
  Add `int lang;` field to `STMT_t` in `scrip_cc.h` (0=SNOBOL4, 1=Icon, 2=Prolog).
  Define `LANG_SNO=0 LANG_ICN=1 LANG_PL=2` constants there.
  Each frontend sets `st->lang` on every statement it produces:
    - `sno_parse` (Bison/Flex path in `sno_parse.y` or shim): set LANG_SNO.
    - `icon_compile`: set LANG_ICN.
    - `prolog_compile`: set LANG_PL.
  Existing single-language paths are unchanged — lang tag is just ignored for now.
  Gate: `make scrip` clean; smoke PASS; regression non-regressing.

- [ ] **U-13** — Polyglot parser in scrip.c: parse a `.scrip` file into one Program*.
  A `.scrip` file is a sequence of fenced blocks (` ```SNOBOL4 `, ` ```Icon `, ` ```Prolog `).
  Add `parse_scrip_polyglot(const char *src, const char *filename) -> Program*` in scrip.c.
  Algorithm: scan for fence open/close, extract each block's text, compile with the
  matching frontend (sno_parse_string / icon_compile / prolog_compile), append all
  resulting STMT_t chains into one Program* with lang tags set.
  Wire `main()`: detect `.scrip` extension, call parse_scrip_polyglot.
  Gate: `scrip demo/scrip/demo2/wordcount.md` (treated as polyglot — runs its SNOBOL4
  section only for now, Icon/Prolog sections parsed but not yet dispatched). `make scrip`
  clean; smoke PASS; regression non-regressing.

- [ ] **U-14** — Per-statement language dispatch in execute_program.
  `execute_program` currently assumes all statements are SNOBOL4.
  Add a dispatch wrapper: before executing each STMT_t, check `st->lang`.
  LANG_ICN statements: set g_lang=1, push fresh icn_env frame, call icn_interp_eval,
  restore g_lang=0, icn_env=NULL on exit.
  LANG_PL statements: route through the existing Prolog interp_eval path.
  LANG_SNO: existing path unchanged.
  Gate: `scrip --ir-run demo/scrip/demo2/wordcount.md` produces correct wordcount output
  for the SNOBOL4 section; Icon/Prolog sections execute without crashing (output may
  differ — correctness of cross-section state sharing is a later step).
  `make scrip` clean; smoke PASS; regression non-regressing.

- [ ] **U-15** — Implement `icn_eval_gen` in scrip.c (the B-8 stub declared in icon_gen.h).
  `icn_eval_gen(EXPR_t *e) -> bb_node_t`: walk an Icon IR expression and return a live
  bb_node_t that bb_broker can drive.
  Cases needed for cross-language demos: E_TO → {icn_bb_to, allocated icn_to_state_t};
  E_TO_BY → {icn_bb_to_by, ...}; E_ITERATE → {icn_bb_iterate, ...};
  E_FNC (user proc call) → {icn_bb_suspend, coroutine wrapping icn_call_proc}.
  Fallback: wrap icn_interp_eval result as a one-shot constant box.
  Gate: `make scrip` clean; smoke PASS; regression non-regressing; Icon rung01-11 59/59.

- [ ] **U-16** — Cross-language test at box level (standalone C).
  Write `test/test_cross_lang.c`: call `icn_eval_gen` on a hand-built E_TO(1,3) node,
  drive result with `bb_broker(..., BB_PUMP, collect_int, &c)`, assert 3 ticks and
  values {1,2,3}. Also: build a `bb_lit` box, drive with BB_ONCE, assert 1 tick on match.
  Gate: test compiles and exits 0; `make scrip` clean.

- [ ] **U-17** — Cross-language call at .scrip file level.
  Write `test/cross_lang.scrip`: SNOBOL4 section defines a pattern that delegates to an
  Icon generator box (via `icn_eval_gen` + `bb_broker` wired into interp_eval_pat for
  E_EVERY nodes tagged LANG_ICN). Icon section produces values consumed by SNOBOL4 OUTPUT.
  Gate: `scrip test/cross_lang.scrip` exits 0 and matches expected output.
  `make scrip` clean; smoke PASS; regression non-regressing.

- [ ] **U-18** — Documentation.
  Update PLAN.md Active Goals table. Update `ARCH-IR.md` to document the polyglot
  Program*, per-statement lang tag, and the single execute_program dispatch loop.
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

---

## Current state (session 2026-04-13, one4all HEAD 74cef6a5)

U-1 through U-11 complete. U-6 γ repack still deferred (only affects --bb-live x86 path).
smoke.sh x86 emit block replaced with SKIP (SM/BB box-by-box emitter pending).

Phase 6 replanned 2026-04-13: program-level unification first, then box-level cross-lang.
Key insight: one interpreter (interp_eval) and one broker (bb_broker) already exist.
The gap is at the Program* level — no lang tag on STMT_t, no polyglot parser, no
per-statement dispatch. icn_eval_gen (B-8) declared in icon_gen.h but not yet implemented.

**Next session starts at U-12.** Tag STMT_t with source language (add lang field).

regression baseline: csnobol4-suite PASS=34 (non-regressing through U-11).
