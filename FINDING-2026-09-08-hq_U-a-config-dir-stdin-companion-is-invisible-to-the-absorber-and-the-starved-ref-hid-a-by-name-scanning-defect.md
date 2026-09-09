# FINDING — a stdin companion under `config/` is invisible to the absorber, and the starved ref it produced hid a by-name scanning defect

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
