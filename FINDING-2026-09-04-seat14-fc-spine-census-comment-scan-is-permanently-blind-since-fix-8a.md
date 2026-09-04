# FINDING 2026-09-04 seat14 — `util_fc_spine_census.sh`'s comment-scan method is permanently blind since FIX-8a, unrelated to and independent of the corpus-path fossil it also had

Row: `dead-suite-path-consumer-sweep`. While fixing `util_fc_spine_census.sh`'s dead `$S4E/corpus/crosscheck`
default (repointed to extract the `crosscheck_*` master-suite families via `lib_master_extract.sh`'s
`master_extract_origin_prefix`, verified: 0 → 325 programs compiled), the census itself still reported
`FC CELLS: 0` across all 325. Checked before writing it up as fixed: is 0 the honest current state of
ZB-FC-3/ZB-ACT-3 (plausible — the script's own header says "the number is supposed to GROW" as those land),
or is the instrument itself unable to measure regardless of population?

**Confirmed the latter.** The census's method is: compile each `.sno` with `--compile --target=x86` under
`SCRIP_ZETA_PORT=6`, then scan the emitted `.s` text for `# IR_MATCH_*` comment lines and attribute nearby
`sub rsp, 16` instructions to whichever comment block they fall under. Direct check —
`src/templates/x86/x86_asm.h:1567`:

```
if (!strcmp(mnem, "comment"))   return std::string();
```

Every `x86("comment", "IR_MATCH_SPAN")`-style call (still present throughout `src/templates/bb/bb_match_*.cpp`
— the source-level annotations were never deleted) compiles to **zero bytes, unconditionally, in both media**.
This is not a bug: `GOAL-BB-FIXUP.md`'s FIX-8a rung ("TERSE BOX COMMENTS") deliberately terse'd every
`x86("comment", …)` call down to a bare `IR_<KIND>` tag and proved the change **byte-identical** (comment-only
`.s` delta) as its own landing criterion — i.e. the comment was already understood to contribute nothing to
emitted output, verbose or terse, before or after that rung. `RULES.md`'s "`x86(\"comment\")` is
medium-complete" reads the same way once you check the implementation: complete because it behaves identically
(does nothing) in TEXT and BINARY, not because it correctly emits the comment in either.

**Net effect:** `util_fc_spine_census.sh` cannot produce a nonzero FC-cell count under the current architecture,
for any input, because its only signal (a comment string in `--compile` output) was retired by a separate,
already-ratified, already-gated effort that predates this finding and has nothing to do with the corpus reorg.
0 CELLS is not evidence about ZB-FC-3/ZB-ACT-3's landing state one way or the other — the instrument went blind
first.

**Scope note:** the corpus-path fix (0 → 325 programs scanned) is real, verified, and in scope for
`dead-suite-path-consumer-sweep` — landed regardless. Fixing the census's blindness is a different, bigger job
(a real signal needs either instrumenting `zls_fc_cell()` in `src/ir/zeta_storage.c` directly, or a
`--dump-ir`-based pass) and is NOT this row's charter; flagged here and in the script's own header so whoever
next touches ZB-FC/ZB-ACT-3 doesn't read a future `FC CELLS: 0` as a real measurement.

Gave: SCRIP (script header note, same commit as the path fix). No code-path or template changed by this
finding — `src/templates/x86/x86_asm.h:1567` is existing, ratified, gated behavior, not something to revert.
