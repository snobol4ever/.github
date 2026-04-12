# GOAL-NO-SYMLINKS — Remove symlinks from all shell scripts

**Repo:** corpus, harness, snobol4dotnet, one4all (any repo with shell scripts)
**Done when:** No shell script, Makefile, or CI file in any repo creates symlinks via `ln -s`.

## Why

Session 4 of BEAUTY-19 revealed that corpus commit `fbab26b` used `ln -s` to resolve
a deduplication — creating symlinks from `beauty/` into `demo/inc/` which was then deleted.
The result: 18 broken symlinks that silently killed the entire beauty suite (0/18).
Symlinks break when targets move or are deleted. Real files do not.

## Rule

See RULES.md: "No symlinks in shell scripts."

## Steps

- [ ] **S-1** — Audit all shell scripts in corpus for `ln -s` usage. Replace with `cp` or
      direct path references. Gate: `grep -r "ln -s" corpus/` returns nothing.

- [ ] **S-2** — Audit all shell scripts in harness for `ln -s` usage. Replace with `cp` or
      direct path references. Gate: `grep -r "ln -s" harness/` returns nothing.

- [ ] **S-3** — Audit all shell scripts in snobol4dotnet for `ln -s` usage.
      Gate: `grep -r "ln -s" snobol4dotnet/` returns nothing.

- [ ] **S-4** — Audit one4all and any other active repos.
      Gate: clean grep across all repos.

- [ ] **S-5** — Verify no symlinks exist anywhere in corpus source tree.
      Gate: `find corpus/ -type l` returns nothing (or only intentional non-source symlinks,
      documented here explicitly).
