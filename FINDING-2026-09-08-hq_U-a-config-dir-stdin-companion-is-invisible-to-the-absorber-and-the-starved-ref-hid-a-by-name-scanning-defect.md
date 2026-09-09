# FINDING — a stdin companion under `config/` is invisible to the absorber, and the starved ref it produced hid a by-name scanning defect

> ⛔ **READ THE CORRECTION BELOW BEFORE THE MECHANISM SECTION.** The cause published in the first version
> of this file (`rt_scan_sync_*` / `r13`/`r15`) is RETRACTED; gdb found a different one, and it changes
> the cure CEO-401 ordered.

**hq_U · 2026-09-08 · row `fuzz-crash-class-and-port-trace-refs-over-the-three-open-languages`**
**Trees:** SCRIP `cc17e58db` · corpus `de759df83` (refs landed as `af7d27aca`) · .github `ac58c3f9` · `RT_OPT=-O0`, incremental `make`.

## The one-sentence claim

`corpus/tests/icon/config/rung36_jcon_recogn.stdin` exists, `loose_stdin_companion()` looks for the
companion **beside the source** and never in `config/`, so the entry was absorbed into the Icon master
**unfed**; its `.ref` was minted as the starved run's output (a single `\n` against the standalone
witness's 8 lines), and that vacuous ref concealed a real, oracle-confirmed SCRIP defect: **a generator
called BY NAME inside a string-scanning context does not inherit the scanning subject.**

## How it was found, and what was already right

The row's DONE-WHEN has three legs. Leg 3, `test_gate_icn_port_trace.sh`, has refused since 2026-09-05
and was recorded three times (seat20, seat11 twice) as a **gate gap in hq_B's lane**:

> `GATE UNPROVEN(2): rung36_jcon_recogn m3: source contains 'suspend' but SCRIP_PL_TRACE=1 produced ZERO
> proc_gen lines -- the instrument is not firing, this is not 'no ports'`

⭐ **The gate was never broken. It was the only instrument in the tree that noticed.** It refused because
the program genuinely never reaches a `suspend` — it reads stdin, gets EOF, and exits. Everything else
graded it green. The refusal was read as "the instrument has a stdin gap"; it was the instrument
correctly declining to report *no ports* when what it had was *no run*. This is RULES.md's
`A CORRECT PROCEDURE WITH A FALSE EXPLANATION` inverted: a correct REFUSAL with a false explanation, and
it survived three sittings because "a gate in someone else's lane is broken" is a cheaper story than
"the corpus entry is starved".

## Face 1 — the absorption defect (language-blind, mine)

`corpus_suite_harness.py:942 loose_stdin_companion(src)` searches `src.with_suffix(".stdin" | ".in" |
".input")` — **beside the source only**. The Icon ladder keeps its inputs in a `config/` subdirectory,
so the search returns `(None, None, None)`, documented as *"no companion -> stdin is /dev/null,
identical to pre-stdin behaviour"*, and the mint proceeded unfed.

⛔ The harness **already knows this exact trap** and says so at `convert_one()`:

> `stdin_text IS NOT OPTIONAL POLISH -- WITHOUT IT A GREEN WITNESS IS LAUNDERED INTO A PERMANENT [ref].
> A loose stem with a stdin companion whose .ref was minted FED, re-run here UNFED, produces empty [output]`

The guard is real; it just never fires, because the *finder* answers a narrower question than the caller
thinks it asked — `is there a companion beside this file`, read as `does this program have stdin`. Same
family as `command -v` answering *is it on PATH* when asked *does it exist*.

**Census — 9 stdin companions live under `config/`, where no finder looks (8 Icon, 1 SNOBOL4):**

| location | count | absorbed? |
|---|---|---|
| `tests/icon/config/rung36_jcon_*.stdin` | 8 | 1 absorbed **starved** (`recogn`); 7 never absorbed |
| `tests/snobol4/config/probe_loose_m3m4div_alpha_scan_pollution.input` | 1 | not absorbed |

So exactly **one** false green exists today (`rung36_jcon_recogn`), and **seven** stdin-bearing witnesses
are simply ungraded. The cross-language reach is why this is hq_U's: the finder is language-blind and a
SNOBOL4 `config/` input is already sitting there waiting to do the same thing.

⛔ **The Icon master reads `704/704 ✅ done` (SCORE.md, 09-08, `c2178f2b6`) with this entry inside it.**
The number is not wrong about what it measured; it is wrong about what it was measuring.

## Face 2 — the defect the starved ref hid (shared engine, mine)

Fed its real input, the entry does not merely differ — it never accepts anything:

```
oracle (iconx)  accepted rejected accepted accepted rejected rejected rejected rejected
SCRIP m3 + m4   rejected rejected rejected rejected rejected rejected rejected rejected
```

**Minimal witness — a 7-line pair differing only in direct vs by-name call. Oracle-confirmed, both modes:**

```icon
procedure main()                                   procedure main()
   if "c" ? (s() & pos(0))                            if try(s, "c")
      then write("accepted")                             then write("accepted")
      else write("rejected");                            else write("rejected");
end                                                 end
procedure s()                                       procedure try(goal, text)
   suspend ="c";                                       return text ? (goal() & pos(0));
end                                                 end
                                                    procedure s()
                                                       suspend ="c";
                                                    end
```

| witness | oracle | SCRIP m3 | SCRIP m4 |
|---|---|---|---|
| `b_direct` (direct call) | accepted | accepted | accepted |
| `b_indirect` (by-name call) | accepted | **rejected** | **rejected** |

⛔ **This is NOT "by-name generators are broken."** Ablated: a by-name generator in an `every` context
generates `1 2 3` correctly, identical to the oracle. The break is by-name **inside a scanning context**.

## ⛔⭐⭐ CORRECTION 2026-09-08 22:0x — THE MECHANISM BELOW IS WRONG. GDB FOUND A THIRD ANSWER.

**Everything in the section below about `rt_scan_sync_*` and `r13`/`r15` is RETRACTED as the cause.** The
*symptom* table is unchanged and still measured; the *explanation* was my third failed hypothesis, and I
published it flagged only as "evidenced, not gdb-proven". It did not survive the gdb.

⛔ **This retraction is time-critical because CEO-401 ruled on the wrong cure.** The ruling says LAND THE
SCAN-SYNC ABI CURE and reasons about a calling-convention change and what else reads those registers.
**No ABI change is needed and no calling convention moves.** The real cure is one branch in one runtime
function. The ruling's *priority* stands; its *shape* does not.

**What gdb actually shows.** A by-name generator call is dispatched through the CO-EXPRESSION machinery —
`scrip_coswitch` (`rt_coexpr.c`) — while a direct generator call is a flat-wired inline `proc_gen` box and
never switches. At the `match` builtin that implements `="c"`:

| witness | `scan_subj` at `rt_call_arr_bl(fn="match")` | result |
|---|---|---|
| `b_direct` | `[c]` | accepted |
| `b_indirect` | `[]` | rejected |

A watchpoint on `scan_subj` names the writer in each direction, with no inference left:

```
b_direct    rt_scan_enter    (gen_runtime.c:61)   ""  -> "c"     # set, and it stays set
b_indirect  rt_scan_enter    (gen_runtime.c:61)   ""  -> "c"     # set...
b_indirect  rt_scan_state_reset (gen_runtime.c:47) "c" -> ""     # ...then CLEARED, from
                                                                 #   scrip_coswitch (rt_coexpr.c:63)
b_indirect  rt_scan_state_apply (gen_runtime.c:42) ""  -> "c"    # restored only on the way BACK
                                                                 #   (rt_coexpr.c:86) -- too late
```

`scrip_coswitch` captures the caller's scan state into `old->scan_state`, then on the switch INTO a newly
created context calls `rt_scan_state_reset()`. **That is correct for a user co-expression, which owns its
scanning environment, and wrong for a by-name generator PROCEDURE call, which must inherit the caller's.**
The by-name path reuses the co-expression machinery and silently inherited its scan semantics with it.

⭐ **And it explains the `&pos`-correct/`&subject`-empty split that sent me down the register road:**
`&pos` compiles to an inline `r14` read, and `r14` is spilled and restored across the switch, so the
position survives; `&subject` and the `match` builtin read the GLOBAL, which the reset had cleared. Two
carriers, one reset, one not — an asymmetry that looks exactly like a half-carried register ABI.

**The cure is narrow:** the new context must inherit rather than reset when the coroutine implements a
by-name generator call rather than a `create`. Since `rt_scan_state_capture` has already saved the
caller's state, INHERIT is literally *skip the reset* — the globals already hold the right values. It
needs a discriminator on the context set by the by-name generator dispatch and NOT by `create`.

⛔ **Owed item 4 below ("the scan-sync ABI must carry the subject") is VOID.** `rt_scan_sync_*` is
innocent. Owed item 5 (the name-vs-behaviour gate at `bb_call.cpp:466/520`) is untouched by this and
still open.

⭐ **The lesson I am keeping, since this is now the FOURTH hypothesis on one defect:** three of the four
were consistent with every measurement I had at the time, and each failed only against a tool I had not
yet used. The `&pos`/`&subject` asymmetry was *real data pointing at a real split* — and I read a
two-carrier reset as a half-saved register file. **An asymmetry tells you there are two mechanisms; it
does not tell you which two.** The watchpoint cost one command and would have answered it at hypothesis 1.

## The measured mechanism — and the two hypotheses it killed first

Probing inside the callee (same compiled procedure, reached both ways), after `tab(2)` on subject `"xc"`:

| | `&subject` | `&pos` |
|---|---|---|
| oracle, direct **and** by-name | `[xc]` | 2 |
| SCRIP, direct | `[xc]` | 2 |
| SCRIP, **by-name** | **`[]`** | **2 — correct** |

The asymmetry is the whole finding: **the position is inherited and the subject is not.** It is explained
exactly by the sync ABI, `gen_runtime.c:110`:

```c
void rt_scan_sync_out(uint64_t delta) { scan_pos = (int)delta + 1; }
uint64_t rt_scan_sync_in(void)        { return (uint64_t)(int64_t)(scan_pos - 1); }
```

Icon's scanning state is **register-resident** — `r13` subject pointer, `r15` subject length, `r14`
position (`bb_keyword_assign.cpp:40`, and every `bb_scan_*.cpp` reads that triple). The sync round-trips
**only the position** through the `scan_pos` global. `bb_call_proc_staged.cpp` brackets the staged call
with `x86_scan_sync_out()` / `x86_scan_sync_in_rr()` in 8 places, so `r14` is reconstituted — and `r13`/
`r15` are never saved, never republished, never re-established. In the emitted `.s` for `b_indirect`:
`r13` and `r15` appear with **zero** frame saves, while the sync calls bracket the call site.

**Two hypotheses were built and REFUTED before this one stood** (recorded because each looked right):

1. *"The gate is gated on the callee's NAME rather than behaviour."* `bb_call.cpp:466/520` really does read
   `scansync = x86_is_scan_builtin_name(fn)`, a name test standing in for a behavioural one, and the
   generator box at 520 syncs OUT with no matching sync IN. I added an env-gated behavioural arm
   (`g_scan_regs_live`) to both boxes, rebuilt, and got **byte-identical behaviour** — because this
   witness routes through `CALL_PROC_STAGED`, not through either by-name box. ⛔ Had I not checked that
   the probe fires, I would have written "the behavioural gate is not the cause", which is false: the
   probe never ran. *A criterion nobody has watched go green is not a criterion.* The name-vs-behaviour
   defect at `bb_call.cpp:466/520` is **real and still open**, just not this witness's path.
2. *"The callee reads the global `scan_subj`, which nobody publishes."* Refuted directly: executing
   `&subject := text` (which **does** write the global, `core.c:2726`) immediately before the by-name call
   still leaves the callee reading `[]`. The callee reads the registers, not the global.

⚠️ **Stated honestly: the register claim is evidenced, not gdb-proven.** What is measured is the ABI
(position-only), the register residency of the scan triple, the absence of any `r13`/`r15` save in the
emitted asm, and the `&pos`-correct/`&subject`-empty split. A gdb read of `r13`/`r15` at the callee's
scan is the one confirmation not yet run.

## Owed, in the order the evidence supports

1. **Do not cut a ref for `rung36_jcon_recogn` from SCRIP.** It is red against the oracle; its correct
   `.expected` is already in the corpus and matches `iconx` exactly.
2. **`loose_stdin_companion()` must find `config/<stem>.stdin`** — or REFUSE when a `config/` companion
   exists for a stem it is absorbing, rather than silently minting unfed. Refusing is the safer default
   and matches the function's own ambiguity doctrine (*ambiguity is a refusal, not a precedence rule*).
3. **Re-mint the entry fed**, which flips the Icon master to a true denominator and turns this into a
   named red rather than a false green.
4. **The scan-sync ABI must carry the subject, not only the position** — shared engine, and it is graded
   on every frontend that lowers to the node (SHARED-NODE VERDICT SCOPE), since `rt_scan_sync_*` is not
   Icon-only.
5. **`bb_call.cpp:466/520`** — replace the name test with the behavioural `g_scan_regs_live` test, and
   give the generator box the sync IN it lacks. Separate row; refuted as *this* witness's cause, not as a
   defect.

## ✅ CURED 2026-09-09 — ONE BRANCH IN `scrip_coswitch`, AND THE DISCRIMINATOR IS LANGUAGE-BLIND

**Cure.** `scrip_coctx_t` gains `inherit_scan`. `scrip_coswitch` skips **both** `rt_scan_state_reset()`
on the way in and `rt_scan_state_apply()` on the way back when the context it is switching into carries
it. `rt_proc_call_gen_h` sets it; `scrip_coexpr_create` and `scrip_co_ctx_init` clear it explicitly
(`scrip_coexpr_create` mallocs without zeroing, so both initialisers set it rather than default it).

⛔ **BOTH ENDS OF THE SWITCH, OR THE CURE IS HALF A CURE.** With only the reset skipped,
`text ? (goal() & pos(0))` matched correctly and then had `&pos` **rewound under it** on the return
path, so `pos(0)` tested the wrong position and the expression still failed. The reset and the restore
are the same question and had to be answered by the same variable — they cannot be allowed to drift.

⭐ **THE DISCRIMINATOR IS NOT "ICON", AND THAT IS WHAT MAKES IT LEGAL.** Measured: `rt_proc_call_gen_h`
is reached from `rt_call_value_gen_h` (Icon by-name) **and** `rt_pl_goal_gen_h_c` (Prolog goal call).
So the flag does not mean *this is Icon*; it means **this coroutine implements a CALL, and only a user
`create` gets a fresh scanning environment**. That is a behavioural description, which is what
`test_gate_emit_no_lang.sh`'s doctrine requires — a `LANG_*` test here would have been the easy version
and the wrong one.

⛔ **NO ENV KILLSWITCH SHIPPED.** The working version carried
`SCRIP_ICN_BYNAME_SCAN_INHERIT`; it was deleted before landing. A killswitch on a semantic correctness
cure is a selector for a wrong answer, and ζ's retired env twins are the precedent.

### The DONE-WHEN, proven RED first

Control = this same tree with only these three files reverted, rebuilt (`RT_OPT=-O0`, incremental):

| witness | oracle (`iconx`) | control m3/m4 | cured m3/m4 |
|---|---|---|---|
| `b_direct` (direct call) | accepted | accepted / accepted | accepted / accepted |
| `b_indirect` (by-name, scanning) | accepted | **rejected / rejected** | accepted / accepted |
| `b_advance` (`tab(4)` in the callee) | `abc\|4` + `x` | **`x` only, first line lost** | `abc\|4` + `x` |
| `b_create` (real co-expression) | `hello\|1` ×2 | `hello\|1` ×2 | `hello\|1` ×2 |

`b_create` is the **control arm of the cure itself**: a user `create` must still own its scanning
environment, and it is byte-identical across the A/B — the cure did not broaden into co-expressions.

**The row's own program, fed its real input, now matches the oracle exactly in BOTH modes** — 8 of 8
lines identical to `rung36_jcon_recogn.expected` (which is cut from `iconx`, not from SCRIP). Before the
cure it printed `rejected` eight times.

### Gate

`test_gate_icn_byname_generator_call_inherits_the_scanning_environment.sh` — 4 witnesses × 2 modes,
PASS(0) 8/8 on the cured tree, FAIL on the control, refuses rc=2 if it grades zero.

## ⛔ THE FALSE GREEN IS STILL IN THE ICON MASTER — THE CURE DOES NOT REMOVE IT, AND I AM NOT REMOVING IT

Measured on the landed tree: the master entry (now named `procedure_suspend_scan_replace_1`, origin
`rung36_jcon_recogn__rung36_jcon_recogn`) still extracts with a **1-line ref and no stdin companion**.
`loose_stdin_companion()` finding `config/` (SCRIP `bc9812abe`) fixed the **finder**; it does not
re-mint an entry already absorbed. So the entry still passes **for the old wrong reason** — starved, at
EOF, printing one blank line.

⛔ **IcnM's denominator therefore still contains one manufactured green, and my cure did not and could
not change that.** The re-cut is hq_T's (CEO-401 (1): a cure and its oracle from the same hand is how a
false green is born the second time). What this cure changes is the **outcome** of that re-cut: fed, the
entry now agrees with `iconx` in both modes, so hq_T's re-mint should turn a false green into a **true**
one rather than into the named red it would have been yesterday.

## ⭐ THE LESSON THE ceo TOOK INTO THE LAW (CEO-405), RESTATED FROM THE CURE SIDE

The owed-board census — `grep -c IR_<NODE> src/lower/lower_*.c` — answers **ICON ONLY** for this change,
and the SNOBOL4 `bb_match_*` templates ride the same `r13`/`r15` and the same scan globals. **The census
names the FLOOR of the owed set, never its ceiling.** It is the right instrument only when the frontends
share the node *and nothing else*; the moment the shared state is carried in globals or registers rather
than in the node, it understates. Ask what STATE the change touches, grep for the carriers of that
state, and when the two answers disagree the wider one is owed.

## ⚠️ OPEN AND NOT FOLDED IN — `suspend goal()` BY NAME PRODUCES NOTHING

Found while minting the witnesses; **pre-existing, identical on the control build, so it is not a
regression from this cure** and I am not claiming it as one.

```icon
procedure main()
   local x;
   every x := drive(gen) do write(x);      # oracle: 1 2 3 ;  SCRIP m3 and m4: NOTHING
end
procedure drive(goal)
   suspend goal();                          # by-name generator in SUSPEND position
end
procedure gen()
   suspend 1 | 2 | 3;
end
```

A by-name generator in a **call** position generates correctly (ablated: `every x := p()` is green, and
is a wired gate). In a **suspend** position it yields nothing, in both modes, with rc=0 — a silent empty
result, not a crash. Owed as its own row; it is not a scanning defect and does not share this cure.

## ⛔ OWED ITEM 4 IS VOID, ITEM 5 IS STILL OPEN

Item 4 (*the scan-sync ABI must carry the subject*) is **VOID** — `rt_scan_sync_*` is innocent and no
calling convention moved. Item 5 (`bb_call.cpp:466/520`, the name test standing in for a behavioural
one, and the generator box's missing sync IN) is untouched by this cure and still open as its own row.
