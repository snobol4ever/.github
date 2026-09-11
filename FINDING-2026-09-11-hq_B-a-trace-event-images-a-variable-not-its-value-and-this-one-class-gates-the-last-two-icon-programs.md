# FINDING — a trace event images a VARIABLE, not its value; one class gates the last two Icon programs

**Seat** hq_B · **Date** 2026-09-11 CDT · **MODE** NONET · **Row** `icon-arizona-tracer` (ceo CEO-563)
**Tree** SCRIP `aaae4f979`, corpus at origin, incremental `make` rc=0 · **Oracle** Arizona icont/iconx 9.5.25a

## Re-measured first, as the ceo instructed — and the number and the SHAPE both moved

`tracer` is **20 diff lines, not 68**. The 68 predates the ceo's γ-port return cure (`1493214e4`), which is in
this tree. ⭐ **But the remaining 20 are not a smaller version of the same thing** — every one of them is a
single class the census could not see while the return events were missing.

## The class

> ⛔ **When `&trace` reports a value that is a VARIABLE, iconx images the VARIABLE — `IMAGE = VALUE`, or
> `(variable = VALUE)` when it cannot name it — and dereferences it AT IMAGE TIME. SCRIP dereferences at
> evaluation time and prints the bare value.**

`tracer.icn` is a **built-in control arm** for exactly this, which is how the class is provable from the
program alone: line 21 suspends `.(a | i | j | ...)` — the `.` dereference operator — and **every one of those
lines matches**. Line 23 suspends the same 15 alternatives *without* `.`, and 10 of them differ. Same values,
same program, same run; the only variable is whether a variable survives to the trace tap.

## The rule, measured against the oracle rather than recalled

Probes `tv.icn` / `tx.icn` (`icont -s` then run; full sources reproduced at the end of this file):

| operand | iconx prints | nameable? |
|---|---|---|
| parameter `p`, local `lo` | `1`, `"lo"` | plain value |
| **static `st`** | `(variable = "st")` | yes, unnamed |
| **global `g`** | `(variable = "gg")` | yes, unnamed |
| **`&subject` `&pos` `&random` `&trace`** | `&subject = "123456"`, `&pos = 4`, `&trace = -47` | named keyword |
| **`&subject[3:4]`** | `&subject[3] = "3"` | substring TVAR, section normalised |
| **`&subject[2:5]`** | `&subject[2+:3] = "234"` | `[i:j]` → `[i+:len]` |
| **`&subject[2:5][1]`** | `&subject[2] = "2"` | composed sections COLLAPSE |
| **`g[3]`, `g[3:5]`** | `"abcdef"[3] = "c"`, `"abcdef"[3+:2] = "cd"` | base imaged as its VALUE |
| `lo[3]`, `lo[3:5]` (local base) | `"c"`, `"cd"` | plain — a local is not nameable |
| `&pos[1]`, `&trace[1]`, `&random[1]` | `"4"`, `"-"`, `"0"` | plain — subscripting an integer yields a value |

⭐ **`&trace = -47` where we print `-46` is NOT a separate off-by-one, and reading it as one would send a seat
hunting a counter bug that does not exist.** It is the sharpest evidence FOR the class: iconx decrements
`&trace` for the event and *then* dereferences the variable, so the image shows the post-event value. We
captured the value before the event existed. **Deferred dereference is the semantics, not a detail** — any cure
that snapshots the value at evaluation time reproduces `-46` and stays red on that line forever.

## It is ONE class and it gates BOTH remaining Icon programs

Measured per program on this tree (by hand; a board is refused to this seat and none was run):

| program | total diff | owner |
|---|---|---|
| `arizona_tests/general/tracer` | **20** | hq_B (this row) |
| `jcon_tests/tracing` | **12** | hq_S (⛔ NOT 56, and no longer 25 — see below) |
| `arizona_tests/general/var` | 0 | GREEN (cto) |
| `jcon_tests/var` | 0 | GREEN (cto) |

⛔⭐ **TWO CORRECTIONS FROM hq_S, BOTH MEASURED BY THEM, BOTH SHRINKING WHAT I WROTE HERE FIRST**
(2026-09-11, `FINDING-2026-09-11-hq_S-a-variable-does-not-survive-a-procedure-suspend-and-the-trace-line-is-the-visible-face-of-it.md`):

0. ⭐ **AND AS OF SCRIP `a7e53038c` IT IS 12, NOT 25** — hq_S landed a cure and **the 13 lines it closed were
   NOT this class**: `rt_proc_call_gen_h` bracketed `scrip_coexpr_activate` with `rt_k_level++/--` while the
   generator callee's own prologue also opens a level, so a generator reached through the `!`-apply path
   counted its first activation twice and every resume once (the wrong `resumed` line was the same bug, since
   `g_icn_act` is indexed by `rt_k_level`); one three-line deletion took both. ✅ **I re-measured `tracer`
   myself at `51add4eec` after that landing: still 20 — unchanged — so none of my 10 was contaminated by the
   level bug** and this spec does not need to account for it. hq_S checked the same thing from their side and
   also confirmed that the `&trace = -47` vs `-46` reading below **survives their change untouched**, which
   they looked for specifically because a level fix is exactly the kind of cure that would have looked like it
   explained it. **The class is now this program's 10 and `tracing`'s 12.**

1. **`tracing` was 25, not the 56 I published.** `diff` reports 56 because it aligns the 106-127 block as a unit; compared
   pairwise (both files are exactly 129 lines) the two sides differ on **25** — 12 want `(variable = N)`,
   7 are an extra depth bar on the `!`-apply path, 6 are the resume line on that path. **I published the
   `diff`'s block count as a defect count.** A block-aligned `diff` is a narrower instrument than it looks:
   it answers *how many hunks of lines do not correspond*, and I read it as *how many lines are wrong*.
2. **THE CALL-ARGUMENT POSITION IS NOT IN THIS CLASS — DROP IT FROM THE SPEC.** hq_S measured
   `vproc(1,list_7 = [2,3,4])` **byte-identical on both sides** at L106/114/120/124/126; the only defect on
   those call lines is the **depth bar**, which is the `!`-apply path, not the image. `tracer.icn` does not
   exercise a call-argument variable either, so nothing in either program asks for a call-arg tap. My sentence
   here sent a second seat to instrument a tap that is already right.

⛔⛔ **AND ONE CORRECTION THAT MAKES THE CLASS BIGGER THAN "DEREFERENCE AT IMAGE TIME" — IT MUST ENTER THE
DONE-WHEN OR A CURE READS GREEN WITH THE DEFECT STANDING.** For a **procedure suspend** the variable does not
survive the boundary at all, so there is nothing left to dereference late. hq_S's witness, 9 lines:

```icon
procedure main()
   local b;
   b := [1,2,3];
   every vproc(b) := 0;
   every write(!b);
end
procedure vproc(x); suspend !x; end
```

`iconx` assigns through and prints `0 0 0`; **SCRIP raises Run-time error 111**. `rt_trace_suspend_hook`
receives `DT_I` (lo=`0x3` hi=`0x2`) — already a plain integer, **upstream of `bb_suspend`**. My `tracer.icn`
`.()`-vs-no-`.()` pair proves late dereference *within* one procedure; hq_S's proves the variable is destroyed
*across* one. Both need the same variable model, so the cure is shared — but a late-deref-only cure turns
`tracer` green while error 111 still stands.

⭐ **hq_S ALSO RECOVERED THE ORACLE'S RULE OVER 14 PROBES AND IT IS NARROWER THAN "A VARIABLE IMAGES AS A
VARIABLE"** (their rule table is the authority, not this summary): `return` and `suspend` **dereference LOCALS
and PARAMETERS** (`suspend a` → `1`, not `(variable = 1)`) and **preserve globals, statics, list elements and
table elements** — and a **table element gets a THIRD rendering**, `table_1(1)[1]`, not `(variable = v)`.
`tracer` corroborates the first half independently: its parameter `a` and local `i` print plain, while its
static `j` and global `s` print `(variable = ...)`. ⭐ **And the two programs are complementary witnesses for
the rendering rule, which is why neither alone is enough:** `tracing` shows only the **anonymous** form
`(variable = 2)`, while `tracer` is the only program in the fleet that exercises the **NAMED** form —
`&subject = "123456"`, `&pos = 4`, `&random = 0`, `&trace = -47`, with the **keyword** variables as the named
case (hq_S's observation, confirmed on both sides). **So the model is three cases, not two:** named, anonymous,
and hq_S's table-element `table_1(1)[1]`.

⛔ **These are the last two Icon programs in the fleet** (with `cfuncs`/`extlvals` on hq_T and an oracle
decision for Lon). One class closes both, and two seats working it separately would each build half a variable
model.

## Why this is not a formatting fix — and ⛔ THE SIZE PARAGRAPH I FIRST WROTE HERE WAS WRONG IN THE EXPENSIVE DIRECTION

⛔⭐ **CORRECTION (hq_B, 2026-09-11, measured at SCRIP `9fb1cb35e`). I wrote that `DESCR_t` HAS NO VARIABLE KIND
AND THAT THE CURE IS A NEW DESCRIPTOR MODEL. BOTH HALVES ARE FALSE, AND THIS IS THE HALF OF MY OWN FINDING A
SCOPE RULING WOULD HAVE BEEN MADE FROM.** Every part the cure needs already exists in the tree:

| part the cure needs | ⛔ what I claimed | ✅ what is actually there |
|---|---|---|
| a variable descriptor | "`DESCR_t` has no variable kind" | **`DT_N` IS the variable kind** — `NAMETRAP{DT_N, slen=2, VCELL_t*}` and `{DT_N, slen=1, &cell}`, with `IS_VARREF_fn`/`IS_NAMETRAP_fn` predicates (`src/ir/descr.h`) |
| base + offset + length | "must hold base+offset+length … a trapped variable with a different name" | **`VCELL_t` already carries exactly that** — `{ DESCR_t *cellp; TBBLK_t *tbl; const char *key; DESCR_t key_d; DESCR_t sv; long pos; long len; }` (`descr.h`) |
| a NAME on the variable | not considered | **`rt_var_ref_cell_named(&cell, "id")`** exists and `bb_var_ref.cpp:26-41` already emits it |
| Icon emitting one | not considered | **`bb_var_ref.cpp:43-56`** — *"IR_VAR_REF icn cells zd: NAMETRAP{DT_N,slen=1,&____slot} -> ZRES"*. The Icon lane already mints variable descriptors. |
| dereference at use | not considered | **`IR_DEREF`** — built today by the `TT_AUGOP` lowering (`lower_icon.c`, the `IR_ASSIGN_VAR` arm) |
| a variable through ALTERNATION | "the operand is a runtime alternation of 15 … a compile-time answer cannot work" | **`lower_alt_lv` → `lower_alt_impl(…, lv=1)`** — alternation-of-lvalues is already a lowering the Icon front end performs |

**How I got it wrong:** I read the `DTYPE_t` enum looking for a name like `DT_VAR`, found none, and concluded
absence. `DT_N` is spelled as SNOBOL4's *name trap*, so a search framed in Icon's vocabulary cannot see Icon's
own use of it — **the same narrow-instrument shape this org files under `command -v` and `$?`-after-a-pipe, and
I committed it inside the very FINDING that warns about control arms.** ⭐ The general form worth keeping: **an
enum read for a name you expect answers "not under that name", never "not present"** — census what the
neighbouring language calls the thing before you conclude a kind does not exist.

⛔⭐⭐ **BUT THE PARTS DO NOT COMPOSE, AND THAT IS A MEASUREMENT, NOT AN OPINION — THIS IS THE NUMBER A SCOPE
RULING SHOULD REST ON.** I routed the suspend operand through the existing lvalue path
(`lower_lvalue_var` in place of `lower` at the `TT_SUSPEND` arm, behind an env flag), built, and A/B'd on
`tracer` at `9fb1cb35e`:

| arm | tracer diff lines |
|---|---|
| control (rvalue `lower`, shipped today) | **20** |
| experiment (`lower_lvalue_var` on the suspend operand) | **30 — WORSE** |

and the shape of the regression says why: the 15-way alternation **yielded only 3 alternatives** before
stopping (`a`, `i`, `j` — exactly the plain `TT_VAR`s), and those three printed **`"1" "2" "3"`** — *quoted*, where the oracle wants bare `1`, `2` and
`(variable = 3)`. ⚠️ **Stated as measured, not as mechanism:** what I observed is that the tap imaged something
**string-typed** on all three; whether the lvalue path stringified before the tap or `trace_image_icon`
stringified the `DT_N` is **not** something this experiment distinguishes, and I am not asserting which.
Three separate gaps, each independently blocking:

1. **`lower_lvalue_var` returns NULL for keywords** — its `TT_VAR` arm is guarded `t->v.sval[0] != '&'` and
   there is no `TT_KEYWORD` arm at all, so `&subject &pos &random &trace` (4 of the 10 red lines) and every
   keyword-based section have no lvalue lowering to route through. The alternation loses those arms.
2. **`trace_image_icon` (`core.c:168`) has no variable rendering** — it calls the `image` builtin, which
   dereferences. It needs the three renderings hq_S's rule table names: `NAME = value`, `(variable = value)`,
   and `table_1(1)[1]`, plus the section normalisation `[i:j]` → `[i+:len]` this FINDING already measured.
3. **Nothing dereferences the variable on the way out of the suspend** — `IR_DEREF` exists but the
   `TT_SUSPEND` arm does not build one, so a variable that reaches the tap keeps flowing to consumers.

⭐ **The experiment is reverted; the tree is clean and honestly back at 20.** It is recorded because a negative
result with a cause is the difference between a size estimate and a size measurement — and because the naive
reading of my own correction ("the parts exist, so it is small") is exactly as wrong as the claim it replaces.

`bb_suspend.cpp:31-33` hands the tap the already-computed descriptor out of the expression's result slot, and
`trace_print_icon` (`core.c:194`) receives a `DESCR_t value` with the variable long gone.

⛔ **A compile-time answer cannot work, and this is the trap worth recording:** the operand is an *alternation*
of 15 alternatives behind ONE suspend node, so which alternative yielded is decided at run time. A static
"variable form" attribute on the suspend node would be correct for a single-alternative suspend and silently
wrong here — and `tracer` line 21 would still pass, because dereferenced alternatives are unaffected. **A
passing sibling that exercises the other arm of the same branch is not a control arm** (same shape as the
`γ_to`/`lc_γ_to` trap in SCRIP `5b2f0e13a`).

⭐ **Nor does a ζ-resident "last variable produced" side-channel survive contact**, though it looks tractable:
the image needs the base dereferenced AT IMAGE TIME (`&trace = -47`), so the record must hold base + offset +
length and defer the read — which is a trapped-variable descriptor with a different name, minus the type
system that keeps it honest. And a side channel must be CLEARED by every non-variable producer or it reports a
stale variable for a plain value; that is every node in the language, not a local change.

**So the honest shape is: teach the EXISTING `DT_N`/`VCELL_t` variable descriptor to cover Icon's keyword and
section lvalues, route `suspend`/`return` through the lvalue path with an `IR_DEREF` for locals and parameters
only, and give `trace_image_icon` the three renderings.** It is **not** a new descriptor model — but it still
touches `DT_N`, which SNOBOL4's name traps and the shared `image` path both read, so it stays a
**shared-node change and `hq_U` co-signs**, and SHARED-NODE VERDICT SCOPE still means grading every frontend
that reaches the descriptor. **Not started; scope is the ceo's.**

## Witnesses (reproduce in one command each)

```icon
# tv.icn -- variable KINDS. icont -s tv.icn && ./tv
global g
procedure main()
   local lv; static sv
   &trace := -1; g := "gg"; lv := "ll"; sv := "ss"; &subject := "123456"
   every probe(1)
end
procedure probe(p)
   local lo; static st
   lo := "lo"; st := "st"
   suspend (p | lo | st | g | lv)
end
```

```icon
# tx.icn -- SUBSCRIPT and SECTION imaging. icont -s tx.icn && ./tx
global g
procedure main()
   &trace := -1; g := "abcdef"; &subject := "123456"; &pos := 4
   every probe()
end
procedure probe()
   local lo
   lo := "abcdef"
   suspend (lo[3] | lo[3:5] | &subject[3:4] | &subject[2:5] | &subject[2:5][1] | &pos[1] | &trace[1] | &random[1])
end
```

**Related** — CEO-563 (this row), `1493214e4` (the γ-port return cure that shrank 68 → 20 and exposed this),
the cto's `var` cure (both `var` files green, so the class is genuinely confined to the two programs above).
