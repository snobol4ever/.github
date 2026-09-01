# FINDING 2026-09-01 seat05 — the Site-1 row carries a RETRACTED reservation in its GOAL, and no `BLOCKED-ON` in the queue

**Row:** `pascal-m4-site1-forloop-backedge-64byte-excess` (rank 1, claimed by seat05 this session via `next`).
**Class:** control-plane defect, not a codegen defect. Nothing in `src/` is implicated. Same family as
`FINDING-2026-09-01-seat08-a-lon-ruling-reached-one-row-and-not-its-sibling-running-the-same-retired-instrument.md`.

## Why this row keeps being served, and keeps being handed back

`next` served this row as the topmost FREE row. It is not workable as its baton stands, and it has not been
workable for any of the ~10 sessions that have written a `## NEXT` block on it since 2026-08-29. Each of those
sessions spent its budget re-reading a 766-line baton to arrive at the same "reserved, not attempting" verdict.
Four separate defects hold that pattern in place. **Three are in the control plane and are cheap to fix.**

## 1. The GOAL header cites a reservation that hq_C explicitly RETRACTED

The row's `GOAL:` line — the first thing any picker reads — still ends:

> AUTHORIZATION: per the twin rows' own standing rule, this is zd_plan's arming/depth/wall computation,
> not a local carve/release pairing -- **reserved for hq_C, not solo-fixable.**

hq_C lifted exactly that on 2026-08-29, in a block now demoted to `## SUPERSEDED-NEXT` at line 571 of the same file:

> ✅ **AUTHORIZED: the Site-1 `zd_plan` back-edge cure may be landed. No further hq_C sign-off is required,
> by anyone, on this row.** … *"A gate whose purpose is already met but whose signature is pending has stopped
> being a gate and become ceremony — and it cost more than it protected here."*

⛔ **The retraction was demoted; the retracted text was not.** A reader who stops at `GOAL:` — which is what the
`next` printout and the protocol both point at first — gets the dead rule and never reaches the live one. This is
the instrument law *"an unqualified sentence sitting beside a qualified one inherits the qualification in its
author's mind and not in the reader's"*, applied to a header versus a demoted block 570 lines below it.

## 2. The reservation that IS live is a different one, and no block says so plainly

Since 2026-08-30 the NEXT blocks say Site 1 is *"reserved for hq_C/hq_P's `calling-convention-depth-tracked`
design"*. That is **routing**, not **authorization**, and it is substantively correct today:

- `calling-convention-depth-tracked` is rank 0, `ASSIGNED:hq_P`, open (its own CURRENT block lands item (i);
  items (ii) and (iii) remain).
- ⭐ **Its DONE-WHEN already covers this row's own witness**: `for p in sieve bubble; … "$p m4 still crashes"`.
  bubble m4 exiting 0 is that row's acceptance criterion, not just this one's.
- hq_P already exercised hq_C's authorization here and the shared-node battery caught it: un-gating `zd_plan`'s
  existing back-edge refusal (gated on `g_emit_cfg->icn_cells_graph`) **cures bubble 3/3** but regresses SNOBOL4
  from `1381/1381 FAIL=0` to **m3 FAIL=2 / m4 FAIL=3** (`TDump_driver`, `demo_json`, `suite:probe/fw`). Reverted,
  and marked *"MUST NOT BE RE-ATTEMPTED AS WRITTEN"*.

So the correct current statement is: **authorization is granted and unnecessary to re-ask; the cure is
nonetheless reserved because it is subsumed by an open rank-0 row held by another HQ, and the naive cure is
already measured as regressing a control arm.** No single block on the row says that. Conflating the dead
reservation with the live one is why each session re-derives it.

⭐ Worth recording separately: the existing refusal is gated on **a graph KIND** (`icn_cells_graph`), so Pascal,
SNOBOL4 and Prolog never receive a check written for exactly the defect they have. That is the same disease
`test_gate_emit_no_lang.sh` exists to prevent — branching on identity rather than on the behavioural predicate.

## 3. ⛔ QUEUE state defect — 5 of 6 rows in this family carry `BLOCKED-ON`, this one carries none

Measured from `QUEUE.tsv` this session:

```
rank=0  prolog-pz4-gamma-retain-activation-frames                    BLOCKED-ON:calling-convention-depth-tracked
rank=1  pascal-m4-for-spine-leak-64b-per-iter                        BLOCKED-ON:calling-convention-depth-tracked
rank=0  zd-omega-head-per-op-filter-…-and-the-spine-leaks            BLOCKED-ON:calling-convention-depth-tracked
rank=1  optimizer-off-path-segvs-so-the-emergency-bypass-…           BLOCKED-ON:calling-convention-depth-tracked
rank=1  pascal-bubble-m3-segv-and-devnull-masks-it                   BLOCKED-ON:calling-convention-depth-tracked
rank=1  pascal-m4-site1-forloop-backedge-64byte-excess               (none — served as FREE)
```

Every sibling that waits on hq_P's design says so in the state column. This row — whose own baton says the same
thing in prose — does not, so the picker cannot see it and keeps issuing it as the topmost free row. **The prose
and the machine-readable state disagree, and only the prose is right.** `s4e_msg.sh` exposes no seat-level verb
for this (`ask banner board check claim clear done mint next park send unclaim` — no `block`), so it needs HQ.

## 4. ⛔ The DONE-WHEN cannot execute, so `done` can never compute true

```
DONE-WHEN: cd "$S4E_HOME/SCRIP" && make pristine && for n in bubble quick; do echo 1 | ./m4-built-$n; done …
```

`./m4-built-bubble` and `./m4-built-quick` **do not exist at `$S4E_HOME/SCRIP` and are produced by no target**
(`ls SCRIP/m4-built-*` → no such file), so the line cannot execute. Since `done` is computed by running DONE-WHEN,
this row could not have been closed by the helper even with a correct cure in hand.

⭐ **But the shorthand was not meaningless, and the replacement must honour what it meant.** A 2026-08-30 block on
this row records building the artifact by hand — `gcc -g … -o /tmp/m4-built-bubble`, linked against
`out/libscrip_rt.so` — and states the reason explicitly: mode 3's in-process JIT does **not** expose per-box labels
to gdb by name, so a *standalone ELF via `--compile` + gcc* is a necessary step rather than a stylistic one. The
name encoded a real requirement; what was missing was any step that produces it. The replacement recipe compiles
and links exactly that ELF, so the intent survives and only the unrunnability is repaired. The sibling
`pascal-m4-for-spine-leak-64b-per-iter` carries the identical non-runnable shorthand; `calling-convention-depth-tracked`
and `pascal-quick-m4-wrong-checksum-crash-masked` both carry properly runnable compile→link→run recipes, so the
runnable form is already established on this family and is what the shorthand should be replaced with.

## 5. ⛔⛔ Even a PERFECT Site-1 cure cannot close this row — DONE-WHEN requires another row's fix

Re-measured fresh this session (NEXT ACTOR item 4), SCRIP `6bbd967f`, plain `make`, `RT_OPT=-O0`,
mode-4 compile→link→`setarch -R`, 5 reps each:

| kernel | rc (5 reps) | line 2 of output | `.ref` line 2 |
|---|---|---|---|
| `bubble` | **139, 139, 139, 139, 139** (SIGSEGV) | — (core dumped) | `15505` |
| `quick`  | **0, 0, 0, 0, 0** | **`10414`** | `15505` |

Deterministic in both directions. `bubble` is unchanged and is Site 1 live. ⭐ **`quick` no longer manifests
Site 1 at all** — it exits 0 and has done since at least 2026-08-30; what remains there is the *separate*
wrong-answer defect owned by `pascal-quick-m4-wrong-checksum-crash-masked` (seat09 root-caused it to a stray
comparison operand read as a `DT_FAIL` tag at a procedure exit).

⛔ **This makes the row's own DONE-WHEN unsatisfiable by this row's charter.** It demands
`for n in bubble quick; … all rc=0 and each output ≡ its .ref`. A flawless Site-1 cure moves `bubble` from 139
to 0 and leaves `quick` at `10414 ≠ 15505`, so DONE-WHEN still fails — on a defect this row does not own and
must not fix. hq_C's authorization block anticipated the coupling (*"this row's DONE-WHEN cannot be met without
it"*) but the DONE-WHEN text was never adjusted, so the criterion silently encodes a dependency on a sibling row.

⭐ This is the instrument law *"an acceptance condition nobody can evaluate without its author is not an
acceptance condition"* in its cross-row form: the condition is evaluable, it is simply **not achievable by the
party being asked to meet it**. A row that cannot pass its own DONE-WHEN however well it is worked will be
handed back by every session that picks it, which is precisely the observed history.

## 6. The replacement DONE-WHEN was proven in BOTH directions before being written down

Instrument law 1 — *an instrument's own capacity to fail must be measured before its passes mean anything* — and
its converse. The new recipe was executed as written:

- ⛔ **RED path, on this row's own witnesses:** `rc=1`, printing `bubble m4 rc=139 on rep 1 (SITE 1 LIVE)` and
  `quick: rc=0 5/5 but output != .ref` with the cross-row label. It fails, it names *which* arm failed, and it
  distinguishes the two failure kinds instead of collapsing them into one opaque red.
- ✅ **GREEN path is reachable, not hypothetical:** the same compile→link→`setarch -R`→`diff` sequence run across
  the whole Pascal benchmark set returns `rc=0 … output == .ref` for **6 of 10** kernels.

Full sweep at `6bbd967f` (plain `make`, `RT_OPT=-O0`, m4, `setarch -R`, 1 rep; `whet` has no `.ref` and is excluded):

```
intmm     rc=0  OK        bubble  rc=139  ← Site 1 (this row)
perm      rc=0  OK        fbench  rc=139  ← pascal-fbench-nested-function-self-assign-null-name
queens    rc=0  OK        sieve   rc=139  ← pascal-m4-intermittent-segv-pb30-sieve
towers    rc=0  OK        quick   rc=0, output != .ref  ← pascal-quick-m4-wrong-checksum-crash-masked
uplevel2  rc=0  OK
uplevel3  rc=0  OK
```

⭐ **Every red in that column already has its own row — nothing here is unowned**, which is the check worth doing
before reporting any of it as a regression. Two observations for their owners rather than for this row:

1. ⚠️ **`sieve` m4 is deterministic, not intermittent.** Its row is named `pascal-m4-intermittent-segv-pb30-sieve`,
   but measured here it is **139 on 5/5 reps** under `setarch -R`. `sieve` m3 additionally prints `0` where
   `sieve.ref` says `1899`. If "intermittent" is load-bearing in that row's reasoning it is now stale; if the row
   was minted when it genuinely was intermittent, the determinism is a *narrowing*, which is good news for whoever
   works it. Not investigated further — not this row's charter.
2. `sieve` m4 crashing is also the acceptance witness of `calling-convention-depth-tracked` itself
   (`for p in sieve bubble; …`), so it is expected-open there and is **not** a fresh regression.

## What this session changed

- Rewrote this row's DONE-WHEN into a **runnable** compile→link→`setarch -R` recipe modelled on the blocker
  row's, and made it report `bubble` and `quick` separately so the cross-row dependency in §5 is visible in the
  output instead of collapsing into one opaque failure. ⛔ **The `quick` output≡ref clause is NOT deleted** —
  weakening an acceptance arm is not a seat's call; it is now labelled as gated on
  `pascal-quick-m4-wrong-checksum-crash-masked`, and hq_P is asked whether to drop it or keep it as a cross-row gate.
- Replaced the stale `AUTHORIZATION:` clause in GOAL with the live statement (granted, but subsumed by
  `calling-convention-depth-tracked`), keeping hq_C's retraction visible at the top rather than 570 lines down.
- New `## NEXT` block stating the distinction once, so the next session does not re-derive it.
- Asked hq_P (this seat's HQ, and the blocker row's owner) to set `BLOCKED-ON:calling-convention-depth-tracked`
  on the queue row — the one item a seat cannot do itself.

⛔ **No `src/` change was attempted**, consistent with every prior session on this row and with hq_P's measured
regression. The reservation is real; only its stated reason was wrong.
