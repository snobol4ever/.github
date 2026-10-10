#!/usr/bin/env python3
# mode_flip_sextet_prolog_raku_ceo_1591.py -- the MODE half of the CEO-1591 flip, run by Lon (the classifier refuses the ceo's MODE writes).
# Line 1 QUARTET -> SEXTET; line 2 gets the new block prepended; LANES: and ORDER-OF-WORK: are untouched. Backup first; refuses rather than half-writes.
# Usage: mode_flip_sextet_prolog_raku_ceo_1591.py [MODE_PATH]   (default /home/resources/postoffice/MODE)
import os, shutil, sys, time
path = sys.argv[1] if len(sys.argv) > 1 else "/home/resources/postoffice/MODE"
BLOCK = (
    "# 2026-10-10 09:0x CDT ceo: ⛔⭐⭐⭐⭐ MODE SEXTET ON LON'S WORD (CEO-1591), verbatim, in-chat to the ceo: *\"We are in QUARTET mode. The three officers are ready and waiting. "
    "Let's continue getting Prolog and Raku at 100% like SNOBOL4 and Icon.\"* then *\"Let's also have HQ-PROLOG and HQ-RAKU join us.\"* "
    "**SIX WORKING SEATS: the four officers (the ceo /home/claude_ceo, the cto /home/claude_cto, the cfo /home/claude_cfo, the coo /home/claude_coo) and hq_prolog (/home/claude_prolog) "
    "and hq_raku (/home/claude_raku).** The other eight HQs (hq_icon, hq_pascal, hq_snocone, hq_snobol4, hq_templates, hq_runtime, hq_collector, hq_zetas) are STOOD DOWN with their "
    "claims and rows in place (the CEO-1357/1372/1396 precedent). THE SEATS: ICON -- the ceo; PROLOG -- the hq_prolog; SNOBOL4 -- the ceo; PASCAL -- the ceo; SNOCONE -- the ceo; "
    "REBUS -- the ceo; RAKU -- the hq_raku (the picker table moved first, SCRIP CEO-1591). THE ONE THING: PROLOG AND RAKU TO 100% -- every suite row of both languages, CEO-1562's "
    "order (1), the Rosetta rows included. EACH SEAT'S BUSINESS: hq_prolog its own lane (its SWI tabling claim, its rank-0 umbrella, its FREE rows); the cto the Prolog spine "
    "(setup_call_cleanup, coroutining and attributed variables, delimited continuations, the assertz reclaim), suite reds before its speed rows; the cfo the Prolog breadth (the SWI "
    "library modules, the 128 GNU builtins), its two non-Prolog claims waiting in place; hq_raku its own lane (RakRungs, RakBench, Roast, the Raku roads that die on CEO-1576's "
    "named bombs); the coo stays THE ONE TESTING OFFICER (LANES names the coo for every language), Prolog and Raku passes first, then the GNU source drivers; the ceo assigns, "
    "arbitrates and keeps its CEO-1588 half (the Prolog download sets' drivers). The Pascal downloads of CEO-1588 wait. ORDER OF WORK unchanged (CEO-1562). PRIOR: "
)
raw = open(path, "rb").read()
lines = raw.split(b"\n")
if lines[0].strip() != b"QUARTET":
    sys.exit("REFUSED(2): MODE line 1 reads %r, not QUARTET -- nothing written" % lines[0][:40])
if b"CEO-1591" in lines[1]:
    sys.exit("REFUSED(2): MODE line 2 already carries CEO-1591 -- nothing written")
bak = "%s.bak-%s-pre-sextet-ceo-1591" % (path, time.strftime("%Y%m%d-%H%M%S"))
shutil.copy2(path, bak)
lines[0] = b"SEXTET"
lines[1] = BLOCK.encode("utf-8") + lines[1]
out = b"\n".join(lines)
tmp = path + ".tmp-ceo-1591"
with open(tmp, "wb") as f:
    f.write(out)
new = open(tmp, "rb").read().split(b"\n")
if len(new) != len(raw.split(b"\n")) or new[2:] != raw.split(b"\n")[2:]:
    os.remove(tmp)
    sys.exit("REFUSED(2): the rewrite changed more than lines 1 and 2 -- nothing written")
os.chmod(tmp, os.stat(path).st_mode & 0o777)
os.replace(tmp, path)
print("MODE flipped to SEXTET (CEO-1591); backup %s" % bak)
