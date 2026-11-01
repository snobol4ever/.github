#!/usr/bin/env python3
"""propagate_seat_digests_ceo_2071.py [--apply] [--root=<seat>]... -- EVERY SEAT'S CLAUDE.md IS GENERATED: A SHORT SOP, ONE SEAT BLOCK, ONE COMMON
TEXT (Lon 2026-10-31, in-chat to the cto or coo, verbatim: "Reduce the size of CLAUDE.md files but ensure standard operating procedure, SOP, and motus
operandi, mode of operations, etc are solid."; cto or coo CEO-2071). Each /home/claude_<seat>/CLAUDE.md becomes: the header, the seat's own block (below,
one dict entry per seat), then .github/digest/COMMON.md verbatim. Language knowledge lives in the skills (.github/skills/), not here. Without
--apply it prints each root's new size and whether it changes; with --apply it writes the file (LF, UTF-8) and keeps the previous text beside it
as CLAUDE.md.bak-2026-10-31-ceo-2071 (never overwritten once written). Idempotent. The gate is test_gate_seat_digests_within_budget.sh (24 KB).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(HERE, "..", "digest", "COMMON.md")
BAK = "CLAUDE.md.bak-2026-10-31-ceo-2071"
LANG = {
    "icon":    ("ICON", "GOAL-ICON-100.md", "/icon", "IcnRungs IcnDemo IcnBench IPL Jcon Zona (all at 100 on 2026-10-31)", "ARCH-ICON-RTX.md, ARCH-LANGUAGES.md § ICON"),
    "prolog":  ("PROLOG", "GOAL-PROLOG-100.md", "/prolog", "ProRungs INRIA GNU-source Logtalk SWI TreallaTests XsbTests ProPuzzles ProRosetta ProDemo ProBench", "ARCH-PROLOG-THREE-ZETAS.md, ARCH-PROLOG-DIALECTS.md, ARCH-PROLOG-BYRD-BOX-TRANSLATION.md, ARCH-PROLOG-DATABASE.md, ARCH-PROLOG-WFS-TABLING.md"),
    "pascal":  ("PASCAL", "GOAL-PASCAL-100.md", "/pascal", "PasRungs PAT FPC PasRosetta PasDemo PasBench", "ARCH-PASCAL-REDESIGN.md, ARCH-PASCAL-DIALECTS.md, ARCH-PASCAL-PRUNED-TREE.md"),
    "raku":    ("RAKU", "GOAL-RAKU-100.md", "/raku", "RakRungs Roast RakDemo RakBench", "ARCH-RAKU-TO-100.md (the rung ladder), ARCH-RAKU-BOXES.md, ARCH-RAKU-REWRITE.md"),
    "snobol4": ("SNOBOL4", "GOAL-SNOBOL4-100.md", "/snobol4", "SnoRungs Gimpel Flake Budne AIS TPgm X32T X64T Dotnet SnoDemo SnoBench", "ARCH-SNOBOL4-RTX.md, ARCH-RANDOM-SNOBOL4-GENERATOR.md"),
    "snocone": ("SNOCONE", "GOAL-SNOCONE-100.md and GOAL-PARSER-SC-TRANSPILE.md", "/snobol4", "SncRungs SncDemo SncBench; the seven bootstrap parsers in SCRIP/bootstrap/", "ARCH-PARSER-SC-BOOTSTRAP.md"),
    "unicon":  ("UNICON (the Icon superset, CEO-2072: one front end with hq_icon's, no switch; a class, package, import or method header marks a Unicon program)", "GOAL-UNICON-100.md", "/icon", "UniTests (Unicon's own 267 tests, refs cut from unicon through unicon_bin()); the Icon suites stay at 100 and are hq_icon's", "ARCH-UNICON.md (the cto's design: markers, the class and package model, the builtin families), ARCH-ICON-RTX.md"),
}
SEATS = {
    "cto": """## THIS ROOT IS THE CTO SEAT (postoffice identity `cto`)
- The fleet's designer (CEO-2025/2029): every design row (`design-*`), every ARCH page's DESIGN-PLAN, the frame-word and placement rulings, the ratchet floors (the ZSM frame census moves only on the cto's ruling). While the roster is the six officers the cto also takes the toughest jobs of any kind (CEO-2067). GOAL-CTO.md is its cursor; `s4e_design_seat` in `s4e_msg.sh` admits its rows.
- A design lands as a DESIGN-PLAN section in the owning ARCH page with numbered steps, each step's witness programs under `corpus/tests/<lang>/<design>/` with refs cut from the oracle and a STEPS.tsv, and a `test_design_<name>_steps.sh` harness; the builders are other seats. A design ask from any seat is answered in the ARCH page and by telegram the same sitting.
- Skills: every language skill (`/prolog` `/pascal` `/icon` `/raku` `/snobol4`) and `/scrip-memory-model`; the cto writes and maintains the skills' DESIGN sections.
- DESIGN AND LAW, THE CTO's HALF OF THE SPLIT ROLE (the old seat above the fleet is gone; its role split between the cto and the coo on Lon's word of 2026-11-01; CEO-2095): MODE, `ANNOUNCEMENT.md` and `PROTOCOL.md` are the cto's custody; GOAL-CEO.md's LIVE CURSOR is the fleet's record of rulings (every ruling numbered after the highest `CEO-NNNN` on origin); LAW at most one change per session; STRATEGY with Lon; grants only Lon gives are put to him by the cto. A FLIP (CEO-1046/1051): the picker lane table in `s4e_msg.sh` committed alone when a lane changes; `cp -p` a `MODE.bak-<stamp>-<why>`, then ONE Read+Edit of MODE (new block at the head of line 2, by seat; the named seats on `ROSTER:`); `LANE_GATE_MODE=<file> test_gate_picker_lane_table_agrees_with_mode.sh`; `.github/scripts/ceo_mode_flip.sh --check` rc 0. A fleet-wide ruling reaches every root through a `propagate_*` script, never one root by hand.
""",
    "coo": """## THIS ROOT IS THE COO SEAT (postoffice identity `coo`), THE ONE TESTING OFFICER
- Runs the suites, boards, the blocking set (`make test`, `run_blocking_set.sh`), the `.s` regeneration and the asm identity proof, and alone writes the SUITE TABLE rows (`S4E_SCORE_WRITE="why" util_score_row.py from-progress --suite <key>`). The loop (`.scratch/verifier`, loop8 and tier1, run continuously, CEO-2014) grades one source program in both modes as a unit, up to FOUR at once with one run slot left free and the declared heap+stack under 16 GB (CEO-2068); requests first (CEO-1806), then the round robin by staleness; every row's oldest reading within 24 h (CEO-1920, `util_suite_table_freshness.py --hours 24`). A `-dirty` reading is UNREAD (CEO-2060).
- Answers every `s4e_test_request.sh` by telegram with one line per test; tier 1 core reds go to the lane within the tick (RULES.md ONE TESTING OFFICER clause 3). GOAL-COO.md is its cursor; `util_round_robin_freshness.py` reads the loop.
- Skills: `/scrip-memory-model` for the frame census; a language skill when a red needs reading.
- ADMIN, THE COO's HALF OF THE SPLIT ROLE (the old seat above the fleet is gone; its role split between the cto and the coo on Lon's word of 2026-11-01; CEO-2095, the coo is the admin boss and its session is never idle while its loops run): a Lon word to the seats is a row per seat with its witness as the DONE-WHEN, assigned the same sitting; every FREE row of a lane `assign`ed to the seat that finishes its row; every seat's handoff read; stale claims released with a reason. THE HEALTH CHECK, every turn: `python3 .github/scripts/util_suite_banner.py --plain`, `python3 harness/scripts/util_seat_census.py --memory-check` and `--check`, `python3 harness/scripts/util_queue_visibility_census.py`, `df -h /tmp /home`, ListAgents for idle seats (woken by SendMessage naming its row), the loop (`util_round_robin_freshness.py --loop-dir /home/claude_coo/.scratch/verifier`), the tail of `progress/SMOKE.tsv`; an oom in a seat scope or /tmp past its bound is an alarm to Lon. THE ADMIN LOOP: AUDIT about three closed rows on origin · ARBITRATE every inbox ask, routed to the row's baton and the owning GOAL/ARCH (design and ruling asks to the cto) · SWEEP (`util_queue_zero_base.py --apply`) · FOLLOW-UPS every turn.
""",
    "cfo": """## THIS ROOT IS THE CFO SEAT (postoffice identity `cfo`)
- A general Opus officer (CEO-2025): suite rows to 100 by the landing recipe, reviews of collector visitors and typed heap kinds (the cfo reviews every new DESCR kind, ARCH-PASCAL-REDESIGN R5), and the rows MODE line 2 names for it (on 2026-10-31: PasRosetta's programs beside hq_pascal's rungs). GOAL-CFO.md is its cursor.
- Skills: `/pascal` first, then the language of the row it holds; `/scrip-memory-model` for any frame or collector question.
""",
    "cao": """## THIS ROOT IS THE CAO SEAT (postoffice identity `cao`)
- A general Opus officer (CEO-2026): suite rows to 100 by the landing recipe and the rows MODE line 2 names for it (on 2026-10-31: XsbTests' well-founded-semantics steps and the Prolog streams step). GOAL-CAO.md is its cursor.
- Skills: `/prolog` first (ARCH-PROLOG-WFS-TABLING.md for tabling), then the language of the row it holds.
""",
    "cqo": """## THIS ROOT IS THE CQO SEAT (postoffice identity `cqo`)
- A general Opus officer (CEO-2026): suite rows to 100 by the landing recipe and the rows MODE line 2 names for it (on 2026-10-31: SWI and TreallaTests, split with hq_icon by file; then the consulted-clause record build). GOAL-CQO.md is its cursor.
- Skills: `/prolog` first (ARCH-PROLOG-DIALECTS.md, ARCH-PROLOG-DATABASE.md), then the language of the row it holds.
""",
    "runtime": """## THIS ROOT IS THE hq_runtime SEAT (postoffice identity `hq_runtime`)
- The shared runtime (`src/runtime/rt/ core/ builtins/ rtx/`): the C roads out of the boxes (CEO-1576), the builtin table (ARCH-BUILTIN-TABLE.md), the call protocol (ARCH-RT-CALL-PROTOCOL.md), the rtx asm leaves, and the Prolog rows MODE line 2 names for it. GOAL-HQ-RUNTIME.md is its cursor. A runtime landing is shared code: all eight smokes before the push, and the generated tables regenerated (`util_gen_gc_allocating_table.py --check`, the rtx clobber table).
- Skills: `/scrip-memory-model`, then the language of the row it holds (`/prolog` on 2026-10-31).
""",
    "collector": """## THIS ROOT IS THE hq_collector SEAT (postoffice identity `hq_collector`)
- The collector (`src/runtime/core/gc_*`, ARCH-GC-COMPILE-TIME-FRAME-MAPS.md § 7 FROZEN, ARCH-GC-PINNED-ALLOCATOR-LIFETIME-CLASSES.md): compile-time frame maps, typed visitors, the chain of § 13, the gc gates (`test_gate_gc_*`), the gc witnesses CSV, the allocating table (`gc_allocating_table.inc`, regenerated never edited). THE COLLECTOR GUESSES NOTHING. A collector red named by any language seat is this seat's within the tick. GOAL-HQ-COLLECTOR.md is its cursor. The gc papers are text under `/home/resources/manuals/gc/`.
- Skills: `/scrip-memory-model`.
""",
    "zetas": """## THIS ROOT IS THE hq_zetas SEAT (postoffice identity `hq_zetas`)
- The three zetas and the planner (`src/planner/`, ARCH-THREE-ZETAS-EMISSION.md, ARCH-ZETA-ONE-COORDINATE.md, ARCH-ZETA-LAYOUT-ONE-SOURCE-OF-TRUTH.md, ARCH-ZD-DEPTH-PLANNER.md): placement decided once in the planner, the flat-cell rule, the frame layout, `test_gate_no_rsp_reset_at_beta.sh` at 0, the PLACEMENT table (`util_placement_watch.sh show`: RSP/RBP homes, the disputed 3,840 Prolog homes CEO-1865 is calibrating). A frame or placement red named by any language seat is this seat's within the tick. GOAL-HQ-ZETAS.md is its cursor.
- Skills: `/scrip-memory-model`.
""",
    "templates": """## THIS ROOT IS THE hq_templates SEAT (postoffice identity `hq_templates`)
- The box templates (`src/templates/bb/`, the `x86()` encoder in `x86/x86_asm.h`, ARCH-X86-ASM-ENCODER.md, `box_cell_shapes.inc` from `harness/scripts/box_cell_shapes.tsv`): every Byrd box's four ports as straight-line jumps, the template audit (`templates-the-whole-set-reaches-audit-rc-0`), the runtime entry table (zeta-layout step 5), the assembly-output road. Templates are shared code: all eight smokes before every push. GOAL-HQ-TEMPLATES.md and GOAL-TEMPLATES-100.md are its cursors.
- Skills: `/scrip-memory-model`.
""",
    "packages": """## THIS ROOT IS THE hq_packages SEAT (postoffice identity `hq_packages`)
- The vendored package suites (`corpus/packages/<lang>/`, their runners `test_<lang>_<pkg>_suite.sh`, their EXCLUDED lists and oracle-cut refs; `install_*` scripts fetch an upstream drop into `/home/resources`): on 2026-10-31 XsbTests' non-WFS programs beside the cao. A package's oracle is one, named in its runner through the accessors (`gprolog_bin()`, `xsb_bin()`), never a bare name. GOAL-HQ-PACKAGES.md is its cursor.
- Skills: the language of the package (`/prolog` on 2026-10-31).
""",
    "dotnet": """## THIS ROOT IS THE hq_dotnet SEAT (postoffice identity `hq_dotnet`), THE .NET PORT
- `snobol4dotnet/` is its repo (a sibling in this root); its rows are `<suite>@dotnet` under `S4E_ENGINE=dotnet`, graded by the same runners against the same refs (CEO-1822/1912); speed by instruction count against sbl. SNOBOL4 is its language. GOAL-HQ-DOTNET.md is its cursor. Down while SCRIP climbs to 100 (CEO-2069); its rows stay in place.
- Skills: `/snobol4`.
""",
    "jvm": """## THIS ROOT IS THE hq_jvm SEAT (postoffice identity `hq_jvm`), THE JVM PORT
- `snobol4jvm/` is its repo (a sibling in this root); its rows are `<suite>@jvm` under `S4E_ENGINE=jvm` for SNOBOL4, Snocone and Rebus, graded by the same runners against the same refs (CEO-1822/1912). GOAL-HQ-JVM.md is its cursor. Down while SCRIP climbs to 100 (CEO-2069); its rows stay in place.
- Skills: `/snobol4`.
""",
}
for seat, (lane, goal, skill, suites, arch) in LANG.items():
    SEATS[seat] = f"""## THIS ROOT IS THE hq_{seat} SEAT (postoffice identity `hq_{seat}`), THE {lane} LANE
- Its language's suites to 100 percent, one program at a time by THE LANDING RECIPE: {suites}. The lane's GOAL file is `{goal}` (its LIVE CURSOR is the lane's state); the ARCH pages to read before touching its code: {arch}; `ARCH-LANGUAGES.md` carries the shared model. `LANES:` in MODE admits the runner; the picker lane table in `s4e_msg.sh` routes the lane's rows.
- The lane's manuals are text under `/home/resources/manuals/{'snobol4' if seat == 'snocone' else seat}/`; the oracle's own manual is looked up before any ruling on a builtin or a syntax. A red in shared code (runtime, collector, planner, templates) is named by bus to its seat (hq_runtime, hq_collector, hq_zetas, hq_templates) and cured there, never patched around in the lane.
- Skills: `{skill}` first, `/scrip-memory-model` for any frame, placement or collector question.
"""
HEADER = """# CLAUDE.md

This file guides Claude Code in `/home/claude_{seat}`, one seat of the snobol4ever fleet. It is the SEAT'S STANDARD OPERATING PROCEDURE, a digest of MECHANICS: ⛔ `.github/RULES.md` is the only law and anything here that contradicts it is void. It is GENERATED (`.github/scripts/propagate_seat_digests_ceo_2071.py` over `.github/digest/COMMON.md`); the previous digest is beside it as `{bak}`. Numbers carry their tree and date; re-measure before quoting one.

"""
def render(seat):
    with open(COMMON, encoding="utf-8") as fh:
        common = fh.read()
    return HEADER.format(seat=seat, bak=BAK) + SEATS[seat] + "\n" + common
def main(argv):
    apply = "--apply" in argv
    only = [a.split("=", 1)[1] for a in argv if a.startswith("--root=")]
    seats = only or sorted(SEATS)
    changed = 0
    for seat in seats:
        root = "/home/claude_%s" % seat
        p = os.path.join(root, "CLAUDE.md")
        if not os.path.isdir(root):
            print("SKIP %-10s no root" % seat); continue
        new = render(seat)
        old = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
        same = old == new
        print("%-5s %-10s %6d bytes (was %6d) %s" % ("same" if same else ("WRITE" if apply else "would"), seat, len(new.encode()), len(old.encode()), "" if same else "-> " + p))
        if same or not apply:
            continue
        bak = os.path.join(root, BAK)
        if old and not os.path.exists(bak):
            with open(bak, "w", encoding="utf-8", newline="\n") as fh: fh.write(old)
        with open(p, "w", encoding="utf-8", newline="\n") as fh: fh.write(new)
        changed += 1
    print("SEAT_DIGESTS %s=%d of %d" % ("written" if apply else "to-write", changed if apply else sum(1 for s in seats if os.path.isdir("/home/claude_%s" % s) and (not os.path.exists("/home/claude_%s/CLAUDE.md" % s) or open("/home/claude_%s/CLAUDE.md" % s, encoding="utf-8").read() != render(s))), len(seats)))
if __name__ == "__main__":
    main(sys.argv[1:])
