#!/usr/bin/env python3
"""CEO-1386 digest propagation (Lon-run where the harness refuses a ceo Bash write into a sibling root).
Lon 2026-10-01 09:3x CDT to the ceo: "So get your findings=0 or whatever you need to get your act together and the
fleet working real needed work." and "Do everything you suggest to modify your protocol, standard operating procedure,
mode of operation, ways to communicate, etc. You are the CEO." This inserts one dated law bullet at the head of every
/home/claude_*/CLAUDE.md (right after the '# CLAUDE.md' title line), a dated .bak beside each file first.
    python3 .github/scripts/propagate_row_exists_while_measured_ceo_1386.py --dry-run | --apply [--only /home/claude_x/CLAUDE.md]
"""
import glob, shutil, sys, datetime
BULLET = ("⛔⭐⭐⭐⭐ **A ROW EXISTS ONLY WHILE A MEASUREMENT SAYS THE PROBLEM EXISTS (Lon 2026-10-01 09:3x CDT, in-chat to the ceo, "
          "verbatim: *\"So it appears the work list is out of date with reality. How can we tighten up what work items actually exist for real, i.e. are "
          "necessary?\"* · *\"So get your findings=0 or whatever you need to get your act together and the fleet working real needed work.\"* · "
          "*\"Do everything you suggest to modify your protocol, standard operating procedure, mode of operation, ways to communicate, etc. You are the "
          "CEO.\"*; ruled CEO-1386; RULES.md § FACT RULE — A ROW EXISTS ONLY WHILE A MEASUREMENT SAYS THE PROBLEM EXISTS; postoffice PROTOCOL.md "
          "§ of the same name):** the score board is the work list and the queue is its projection — a live row names a red an instrument shows "
          "today. `mint` REFUSES a row with no DONE-WHEN or a prose one (rc=2, nothing written): a Lon word is minted with its WITNESS as the criterion "
          "— the failing program, the gate that reds, the SUITE TABLE row that is not 100% — never a sentence (a bus gate's fixture row names "
          "itself in `S4E_MINT_NO_CRITERION`). THE SWEEP (`.github/scripts/util_queue_zero_base.py --apply`, the ceo, every sitting and at every mode "
          "flip) archives DONE rows, retires SUPERSEDED, RETIRED, flip-parked and plain PARKED rows and every FREE row whose finish line is the "
          "placeholder or runs a board, and RUNS every other FREE finish line: GREEN closes the row, RED keeps it (rank 0/1 re-ranked to 2 unless it is "
          "an every-suite row) and writes the measurement as a LEDGER line in its baton, a refusal retires it, a TIMEOUT keeps it; CLAIMED, ASSIGNED, "
          "PARKED-LON-HOLD, PARKED-UMBRELLA and rows BLOCKED on a live row are never touched (CEO-755c). EXPIRY: a FREE row whose baton is unwritten for "
          "7 days parks as PARKED-EXPIRED, a PARKED-EXPIRED row untouched for 30 days retires. Nothing is deleted — a retired row keeps its baton and "
          "returns only by re-mint from a current red. Rank 0 and 1 are for a red on the SUITE TABLE or a blocking gate. `util_queue_visibility_census.py` "
          "reading 0 is the DONE-WHEN of every sweep.\n\n")
apply = "--apply" in sys.argv
only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
for f in sorted(glob.glob("/home/claude_*/CLAUDE.md")):
    if only and f != only: continue
    t = open(f, encoding="utf-8").read()
    if "CEO-1386" in t: print("already:", f); continue
    if not t.startswith("# CLAUDE.md\n"): print("no title anchor, skipped:", f); continue
    new = "# CLAUDE.md\n\n" + BULLET + t[len("# CLAUDE.md\n"):].lstrip("\n")
    print(("APPLY " if apply else "would ") + f)
    if apply:
        shutil.copy2(f, f + ".bak-" + stamp + "-ceo1386")
        open(f, "w", encoding="utf-8", newline="\n").write(new)
