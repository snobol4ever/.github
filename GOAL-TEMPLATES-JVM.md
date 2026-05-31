# GOAL-TEMPLATES-JVM.md — JVM backend, all languages

**Repo:** SCRIP + .github
**Backend:** JVM — Jasmin assembly → `.class` bytecode → `java`. Mode: `--compile --target=jvm`.
**Read first:** `ARCH-JVM.md` · `ARCH-EMITTER.md` · `ARCH-IR.md` · `RULES.md`

---

## Premise

The six frontends lower to the shared SM/BB IR. This backend supplies the JVM arm
(`IS_JVM` in the unified `emit_core.c` templates) for every SM opcode and BB box-kind, so
that **every language runs on the JVM**. The `.class` IS the Byrd-box graph — labels and
gotos compiled at emit time, no interpreter loop at runtime.

`snobol4jvm` (Clojure) remains the separate semantic oracle (1,896 tests baseline); it is
not this emitter, but the correctness reference for it.

## Done when

Every SM opcode and BB box-kind reachable from any of the six frontends has a non-stub
JVM template arm, and each language's corpus assembles via `jasmin.jar` and runs on `java`
producing output matching the x86/oracle reference.

## All-languages coverage

| Language | JVM emit status |
|---|---|
| SNOBOL4 | original target: beauty.sno byte-identical to SPITBOL oracle |
| Snocone | extend in-tree JVM host (code in `src/driver/jvm/`) |
| Icon | shares the IR; arms follow once x86 frontend lands the opcodes |
| Prolog | resumable-predicate pattern (Closure + tableswitch on clause state) — see ARCH-JVM.md |
| Raku | shares the IR; arms follow x86 frontend |
| Rebus | shares the IR; arms follow x86 frontend |

## Backend-specific notes (detail in ARCH-JVM.md)

- One class per box; α/β public methods; γ/ω = return value (`Spec` or null sentinel); ζ in instance fields, GC-reclaimed.
- Three-column form preserved; port exits compile to `goto` / `areturn` / `aconst_null + areturn`.
- Tools: `javac`, `java`, bundled `src/backend/jasmin.jar`. Boxes assemble to `bb/*.class`, packaged into `boxes.jar`.
- Per RULES.md: zero C Byrd boxes; no AST walking in modes 2/3/4; byte production only inside templates.
