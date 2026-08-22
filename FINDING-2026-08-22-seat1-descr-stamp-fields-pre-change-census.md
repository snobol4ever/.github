# FINDING seat1 (this session) — descr-stamp-fields FIRST STEP: pre-change census (three classes); ARCH-SNOBOL4-RTX.md §9 does not exist

**Session:** seat1 (`/home/claude1`, Claude Sonnet 5) · **Date:** 2026-08-22 · **Queue row:** `descr-stamp-fields` (rank 0, held, NOT done)
**Tree:** no code changes this step — census only, per the row's own FIRST STEP instruction ("run the three censuses and post the counts before changing anything"). `.github` this file only, plus a pending `ask` to HQ.

---

## 0. BLOCKER ON ARRIVAL — ASKED, NOT STALLED ON

The brief's mandatory read, "⛔ READ ARCH-SNOBOL4-RTX.md §9 FIRST — HQ measured the whole design there; do not re-derive it," does not exist: that file ends at §8 SPITBOL LESSONS, line 88. None of the brief's cited facts (`sizeof(DESCR_t)`, `DT_DATA_STRIDE`, "MEASURED LAYOUT") appear anywhere in it. Sent `s4e_msg.sh ask descr-stamp-fields` with receipts. All of the brief's structural claims were independently re-verified directly against the live `src/contracts/descr.h` instead (§1 below) and check out, so this did not block the rest of the FIRST STEP — but the citation itself needs fixing for the next reader, same STALE-ORIENTATION(a) class as this very file's own s186 self-correction at its top.

Side note for whoever chases the missing §9 later: `DESIGN-SN4-ARITH-INLINE-AND-DT-BITS.md` §2.3 has a similarly-titled "THE LAYOUT" section, but it documents a **different, unrelated, not-yet-landed proposal** — a `DT_t` bit-renumbering under which `DT_DATA` would move to `0x80`. This row's live tree has `DT_DATA = 0x70`. Don't conflate the two designs.

## 1. STRUCTURAL FACTS RE-VERIFIED AGAINST LIVE `src/contracts/descr.h`

- Current `DESCR_t`: `DTYPE_t v` @0 (4B, plain C enum) · `uint32_t slen` @4 · anonymous union @8 (widest members 8B: pointers, `int64_t`, `double`) ⇒ `sizeof`=16, natural alignment=8, zero tail padding (16 is already a multiple of 8). **Matches the brief exactly.**
- `DT_DATA = 0x70 = 112` is the highest enumerator under the current numbering. **Matches the brief exactly.**
- `DT_DATA_STRIDE` (`#define DT_DATA_STRIDE 8`, descr.h:9) has exactly one live reference tree-wide — the `_Static_assert` at descr.h:45-46. **Confirmed vestigial, as the brief states.**
- `IR_OP_COUNT` (`src/contracts/IR.h:150`) and `kind_names[IR_OP_COUNT]` (`src/contracts/scrip_ir.c:7`) exist exactly as described. Did not enumerate the claimed 128/129-named split this step — that's implementation-phase work, not census.

## 2. CENSUS (a) — C TAG TESTS ("642" claimed)

Grepped `src/` (`*.c`/`*.h`/`*.cpp` — confirmed the only live C-family extensions; `.cs`/`.java`/`.il`/`.wat` are dormant non-x86 backends, out of scope) for every shape that reads `DESCR_t.v`:

| shape | count |
|---|---|
| `.v == DT_x` / `->v == DT_x` (either order; reversed `DT_x == ...v` = 0) | 501 |
| `.v != DT_x` / `->v != DT_x` | 86 |
| `switch(...v) { case DT_x: }` — a shape the brief's prose didn't name | 10 switches / 77 case labels |
| relational (`>=`/`<`/`>`/`<=` against `DT_DATA`) | **3 — matches the brief exactly** (2 sites in `driver_data.c` + 1 `core.c:437` `>= DT_P`) |

No combination of these (== alone 501, ==+!= 587, ==+!=+case 664) lands on the brief's cited 642. Reporting the breakdown rather than forcing a match — the discrepancy is real and worth HQ knowing, not a transcription slip resolvable from here alone. All four shapes are uint8_t-safe by the same argument the brief gives for the `==` case: every named `DT_` constant is ≤112, so a byte-narrowed `v` compares identically under `==`, `!=`, `switch`/`case`, and the 3 relational tests.

## 3. CENSUS (b) — ASM + TEMPLATE 'cmp reg, DT_x' SITES ("65 asm + 103 template = 168" claimed)

- **asm** (`src/runtime/rtx/*.S`, 17 files): `cmp <reg32>, DT_x` — **65, matches the brief exactly.** Registers: edi 26 · edx 15 · eax 16 · ecx 6 · esi 2.
- **template** (`src/templates/bb_*.cpp`, 132 files): `x86("cmp", "<reg>", (long)DT_x)` and its `std::to_string((long)DT_x)` variant — **106, not 103.** Breakdown: 104 sites use the plain `(long)DT_x` cast (eax 85 · edx 11 · ecx 7 · r8d 1); the other 2 (`bb_field_get.cpp:22,37`) wrap it as `std::to_string((long)DT_FAIL)` — same shape, the kind of thing a naive grep undercounts, though that alone doesn't close the full 3-site gap to 103. Zero reversed-operand or non-`cmp`-opcode DT_ tag tests found. **Combined actual total: 65 + 106 = 171, not 168.**

Both counts are receipts-backed (exact commands + raw match lists run this session); can hand the precise greps to whoever reconciles against HQ's original 168.

## 4. CENSUS (c) — POINTER/TYPE-ALIASING HAZARDS (the class HQ explicitly did not measure)

Checked every way existing C code could break once `.v` narrows from a 4-byte `DTYPE_t` to a `uint8_t`:

| hazard | count |
|---|---|
| `&d.v` / `&d->v` (address-of the tag member alone) | **0** |
| `DTYPE_t *` anywhere in `src/` (param, local, cast) | **0** |
| `(DTYPE_t*)&d`-style raw cast off a descriptor address | **0** |
| `sizeof(DTYPE_t)` / `sizeof(...v)` | **0** |
| `DTYPE_t` as a plain by-value function parameter type | **0** |
| bitwise/shift ops directly on `.v`/`->v` (`<<` `>>` `\|` `&`) | **0** (1 raw hit was `y.v || ...`, logical-or chaining, not a bitwise op on the tag) |

Two tooling traps hit while building these greps, worth flagging for the next seat: (1) this shell's `grep` is `ugrep`, and a bare leading `-` in an `-e`-less pattern (e.g. `'->v == DT_'`) is parsed as an option flag and fails loudly instead of matching — always pass such patterns via `-e`. (2) A naive `&\w+(\.|->)v\b` address-of pattern picks up `&&` (logical-and) followed by an unrelated AST-node `.v` union member (`t->v.sval` etc. on `TT_VAR`/`TT_FNC` parse nodes — a *different* `.v` entirely) as false positives: 218 of them on the first pass. Fixed with a PCRE lookaround (`(?<!&)&...(?![.\w])`) excluding both `&&` and further `.` drill-down.

**Bottom line: this hazard class is clean.** Nothing today takes the tag member's address or treats it as a full-width standalone type, which is good news for the row — the field split itself should be mechanically safe on the C side, independent of whatever the true 642/103/168 reconciliation turns out to be.

## 5. SCOPE OF THIS STEP

This is the row's FIRST STEP only: read the ARCH doc, run the three censuses, post counts before changing anything. **No source was edited.** None of the row's DONE-WHEN criteria (struct split, `_Static_assert` pinning `sizeof`, the 168(+3)-site asm/template conversion, killswitch, corpus/gate/pristine proof, core-dump creator/modifier witness) are attempted here — that is deliberately left for the next step now that a measured baseline exists. `ARCH-SNOBOL4-RTX.md` §9 question is open in HQ's inbox (`q-descr-stamp-fields`); claim `descr-stamp-fields` stays held, not done.
