# FINDING: Icon `key()`/table iteration order no longer matches the Arizona oracle — a measured, unverified side effect of the SNOBOL4 TABLE rewrite on a mechanism the two languages share

**Seat:** seat08 · **Date:** 2026-08-28 · **Task:** tests-consolidate-icon (rung10-equivalent survey of `corpus/tests/icon/repro/`) · **Not a crash, not PZ-4 — a wrong-answer class finding, routed to hq_C per RULES.md's own two-HQ interlock ("a wrong ANSWER belongs to hq_C").**

## The witness

`corpus/tests/icon/repro/table_key_order.icn`:
```icon
procedure main();
   local t, k, out;
   t := table();
   t["@"] := 1; t["%"] := 2; t["$"] := 3; t["!"] := 4;
   t["*"] := 5; t["+"] := 6; t["-"] := 7; t["/"] := 8;
   out := "";
   every k := key(t) do out := out || k;
   write("keyorder=", out);
end
```
Its committed `.expected`: `keyorder=@-*$!+%/`.

**Measured, three ways, same day, same tree (SCRIP `7203a29b`):**
- scrip mode-3 (`--run`): `keyorder=*+@-$!/%`
- scrip mode-4 (`--compile` + link against `out/libscrip_rt.so`): `keyorder=*+@-$!/%` — identical to m3, so this is not a mode-divergence artifact under the new MODES-MAY-DIVERGE law, it's the same wrong order both ways.
- **Arizona reference** (`/home/resources/icon-master/bin/icon table_key_order.icn`, built binary already present, `icont`/`iconx` both there): `keyorder=@-*$!+%/` — **byte-identical to `.expected`.**

Not a data-loss bug: `echo -n '@-*$!+%/' | fold -w1 | sort` and the same on scrip's output both give `!%*+-/@$` — same 8 characters, every one accounted for, purely a different enumeration order.

## Why this isn't "Icon doesn't guarantee table order, so the test is invalid"

That was my first hypothesis and I did not stop there — checked it against the real oracle instead of asserting it. If `.expected` were merely "whatever some arbitrary past run produced," the Arizona reference would have no particular reason to reproduce it today. It does, byte-for-byte. That means the order is a **deterministic function of insertion sequence + the reference implementation's hash algorithm**, not free-floating nondeterminism — the Icon language report doesn't *mandate* an order, but a specific implementation's order is still a reproducible, checkable fact about that implementation, and this repro was presumably captured for exactly that reason (or authored against the real oracle directly).

## The mechanism — confirmed at the code level, not inferred from timing alone

`by_name_dispatch.c:6520`, `BID_key`'s entire implementation:
```c
for (unsigned _bi=0;_bi<td.tbl->nbuck;_bi++)
    if (td.tbl->buckets[_bi] && td.tbl->buckets[_bi]->len) {
        *out = td.tbl->buckets[_bi]->ent[0].key_descr; return 1;
    }
```
Icon's `key()` walks `->buckets[]` directly, bucket-major, first-entry-in-bucket. This is **the exact structure** `FINDING-2026-08-23-hq_P-table-rewrite-typed-hash-contiguous-bucket-binary-search-asm.md` rewrote for SNOBOL4's `TABLE`: "contiguous, hkey-sorted bucket," a new per-datatype hash algorithm, new growth policy. That FINDING's own "Correctness" section: *"Oracle `sbl -bf` byte-for-byte... Corpus m3 357/359, m4 355/359"* — **SNOBOL4/SPITBOL only.** No Icon board, no Icon witness, anywhere in it. `aggregates.c` (where the per-datatype hash arms live) has zero Icon-specific code — consistent with this project's own "no language identity past lower" architecture, and confirming the mechanism genuinely is shared, not coincidentally similar.

So: a shared mechanism changed, its own verification scoped to one frontend, and the other frontend that walks the identical structure was never re-graded. This is a live, concrete instance of the class RULES.md's own **SHARED-NODE VERDICT SCOPE** law (line 185) exists to catch: *"A change to the codegen or lowering of an IR node shared across frontends is graded on every frontend that lowers to that node before its verdict is quotable."* I'm not asserting the rewrite is wrong to have shipped — the SNOBOL4 correctness case for it is solid and oracle-proven on its own terms — only that Icon's table-order behavior was an unchecked, unlabeled side effect of it, discovered five days later by an unrelated task.

## What I did NOT do

Did not re-baseline `.expected`/`.ref` to scrip's current output — that would bake an unverified-against-Icon's-own-oracle change into a permanent regression fixture, the same "amend the format to accommodate our own bug" trap RULES.md already names (line 159). Did not convert this file into the new suite format either way. Left it loose, not in KEEP.md (this may or may not be a permanent design choice — not mine to decide).

## Open question for hq_C, not decided here

1. Is Arizona-compatible table/key ordering an actual goal for SCRIP Icon, or is post-rewrite order acceptable and `.expected` should be regenerated from scrip's current (verified-complete, just reordered) output?
2. If (1) is "acceptable," should tests asserting `key()`/table enumeration order be excluded from the runtime-suite scheme on principle (the language report doesn't guarantee it) rather than converted at all — same shape as this task's own `rung50_between_errors`-style "different bug, needs its own scope call" items on the sibling prolog task?
3. Is this the ONLY Icon-visible consequence of the s262 rewrite, or are there others (e.g. `sort(tbl)` output order, `every ... := !tbl`) that were also never re-graded? I checked only the one witness this task's survey surfaced — did not go looking for more, out of this row's scope.

No source changes made. `corpus/tests/icon/repro/table_key_order.icn` + `.expected` left exactly as found.
