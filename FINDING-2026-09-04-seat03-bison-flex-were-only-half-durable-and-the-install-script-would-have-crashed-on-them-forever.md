# FINDING 2026-09-04 seat03 — bison/flex were only half durable, and install_system_packages.sh would have re-broken on them forever

**Tree:** SCRIP `57ebba8ad` · measured 2026-09-04, seat `seat03`, row `bison-pkgdatadir-missing-blocks-all-grammar-regen` (minted by hq_C 2026-08-30). Cured in this commit.

## The claim

The row's GOAL said the bison *data files* needed a durable home. Measuring it turned up two more things
still pointed at `/tmp`, both of which the row's own DONE-WHEN and GOAL text implied but didn't name.

## What was already fixed vs. what wasn't

The 2026-08-30 finding (`FINDING-2026-08-30-hq_C-bison-on-path-could-not-generate-…`) durably copied the
bison **skeleton tree** to `~/.local/share/bison` and taught `lib_build_flags.sh`'s `gen_tools_ready()` a
fallback chain to find it. That fix is real and still there. But two things still pointed straight at
`/tmp/flexbison/root` (dated 2026-08-20 — a `dpkg -x`-extracted, never-`dpkg -i`'d, copy of the Ubuntu
`bison`/`flex` `.deb`s, stranded because this box has no passwordless sudo to actually install them):

1. **`~/.local/bin/bison` — the thing actually on PATH — was still a symlink into `/tmp`.** A real,
   already-durable copy sat right next to it as `~/.local/bin/bison.real` (created 2026-08-30, same
   timestamp as the skeleton copy), but nothing ever repointed the PATH entry at it. `gen_tools_ready()`
   protects the one script that sources it; every other caller of bare `bison` — a terminal, `cron`, this
   very row's DONE-WHEN — still resolved to the `/tmp` symlink.
2. **`~/.local/bin/flex` was the same symlink pattern**, and flex has no pkgdatadir fallback to fix — if
   `/tmp` is swept, the *binary itself* disappears, not just its data. Nothing in the 08-30 finding
   mentions flex; it wasn't in scope then. It's used by 4 of the 5 grammars this row's DONE-WHEN cares
   about, so it's the same disease, not a different one.

## The cure

- `~/.local/bin/bison` is now a wrapper script (`export BISON_PKGDATADIR="${BISON_PKGDATADIR:-$HOME/.local/share/bison}"; exec bison.real "$@"`) —
  bare `bison` needs no caller-side env override, and an explicit override (if anyone ever sets one) still wins.
- `~/.local/bin/flex` is now a real copy, not a symlink.
- Verified: the row's DONE-WHEN → `BISON-WORKS-WITHOUT-OVERRIDE`. `env -u BISON_PKGDATADIR bash
  scripts/regenerate_parser_and_lexer_from_sources.sh` regenerates all five grammars (snobol4, snocone,
  rebus, raku, pascal) with no tooling error. Three files came out differing from HEAD (`pascal.tab.{c,h}`,
  `snobol4.lex.c`) — pure content drift, unrelated to this row, and per the 08-30 finding's own explicit
  deferral ("cross-language change under SHARED-NODE VERDICT SCOPE… whoever holds those lanes can land
  it") — **reverted, not committed**, so this row stays scoped to the install, not a parser-output change.
- `make -j4 scrip`: builds clean, no regression.

## A third thing, found but not fixed here

`scripts/install_system_packages.sh` decides what to install via `dpkg -s`, which has no idea bison/flex
exist (they were `dpkg -x`'d, never registered). Every run would add them to `MISSING`, then hit
`apt-get update`, which fails immediately on this box (`Permission denied` — no root, no passwordless
sudo), aborting the **entire** "NOT optional" session-start script under `set -e` — for every package in
the list, not just bison/flex. Confirmed live, not theoretical: `apt-get update` bare on this box today →
`E: Could not open lock file /var/lib/apt/lists/lock … Permission denied`.

Patched: before trusting `dpkg -s` for bison/flex, the script now proves generation on a throwaway
grammar (same probe idiom as the row's DONE-WHEN) and skips the apt path entirely if it already works —
mirroring the "prove capability, not presence" rule this same file already applies to `gdb`. Verified by
running the patched script for real.

⚠️ **Left for whoever owns it, deliberately not done here:** with bison/flex now silently self-satisfying,
the script's *next* run surfaced two more packages `dpkg -s` doesn't know about — `wabt` and `gawk` — both
genuinely absent (not a `/tmp` stranding, just never installed), both requiring the same real sudo this
box doesn't have. Unrelated to this row (wabt is WASM tooling for a stubbed-out backend; gawk's absence
hasn't broken anything observed). Recorded here so the next reader doesn't mistake it for a regression
from this fix.

## The generalizable rule

**A durable-location fix isn't durable until you check what's *pointing at* the fix, not just the fix
itself.** The 08-30 finding correctly relocated the data; nothing then asked whether the thing meant to
*use* that data was actually wired to look for it outside the one script that already knew the trick. The
same question ("does the fleet's normal path reach this, or only the path I personally tested") is worth
asking of any `/tmp`-adjacent repair before calling it durable.
