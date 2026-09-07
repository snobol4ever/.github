# FINDING — an env-selectable ceiling turns a byte-identity control arm into a one-command diff on ONE binary

**hq_B · 2026-09-06 · OCTET · row `icon-generator-host-carve-sums-the-whole-component-and-reserves-66mb-on-jtran-main` (CEO-368, re-ruled CEO-370)**
**Tree measured: SCRIP `d4eefd1ac`-DIRTY · corpus `1340f33ea` · .github `82c283c1`. Build: incremental `make` (`RT_OPT=-O0`).**

## ⛔⭐ CORRECTION, SAME DAY — LON REFUSED THE CURE THIS DOCUMENT WAS WRITTEN BESIDE

**Lon, 2026-09-06 20:18 CDT, in-chat to the ceo, verbatim: *"No activations on the heap."*** The frame law
stands unamended (`RULES.md` § BB FRAME-PLACEMENT CRITERION, Lon 2026-08-27): activation frames live on the
machine stack, no frame store may replace the deleted island, only genuine escapers go to the heap.
**`carve-small-allocate-big` is REFUSED as a landing** — the block is activation storage and does not go on
the heap *whatever frees it*, so neither the cto's explicit release nor hq_B's shadow stack rescues it.
CEO-370 and CEO-371 authorising it are **RETRACTED**; hq_U's objection was correct and stands as the
co-sign refusal it was. **Everything below describing that cure as landing or authorised is superseded by
this banner.** The cure is now, on the stack: per-**activation**, per-**path** carving of what a host
actually enters (never the worst-case transitive sum charged per call site), on the RSP spine or in the RBP
activation frame per the criterion; the sanctioned loud rc-refusal cap as the floor for anything still over
a ceiling after that; co-expression stacks sized to the snapshot.

⭐ **WHAT SURVIVES UNCHANGED, and it is why this document is corrected rather than deleted** — Lon's ruling
keeps all of it as the control arm: the **bimodal census**, the **43-of-46 byte-identity** arm, the
**env-selectable-ceiling technique** that made it a one-command diff, and the DONE-WHEN (jtran rc=0 with
`icon_parser` and `icon_recognizer` still matching `icont`). None of those depended on where the block
lived. ⛔ And one thing that is NOT contradicted: the measurement that killed the size-keyed compile-time
refusal was taken against the **old inflated per-call-site sums**. Once per-path sizing lands, the
over-ceiling population is a different set — so the cap returning as the floor is not a reversal of that
finding, it is the same finding applied after the sizing is fixed. Do not cite it either way without
re-censusing the distribution.

⛔ The **GC hazard** below is now moot for the landed shape (stack storage is scanned by the `cons_stack`
arm, which is the whole point of the law) — it is kept as the measured reason the heap shape was expensive,
not as a live instruction.

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

Design and DONE-WHEN: hq_B. ⛔ **NEITHER SHAPE LANDED.** The cto's explicit-release shape and hq_B's
lazy-shadow-stack shape were both heap blocks, and Lon refused the class outright (see the banner). Neither
was ever pushed to `origin/main`; the cto's branch is kept for its **measurements** and its **co-expression
face** (fresh block per birth — the create snapshot otherwise shares one slice), and the block itself is
deleted from it before anything lands. hq_B's build is preserved as a patch only.

⭐ **The one piece of hq_B's refused shape the ceo adopted before Lon's ruling, recorded because the reason
outlives it:** the reclaim-on-push sweep keyed on owner rsp, as a **backstop** under explicit release, for
the case an explicit release provably cannot cover — a host nested inside a co-expression destroyed via
`9cfdc2b8a`'s longjmp exit, which bypasses every epilogue. Any stack shape has the same hole and needs the
same answer; unwinding is what fills it on the stack.

⛔ **hq_U never co-signed**, and that is the load-bearing fact of this row, not a procedural footnote. The
co-sign requirement (CEO-359 / SHARED-NODE VERDICT SCOPE) is what caught this: two seats and the ceo had
converged on a cure that a third seat recognised as a frame-law violation on sight. A design reviewed only
by the people building it passes.

⭐ **The next defect is already located and is NOT this one** (cto, measured under gdb): with the carve
bounded, the 17-module `jtran` symbolic stage still dies *inside* the block — the 63-slot cycle cut sizes
an activation's callee area as **one cycle sum** while the call-site offsets are laid out as **full
inflated slices**, so a recursive callee that is not the first generator site in a body starts near the
end of its container and overruns it. Container and contents are sized by two different rules. That is a
sizing defect, distinct from the storage-location defect this row cured, and it is not covered by "the
per-call-site sum is right" above.
