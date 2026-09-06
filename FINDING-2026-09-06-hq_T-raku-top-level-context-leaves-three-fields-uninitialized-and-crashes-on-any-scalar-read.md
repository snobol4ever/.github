# FINDING 2026-09-06 hq_T — the Raku TOP-LEVEL lowering context leaves three fields uninitialized, so reading any scalar SIGSEGVs about a quarter of the time

**Seat:** hq_T · **Found while:** curing `test_gate_raku_paren_call_passes_its_arguments.sh` (ceo CEO-365), which was
reporting this crash as a DIVERGE between two call forms · **MODE:** OCTET

## 1. The witness is two lines, no modules, no patterns

```raku
my $i;
say $i;
```

| variant | ASLR on | `setarch -R` |
|---|---|---|
| `my $i; say $i;` | **11/40 SIGSEGV** | 0/40 |
| `my $i = 5; say $i;` | **12/40** | 0/40 |
| `my $s = "a"; say $s;` | **14/40** | — |
| `my $i = 5;` (declared, never read) | 0/40 | — |
| `my $i = 5; say 1;` (declared, literal said) | 0/40 | — |
| `say 5;` | 0/40 | — |

**The trigger is READING a declared scalar.** Declaring one is green; saying a literal is green. This is the most
basic shape a Raku program has, and it crashes roughly a quarter of the time.

## 2. Root cause — read out of the debugger, not inferred

`src/lower/lower_raku.c:1159` builds the **top-level** lowering context:

```c
IR_graph_t * tg = IR_alloc(8192); rcx_t tcx; tcx.g = tg; tcx.try_catch = NULL; tcx.loop_exit = NULL; tcx.loop_next = NULL;
```

`rcx_t` has **seven** members (`:5`). Four are set here. **`cur_proc`, `cur_byref_mask` and `cur_nparams` are never
initialized** — `tcx` is an automatic, so they are whatever was on the stack. The proc-lowering path at `:837-840`
sets all three; only the top-level path forgets.

`rk_name_is_byref` (`:35`) then runs on every name lowered at top level:

```c
if (!cx || !cx->cur_proc || !cx->cur_byref_mask || !name) return 0;
for (int k = 0; k < cx->cur_nparams && k < 64 && (1 + k) < cx->cur_proc->n; k++) {
```

The guard is a NULL check, and garbage is not NULL. Printed at the crash:

```
cur_proc       = 0x2020202020202020
cur_byref_mask = 140737264464052
cur_nparams    = 538976288            (0x20202020)
```

`0x2020202020202020` and `0x20202020` are **ASCII spaces** — stack residue from a string that occupied those bytes
earlier. Non-NULL `cur_proc` and non-zero `cur_byref_mask` pass the guard, and `cx->cur_proc->n` dereferences the
spaces. Backtrace: `rk_name_is_byref` ← `lower_rv:263` ← `lower_rcall:143` (`rk_write`) ← `lower_rv:314` ←
`lower_raku_stage2:1187` ← `sm_preamble` ← `main`.

⭐ **Why ASLR decides it, and why that is the whole reason this went unnoticed:** the stack residue depends on the
environment and mapping layout, so with ASLR off it is reproducibly benign (one of the two guard fields lands zero)
and with ASLR on it is sometimes a non-NULL unmapped pointer. **A defect that is 0/40 under `setarch -R` and 28% with
ASLR on reads as "flaky infrastructure" from every angle except the debugger.**

## 3. The cure

One line: initialize the three fields at `:1159` the way `:838` already does — at top level there is no enclosing
proc, so `cur_proc = NULL`, `cur_byref_mask = 0`, `cur_nparams = 0`, which makes `rk_name_is_byref` correctly answer
"a top-level name is never a by-ref parameter".

⛔ **The guard is not the defect and must not be "hardened" instead.** Adding a range check on `cur_proc` would make
the symptom rarer and leave an uninitialized read in place. The field has one correct value at top level and the
constructor should write it.

## 4. What this cost, and the instrument lesson

This crash was reaching `test_gate_raku_paren_call_passes_its_arguments.sh`, which folded it into the same
`BUILDFAIL` string a genuine build error produces and then **compared it as a value**, printing
`m4 DIVERGE: listop BUILDFAIL vs paren <md5>`. The two call forms never disagreed — one of them never ran.

⛔⭐ **That gate is ARM 2 OF 60 in `make test`, so this red stopped the other 58 arms — the SNOBOL4 board among
them — fleet-wide, with a plausible-looking cause attached to whoever happened to be holding a patch.** I was one
decision away from reverting a correct, fully-differentialled ARBNO cure because the gate reddened on my build and
passed on base in a single reading.

⭐ **THE RULE THAT SAVED IT, and it works for a seat with nobody to disagree with:** a single base/patched split that
agrees with your hypothesis is not evidence until **the base arm is repeated**. Base failed 2 of 4 runs with the
violation count varying 0/1/2 on an unchanged tree. **A pass/fail flip has an innocent story available; a varying
violation count on a fixed build has none.**

⭐ **And the reframing that mattered more:** "flaky under load" was my first diagnosis and it was wrong. `BUILDFAIL`
was never a timeout — I never measured what it actually was. One `date`-bracketed run showed rc=139 in 1.8s, not a
20s timeout. **An aggregate label like "flaky" is a place where a measurement should be.**
