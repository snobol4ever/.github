# FINDING 2026-09-10 hq_R — the generator prologue never seeded its named locals, so BOTH null tests inverted

**Tree:** SCRIP `43c46e25b` (cure) / corpus `03eeff382` / RT_OPT=-O0, incremental `make`.
**Measured by:** hq_R. **Closes:** the last red in the IPL package (`procs/ichartp`), taking the run-graded
population to 108/108.

## The symptom did not look like the bug, and it was the third bug behind one program

`ipl/procs/ichartp` — a chart parser — answered `can't parse <sentence>` for every line of its own `.dat`,
where the oracle prints five parse trees. Two cures had already been attributed to this program and neither
was it: hq_S's `d0f4ca297` (reversible assignment on a keyword) is an ancestor of the tree that still graded
it FAIL both modes, and the scan-subject length class was a different entry. **A program that has been red
for days accumulates claimed cures; the only thing that closes it is grading THAT program.**

## What the probes said

Instrumenting `parse_sentence` showed the grammar loading identically under both engines (elist=59 ltbl=12
tset=33, tokens=3, inactive=7 active=59). The divergence was that SCRIP never entered the parser's main loop:

```icon
until \none_found do { ... }          # none_found is a local, never assigned before the loop
```

A probe printed, inside the same procedure, on the same variable:

| | `image(nf)` | `/nf` | `\nf` |
|---|---|---|---|
| iconx | `&null` | succeeds | FAILS |
| SCRIP | `&null` | **FAILS** | **succeeds** |

Both null tests inverted, on a value that images as null. ⭐ **`image()` and the null test were reading
different things, which is why the state looked innocent.** A probe that prints a value can agree with the
oracle while every predicate over that value disagrees; print the PREDICATE, not only the value.

## The cause, and why the sibling pair is one keyword wide

Not `bb_unop.cpp`, whose `TT_NULL`/`TT_NONNULL` arms are correct. The operand was never null. `emit.cpp`'s
generator prologue (`icn_gen_regime() && g_emit.flat_gen`) carves the activation record, calls
`rt_icn_zframe_args_install`, and stops. The `flat_lcl_proc` prologue **immediately below it** also emits
LCL-SEED — a `rep stosb` over `[R+zls_g_locals(g), R+zls_g_region(g))`. Those are two different regions:
args-install seeds `R+(i+1)*16`; the named-local vslots are where `zls_g_locals` points. So a procedure that
**suspends** read whatever the spine last held, and any lexical local tested with `/` or `\` before its
first assignment answered backwards.

The witness is nine lines and the passing sibling differs by ONE KEYWORD:

```icon
procedure gen(); local nf; if /nf then write("slash"); suspend 1; end   # wrong
procedure gen(); local nf; if /nf then write("slash"); return  1; end   # right
```

⭐ **THE GENERAL FORM, and it is the reusable part of this finding: two prologues sat adjacent in one file,
one seeded its locals and one did not, and nothing in the tree compared them.** The asm diff of that sibling
pair is four instructions wide (`mov rdi,rsp · add rdi,lo · xor eax,eax · mov ecx,n · rep stosb` present in
one, absent in the other) and it took minutes to see once the pair existed. **When two code paths carve the
same thing, the cheap gate is not a test of either one — it is a diff of the two.** ASM-DIFF-FIRST found this
after the probes had already localised it; the probes alone would have kept accusing the null-test box.

Cure: emit the same LCL-SEED in the generator branch, same position relative to the args install. The
install's base moves `rax` → `rsp`, equal there (`mov rsp, rax` immediately precedes) and necessary because
the seed clobbers `eax`.

## Control arms — and the reason they are quotable

The change is in a shared file but provably Icon-only: `icn_gen_regime()` reads `icn_cells_graph`, set in
`lower_icon.c` and nowhere else. Each standing red was measured on the cured tree **and again at origin with
the change stashed**, byte-identical both times, so none of them is mine:

| gate | reading, both trees |
|---|---|
| `icn_rbp_census_ratchet` | C_data=24236 E_activation=23174 DRIFT=0 — red against a baseline that is a **literal 0** in the script |
| `icn_var` | 440/442 m2/m3/m4 — `rung36_jcon_errors`, the cfo's class |
| `icn_port_trace` | 18 failed checks of 20 examined |

Green: `smoke_icon` 15/15 both modes · `smoke_prolog` 5/5 · `smoke_snocone` 5/5 · `smoke_rebus` ·
`emit_no_lang` · `template_medium_invisible` · `strip_comments --check` · and twelve Icon generator/frame
gates including `icn_no_stack`, `icn_one_reg_frame`, `icn_local_no_nv`, `icn_suspend_record_stack_alignment`,
`icn_generator_regime_calls_the_runtime_at_c_parity`, `icn_display_reads_every_activations_locals`.

⭐ **A standing red is only quotable as standing once you have measured it WITHOUT your change.** Three gates
here were red before and after; asserting that from their content would have been a guess, and one of the
three (`port_trace`) is generator-focused, exactly where a real regression of mine would have shown.

## One piece of bookkeeping that is NOT this cure's output

`update_icon_bench_asm.sh` reported `updated=9`; a second run reported `updated=0`, so the emitter is
deterministic and those nine artifacts were **stale on origin** from an earlier codegen landing that skipped
its handoff regen. Paid in corpus `03eeff382`. Proven not to be this change: **zero of the 23 icon bench
artifacts contain the generator prologue's own carve comment at all**, so the cure cannot have touched one of
them. An 86k-line diff shipping beside a 10-line cure is exactly the shape a future bisect lands on wrongly,
which is why it is a separate commit saying so in its first line.
