# HANDOFF-2026-05-28-OPUS-IBB-HELLO-MODE3.md

**Goal:** GOAL-ICON-BB (IBB ground-zero)
**Author:** Claude Opus 4.7
**Date:** 2026-05-28
**Branch:** `SCRIP/main`
**HEAD:** `6393c743`
**Predecessor:** `48409299` (SBL-XNME-VARNAME)

---

## Result

**Mode-3 canonical-5: 0/5 → 1/5.** `hello.icn` (`procedure main() write("hello") end`) now PASSes via flat-wired x86 (`bb_build_flat` → seal RX → call slab as `bb_box_fn`), byte-identical to mode 2. The IBB ground-zero target for hello.icn is met.

All other regressions held: mode-2 corpus 200/47/36=283 unchanged; smoke_icon 5/5; smoke_prolog 5/5; broker 38/15; FACT=0; `--dump-sm` count=0 for hello.icn under SCRIP_ICN_BB.

---

## Commits (local, on `SCRIP/main`, not yet pushed)

### `3d85c4de` — `bb_lit_scalar` MEDIUM_BINARY
10-byte pass-through (`α: jmp γ ; β: jmp ω`), exact mirror of `bb_fail.cpp` / `bb_seq.cpp` (n==0). Bin `{sites={1,5,6}, labels={γ_p, β_p, ω_p}, is_def={F,T,F}}`. The per-node α minted by `bb_fill_alpha` is unreferenced in the flat path — `flat_drive_seq` defines `mids[i]` at the same slab offset where these 10 bytes begin, so the LIT leaf's own α can be a no-op in BINARY. Verified by the predecessor's `bb_fail` having lived in mode 3 unchanged.

The handoff `e572ecce` hedge ("not verified under EP-pair regime") was overcautious — `bb_fail` and `bb_seq` (n==0) have been live in mode 3 with this exact shape; `bb_lit_scalar` is structurally identical.

### `6393c743` — `bb_call` + `bb_seq(n>0)` MEDIUM_BINARY: hello.icn mode 3 PASS

**`bb_call` MEDIUM_BINARY (write(string_literal) only).** 37 bytes:
```
off  bytes                       asm
0    48 BF <u64 sptr>            movabs rdi, &"hello"
10   BE <u32 slen>               mov esi, 5
15   48 B8 <u64 fnptr>            movabs rax, &rt_write_str_nl
25   FF D0                       call rax
27   E9 <rel32 → γ>              jmp lbl_γ
32   (lbl_β defined here)
32   E9 <rel32 → ω>              jmp lbl_ω
37   end
```
Bin patches three label sites (offsets 28/32/33 → γ/β/ω). Runtime fn pointer and string-literal pointer embedded as movabs immediates — same pattern as `bb_upto.cpp` lines 86 / 107 / 110 (strchr / hay / cset). The `e572ecce` handoff comment claiming this "violates the rule" was a misreading — RULES.md FACT permits `bytes()` / `u64le()` inside `*_templates/`; only the label-patch mechanism goes through `bin{sites,labels,is_def}`. In-process address embedding is precedented and correct for `--run` (sealed-RX slabs live for the process; AST `sval` lives in the parse pool, also process-lifetime).

**`bb_seq` n>0 MEDIUM_BINARY.** Mirrors `bb_pl_seq.cpp`'s EP-pair iteration exactly. `flat_drive_seq` populates `g_emit.xa_bb_emit_pair_*[]` with `{define=lbl_β, jmp=lbl_ω}` before `EMIT_PAIR_FILL → walk_bb_node` dispatches to us; we walk the arrays, emit `\xE9 + u32le(0)` per jmp pair, build `bin.sites/labels/is_def`. No bytes-helper outside templates.

---

## Mode-3 canonical-5 status (verified by running)

| Program | Mode 2 | Mode 3 | Next gap if not passing |
|---|---|---|---|
| `hello.icn` (`write("hello")`) | ✅ | **✅ (NEW)** | — |
| `add.icn` (`write(1+2)`) | ✅ | ❌ | `bb_call: write(BB_BINOP)` shape — needs value-passing convention |
| `every_to.icn` (`every write(1 to 3)`) | ✅ | ❌ | `walk_bb_flat: BB_EVERY needs flat_drive_every` |
| `alt.icn` (`every write(1|2|3)`) | ✅ | ❌ | Same — needs flat_drive_every + BB_ALTERNATE in flat walk |
| `full.icn` (`every write(5 > ((1 to 2)*(3 to 4)))`) | ✅ | ❌ | Same — plus generator-arg odometer in flat |

---

## What's next — architectural question for Lon

The remaining 4 canonical-5 programs all share one missing piece: **a value-passing convention for mode-3 sealed-RX slabs.** Mode 2 uses `BB_graph_t.ring` (a struct-field deque) — `BB_BINOP` apply reads `peek(1)/peek(0)`, `bb_exec`'s odometer drives generator args. Mode 3 needs an equivalent the slab can manipulate. Three candidates, each with precedent or downside:

1. **`r12`-anchored ring in a `bb_pool`-allocated buffer.** Precedent: `bb_upto.cpp` already uses `r12` to push DESCR_t-shaped (16-byte) records (`mov dword[r12], 1; mov dword[r12+4], slen; mov [r12+8], ptr; add r12, 16`). Extension: ring pointer initialized at slab entry (in `XA_FLAT_PROLOGUE`), torn down at exit.

2. **The existing `vstack` exposed via runtime helpers** (`rt_vstack_push_int`, `rt_vstack_pop_int`). Higher per-op overhead (call/ret per push), but the runtime already implements DESCR_t discipline and FAILDESCR propagation.

3. **A fresh in-slab data area** (one `u64` slot per BB node), pre-allocated by `bb_alloc` and addressed via `movabs`. Mirrors mode-2 `peers[]` more closely; trades cache locality for simpler emit.

Plus the orthogonal question: does `BB_LIT_I` MEDIUM_BINARY (currently the 10-byte pass-through stub from commit `3d85c4de`) **stay a pass-through** — relying on the BB graph's structural lhs/rhs ordering and the apply node knowing what to read — or does it **emit a real push** of its `ival` onto the chosen value channel?

Per goal-file IBB-3 ("`BB_ICN_ILIT` template (mode-2 only at this rung). α pushes `DT_I(ival)` via γ"), the intent for LIT_I in mode 2 was an explicit push. Same intent ports to mode 3 once the channel is chosen.

**My recommendation:** option 1 (r12 ring), because `bb_upto.cpp` has already battle-tested it and `XA_FLAT_PROLOGUE` is the natural place to initialize it. But this is your architecture call.

---

## Stale text I did NOT update (waiting for confirmation)

- `PLAN.md` ICON-BB row: still says "Mode-3 score on 5 canonical: 0/5". Updated score is 1/5.
- `GOAL-ICON-BB.md` ground-zero table at line 16-20: same.
- The MEDIUM_BINARY column at line 29-38 needs `bb_lit_scalar`, `bb_call` (for write(strlit)), `bb_seq` (n>0) flipped from ABORT to "real".

I left these for you to review before the row gets re-stamped. They're trivial diffs once you confirm the values above.

---

## Gates

```
$ bash scripts/build_scrip.sh                    # OK
$ bash scripts/test_smoke_icon.sh                # PASS=5 FAIL=0
$ bash scripts/test_smoke_prolog.sh              # PASS=5 FAIL=0
$ bash scripts/test_smoke_unified_broker.sh      # PASS=38 FAIL=15
$ SCRIP_ICN_BB=1 ./scrip --interp /tmp/hello.icn # hello (exit 0)
$ SCRIP_ICN_BB=1 ./scrip --run    /tmp/hello.icn # hello (exit 0)  ← NEW
$ SCRIP_ICN_BB=1 ./scrip --dump-sm /tmp/hello.icn # ; SM_sequence_t  count=0
$ SCRIP_ICN_BB=1 bash scripts/test_icon_all_rungs.sh  # PASS=200 FAIL=47 XFAIL=36 TOTAL=283
$ grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' \
    src/ | grep -v _templates/ | grep -v emit_core | wc -l   # 0
```

All green.
