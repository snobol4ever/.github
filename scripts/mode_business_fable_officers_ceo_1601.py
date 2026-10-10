#!/usr/bin/env python3
# mode_business_fable_officers_ceo_1601.py -- MODE line 2 gets the CEO-1601 block (no flip: line 1 stays SEPTET), run by Lon (the classifier refuses the ceo's MODE writes).
# Backup first; refuses rather than half-writes; LANES: and ORDER-OF-WORK: untouched.
import os, shutil, sys, time
path = sys.argv[1] if len(sys.argv) > 1 else "/home/resources/postoffice/MODE"
BLOCK = (
    "# 2026-10-10 11:1x CDT ceo: ⭐⭐⭐ THE OFFICERS HOLD THE HARDEST PROBLEMS (CEO-1601; Lon, in-chat to the ceo, verbatim: *\"I'm thinking having both CTO and CFO seated as Fable 5.1. "
    "Are they working on the hardest problems?\"* then *\"Both CTO and CFO are seated as Fable 5.1 with xhigh effort.\"*). MODELS: the ceo, the cto and the cfo Fable 5.1 at xhigh; the coo "
    "Opus 5.5 at xhigh; the HQs as Lon seats them. THE RE-AIM: the cto keeps the Prolog spine (the assertz reclaim, attributed variables and wake-up -- the FD foundation of "
    "ARCH-PROLOG-CLPFD.md -- then delimited continuations) and takes Raku's generators rewrite after attributed variables (gather/take and the sequence operator as lazy generator boxes on "
    "the suspend road, ARCH-RAKU-BOXES.md step 2); the cfo lands SSU, then takes Raku's regex-and-grammars rewrite (every regex node a Byrd box, rx.c retiring, step 3), its Prolog breadth rows "
    "(the SWI library modules, clpfd, the GNU FD spelling) the fill-in behind it; hq_raku keeps the 21 C-calls-user-code roads (step 1), its umbrella and reds, and dispatch (step 4); hq_prolog "
    "tabling and its lane; hq_pascal the Prolog vendoring; the coo the one testing officer. The officers tell hq_raku before each Raku landing. Everything else as CEO-1595 wrote it. PRIOR: "
)
raw = open(path, "rb").read()
lines = raw.split(b"\n")
if lines[0].strip() != b"SEPTET":
    sys.exit("REFUSED(2): MODE line 1 reads %r, not SEPTET -- nothing written" % lines[0][:40])
if b"CEO-1601" in lines[1]:
    sys.exit("REFUSED(2): MODE line 2 already carries CEO-1601 -- nothing written")
bak = "%s.bak-%s-pre-fable-officers-ceo-1601" % (path, time.strftime("%Y%m%d-%H%M%S"))
shutil.copy2(path, bak)
lines[1] = BLOCK.encode("utf-8") + lines[1]
out = b"\n".join(lines)
tmp = path + ".tmp-ceo-1601"
with open(tmp, "wb") as f:
    f.write(out)
new = open(tmp, "rb").read().split(b"\n")
if len(new) != len(raw.split(b"\n")) or new[0] != raw.split(b"\n")[0] or new[2:] != raw.split(b"\n")[2:]:
    os.remove(tmp)
    sys.exit("REFUSED(2): the rewrite changed more than line 2 -- nothing written")
os.chmod(tmp, os.stat(path).st_mode & 0o777)
os.replace(tmp, path)
print("MODE line 2 carries CEO-1601 (the officers Fable 5.1, the re-aim); backup %s" % bak)
