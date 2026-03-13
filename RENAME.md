# RENAME.md — SNOBOL4-plus → snobol4ever

One-time rename execution plan. Eight phases, strict order. Do not reorder — sequencing is load-bearing.

---

## Locked Naming Rules

| context | format | example |
|---------|--------|---------|
| marketing name | no dashes, all lowercase | `snobol4jvm` |
| github repo slug | one dash separator, all lowercase | `snobol4-jvm` |
| cli command | `sno4` prefix, no dashes | `sno4jvm` |
| package manager | all lowercase, no dashes | `snobol4jvm` |
| the language itself | ALL CAPS, unchanged | `SNOBOL4` (technical/historical refs only) |

---

## Complete Name Grid

| product | marketing | repo | cli | package mgr | namespace |
|---------|-----------|------|-----|-------------|-----------|
| **ORG** | | | | | |
| organization | `snobol4ever` | `github.com/snobol4ever` | — | — | — |
| **COMPILERS** | | | | | |
| native kernel | `snobol4all` | `snobol4-all` | `sno4all` | — | `snobol4all.c` / `snoc` (internal) |
| jvm backend | `snobol4jvm` | `snobol4-jvm` | `sno4jvm` | Maven: `snobol4/jvm` | `snobol4.jvm` |
| .net backend | `snobol4dotnet` | `snobol4-dotnet` | `sno4net` | NuGet: `snobol4dotnet` | `Snobol4.Dotnet` ¹ |
| **PATTERN LIBRARIES** | | | | | |
| python | `snobol4python` | `snobol4-python` | — | PyPI: `snobol4python` | `import snobol4python` |
| c# | `snobol4csharp` | `snobol4-csharp` | — | NuGet: `snobol4csharp` | `Snobol4.CSharp` ¹ |
| **INFRASTRUCTURE** | | | | | |
| test corpus | `snobol4corpus` | `snobol4-corpus` | — | — | — |
| test harness | `snobol4harness` | `snobol4-harness` | — | — | — |
| **EXPERIMENTAL** | | | | | |
| cpython ext | `snobol4artifact` | `snobol4-artifact` | — | PyPI: `snobol4artifact` | `import snobol4artifact` |

¹ C# namespaces follow PascalCase by platform convention — the one intentional exception to the all-lowercase rule.

---

## Phase 1 — Text edits in `.github` repo

Edit all `.md` files. **Do not push yet.**

### URL substitutions

| find | replace |
|------|---------|
| `github.com/SNOBOL4-plus/SNOBOL4-tiny` | `github.com/snobol4ever/snobol4-all` |
| `github.com/SNOBOL4-plus/SNOBOL4-jvm` | `github.com/snobol4ever/snobol4-jvm` |
| `github.com/SNOBOL4-plus/SNOBOL4-dotnet` | `github.com/snobol4ever/snobol4-dotnet` |
| `github.com/SNOBOL4-plus/SNOBOL4-corpus` | `github.com/snobol4ever/snobol4-corpus` |
| `github.com/SNOBOL4-plus/SNOBOL4-harness` | `github.com/snobol4ever/snobol4-harness` |
| `github.com/SNOBOL4-plus/SNOBOL4-python` | `github.com/snobol4ever/snobol4-python` |
| `github.com/SNOBOL4-plus/SNOBOL4-cpython` | `github.com/snobol4ever/snobol4-artifact` |
| `github.com/SNOBOL4-plus/SNOBOL4-csharp` | `github.com/snobol4ever/snobol4-csharp` |
| `github.com/SNOBOL4-plus/.github` | `github.com/snobol4ever/.github` |

### Brand text substitutions

| find | replace |
|------|---------|
| `SNOBOL4ever` | `snobol4ever` |
| `SNOBOL4now` | `snobol4now` |
| `SNOBOL4everywhere` | `snobol4everywhere` |
| `SNOBOL4-tiny` (repo refs) | `snobol4-all` |
| `SNOBOL4-jvm` (repo refs) | `snobol4-jvm` |
| `SNOBOL4-dotnet` (repo refs) | `snobol4-dotnet` |
| `SNOBOL4-corpus` (repo refs) | `snobol4-corpus` |
| `SNOBOL4-cpython` (repo refs) | `snobol4-artifact` |
| `SNOBOL4-python` (repo refs) | `snobol4-python` |
| `SNOBOL4-csharp` (repo refs) | `snobol4-csharp` |
| `SNOBOL4-plus` (org refs) | `snobol4ever` |

### Files to touch

`README.md` · `PLAN.md` · `SESSION.md` · `TINY.md` · `JVM.md` · `DOTNET.md` · `CORPUS.md` · `HARNESS.md` · `STATUS.md` · `MISC.md` · `PATCHES.md` · `profile/README.md`

### SESSIONS_ARCHIVE.md — special handling

Append-only. Do not find/replace. Add one line at the very top only:

```
> Org renamed SNOBOL4-plus → snobol4ever, March 2026. Historical entries use old names.
```

---

## Phase 2 — Commit (do not push yet)

```bash
git add -A
git commit -m "rename: SNOBOL4-plus -> snobol4ever, brand casing, naming rules"
```

---

## Phase 3 — Rename the GitHub org

GitHub Settings → Organization → Rename:

`SNOBOL4-plus` → `snobol4ever`

GitHub creates redirects from all old URLs automatically.

---

## Phase 4 — Rename each GitHub repo

Settings → General → Repository name, one at a time:

| from | to |
|------|----|
| `SNOBOL4-tiny` | `snobol4-all` |
| `SNOBOL4-jvm` | `snobol4-jvm` |
| `SNOBOL4-dotnet` | `snobol4-dotnet` |
| `SNOBOL4-corpus` | `snobol4-corpus` |
| `SNOBOL4-harness` | `snobol4-harness` |
| `SNOBOL4-python` | `snobol4-python` |
| `SNOBOL4-cpython` | `snobol4-artifact` |
| `SNOBOL4-csharp` | `snobol4-csharp` |
| `.github` | `.github` (unchanged — GitHub requires this name) |

---

## Phase 5 — Update all local git remotes

Run in each cloned repo on every machine:

```bash
git remote set-url origin https://github.com/snobol4ever/snobol4-all
git remote set-url origin https://github.com/snobol4ever/snobol4-jvm
git remote set-url origin https://github.com/snobol4ever/snobol4-dotnet
git remote set-url origin https://github.com/snobol4ever/snobol4-corpus
git remote set-url origin https://github.com/snobol4ever/snobol4-harness
git remote set-url origin https://github.com/snobol4ever/snobol4-python
git remote set-url origin https://github.com/snobol4ever/snobol4-artifact
git remote set-url origin https://github.com/snobol4ever/snobol4-csharp
git remote set-url origin https://github.com/snobol4ever/.github
```

---

## Phase 6 — Push `.github`

```bash
git push
git log --oneline -1
```

---

## Phase 7 — Source code and comments in each repo

For each repo, audit and update:
- Comments referencing `SNOBOL4-plus` org name
- Hardcoded GitHub URLs in source files
- `README.md`, `INSTALL.md`, `CONTRIBUTING.md` in each repo root
- CI/CD config (`.github/workflows`) referencing old org or repo names

**`snobol4-all` internal note:** `snoc` stays as the internal compiler binary name. `sno4all` is the user-facing command. Do not rename `snoc`.

Commit each repo:
```bash
git commit -m "rename: org SNOBOL4-plus -> snobol4ever, brand casing update"
```

**PyPI — `snobol4artifact`:** If `SNOBOL4-cpython` is published on PyPI under the old name, publish a new `snobol4artifact` package and add a deprecation notice to the old one. PyPI does not support renames.

**NuGet — namespace convention:** Coordinate with Jeffrey. Package name is `snobol4dotnet` (lowercase) but namespace is `Snobol4.Dotnet` — intentional PascalCase exception for C# convention.

---

## Phase 8 — Verify

```bash
grep -ri "SNOBOL4-plus" . --include="*.md"   # expect: empty
grep -ri "SNOBOL4-plus" . --include="*.c"    # expect: empty
grep -ri "SNOBOL4-plus" . --include="*.clj"  # expect: empty
grep -ri "SNOBOL4-plus" . --include="*.cs"   # expect: empty
```

Check redirects (GitHub grace period is generous but not infinite):
```bash
curl -I https://github.com/SNOBOL4-plus/SNOBOL4-tiny
# expect: 301 Moved Permanently → github.com/snobol4ever/snobol4-all
```

---

## Open Items

| item | question | owner |
|------|----------|-------|
| `snoc` vs `sno4all` | `snoc` = internal build tool, `sno4all` = user command. Confirm. | Lon |
| `snobol4-all` vs `snobol4-tiny` | `tiny` (Ant-Man: small source, small binary, universe-level power) vs `all` (does everything). Both are true. Decide before executing Phase 4. Affects all cells in name grid for native kernel row. | Lon |
| PyPI `snobol4artifact` | Is SNOBOL4-cpython currently on PyPI? If yes, new package needed. | Lon |
| NuGet casing | `Snobol4.Dotnet` namespace — coordinate on C# convention exception. | Jeffrey |
| `SESSIONS_ARCHIVE.md` | Header note only. Do not rewrite history. | Lon |
