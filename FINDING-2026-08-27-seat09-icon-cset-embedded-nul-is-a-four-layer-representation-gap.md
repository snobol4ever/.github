# FINDING 2026-08-27 (seat09) — ICN CSET/STRING EMBEDDED `\x00`: NOT A LOOP BUG, A FOUR-LAYER REPRESENTATION GAP

**Status: ROOT-CAUSED IN FULL, ACROSS FOUR SEPARATE LAYERS. NOT FIXED, DELIBERATELY — see WHY NOT FIXED.
Supersedes/extends `FINDING-2026-08-24-seat16-icon-cset-string-literal-embedded-nul-truncates-to-empty.md`, whose
own "not investigated: where the truncation happens" is now answered, and the answer is bigger than a single site.**

Picked up from `icon-n3-scan-one-depth-authority.task.md` NEXT item 4 ("jcon_scan1's blocker... still a separate
row candidate"). Confirmed via direct source reading at every layer, not inferred.

## REPRO (unchanged from seat16's original finding, re-verified this session)
```icon
procedure main(); local skips; skips := '\x00ab'; write(*skips); write(skips ? upto('a')); end
```
SCRIP: `0` then the scan fails. Arizona `icont`/`iconx`: `3` then `2`.

## THE FOUR LAYERS, EACH CHECKED DIRECTLY AGAINST SOURCE

**LAYER 1 — LEXER (`src/frontend/icon/icon_lex.c`, `scan_cset`/`scan_string`, `buf_push`): CORRECT.**
Length is tracked explicitly (`len`/`cap`, never `strlen`); `buf_push` appends any byte value including
`0x00` and tracks length separately from the convenience NUL it also appends. `t.val.sval.len` is accurate.

**LAYER 2 — AST (`src/ir/ast.h` `struct tree_t`, `src/frontend/icon/icon_parse.c` `e_leaf_sval`/`intern_n`
in `src/frontend/snobol4/scrip_cc.h:58-60`): LENGTH IS LOST HERE, SILENTLY, EVEN THOUGH THE BYTES SURVIVE.**
`intern_n(s, len)` does `memcpy(p, s, len); p[len] = '\0'` — the malloc'd buffer genuinely contains the correct
bytes, embedded NUL included. But `tree_t` (`ast.h:97-107`) stores the result only as `char *sval` in a union
with `ival`/`dval` — **there is no length field anywhere on the node.** From this point on, nothing downstream
can recover where the literal actually ends; every consumer that needs a length is forced to guess via `strlen`.

**LAYER 3 — LOWERING (`src/lower/lower_icon.c`): THE VISIBLE SYMPTOM'S DIRECT CAUSE, BUT NOT THE ONLY BUG.**
`icn_cset_canon` (lines 46-53):
```c
static const char * icn_cset_canon(const char * s) {
    if (!s) return s;
    unsigned char seen[256]; memset(seen, 0, sizeof seen);
    for (const unsigned char * p = (const unsigned char *) s; *p; p++) seen[*p] = 1;   // <-- stops at first \x00
    ...
```
Called from two sites (line 329, line 393: `IR_LIT(nd).sval = icn_cset_canon(t->v.sval)`), always with a bare
`char *` and no length (layer 2 already lost it, so none is available to pass even if this function accepted one).
For the exact repro and for the real corpus witness (`rung36_jcon_scan1.icn`'s `skips` cset, `\x00` also first),
the collection loop runs **zero iterations**, `n` stays 0, and the canonical set collapses to `""` — this is
the entire visible bug. When `\x00` is NOT the first member, the same loop would silently drop it and every
member after it, a strictly worse (silent partial data loss) case that just happens not to be in the current repro.

**LAYER 4 — CODEGEN (`src/emitter/emit.cpp:1071` → `src/templates/bb/bb_lit_scalar.cpp`): CONFIRMS LENGTH IS
NEVER CARRIED THROUGH, EVEN IF LAYER 3 WERE FIXED.** `IR_LIT_STRING`'s codegen (line 39) bakes
`strlen(_.op_sval)` as the runtime length constant — wrong for any embedded-NUL string regardless of layer 3.
`IR_LIT_CHARSET`'s codegen (line 67) does something different and revealing: it **always** bakes
`(long)-1` into the DESCR_t's length slot, never a real count. `-1` as the 32-bit slot is `0xFFFFFFFFu` —
**this is exactly `CSETVAL`'s sentinel** (`src/runtime/core/core.h:23`:
`#define CSETVAL(s_) ((DESCR_t){ .v = DT_S, .slen = 0xFFFFFFFFu, .s = (s_) })`). So `.slen` is not a spare
field opportunistically available for a length — **it is permanently committed as the DT_S/is-this-a-cset type
tag**, and every charset literal defers its actual length to a runtime lookup, unconditionally, by construction.
(Not independently confirmed this session: whether the `.data`/`.string` blob-emission path can even represent
an embedded-NUL byte correctly in TEXT/mode-4 `.s` output — `x86(".string", ...)` needs octal/hex escaping for
a literal NUL to survive as assembler text, and that was not traced. Flagged, not chased — moot until layers
2-3 carry a real length to hand it.)

**LAYER 5 — RUNTIME (`src/runtime/keywords.c` `kw_cset_len`; `src/frontend/icon/icon_runtime.c`
`cset_canonical`/`cset_union`/`cset_diff`/`cset_inter`): THE ONLY EXISTING LENGTH CHANNEL DOES NOT SCALE, AND
THE RUNTIME SET-ALGEBRA FUNCTIONS HAVE THE IDENTICAL LAYER-3 BUG INDEPENDENTLY.**
`kw_cset_len` (`keywords.c:77-84`) is a pointer-identity registry, `g_kw_cset_names[KW_CSET_MAX]` with
**`KW_CSET_MAX == 16`**, populated *only* by `kw_cset_prime()` for the six hardcoded keyword csets
(`&lcase &ucase &digits &letters &ascii &cset`). Any other cset pointer — every user literal, every
runtime-computed union/diff/intersection result — is invisible to it and falls through to `strlen()`.
Separately, and independently of the literal-parsing path entirely: `cset_canonical`, `cset_union`, `cset_diff`,
`cset_inter` (`icon_runtime.c:10-67`, used for `&cset -- &ascii`-style expressions via
`src/runtime/arithmetic.c:283-301` and `src/runtime/by_name_dispatch.c:7149-7151`) **all** iterate their inputs
with `for (i=0; a[i]; i++)` — the same NUL-terminated assumption as layer 3's `icn_cset_canon`, so a cset
*expression* that would legitimately produce a byte-0-inclusive result is broken by an entirely separate
occurrence of the same defect shape, not fixable by touching layer 3 alone.

## WHY NOT FIXED THIS SESSION

A loop-bound fix to `icn_cset_canon` alone changes **nothing observable**: even a byte-correct canonical buffer
still starts with `0x00` when the set contains it, so `strlen()` at layer 4/5 reports 0 regardless — the
`*skips` symptom would be unchanged. A real fix needs a length that survives from layer 2 through to layer 5,
and the only existing channel for "a cset pointer's length that isn't strlen" (`kw_cset_len`'s registry) is a
fixed 16-slot table hardcoded for six specific keyword pointers, not a general per-literal mechanism — growing
it to cover arbitrary program literals means codegen must emit a registration call (or table) at program init
for every charset literal, which in turn means layer 2/3 must carry a real length that far. That is a genuine,
multi-file feature (new length-carrying path from AST or IR through codegen into a scalable runtime registry,
*and* the independent layer-5 set-algebra fix), not a patch — and per this project's own established pattern
(this same task's LEDGER, hq_P's own ruling on the tab/move bug: "record it... the next attempt starts from
it"), rushing a partial version onto a session already time-conscious risks exactly the kind of regression this
codebase has been repeatedly bitten by. `DESCR_t.slen`'s layout is shared across every language's runtime;
touching it is a bigger decision than one seat should make unreviewed, matching RULES.md's caution on
widely-shared structures and the explicit "PEERS RULE" instinct against ad hoc field reuse.

## BLAST RADIUS (confirmed, not estimated)

Every `upto()`/`any()`/etc. call in `rung36_jcon_scan1.icn` using its `skips` cset (`\x00` first member) as
either subject or needle — `ascii?skips`, `letts?skips`, `vowls?skips`, all `skips?*` lines — is affected, per
seat16's original finding. `uppers := &cset -- &ascii` in the same file exercises the independent layer-5
`cset_diff` bug too (though `&cset`/`&ascii` are themselves pre-registered, so the *inputs* self-report
correctly via `kw_cset_len` even though the *diff loop* would mis-handle a byte-0 result if `&cset`'s own
content actually included 0 — not separately re-verified this session against the registered content's actual
byte range).

## CANDIDATE FIX DIRECTIONS (neither attempted)
1. Replace `kw_cset_len`'s fixed 16-slot table with a growable, program-scoped registry; have codegen emit one
   registration call per charset literal at program-init time, carrying a real length computed from a
   length-aware rewrite of `icn_cset_canon` (needs layer 2 to carry length that far — e.g. via the IR operand
   mechanism `ir_operand_push`, not a new `tree_t`/`IR_t` field, per PEERS RULE); fix `cset_canonical`/
   `cset_union`/`cset_diff`/`cset_inter` (layer 5) to take explicit lengths instead of NUL-scanning.
2. A DESCR_t layout change giving csets a real length field instead of the `slen` type-tag sentinel — bigger,
   shared across every language's runtime, needs architectural sign-off, not a seat's unilateral call.

## ROUTING
Sent to `hq_C` (topic `icn-cset-nul-four-layer-gap`) — this is a wrong-ANSWER bug, hq_C's per the two-HQ
interlock. Task file `icon-n3-scan-one-depth-authority.task.md` NEXT/LEDGER updated to point here so the next
holder of that row's item 4 does not re-derive this.
