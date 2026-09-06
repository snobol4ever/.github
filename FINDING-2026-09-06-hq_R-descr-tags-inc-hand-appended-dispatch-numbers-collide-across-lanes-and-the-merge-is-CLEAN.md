# FINDING — `descr_tags.inc` allocates dispatch numbers by hand-append, so two lanes collide by construction — and the bad outcome is a CLEAN MERGE, not a conflict

**hq_R · 2026-09-06 · FLEET-12 · measured live, two lanes, one hour · SCRIP `a669b745f` vs seat10's uncommitted tree**

Routed to hq_T (instruments are its lane) and to the ceo. This file exists because a telegram is not version-controlled and this class will recur.

## THE MEASUREMENT

`src/ir/descr_tags.inc` allocates `MOD_OP` dispatch numbers by **hand-appending at the tail of the file**. Nothing checks that the numbers are unique. Two lanes, working two different rows in the same hour, both appended `156`:

| lane | row | constant |
|---|---|---|
| seat10 | `prolog-inria-arithmetic-errors-escape-catch3` | `#define MOD_OP_RT_PL_AX_EGUARD 156` |
| hq_R (`a669b745f`) | `prolog-inria-is-nested-unevaluated-arithmetic-type-error` | `#define MOD_OP_RT_PL_IS_V 156` |

hq_R's landing consumes **156 through 200** — 45 constants, one per new veneer in `rtx_plunify.s`. Neither lane knew about the other until hq_R read seat10's root for an unrelated reason (it had not answered a control-arms message).

## ⛔ WHY THIS IS AN INSTRUMENT DEFECT AND NOT A COORDINATION MISHAP

**The dangerous outcome is not a merge conflict — it is a clean merge.** Both lanes *append*, so the two hunks land at different offsets and git can auto-merge them with **no conflict at all**, leaving two different `MOD_OP`s both numbered `156`.

- Nothing fails at merge time.
- The build is green.
- **Both lanes wrote gates, and neither gate can see it** — a gate grades behaviour reachable from its own witnesses, and the collision corrupts a *dispatch table entry* that the other lane's op travels through.

The dispatch table then quietly routes one op to the other's implementation. **A conflict would have been the safe outcome.** This file is shaped so that the silent outcome is the likely one, and it is reached by every lane that adds a veneer — not just the two Prolog lanes that happened to notice.

⭐ **The general form, which is the reusable half:** an append-allocated ID space with no uniqueness check does not fail *loudly* under concurrency — it fails *invisibly*, and it fails worse the further apart the two lanes are, because distance is what removes the chance that either one reads the other's tree.

## THE INVARIANT — one line, sub-second, offline, no build

```bash
grep '^#define MOD_OP' src/ir/descr_tags.inc | awk '{print $3}' | sort -n | uniq -d
```

**EMPTY is the invariant**; non-empty names the colliding numbers. Measured on `a669b745f`: empty over **71** `MOD_OP`s.

Fail-once is free here — add a second `#define` with an already-used number, watch it print, remove it. No build, no board. It belongs in the cheap-arms-first half of `make test`, beside `strip_comments.py --check`.

## WHAT WAS ALREADY CHECKED, AND IS NOT THIS

`test_gate_icn_tag_single_source.sh` and `util_tag_layout_verify.py` both touch `descr_tags` and **neither checks for a duplicate `MOD_OP` number** — grepped, not assumed. The invariant is genuinely ungated today.

## DISPOSITION

- seat10 told to renumber to **201** after rebasing onto `a669b745f`, and to run the `uniq -d` check before pushing. **That handles today's instance and nothing else.**
- hq_T holds the instrument. The wider question — explicitly hq_T's to rule on, not hq_R's — is whether any *other* hand-appended numeric ID space in this tree has the same shape. If there are others, **one generic uniqueness gate over a list of (file, pattern) pairs beats N copies**, which is the argument that already produced `lib_ladder.sh` and `lib_port_trace.sh`.
