# HANDOFF 2026-05-20 — ISOLATION rung (parse->lower / parse->runtime)

**Goal:** GOAL-HEADQUARTERS
**Session model:** Claude Opus 4.7
**Trigger phrases used this session:** "here we go" (implicit), "perform hand off"
**Watermark advance:** `b4859b69` → `cb1738f6` on one4all.  corpus unchanged at `b10933c`.

## What landed (three orthogonal constructs)

### ISO-1 (commit `261ff13d`): `lower()` takes `tree_t *` directly

`lower(const ParserOutput *po)` → `lower(const tree_t *prog)`.  The `ParserOutput` struct was hollow at the seams — only `prog` was read, and two of its three callers (`scrip.c dump_sm`, `sync_monitor_run`) never invoked `parser_output_build`, silently relying on whoever called them earlier to have populated the three file-scope sidecars (`label_table`, `proc_table`, `g_pl_pred_table`).

Sidecar build (`label_table_build`, `prescan_defines`, `polyglot_init`) moves into the top of `lower()` as a single point of truth.  The duplicate `label_table_build` + `prescan_defines` calls (which `parser_output_build` made, and which `polyglot_init` also made) collapse to one set inside `polyglot_init`.

`ParserOutput` struct + `parser_output.{c,h}` + Makefile entry deleted (8 files / +12 −60 LOC).  Callers `scrip.c dump_sm`/`mode_monitor`, `scrip_sm.c sm_preamble`, `sync_monitor_run` all simplified.

### ISO-2 (commit `1691f44f`): parse->lower header firewall gate

`scripts/test_gate_lower_isolation.sh`: enforces that no file under `src/lower/` may `#include` a file under `src/frontend/` except via an explicit allowlist.

At commit time: 10 includes / 7 allowlist entries.  Each entry documents (a) what the header contains, (b) why it is currently misfiled under `frontend/`, and (c) the owning relocation goal that would let the entry be removed.

The allowlist is a ratchet — future commits may shrink it (by moving a header out of `frontend/`) but must never grow it.  A new direct include into `frontend/` fails the gate with a clear remediation message.

### ISO-3 (commit `cb1738f6`): relocate icon_gen.h + runtime firewall

Two coordinated moves in one commit:

1. **Relocate `src/frontend/icon/icon_gen.h` → `src/runtime/interp/icon_gen.h`** (`git mv`, history preserved).  The header is pure Icon Byrd-box generator runtime state — `icn_to_state_t`, `icn_find_state_t`, `icn_bb_*` function decls, `IcnBinopKind` enum, ~30 procedure-runtime structs.  It was misfiled under `frontend/icon/` for historical reasons; no `.c` file under `src/frontend/` ever included it.  Seven include sites updated.  Lower firewall: 10/7 → 9/6.

2. **Add `scripts/test_gate_runtime_isolation.sh`** — companion gate enforcing the symmetric invariant on the parse->runtime edge.  Today 16 includes / 8 allowlist entries.  Most are Prolog runtime-ish headers bundled under `frontend/prolog/` alongside the Prolog lex/parse code (owning relocation goal: split that directory into pure-parse + `runtime/interp/prolog/`).

## What did NOT land (and why)

**No symbol-level isolation proof.**  The firewalls are *header* firewalls.  They catch direct `#include` regressions in seconds during inner-loop edits.  They do **not** prove that `lower` reads only the AST passed to it; symbols reachable through an allowlisted header (most acutely through `scrip_cc.h`) are not detected.  The stronger guarantee — link-time isolation test (`lower.o` linked against a tree with all `frontend/*.o` absent) — is recorded as ISO-7 and deferred.

**Calling the firewalls "isolation" is overstating what's in the tree.**  This is recorded in the HEADQUARTERS rung text so the next session does not over-trust them.

**No subprocess `scrip_parse` work.**  Lon proposed converting the six parsers into a separate executable that pipes TDump/TLump S-expressions back to SCRIP.  Scoping discussion landed at: that's many sessions of work, the C-side *deserializer* doesn't exist yet (only the dumper does in `src/ast/ast_print.c`, mirroring `corpus/SCRIP/tdump.sc`), and the next-session-first-step should be writing the deserializer + a roundtrip self-test on the existing in-process parse pipeline — *before* introducing a process boundary that makes debugging harder.  This is now ISO-4 on the rung list.

## State of the world at handoff

```
one4all HEAD: cb1738f6
corpus  HEAD: b10933c (unchanged)
.github HEAD: (this commit)

GATE-1 smoke icon:      5/0          (watermark match)
GATE-2 smoke broker:    23/26        (watermark match)
GATE-3 icon rungs:      194/36/35    (watermark match)

smoke snobol4: 7/0   smoke prolog: 5/0   smoke rebus: 4/0
smoke snocone: 5/0   smoke raku:   5/0

firewall lower:   9 includes / 6 allowlisted  ✅ green
firewall runtime: 16 includes / 8 allowlisted ✅ green
```

## Files for next session to know about

- `scripts/test_gate_lower_isolation.sh` — read top comment for ratchet rules
- `scripts/test_gate_runtime_isolation.sh` — same
- `src/lower/lower.h` + `lower.c:2067` — new signature, sidecar build at entry
- `src/lower/lower.c:2071` — comment "Was previously parser_output_build at the driver" traces the history

## Open relocation rungs surfaced by the allowlists (ISO-5/6 candidates)

Each is a separable named rung when ready to take on:

1. `frontend/icon/icon_lex.h` — extract `IcnTkKind` enum to `src/include/icon_tk.h` (rest of `icon_lex.h` stays put)
2. `frontend/raku/raku_driver.h` — split into `raku_parse.h` (stays) + `raku_runtime.h` (moves to `src/runtime/interp/raku/`)
3. `frontend/prolog/{term,prolog_runtime,prolog_atom,prolog_driver,prolog_builtin,pl_broker}.h` (six headers) — relocate to `src/runtime/interp/prolog/`.  This is the largest set; the Prolog frontend directory blends parse + runtime today.
4. `frontend/snobol4/scrip_cc.h` — rename + relocate to `src/include/scrip_lang.h`.  54 includers tree-wide.  Mechanical move but huge sed surface.
5. `frontend/raku/raku_re.h` — relocate to `src/runtime/interp/raku/`.

Each move shrinks both firewall allowlists symmetrically.

## Recommended next session

ISO-4 step 1: write the C-side TDump/TLump deserializer.  Reference: `src/ast/ast_print.c` (dumper).  Prove with a roundtrip self-test (`scrip --dump-ast file.sno | deserializer` produces a `tree_t` identical to in-process parse).  Do not introduce the process boundary until roundtrip is proven on the language corpus.

Two preflight questions saved for that session (raised but not resolved this session):
1. Should the C deserializer match `corpus/SCRIP/tdump.sc`'s output exactly (interop with SCRIP-side dumps), or only `src/ast/ast_print.c`'s output?
2. TDump vs TLump — handle both, or only TLump (the line-fitted budgeted form that crosses the pipe)?

Authors: LCherryholmes . Claude Opus 4.7
