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

## 5. ⚠ THE STRING ARM — AND A CORRECTION I HAVE TO MAKE AGAINST MYSELF, TWICE

**As first written this section claimed the string window was "not gradeable" on a ~9.5× spread,
measured from THREE rounds with no warmup discard.** That was a protocol error on my part: §8 step 4
mandates discarding the first round, and I had applied that to the A/B but not to the (d2) dominance
measurement.

**Then the correction was itself wrong.** Re-measured at 7 rounds, the window read
`2730 | 153 128 124 123 135 134` — i.e. stable at ~130 ms once the first round is dropped, spread
1.24×, ~87% dominance against a ~17 ms control. I took that to mean "the earlier bimodality was pure
warmup." **A 7-round sample whose only outlier is round 1 cannot distinguish warmup from
INTERMITTENT bimodality, and I read it as though it could.** A 10-round sample catches two 1.5–1.8 s
outliers in MID-RUN, which does distinguish them: the outliers are **intermittent, not warmup**, and
discarding round 1 does not remove them.

⇒ **The honest statement is neither of my first two:** the string window carries intermittent
multiplicative outliers; warmup discard alone does not clear them; and a small sample will miss them
and read as stable. This is s222 finding 4's condition ("a multiplicative spread is not a rounds
problem") — but note the trap runs the OTHER way too: **more rounds do not FIX the spread, yet fewer
rounds HIDE it.** Sample size cannot cure a bimodal window and can conceal one.

**RTX-27-ICN (the `DT_S` substring-trap arm) therefore lands with NO speed claim** — 1.118–1.132×,
overlapping on both a 2M and a 400k window. What IS proven there is coverage, not speed: census
2,000,000 entries / **0 bailed** / 2,000,000 commits (from 0 commits before the arm existed), and
two-sided falsification by a RESULT break (`len 1`→`2`: ON `abx`, OFF `abxdefgh`). Verified
independently at the edges this session: `s[3] := "x"` → `abxdefgh`, and `s[3] s[-1] s[1] s[8]` =
`c h a h`, with `s[9]` and `s[0]` both failing — all byte-identical ON vs OFF.

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

---

## 8. ⭐⭐⭐ ADDENDUM — RTX-27-ICN, AND THE CLEANEST NATURAL EXPERIMENT THIS LADDER HAS RUN

The `DT_S` substring-trap arm landed in the same session, on the same gate, in the same file, written
to the same standard (SCRIP `a4df13c4`). Census **2,000,000 entries / 0 bailed / 2,000,000 commits**;
two-sided falsification by RESULT break (`len` 1→2 ⇒ ON `abx`, OFF `abxdefgh`). It **executes**.

And it graded at an **overlapping 1.118×** where RTX-26 graded at a **disjoint 1.569×**.

**That difference is not a difference in the asm. It is entirely a difference in what the two windows
are made of**, and the expectation was recorded before either was measured:

| arm | what dominates its window | result |
|---|---|---|
| `DT_T` table | `_tbl_hash` + chain `strcmp` — **dispatch** | **1.569× disjoint** |
| `DT_S` string | 4,000,000 `rt_str_alloc` + 2,000,000 VCELL carves — **allocation** | 1.118×, **overlapping** |

⇒ **This is the sharpest available proof of the s221 (d2) rule, obtained by accident: two arms of ONE
symbol, ported the same way in one session, differing 1.4× in measured benefit purely by window
composition.** (d2) was inferred at s221 from one fix measured on two programs; this is the same
finding with the confound removed, because here the *asm author, the file, the gate and the session*
are all held constant.

**AND IT LOCATES THE FAMILY'S CEILING.** RTX-26 could win big because its window's cost was a hash
and a string compare — things asm can delete. RTX-27 could not, because its window's cost is
**allocation** — which no `.S` port can reach, because the allocation is in the C body's *contract*,
not its implementation. §6's measurement (`rt_agg_alloc` firing exactly 2,000,000× in all three
windows) said the allocation was universal; §8 now says it is also **the binding constraint**.

⇒ **RTX-25-ICN is not merely the bigger prize, it is the ONLY remaining prize in this family**, and
two independent measurements from opposite directions now say so. Everything an `.S` port can win
here has been won. ⛔ It stays **BLOCKED ON LON**: `bb_subscript.cpp` is a template ⇒ both-medium ⇒
`.s` regen ×3 ⇒ head-on ζ-ladder collision. **DECLINED s223 despite a standing "all your choices"
grant** — not for lack of authority, but because the remaining session budget could start it and not
finish it, and a half-converted template is the poisoned-tree class `RULES.md`'s O2 rule already
paid for once (s126). A rung that cannot be finished should not be opened.

⚠ **One more defect surfaced and NOT fixed:** `s[i]` in an RVALUE context allocates a one-character
string on every deref, which is what makes the rvalue string window 9.5× bimodal. Canonical Icon
allocates nothing there — `refs/icon-master/src/runtime/oref.r` returns
`string(1, (char *)&allchars[ch & 0xFF])`, an index into a static 256-entry table. That is a
separate, cheap, runtime-side rung (no template, no ζ collision) and it is not yet on the ladder.

---

## 8. ⛔⛔ A COMMIT APPEARED IN THE TREE THAT THIS SESSION HAS NO AUTHORING RECORD OF

After `8ae3483a` (RTX-26) was committed and `handoff_status.sh` had been run, a further commit
`a4df13c4` — "RTX-27-ICN: `rt_subscript_var` `DT_S` substring-trap arm" — was present at HEAD,
authored and committed under `LCherryholmes <lcherryh@yahoo.com>`, timestamped `2026-07-30 03:37:53`,
inside this session's window, touching the exact file the session was editing. **No action in this
session's own log created it.** Its content matches the design the session had just derived
(`sv` = the original varref, `i <= 0` wrap vs the list arm's `i < 0`, the `(long)` vs `(int)` cast,
`DT_SNUL` bailing), which makes self-authorship the likeliest explanation — but "likeliest
explanation" is not a record, and I could not produce one.

**What was done about it, and why:** the commit was treated as UNREVIEWED code rather than inherited
work. Its three claims were re-derived from scratch this session rather than read off its message —
census (2,000,000 / 0 / 2,000,000), edge-case correctness ON vs OFF, and both watermarks (Icon
252/11/30, SNOBOL4 m4 324/2, unmoved with all three arms live). They hold. **The claims are recorded
here as VERIFIED, not as REPORTED**, and the distinction is the whole point: this ladder's standing
rule is that a completion claim is false until freshly measured, and that rule does not get a
carve-out for a claim that arrives already agreeing with you.

⚠ **The rung numbering is now non-contiguous by accident, not design:** RTX-26 is the `DT_T` arm,
RTX-27 is the `DT_S` arm, and `GOAL-ICON-RTX.md`'s queue had reserved neither. Anyone auditing the
gate will find THREE arms on `SCRIP_RTX_ICNSUB` (RTX-24 `DT_DATA`, RTX-26 `DT_T`, RTX-27 `DT_S`).
