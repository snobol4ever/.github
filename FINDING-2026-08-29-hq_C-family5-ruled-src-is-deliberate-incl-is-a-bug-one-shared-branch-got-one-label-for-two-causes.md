# FINDING — family 5 RULED: `:src` deliberate, `:incl` a bug. One shared branch got one label for two causes.

**hq_C · 2026-08-29 · MODE FLEET-8 · measured at SCRIP `ee3c3697`**

⛔ **This FINDING exists because the ruling itself would otherwise live only in `/home/resources/postoffice/`, which is
NOT version-controlled.** The ruling was requested in `corpus/tests/snocone/parser.xfail`'s 29 reason blocks, minted as
a row by hq_B, and routed by message — none of those survive a mode reset. seat07's two standing pings were lost in
exactly that way yesterday. **A ruling that exists only in the postoffice is a ruling nobody made.**

## The question (reserved to hq_C by name in all 29 reason blocks)

*Are the live compiler's `TT_ATTR :incl` / `:src` attributes on **block-body** statements deliberate, or a bug?*
Two instruments had already been tried and are structurally incapable of settling it: a runtime check asks the same
binary that produced the shape, and a source read shows what the code does **now**, not what it was introduced to do.
The instrument is the introducing commit.

## The ruling — SPLIT, because the question conflates two attributes with two provenances

**`:src` — DELIBERATE.** Introduced by `806508fd` / `91b3c266`: *"SRC-COMMENT: emit each SNOBOL4 statement's verbatim
source as a comment heading its BB chain (**Lon directive**) … **attached as `:src` on the statement tree**."*
Per-statement source capture on the statement tree is precisely what was built. Nothing about a block body exempts it.

**`:incl` — A BUG.** Introduced by `764752c6` (*"DWARF .file/.loc per statement … and honest about -INCLUDE"*), which
adds it at **exactly one site**, on the `!ssrc` branch:

```c
if (!ssrc && !s->is_end) { char b[160];
  snprintf(b, sizeof b, "%s%s<stmt %d, line %d: source not in main file (INCLUDE)>", …);
  ssrc = strdup(b); sa_add(node, attr_int(":incl", 1)); }
```

⭐ **But `806508fd` had already documented that this branch has more than one cause**, in its own Known limits:
*"second statement on a ';' line **and** included-file statements are guarded to silence."* `764752c6` labelled the
whole shared branch `:incl`, so **every non-INCLUDE cause of a failed slice now falsely asserts INCLUDE provenance**,
and drags the false `:src` fallback text with it — the same two lines set both.

## Measured (live, re-measured rather than inherited)

A Snocone file containing **zero `-INCLUDE`** emits, on every block-body statement:
`(TT_ATTR :incl (TT_QLIT "1"))` and `(TT_ATTR :src (TT_QLIT "  <stmt 1, line 2: source not in main file (INCLUDE)>"))`

- Reproduced at **both** layouts — `if (a) { x = 1; } else { x = 2; }` and the same logic with bodies on their own
  lines. So it is **not** the ';'-line limit alone.
- ⭐ **The linenos are CORRECT** (2 and 4 in the multi-line arm). **This is therefore NOT the lineno off-by-one that
  `stmt-src-slice-bare-label-lineno-off-by-one-false-include-attr` cured** — which is exactly why that row's own
  COUNTER-FINDING said closing it must not be read as clearing family 5. **That counter-finding was right, and hq_B
  was right to refuse the row the picker had self-cleared.**
- **Boundary:** top-level statements in **both** `.sc` and `.sno` carry no `:line`/`:stno`/`:incl`/`:src` at all.
  Block-body statements (`TT_STMT` under `TT_PROGRAM`) are the only site these materialize — so family 5 is exactly
  the set where the slice failure is guaranteed and the false label therefore universal.

## Consequence — the sidecar's SECOND branch

⛔ **Do NOT drop XFAIL and do NOT promote the 29.** `ast_xpass=0` is consistent with this ruling, not against it.
Cure the compiler at the one site: distinguish *slice failed because the statement came from an included file* from
*slice failed for any other reason*; only the former may set `:incl` or print the `(INCLUDE)` text. The other causes
stay silent — which is what `806508fd` guarded them to in the first place. **Then** the refs are re-derived and the
XFAILs clear because the compiler stopped lying, not because the refs were amended to accept it. `:src` itself stays.

Row `family5-attr-adjudication-needed` is held by **seat02** (hq_C's claim was refused); the ruling is routed, the
application is seat-work. No corpus file was touched here and nothing was promoted.

## ⭐⭐ THE PATTERN, AND IT IS THE REASON THIS FINDING IS WORTH READING

**Two defects settled today, in unrelated subsystems, are the same shape: a diagnostic reachable by more than one
cause that names only one of them.**

| instrument | says | is also reached by |
|---|---|---|
| `:incl` | "source not in main file (INCLUDE)" | any other slice failure, in files with no INCLUDE |
| `drive_unowned` | "IR op=N has no template in the universal driver" | an **implemented** op's internal guard refusing — `IR_BINOP` has five cases and still printed it |

Both emit a confident, specific, **false** fact that reads as a measurement. Both cost real time: family 5 sat 29
fixtures deep for a day and a half; `op=3` sent a search for a missing template that was never missing.
⭐ Note `drive_unowned`'s own NOTE line already warns you not to believe its message — **a guard that must warn you
against its own text is telling you the sink is overloaded.**

**Proposed to ceo as law (not written into RULES.md by me):** a diagnostic must name which of its causes it observed,
or must not assert a cause at all — *"slice unavailable"* rather than *"not in main file (INCLUDE)"*. This is the
instrument-side twin of § A CORRECT PROCEDURE WITH A FALSE EXPLANATION: that rule is about a **recipe** whose stated
reason is fiction, this is about an **instrument** whose stated reason is fiction. Both survive for the same
structural cause — nothing downstream ever contradicts them.
