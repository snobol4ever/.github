# FINDING 2026-07-27 — `**@r` (SLURPY_LOL) lands, and the "cheap rung" estimate is FALSIFIED

**Session:** s2026-07-27 (Claude Opus 5) · SCRIP `56a1cbd2` · Raku m3/m4 **695/0 → 702/0**

---

## 1. THE HEADLINE — A RANKED "NEXT RUNG" ESTIMATE WAS WRONG, AND THE WRONGNESS IS THE VALUE

The s2026-07-26c LIVE CURSOR ranked `**@r` first by cost:

> (a) **`**@r` (SLURPY_LOL, non-flattening)** — needs one more lexer rule (`"**@"`) and a THIRD
> `rest_kind` value (`REST_NESTED`) … **the plumbing this session built takes it directly, no redesign.**

The plumbing claim is TRUE. The *semantic* claim hidden inside it is FALSE, and no amount of plumbing
reaches it:

**Under SCRIP's one-level SOH aggregate encoding, a non-flattening join is BYTE-IDENTICAL to a
flattening join.** Splitting each argument on `SOH` and rejoining all segments with `SOH` is the
**identity function** on the concatenated string. So `REST_NESTED` implemented "correctly" — join the
arguments verbatim, never split — produces the same bytes as `REST_FLAT_AGG` in every case.

Proven mechanically before any SCRIP edit (standalone C, both folds side by side):
`flat_len=5 verbatim_len=5 identical=YES` for args `{"1\x012", "9"}`.

Then confirmed end-to-end in the built compiler:

```raku
my @x = 1, 2;
sub flat($a,  *@r) { say @r.elems; }   # canonical 3  → SCRIP 3   ✅
sub lol( $a, **@r) { say @r.elems; }   # canonical 2  → SCRIP 3   ❌
flat(0, @x, 9);  lol(0, @x, 9);
```

⟹ **`**@` differs observably from `*@` ONLY for an Iterable argument, and representing that
difference requires an array-NESTING level the encoding does not have.** Arrays *and* hashes are both
string-encoded; `SOH` separates elements and `STX` separates hash key/value — there is no third level
and no escape. Giving `@r[0]` back the array `@x` as ONE element means escaping inner `SOH`, which
then has to be un-escaped in `to_cstring`, every subscript path, `.elems`, `for`, reductions… i.e. a
representation-wide arc, NOT a rung.

**Do not re-rank `**@r`-style work as cheap on the strength of the plumbing existing.** The plumbing
carries the *decision*; the *semantics* live in the representation.

## 2. WHAT ACTUALLY LANDED (and why it is still worth landing)

`sub f($a, **@r)` was a **hard parse error** — any program using `**@` died outright. It now parses,
binds, and is **canonical-correct for scalar arguments**, which is the common case and the only case
the existing corpus exercises. The divergence above is named, smoke-adjacent, and deferred.

- **Lexer** — `"**@"{ALPHA}{ALNUM}*` → new `SLURPY_LOL` (`sval = yytext+2`). Flex longest-match takes
  it ahead of `"**"`→`OP_POW` regardless of rule order; **zero conflict delta (93 s/r, 9 r/r)**.
- **Grammar** — `rk_slurpy_lol_param()` mirrors `rk_slurpy_param()`, marker `TT_QLIT "**@"`; two
  productions mirroring the `SLURPY_POS` pair.
- **Lowerer** — that marker → `rest_kind = 2` (`REST_NESTED`). Marker-driven, one `else if`.
- **Runtime** — `rt_proc_set_rest_kind` **stopped clamping** (`kind ? 1 : 0` → `kind`; the clamp
  would have silently collapsed 2→1); `rt_frame_bind_args` dispatches three ways; new
  `rt_make_nested_agg` is the verbatim fold **and is the documented seam where nesting lands**.
- **Representation is named by WHAT differs**, never `is_raku_lol` — `REST_LIST` / `REST_FLAT_AGG` /
  `REST_NESTED`, per the shared-helper FACT RULE.

**No new IR opcode, no BB template, no x86 encoder, zero emitter/template files in the diff.**

## 3. ⚠ THE M4 REPLAY TRAP — HIT AGAIN, IN THE EXACT CODE THAT WARNED ABOUT IT

`scrip.c`'s `rt_proc_set_rest_kind` replay emitted a **hardcoded `mov esi, 1`**. Its own comment (added
s2026-07-26c) warns that the startup replay is an ALLOWLIST, not a snapshot — yet it hardcoded the one
value that existed at the time. A third `rest_kind` would have been **silently downgraded to
`REST_FLAT_AGG`** in every standalone binary while m3 passed.

Fixed to `emit_textf("  mov esi, %d\n", pe->rest_kind)`. Verified in the emitted `.s` (`mov esi, 2`,
three procs) and **falsified rather than assumed** — stripping the replay calls from the `.s` and
relinking reproduces `[GZ-10] rt_call_proc_descr: procedure 'list__elems' has no stackless slab`.

**GENERALIZABLE:** when a replay emitter writes a literal that mirrors a *field*, it is a latent
downgrade waiting for that field's second value. Emit the field. Grep the other replay emitters for
hardcoded `mov esi, 1` beside a multi-valued fact.

## 4. VERIFICATION LEDGER (all measured this session, live)

| Check | Result |
|---|---|
| Starting watermark, verified LIVE before first edit | m3 **695/0**, m4 **695/0** (matches prior cursor) |
| Toolchain provenance BEFORE editing | bison 3.8.2 + flex 2.6.4 reproduce `raku.tab.c`/`.tab.h`/`.lex.c` **byte-for-byte** |
| Final | m3 **702/0**, m4 **702/0** (+7, all `[m3 PASS] [m4 PASS]`) |
| Bison conflicts | **93 s/r / 9 r/r — ZERO delta** |
| Peers | Icon **14/14**, SNOBOL4 **7/7** both modes |
| Lang-blind gate | green |
| SNOBOL4 `.s` artifacts | **150/150 compilable byte-identical** (5 non-regens are `-I lib/` include-path misses in my harness invocation, NOT drift — diagnosed, `cannot open include 'lib/math.sno'`) |
| Emitter/template files in diff | **0** ⟹ the pre-existing purity (`bb_call.cpp`, `bb_call_write_slot.cpp`) and concurrency doc-anchor violations are provably not this session's |
| Build opt level | `-O0` throughout (zero `-O2` in build logs) |

## 5. NEXT

1. **`*%h` (SLURPY_NAMED)** — still wants the named-arg envelope surviving into the callee; pairs with
   named args to USER METHODS (needs a `meth_call` seam after MRO resolution).
2. **`+@r` (SLURPY_ONEARG)** — `from-slurpy-onearg` (`List.rakumod:215`), the single-arg rule. Now a
   **genuinely** cheap rung: it is a fourth `rest_kind` and, unlike `**@`, its semantics are
   expressible in the current encoding.
3. **ARRAY-NESTING REPRESENTATION ARC** — the real blocker behind `**@`, nested lists, `[[1,2],[3]]`,
   and `.WHAT`→`(Array)` inside aggregates. Schedule deliberately; it is multi-rung. `rt_make_nested_agg`
   is the seam.
4. `multi` + slurpy still blocked as named in the prior cursor (`rk_multi_mangle` reads the marker
   `TT_QLIT` as a param TYPE; fix = mangler skips the marker).
