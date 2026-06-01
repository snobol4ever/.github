# HANDOFF 2026-06-01 OPUS48 — SNOBOL4-BB TEMPLATE-SYSTEM REVAMP v1 (PIVOT)

**SCRIP:** `29c3613` (was `65686c2`)  ·  **.github:** this commit
**Goal:** GOAL-SNOBOL4-BB.md  ·  **Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus

---

## WHY (Lon directive, this session)

Kill the SPIN/CHURN of every GOAL-*-BB box maintaining **two divergent arms**
(`MEDIUM_BINARY` hand-coded byte map + `MEDIUM_TEXT` GAS) **plus a hand-counted
`bb_bin_t` offset table**. The two arms drift (e.g. bb_lit's BINARY baked `movabs`
absolute addresses while TEXT used position-independent `lea [rip+...]` / `call @PLT`),
and the literal `{13,65,80,84,95}` patch offsets break on every edit.

A converted box is now **ONE return per `PLATFORM_*`**, **pure string concatenation**,
**no template locals** (operands are functions of `g_emit` / `_`), all variance inline
via `IF(...)`/`FOR(...)`. Medium is **invisible** in the template.

## WHAT LANDED

**`src/emitter/BB_templates/x86_asm.h`** (NEW, header-only — no Makefile change):

- Self-encoding x86 helpers, each `MEDIUM_BINARY → record stream` else `→ GAS text`:
  `x86_mov/cmp/test` (alu r/m32,r32), `x86_add/x86_sub` (r32,imm32), `x86_movsxd`,
  `x86_lea_subj_cursor` (lea dst,[r13+rcx]), `x86_store_cursor_mirror` (legacy [r10]),
  `x86_push/x86_pop`, `x86_movimm` (TEXT `mov dst,imm` / BIN `movabs`), `x86_load_ro`,
  `x86_call_ro`, `x86_jcc/x86_jmp/x86_deflabel`.
- **In-band patch records replace `bb_bin_t`.** Records: `L <len> <bytes>` (literal
  code), `J <port>` (rel32 patch to α/β/γ/ω), `D <port>` (define label here). Ports
  `0=α 1=β 2=γ 3=ω`. `bb_emit_x86(stream)` walks them, **discovering** byte positions
  as it copies (no hand-counted offsets). One primitive (`bb_emit_patch_rel32`,
  disp = target−(site+4)) serves jmp rel32, lea[rip+disp], and call qword[rip+disp].
- All concat helpers are **side-effect-free**; the only side effects (emit bytes /
  register patches) live in `bb_emit_x86`, called from the extern, NOT in the concat.

**`src/emitter/BB_templates/bb_lit.cpp`** (converted x86 arm; JVM/JS/NET/WASM untouched):
x86 arm is one return of `x86_*` calls; `MEDIUM_MACRO_DEF` arm dropped; `bb_bin_t` gone.
The two divergent instructions are encapsulated in `x86_load_ro` / `x86_call_ro` — both
arms adjacent so they can't silently drift.

**Verified (briefly — see "TESTING POLICY" below, do NOT repeat at length):**
BINARY arm byte-identical to `65686c2` (addr-masked diff: only the two `movabs` ASLR
imm64 fields differ). TEXT arm assembles clean under `as`. Gates unchanged: m2 **7/7
HARD**, m3 5/6, m4 0/6 (pre-existing by-design abort), prove_lower2 **67**, sm_dead 0,
no_vstack 5-residual, purity 8 (bb_lit not flagged), concurrency OK.

## GO-FORWARD STRATEGY (Lon, authoritative for next sessions)

1. **TEXT-FIRST.** Take the **TEXT** arm as source of truth and **throw away the
   hand-coded BINARY** arm. Convert the TEXT representation into the new `x86_*` format;
   the helpers regenerate binary from that one description. (Deterministic auto-conversion
   is likely too hard — do it by hand.) This makes BINARY follow TEXT semantics, i.e.
   position-independent (`lea [rip+...]`, `call @PLT`) — the **REG-RO** direction.
2. **NO SAFETY NET.** No full regression suite. Four parallel sessions will fix any few
   typos. Optional only: a couple of before/after `as` runs to confirm the `.o` matches.
3. **STRAIGHT-FORWARD / FAST.** All sessions on hold for this. We are at **GROUND ZERO** —
   everything is effectively broken (we are at `write("hello world")`), so byte-identity
   against the (broken) baseline is NOT the goal; do not over-verify.

## ⚠ PENDING — FACT-RULE REWRITE (grand-master-reorg; Lon authorizes)

The shared `x86_*` byte-producing helpers **supersede** the **TWO-LITERAL-FORMS** and
**TEMPLATE-ONLY-EMISSION** FACT RULES ("hand-coded literal byte map", "duplicate the
bytes into each file", "no shared helper returns templated x86 bytes"). Nothing went
red this session, but only for incidental reasons (`audit_concurrency_invariants` checks
the FACT-RULE *comment text* is replicated across the 5 GOAL `.md` files — untouched;
`util_template_purity_audit` globs `*.cpp` — the pure `.h` isn't scanned). To land
cleanly, the rule text in the **five GOAL-*-BB files + RULES.md** and the **purity /
concurrency gates** (incl. the EMITTER/LOWER md5 pins) must be rewritten together to
describe the unified self-encoding model. NOT done here — teed up for the authorized reorg.

## NEXT (concrete)

- **(A)** Flip `x86_load_ro` / `x86_call_ro` BINARY arms to position-independent: string
  bytes → sealed RO trailer + `lea dst,[rip+disp]`; runtime ptr → in-blob 8-byte slot +
  `call qword [rip+disp]`. Needs trailer record kinds in `bb_emit_x86` (collect trailer
  data, define its labels after the code, back-patch the rip-rel sites). This is REG-RO
  for bb_lit and also retires the legacy `[r10]` mirror.
- **(B)** Convert the next pattern boxes TEXT-first with the `x86_asm.h` vocabulary
  (generalize the helper set as new instruction shapes appear). Candidates: bb_match,
  bb_pat_any/notany/span/break/len/rem (REG-2 family), then pos/tab/atp, combinators,
  generators.
- **(C)** When ready, the FACT-RULE rewrite above.

Older per-session writeups: other `HANDOFF-*.md`.
