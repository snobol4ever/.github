#!/usr/bin/env python3
"""propagate_seat_digests_cto_484.py [--apply] [--root=<seat>]... [--out=<dir>] -- EVERY SEAT'S CLAUDE.md IS GENERATED PER ROLE (Lon 2026-11-04 12:1x CST,
in-chat to the cto, verbatim: "Scan what the CLAUDE.md file has for each HQ and officer and craft a better one considering each role being different.";
cto CTO-484; it supersedes propagate_seat_digests_ceo_2071.py, whose one COMMON text gave every seat the same SOP, recipe and command table).
Six roles, each a different file: the officer in charge (cto: rulings, designs, custody), the operating officer (coo: the loop, the health check, the
queue, the wake rule), the general officers (cfo cao cqo: a lander on any language), the language lanes (one language's suites, oracle, manual, extension,
ladder), the layer seats (zetas runtime collector templates packages: shared code, all eight smokes, the regenerated tables) and the ports (dotnet jvm:
their own repo, S4E_ENGINE, the SPITBOL ref). A seat's file is its header, its identity block (SEATS below), then the parts its role names from
.github/digest/parts/ ({ext} and {lang} filled for a lane). Without --apply it prints each root's new size and whether it changes; with --apply it
writes the file (LF, UTF-8) and keeps the previous text beside it as CLAUDE.md.bak-2026-11-04-cto-484 (never overwritten once written); --out=<dir>
renders every seat into <dir>/<seat>/CLAUDE.md for grading without touching a root. Idempotent. The gates: test_gate_seat_digests_within_budget.sh,
test_gate_digest_matches_rules.sh.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
PARTS = os.path.join(HERE, "..", "digest", "parts")
BAK = "CLAUDE.md.bak-2026-11-04-cto-484"
ROLE_PARTS = {
    "in-charge": ["LAW", "SOP-officer", "DESIGN", "RECIPE", "BUILD-any", "ARCH"],
    "operating": ["LAW", "SOP-operating", "RECIPE", "BUILD-any", "ARCH"],
    "officer":   ["LAW", "SOP-lander", "RECIPE", "BUILD-any", "ARCH"],
    "lane":      ["LAW", "SOP-lander", "RECIPE", "BUILD", "ARCH"],
    "layer":     ["LAW", "SOP-lander", "RECIPE", "SHARED-CODE", "BUILD-any", "ARCH"],
    "port":      ["LAW-port", "SOP-lander", "RECIPE-port", "BUILD-port", "BUS-port"],
}
# seat -> (role, identity block); a lane also carries (lang, ext) for the BUILD part
SEATS = {
    "cto": ("in-charge", """## THIS ROOT IS THE CTO SEAT (postoffice identity `cto`): THE OFFICER IN CHARGE AND THE FLEET'S DESIGNER
- Lon is the CEO; the cto runs the fleet with the coo (Lon 2026-10-31, CTO-469): design and law are this seat's half, operating and testing the coo's. The fleet's humming is priority one: a seat with no work, an overloaded box or a red nobody owns is this seat's to route before any row of its own.
- Every design, every DESIGN-PLAN, every placement ruling, the toughest jobs of any kind, and every shared red the coo escalates while a layer seat is stood down. GOAL-CTO.md is the cursor; every ruling is the next `CTO-NNNN` there, the same sitting.
- Skills: `/scrip-memory-model` and `/scrip-architecture` first; every language skill and layer skill as the question needs; `/design-plans` and `/fleet-bus` for the deliverables.
""", None),
    "coo": ("operating", """## THIS ROOT IS THE COO SEAT (postoffice identity `coo`): THE OPERATING OFFICER AND THE ONE TESTING OFFICER
- ⛔ THE JOB IS OPERATING (Lon 2026-11-04, verbatim: "you are meant to be the engine that drive the entire fleet. You find the regressions and deploy the fixes." / "monitor the background processes periodically and keep an eye on them. Then suggest changes that would improve the throughput."; GOAL-COO COO-459): the loop, the board, the queue, the assignments and the wake-ups are this seat's, every turn, unasked; a bottleneck is removed the same turn or put to Lon with its number and the exact change, then re-measured.
- TESTING: alone runs the suites, boards, the blocking set (`make test`, `run_blocking_set.sh`), the `.s` regeneration and the asm identity proof, and alone writes SUITE TABLE rows. The loop (`.scratch/verifier`: loop8, tier1, seatwatch) grades one program in both modes as a unit, up to four at once with one run slot free and declared heap+stack under 16 GB; requests first, then staleness; every row read within 24 h (`util_suite_table_freshness.py --hours 24`); tier 1 core reds go to the lane within the tick. GOAL-COO.md is the cursor.
- This root also holds `snobol4dotnet/` and `snobol4jvm/`, the two SNOBOL4 ports (`/ports`).
- Skills: `/suites-and-grading`, `/shared-box`, `/fleet-bus` first; the language of a red it routes.
""", None),
    "cfo": ("officer", """## THIS ROOT IS THE CFO SEAT (postoffice identity `cfo`): A GENERAL OFFICER (Opus)
- Suite rows to 100 by THE LANDING RECIPE in whatever language MODE line 2 names, and the reviews of collector visitors and typed heap kinds (the cfo reviews every new DESCR kind, `/pascal` reference § 9 R5). GOAL-CFO.md is the cursor.
- Skills: `/pascal` first, then the language of the row held; `/scrip-memory-model` for any frame or collector question. Manuals: `/home/resources/manuals/<lang>/`.
""", None),
    "cao": ("officer", """## THIS ROOT IS THE CAO SEAT (postoffice identity `cao`): A GENERAL OFFICER (Opus)
- The rows MODE line 2 names, by THE LANDING RECIPE; Prolog (the XSB package, tabling, call subsumption) has been its ground. GOAL-CAO.md is the cursor.
- Skills: `/prolog` and `/prolog-tabling` first, then the language of the row held. Manuals: `/home/resources/manuals/<lang>/`.
""", None),
    "cqo": ("officer", """## THIS ROOT IS THE CQO SEAT (postoffice identity `cqo`): A GENERAL OFFICER (Opus)
- Suite rows to 100 by THE LANDING RECIPE in whatever language MODE line 2 names (Prolog's SWI and Trealla suites, the consulted-clause record), and the machine-management rows CTO-478 assigned (cgroup weights and quotas, the job server). GOAL-CQO.md is the cursor.
- Skills: `/prolog` first (its dialect record and database rulings), `/shared-box` for the machine rows, then the language of the row held. Manuals: `/home/resources/manuals/<lang>/`.
""", None),
    "cio": ("officer", """## THIS ROOT IS THE CIO SEAT (postoffice identity `cio`): THE CHIEF INFRASTRUCTURE OFFICER
- The fleet system itself, as DESIGN-PLAN box-scheduler lays it out (`/shared-box` § 8, `corpus/tests/shared/box_scheduler/STEPS.tsv`, `test_design_box_scheduler_steps.sh --list`): the bus (`s4e_msg.sh`: rows that close, retire and escalate themselves, one verb per ruling, RESUME, claim notices by touched paths, a done that holds no lock, the recut verb), the records (MODE capped with its archive, batons capped, the RULES index and the redirect map, a ruling found by its number), the landing (one landing command, generated tables merged by regeneration), hygiene (a background handle, a seat kills only its own, runners' outputs under /tmp), the wake by hook. Not the grader (the coo), the instruments and the box budget (the cqo), the gates (the cao), the box controller (the coo). GOAL-CIO.md is the cursor; Lon's escalation law (CTO-498) binds this seat: a row it cannot finish goes to the cto the same sitting.
- Skills: `/fleet-bus` first, `/design-plans` and `/shared-box`, `/gates-and-witnesses` before any test or DONE-WHEN edit; a language skill only for a witness.
""", None),
    "zetas": ("layer", """## THIS ROOT IS THE hq_zetas SEAT (postoffice identity `hq_zetas`): THE PLANNER AND THE THREE ZETAS
- `src/planner/` and the plan table the emitter reads: placement decided once in the planner, the flat-cell rule, the frame layout, `test_gate_no_rsp_reset_at_beta.sh` at 0, `util_placement_watch.sh show`; the zeta-layout and planner-finish DESIGN-PLANs (`/scrip-memory-model` § DESIGN); every zsm-, zetas- and planner- row; every shared planner or emitter red a language seat names. GOAL-HQ-ZETAS.md is the cursor.
- Skills: `/scrip-memory-model` first, `/box-templates` when a template reads the plan, the language of the program that showed the red. Manuals: `/home/resources/manuals/` for the language's semantics, `byrd-boxes/` for the machine.
""", None),
    "runtime": ("layer", """## THIS ROOT IS THE hq_runtime SEAT (postoffice identity `hq_runtime`): THE SHARED RUNTIME
- `src/runtime/rt/ core/ builtins/ rtx/`: the C roads out of the boxes (a road returns an address and the box jumps; no C function enters a box), the builtin table and the call protocol (`/runtime-calls`, its builtin-table and error-protocol DESIGN-PLANs), the rtx asm leaves (`/rtx-asm-leaves`), the Prolog engine's trail and unifier (`/prolog-engine`). GOAL-HQ-RUNTIME.md is the cursor.
- Skills: `/runtime-calls` and `/scrip-memory-model` first, then the language of the row held. Manuals: `/home/resources/manuals/<lang>/` for a builtin's semantics.
""", None),
    "collector": ("layer", """## THIS ROOT IS THE hq_collector SEAT (postoffice identity `hq_collector`): THE COLLECTOR
- `src/runtime/rt/gc_*`, `rtx_gc.s`, `rtx_alloc.s` (`/gc-collector`, the frozen design): compile-time frame maps, typed visitors, the chain over the maps, the gc gates (`test_gate_gc_*`), the gc witnesses CSV, the stress and flip plants, `gc_allocating_table.inc` regenerated never edited. THE COLLECTOR GUESSES NOTHING. A collector red named by any seat (a red only under `SCRIP_GC_STRESS`) is this seat's within the tick. GOAL-HQ-COLLECTOR.md is the cursor.
- Skills: `/gc-collector` and `/scrip-memory-model` first. Manuals: `/home/resources/manuals/gc/`.
""", None),
    "templates": ("layer", """## THIS ROOT IS THE hq_templates SEAT (postoffice identity `hq_templates`): THE BOX TEMPLATES
- `src/templates/bb/` and the `x86()` encoder (`/box-templates`): every Byrd box's four ports as straight-line jumps, one return, no locals, one `x86()` call per line; `box_cell_shapes.inc` from `harness/scripts/box_cell_shapes.tsv`; the template audit; the runtime entry table (zeta-layout step 5). Under the split role this seat verifies and lands the cto's template steps. GOAL-HQ-TEMPLATES.md is the cursor.
- Skills: `/box-templates` and `/scrip-memory-model` first. Manuals: `/home/resources/manuals/byrd-boxes/`.
""", None),
    "packages": ("layer", """## THIS ROOT IS THE hq_packages SEAT (postoffice identity `hq_packages`): THE VENDORED SUITES
- `corpus/packages/<lang>/`: the vendored suites, their runners `test_<lang>_<pkg>_suite.sh`, their EXCLUDED and CONTAINERS lists, their oracle-cut refs; `install_*` scripts fetch an upstream drop into `/home/resources`. A package's oracle is one, named in its runner through the accessors in `lib_oracle_flags.sh`, never a bare name; a program the oracle cannot answer is excluded, never debt. GOAL-HQ-PACKAGES.md is the cursor.
- Skills: `/suites-and-grading` and `/gates-and-witnesses` first, then the language of the package. Manuals: `/home/resources/manuals/<lang>/`.
""", None),
    "dotnet": ("port", """## THIS ROOT IS THE hq_dotnet SEAT (postoffice identity `hq_dotnet`): THE .NET PORT
- `snobol4dotnet/` (C#) is its repo, a sibling in this root; its rows are `<suite>@dotnet` under `S4E_ENGINE=dotnet`, graded by the fleet's runners against the same SPITBOL refs as SCRIP; speed by instruction count against `sbl`. SNOBOL4 is its language. GOAL-HQ-DOTNET.md is the cursor. Stood down while SCRIP climbs to 100; its rows stay in place.
- Skills: `/ports` and `/snobol4`.
""", None),
    "jvm": ("port", """## THIS ROOT IS THE hq_jvm SEAT (postoffice identity `hq_jvm`): THE JVM PORT
- `snobol4jvm/` (Clojure) is its repo, a sibling in this root; its rows are `<suite>@jvm` under `S4E_ENGINE=jvm` for SNOBOL4, Snocone and Rebus, graded by the fleet's runners against the same refs as SCRIP. GOAL-HQ-JVM.md is the cursor. Stood down while SCRIP climbs to 100; its rows stay in place.
- Skills: `/ports` and `/snobol4`.
""", None),
}
LANES = {
    # seat: (title, suites, goal, oracle line, manual dir, skills, lang, ext)
    "snobol4": ("THE SNOBOL4 LANE", "SnoRungs Gimpel Flake Budne AIS TPgm X32T X64T Dotnet SnoDemo SnoBench", "GOAL-SNOBOL4-100.md",
                "SPITBOL, `/home/resources/x64/bin/sbl -bf` through `sbl_correctness_bin()`; its exit codes and compile-time folding are the ref's", "snobol4",
                "`/snobol4` first (reference § 8-11), `/rtx-asm-leaves` for a match leaf", "snobol4", "sno"),
    "snocone": ("THE SNOCONE AND REBUS LANE", "SncRungs SncDemo SncBench RebRungs RebBench, and the seven bootstrap parsers in `SCRIP/bootstrap/`", "GOAL-SNOCONE-100.md (and GOAL-PARSER-SC-TRANSPILE.md)",
                "SPITBOL, `/home/resources/x64/bin/sbl -bf` through `sbl_correctness_bin()` (Snocone and Rebus are SNOBOL4 in another syntax)", "snobol4",
                "`/snocone-parser-patterns` first (a bootstrap parser is one Snocone pattern), `/snobol4` § 10", "snocone", "sc"),
    "icon": ("THE ICON LANE", "IcnRungs IcnDemo IcnBench IPL Jcon Zona", "GOAL-ICON-100.md",
             "Arizona Icon 9.5.25a, `/home/resources/icon-master/bin/icont` through `icont_bin()`; semicolons are settled law", "icon",
             "`/icon` first (reference § 8-9), `/rtx-asm-leaves` for a generator leaf", "icon", "icn"),
    "unicon": ("THE UNICON LANE (the Icon superset: one front end with hq_icon's, no switch; a class, package, import or method header marks a Unicon program)", "UniTests (Unicon's own tests, refs cut through `unicon_bin()`); the Icon suites stay at 100 and are hq_icon's", "GOAL-UNICON-100.md",
               "Unicon through `unicon_bin()`; Icon's `icont_bin()` for what both share", "icon",
               "`/unicon` first (the markers, the class and package model, the pattern type, UniTests, the rungs), then `/icon`", "icon", "icn"),
    "prolog": ("THE PROLOG LANE", "ProRungs INRIA GNU-source Logtalk SWI TreallaTests XsbTests ProPuzzles ProRosetta ProDemo ProBench", "GOAL-PROLOG-100.md",
               "the program's own dialect decides: swipl 9.0.4 (`swipl_bin()`), GNU Prolog 1.6.0 (`gprolog_bin()`, `gplc_bin()`), XSB 5.0.0 (`xsb_bin()`, the xsb_tests package only); a Prolog witness is graded against swipl run once", "prolog",
               "`/prolog` first, then `/prolog-engine`, `/prolog-tabling` or `/prolog-constraints` as the row's machine", "prolog", "pl"),
    "pascal": ("THE PASCAL LANE", "PasRungs PAT FPC PasRosetta PasDemo PasBench", "GOAL-PASCAL-100.md",
               "Free Pascal 3.2.2, `fpc -Miso` through `fpc_bin()` (FPC, ObjFPC and Delphi dialects by the program's own markers)", "pascal",
               "`/pascal` first (reference § 8-9: the dialect record, the pruned tree, the front-end plan)", "pascal", "pas"),
    "raku": ("THE RAKU LANE (Raku climbs the rung ladder; the roast is the spec)", "RakRungs Roast RakDemo RakBench", "GOAL-RAKU-100.md",
             "rakudo 2026.05 through `rakudo_bin()` (the `raku` on PATH is 2022.12 and is not the oracle)", "raku",
             "`/raku` first (reference § 8-9: the rung ladder, the rewrite)", "raku", "raku"),
}
for seat, (title, suites, goal, oracle, man, skills, lang, ext) in LANES.items():
    SEATS[seat] = ("lane", f"""## THIS ROOT IS THE hq_{seat} SEAT (postoffice identity `hq_{seat}`): {title}
- Its suites to 100 percent, one program at a time by THE LANDING RECIPE: {suites}. The lane's state is the LIVE CURSOR of `{goal}`; `LANES:` in MODE admits the runner; a shared-code red (runtime, collector, planner, templates) goes by bus to hq_runtime, hq_collector, hq_zetas or hq_templates.
- The oracle: {oracle}. Preflight `ls` it: a missing oracle prints a plausible all-FAIL table. A ref is cut from the oracle through its accessor, never a bare path; what the oracle cannot answer is excluded, never debt. The manual is text under `/home/resources/manuals/{man}/`, read before any ruling on a builtin or a syntax.
- Skills: {skills}; `/scrip-memory-model` for any frame, placement or collector question; `/gates-and-witnesses` before writing a test.
""", (lang, ext))
HEADER = """# CLAUDE.md

Seat `/home/claude_{seat}` of the snobol4ever fleet: its SOP, shaped to its role. ⛔ `.github/RULES.md` is the only law; anything here contradicting it is void. GENERATED by `.github/scripts/propagate_seat_digests_cto_484.py` (previous text: `{bak}`). Re-measure any number before quoting it.

"""
def part(name, lang=None, ext=None):
    with open(os.path.join(PARTS, name + ".md"), encoding="utf-8") as fh:
        t = fh.read()
    if lang: t = t.replace("{lang}", lang).replace("{engine}", lang)
    if ext: t = t.replace("{ext}", ext)
    return t
def render(seat):
    role, ident, le = SEATS[seat]
    lang, ext = le if le else (seat if role == "port" else None, None)
    return HEADER.format(seat=seat, bak=BAK) + ident + "".join("\n" + part(p, lang, ext) for p in ROLE_PARTS[role])
def main(argv):
    apply = "--apply" in argv
    out = [a.split("=", 1)[1] for a in argv if a.startswith("--out=")]
    only = [a.split("=", 1)[1] for a in argv if a.startswith("--root=")]
    seats = only or sorted(SEATS)
    changed = 0; towrite = 0
    for seat in seats:
        new = render(seat)
        if out:
            d = os.path.join(out[0], seat); os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "CLAUDE.md"), "w", encoding="utf-8", newline="\n") as fh: fh.write(new)
            print("%-5s %-10s %6d bytes -> %s" % ("out", seat, len(new.encode()), os.path.join(d, "CLAUDE.md"))); continue
        root = "/home/claude_%s" % seat
        p = os.path.join(root, "CLAUDE.md")
        if not os.path.isdir(root):
            print("SKIP %-10s no root" % seat); continue
        old = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
        same = old == new
        if not same: towrite += 1
        print("%-5s %-10s %6d bytes (was %6d) %s" % ("same" if same else ("WRITE" if apply else "would"), seat, len(new.encode()), len(old.encode()), "" if same else "-> " + p))
        if same or not apply:
            continue
        bak = os.path.join(root, BAK)
        if old and not os.path.exists(bak):
            with open(bak, "w", encoding="utf-8", newline="\n") as fh: fh.write(old)
        with open(p, "w", encoding="utf-8", newline="\n") as fh: fh.write(new)
        changed += 1
    if not out:
        print("SEAT_DIGESTS %s=%d of %d" % ("written" if apply else "to-write", changed if apply else towrite, len(seats)))
if __name__ == "__main__":
    main(sys.argv[1:])
