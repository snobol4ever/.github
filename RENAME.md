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
| native kernel | `snobol4x` | `snobol4x` | `sno4x` | — | `snobol4x.c` / `snoc` (internal) |
| jvm backend | `snobol4jvm` | `snobol4-jvm` | `sno4jvm` | Maven: `snobol4/jvm` | `snobol4.jvm` |
| .net backend | `snobol4net` *(pending rename from `snobol4dotnet` — see M-G9)* | `snobol4-net` | `sno4net` | NuGet: `snobol4net` | `Snobol4.Net` ¹ |
| **PATTERN LIBRARIES** | | | | | |
| python | `snobol4python` | `snobol4-python` | — | PyPI: `snobol4python` | `import snobol4python` |
| c# | `snobol4csharp` | `snobol4-csharp` | — | NuGet: `snobol4csharp` | `Snobol4.CSharp` ¹ |
| **INFRASTRUCTURE** | | | | | |
| test corpus | `corpus` | `snobol4-corpus` | — | — | — |
| test harness | `harness` | `snobol4-harness` | — | — | — |
| **EXPERIMENTAL** | | | | | |
| cpython ext | `snobol4artifact` | `snobol4-artifact` | — | PyPI: `snobol4artifact` | `import snobol4artifact` |

¹ C# namespaces follow PascalCase by platform convention — the one intentional exception to the all-lowercase rule.

---

## Phase 1 — Text edits in `.github` repo

Edit all `.md` files. **Do not push yet.**

### URL substitutions

| find | replace |
|------|---------|
| `github.com/SNOBOL4-plus/SNOBOL4-tiny` | `github.com/snobol4ever/snobol4x` |
| `github.com/SNOBOL4-plus/SNOBOL4-jvm` | `github.com/snobol4ever/snobol4jvm` |
| `github.com/SNOBOL4-plus/SNOBOL4-dotnet` | `github.com/snobol4ever/snobol4dotnet` |
| `github.com/SNOBOL4-plus/SNOBOL4-corpus` | `github.com/snobol4ever/corpus` |
| `github.com/SNOBOL4-plus/SNOBOL4-harness` | `github.com/snobol4ever/harness` |
| `github.com/SNOBOL4-plus/SNOBOL4-python` | `github.com/snobol4ever/snobol4python` |
| `github.com/SNOBOL4-plus/SNOBOL4-cpython` | `github.com/snobol4ever/snobol4artifact` |
| `github.com/SNOBOL4-plus/SNOBOL4-csharp` | `github.com/snobol4ever/snobol4csharp` |
| `github.com/SNOBOL4-plus/.github` | `github.com/snobol4ever/.github` |

### Brand text substitutions

| find | replace |
|------|---------|
| `SNOBOL4ever` | `snobol4ever` |
| `SNOBOL4now` | `snobol4now` |
| `SNOBOL4-tiny` (repo refs) | `snobol4x` |
| `SNOBOL4-jvm` (repo refs) | `snobol4jvm` |
| `SNOBOL4-dotnet` (repo refs) | `snobol4dotnet` |
| `SNOBOL4-corpus` (repo refs) | `corpus` |
| `SNOBOL4-cpython` (repo refs) | `snobol4artifact` |
| `SNOBOL4-python` (repo refs) | `snobol4python` |
| `SNOBOL4-csharp` (repo refs) | `snobol4csharp` |
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
| `SNOBOL4-tiny` | `snobol4x` |
| `SNOBOL4-jvm` | `snobol4jvm` |
| `SNOBOL4-dotnet` | `snobol4dotnet` |
| `SNOBOL4-corpus` | `corpus` |
| `SNOBOL4-harness` | `harness` |
| `SNOBOL4-python` | `snobol4python` |
| `SNOBOL4-cpython` | `snobol4artifact` |
| `SNOBOL4-csharp` | `snobol4csharp` |
| `.github` | `.github` (unchanged — GitHub requires this name) |

---

## Phase 5 — Update all local git remotes

Run in each cloned repo on every machine:

```bash
git remote set-url origin https://github.com/snobol4ever/snobol4x
git remote set-url origin https://github.com/snobol4ever/snobol4jvm
git remote set-url origin https://github.com/snobol4ever/snobol4dotnet
git remote set-url origin https://github.com/snobol4ever/corpus
git remote set-url origin https://github.com/snobol4ever/harness
git remote set-url origin https://github.com/snobol4ever/snobol4python
git remote set-url origin https://github.com/snobol4ever/snobol4artifact
git remote set-url origin https://github.com/snobol4ever/snobol4csharp
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

**`snobol4x` internal note:** `snoc` stays as the internal compiler binary name. `sno4x` is the user-facing command. Do not rename `snoc`.

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
# expect: 301 Moved Permanently → github.com/snobol4ever/snobol4x
```

---

## Open Items

| item | question | owner |
|------|----------|-------|
| `snoc` vs `sno4x` | `snoc` = internal build tool, `sno4x` = user command. Confirm. | Lon |
| `snobol4x` naming | ✅ Decided 2026-03-17. `snobol4x` replaces `snobol4all` and `snobol4tiny`. Fast, cross-platform, no ceiling implied. | Lon |
| PyPI `snobol4artifact` | Is SNOBOL4-cpython currently on PyPI? If yes, new package needed. | Lon |
| NuGet casing | `Snobol4.Dotnet` namespace — coordinate on C# convention exception. | Jeffrey |
| `SESSIONS_ARCHIVE.md` | Header note only. Do not rewrite history. | Lon |
