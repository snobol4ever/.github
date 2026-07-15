# FINDING-2026-07-14-CLAUDE-PL-ISO-10-COVERAGE-TRUTH-AND-TWO-SILENT-FAILURES.md

**Session:** s56 · Claude Opus 4.8 · 2026-07-14 · goal `GOAL-PROLOG-BB.md` LADDER A (PL-100)
**Landed:** PL-ISO-10 (coverage audit + tracker), PL-ISO-12 partial (`between/3`, `for/3`)
**Board:** rung 138/138 ×3 · crosscheck 150/0/13 ORACLE_MISS=0 · no-new-global EXIT=0 (floor 14) · no-value-stack PASS

---

## 1. The headline: the "~65–70% of GNU Prolog" baseline is not reproducible

`GOAL-PROLOG-BB.md` PL-100 asserts a measured baseline of *"~70% of ISO Part 1 core, ~65–70% of GNU
Prolog's surface"*. Measured mechanically against gprolog 1.4.5's real export surface, **SCRIP admits 38 of
312 (12%)**.

The old number is not wrong so much as it measured a different, narrower thing (a hand-picked ISO subset).
The new number is reproducible on demand and re-derives itself from live code:

```bash
bash scripts/audit_prolog_iso_coverage.sh          # regenerate .github/PROLOG-ISO-TRACKER.md
bash scripts/audit_prolog_iso_coverage.sh --check  # gate: exit 1 if UNASSIGNED != 0
```

**Why the audit can be trusted over prose:** both sides are extracted from source, never hand-listed.
gprolog self-declares every exported builtin as `set_bip_name(Name, Arity)` in `refs/gprolog-master/src/
BipsPl/*.pl` (`'$'`-prefixed names are internal choice-point helpers and are excluded). SCRIP's admitted set
is read from the four real admission sites — `rt_pl_det_builtin_target` (det tab), `pl_ensure_gen_builtin_pred`
(GEN rail), `lower_prolog.c` `goal()` strcmp arms, `prolog_lower.c` `pb_expand_goal` arms. The property that
proves it is live: landing `between/3` + `for/3` moved DONE 36 → 38 **with zero edits to the audit script**.

### Where the gap actually is (this is the useful part)

| family | exports | done | note |
|--------|---------|------|------|
| stream I/O (`stream` 43 + `const_io` 30 + `char_io` 28 + `src_rdr` 22 + `dec10io` 12) | **135** | 0 | **43% of gprolog's entire surface is ONE family**, all owned by PL-ISO-7b — which is parked behind an open sanctioned-global question |
| gprolog extensions (`os_interf` 35, `debugger` 11, `sockets` 8, `stat` 6, `file` 6, `random` 4, `le_interf` 4) | **74** | 1 | **SCOPE DECISION FOR LON** — see §4 |
| `read` 17 / `atom` 15 / `write` 12 / `term_inl` 11 | 55 | 17 | ordinary rung work (PL-ISO-4/7a/9/11) |

Two thirds of the headline gap is therefore *one blocked design question plus one scoping question*, not 274
independent pieces of work. That reframing is the point of the rung.

---

## 2. ⭐ Silent failure #1 — a statically-lowered call to an unknown predicate does not throw

**This is the highest-value open bug for "all source programs working properly", and it is why coverage gaps
are invisible.**

| probe | gprolog 1.4.5 | SCRIP |
|-------|---------------|-------|
| `catch(no_such_pred_xyz(1), E, ...)` — literal goal | `error(existence_error(procedure,no_such_pred_xyz/1),main/0)` | **nothing. rc=0. `catch/3` catches nothing.** |
| `G = no_such_dyn_xyz(1), catch(call(G), E, ...)` — via bridge | `error(existence_error(procedure,no_such_dyn_xyz/1),main/0)` | `error(existence_error(procedure,no_such_dyn_xyz/1),_G-1)` ✅ |

So **PL-ISO-1 only half-landed**: the runtime bridge throws correctly, the statically-lowered call path does
not. The consequence is severe and quiet: *every missing builtin manifests as a wrong answer rather than an
error*. `between/3` was missing for the entire life of the project and the only symptom was a program that
printed nothing and exited 0 — which is indistinguishable from ordinary Prolog failure.

Note the secondary divergence in the working row: the error **context** argument is `_G-1` where gprolog has
`main/0`. An unbound context var is ISO-legal, so this is a *printer* bug, not a semantics bug — `-1` is an
unassigned slot id leaking into the writer, exactly as PL-ISO-5 already flags ("STILL OPEN"). It affects every
error term, not just this one. Rung tests should therefore assert on the **formal** (`catch(G, error(F,_), …)`)
and not bake the broken context into an `.expected`.

**Recommended fix order:** do this BEFORE any further coverage rung. It converts every remaining gap from a
silent wrong answer into a loud, greppable error, which makes the rest of LADDER A mechanical.

---

## 3. ⭐ Silent failure #2 — the whole GEN family is invisible to the `$call` bridge for VAR goals (filed as PL-ISO-14)

Reproducer:

```prolog
:- initialization(main).
e(G) :- catch(G, error(F,_), (write(caught(F)), nl)).
main :- e(sub_atom(abc,0,1,_,_)), write(done), nl.
```

* gprolog → `done`
* SCRIP → `caught(existence_error(procedure,sub_atom/5))` then `done`

**Pre-existing, NOT introduced by s56** — verified by running the identical probe against `sub_atom/5`, the
oldest GEN-rail citizen, and again on a pristine tree with s56's diff stashed.

**Root cause (structural, worth stating precisely):** `pl_ensure_gen_builtin_pred` mints the synthetic wrapper
pred at **LOWER time, only when the lowerer sees the goal syntactically**. When the goal arrives as a variable
it reaches the `$call` runtime bridge, which resolves through the proc table (registered preds) and
`rt_pl_det_builtin_target` (det builtins) — and a GEN builtin is in neither unless the lowerer happened to
register it. The bridge cannot fix this itself: minting a new BB pred at runtime is forbidden in modes 3/4
(NO AST/IR DURING MODE-3/4 EXECUTION).

Therefore **the fix must be a LOWER-time decision.** Two candidates:

1. **Ensure-with-the-bridge (preferred).** `pl_ensure_call_bridge` firing is exactly the signal that var-goals
   are possible; have it also ensure the ~7 GEN builtin preds. The bridge's existing `PLCK_PRED` arm then
   resolves them through the proc table like any user generator — no new mechanism at all. Bounded cost, and
   it only pays when a program actually uses `call/N`.
2. **Shared `rt_pl_gen_builtin_target(nm, ar)`** mirroring `rt_pl_det_builtin_target` (NO-DUP: ONE table,
   serves every GEN builtin forever). Cleaner conceptually, but the bridge still needs a staged-gen driver arm.

Affected today: `sub_atom/5`, `clause/2`, `current_predicate/1`, `predicate_property/2`, `current_op/3`,
`between/3`, `for/3` — and any program of the shape `maplist(between(1,3), L)`.

---

## 4. Scope question that only Lon can answer

PL-ISO-10's own text defines the target as *"the tracker's DONE column equals gprolog's export list"*. Read
literally, that obliges SCRIP to implement `sockets.pl` (8), `le_interf.pl` (linedit, 4), `debugger.pl` (11)
and `os_interf.pl` (35) — 74 predicates that are gprolog **extensions**, not language constructs, and that
have nothing to do with Byrd boxes or ISO Prolog.

The tracker does not decide this. It marks them `scope=gprolog-ext`, homes them under `PL-EXT`, and reports
`core-open` separately from `UNASSIGNED` so the number moves honestly either way. **Ask:** is PL-100's "100%"
(a) gprolog's full 312, (b) the 238 core rows, or (c) ISO Part 1 only? The answer changes the finish line by
~30% and should be written into the rung before anyone measures progress against it.

---

## 5. What landed (`between/3` / `for/3`, PL-ISO-12 partial)

Canonical semantics read from source before writing a line (`RULES.md` CONSULT CANONICAL SOURCES):
`control.pl` → `Pl_Between_3` in `control_c.c`:

```
between(L,U,X): L,U integer-checked; X bound → test L =< X =< U;
                X unbound → L>U fail; L<U push choice point (L+1..U); bind X=L, succeed
for(X,L,U)    → deprecated alias, args swapped → between(L,U,X)
```

* **Runtime** (`by_name_dispatch.c`): `plc_between_t` iterator + `rt_pl_between_gen` on the GEN rail, copying
  the `rt_pl_sub_atom_gen` shape exactly (per-activation `rt_ws_alloc` state in `*resume`, trail mark,
  `pl_trail_unwind` + `plw_zh_kill_to` per candidate). New `rt_pl_iso_throw_type(type, culprit)` helper for
  `type_error(Type, Culprit)` with an arbitrary-term culprit (existing `rt_pl_iso_throw_pi` only builds the
  `Name/Arity` shape). `$for` reuses the SAME generator with permuted args — NO-DUP, one implementation.
* **Lowering** (`lower_prolog.c`): two `pl_ensure_gen_builtin_pred` arms beside `sub_atom`.
* **Zero new globals** — the iterator is per-activation `rt_ws_alloc`, so the ratchet held at floor 14 by
  construction.

**⚠ The bug worth remembering:** the first cut checked only `DT_PLVAR` for "unbound X". A fresh frame cell can
also present as `DT_SNUL`/`DT_FAIL` — `sub_atom` has always checked all three. The narrow check sent fresh
vars down the *bound* branch, which threw `instantiation_error` and made `between(1,3,X)` fail silently while
`findall(X, between(1,3,X), L)` still returned `[1,2,3]` (findall's cell was already materialised). Symptom
split by call path; cause was one missing tag. `plc_is_unbound()` now encodes that notion once.

**Tests:** `corpus/programs/prolog/rung50_{between_enum,between_test,between_errors,for_alias}.pl` — every
`.expected` generated from the **gprolog oracle**, not from SCRIP's own output. `scripts/test_prolog_rung_suite.sh`
glob extended `rung4[0-9]` → also `rung5[0-9]` (rung50+ was being silently skipped; any future rung50+ would
have been invisible).

**Oracle note:** the enum test originally used `aggregate_all/3`, which gprolog rejects (it is SWI-only). The
oracle caught it immediately — a small proof that anchoring `.expected` to gprolog rather than to SCRIP is
doing real work.

---

## 6. Session setup that is NOT in the repo and must be redone every session

`refs/` is gitignored and was **absent** on a fresh clone (as RULES.md warns). No gprolog/swipl archives were
uploaded this session, so per CONSULT CANONICAL SOURCES the upstream was cloned instead:

```bash
git clone --depth 1 https://github.com/didoudiaz/gprolog.git /home/claude/SCRIP/refs/gprolog-master
apt-get update && apt-get install -y gprolog     # 1.4.5 — the exact version the goal file names as oracle
```

`audit_prolog_iso_coverage.sh` fails loudly with these instructions if `refs/` is missing, rather than
silently reporting a wrong number.

---

## 7. Correction to the record

The s55 LIVE CURSOR named SCRIP HEAD `05449bbe`; actual HEAD at s56 start was `a15b82ad` (parallel sessions had
landed CAS-1 and ZS-3b in between). Nothing was wrong — this is the documented 3–4-parallel-session concurrency
— but it confirms the stale-orientation FACT RULE: **trust `git log`, never a hash written into prose.**

Likewise `snocone crosscheck PASS=4 FAIL=4` is **pre-existing** (proven by stashing s56's diff and rebuilding
pristine), despite older board notes claiming "snocone 5/5". Flagged here so the next session does not
mistake it for s56 breakage — it belongs to whoever owns Snocone.
