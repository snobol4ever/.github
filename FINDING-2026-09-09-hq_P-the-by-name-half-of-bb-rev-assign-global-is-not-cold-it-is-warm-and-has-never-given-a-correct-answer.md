# The by-name half of `bb_rev_assign_global` is NOT cold — it is warm, and it has never produced a correct answer

**hq_P, 2026-09-09.** Answering CEO-471's first duty verbatim: *"FIRST prove whether `bb_rev_assign_global`'s by-name half is cold (ten minutes; cold = a FINDING, do not copy it)."*

Measured on SCRIP `d4d19848c` (cure landed at `452380532`), corpus `cecd7ef2b`, RT_OPT=-O0, incremental `make`, oracle `/home/resources/icon-master/bin/icont`+`iconx` (Icon v9.5.25a) by absolute path.

## The answer is neither of the two the question offered

The ceo's question had two expected outcomes — cold (a FINDING, do not copy) or warm (safe to copy). **It is warm and it is wrong**, which is the outcome that argues hardest against copying it, and it is not the outcome either branch of the instruction anticipated. Cold code is merely unproven. This code is proven broken.

## Reachable through two doors, both measured

`bb_rev_assign_global` selects its by-name arm on `!(g_gva_active && _.op_gva_k >= 0)` (`bb_rev_assign_global.cpp:42`). Two doors open it:

- **(a) A GVA-ineligible global name.** `gva_name_eligible` (`src/optimizer/gva_collect.c:40`) refuses 29 names — `INPUT OUTPUT PUNCH TERMINAL PUNCHAR STLIMIT STCOUNT STNO ANCHOR TRIM FULLSCAN CASE MAXLNGTH FTRACE TRACE ERRLIMIT CODE FNCLEVEL RTNTYPE ALPHABET ABEND DUMP STEXEC ERRTYPE ERRTEXT GTRACE FATALLIMIT PARM PI` — so `gva_index_of` returns -1 and the by-name arm emits. Icon lets you declare any of those as a global.
- **(b) `g_gva_active == 0`**, reachable in m3 with `SCRIP_M3_GVA=0` and on the m3 arena-allocation failure path (`scrip.c:1686`).

Both doors were opened by execution, not by reading. Door (a): `global PI` + `PI <- y` emits `call NV_GET_fn` / `call NV_SET_fn` in the rev-assign box — confirmed in the emitted `.s`.

## Through either door the answer is wrong, and it is wrong before `<-` runs

| program | oracle (icont/iconx) | SCRIP m3 |
|---|---|---|
| `global PI` · `PI := 10` · `write(image(PI))` | `PI=10` then `PI=15` | `PI=""` then `PI=""` |
| same program, `PI` renamed `gp` (control arm) | `gp=10` then `gp=15` | `gp=10` then `gp=15` — **correct** |
| `global gp` · plain assign, `SCRIP_M3_GVA=0` (door b) | `gp=10` then `gp=15` | `gp=""` then `gp=""` |

Six ineligible names were tried (`PI ALPHABET DUMP PARM ABEND STEXEC`) and all six behave identically. The control arm is the load-bearing half: **rename the global and the identical program is correct**, so this is the name's GVA-eligibility and nothing else.

⭐ **The defect is not in reversible assignment at all.** A plain `PI := 10` is already dead — the store goes nowhere and every read yields `""`. `<-` was merely the construct that led here. The by-name global path for **Icon** is broken across the board, for every construct that uses it.

## Why this settles the design question CEO-471 asked

hq_P's own earlier proposal was `rsw_kind 2` with `rsw_get`/`rsw_set` *following `bb_rev_assign_global`*, which carries a GVA fast path AND a by-name path. Copying that by-name path into `<->` would have copied a path that has never once produced a correct answer, and it would have doubled combinatorially while doing it (lhs and rhs each independently local, global or keyword). **The ceo's ruled alternative — the `NV_PTR_fn` pointer shape — is the right cut**, and this measurement is the reason rather than the taste.

## Exposure: zero today, which is why nobody has seen it

`grep -rlE "^ *global +(<the 29>)" --include=*.icn corpus/` → **0 files**. Door (a) is a latent trap, not a live red; door (b) needs an env var. ⛔ That is exactly why it survived: **a wrong-answer path with no corpus witness is invisible to every board we run**, and it was reached here only by a probe minted to ask a different question.

## The shape worth inheriting

⭐ **A SNOBOL4 keyword list is being applied to Icon names.** `gva_name_eligible`'s 29 exclusions are SNOBOL4 keywords (`&TRIM`, `&ANCHOR`, `&MAXLNGTH`…). In SNOBOL4 they are language-owned names that must not be GVA-cached. In Icon they are ordinary identifiers a user may declare with `global`. This is the *language identity stops at lower* rule (`CLAUDE.md` § Architecture, gate `test_gate_emit_no_lang.sh`) failing in the one direction that gate cannot see: not a `LANG_*` enum downstream, but a **name set** from one language silently governing another. A per-name list is the per-op filter wearing a different hat.

⛔ **NOT CURED BY THIS ROW, AND NOT MINE TO CURE SILENTLY.** The cure is a frontend-scoped eligibility question (does this name belong to *this* program's language?) and it reaches every construct, not `<->`. Named here for the ceo to route. This row cures `<->` on globals in the `NV_PTR_fn` shape and makes the `NV_PTR_fn`-returns-NULL case refuse loudly instead of exchanging &null with nothing.
