# SESSION-icon-js.md — Icon × JavaScript (one4all)

**Repo:** one4all · **Frontend:** Icon · **Backend:** JavaScript
**Session prefix:** `IJJ` (Icon JS — distinct from `IJ` = Icon JVM)
**Trigger:** "playing with Icon JavaScript" / "Icon JS"
**Replaces:** SESSION-icon-wasm.md (⛔ PARKED)
**Depends on:** M-SJ-A01 complete (shared trampoline + runtime)

---

## §SUBSYSTEMS

| Subsystem | Doc |
|-----------|-----|
| Icon language / IR | `PARSER-ICON.md` |
| JS backend | `EMITTER-JS.md` |
| Milestone ladder | `MILESTONE-JS-ICON.md` |

---

## §KEY INSIGHT — Goal-Directed Evaluation → Trampoline

Proebsting's paper (in ByrdBox.zip) gives the exact templates.
`5 > ((1 to 2) * (3 to 4))` compiles to a state machine with
`_to_i` counters and conditional trampoline returns — identical
to the C backend's `emit_byrd_c.c` `case 'TO':` handler in `byrd_box.py`.

Each EKind gets four labeled trampoline functions (α/β/γ/ω).
The Proebsting Figure 2 "optimized code" IS what the emitter should produce
after copy-propagation. Read Figure 1 first to understand the wiring,
then collapse it to Figure 2 in the emitter.

---

## §KEY FILES

| File | Role |
|------|------|
| `src/backend/emit_js_icon.c` | Icon JS emitter (to create) |
| `src/runtime/js/icon_runtime.js` | extends sno_runtime.js |
| `src/backend/emit_wasm_icon.c` | Oracle for IR switch structure |
| `src/backend/emit_jvm_icon.c` | Oracle for Byrd wiring |

---

## §NOW — IJJ-1

**Next milestone: M-IJJ-A01** (requires M-SJ-A01 complete first)

Read: `EMITTER-JS.md` · `MILESTONE-JS-ICON.md` · `PARSER-ICON.md`
Then: `src/backend/emit_wasm_icon.c` IR switch (parked but useful template)

---

*SESSION-icon-js.md — rewritten IJJ-1, 2026-03-31, Claude Sonnet 4.6.*
