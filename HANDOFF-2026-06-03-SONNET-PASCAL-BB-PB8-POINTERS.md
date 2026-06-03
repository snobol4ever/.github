# HANDOFF — Pascal PB-8 pointers/`new` (2026-06-03, Claude Sonnet)

**Status: PB-8 COMPLETE.** `record` + `set` + pointers/`new` all green. Next rung is PB-9 (mode-3/4 compiled BBs).
**HEADs at handoff:** SCRIP `f79fae0`, corpus `58a7174`, .github (this commit).

## What landed
Mode-2 pointer support on the NV heap, modelled on `pint` ("pointers are addresses, nil is a distinct value").

- **All pointers are integer cell numbers** sharing one file-scope counter `g_pas_heap_ctr` (in
  `by_name_dispatch.c`). `nil` = `ilit(0)` — integer 0, distinct from every allocation. Heap cell key = `__heap_<n>`.
- **Record cells store the SOH-packed record on the existing array rail**, so `arr_get` reads fields for free and
  the read path needs no new code.
- One `IR_LANG_PAS`-gated arm in `lower.c` (`v_assign`); zero interpreter structural changes.

## The map (construct → emission → runtime)
| Construct | Parser emits | Runtime |
|---|---|---|
| `nil` | `ilit(0)` (in `mk_ident`) | — |
| `new(p)` scalar | `p := __pas_alloc()` (via `mk_assign`) | INTVAL cell, inits `__heap_n`=0 |
| `new(p)` record | `p := __pas_alloc_rec(nf)` | INTVAL cell, inits `__heap_n`=`nf` SOH "0" segs |
| `new(head^.next)` | `__pas_field_set(head, idx, __pas_alloc_rec(nf))` | alloc then field-write-back |
| `p^` scalar read | `__pas_deref(p)` | `NV[__heap_n]` |
| `p^ := v` scalar | `lower.c` arm → `__pas_deref_set(p,v)` | `NV[__heap_n]=v` |
| `p^.field` read | `TT_IDX(__pas_deref(p), ilit(idx))` | `arr_get` (free) |
| `p^.field := v` | `mk_assign` → `__pas_field_set(p,idx,v)` | read-modify-write SOH cell |

`nf` comes from the pointed-to rectype via `pas_ptrexpr_target` (which works for both `TT_VAR` and `TT_IDX` field
targets, hence `new` on a field works). Chained `head^.next^.val` resolves through per-field pointer-target
tracking (`fldptrto[]` added to the rectype table) plus mutually-recursive `pas_selector_rectype` /
`pas_ptrexpr_target`. Pointer-to-record **parameters** are registered in both the value and `var` parameter arms.

## Files touched (SCRIP)
- `src/runtime/by_name_dispatch.c` — file-scope `g_pas_heap_ctr`; five name-gated builtins `__pas_alloc`,
  `__pas_alloc_rec`, `__pas_field_set`, `__pas_deref`, `__pas_deref_set`.
- `src/lower/lower.c` — one `IR_LANG_PAS`-gated `v_assign` arm for scalar `p^ := v` (placed BEFORE the generic
  `TT_FNC`-LHS result-var arm, which would otherwise treat `__pas_deref` as a result-var name).
- `src/parser/pascal/pascal.y` (+ regenerated `pascal.tab.c`/`.tab.h`) — `mk_deref`, `mk_assign`, `nil` and `new`
  handling in `mk_call`; pointer-type table (`g_pas_ptrtypes`) + pointer-var table (`g_pas_ptrvars`); `fldptrto[]`
  in the rectype table; `pas_rectype_field_index`/`_nf`/`_field_ptrto_by_index`; `pas_selector_rectype`/
  `pas_ptrexpr_target`; grammar arms `selector ARROW`, `selector PERIOD IDENT`, `type: ARROW IDENT`,
  `type: simple_type` (propagate `-3`), record/array/set/file `type` arms (clear leaked ptr-target), `type_decl`,
  `var_decl`, both pointer-`parameter_decl` arms, `assignment`, and table resets in `pascal_parse_string`.

## Two real bugs found by probing (both fixed)
1. **String heap keys collided with nil.** First attempt keyed cells by string; a string coerces to int 0 under
   `<>`, colliding with `nil`=0 so `p <> nil` read false. Fixed by making pointers integers (`ptr3` caught it).
2. **Record pointer-field leaked the pending ptr-target.** A field `next:link` set `g_pas_pend_ptrtarget`, which
   leaked up to the enclosing `type:` rule and made `type_decl` register the *record* as a pointer type. Fixed by
   clearing the leaked target in the record/array/set/file `type` arms and propagating the `-3` sentinel through
   `type: simple_type` (`ptr4` caught it). A related gap — pointer **parameters** not registered, so `p^.field` in
   a proc body fell to `TT_FIELD` — was caught by `ptr8`.

## Probes (corpus `programs/pascal/ptr1..ptr8.pas`, all byte-identical to `pcom`/`pint`)
`ptr1` scalar · `ptr2` two cells + arithmetic · `ptr3` nil compare · `ptr4` linked list, chained `head^.next^.val`
· `ptr5` build-in-loop (prepend) + `while p<>nil` traversal (`p := p^.next`) · `ptr6` aliasing + `p=q` · `ptr7`
distinct cells unequal then aliased · `ptr8` pointer-as-procedure-parameter (traverse + mutate through param) +
`new(head^.next)`.

## Verification (merged build, after rebasing onto concurrent commits)
- Pascal suite **33/0/1** (25 prior + 8 pointer probes; `recursion` is the known `fact(8)`/maxint XFAIL).
- Icon `--interp` **130/117/36** — exact match to documented baseline, every bucket pinned.
- Prolog **0 fail / 0 abort** over the 111 `.expected`-covered programs (the documented 132 total uses the team's
  oracle harness; the invariant that matters — no fail, no abort — holds).
- Isolation proven additionally by a stash/rebuild run showing byte-identical Icon/Prolog crash signatures with and
  without the changes. Parser still has exactly the one pre-existing dangling-else s/r conflict.

## Deferred (no probe forces; do NOT build speculatively)
Variant-record `new(p, tag)` (pcom *does* use these — likely the first thing a real pcom run will demand),
`dispose`, nested records, `with`, record-valued `var` params. The `g_pas_ptrvars`/`g_pas_ptrtypes` tables are flat
globals (same scoping limitation already accepted for arrays/recvars). Two pre-existing cross-language borrows
remain logged-and-deferred (Raku-named `v_raku_det_call`/`v_raku_mutate_writeback`; SNOBOL4-style `:subj` proc
envelope) — unchanged by this session.

## Recommended next
PB-9 (mode-3/4 compiled BBs) per the goal doc, OR — if the aim is to actually run `pcom.pas` — variant-record
`new(p,tag)` is the most likely next probe-forced pointer feature. Climb only as far as a probe forces.

## Gotchas for the next session
- Parser regen: the full regen script aborts at the snobol4 flex step; use `cd src/parser/pascal && bison -d -o
  pascal.tab.c pascal.y` directly. Must stay at exactly 1 s/r conflict.
- Oracle build: `cd corpus/programs/pascal && fpc -Ci -Co -Cr -gl pcom.pas && fpc -Ci -Co -Cr -gl pint.pas`. Check
  pattern: `./pcom < probe.pas >/dev/null 2>&1 && cp prr prd && ./pint < /dev/null` vs `scrip --interp probe.pas`.
- The repos move under you: all three needed a fetch+rebase before push this session. Sync first.
