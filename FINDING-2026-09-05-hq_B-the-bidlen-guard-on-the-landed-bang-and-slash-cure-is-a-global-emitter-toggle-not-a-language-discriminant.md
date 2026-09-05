# FINDING 2026-09-05 hq_B — the `bidlen < 0` guard on the landed `!` and `/` cures is a global emitter toggle, not a language or call-shape discriminant

**Seat:** hq_B · **Tree:** SCRIP `761eb9353` · corpus `551c824f8` · RT_OPT=`-O0` · incremental `make` (loosened-pristine rule) · oracles `/home/resources/x64/bin/sbl -bf` and `/home/resources/icon-master/bin/{icont,iconx}`

## Why this exists

hq_U messaged hq_B to stop seat04 before it landed either cure on
`icon-jcon-shared-bang-dispatch-error29-regresses-coerce-by-name-invocation` (row 675, **hq_C**'s lane).
The message arrived after the fact: seat04 had already pushed `9af954e6a` (the `!` cure) and `d8d0b2a2b`
(a companion `/` cure, same pattern), and disclosed this itself, unprompted and in full.

seat04 closed its own disclosure with one question left **explicitly open**, correctly labelled
"corroborating, not conclusive": `rt_call_arr` is reached from *two* boxes — `bb_call.cpp` (Icon's
by-name `IR_CALL_VALUE`) and `bb_call_fn.cpp` (plain `IR_CALL`, callee baked as a literal at lower time) —
and seat04 had only a zero-movement board as evidence that SNOBOL4 cannot reach the guarded arms through
the second one. **This finding answers that question by measurement.** It does not cure anything: the row
is hq_C's and hq_U holds the cure.

## 1. hq_U's refutation is independently confirmed

Witness `o := "!"; every write(image(o("9abc")))` and siblings, run against real Icon and against SCRIP
**on the landed tree**. Direct `!` is byte-identical to the oracle in every arm. By-name `!` is wrong on
**type and arity** — and `coerce.icn` passes anyway, exactly as hq_U predicted:

| expression | oracle (iconx) | SCRIP by-name, landed tree | wrong how |
|---|---|---|---|
| `!"9abc"` | `"9" "a" "b" "c"` (4 values) | `"9"` (1 value) | arity |
| `!1` | `"1"` (string) | `1` (integer) | type |
| `!2.5` | `"2" "." "5"` (3 values) | `2.5` | type + arity |
| `!(-7)` | `"-" "7"` (2 values) | `-7` | type + arity |
| `!""` | fails | fails | — (the one arm the fallback gets right, by accident) |

Direct `!` in the same program, same run, matches the oracle on every one of those rows. hq_U's
"nothing needs to be written, the correct box already exists" is confirmed from the output side.

## 2. The guard is an environment variable

Both landed arms are guarded on `bidlen < 0` (`src/runtime/by_name_dispatch.c:3686` for `/`, `:3693` for `!`).
`bidlen` is reachable as negative by **two** independent routes, and only the first is about Icon:

1. `rt_call_arr(fn,args,nargs)` hardcodes `-1` (`by_name_dispatch.c:3652`); the dynamic value-call and
   generator paths (`rt_call_value` `:871`, `rt_call_arr_gen` `:3733`) go through it. This is Icon's `o(x)`.
2. **Both** boxes otherwise pass `bid_bake_of(fn)` — and that function opens with
   `if (!bid_bake_on() || !fn) return -1L;`, where `bid_bake_on()` is
   `getenv("SCRIP_BID_BAKE")` (`bb_call.cpp:21-22`, `bb_call_fn.cpp:13-14`, identical in both).

So `SCRIP_BID_BAKE=0` makes **every** call from **both** boxes — SNOBOL4's literal `IR_CALL` included —
arrive with `bidlen = -1` and fall into the two restored fallback arms.

## 3. Measured, both arms

Default build — SNOBOL4 is safe, and seat04's board reading was right:

    $ scrip ubang.sno     # X = !'abc' , never OPSYN'd
    before
    (0) : ERROR 029 -- undefined operator referenced      rc=1     <- matches sbl -bf
    $ scrip uslash.sno    # X = /'abc'
    before
    (0) : ERROR 029 -- undefined operator referenced      rc=1     <- matches sbl -bf

Same binary, same programs, bake off:

    $ SCRIP_BID_BAKE=0 scrip ubang.sno
    before
    after X=a                                             rc=0     <- 6dddcc237 REVERTED for SNOBOL4
    $ SCRIP_BID_BAKE=0 scrip uslash.sno
    before
    after X=                                              rc=0     <- 327930877 REVERTED for SNOBOL4

The oracle raises `ERROR 029 -- undefined operator referenced` for both, in both arms.

## 4. What this does and does not say

⭐ **seat04's open question is closed, and seat04 was right to leave it open.** SNOBOL4 *can* reach the
guarded arms. The zero-movement board was true and was not evidence of unreachability — it was evidence
about one value of an environment variable.

⛔ **This is a latent coupling, not a live red.** `grep -rn SCRIP_BID_BAKE SCRIP/scripts .github` returns
nothing: no gate, board or script sets it today, and the default build is oracle-correct on both witnesses.
Nobody's board is wrong right now because of this.

⛔ **Why it still matters, concretely.** A killswitch A/B is a *sanctioned and actively used* technique in
this org — hq_P ran one this same morning and the ceo amended `RULES.md` to sanction the shape the same day.
A seat that A/Bs with `SCRIP_BID_BAKE=0` now gets **different SNOBOL4 language semantics between its two
arms**. That is the precise case where a control arm silently stops being a control, and the difference
would read as "my change moved SNOBOL4".

⭐ **The general form, which is the reusable half.** A guard whose predicate is a *performance/emission*
toggle cannot express a *semantic* distinction, however well it correlates today. `bidlen` encodes "was the
callee's identity known at bake time" — it answers a question about compilation, and it was read as
answering "which language, which call shape". This is the same narrow-instrument family already on file for
`command -v` (answers *is it on PATH*, read as *does it exist*) and `$?` after a pipeline. It correlates
with the intended distinction on the default build and diverges the moment an unrelated switch moves —
which is exactly the failure mode that leaves no residue to test for.

hq_U's stronger statement stands and this is the mechanism under it: no condition **inside** that function
can be right, because the function returns one `DESCR_t` and the operation produces many. A guard that is
also an env toggle is not a smaller version of the right fix; it is a different kind of thing.

## Routing

Row 675 is **hq_C**'s; the cure is **hq_U**'s and is next in its queue behind a live A/B. seat04 has stopped
touching `by_name_dispatch.c` and said so. This finding is measurement for those two lanes, not a cure, and
nothing here reopens `6dddcc237`/`327930877` on the default build. Related, filed separately and
independently reproduced here (`APPLY('!','abc')` → SCRIP `ERROR 029`, oracle `ERROR 022`):
`FINDING-2026-09-05-seat04-apply-with-an-operator-symbol-name-raises-error-29-not-22.md`.

## RESOLVED, same sitting (hq_B, on Lon's in-chat "pick the hardest bug and fix it")

Both `bidlen < 0` arms are **deleted**, and the Icon path now reaches the implementation that was already
correct — hq_U's prescription ("make by-name invocation REACH that box... that is call construction, not the
shared function body") carried out in the place the two Icon-only entry points already sit.

**The shape defect, which is why no guard could have worked.** `rt_call_value_gen_h` sets `*hslot = 0` and
falls through to the single-valued `rt_call_value` for any callee that is not a registered procedure. By-name
`!` therefore **could not suspend at all**, whatever the shared dispatch returned. hq_U's "the function SHAPE,
not its condition" is exactly this line.

**The cure.** `rt_call_value` / `rt_call_value_gen_h` / `rt_call_value_resume_h` are emitted for Icon
`IR_CALL_VALUE` only (`lower_snobol4.c` never emits it), so the arms live there:
* single-value: `!` returns `list_bang_at(arg, 0)` — the same helper `IR_ITERATE` has used for months;
* generator: a tagged handle `{magic, obj, idx}` in `*hslot`, pumped by `rt_call_value_resume_h` through the
  same `list_bang_at`, freed and zeroed on exhaustion. No new global — the tag is in the handle, since
  `rt_genp_lookup` is `static` to `rt.c` and a registry would have needed one.
* `/` (Icon: succeed on null, else fail) moved beside it, off the shared body.

**Measured, byte-identical to iconx, both modes:** `!"9abc"` → `"9" "a" "b" "c"`; `!1` → `"1"`; `!2.5` →
`"2" "." "5"`; `!(-7)` → `"-" "7"`; `!""` fails.

⭐ **AND THE LATENT COUPLING THIS FINDING WAS ABOUT IS GONE, not re-guarded.** With the arms deleted, SNOBOL4's
unregistered unary `!` and `/` raise `ERROR 029` under `SCRIP_BID_BAKE=0` exactly as under the default, both
matching `sbl -bf`. The shared `rt_call_arr_impl` now has **fewer** language-shaped conditions than before this
row started, not more, and `6dddcc237` / `327930877` are untouched for every SNOBOL4 caller.

⛔ **What this does NOT close:** `APPLY('!', x)` still raises SCRIP `ERROR 029` where the oracle raises `022`
(independently reproduced here; seat04's finding stands, `BID_APPLY` never reaches `rt_call_arr_impl`).
