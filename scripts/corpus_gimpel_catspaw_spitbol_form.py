#!/usr/bin/env python3
"""Re-vendor corpus/packages/snobol4/gimpel as Catspaw's (Mark Emmer's) SPITBOL form, verbatim, under lower-case names.

Lon 2026-09-27, in-chat to the ceo, verbatim: "Use the *.inc names exclusively. Ensure we have the SPITBOL dialect from the Mark
Emmer's distribution, and not the SNOBOL4 dialect." (CEO-1319) -- and, refined: "So we should vendor all SPITBOL-form files
verbatum, with only uppercase keywords/reserved-words for SCRIP acceptance." and "And any other edit required to get running under
Linux." (CEO-1320). The checker is SCRIP scripts/util_gimpel_is_the_catspaw_spitbol_form.py; this tool builds what it checks.

WHAT IT DOES, in one --apply (the dry run prints every step and an `owed:` line):
  FORM     every file of /home/resources/gimpel/SPITBOL (README* aside) is git-mv'd from its vendored counterpart to its own name
           LOWER-CASED and rewritten with the form's bytes, CR and ^Z dropped. The counterpart is the one vendored library or program
           of the same stem (NAME.sno | NAME.INC | NAME.inc) or data file (NAME.IN), except the four the fleet split or replaced:
           INFINIP_lib.INC -> infinip.inc, INFINIP.sno (the SNOBOL4+ program) -> infinip.spt, RSEASON_lib.INC -> rseason.inc and
           RSEASON.sno -> rseason.spt.
  EDITS    the edits EDITS.tsv declares, applied and written there with their vendored line numbers (the checker's schema):
             RESERVED_UPPER  infinip.spt: every SPITBOL reserved word or &keyword written lower-case outside a string, upper-cased
             LINUX           infinip.spt's `-include` control line (sbl -bf ignores a lower-case control line; measured ERROR 022);
                             frsort.inc's "stringout.inc" -> "stringou.inc" (the DOS 8.3 name the form's own file carries); timer.inc
                             and timegc.inc's "resolution.inc" is left: their output is wall-clock timing, ungradable if they run
  NOTHING  every other library, program or data file is deleted (BAL.sno and PHRASES.sno are the SNOBOL4 form's alone,
           stringout.inc was our alias), and so is every driver whose library leaves (BAL_driver).
  DRIVERS  every NAME_driver.* is git-mv'd to its name LOWER-CASED, so a driver's stem is its library's stem on a case-sensitive file
           system; its -INCLUDE lines are resolved as the lexer resolves them (its own directory, then corpus/include) and rewritten
           to the renamed file, and every whole-token old file name in it (a comment, a companion like MFREAD_driver.d1) is renamed.
           The two stems the form ships twice keep the _lib convention: x_driver drives the program x.spt, x_lib_driver the library
           x.inc (infinip, rseason).
  RECORDS  ALL.csv's entry and origin columns follow the drivers; the package's .tsv/.txt/.md records have every whole-token old
           file name renamed, and a deleted driver's ALL.csv row is dropped.

Usage:  corpus_gimpel_catspaw_spitbol_form.py --dry-run | --apply   [--root CORPUS] [--form DIR]
"""
import argparse, collections, os, re, subprocess, sys

FORM_DEFAULT = "/home/resources/gimpel/SPITBOL"
PKG = os.path.join("packages", "snobol4", "gimpel")
SPLIT = {"INFINIP.INC": "INFINIP_lib.INC", "INFINIP.SPT": "INFINIP.sno", "RSEASON.INC": "RSEASON_lib.INC", "RSEASON.SPT": "RSEASON.sno"}
SIDE = re.compile(r"^(ALL\..*|.*\.tsv|README\.md|PROVENANCE\.md|\.gitkeep)$")
DRV = re.compile(r"^([A-Za-z0-9_]+)_driver\.([A-Za-z0-9]+)$")
RECORD_EXT = (".tsv", ".txt", ".md")
REF_B = re.compile(rb'''^(-INCLUDE\s+(["']))(.+?)(\2)''', re.I | re.M)   # a control line, column 1 -- never a comment's quotation of one
# the checker's reserved words (util_gimpel_is_the_catspaw_spitbol_form.py RES) and its tokenizer, so an edit made here is one it accepts
RES = set('''OUTPUT INPUT TERMINAL PUNCH DEFINE SIZE DUPL TRIM IDENT DIFFER EQ NE LT GT LE GE SPAN BREAK BREAKX ANY NOTANY LEN POS
RPOS TAB RTAB ARB BAL REM FAIL FENCE SUCCEED ABORT CONVERT DATATYPE ARRAY TABLE DATA ITEM OPSYN APPLY SUBSTR REPLACE REVERSE LPAD RPAD
INTEGER REMDR RETURN FRETURN NRETURN END ENDFILE DETACH REWIND EVAL CODE LOAD UNLOAD CHAR LGT LEQ LNE LGE LLE LLT ARBNO COPY FIELD
PROTOTYPE SORT RSORT EXP LN SQRT SIN COS TAN ATAN CHOP HOST DATE TIME COLLECT DUMP SETEXIT STOPTR TRACE EXIT BACKSPACE CONTINUE
SCONTINUE VALUE CLEAR NUMERIC REAL STRING PATTERN NAME EXPRESSION'''.split())
TOK = re.compile(r"'[^']*'|\"[^\"]*\"|&?[A-Za-z][A-Za-z0-9_.]*|.")
# timer.inc and timegc.inc name "resolution.inc" (RESOLUTI.INC) too, and are deliberately NOT edited: their whole output is wall-clock
# timing that never repeats (the cfo's 2026-09-07 call, kept), so an edit that lets them run buys a red that no grade can settle.
LINUX_SUBS = {"frsort.inc": [(b'"stringout.inc"', b'"stringou.inc"')]}
LINUX_WHY = {"frsort.inc": "the DOS 8.3 name: the form includes stringout.inc and ships the file as STRINGOU.INC; on Linux the long name is another file",
             "infinip.spt": "sbl -bf folds no case, and it ignores a lower-case -include control line (measured: the include is skipped and the first call dies ERROR 022); the form's DOS SPITBOL folded case"}


def refuse(msg):
    print("REFUSED(2): " + msg, file=sys.stderr)
    sys.exit(2)


def upper_reserved(line):
    """Upper-case every reserved word or &keyword written lower-case outside a string; (new line, tokens changed)."""
    out, n = [], 0
    for t in TOK.findall(line):
        if t[:1] not in "'\"" and t != t.upper() and (t.upper() in RES or (t.startswith("&") and len(t) > 1)):
            out.append(t.upper()); n += 1
        else:
            out.append(t)
    return "".join(out), n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--form", default=FORM_DEFAULT)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--apply", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root or (os.path.join(os.environ["S4E_HOME"], "corpus") if os.environ.get("S4E_HOME") else
                                      os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "corpus")))
    P = os.path.join(root, PKG)
    if not os.path.isdir(P) or not os.path.isdir(os.path.join(root, "include")):
        refuse("%s is not a corpus with a gimpel package" % root)
    if not os.path.isdir(a.form):
        refuse("no Catspaw SPITBOL form at %s" % a.form)
    form = sorted(f for f in os.listdir(a.form) if not f.upper().startswith("README"))
    vend = sorted(os.listdir(P))
    print("root: %s\nform: %s (%d files)" % (root, a.form, len(form)))

    # ---- FORM: each form file's vendored counterpart
    moves = {}                       # old vendored name -> new lower-case name (library, program, data)
    already = []                     # form files already vendored under their lower-cased name
    libs = [f for f in vend if not SIDE.match(f) and not DRV.match(f)]
    for f in form:
        new = f.lower()
        if new in libs:                                       # already vendored under its own lower-cased name (a re-run)
            old = new
        elif f in SPLIT:
            old = SPLIT[f]
        else:
            base, ext = f.rsplit(".", 1)
            if ext.upper() == "IN":
                c = [v for v in libs if v.lower() == new]
            else:
                c = [v for v in libs if v.rsplit(".", 1)[0].lower() == base.lower() and v.rsplit(".", 1)[-1].lower() in ("sno", "inc", "spt")
                     and v not in SPLIT.values()]
            if len(c) > 1:
                refuse("%s has %d vendored counterparts: %s" % (f, len(c), c))
            old = c[0] if c else None
        if old is None:
            refuse("%s has no vendored counterpart" % f)
        if old not in vend:
            refuse("%s's counterpart %s is not vendored" % (f, old))
        if old == new:
            already.append(new)
        moves[old] = new
    gone = [f for f in libs if f not in moves]
    print("form files mapped: %d (%d already lower-case)" % (len(moves), len(already)))
    print("library/program/data files not in the form, deleted: %s" % " ".join(gone))

    # ---- DRIVERS
    stems_after = {n.rsplit(".", 1)[0] for n in moves.values()}
    dmoves, dgone = {}, []
    for f in vend:
        m = DRV.match(f)
        if not m:
            continue
        stem = m.group(1).lower()
        lib = stem[:-4] if stem.endswith("_lib") and stem not in stems_after else stem
        if lib not in stems_after:
            dgone.append(f)
        else:
            dmoves[f] = f.lower()
    print("drivers and companions lower-cased: %d; deleted with their library: %s" % (len(dmoves), " ".join(dgone)))
    clash = [n for n, k in collections.Counter(list(moves.values()) + list(dmoves.values())).items() if k > 1]
    if clash:
        refuse("two files would take one name: %s" % clash)

    renamed = dict(moves); renamed.update(dmoves)            # every old name -> new name in the package
    old_names = sorted((o for o in renamed if renamed[o] != o), key=len, reverse=True)

    def resolve(target):
        for d in (P, os.path.join(root, "include")):
            c = os.path.normpath(os.path.join(d, target))
            if os.path.isfile(c):
                return c
        return None

    # ---- the new bytes of every form file, with the declared edits
    data, edits = {}, []
    for f in form:
        new = f.lower()
        raw = open(os.path.join(a.form, f), "rb").read().replace(b"\r", b"").replace(b"\x1a", b"")
        if new in LINUX_SUBS:
            lines = raw.split(b"\n"); hit = []
            for i, l in enumerate(lines):
                for o, n in LINUX_SUBS[new]:
                    if o in l:
                        lines[i] = l.replace(o, n); hit.append(i + 1)
            if not hit:
                refuse("%s: no line carries the LINUX edit's text" % new)
            raw = b"\n".join(lines)
            edits.append((new, "LINUX", hit, LINUX_WHY[new]))
        if new == "infinip.spt":
            lines = raw.decode("latin-1").split("\n"); up, ntok, inc = [], 0, []
            for i, l in enumerate(lines):
                if l.startswith("-include"):
                    lines[i] = "-INCLUDE" + l[len("-include"):]; inc.append(i + 1); continue
                if l.startswith("*"):
                    continue
                nl, k = upper_reserved(l)
                if k:
                    lines[i] = nl; up.append(i + 1); ntok += k
            raw = "\n".join(lines).encode("latin-1")
            edits.append((new, "RESERVED_UPPER", up, "%d tokens: every SPITBOL reserved word and &keyword this file writes lower-case, upper-cased -- sbl -bf and SCRIP both fold no case (Lon 2026-09-27, CEO-1320)" % ntok))
            edits.append((new, "LINUX", inc, LINUX_WHY[new]))
        data[new] = raw

    # ---- driver rewrites: -INCLUDE resolved and renamed; whole-token old names renamed
    tok_re = re.compile(rb"(?<![A-Za-z0-9_./])(" + b"|".join(re.escape(o.encode()) for o in old_names) + rb")(?![A-Za-z0-9_])") if old_names else None
    drv_text, unresolved = {}, collections.Counter()
    # a COMMENT naming a library or program by an older spelling (NAME.sno, NAME.SNO, NAME.INC, NAME_lib.sno) names the shipped file
    ship = {n for n in moves.values() if n.endswith((".inc", ".spt"))}
    cmt_re = re.compile(rb"(?<![A-Za-z0-9_./])([A-Za-z][A-Za-z0-9_]*)\.(sno|SNO|INC|inc|SPT|spt)(?![A-Za-z0-9_])")

    def cmt_name(m):
        stem, ext = m.group(1).decode().lower(), m.group(2).decode().lower()
        if stem.endswith("_driver"):
            return m.group(0)
        if stem.endswith("_lib") and stem[:-4] + ".inc" in ship and stem + ".inc" not in ship:
            return (stem[:-4] + ".inc").encode()
        pref = {"inc": (".inc", ".spt"), "spt": (".spt", ".inc"), "sno": (".spt", ".inc")}[ext]
        for e in pref:
            if stem + e in ship:
                return (stem + e).encode()
        return m.group(0)
    for old, new in dmoves.items():
        if not old.endswith(".sno"):
            continue
        raw = open(os.path.join(P, old), "rb").read()

        def sub(m):
            t = m.group(3).decode("latin-1").strip()
            hit = resolve(t)
            if hit is None or os.path.dirname(hit) != P:
                if hit is None:
                    unresolved[old + " -> " + t] += 1
                return m.group(0)
            b = os.path.basename(hit)
            if b in renamed:
                return m.group(1) + t[: len(t) - len(t.rsplit("/", 1)[-1])].encode("latin-1") + renamed[b].encode("latin-1") + m.group(4)
            if b in gone:
                refuse("%s includes %s, which leaves the package" % (old, b))
            return m.group(0)

        txt = REF_B.sub(sub, raw)
        if tok_re:
            txt = tok_re.sub(lambda m: renamed[m.group(1).decode()].encode(), txt)
        txt = b"\n".join(cmt_re.sub(cmt_name, l) if l.startswith(b"*") else l for l in txt.split(b"\n"))
        drv_text[new] = txt
    for k in sorted(unresolved):
        print("   unresolved include (left as written): " + k)

    # ---- records
    rec_text = {}
    for f in vend:
        if not SIDE.match(f) or f == "ALL.csv" or not f.endswith(RECORD_EXT):
            continue
        raw = open(os.path.join(P, f), "rb").read()
        txt = tok_re.sub(lambda m: renamed[m.group(1).decode()].encode(), raw) if tok_re else raw
        if txt != raw:
            rec_text[f] = txt
    csv_old = open(os.path.join(P, "ALL.csv"), encoding="utf-8").read().split("\n")
    csv_new, dropped = [], []
    gone_stems = {DRV.match(d).group(1) for d in dgone if d.endswith(".sno")}
    for l in csv_old:
        c = l.split(",")
        if len(c) > 2 and c[1].endswith("_driver"):
            if c[1][: -len("_driver")] in gone_stems:
                dropped.append(c[1]); continue
            c[1] = c[1].lower(); c[2] = c[2][: len(c[2]) - len(c[1])] + c[1] if c[2].lower().endswith(c[1]) else c[2]
            l = ",".join(c)
        csv_new.append(l)

    print("EDITS: " + "; ".join("%s %s lines %s" % (f, k, ",".join(map(str, ls))) for f, k, ls, _ in edits))
    print("drivers rewritten: %d; records renamed: %s; ALL.csv rows re-keyed, dropped: %s" % (len(drv_text), " ".join(sorted(rec_text)), " ".join(dropped)))
    owed_moves = sum(1 for o, n in renamed.items() if o != n)
    owed_data = sum(1 for n, b in data.items() if not os.path.isfile(os.path.join(P, n)) or open(os.path.join(P, n), "rb").read() != b)
    print("owed: %d rename(s), %d form file(s) to write, %d deletion(s), %d driver rewrite(s), %d record(s)"
          % (owed_moves, owed_data, len(gone) + len(dgone), sum(1 for n, t in drv_text.items() if not os.path.isfile(os.path.join(P, n)) or open(os.path.join(P, n), "rb").read() != t),
             len(rec_text)))
    if a.dry_run:
        return 0

    def git(*args):
        subprocess.run(["git", "-C", root] + list(args), check=True, stdout=subprocess.DEVNULL)
    for f in gone + dgone:
        git("rm", "-q", os.path.join(PKG, f))
    for o, n in renamed.items():
        if o != n:
            git("mv", os.path.join(PKG, o), os.path.join(PKG, n))
    for n, b in data.items():
        open(os.path.join(P, n), "wb").write(b)
    for n, t in drv_text.items():
        open(os.path.join(P, n), "wb").write(t)
    for f, t in rec_text.items():
        open(os.path.join(P, f), "wb").write(t)
    open(os.path.join(P, "ALL.csv"), "w", encoding="utf-8").write("\n".join(csv_new))
    with open(os.path.join(P, "EDITS.tsv"), "w", encoding="utf-8") as fh:
        fh.write("# EDITS.tsv -- every line of the vendored gimpel package that differs from Catspaw's SPITBOL form (/home/resources/gimpel/SPITBOL),\n"
                 "# CR and ^Z aside. Lon 2026-09-27 (CEO-1320): verbatim, with only upper-case reserved words for SCRIP acceptance, and any other\n"
                 "# edit Linux requires. Checked mechanically by SCRIP scripts/util_gimpel_is_the_catspaw_spitbol_form.py.\n"
                 "# file<TAB>class<TAB>lines<TAB>reason\n")
        for f, k, ls, why in edits:
            fh.write("%s\t%s\t%s\t%s\n" % (f, k, ",".join(map(str, ls)), why))
    git("add", "-A", PKG)
    print("applied: %d renames, %d form files written, %d deletions, %d drivers rewritten, %d records, EDITS.tsv %d rows"
          % (owed_moves, len(data), len(gone) + len(dgone), len(drv_text), len(rec_text), len(edits)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
