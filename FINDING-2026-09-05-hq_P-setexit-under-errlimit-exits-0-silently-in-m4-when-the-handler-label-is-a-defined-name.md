# FINDING 2026-09-05 hq_P — in mode 4, SETEXIT under `&ERRLIMIT` exits 0 with zero output when the handler label is also a DEFINE'd name

**Measured:** hq_P, 2026-09-05, SCRIP `94f894b80`, incremental `make`, both modes.
**Row:** `setexit-not-invoked-under-errlimit-survival` (rank 1, ASSIGNED:hq_P — REOPENED by ceo 10:52 after
the audit on hq_P's own 09-04 landing).

## 1. What the 09-04 cure missed, and why its gate could not see it

The 09-04 landing (`SCRIP 1840c6846`) is not wrong — its gate
`test_gate_sno_setexit_resume_matches_oracle.sh` and both master witnesses still pass in both modes today.
It is **blind to one composition**: SETEXIT armed under a nonzero `&ERRLIMIT` where the handler label is
also a DEFINE'd function name. In that shape **mode 4 prints nothing at all and exits 0**, while mode 3
prints the full, correct answer.

    m3:  CAUGHT 5 | next | CAUGHT 38 | done 2       (4 lines, rc=0)
    m4:  <zero bytes, rc=0>

⛔ rc=0 and an empty stream is the worst available shape: no diagnostic, no signal, and every wrapper that
greps output rather than comparing it reads it as "nothing to report".

## 2. Minimal pair — one ingredient apart

Both programs arm SETEXIT under `&ERRLIMIT = 1000`, trap one error, and resume with `:(CONTINUE)`.

| witness | handler label `H` is… | m3 | m4 | `LBL__H` in the `.s` |
|---|---|---|---|---|
| `k_bare` | a **bare statement label** | `caught\|after\|fin` | `caught\|after\|fin` ✅ | 4 |
| `l_alsogoto` | a **DEFINE'd function name** | `caught\|after` | *(empty)* ⛔ | **0** |

The two differ in exactly one ingredient. It is **not** the keyword, not statement tracking, and not
SETEXIT itself — `g_noerr` (SETEXIT armed, no error) is correct in both modes.

## 3. The mechanism, end to end

1. `scrip.c:1404` suppresses the `LBL__<name>` alias when that landing node is already a DEFINE's dentry
   target: `if (bbg->dentry_entry[_dq] == _bn) { _dl = 1; break; } if (_dl) continue;`
   The DEFINE registration and the label alias are treated as mutually exclusive — but they serve
   **different consumers**: the define site (a call) and `rt_goto_transfer` (a by-name goto).
2. `rt_goto_resolve` (`runtime_eval.c:330`) therefore finds neither `rt_label_get_fn("H")` nor
   `rt_proc_get_fn("LBL__H")`, and returns NULL.
3. `rt_goto_transfer` (`runtime_eval.c:366`) is `{ void *fn = rt_goto_resolve(name); if (fn) rt_chain_enter(...); }`
   — **it cannot report failure and silently returns.**
4. `core_runtime_error` (`core.c:2156`) treats that return as "the handler ran and did not come back"
   and calls `exit(0)`.

⭐ **The load-bearing defect is step 3→4: a function that cannot express failure, called by a site that
interprets its only possible return as success.** Step 1 is the trigger, but this composition would be a
silent exit for *any* unresolvable handler label.

## 4. Two cure candidates measured and ELIMINATED — both reverted, tree clean

Recorded so the next attempt does not re-spend them. Each was built and run, then reverted, and the
revert proven by control arm (the defect reproduces again at baseline, `git status` clean).

- **(a) Un-suppress the alias** (drop the dentry skip at `scrip.c:1404`, behind a killswitch).
  **NECESSARY BUT NOT SUFFICIENT.** `LBL__H` is then emitted (0 → 3-4 occurrences) and the program is
  **still silent**. So an emitted asm label is not what `rt_goto_resolve` reads — the by-name path needs a
  runtime *registration*, not a symbol. Anyone who fixes only the emission will believe they have the cure
  until they run it.
- **(b) Guard the trap arm on resolvability** (`rt_goto_resolve(_setexit_label)` non-NULL) and replace the
  `exit(0)` with a loud refusal. **Turns the silence into an `ERROR 246 -- stack overflow`**: falling
  through to the plain `&ERRLIMIT` survival arm makes the failed statement re-raise without bound. So the
  survival arm cannot absorb this composition either, and the fix is not "skip the trap when unreachable".

⛔ Neither was landed. The real cure has to make the by-name transfer *resolve* in m4 — register the
DEFINE entry's landing under `LBL__<name>` as well as under the function name — and only then is the
`exit(0)` unreachable rather than merely guarded.

## 5. Landed this sitting

The row's DONE-WHEN now carries the m4 composition arm, proven both ways: **rc=1** today (the two
pre-existing witness arms still PASS, the new arm FAILs, so the criterion is red for exactly the reason
the row names) and **rc=2** when it cannot measure (no witness, or the m4 build fails). The arm had to be
inserted *before* the criterion's closing `exit $rc` — appended after it, it was dead code that reported
green, which is the same false-green shape as a `.PHONY` target with no recipe, and it did report green
once before being caught.
