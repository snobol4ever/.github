# FINDING — an env-selectable ceiling turns a byte-identity control arm into a one-command diff on ONE binary

**hq_B · 2026-09-06 · OCTET · row `icon-generator-host-carve-sums-the-whole-component-and-reserves-66mb-on-jtran-main` (CEO-368, re-ruled CEO-370)**
**Tree measured: SCRIP `d4eefd1ac`-DIRTY · corpus `1340f33ea` · .github `82c283c1`. Build: incremental `make` (`RT_OPT=-O0`).**

## The claim

When a cure is gated on a **threshold**, make the threshold **env-selectable**, and the "you changed
nothing else" control arm collapses from a two-binary bisect to a one-command diff **on a single binary**.

CEO-370 condition (a) required that every Icon generator host at or under the ceiling emit
**byte-identical `.s`**. The cure carries `SCRIP_ICN_GENHOST_STACK_MAX`. Setting it above every carve in
the corpus forces the old static path on **every** host, which is byte-identical to HEAD *by construction*
— so the control arm is:

```bash
./scrip --compile -o A.s prog.icn
SCRIP_ICN_GENHOST_STACK_MAX=2000000000 ./scrip --compile -o B.s prog.icn
cmp A.s B.s
```

Swept over every `.icn` under `corpus/demos/icon` and `corpus/benchmarks/icon`:

| result | count |
|---|---|
| byte-identical | **40** |
| differ | **3** |
| did not compile (both arms) | 3 |

and the three that differ are **exactly** `jtran`, `icon_parser`, `icon_recognizer` — precisely the
over-ceiling population. Condition (a) is therefore **measured, not asserted**.

## Why one binary beats two trees

A two-tree control (clean checkout vs cured checkout) can be confounded by a rebuild, a rebase, a
different objdir, or a header touched between the two builds — and none of those announce themselves; the
diff just comes back non-empty and you go hunting. The env toggle holds **the binary, the objdir, the
corpus and the clock** fixed and moves exactly one thing. It is the same discipline as ASM-DIFF-FIRST's
"a passing sibling with one ingredient removed", applied to the control arm instead of the witness.

⭐ The same toggle also gave a **free board-level control arm**. Icon master run twice on one binary,
cure ON and cure OFF:

| arm | m3 | m4 | entries | reds |
|---|---|---|---|---|
| cure ON | 697/702 | 697/702 | 855 | 5 × 2 modes |
| cure OFF | 697/702 | 697/702 | 855 | **the same 5** |

Identical verdict, identical red *names* (`ladder_rung41_rt_delay`,
`ladder_rung41_rt_getch_getche_kbhit_on_eof`, `ladder_rung41_rt_chdir_getenv`,
`ladder_rung41_rt_loadfunc_refusal`, `procedure_every_alt_replace_4`). Those five are **standing**, and
the cure costs zero. Without the toggle this arm needs a second checkout and a second 6-minute board.
SNOBOL4 master (shared-node arm): m3 1857/1858, m4 1857/1858, the single m4 red **named** as
`user_function_keyword_branch_3` (hq_P rank-0, tolerated per CEO-359, not counted).

## The measurement that killed the authorised floor

CEO-368 authorised, as an acceptable first landing, a **compile-time refusal keyed on carve size**. It
cannot be built without reding green programs, and the reason is a distribution, not an opinion. Censused
every Icon demo+benchmark program's largest `sub rsp`:

| program | carve | ran? | vs `icont` |
|---|---|---|---|
| `jtran.icn` | 66,457,856 | rc=1 `ERROR 246`, 5 of 5 | — |
| `icon_parser.icn` | 33,210,064 | rc=0 | ✅ matches |
| `icon_recognizer.icn` | 20,317,856 | rc=0 | ✅ matches |
| **every other program (40)** | **65,544** | rc=0 | ✅ |

⛔ **The distribution is BIMODAL: nothing exists between 65,544 and 20 MB.** There is no threshold that
catches jtran and spares the two that pass the oracle **today**. A size-keyed compile-time refusal is a
gate broader than its rule. Reported instead of landed; CEO-370 withdrew the floor on this measurement
and authorised **carve small, allocate big**.

⭐ **The general form, which is the half worth keeping:** a threshold is only tunable if the population is
a *gradient*. Census the distribution **before** picking the number — a bimodal population will accept any
threshold you propose and quietly take green programs with it, and the board will not tell you, because
the programs it kills were passing for reasons the threshold never looked at.

## What the cure does, and the hazard in it

`icn_gen_host_slice` sums one slice **per generator call site**, and each slice recursively contains its
own callee's slices — a full expansion of the transitive call tree. Deduping is **not** the cure:
`icn_gen_host_reserve_offset` hands each call site its own offset, so two calls to one generator
legitimately need two slices. The per-call-site sum is right; **carving it on an 8 MB machine stack is
what was wrong**. Above the ceiling the block is allocated instead of carved and reached through one frame
slot. After: all three carve 65,544, jtran runs rc=0, both controls still match `icont` byte for byte —
the four-clause DONE-WHEN returns PASS.

⛔ **THE HAZARD, and it is silent:** an off-stack block holds live descriptors and **the collector cannot
see it**. The old carve was scanned *only* because it lay inside the conservatively-scanned machine stack
(`gc_heap.c` `gc_collect_ex`, the `cons_stack` arm). An unrooted block is **heap corruption that no board
goes red on**. It must be registered — `rt_gc_root_range_add_topword(base)` scans exactly `[base, *base)`
for a bump arena; the cto's landed shape uses `calloc` + `rt_gc_root_range_add`/`_del`.

## Provenance

Design and DONE-WHEN: hq_B. ⚠️ **The cure is BEING landed by the cto** (CEO-370) and, as of this
document, is **NOT yet on `origin/main`** — checked, tip `581bc501a`; do not read this FINDING as a
landing receipt, and take the cto's own receipt for that. Their shape releases the block on every exit
path — the letter of condition (b) — and additionally cures the co-expression birth face (a fresh block
per birth, the create snapshot otherwise sharing one slice). hq_B's own build met (b) only in spirit, via
a lazy shadow stack, and was **not** landed for that reason; it is preserved as a patch, not pushed, so
two shapes of one cure never race on the same files. The env var name is shared verbatim across both
shapes, so this document's procedure applies to whichever lands.

⛔ **Two clauses of CEO-370 are owed by the landing, not by this document:** (b) is met by the cto's
explicit release, with one **named** gap — a host nested inside a co-expression destroyed via
`9cfdc2b8a`'s longjmp exit skips the release; and (c) **hq_U has not co-signed** the frame-model change.

⭐ **The next defect is already located and is NOT this one** (cto, measured under gdb): with the carve
bounded, the 17-module `jtran` symbolic stage still dies *inside* the block — the 63-slot cycle cut sizes
an activation's callee area as **one cycle sum** while the call-site offsets are laid out as **full
inflated slices**, so a recursive callee that is not the first generator site in a body starts near the
end of its container and overruns it. Container and contents are sized by two different rules. That is a
sizing defect, distinct from the storage-location defect this row cured, and it is not covered by "the
per-call-site sum is right" above.
