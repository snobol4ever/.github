# String invocation reached every Icon operator except the one whose native form is a GENERATOR

**Measured 2026-09-09 by hq_U** · SCRIP `b2824175a` (cured; parent `01eb996ca`) · corpus `f7c68a8c5` · `RT_OPT=-O0` · incremental `make` · oracle `/home/resources/icon-master/bin/icont` + `iconx` (Icon v9.5.25a), reached by absolute path.
**Row** CEO-445, the cross-program Icon engine classes: *string invocation of an operator name (evalx)*.

## The claim

`"..."(1,10,2)` — string invocation of Icon's ternary `to`/`by` operator — raised `ERROR 022 -- Undefined function called`. `icont`/`iconx` generate `1 3 5 7 9`.

## ⭐ THE CLASS WAS ONE ARM WIDE, AND MEASURING THAT FIRST IS WHAT MADE THE CURE SMALL

The ceo's brief named the class *string invocation of an operator name*, which reads as a whole mechanism being absent. **It is not.** Probing eleven forms against the oracle before touching code:

| form | oracle | SCRIP (before) |
|---|---|---|
| `"+"(3,4)` `"-"(9,4)` `"*"(3,4)` `"||"("ab","cd")` `"<"(1,2)` | correct | **correct** |
| `"-"(7)` `"*"("hello")` unary | correct | **correct** |
| `"!"([1,2,3])` — a **generator** operator | `1 2 3` | **correct** |
| `"write"(1)` — named function by string | correct | **correct** |
| `"..."(1,10,2)` | `1 3 5 7 9` | ⛔ `ERROR 022` |

**Every other operator already worked, including a generator one.** So the defect was a single missing arm, not a missing mechanism — and `"!"` working is what proved the generator path was already reachable and already correct. ⛔ Had I read the brief's wording as the scope, the cure would have been a rewrite of a dispatch that is fine.

## Why it could not be one more `strcmp` in the operator table

The by-name operator table (`by_name_dispatch.c` ~4178) returns a single `DESCR_t` per call. **`...` is a generator**: under `every` it must suspend and resume. A single-value return cannot carry it, which is precisely why `...` is the operator that was missing while twenty-odd others were not — the table it belonged in could not hold it.

The cure routes it through `ICN_OPGEN_t` / `icn_opgen_pump`, **the same path `"!"` already used**, giving the struct a `kind` and a `cur/lim/step` triple; `rt_call_value_resume_h` already pumps that struct, so resumption needed no change. `proc("...",3)` needed the name added to the `op2` table as well — a second red found by probing rather than reported.

⭐ **The one placement fact worth carrying:** the new arm was inserted **ahead of** the `"!"` arm in the same dispatch. That makes `"!"` a displaced sibling, so it is graded in the gate beside the cure — a gate that only grades new behaviour cannot see what the new code pushed down.

## The oracle's contract, taken from the oracle and not from memory

- `"..."(1,5,1)` → `1 2 3 4 5` · `"..."(5,1,-2)` → `5 3 1` · `"..."(5,1,1)` → generates nothing · `"..."("1","4","1")` → `1 2 3 4` (string args coerce).
- `"..."(1,5,0)` → **runtime error 211** *by value equal to zero*. Cured by routing to `core_icn_by_zero_check`, the same helper the native operator uses, so the string form raises what the operator raises.
- ⭐ **`"..."(1,5)` is an ERROR in Icon** — `iconx` gives runtime error 106. `to` and `to by` are one *ternary* operator, so arity 3 is the whole contract. Guessing a binary form would have been inventing semantics; two args still error in SCRIP (022 rather than 106 — both refuse, the code differs, recorded not cured).

## The discipline that shaped the cure: agree with the operator, not merely with the oracle

SCRIP's **native** `1 to 5 by 2` was already fully correct, error 211 included. The string form is required to agree with the operator it names, so `native` is graded inside the gate. This matters because the two could have been made to agree with `iconx` separately and still disagree with each other.

## ⛔ A SEPARATE RED I MEASURED AND DELIBERATELY DID NOT FOLD IN

`"a" to 5` — a **non-numeric** operand to the native operator:

| | oracle | SCRIP |
|---|---|---|
| `every write("a" to 5)` | runtime error 101, *integer expected* | **`0 1 2 3 4 5`** |

SCRIP coerces `"a"` to 0 and generates six values where Icon refuses. That is a **different witness with a different first divergence**, in the native operator rather than in string invocation, so under CEO-445's one-program-at-a-time method it is filed, not folded in. ⛔ It is the more dangerous of the two: this one prints a plausible answer instead of refusing. The cured string form deliberately uses the **same** `to_int` coercion as native, so the two remain consistent and one cure will fix both — making them agree separately would have hidden this.

## Arms

- **Icon master (`board_icon_master.sh`, the cell's owning runner): `707/707 FAIL=0` both modes**, on the clean pushed tree `b2824175a` — no worse than the `707/707` anchor read off `SCORE.md` for parent `01eb996ca`. Row rewritten through the runner.
- **Prolog control arm: ladder `533/568 FAIL=35`, identical to the pre-cure arm.** Owed because `IR_CALL_VALUE` — the node driving `bb_call_value.cpp`, which emits every call to the three changed entry points — is lowered by **icon=2 and prolog=1**. That is *reach*, not merely the linkage every frontend has through `libscrip_rt.so`, so this arm was mandatory rather than courteous.
- **Gate** `test_gate_icn_string_invoked_to_by_is_a_generator.sh`: **GREEN 18/18**, then **RED 12/18** on a control build with `by_name_dispatch.c` reverted, run in that order before wiring (CEO-381). The 12 reds are the six cured witnesses × two modes; `bang`, `plus` and `native` hold green on **both** arms, so the gate is not red-by-default. Wired at `Makefile:187` with its measured 2.8s cost, and adopted into the ratchet floor.

## NOT CLAIMED

- **No entry was added to `corpus/tests/icon/ALL.icn`.** The seven-point standard asks for one; I deliberately did not, two days before the announcement, because it moves the master denominator (707) that every other seat is citing this week. The wired gate carries the coverage and is the stronger instrument (it has the A/B the master cannot have). **Recorded as owed**, not as done.
- `"..."(1,5)` still answers 022 where the oracle answers 106. Both refuse; only the code differs.
- The non-numeric coercion red above is **filed, not cured**.
- I did not re-run the SNOBOL4 master: SNOBOL4 is parked under Lon's Icon-only order, and it has no reach to `IR_CALL_VALUE` — linkage only.

---

## ✅ ADDENDUM 2026-09-09 — A SECOND MISSING ARM, `"[:]"`, FOUND BY hq_V'S RUNG AND NOT BY MY PROBE SET

SCRIP `583af75c5`. hq_V minted `ladder__rung29_type_string_invocation_of_operator_names` (corpus `cf265e9f1`) as an oracle-cut master witness for this class **before** my cure, per CEO-445. It exercises six forms — `"..."`, `"[:]"`, `"[]"`, `"image"`, `"+"` and `proc("^",2)` — and after the `"..."` cure it **still failed**, at ERROR 022 on `"[:]"`, the ternary **section** operator.

⭐ **MY OWN PROBE SET MISSED IT AND hq_V'S DID NOT, WHICH IS THE ARGUMENT FOR AN INDEPENDENTLY MINTED WITNESS.** I probed eleven forms and concluded the class was one arm wide. It was **two**. My eleven were the operators I thought of; hq_V cut theirs from the constructs Arizona `misc`/`traps`/`evalx` actually die on. Isolating each of rung29's six forms: `"[]"`, `"image"`, `"+"` and `proc("^",2)` were already green, so `"[:]"` was the one remaining arm — but *"I probed the class and it is one arm wide"* was a claim my probe set could not support, and only someone else's witness falsified it.

**The cure, and the trap in it.** `rt_section_var` (`pattern_match.c:1489`) requires `IS_VARREF_fn(base)` — a section is **assignable** (`s[3:5] := "x"`), so it builds a NAMETRAP over a variable. String invocation passes a **value**, so the first attempt returned `FAILDESCR` and the program printed *nothing* rather than erroring — a silent failure that looked like a wrong cure site. The fix stages the value into an arena cell and wraps it with `rt_var_ref_cell`, so `rt_section_var`'s index arithmetic — negative indices, out-of-range refusal, the `i > j` swap — has **one copy** serving both callers rather than a duplicate in the by-name path.

### ⛔ ONE ENTRY CHANGED KIND, AND IT IS NOT A REGRESSION — MEASURED, NOT ARGUED

A name-level A/B against a build with **only** this arm reverted, same corpus, m3:

- `procedure_write_255` (hq_V's rung29): **FAIL → PASS.** The flip.
- `procedure_record_every_replace_13`: **FAIL → HANG.** Red on both arms, different kind.

⭐ The second looks like a regression and is the opposite. On the control build that program dies at **34 lines**, at its own `"[:]"` line inside `p3`. On the cured build it reaches **241 lines** — roughly 200 lines further, all correct — and hangs in `p12`. **The cure did not break it; it unblocked it into a pre-existing defect two hundred lines downstream.** Reduced to a three-line witness:

```icon
procedure main();
    write(image(while break) | "none");
    write("after");
end
```

`iconx` prints `&null` then `after`. SCRIP hangs, rc=124. **`while break` — `break` as a `while` CONDITION — is an Icon control-flow defect with nothing to do with string invocation**, and it is filed here rather than cured because it is not in this lane. ⚠️ It costs every Icon board run a 12-second timeout, so it is worth someone's rank-0; naming it is the point of this paragraph.

**Arms.** Gate extended to **24 gradings** (`section`, `sectvar`, `subscript` added, all three expectations cut from `iconx` and verified against it rather than assumed); control build with only `by_name_dispatch.c` reverted reads **RED 4/24**, the four being exactly the two section witnesses × two modes, so the arm is isolated. Icon master **712/726 both modes**. Prolog ladder **533/568 FAIL=35**, identical again.
