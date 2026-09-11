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

## ✅ CURED — and the shape that finally worked is the one the negative result pointed at

**hq_B, 2026-09-11, SCRIP `70a0bc6c0` + this landing. Both programs are 0 diff lines in BOTH modes:**
`arizona_tests/general/tracer` (was 20) and `jcon_tests/tracing` (was 24, the cfo's and hq_S's half).
Measured by hand, per program, against each `.std` — no board was run and none is claimed (ONE RUNNER).

⭐ **The correction that unlocked it: "a compile-time answer cannot work" was true of the wrong thing.** What
cannot work is a static *variable-form attribute on the suspend node*, because which of 15 alternatives yields
is a run-time fact. What works perfectly is deciding **per ALTERNATIVE** — each arm of the alternation is
lowered by itself, so `&subject` can take the variable route while `a` takes the value route, and the run-time
choice of arm then selects between two already-correct pieces of code. **The failed experiment did not
disprove the compile-time route; it disproved routing the WHOLE operand through a lowering that returns NULL
for the arms it cannot take** — `lower_lvalue_var` had no keyword arm, so four of ten red lines had nothing to
route through and the alternation collapsed 15 → 3. Per-arm choice with a **fallback to the value route** is
what makes it safe: an arm the lvalue path cannot take is exactly as it was before the change.

### The five pieces

1. **`icn_trace_var_form`** (`lower_icon.c`) — the measured rule, per alternative: a **local or parameter is
   dereferenced**; a **global, static, keyword, subscript or section of a nameable base is not**. `suspend`
   routes its operand through `lower_trace_operand`, which is `lower_alt_impl(..., lval=2)` — the per-arm mode.
2. **`IR_KW_ICON` grew a VARIABLE form** (`pat_static == 1`, **not** `IR_LIT.ival` — `sval`/`ival`/`dval` are
   one **union** and the keyword's name lives in `sval`; writing `ival` set `op_activate_proc` to `0x1` and
   SIGSEGV'd the compiler inside `strdup`). The box calls **`rt_keyword_var(name)`**, minting a `VCELL_t` with
   `cellp == 0 && tbl == 0 && key != 0 && pos == -1` — a keyword has **no addressable cell** (`&subject` and
   `&pos` live in scan registers, `&trace` behind `kw_read`), so its deref re-reads the keyword.
3. **`bb_suspend` dereferences AFTER the tap** (`rt_trace_deref_slot`), so the variable is visible to the trace
   image and to nothing else. The whole `DT_N` exposure is the span between the operand and the tap.
4. **`trace_image_icon` grew the three renderings** — named (`&trace = -47`), anonymous (`(variable = 3)`),
   and the table element `table_1(1)["k"]`, plus section normalisation and the composed-section collapse.
5. **`rt_list_bang_var_at` / `"lvv"`** — see the next section; `!` is the operand the rule cannot classify.

### ⭐ The cfo's measurement was the one that paid, and a probe against iconx made it sharper still

The cfo (`icon-jcon-tracing-events-are-byte-exact-against-the-jcon-std`) measured that `!` over a **string** and
a string **subscript** print the plain value, `!` over a **table** prints `table_1(1)` with the key, and only
the **list** element prints `variable = value` — so **the rendering cannot be decided syntactically at the
suspend site.** Probing that against iconx 9.5.25a (`ex2.icn`/`ex4.icn`, byte-identical both sides now) gave
the rule underneath it:

| `!x` where x is | iconx images | why |
|---|---|---|
| a **list** (local, parameter or global) | `(variable = 1)` | an element is a **cell**, nameable regardless of what holds the list |
| a **global** string, or a section of one | `"ab"[1] = "a"` | a string element is a **substring of its base**, and the base is nameable |
| a **local or parameter** string | `"a"` | same substring, base **not** nameable |
| a **table** | `table_1(1)["k"]` | third rendering — table image, key, **and no value at all** |

⭐ **So `!` needs a third selector, not a second.** `"lv"` (every element a variable) is right for a nameable
base; `"lvv"` — aggregate elements stay variables, **string** elements become characters — is right for a
local or parameter base. The base's nameability **is** a compile-time fact even though the element's kind is
not, which is why the split lands in the lowerer and the type test stays in the runtime.

⛔ **Two defects this probe caught that the two suite programs never would have**, both introduced by the first
cut and both invisible to `tracer` and `tracing`:
- `suspend !G[1:3]` **generated nothing at all** (`u failed` where iconx yields two values). `rt_list_bang_var_at`
  returned `FAILDESCR` for a string base that was not a varref, and lowering a section base as a *value* made
  every `!<section>` hit that arm. A generator that silently yields zero values is the worst possible failure
  mode for a trace change, because the trace lines it should have printed simply are not there to be diffed.
- a **record field** element trap carries `pos = -(field+1)` and an `sv`, so read as "has an sv, so it is a
  substring" it would image field 1 of a record as a string section. The keyword trap and the substring trap are
  now told apart by `cellp == 0` **and** the sign of `pos`, not by presence of a field.

⭐ **The general form, which is the half worth keeping:** the two suite programs are a *sample*, not a
*specification* — they exercise `!` over exactly one kind of base. **A cure graded only on the programs that
made it red will hide every case those programs do not contain**, and here two such cases were one probe away.
The `.std` files were the DONE-WHEN; the oracle was the control arm.

### What is still open

⛔ **hq_S's assign-through witness is NOT closed by this** and I am not claiming it: `every vproc(b) := 0` over
`procedure vproc(x); suspend !x; end` still raises **Run-time error 111** where iconx prints `0 0 0`. This cure
dereferences *after* the tap precisely so the variable does not flow onward; making it flow onward is the
assign-through cure and it is a different, larger change. `tracer` and `tracing` are green with 111 standing —
exactly as this FINDING warned they would be — so **the CLASS done-when still needs hq_S's arm**, and the ask
to the ceo stands.

`return` is untouched: hq_S's rule covers `return` as well as `suspend`, but neither program exercises a
returned variable, so nothing here is graded on it and nothing here changes it.

### ⛔⭐ A THIRD DEFECT THE GATES CAUGHT AND THE PROBES DID NOT — `!&digits` RAN FOREVER

`test_gate_icn_var.sh` went red on one bucket entry, `rung36_jcon_iobig`, FAIL in **every** mode. `iobig`
contains `suspend !&digits` and `suspend !&cset`, and the first cut sent them down the variable route, where:

⛔ **A CSET IS SPELLED `DT_S` WITH `slen == 0xFFFFFFFFu`** (`IS_CSET_fn`, `core.h`). So `obj.v == DT_S` is
**true of a cset**, and the idiom `obj.slen ? (long)obj.slen : (long)strlen(sp)` — which is correct for every
real string and appears verbatim in several runtime arms — reads the sentinel as a length of **4 294 967 295**.
`!&digits` yielded its ten digits and then emitted `"\x00"` without end. ⭐ **The tag byte answered "is it a
string" and the question actually being asked was "does it have a length"**, which is the same
narrow-instrument shape as the `DT_VAR` enum search that opens this FINDING — committed twice in one row, in
two different vocabularies. `!` over a cset generates its **members** and belongs to the value generator.

⭐ **The cure that makes the class impossible rather than fixing this instance: the variable form of `!` now
DELEGATES to the value generator (`rt_list_bang_at`) for every base it does not specially name** — cset, file,
anything later — instead of returning `FAILDESCR`. A variable-producing generator must be a **superset** of the
value-producing one; when it is a subset, the difference is not a wrong value, it is **no values at all**, and a
generator that silently yields nothing leaves no line in the diff to notice.

⛔ **And one behaviour I changed and then put back on purpose.** Routing keyword and section bases through the
lvalue path let `&subject[2:4] := "PQ"` reach `rt_assign_var` as a proper trapped variable — where it found no
cell to write and **silently failed**, printing `123456`. Before the change it **aborted** with the `[IDX] BOMB`
diagnostic. Neither is iconx's `1PQ456`, but *an abort is a better wrong answer than a silent one*, so the
keyword trap now refuses loudly with an accurate message: writing `&subject` also resets `&pos` and the scanning
registers, so there is no honest C-level cell store. **Assignment to a keyword section is unimplemented, it was
unimplemented before, and it is now unimplemented out loud** — row `icon-a-section-of-a-keyword-is-not-assignable`.

### Arms (ONE RUNNER: no board was run and none is claimed)

| arm | result |
|---|---|
| row DONE-WHEN (`tracer`, m3 **and** m4) | **PASS** — 0 diff lines both modes |
| `jcon_tests/tracing`, m3 and m4 | **0 diff lines** both modes (was 24) |
| `jcon_tests/iobig`, m3 and m4 | 0 diff lines both modes (the regression above, cured) |
| iconx probes `ex2`/`ex4` (`!` over list / string / table / section, local and global bases) | byte-identical |
| 74 Icon gates (`test_gate_icn_*`, `test_gate_icon_*`, `test_smoke_icon`) | 4 red + 1 ONE-RUNNER refusal |
| **control arm**: those same 4, clean tree, change stashed, rebuilt | **identical** — `list_element_alternation_position`(2) `port_trace`(1) `rbp_census_ratchet`(1) `suspend_record_stack_alignment`(2) |
| 37 SNOBOL4/Snocone gates (the other frontend reaching `DT_N` and `rt_deref`) | 6 red |
| **control arm**: those same 6, clean tree, change stashed, rebuilt | **identical** — `define_redefinition_per_binding_dispatch`(1) `port_trace`(1) `setexit_resume_matches_oracle`(2) `system_fn_protection_matches_spitbol`(1) `snobol4_master_named_set_equality`(1) `snocone_returns_codegen`(1) |
| `make` preflight | rc=0 |

Every red above is a **standing** red, named with the measurement that put it there, and reads **no worse than
a clean tree without the change** (RULES.md § SHARED-NODE VERDICT SCOPE, the control-arm bar, CEO-359).
