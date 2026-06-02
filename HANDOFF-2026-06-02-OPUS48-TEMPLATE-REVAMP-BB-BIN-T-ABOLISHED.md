# HANDOFF 2026-06-02 (Opus 4.8) — `bb_bin_t` ABOLISHED + MEDIUM-INVISIBLE PRISON; SCRIP BUILDS + ABORTS BEAUTIFULLY

**Lon directive (verbatim intent):** "Let's get the build broke nice. Build the prison of rules. Leave it to the
Four Musketeers (the GOAL-*-BB sessions) to fix up as they go along on their particular test. Just ensure the
SCRIP builds and aborts in 100s of places beautifully."

## WHAT LANDED

### 1. The prison — TWO new FACT RULES (staged in `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md`; fold byte-identical-×5 at grand-master-reorg)
- **`bb_bin_t` IS ABOLISHED.** The `struct bb_bin_t { sites,labels,is_def,bytes }` + `bb_emit_asm_result()` +
  `bb_emit_asm_result_pairs()` are DELETED from `emit_str.h`/`emit_str.cpp`. The `bin.sites.push_back((int)b.size())`
  idiom (a FUNCTION counting bytes for a patch offset) no longer compiles because the type is gone. Every box now
  emits via **`bb_emit_x86(out)`** with IN-BAND patch records (`L`/`J`/`D`/`E`/`F`) that DISCOVER byte positions.
  Gate: `scripts/test_gate_no_bb_bin_t.sh` (GREEN — zero live code refs).
- **ONE MEDIUM, INVISIBLE.** A template never writes an instruction twice (`IF(MEDIUM_TEXT,"<gas>") +
  IF(MEDIUM_BINARY,<bytes>)`) nor calls a raw-byte producer (`x86_Lrec`/`x86_b1/2/3`/`bytes(`/`u32le`/`u64le`). Every
  instruction goes through `x86(mnem,…)`; the medium switch lives inside the encoder. Carve-out: `IF(MEDIUM_TEXT,
  s_comment/label)` (no byte form) is fine. Gate: `scripts/test_gate_template_medium_invisible.sh` (informational;
  `--strict` enforces zero). **1 remaining: `bb_unop.cpp` (Icon) — needs an `x86("neg","rax")` encoder.**

These two + the existing no-`pBB`/`_.node` rule are **three faces of ONE end state**: a converted box is pure
`x86()` concatenation reading only `_`. A box that still uses `bb_bin_t` also still branches on the medium and still
hand-encodes bytes — converting it to `x86()` clears all three at once. The three gates reach zero together,
box-by-box, as the revamp completes.

### 2. The build is GREEN and ABORTS BEAUTIFULLY
- `scripts/build_scrip.sh` rc=0 (`scrip` built) · `make libscrip_rt` rc=0 (`out/libscrip_rt.so` built).
- **63 boxes are now LOUD `x86_bomb()` stubs** + **9 empty router sub-TUs** (binop/seq arms whose only caller is a
  now-stubbed router). A stubbed box prints e.g. `libscrip_rt: BOMB — bb_lit_scalar: TEMPLATE-REVAMP not yet
  converted (was offset-table)` then `Aborted` when its emitted code is reached. ~63 beautiful abort sites.
- **Mode-2 (`--interp`) oracle is UNTOUCHED and HARD-GREEN: SNOBOL4 7/7, Icon 12/12.** Modes 3/4 now bomb per-box
  (SNOBOL m3 5→0, Icon m3 12→0) — expected; restored as each lane converts its boxes.
- `g_vstack` 0 · `prove_lower2` 67 PASS · concurrency invariants OK (FACT RULES byte-identical ×3 unperturbed) ·
  template-purity now GREEN (the bomb stubs removed the side-effecting `bb_emit_asm_result` calls).

### 3. New `x86_asm.h` vocabulary (additive — no existing encoder perturbed)
- **`x86_and(reg,imm)`** — `and reg,imm` (imm8 short form / eax 0x25 / imm32), REX.W-aware. Byte-verified vs `as`
  (`and rsp,-16` = `48 83 E4 F0`). Wired into `x86(mnem,reg,imm)`. This was the missing encoder behind the
  `bb_pat_defer` medium-branch (now fixed — the alignment dance `mov rbx,rsp` / `and rsp,-16` / `mov rsp,rbx` goes
  through `x86()`; the two `mov`s already had `x86_mov`).
- **`x86_bomb(msg)`** — the canonical LOUD abort stub, built from `x86_load_ro` + `x86_call_ro` + a `ud2` literal
  (medium-invisible, lives in `x86_asm.h` as the sanctioned raw-byte carve-out). A stub box is exactly
  `extern "C" void bb_foo(...) { bb_emit_x86(x86_bomb("bb_foo: …")); }`.

### 4. SNOBOL-lane combinators converted (the original first-incomplete step)
- `bb_pat_cat` + `bb_pat_alt` → `x86_pair_loop()` (pBB-free), matching `bb_conj`/`bb_ite`. `bb_templates.h` +
  `emit_core.c` dispatch made parameterless. `bb_pat_defer` medium-branch eliminated. `xa_flat.cpp` (shared mode-4
  prologue/epilogue) converted off `bb_bin_t` to a LOCAL one-site emit (`xa_emit_one`) preserving exact bytes +
  driver-label semantics (its patch targets are driver labels `flat_β_p`/`flat_fail_p`, not box ports).

## THE FOUR MUSKETEERS — YOUR JOB (convert your lane's bomb stubs as your test reaches them)

Each `x86_bomb` stub is a box whose `x86()` self-encoding you write per the RULES-DRAFT recipe (R1–R13 + the three
FACT RULES). Replace `bb_emit_x86(x86_bomb("…"))` with the real `return …x86()… ;` concat. Reference conversions:
`bb_pat_pos` (loop-free), `bb_pat_span` (looping + ζ-frame), `bb_conj`/`bb_ite`/`bb_pat_cat`/`bb_pat_alt`
(`x86_pair_loop()` combinators). The git history of each stubbed file (`git show HEAD~1:<path>`) has the ORIGINAL
byte logic to translate from.

**Stubbed boxes by lane** (8/8/8 + Icon/shared):
- **SNOBOL4:** `bb_sno_assign`, `bb_sno_scan`, `bb_sno_subject`, `bb_match`, `bb_capture`, `bb_arbno`,
  `bb_ref_invariant`, `bb_eps`. (`bb_pat_*` leaves + cat/alt/defer already converted.)
- **Prolog:** `bb_goal`, `bb_builtin`, `bb_unify`, `bb_choice`, `bb_disj`, `bb_catch`, `bb_logicvar`, `bb_atom`.
  (`bb_conj`/`bb_ite`/`bb_cut`/`bb_arith` already converted.)
- **Raku:** `bb_nfa_eps`/`_cap_open`/`_cap_close` (in `bb_nfa_passthrough.cpp`), `bb_nfa_char`, `bb_nfa_any`,
  `bb_nfa_class`, `bb_nfa_bol`, `bb_nfa_eol`, `bb_nfa_accept`, `bb_rk_gather`.
- **Icon/shared:** `bb_binop` (+ 6 empty arm-files `bb_binop_agpure/concat_lit/concat_slot/jct_relop/lit_arith/
  relop`), `bb_binop_gen`, `bb_assign`, `bb_var`, `bb_swap`, `bb_field`, `bb_idx`, `bb_list_bang`, `bb_return`,
  `bb_call`, `bb_proc`, `bb_proc_gen`, `bb_program`, `bb_keyword`, `bb_initial`, `bb_case`, `bb_if`, `bb_to`,
  `bb_to_by`, `bb_upto`, `bb_every`, `bb_alt`, `bb_gen_alt`, `bb_gen_scan`, `bb_iterate`, `bb_limit`, `bb_suspend`,
  `bb_seq` (+ 3 empty arm-files `bb_seq_flat/gather/passthrough`), `bb_lit_scalar`, `bb_fail`, `bb_unop` (last
  medium-branch). The 9 empty TUs get rebuilt when their router is converted.

**Gate after each conversion:** your mode-2 HARD must stay green; `test_gate_no_bb_bin_t.sh` green;
`test_gate_template_medium_invisible.sh` count drops; `make scrip` + `make libscrip_rt` rc=0; raise your
MODE3_MIN/MODE4_MIN floors as your boxes come back.

## SESSION-SETUP GATE LIST — ADD
```
bash scripts/test_gate_no_bb_bin_t.sh                 # HARD: bb_bin_t abolished (must be 0)
bash scripts/test_gate_template_medium_invisible.sh   # informational; --strict at end of revamp
```

**Watermark:** SCRIP local (NOT pushed — Lon's call on handoff trigger). `.github` this file + RULES-DRAFT.
