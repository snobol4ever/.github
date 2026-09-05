# FINDING 2026-09-05 hq_P — DEFINE redefinition is deduped in the compile-time `defs[]` table, so the last DEFINE wins *retroactively*

**Measured:** hq_P, 2026-09-05, SCRIP `94f894b80` (incremental `make`), both modes, oracle
`/home/resources/x64/bin/sbl -bf` (post-10:34 swap, md5 `bc694a0cc699f91d06ff7fde01732000`).
**Row:** `define-redefinition-ordering` (rank 3, hq_P lane) · umbrella
`snobol4-every-xfail-fixed-as-a-faulty-test-or-cured-as-a-defect`.
**Witnesses:** master entries `user_function_replace_4` (1816), `user_function_replace_7` (1817).

## 1. The behaviour, re-verified against today's tree

    DEFINE('F()')            :(E1)
    F   F = 'first'          :(RETURN)
    E1  OUTPUT = F()
        DEFINE('F()','G')    :(E2)
    G   F = 'second-via-alt-entry'  :(RETURN)
    E2  OUTPUT = F()

| | line 1 | line 2 |
|---|---|---|
| oracle | `first` | `second-via-alt-entry` |
| SCRIP m3 **and** m4 | `second-via-alt-entry` | `second-via-alt-entry` |

`user_function_replace_7` is the same shape with an argument and two body labels (`F1`/`F2`) and fails
identically (`second:a` / `second:b` where the oracle prints `first:a` / `second:b`).

**m3 and m4 are byte-identical**, which places the defect in shared ground — lowering, not a runtime or a
per-mode codegen arm.

## 2. Root cause — three identical lines in `lower_snobol4.c`

The compile-time DEFINE table is **keyed by function name and overwritten in place**:

    lower_snobol4.c:2622   for (int k = 0; k < ndefs; k++) if (!strcmp(defs[k].fname, d.fname)) { found = k; break; }
    lower_snobol4.c:2623   if (found >= 0) defs[found] = d;            /* ← the second DEFINE REPLACES the first */
    lower_snobol4.c:2624   else if (ndefs < SNO_DEF_MAX) defs[ndefs++] = d;

The same three lines appear at `:2602-2604` (body-form DEFINE) and `:2446-2448` (`sno_prescan_expr`).
So a program with two `DEFINE('F'…)` statements ends lowering with **one** `defs[]` row — the last one —
and only that body is ever built, named, and emitted.

Proven by instrumenting the driver's dentry loop (`scrip.c:1388`, probe reverted, tree clean):

    DBG bind sval=F
    DBG   proc[1] name=LBL__G  entry=0x3a33a070
    DBG   proc[2] name=F       entry=0x3a33cb00
    DBG   matched proc[2] name=F _gd op=37 sval=G      ← GOTO_DEFERRED to G
    DBG bind sval=F                                    ← the SECOND bind
    DBG   matched proc[2] name=F _gd op=37 sval=G      ← resolves to the SAME proc

There is exactly **one** proc named `F`, and it is the *second* DEFINE's (its stub defers to `G`).
`LBL__F` and a first `F` proc do not exist at all. The emitted asm agrees — one `F_α` label, and both
registration sites pass the identical pointer:

    57:   lea   r9, [rip + F_α]     …   61:  call rt_define_site@PLT
    336:  lea   r9, [rip + F_α]     …   340: call rt_define_site@PLT

## 3. ⭐ The ordering machinery is already correct — it is being fed identical pointers

This is the part that changes how the cure should be scoped, and it is the opposite of the inherited
characterization ("resolved as if declarative/hoisted"). **The registration is not hoisted.** Both
`rt_define_site` calls are emitted *at their own statement*, in program order — `bb_define.cpp:263-275`,
whose own comment reads "DEFINE-SITE s57: constant-folded registration AT the statement". The runtime
already anticipates redefinition: `rt_define_site` (`rt.c:1770`) finds the existing proc, sets
`p->redefined = 1`, and repoints `p->fn`; `rt_define_tiny_ok` then refuses the tiny fast path for a
redefined function.

⛔ **So the defect is not "DEFINE is declarative". It is that both ordered registrations name the same
body**, because the compile-time table kept only one. An ordered mechanism fed a deduped table produces
output indistinguishable from a hoisted one — which is exactly why the symptom was read as hoisting.

⭐ **The transferable shape: a correct sequencing mechanism can be made invisible by a dedupe upstream of
it, and the symptom then names the wrong subsystem.** Two sittings recorded "declarative/hoisted" from the
output alone; the asm shows the sequencing is there and firing twice.

## 4. Eliminated, so the next seat does not re-spend it

- `SCRIP_DEFINE_FN_DIRECT_ALPHA=0` — the template's own killswitch on the branch that rewrites the target
  label to `fname + "_α"` (`bb_define.cpp:266`). **Changes nothing** on either witness. It was the obvious
  suspect and it is not the cause: with only one `defs[]` row there is only one body to point at, so no
  label choice can distinguish the two DEFINEs.
- Not a runtime-library defect, not mode-specific (m3 ≡ m4), not the `dentry` first-match in
  `scrip.c:1388` — that loop *does* take the first proc named `F`, but there is only one to take.

## 5. Cure design (not landed — deliberately)

Keeping both rows in `defs[]` is one line at each of the three sites, but it is **not sufficient alone**
and must not be landed on its own: two rows both named `F` would then create two `proc_table` entries
with the same name, and the alpha label is emitted per proc *name*, so they would collide and the last
would still win. A complete cure is three coordinated parts:

1. `defs[]` keeps every DEFINE (append, never overwrite) at all three sites above.
2. `proc_table` names them distinctly when a name repeats, so each DEFINE gets its own emitted alpha body.
3. The driver's dentry loop (`scrip.c:1388`) maps the **Nth bind node** for a name to the **Nth def** for
   that name — `stmt_bind_fname[]` already records the bind statements in source order, so the ordering
   information the loop needs is present and only the pairing is missing.

⛔ Then the existing `rt_define_site` chain gives correct last-wins-at-execution-time semantics with no
runtime change at all.

**Blast radius:** DEFINE dispatch is shared ground for every SNOBOL4 program with a function, so this
lands with the full 1859-entry master as its control arm, both modes, plus the Icon watermark — not with
the two witnesses alone. That is why it is recorded here rather than half-landed: the diagnosis is
complete and cheap to act on, the change is not.

## 6. State

Zero `src/` edits. The instrumentation used in §2 was reverted and the revert proven by control arm —
the defect still reproduces on the reverted tree and `git status` is clean, so the diagnosis was not read
off a modified binary.
