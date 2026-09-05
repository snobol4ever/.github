# FINDING 2026-09-05 seat01: Icon `<->` (reversible exchange) behaves identically to `:=:` -- no undo-on-resume

Row: icon-ladder-every-feature-in-isolation-with-variations (rung15 reversible_swap, form rev_exchange).

The book documents two distinct exchange operators on App.D Infix Operations p.302-303: `v1 :=: v2`
(plain exchange, already covered by this rung's swap_basic/swap_str witnesses) and `v1 <-> v2` ("exchange
values reversibly... reverses the exchange if it is resumed") -- a genuinely different, stronger semantic:
resuming the expression (asking it for a second result) must undo the swap before failing, not just fail.

Witness (`ladder__rung15_real_swap_rev_exchange`, entry 760):
```
procedure main()
  local x, y;
  x := 1;
  y := 2;
  write(x, " ", y);
  every (1 to 2) & (x <-> y) & write(x, " ", y);
  write(x, " ", y);
end
```
`every` drives the conjunction for all of `(1 to 2)`'s results, so `(x <-> y)` is evaluated fresh once and
then **resumed** once (when `(1 to 2)` advances to its second value and the containing `every` backtracks
into everything to its right first). A plain `:=:` in the same harness (verified as a control, not landed
in the corpus) gives `1 2 / 2 1 / 1 2 / 1 2` (state keeps advancing, no undo). Real `<->`, cut against the
oracle (`/home/resources/icon-master/bin/icon` v9.5.25a), gives `1 2 / 2 1 / 2 1 / 1 2` -- the swap
re-appears identically on the second pass because the resume-undo resets x,y before `(1 to 2)` even yields
its second value, and the final state is restored to the untouched original.

SCRIP's actual output for this witness is **byte-identical to the `:=:` control**: `1 2 / 2 1 / 1 2 / 1 2`.
Despite a dedicated box existing for this operator (`src/templates/bb/bb_rev_swap.cpp`, distinct from
`bb_swap.cpp`), it is not implementing the reversible/undo-on-resume semantics -- functionally, `<->`
currently has no observable behavioral difference from `:=:` on this tree (SCRIP=23f342b4). FAILs both
m3 and m4 (rc matches at 0; stdout mismatches).

Landed in the master red per this row's own "there is no xfail" rule, oracle-cut and corrupted-ref-proven
before judgment. `test_icon_ladder.sh --only 15`: 12/14 PASS, this witness 0/2. A sibling gap noted but not
minted this session: the book documents a third, related reversible operator on the same page, `v <- x`
("assign value reversibly"), also unwitnessed anywhere in the corpus -- worth minting alongside whoever
fixes `bb_rev_swap.cpp`, same technique.

Owner: Icon-lane (hq_B) -- `bb_rev_swap.cpp` has no other-language caller found (`grep -rl bb_rev_swap src/`
hits only templates/bb + emit.cpp), so this looks Icon-local, not a shared-node defect.

## Disposition update 2026-09-05 (seat01)

CURED: SCRIP `81cab0ec`. The box itself (`bb_rev_swap.cpp`, `rt_rev_swap_fwd`/`rt_rev_swap_undo`) was
already correct, exactly as hq_B's inbox report to this seat diagnosed -- the undo was emitted but
unreachable. Root cause confirmed identical to that report: `is_resumable()` (`src/lower/lower_icon.c`)
listed `TT_REVASSIGN` in its unconditionally-resumable switch but not sibling `TT_REVSWAP`, so the
conjunction's fail-GOTO in `lower_icon.c` targeted the enclosing disjunction instead of this box, skipping
its beta/undo. One-token fix: added `TT_REVSWAP` alongside `TT_REVASSIGN`.

⚠ Process note for whoever reconciles hq_B's message history: hq_B told this seat (inbox,
`rev-exchange-root-caused-and-cured-your-witness-760-now-matches-oracle`) that this was already "CURED on
my tree" with the same root cause. At this session's fresh `git pull --rebase origin main` (SCRIP
23f342b4 -> 03705701, no lower_icon.c in the diff), `is_resumable()` still lacked `TT_REVSWAP` -- the fix
was not actually in `origin/main` yet. Re-diagnosed independently (confirmed via direct witness-760 rerun,
not assumed from the message) and landed here rather than waited on, per THE LOOP's "fix it, don't park
it" norm. Not a criticism of hq_B's diagnosis, which was exactly right -- just noting the tree it described
and the tree on origin were not yet the same tree.

Verified: witness 760 now byte-identical to the oracle (`1 2 / 2 1 / 2 1 / 1 2`), `test_icon_ladder.sh
--only 15` 14/14, Icon master board 596->607 both modes, zero SNOBOL4 exposure (no SNOBOL4 lowering site
for either TT_REVASSIGN or TT_REVSWAP). The still-owed sibling mint (`v <- x`, rev_assign) remains
unminted, unchanged from above.
