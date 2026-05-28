# HANDOFF 2026-05-28 Opus 4.7 — SBL-EP-BINARY FACT-violation fix

**Sequel to** `HANDOFF-2026-05-28-OPUS-SBL-EP-BINARY.md` (same session, same goal).

## What went wrong

Commit `1bc53211` (one4all main) added a shared helper `ep_bin_fill_str(bin, prelude_lbl)`
to `src/emitter/emit_str.cpp`. The helper returned `bytes(1, "\xE9") + u32le(0)`
sequences and the six combinator templates (ALT/CAT/FENCE/PL_SEQ/PL_ITE/SUCCEED) called
it from their MEDIUM_BINARY arms.

**That violated the FACT RULE.** Every byte of emitted x86 must originate inside a
template file under `*_templates/`. A helper in `emit_str.cpp` that returns x86 byte
sequences is the same class of violation as `emit_standard_blob` — it concentrates
template bytes outside templates. The audit script's text-based heuristics missed it
because the bytes-producing call was in a non-template file.

Lon caught it. The session prompt response was, verbatim:

> "Something happened to the x86 bytes and some stupi function is there instead.
> Whoops! Get those bytes back there in ALL SM and BB opcode! Big, dummy!
> That violates the RULES."

## What the fix did

1. **Deleted `ep_bin_fill_str`** from `emit_str.{cpp,h}` entirely. Removed the
   `emit_globals.h` include that only the helper needed.

2. **Duplicated the EP-walk + byte-emit loop inline into each of the six combinator
   templates.** Every `bytes(1, "\xE9")` and `u32le(0)` literally appears in
   `bb_pat_alt.cpp`, `bb_pat_cat.cpp`, `bb_pat_fence.cpp`, `bb_pl_seq.cpp`,
   `bb_pl_ite.cpp`, `bb_succeed.cpp`. The duplication is the point. Each template
   owns its own bytes.

   The per-template body has the shape:
   ```cpp
   IF(MEDIUM_BINARY, [&]() {
       std::string b;
       // optional prelude site for templates that emit lbl_α: in TEXT
       if (_.lbl_α_p) {
           bin.sites.push_back(0);
           bin.labels.push_back(_.lbl_α_p);
           bin.is_def.push_back(true);
       }
       for (int i = 0; i < g_emit.xa_bb_ep_n; i++) {
           if (g_emit.xa_bb_ep_define[i]) {
               bin.sites.push_back((int)b.size());
               bin.labels.push_back(g_emit.xa_bb_ep_define[i]);
               bin.is_def.push_back(true);
           }
           if (g_emit.xa_bb_ep_jmp[i]) {
               b += bytes(1, "\xE9");
               bin.sites.push_back((int)b.size());
               bin.labels.push_back(g_emit.xa_bb_ep_jmp[i]);
               bin.is_def.push_back(false);
               b += u32le(0);
           }
       }
       return b;
   }())
   ```

   FENCE additionally handles its 0-children case in-template (synthesised
   `lbl_α: jmp γ ; lbl_β: jmp ω` shape, four sites, two `\xE9 + u32le(0)` pairs).

3. **Strengthened RULES.md FACT entry** to explicitly name this failure mode:

   > **ALSO FORBIDDEN OUTSIDE TEMPLATES:** any helper that returns x86 opcode bytes
   > — `bytes()`, `u8()`, `u32le()`, `u64le()` may appear in `emit_str.cpp` ONLY
   > inside `bomb_bytes` and `bb_emit_asm_result`; nowhere else outside
   > `*_templates/` may construct an x86 byte sequence and return it for templates
   > to splice in. If multiple templates need the same byte pattern, **duplicate
   > the byte-producing code into each template file** — that duplication is the
   > point. A shared `*_str` helper in `emit_str.cpp` that returns templated x86
   > bytes is the SAME violation as `emit_standard_blob` with extra steps.

4. **Extended `audit_m3_native_binary_arms.sh`** to recognise `bin.sites.push_back`
   / `bin.labels.push_back` as substantive — distinguishes real EP-driven arms (which
   register patch sites for the labels they emit) from fake-jmp stubs (which never
   touch `bin`). All six EP-driven combinators classified REAL; the three procedural
   Prolog templates (`bb_pl_alt`, `bb_pl_call`, `bb_pl_choice`) remain BOMB.

## Gates at handoff

| Gate | Result |
|------|--------|
| GATE-1 smoke (default) | 13/13 |
| GATE-1 smoke (SCRIP_M3_NATIVE=1) | 13/13 |
| GATE-2 broker | 35 |
| GATE-3 mode-4 corpus | 175/280 |
| GATE-4 mode-2 corpus | 238/280 |
| NATIVE corpus | 165/280 (unchanged — combinator flat-wire not yet enabled) |
| Rung suite | M2=19 M4=15 SKIP=0 |
| Prolog smoke / mode-4 rung / BB honest | 5/5 / 4/4 / 128/0 |
| Raku smoke | 5/5 |
| FACT RULE | 0 (restored) |
| audit_m3_native | GATE OK |

## Lesson recorded

The FACT RULE means **every byte in its template's own file** — even if it costs
duplication. If you ever find yourself writing a function in `emit_str.cpp` that
returns `bytes(...)` or `u32le(...)`, **stop**. Those bytes belong in the template.
The duplication you avoid is not worth the violation you incur.

---

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus
