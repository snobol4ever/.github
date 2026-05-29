# HANDOFF 2026-05-28 — Opus 4.7 — PROLOG-BB: SWI-2-pre findall determinism guard

**Repos:** one4all `cda40a70` · .github (this commit) · corpus untouched.

---

## What landed this session

### `cda40a70` — SWI-2-pre: findall determinism guard

Four-line addition in `src/lower/bb_exec.c` findall loop:

```c
while (!IS_FAIL_fn(res) && fa_safety-- > 0) {
    if (nacc >= 4096) break;
    acc[nacc++] = bb_copy_term(pl_node_to_term(fs->tmpl));
    /* SWI-2a: determinism guard — mirrors BB_PL_CALL line 3340. A deterministic goal */
    /* body holds no live inner choice point after first success; resuming would re-fire */
    /* it from entry and loop. Stops findall(N, det_goal(N), _) returning N copies of N. */
    if (!bb_body_has_live_choice(fs->gcfg)) break;
    res = bb_exec_resume(fs->gcfg);
}
```

Mirrors the BB_PL_CALL discipline at line 3340 which already had this fix for the
prior `findall(X, fact(X), _)` infinite-loop class. Closes handoff bug (C) from
`HANDOFF-2026-05-28-SONNET-PROLOG-BB-SWI-1A-LANDED.md`.

### Verification

| Input | Pre-patch | Post-patch |
|---|---|---|
| `findall(X, fact(only_one), L)` — single fact | re-fired forever / safety bound | `[only_one]` |
| `findall(C, color(C), L)` — 3 facts (non-det) | `[red,green,blue]` | `[red,green,blue]` (unchanged) |
| `findall(X, det_clause_with_body(X), L)` | thousands of copies | terminates (separate issue: body returns 0 — see below) |

The guard is precise: it fires only when `bb_body_has_live_choice()` returns false,
i.e. the goal body has no `BB_PL_CALL`/`BB_CHOICE`/`BB_PL_ALT` node in `state>0`.
Non-deterministic goals are unaffected.

### Gates at HEAD `cda40a70` — all byte-identical to `86abe166`

| Gate | Mode-2 | Mode-3 | Mode-4 |
|---|---|---|---|
| GATE-1 smoke | 5/5 ✅ | 5/5 ✅ | 5/5 ✅ |
| GATE-2 crosscheck | 132/0 ✅ | (part of G2) | n/a |
| GATE-3 rung suite | **104/107** | **104/107** | **54/107** |
| GATE-4 mode-4 minimal | 4/4 ✅ | n/a | 4/4 ✅ |
| GATE-SWI plunit | 0/57 | 0/57 | n/a |
| FACT grep | 0 ✅ | — | — |

---

## Adjacent finding (not addressed this session)

While verifying the guard, an *independent* deterministic-body bug surfaced:

```prolog
tc(memberchk) :- memberchk(y, [a,b,y,c]).
?- findall(N, tc(N), L).      % returns [] — should return [memberchk]
```

A bare fact `tc(memberchk).` correctly returns `[memberchk]`. The body `:- memberchk(...)`
on a single-clause predicate causes the findall snapshot to capture `tc/1` *after* the
clause body has succeeded but apparently before the head argument binding is committed
to the snapshot env — or the snapshot is reading `N` from the outer env where it's
still unbound. This is **not** the guard bug; it's the original SWI-2 bug (B) the handoff
identified — `call(Goal)`/single-clause-with-body via findall template env aliasing.

This unblocks the **SWI-2b approach**: rewrite `plunit.pl` to use `clause(test(N,O), G)`
enumeration which sidesteps the body-in-template-snapshot interaction entirely. That is
the next session's work.

---

## Next session entry point

**SWI-2a (proper):** implement `clause/2` mode-2 in `bb_exec.c`. Walk `pl_bb_table` for the
functor, enumerate clause bodies by walking `zc->bodies[]`, materialise head unification
plus body as term. Gate: `clause(append([],L,L), true)` succeeds; `clause(append([H|T],L,[H|R]), Body)`
returns the body term.

**SWI-2b:** Update `plunit.pl` `pj_run_suite` to use `clause(test(N,O), G)` enumeration
instead of `pj_test/4`. Add `test/1` normaliser. Bypasses bugs A and B from the SWI-1a
handoff. Target: `test_list` PASS memberchk mode-2 and mode-3.

The four-step recipe in `HANDOFF-2026-05-28-SONNET-PROLOG-BB-SWI-1A-LANDED.md` lines
"Recommended next session approach" stays valid; Step 1 (this commit) is done, Steps 2–4
remain.

---

## Commit identity

```bash
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```
