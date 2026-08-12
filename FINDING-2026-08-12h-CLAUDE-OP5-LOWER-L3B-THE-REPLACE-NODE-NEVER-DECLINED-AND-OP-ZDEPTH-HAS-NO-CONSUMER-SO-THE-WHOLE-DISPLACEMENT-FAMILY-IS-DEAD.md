# FINDING 2026-08-12h — LOWER L-3b: the replace node never declined, `op_zdepth` has no consumer, and the displacement family is dead

**Seat:** LOWER (`GOAL-SN4-HOME-LOWER.md`) · **Session:** s37 (Opus 5) · **HEAD at start:** SCRIP `67e9383c`
**Emitted-byte change: ZERO.** Board at close: **3 PASS / 10 FAIL — identical BY SET to s36's floor.** No regression, no gain.

---

## SUMMARY

L-3b's step 1 instructed the seat to *"find why the replace node declines the ZD arm."* **The replace node does not decline.** Measured, first command of the session. Everything downstream of that premise in s35/s36's cursor is therefore built on a false floor, and three further inherited claims fell with it. This session produced **no fix**; it produced a **corrected map** and **five instruments**, and it **closed off the entire displacement-tuning approach** by exhausting it.

The honest headline: *four sessions have now looked for a displacement. There isn't one.*

---

## 1. FALSIFIED: "the replace node declines the ZD arm"

`SCRIP_ZD_DIAG=1` on `l3_spl_span_nonterm`, run `h=4`:

```
[ZD] h=4 r=6 i=10 IR_MATCH_END      K=0  zout=32
[ZD] h=4 r=7 i=11 IR_LIT_STRING     K=16 zout=48
[ZD] h=4 r=8 i=12 IR_MATCH_REPLACE  K=0  zout=48
```

Every node admits. No `DECLINED` line. `zon[12]=1`.

**Why it cannot decline:** `zd_wl_kind` (emit.cpp:1899) short-circuits at **line 1909** — `if (!(icn_cells_graph || pl_cells_graph)) return 1;` — the *UNIVERSAL ARM*. SN4 sets neither flag, so **the entire per-kind whitelist beneath it is Icon/Prolog-only and structurally unreachable from SNOBOL4.** Line 1915's own comment says as much for its own case (*"SNOBOL4 has no lexical locals … zero customers"*).

There is no guard separating the start_off-64 group from the start_off-48 group. That split has another cause.

## 2. FALSIFIED: the C-9 `op_zdepth` correction can reach `bb_match_replace`

`emit.cpp:841` stages `op_zdepth = g_zd_k + g_zd_zunder`, and three sessions of cursor text describe `FRQ` as `[rsp+off+op_zdepth]`.

`bb_match_replace.cpp` reads via `FR`/`FRQ` → **`x86_zop()`** (x86_asm.h:1021–1027). **`op_zdepth` appears nowhere in `x86_zop`.** It is read only by `x86_ztos` (x86_asm.h:1040), the `ZTOS`/`ZTOSD` family, which this template never calls. The four-mode contract at x86_asm.h:1046–1051 names them as *different modes*: `FR`/`FRQ` are mode 4 ("LEGACY FRAME"), `ZTOS` is the value-spine arm.

`g_zd_zunder` is computed correctly (16 literal / 80 concat — matching C-9's own measured numbers) and then handed to a field **nobody downstream reads**. The template's only live lever is `op_zpat`.

## 3. FALSIFIED: `op_zpat` is the non-carving class's field

`emit.h:627`, its own authorship comment: *"bytes of dynamic zeta cells carved by PATTERN-INTERIOR match primitives (**TAB/RTAB/POS/RPOS** — they pop only on their FAIL edges)."*

That is the **carving** class, which s36 correctly split out as a **separate defect**. But the implementing predicate is `op >= IR_MATCH && op <= IR_MATCH_VALUE` — **broader than the documented intent** — so it incidentally sums SPAN's K=16.

⇒ `zpat=16` on a SPAN witness is a **formula artifact, not evidence.** Confirmed: `l3_spl_tab_nonterm` (carving) and `l3_spl_span_nonterm` (non-carving) both report `zpat=16, head_fp=16`, yet fail with **completely different signatures** — TAB `S=[XX*YYYY]` (bounded, `end` correct) vs SPAN `S=[XXX*]` (catastrophic). Equal fields, different diseases. **s36's two-defects ruling is reconfirmed from a second direction.**

## 4. FALSIFIED — MY OWN ERROR: "`fc_head_fp` is dead code"

I grepped **two files**, found no `fc_head_register` call, and concluded the `fch[]` table was never populated. **Wrong.** Full-tree grep:

```
src/lower/lower_snobol4.c:1828:  fc_head_register(head, fp_stmt);
```

`fc_head_fp` returns **16** (SPAN) and **0** (pure LEN) — live, LOWER-registered, load-bearing. Direct instrument (`SCRIP_FCDISP_DIAG`) settled it: `tail_release=0 br=-1 head_fp=16`.

⛔ **Rule earned: grep the whole tree before declaring anything dead.** I recorded this against myself because a "dead code" claim is exactly the kind that gets inherited unexamined.

---

## 5. THE MEASUREMENT — and why it kills the displacement family

Five env-gated instruments landed (`SCRIP_ZPAT_DIAG`, `SCRIP_REPL_ADDR_DIAG`, `SCRIP_MEND_ADDR_DIAG`, `SCRIP_EDRIVE_END_DIAG`, `SCRIP_FCDISP_DIAG`). Writer and reader, one run, one coordinate system:

| witness | `op_fc_disp` | WRITER stores | READER loads | delta |
|---|---|---|---|---|
| `len_pure` (**PASS**) | 0 | `rsp+80` / `rsp+104` | `rsp+48` / `rsp+72` | **32** |
| `span_nonterm` (FAIL) | 16 | `rsp+96` / `rsp+120` | `rsp+32` / `rsp+56` | **64** |

Writer arm (bb_match_end.cpp, `rfc()` + `ZC_FRAME_RSP`; **confirmed live**, `rfc=1 zc_frame=2` both) = `[rsp + op_off + op_fc_disp + 32]`. Reader has **neither** term.

⛔ **THE PASSING ROW IS THE DISCRIMINATOR.** `len_pure` reads **32 below** the writer's address **and is correct**. Therefore RSP is **not equal** at the two program points, and *"make the reader's N match the writer's N"* is the **wrong target**.

Three variants, all built, all run against the full board:

| reader expression | `raw_start` | verdict |
|---|---|---|
| `op_off - op_zpat` (HEAD) | **3** | FAIL |
| `op_off + op_zfc + 32` (writer-matching) | **0** | FAIL |
| `op_off + op_zfc` (32 cancelled) | **18** (=slen) | FAIL |
| *correct* | **10** | — |

Controls `{len_nonterm, len_pure, lit_len}` held PASS in **all three** variants (the `op_zfc==0` fallback is numerically identical to HEAD).

**A quantity that lands 3, 0, and 18 while never landing 10 is not a displacement needing one more tweak.** The reader is reading a cell **nobody wrote the cursor into**. This is s34's *"find the writer, not an offset"* — prematurely discharged by s35's *"the writer was never missing"* — **re-earned the hard way.** s35's discharge was correct that `MATCH_BEGIN`/`MATCH_END` write *somewhere* correctly; it did not establish that they write where `MATCH_REPLACE` looks at the moment it looks.

---

## 6. WHAT LANDED (and what deliberately did not)

**Landed, inert:** five instruments; `op_zfc`/`g_zd_zfc` — a carrier staging `fc_head_fp(head)` at the `g_zd_zpat` choke, surviving the per-node `op_fc_disp` reset (`op_fc_disp` is `-1` by the time `IR_MATCH_REPLACE` emits — verified via `SCRIP_EDRIVE_END_DIAG`). **Staged and printed; no emitter arm consumes it.**

**Deliberately NOT landed:** the behavioural change. It moved the read to the writer-matching address and the board stayed **3 PASS / 10 FAIL — identical BY SET**. Per the goal's own judge-BY-SET law, a new struct field plus a codegen change across the whole non-carving class **with zero measured benefit** is not justified. Reverted; baseline re-proved by re-running the board.

**Byte-identity:** diff audited line-by-line — every hunk is an env-gated `fprintf`, the unconsumed field, or lambda-wrapping of two `x86("mov",…)` calls whose arguments are **character-identical** to HEAD's. Board result independently confirms. Regen ×3 **not triggered** (no emitted-`.s` change is possible).

---

## 7. LAND MINES FOR THE NEXT SEAT

- ⛔ **`x86("comment", …)` returns an empty string ALWAYS** (x86_asm.h:1590, SN4-ASM-CRIT/s173). A diagnostic written that way is **silently inert, not broken.** Use `fprintf(stderr,…)`. Cost one build cycle.
- ⛔ **`FR`/`FRQ`/`x86_zop` return a shared static rotating buffer** (`static char b[16][48]`). Capture to `std::string` **immediately**; re-deriving later in a chain can read an aliased slot.
- ⛔ **`--dump-zeta` is a DIFFERENT coordinate system from the template's `op_off` arithmetic.** I nearly published a conclusion comparing them. The dump documents `head.cursor` at `+48` while the template reads `op_off+0`. Do not cross them without proving the base.
- ⛔ **NO GDB IN THE CONTAINER** (`gdb: not found`). The MONITOR-FIRST gdb step is unavailable; runtime facts need emitted-trace instruments instead. This affects more rungs than this one and belongs in BOARD's tooling debt.
- ⛔ **The shell `[` builtin mis-parses the board's bracketed output.** `[ "$g" == "$w" ]` printed a false all-FAIL. Use `=`, and `tr '\n' '|'` before printing.
- ⛔ **Two `case IR_MATCH_END:` / two `case IR_MATCH_REPLACE:` exist** (`walk_bb_node_inner` ~984 and `emit_drive` ~1326/1347). They are **sequential, not competing**: `emit_drive` → `DRIVE_FILL` → `walk_bb_node` → `walk_bb_node_inner` → template. I misread them as rival paths and burned several hops on a "stale carryover" theory that measurement killed.

---

## 8. HONEST ACCOUNTING

Four wrong turns, each caught by instrument before it reached a conclusion, each costing real budget: (i) a sign-flip tested blind; (ii) a `--dump-zeta` cross-coordinate comparison; (iii) a "dead code" call from a two-file grep; (iv) a "stale carryover" theory from misread dispatch. The pattern is the same each time — **reading code to form a theory, instead of instrumenting to get a number.** RULES §1 says exactly this, and the three findings that eventually stuck (§1, §2, §5) all came from a `fprintf`, not from reading.

The session's real deliverable is **subtraction**: L-3b's stated step 1 is void, `op_zdepth` is void for this template, `op_zpat` belongs to the other class, and the displacement family is exhausted. A seat that inherits this file will not re-spend those four.
