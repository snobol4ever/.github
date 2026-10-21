#!/usr/bin/env bash
# remove_our_symlinks_in_roots_ceo_1853.sh -- EVERY LINK WE MADE IN A SEAT ROOT GOES (ceo CEO-1853; Lon 2026-10-21, in-chat to the ceo, verbatim:
# "Get all those symlinks removed. We do not use symlinks anywhere for the snobol4ever organization." · "We use proper absolute and relative
# paths. All repos are siblings. And /home/resources is location for many things." · "I am concerned only with ones we create.").
# MEASURED 2026-10-21 09:1x CDT: 182 links in six roots, every one ours -- five down HQ roots (collector, pascal, raku, snocone, templates)
# still on 10-14/10-15 checkouts whose corpus tracks 31 links and whose SCRIP tracks one (origin tracks none since CEO-1820), plus untracked
# leftovers (a stale build's out/libscrip_rt.so, SCRIP/scripts/scrip, the cfo's SCRIP/refs/*, the collector's .scratch trees).
# PER ROOT: (1) each git repo (SCRIP, corpus, harness, .github, a port repo) that is CLEAN and NOT AHEAD of origin is fetched and
# fast-forwarded -- origin tracks no link, so the tracked links leave with the pull; a dirty or ahead repo is NAMED and left untouched for
# its seat. (2) every symlink still on disk under the root outside .git is deleted -- the link only, never what it points at.
# /home/resources is NOT touched (Lon: "do not mess with /home/resources folder if the layout is as intended by the authors").
#   bash /home/claude_ceo/.github/scripts/remove_our_symlinks_in_roots_ceo_1853.sh            dry run: what it would do, every root
#   bash /home/claude_ceo/.github/scripts/remove_our_symlinks_in_roots_ceo_1853.sh --apply    do it, every root
#   bash /home/claude_ceo/.github/scripts/remove_our_symlinks_in_roots_ceo_1853.sh --apply /home/claude_x   one root
# rc 0 every root reads zero links after · rc 1 a root still holds links (named) · rc 2 a fetch failed (named), the rest still done.
set -u
apply=0; [ "${1:-}" = "--apply" ] && { apply=1; shift; }
roots="${1:-$(ls -d /home/claude_* 2>/dev/null)}"
rc=0
for R in $roots; do
    before="$(find "$R" -path '*/.git' -prune -o -type l -print 2>/dev/null | wc -l)"
    [ "$before" = 0 ] && { printf '%-26s 0 links\n' "$R"; continue; }
    printf '%-26s %s link(s)\n' "$R" "$before"
    for g in "$R"/*/.git "$R"/.github/.git; do
        [ -d "$g" ] || continue
        d="$(dirname "$g")"
        tl="$(git -C "$d" ls-files -s 2>/dev/null | awk '$1=="120000"' | wc -l)"
        [ "$tl" = 0 ] && continue
        dirty="$(git -C "$d" status --porcelain --untracked-files=no | wc -l)"
        if [ "$dirty" != 0 ]; then echo "    HOLD  $d tracks $tl link(s) but has $dirty local change(s) -- its seat pulls it"; continue; fi
        if [ "$apply" = 0 ]; then echo "    would fetch + ff-only $d (tracks $tl link(s); origin tracks none)"; continue; fi
        git -C "$d" fetch -q origin || { echo "    ⛔ $d: fetch failed"; rc=2; continue; }
        ahead="$(git -C "$d" rev-list --count origin/main..HEAD 2>/dev/null || echo 1)"
        if [ "$ahead" != 0 ]; then echo "    HOLD  $d is $ahead commit(s) ahead of origin -- its seat pulls it"; continue; fi
        git -C "$d" merge -q --ff-only origin/main && echo "    ff    $d -> $(git -C "$d" log -1 --format=%h)" || { echo "    ⛔ $d: ff-only merge refused"; rc=2; }
    done
    left="$(find "$R" -path '*/.git' -prune -o -type l -print 2>/dev/null)"
    if [ -n "$left" ]; then
        if [ "$apply" = 0 ]; then printf '%s\n' "$left" | sed 's/^/    would delete link /' | head -12; [ "$(printf '%s\n' "$left" | wc -l)" -gt 12 ] && echo "    ..."
        else
            for l in $left; do git -C "$(dirname "$l")" ls-files --error-unmatch "$(basename "$l")" >/dev/null 2>&1 && { echo "    HOLD  $l is still tracked -- its repo did not fast-forward"; continue; }; rm -f -- "$l"; done
        fi
    fi
    after="$(find "$R" -path '*/.git' -prune -o -type l -print 2>/dev/null | wc -l)"
    [ "$apply" = 1 ] && { printf '    after: %s link(s)\n' "$after"; [ "$after" = 0 ] || rc=$(( rc == 2 ? 2 : 1 )); }
done
exit "$rc"
