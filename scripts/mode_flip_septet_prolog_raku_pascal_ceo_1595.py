#!/usr/bin/env python3
# mode_flip_septet_prolog_raku_pascal_ceo_1595.py -- the MODE half of the CEO-1595 flip, run by Lon (the classifier refuses the ceo's MODE writes).
# Line 1 SEXTET -> SEPTET; line 2 gets the new block prepended; LANES: and ORDER-OF-WORK: are untouched. Backup first; refuses rather than half-writes.
# Usage: mode_flip_septet_prolog_raku_pascal_ceo_1595.py [MODE_PATH]   (default /home/resources/postoffice/MODE)
import os, shutil, sys, time
path = sys.argv[1] if len(sys.argv) > 1 else "/home/resources/postoffice/MODE"
BLOCK = (
    "# 2026-10-10 10:1x CDT ceo: ⛔⭐⭐⭐⭐ MODE SEPTET ON LON'S WORD (CEO-1595), verbatim, in-chat to the ceo: *\"Give the tasks of mining and vendoring the Prolog programs in "
    "/home/resources to another HQ seat. Which HQ do you want on the team?\"* -- the ceo chose hq_pascal. **SEVEN WORKING SEATS: the four officers (the ceo /home/claude_ceo, the cto "
    "/home/claude_cto, the cfo /home/claude_cfo, the coo /home/claude_coo), hq_prolog (/home/claude_prolog), hq_raku (/home/claude_raku) and hq_pascal (/home/claude_pascal).** The other "
    "seven HQs (hq_icon, hq_snocone, hq_snobol4, hq_templates, hq_runtime, hq_collector, hq_zetas) are STOOD DOWN with their claims and rows in place. THE SEATS: ICON -- the ceo; PROLOG -- "
    "the hq_prolog; SNOBOL4 -- the ceo; PASCAL -- the ceo; SNOCONE -- the ceo; REBUS -- the ceo; RAKU -- the hq_raku (the picker table unchanged from CEO-1591; hq_pascal's rows are "
    "ASSIGNED, never picked by language). THE ONE THING stays PROLOG AND RAKU TO 100% (CEO-1591). hq_pascal's BUSINESS: mining and vendoring the Prolog downloads under /home/resources "
    "(prolog-demos, prologs) as ProDemo entries and oracle-graded packages -- the four demos (chat80, PRESS, ELIZA, advent-of-code), the ProRosetta drivers, the trealla and XSB test "
    "suites as packages, and the puzzles and provers rows once hq_prolog lands its hakank smoke and releases them; refs cut from swipl, licences named, nothing excluded but by a Lon "
    "class. MODELS: the ceo Fable 5.1 xhigh (Lon 2026-10-10 09:5x, CEO-1594); the cto, cfo and coo Opus 5.5 xhigh; the HQs as Lon seats them. Everything else as CEO-1591 wrote it. PRIOR: "
)
raw = open(path, "rb").read()
lines = raw.split(b"\n")
if lines[0].strip() != b"SEXTET":
    sys.exit("REFUSED(2): MODE line 1 reads %r, not SEXTET -- nothing written" % lines[0][:40])
if b"CEO-1595" in lines[1]:
    sys.exit("REFUSED(2): MODE line 2 already carries CEO-1595 -- nothing written")
bak = "%s.bak-%s-pre-septet-ceo-1595" % (path, time.strftime("%Y%m%d-%H%M%S"))
shutil.copy2(path, bak)
lines[0] = b"SEPTET"
lines[1] = BLOCK.encode("utf-8") + lines[1]
out = b"\n".join(lines)
tmp = path + ".tmp-ceo-1595"
with open(tmp, "wb") as f:
    f.write(out)
new = open(tmp, "rb").read().split(b"\n")
if len(new) != len(raw.split(b"\n")) or new[2:] != raw.split(b"\n")[2:]:
    os.remove(tmp)
    sys.exit("REFUSED(2): the rewrite changed more than lines 1 and 2 -- nothing written")
os.chmod(tmp, os.stat(path).st_mode & 0o777)
os.replace(tmp, path)
print("MODE flipped to SEPTET (CEO-1595); backup %s" % bak)
