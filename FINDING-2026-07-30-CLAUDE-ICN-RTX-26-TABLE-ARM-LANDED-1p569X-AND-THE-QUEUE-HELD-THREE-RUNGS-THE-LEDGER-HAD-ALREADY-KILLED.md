# FINDING-2026-07-30-CLAUDE-ICN-RTX-26-TABLE-ARM-LANDED-1p569X-AND-THE-QUEUE-HELD-THREE-RUNGS-THE-LEDGER-HAD-ALREADY-KILLED

**Session s223-ICN. Ladder `GOAL-ICON-RTX.md`. Contract `ARCH-ICON-RTX.md`. SCRIP `8ae3483a`.**

---

## 1. ⭐ RTX-26-ICN LANDED — the `DT_T` table arm, `1.569×` disjoint

`SCRIP_RTX_ICNSUB` widened from RTX-24's `DT_DATA` list arm to the `DT_T` table arm keyed by a
`DT_S` subscript. Two calls eliminated per subscript, both real calls at `RT_OPT=-O0`:
`_tbl_hash` (`aggregates.c:78`, static but not inlined at O0) becomes a 6-instruction loop with no
frame; the bucket-chain `strcmp` becomes an inline byte compare that stops on the first mismatch or
the shared NUL.

| | ON | OFF |
|---|---|---|
| 10 interleaved rounds, warmup discarded | 90–98 ms (spread 1.09×) | 141–154 ms (spread 1.09×) |

**1.569× median · 1.567× min-min · DISJOINT.** `RT_OPT=-O0`. Beats RTX-24's 1.376× on the same symbol.

**Two-sided falsification by breaking a RESULT, not a route** (§8): `&e->val` → `&e->key_descr`
⇒ gate ON prints `0`, gate OFF prints `14000000`. The asm provably executes and the switch
provably switches.

**Gates:** Icon **252/11/30 unmoved** · SNOBOL4 **m4 324/2 unmoved** (m3 329/5) · Prolog
`test_corpus_prolog_parser.sh` FAILs identically at gate ON **and** OFF ⇒ the differential is an
**identity**, pre-existing/environmental, **not this rung's** (s222's condition, reproduced exactly,
not inherited on trust).

**No `.s` regen owed** — `runtime/rtx/*.S` + `rtx_init.c` only, zero templates.

---

## 2. ⭐⭐ THE MISS PATH MUST BAIL, NOT FAIL — AND `FAILDESCR` WOULD HAVE BEEN SILENT

On a chain miss the C body **does not fail**. It mints a key-**INSERT** trap: `cellp = 0`,
`tbl = tb`, `key = rt_ws_strdup_c(ks)` — an allocation and a copy, so that `t[k] := v` on a fresh
key has somewhere to land. An asm arm that returned `FAILDESCR` on chain-exhaustion would read as
correct on every rvalue workload in the corpus and would **silently break lvalue insert**. The arm
therefore tail-jumps to C with byte-identical arguments on the miss.

**The census makes this visible rather than theoretical:** after the port the table window reads
**2,000,001 entries / 1 bailed / 2,000,000 commits.** That single bail is `t["alpha"] := 7`, the
one fresh-key insert in the program. A port that "handled" the miss would have shown 0 bails and
been wrong.

---

## 3. ⭐⭐⭐ THE QUEUE LISTED THREE RUNGS AS OPEN THAT THE LEDGER HAD ALREADY MEASURED DEAD

`GOAL-ICON-RTX.md`'s PHASE 1 queue carries, verbatim, "**Step 0(d) first**" on RTX-1-ICN, RTX-2-ICN
and RTX-3-ICN. `RTX-CLAIMS.md` — the file both documents name as the single source of truth —
records that step 0(d) has **already been run on all three and came back dead**:

| queue rung | symbol | ledger state |
|---|---|---|
| RTX-2-ICN ("#2, 897 sites") | `rt_arg_stage` | ⛔ `BLOCKED:MEASURED-ZERO` |
| RTX-1-ICN ("361 + 210×4") | `rt_proc_set_fn` | ⛔ `BLOCKED:MEASURED-FLAT` |
| RTX-3-ICN ("542") | `rt_call_proc_descr` | ⛔ `BLOCKED:MEASURED-ZERO` |

A session that oriented off the ladder — which is what the ladder is *for* — would have opened
RTX-2 as the rank-2 prize and spent its whole 0(d) budget re-deriving a zero the ledger already
held. **This is s222 finding 7 recurring with a different set of rows, and it is the third
consecutive session to find the ladder disagreeing with the ledger.** Corrected in place: the three
queue rows now carry their ledger verdicts inline.

⇒ **PROPOSED, needs Lon:** the queue should not restate a symbol's step-0 status at all. It should
name the symbol and the gate and let `util_rtx_claims.sh` supply the state, the way the §Concurrency
table was already demoted to a pointer at s222. Two files that both hold status will disagree; the
only stable fix is for one of them to stop holding it.

---

## 4. ⛔ RTX-24's "LOCAL COMMIT ONLY — NOT ON origin" BANNER WAS FALSE

`GOAL-ICON-RTX.md` s222 states, twice and in bold, that RTX-24-ICN is a local commit on a
disposable sandbox and that the s202 ancestry check is unsatisfiable. **Measured at the top of
s223 from a fresh clone, before any edit:** `rtx_icnsub.S` is present, the adding commit is
`b38e31d8`, `git rev-list --count origin/main..HEAD` == **0**, and `rtx_icnsub.o` is in the
`libscrip_rt.so` link line. **RTX-24 is on `origin/main`.** The `[x]` was honest; the banner
warning against it was not.

This is `RULES.md` s47 rule (a) exactly — *"NEVER WRITE PUSH STATUS INTO A DOC… a claim about an
event that occurs AFTER the text is frozen into the commit is structurally incapable of being
true, and it is never corrected afterward because nobody edits a committed session-state block."*
The rule names the failure, the rule was in force, and the banner was written anyway, because the
session that wrote it genuinely could not push and had no way to know a later push would succeed.
⇒ **The lesson is not "try harder." It is that the banner has no correct form and must not be
written.** Voided in the goal file; `handoff_status.sh` remains the only ground truth on push state.

---

## 5. ⚠ THE STRING ARM IS LIVE, UNPORTED, AND ITS WINDOW IS NOT GRADEABLE

`s[3]` measured **2,000,000 entries / 2,000,000 bailed / 0 commits** — as live and as unported as
the table arm was. But its wall clock is **1717 / 180 / 1275 ms**, a ~9.5× multiplicative spread.
The cause is structural, not noise: `s[i]` mints a substring trapped variable whose consumer's
`rt_deref` then allocates a one-character string, so the window carries **two** allocations per
iteration and is allocation-dominated. Per (d2)'s own prohibition — *never grade a dispatch port on
an allocation-dominated window* — **the string arm cannot be graded until the window is rebuilt**,
and s222 finding 4 already established that more rounds cannot fix a multiplicative spread.
Recorded so the next session does not read the bimodality as a refusal of an unwritten port.

---

## 6. ⭐⭐ EVERY ARM ALLOCATES A VCELL IT THROWS AWAY — RTX-25's CASE IS NOW MEASURED ON THREE ARMS

`rt_agg_alloc` fires **exactly 2,000,000 times in all three windows** (list, table, string) —
one 72-byte `VCELL_t` per subscript, on every arm, in an rvalue context that immediately
`rt_deref`s the cell and discards it. Canonical Icon does not allocate to fetch an element:
`refs/icon-master/src/runtime/oref.r`'s `operator{0,1} [] subsc` returns
`struct_var(&bp->lelem.lslots[i], bp)` — a pointer **into the existing element block**. The table
arm is the one place canonical Icon *does* allocate (`alctvtbl`, a table-element trapped variable),
so SCRIP's table behaviour is right and its list/string behaviour is not.

⇒ **RTX-25-ICN's premise is now measured across the whole family rather than one arm, and it
dominates RTX-26 by construction:** RTX-26 makes each arm's dispatch ~1.57× cheaper while leaving
the allocation in place; RTX-25 removes the allocation. **RTX-25 remains blocked on Lon** —
`bb_subscript.cpp` is a template ⇒ `.s` regen ×3 ⇒ ζ-ladder collision ⇒ must be serialized, not
run concurrently. RTX-24's and RTX-26's asm arms are not wasted by it: both remain the lvalue path.

---

## 7. Ledger

`rt_subscript_var` — `DONE:ICON-RTX:s222` (DT_DATA list arm) **+ s223 `8ae3483a` (DT_T table arm)**.
Same gate, same file, arms selected by disjoint subscript tags. Still C on that symbol: `DT_A`
arrays · `DT_S`/`DT_SNUL` string subscripting (live, ungradeable window, §5) · non-integer
subscripts · the `slen==2`/`slen==0` VARREF forms · the table MISS/insert path (deliberate, §2).

⚠ The `DT_S` arm wraps on `i <= 0`, the `DT_DATA` arm on `i < 0`. Two arms, two rules, one
function. **Still do not tidy that** — reconfirmed by reading the C, s223.

---

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
