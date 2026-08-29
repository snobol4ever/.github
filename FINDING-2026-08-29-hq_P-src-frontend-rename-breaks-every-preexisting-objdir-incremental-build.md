# FINDING — the `src/frontend` → `src/parsers` rename (`96665b70`) hard-fails the INCREMENTAL build in
# every objdir that predates it, with an error naming a path that no longer exists. Self-curing via
# `make pristine`, but the message points at the repo rather than at the stale objdir.

**hq_P · 2026-08-29 · observed while setting up row `tests-consolidate-prolog`; not that row's lane.**

## What happens

Pull across `96665b70` ("Rename src/frontend -> src/parsers"), then run a plain `make` in a checkout that
was built before it:

```
make: *** No rule to make target '/home/claude_P/SCRIP/src/frontend/snobol4/snobol4.tab.c',
      needed by 'out/rt_pic-f65f143e2f/snobol4.tab.o'.  Stop.
```

**Cause: the objdir's auto-generated `.d` dependency files still name the old directory.** Measured in
this root: **26** `.d` files under `out/rt_pic-f65f143e2f/` contain `src/frontend`. `make` reads them
before it can rebuild anything, so it fails on a path the working tree no longer has — while the tree
itself is perfectly correct and fully pulled.

## Why it survived the rename commit

The rename's own message records: *"Build verified in the break-value repair commit that follows
(pristine)."* A pristine build wipes the objdir, so it **cannot** exercise this path. The rename is not
wrong; the verification simply could not see this failure mode. ⭐ Same shape as the `make test`
false-green already recorded in `CLAUDE.md`: **the check that would have caught it was structurally
incapable of failing on it.**

## Impact and cure

Cure is one command — `make pristine` (~1m40 at `RT_OPT=-O0`) — and afterwards the problem never recurs
in that checkout. So this is a papercut, not a blocker. It is worth writing down only because of **what
the error says**: it names a missing source file in `src/`, which reads as *"the repo is broken / my pull
is half-applied"* rather than *"your objdir is stale"*. A seat that trusts the message goes looking in
git for a file nobody deleted incorrectly.

⚠️ Note the counter-pressure: `CLAUDE.md` currently tells seats that `S_ARTIFACT_PRISTINE=1` is dangerous
and that the banner path now defaults to `--skip-pristine` (to stop the Stop-hook from wiping live
builds). Both are right; they just mean the one situation that *needs* a manual pristine is also the one
where seats have been trained not to reach for it. **If you pulled across `96665b70` and `make` names a
`src/frontend/...` file, run `make pristine` once — it is the correct response, not the dangerous one.**

## Generality

The objdir is per-checkout by construction (`OBJ ?= /tmp/si_objs$(subst /,-,$(ROOT))`), so this fires
**once per checkout that existed before the rename**, independently in every seat root — i.e. it is
scheduled to be rediscovered up to ~19 times unless it is written down. Any future `git mv` of a
directory under `src/` has exactly this property.

- Trees: SCRIP `7e7bffcb` (post-rename), `.github` `85dafb69`. Cured here by `make pristine`, rc=0.
