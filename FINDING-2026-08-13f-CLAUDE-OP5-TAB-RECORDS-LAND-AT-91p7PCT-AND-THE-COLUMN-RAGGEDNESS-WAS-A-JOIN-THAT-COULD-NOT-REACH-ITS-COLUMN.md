# FINDING 2026-08-13 — CLAUDE-OP5 — TAB RECORDS LAND AT 91.7% AND THE COLUMN RAGGEDNESS WAS A JOIN THAT COULD NOT REACH ITS COLUMN

**Goal:** GOAL-RBP-EARN (s63) · **Repos:** SCRIP `add2872a`, `852b7db4`, `8e35d148` · corpus `c7d4dd31`, `7a4e5d38`

---

## 1. What was asked

Lon, in-chat: *"Finish emitted ASM formatting code. Add TAB delimited to save space. Make all
the columns line up nicely. Make all the labels and instructions nicely compacted."*

The TAB design was **banked by s62b and never implemented** (runway exhausted at ~97% context).
This session implements it and then addresses the column ask, which turned out to be a
**separate, measurable defect** — not a restyling.

---

## 2. ⭐ THE SINK NO LONGER SNIFFS TEXT — FIELD OCCUPANCY REPLACED THREE HEURISTICS

`x86_4col_kind` is DELETED. In its place `x86_rec_split` parses a line into an `x86_rec_t`
(`label` / `opcode` / `operands`) and `x86_rec_kind` reads the KIND off **occupancy**: an empty
opcode field *is* a label-only line. The three heuristics the banked design named are dead on
the TAB path:

| heuristic (pre-s63) | status |
|---|---|
| first-token whitespace scan | gone — the separator is the field boundary |
| `':'` suffix = label detection | gone — field 0 *is* the label |
| `rep`/`lock` prefix special case | gone — a prefixed mnemonic is simply what the opcode field CONTAINS |

**The s62b trap was real and is handled as the design predicted:** label-only lines and the `#@`
note marker are now *records with empty fields*, and kind keys off occupancy, never off text.

**LEGACY LINES SURVIVE BY CONSTRUCTION.** A record with no TAB falls to the whitespace parse.
This is what made the conversion *stageable* instead of a cutover — and it is why the rung could
land green at 91.7% coverage rather than waiting on 100%.

---

## 3. ⛔ TABS CANNOT COLLIDE WITH CONTENT — VERIFIED BEFORE THE SEPARATOR WAS CHOSEN

`x86_asm_str_escape` (x86_asm.h:868) and `emit_str.cpp` (:69, :165) both render a literal tab as
the two characters `\` `t`. **No raw tab can reach a `.string` operand.** This was checked
*before* committing to TAB as the delimiter, not after — the alternative was discovering it via a
corrupted string constant in a program nobody runs often.

---

## 4. COVERAGE IS 91.7% OF RECORD-BEARING LINES — AND THE DENOMINATOR MATTERS

Converted in `x86_asm.h`: 65 mnem+operand literals · 3 no-operand · 29 inline-operand ·
15 appended-literal (the RTCC wb/rl text) · 5 label emitters · **7 variable-mnemonic builders**.

⭐ **THE VARIABLE-MNEMONIC BUILDERS WERE INVISIBLE TO A LITERAL-ONLY SWEEP.** `std::string(" ") +
mnem + " " + rm + ", " + reg` carries no mnemonic literal, so the first regex pass could not see
the ALU and jcc families at all. Coverage read 36% → 69% → 76% → **91.7%** as each shape was
found. *A grep over literals is not a census of producers* — the same lesson as the s60 "census
is blind to unported symbols" class.

| measure | value |
|---|---|
| record-bearing lines, demo corpus | 176,486 |
| TAB records | 161,751 |
| legacy residue | **14,735 (8.3%)** |

**Residue owners (NOT converted, honest list):** `src/driver/scrip.c` m4 startup hoist — 250
`emit_textf("  …")` **format-string** sites; `emit.cpp` raw blobs; `xa_*.cpp` section/data
directives (`.quad` 1910, `.section` 1378, `.string` 975, `.byte` 656, `.globl` 293).
Converting format strings needs an `emit_recf(mnem, fmt, …)` choke point — a real rung, deliberately
not started at 70% context.

---

## 5. ⭐ THE COLUMN ASK WAS A MEASURED DEFECT, AND THE FIX IS ONE RULE

Column census over the 24-program demo corpus, BEFORE:

| column | correct | **ragged** |
|---|---|---|
| opcode (24) | 127,723 | **777 at 25/26/27** |
| GOTO (78) | 18,433 | **8 at 80/81** |
| note (88) | 8,989 | 0 |

Root cause of both: `x86_4col_pad`/`x86_4col_to` clamp `pad < 1 → 1`. A join whose pending line
had already **reached or passed** its target column got one space instead of alignment, landing
one-to-three columns right. An over-long label shoved its instruction; a long operand run shoved
its `;`.

**ONE RULE FIXES BOTH: decline a join that cannot reach its column.**
`pend==1 && pw>=24` → label keeps its own line, instruction beneath starts CLEAN at 24.
`pend==2 && pw+1>=CJ` → jump keeps its own line, still AT the GOTO column.

AFTER: **ragged opcode 0, ragged GOTO 0.** Cost +1,578 lines (+1.08%) — exactly the declined
joins. Still ~1.30× denser than pre-JOIN.

The note-drop test now consults the **real rendered width** rather than the kind-only prediction,
so it agrees with the fit test instead of dropping a note for a join that then gets declined.

---

## 6. ⭐ THE GATE WAS WRITTEN BEFORE THE CODE AND IT CAUGHT A REAL DEFECT

`scripts/test_gate_asm_tabs_identity.sh` — TABS=0 vs TABS=1, md5 per program. It fired on the
**port-label producer smuggling a cosmetic leading space INSIDE the label field**
(`x86_reclbl(std::string(" ") + x86_portname(port))`), which would have shifted every
`nN_..._α:` label one column left across all 23 programs. The pre-TAB sink stripped that space;
the TAB sink cannot, because a label field holds the label and nothing else.

**Invariant proved the strong way — object code, not text:** all 23 assemblable demos assemble
(`as --64`) to **BYTE-IDENTICAL `.o`** against the pre-rung HEAD baseline, across BOTH rungs.
Only padding and line breaks moved.

---

## 7. ⛔ TWO FALSE ALARMS I RAN DOWN INSTEAD OF RECORDING AS FACT

**(a) "Aggregate md5 changed after the sink refactor."** It had not. My aggregate hashed
`md5sum <path>` output, so the **filenames** were in the hash. Per-file comparison showed 24/24
identical. Path-independent aggregation used thereafter.

**(b) "MODE-3 PASS=0 FAIL=18 — I broke execution."** I did not. Rebuilt the **pre-rung tree** and
measured: PASS=0 FAIL=18, *the same 18 programs*. These demos read stdin and their `.ref` was
baked with real input; `< /dev/null` cannot reproduce it. Mode-3 is untouched **by construction**
(`x86_4col` returns early for `MEDIUM_BINARY`; `x86_rec` appears only in TEXT arms) — but the
baseline was measured rather than argued. `board_sno15_ident.sh`: TRI-IDENTICAL 2/15, m3 bad=13,
m4 bad=13, **m3 and m4 agreeing on every failure** — matches FINDING-2026-08-12i's documented
13-of-15, so no MODE34 violation introduced.

`porter` fails to assemble at HEAD **and** after — the pre-existing `.Lx<N>_40` dup-label class
(s60 OWED item 3). Not this rung.

---

## 8. NO NEW GLOBALS

`x86_tabs_on()` uses a function-local `static int` cache of `getenv`, identical in kind to the
existing `x86_4col_joinon()`/`SCRIP_ASM_COLUMNS` gates. **No file-scope mutable state was added
in any repo.** No banner ask was required and none was made.

---

## 9. OWED

1. **Push credential** — 3 SCRIP + 2 corpus commits unpushed; asked in chat.
2. **Residue conversion** — `emit_recf(mnem, fmt, …)` choke point for scrip.c's 250 format-string
   sites; then `emit.cpp` raw blobs and `xa_*.cpp` directives. Until then the whitespace parse in
   `x86_rec_split` must stay.
3. **598 lone jumps** park at the GOTO column with nothing to their left. Left ALONE deliberately —
   that is the four-column BB format working as specified, and it is Lon's call whether a bare goto
   should compact left. Flagged, not "fixed".
4. Inherited and UNTOUCHED: fence1 U-2 stale header comment · dead zls ALT-trio grant in
   `zeta_storage.c` · anchor-rung decision (11 witnesses + 056) · corpus-wide sweep+census.
