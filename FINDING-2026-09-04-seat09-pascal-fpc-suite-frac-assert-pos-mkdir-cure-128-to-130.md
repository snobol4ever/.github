# FINDING: Pascal fpc_tests suite — frac/assert/Pos/mkdir/rmdir added, 128 -> 130 (m3)

**Who/when:** seat09, 2026-09-04, FLEET-16, row `pascal-fpc-suite-62-reds-censused-by-class-and-cured`.

## Fresh measurement before touching anything

Pulled all three repos (SCRIP/corpus/.github all behind). Rebuilt clean, ran
`test_pascal_fpc_suite.sh` fresh: `m3_pass=128` (confirmed unchanged since seat15's last release —
the row's own `## NEXT` was stale, written by seat11 at 126, seat15's later work at 128 was never
folded into a fresh NEXT block, only a LEDGER entry).

## Four builtins added, each mirroring the existing `round`/`halt`/`trunc` pattern

All via `pascal.y`'s `mk_call()` (parse-time rewrite to a runtime call) + a matching `if (_bid == ...)`
arm in `by_name_dispatch.c`'s `try_call_builtin_by_name_bl`. New BIDs 180-184 hand-inserted into
`g_bid_tab[]` at their computed djb2-hash slots (`gen_builtin_ids.py`'s forward transform is still a
one-way tool per the prior census — every existing entry is already in `{}` form, so a new builtin
means computing the slot by hand, same as `round`/`halt` before it):

- **`frac(x)`** (id 180, slot 546, zero probe) -> `__pas_frac`: `x - trunc(x)` via libm `trunc()`.
  Verified real-valued, correct for `frac(1e20)=0`, `frac(3.75)=0.75`, `frac(-3.75)=-0.75`.
- **`assert(cond)`** (id 181, slot 632, zero probe) -> `__pas_assert`: the boolean is evaluated by the
  CALLER (no control-flow rewrite needed, unlike `inc`/`dec`) and passed as a plain int; the runtime
  arm does the conditional itself (`if (!cond) { stderr "Runtime error 227 at $0"; exit(227); }`),
  matching FPC's actual assertion-failure runtime-error code. 2-arg `assert(cond,msg)` is NOT
  implemented (no witness in this suite needs it; `items[0]` is safe either way since the first real
  argument is always at index 0 regardless of the write-style interleaved-pairs convention seat15
  documented for `inc`/`dec`).
- **`Pos(needle, haystack)`** (id 182, slot 24, zero probe) -> `__pas_pos`: plain `strstr`-based
  1-based substring search (0 if absent). The FPC-extended 1-char-as-needle overload (`Pos(aChar,
  aString)`) is handled by reusing the EXISTING `pas_is_charexpr()`/`mk_chr_wrap()` machinery already
  used for `write`/`writeln` char formatting — wraps a char-typed needle through `__pas_chr` (which
  already returns a genuine 1-char STRING descriptor, not just a formatting marker) before the runtime
  call, so `to_cstring()` sees a real string on both sides.
- **`mkdir(path)`/`rmdir(path)`** (ids 183/184, slots 317/133, 0/1 probe) -> `__pas_mkdir`/`__pas_rmdir`:
  thin wrappers over POSIX `mkdir(path,0777)`/`rmdir(path)`, return value discarded (matches the
  witness's own `{$I-}`+`InOutRes:=0` "don't care about the error code" usage). `InOutRes` itself
  needed no new handling — an unrecognized identifier used as a plain assignment target already works
  (silently becomes an ordinary global cell); nothing in this suite ever reads it back.

**One enabling fix**, found because `assert` unmasked it (see below): `const X = true;`/`const X =
false;` was silently folding to `0` regardless of which keyword was used.
`scalar_constant: IDENT {...}` (the const-declaration path) called `pas_const_get()` directly instead
of going through `mk_ident()` (the expression-context identifier resolver, which already special-cases
`true`/`false`/`nil` before falling back to the same const table) — so a `const` initialized from the
literal identifiers `true`/`false` never hit that special-case at all, only ever hit the const table
(which has no entry for a bareword `true`), always defaulting to `cv=0`. Ordinary boolean expressions
(`b1 := TRUE`) were never affected — those go through `mk_ident()` and already worked; only the narrow
`const NAME = true;` declaration form was wrong. Fixed by mirroring `mk_ident()`'s two special cases
inline in `scalar_constant`'s `IDENT` action. Low blast radius: previously ANY unrecognized identifier
in this position silently produced `0`, so this is strictly a correctness improvement, never a
regression risk.

**One enabling fix for the `Pos` witness specifically**: `WideChar`-typed variables were not recognized
as char-typed at all (`g_pas_pend_ischar` only matched the literal type name `"char"`), so a `WideChar`
variable's value stayed a bare integer ordinal at runtime with no static char tag — `pas_is_charexpr()`
correctly said "not a char" and `Pos`'s needle went through `to_cstring()` as `itos(97)="97"`, not `"a"`.
Fixed by treating `widechar` as a `char` synonym at both of `simple_type`'s `IDENT` case's `strcmp`
sites (case-folding to lowercase already happens upstream — confirmed by testing `var c:Char;` prints
the character, not its ordinal, before touching anything). This is a deliberate simplification (no
genuine UTF-16/wide semantics), scoped to exactly the alias FPC's own doc treats as interchangeable
with `Char` for basic single-byte use — matches this witness's own ASCII-only usage.

## What flipped and what didn't (measured, not assumed)

Only **2 of the 4 new builtins' own target witnesses actually flip to PASS** — the other two are
correct in isolation but each is blocked by a SEPARATE, pre-existing, out-of-scope defect, same
unmasking pattern this row has hit repeatedly:

- **`test_units_system_tassert1` (misc-single-witness-builtins): PASSES.** Needed both `assert` and the
  `const X=true` fix together.
- **`webtbs_tw0895` (misc-single-witness-builtins, `mkdir`): PASSES.** Verified in an isolated scratch
  cwd; the program's own `mkdir`/`rmdir` pair self-cleans, confirmed no directory left behind.
- **`webtbs_tw33635` (`frac`): STILL FAILS**, but not on `frac` — `frac()` itself is verified correct
  (isolated: `frac(1e20)=0`, matches ref). The witness's very FIRST line (`writeln('x=',x)`, before
  `frac` is ever called) already mismatches ref on a pre-existing, general default-real-number-format
  divergence (`1.000000000000E+020` vs FPC's `1.0000000000000000e+020` — wrong case, wrong precision).
  This is systemic (affects any bare `writeln(realExpr)` in scientific-notation range), NOT specific to
  this witness or to `frac`, and clearly out of scope here (matches the same shape as `tbs_tb0012`'s
  real-format divergence already flagged in the original census) — flagging, not fixing; too large a
  blast radius for this row.
- **`webtbs_tw12233` (`Pos`, misc-single-witness-builtins): STILL FAILS**, but not on `Pos` or
  `WideChar` — both verified correct in isolation (`Pos('a','badc')=2`, and the exact witness now
  computes the right VALUE, `2`). The mismatch is `writeln(Pos(...))`'s result printing width-10
  space-padded (`"          2"`) where FPC's ref has no padding (`"2"`). This is the shared
  `__pas_writeln`/`__pas_write` runtime default-integer-width behavior (documented elsewhere as
  "default int=10"), used by every Pascal program — NOT something to change for one witness; flagging,
  not touching.

**Net measured: `test_pascal_fpc_suite.sh` m3_pass 128 -> 130, m4_pass 126 -> 128** (m3/m4 move
together, consistent with this suite's historical identical-fail-set property). `130` is the exact
floor of this row's own `DONE-WHEN` (`m3_pass` must match `1[3-9][0-9]`) — re-run fresh before trusting
it if picking this row up again; it has drifted before.

## Regression checks (all clean, none touched shared/other-language code paths)

- SNOBOL4 `make test` control arm: `m3 PASS=1698 FAIL=0`, `m4 PASS=1698 FAIL=0 SKIP=0` (unchanged).
- Pascal master suite (`test_gate_pascal_m3.sh`/`test_gate_pascal_m4.sh`): `175/178` both modes, same 3
  pre-existing fails (`ladder__rung01_var_assign_multi_group`, `ladder__rung02_arithmetic_real_div`,
  `ladder__rung02_arithmetic_mod_neg` — already-filed rung1/rung2 ladder defects from an earlier
  session today, confirmed unrelated to this row's changes by name).
- `test_gate_pas_frame_pairing.sh`: `PASS=2/2` unchanged.
- The only files touched: `src/parsers/pascal/pascal.y` (+ regenerated `.tab.c`/`.tab.h`),
  `src/runtime/builtin_ids.h`, `src/runtime/by_name_dispatch.c`. No shared emitter/template/lowerer
  file touched; no new global variables; `strip_comments.py --check` clean.

## Row disposition

DONE-WHEN's `m3_pass` clause now passes (`130`). The `tisobuf1.tmp`/`tisoread.tmp` litter-file clause
was already clean (the sibling row's fix already prevents them; confirmed by direct `ls`, nothing to
remove). The FINDING-glob and `pascal-fpc-class-*` QUEUE.tsv-count clauses were already satisfied
before this session (11 rows minted, well over the 3 minimum). Closing this row via `s4e_msg.sh done`.

## For whoever picks up the two flagged-not-fixed defects

Both are real, both are general (not single-witness), both need a session that owns shared
runtime/emitter formatting code, which this row's scope (fixture/single-builtin level) does not cover:

- **Default real-number `writeln` formatting diverges from FPC's own default** (wrong case `E`/`e`,
  wrong precision — ours looks like a 12-13 significant-digit `%E`-family format, FPC's default is a
  17-significant-digit `%.16e`-family format). Worth its own row; likely affects other still-failing
  witnesses beyond `webtbs_tw33635` (e.g. `tbs_tb0012`'s divergence looks related, though that one may
  also have a type-tagging issue on top — printed a bare integer, not any real-formatted string at all).
- **Default integer `writeln` width is unconditionally 10** even for a bare function-call-result
  argument with no explicit width specifier, where FPC prints unpadded. Confirmed via `Pos(...)`'s
  result specifically; not investigated whether this differs for a plain int VARIABLE vs a computed
  expression (worth checking before assuming it is universal — this suite has 130 passing entries, so
  something must already be different for at least some plain-int-writeln shapes, or this suite simply
  doesn't exercise many of those without an explicit width).
