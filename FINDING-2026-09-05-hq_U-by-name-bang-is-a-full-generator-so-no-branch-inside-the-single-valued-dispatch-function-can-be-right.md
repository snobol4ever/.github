# FINDING 2026-09-05 hq_U — Icon's by-name `!` is a FULL GENERATOR identical to direct `!`, so no branch inside `try_call_builtin_by_name_bl` can ever be right: the function has the wrong SHAPE, not the wrong condition

**Seat:** hq_U · **Mode:** FLEET-20 · **Tree:** SCRIP `674319235` (+ an unrelated unpushed cure in `core.c`) · corpus `4e11cb9ee` · .github `fed0ee67`
**Oracle:** `/home/resources/icon-master/bin/icont -s` + the produced binary, measured by execution
**Row:** `icon-jcon-shared-bang-dispatch-error29-regresses-coerce-by-name-invocation` — routed to hq_U by hq_B
(seat04 holds the witness). This FINDING is the **contract measurement**, filed before any cure, because it
**refutes the contract the row is written against** and both the row's proposed cures are wrong in the same way.

## 1. The measured contract — three surprises, all in one witness

```icon
procedure main()
   local o;
   o := "!";
   every write("byname:", image(o("9abc")));
   every write("direct:", image(!"9abc"));
   write("t:", image(type(o(1))));
   write("t:", image(type(!1)));
end
```

Real Icon:

```
byname:"9"   byname:"a"   byname:"b"   byname:"c"
direct:"9"   direct:"a"   direct:"b"   direct:"c"
t:"string"   t:"string"
```

1. **By-name `!` ≡ direct `!`, exactly.** Same values, same order, same count. It is not a "fallback" or a
   degraded form of the operator; string invocation reaches the *same operation*.
2. **It is a GENERATOR, not a function.** `!"9abc"` produces **four** values on resumption, not one.
3. **`!1` is the STRING `"1"`, not the integer 1.** `type()` says `string` for both paths. There is no
   identity-for-int arm anywhere in the real semantics — `!x` on a non-structure is *the characters of the
   string coercion*, so `!2.5` → `"2"` (first char of `"2.5"`), `!(-7)` → `"-"`, and `!""` **fails**.

## 2. ⛔ Both cures on the table are refuted by that, and they fail the same way — *invisibly*

**Cure A, "restore the pre-`6dddcc237` fallback"** (`int/real → identity; string → first character`). It is
wrong on **type** (returns the integer 1 where Icon yields the string `"1"`) and on **arity** (yields one
value where Icon yields four).

⛔ **And it would go GREEN on `coerce.icn`.** That suite's own data hides both errors: it calls `!` through
`unop()` in a single-value context (so the generator arity never shows) with `i := 1; r := 2` — integers and
an integral-valued real, whose string coercions `"1"` and `"2"` *print identically* to the integers. The one
witness the row is named for cannot distinguish the correct operation from the wrong one. ⭐ This is the
project's own "a green board is necessary, never sufficient" law with a concrete new instance: the symptom
would leave `coerce.icn` and the defect would stay in the tree, waiting for the first program that says
`!2.5`, `!(-7)`, `!""`, or resumes the operator.

**Cure B, "discriminate inside `try_call_builtin_by_name_bl`"** — by `bidlen < 0`, by language, or by any
other condition. hq_B already showed `bidlen < 0` is branch-on-the-caller-not-on-the-behaviour
(`rt_call_arr` passes `-1` unconditionally, so every plain SNOBOL4 caller satisfies it too). The measurement
above says something stronger and simpler:

⛔⭐ **NO condition inside that function can be right, because the function returns ONE `DESCR_t` and the
operation produces MANY.** `int try_call_builtin_by_name_bl(const char *fn, DESCR_t *args, int nargs, DESCR_t *out)`
is single-valued by signature. A generator cannot be expressed through it at all. **The defect is the
function's SHAPE, not its condition** — so the search for the right predicate was always going to fail, and
would have produced a cure that passes `coerce.icn` and is still wrong.

## 3. Where the cure actually is

Direct `!` lowers to **`IR_ITERATE`** (`src/lower/lower_icon.c:732`, parsed as `TT_ITERATE` at
`src/parsers/icon/icon_parse.c:305`) — a Byrd box that suspends and resumes, which is exactly what makes the
four values possible. **SCRIP's direct `!` is already byte-identical to the oracle** on every arm measured,
including `!2.5` → `"2"`, `!(-7)` → `"-"`, and `!list` generating its elements:

| arm | oracle | SCRIP m3 direct |
|---|---|---|
| `image(!2.5)` · `image(!"9abc")` · `image(!1)` · `image(!(-7))` | `"2"` `"9"` `"1"` `"-"` | identical ✅ |
| `every write("L:", image(!([10,20,30])))` | `L:10 L:20 L:30` | identical ✅ |

So nothing needs to be *written*: the correct implementation already exists and is already graded. The cure
is to make the by-name invocation **reach the `IR_ITERATE` box** rather than the single-valued scalar-op
dispatch — a question for the call construction, not for the shared function's body.

## 3b. ⭐ The generating by-name machinery ALREADY EXISTS and already works — so this cure is bounded, not architectural

The obvious fear about §3 is that "make a by-name call generate" is a deep change to how calls are built.
Measured, and it is not:

```icon
procedure gen3()
   suspend 1 | 2 | 3;
end
procedure main()
   local p;
   p := "gen3";
   every write("byname_proc:", p());
   every write("direct_proc:", gen3());
end
```

| | oracle | SCRIP m3 |
|---|---|---|
| `every p()` where `p := "gen3"` | `1 2 3` | `1 2 3` ✅ **byte-identical** |
| `every gen3()` | `1 2 3` | `1 2 3` ✅ |

**A by-name call in SCRIP already suspends and resumes correctly when the callee is a user procedure.** The
generator path through string invocation is built, graded and working. The only thing missing is that a
by-name call whose callee names an *operator* never reaches an implementation that can suspend — it is
diverted into the single-valued scalar-op dispatch of §2.

So the cure is: route by-name **operator** invocation to the operator's real implementation, the same way
by-name **procedure** invocation already routes to the procedure's. It is a routing question with a working
precedent in the same subsystem, not new generator machinery.

⛔ **And it is a CLASS, not `!`.** NO PER-OP FILTER (RULES.md): the fix must be "by-name operator invocation
reaches the operator's real implementation", not "`!` gets a special case". `!` is merely the member of the
family whose wrongness is *visible*, because it is the one that generates; a single-valued operator diverted
into the same scalar dispatch can be wrong in quieter ways (`~` and `?` are the ones to check next, and
`coerce.icn` exercises a whole unop/binop alphabet against `coerce.std` that nobody has diffed per-operator).

## 4. What this does NOT disturb — the SNOBOL4 half stays exactly as it is

`6dddcc237` is **not** reverted by this. SNOBOL4 has no `!` operator unless `OPSYN`'d, so
`core_runtime_error(29, "undefined operator referenced")` in that arm is correct for SNOBOL4 and recovered 19
of 23 previously-silent type-29 traps in `testpgms` test1. Because the cure moves the Icon path *out* of that
function rather than adding a branch *inside* it, the SNOBOL4 arm is untouched and its 29 keeps firing.

⭐ **The "two frontends want opposite answers from one shared function" framing dissolves once measured.**
They were never asking the same function for two answers: SNOBOL4 asks a single-valued operator dispatch
about an undefined operator, and Icon asks for a generator that this function cannot express. One of the two
callers is simply at the wrong door. That is a better outcome than a discriminator, because a discriminator
would have left both languages sharing a function that is the wrong shape for one of them.

## 5. Reproduce

```
cd $(mktemp -d) && cat > b.icn <<'ICN'
procedure main()
   local o;
   o := "!";
   every write("byname:", image(o("9abc")));
   write("t:", image(type(o(1))));
end
ICN
/home/resources/icon-master/bin/icont -s -o b.oracle b.icn && ./b.oracle   # 9 a b c, then "string"
/home/claude_U/SCRIP/scrip b.icn                                          # ERROR 029 today
```
