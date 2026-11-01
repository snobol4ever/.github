#!/usr/bin/env python3
# hdr7c_harness.py <harness/scripts> -- step 7, the third harness pass: the instrument reads its dependency lists from the compiler, not from the .d files.
# WHY: the build cache (util_build_cache.sh FORMAT 2) carries the producer root's .d files into every root that fetches; a .d is rewritten only by a
# LOCAL compile of its unit, so on a cache-using root it is as old as that root's last local compile of the unit -- 45 of this root's 308 named
# ir/IR.h, ir/SM.h, ir/pin_va.h, headers deleted weeks ago, and the ceiling gate, BLOCKING since the step-7 landing, read 33 fan-in raises on a tree
# whose worktree (pristine .d) read 0. The tree as the compiler sees it: `make -B -n build-all` lists the 297 compile lines with their flags
# (0.5 s), and `gcc -MM <flags> <unit>` answers each unit's includes (30-60 ms each, eight at a time). The .d reader stays for the gate's fixtures (--obj) and --from-d.
import sys, re
H = sys.argv[1].rstrip('/') + '/'
p = H + 'util_header_fanin.py'; t = open(p).read()
old = """class Tree:
    def __init__(self, root, obj, min_units):
        self.root, self.obj = os.path.abspath(root), obj
        dfiles = []
        for base in (obj, os.path.join(self.root, 'out')):
            for dp, dn, fn in os.walk(base):
                dfiles += [os.path.join(dp, f) for f in fn if f.endswith('.d')]
        if len(dfiles) < min_units:
            print('REFUSE(2): %d .d files under %s and %s/out, fewer than %d: build the tree first' % (len(dfiles), obj, self.root, min_units), file=sys.stderr)
            sys.exit(2)
        self.unit_deps = collections.defaultdict(set)
        for d in dfiles:
            src, deps = self.read_d(d)
            if src:
                self.unit_deps[src].update(deps)
"""
new = """class Tree:
    def __init__(self, root, obj, min_units, from_d=False):
        self.root, self.obj = os.path.abspath(root), obj
        self.unit_deps = collections.defaultdict(set)
        if from_d:
            dfiles = []
            for base in (obj, os.path.join(self.root, 'out')):
                for dp, dn, fn in os.walk(base):
                    dfiles += [os.path.join(dp, f) for f in fn if f.endswith('.d')]
            if len(dfiles) < min_units:
                print('REFUSE(2): %d .d files under %s and %s/out, fewer than %d: build the tree first' % (len(dfiles), obj, self.root, min_units), file=sys.stderr)
                sys.exit(2)
            for d in dfiles:
                src, deps = self.read_d(d)
                if src:
                    self.unit_deps[src].update(deps)
        else:
            self.deps_from_compiler(min_units)
"""
assert t.count(old) == 1; t = t.replace(old, new)
old2 = """    def read_d(self, path):
        text = read(path).replace('\\\\\\n', ' ')
"""
new2 = """    def compile_lines(self):
        \"\"\"[(compiler, flags, source)] from `make -B -n build-all` in the root: every line with a -c, its -I/-D/-std/-finput-charset/-include flags.\"\"\"
        r = subprocess.run(['make', '-B', '-n', 'build-all'], cwd=self.root, capture_output=True, text=True)
        if r.returncode != 0:
            print('REFUSE(2): make -B -n build-all failed in %s: %s' % (self.root, (r.stderr or r.stdout).strip().splitlines()[-1:] or ''), file=sys.stderr)
            sys.exit(2)
        units = []
        for line in r.stdout.splitlines():
            if ' -c ' not in line:
                continue
            toks = shlex.split(line)
            if toks and toks[0] == 'ccache':
                toks = toks[1:]
            if '-c' not in toks:
                continue
            src = toks[toks.index('-c') + 1]
            flags, i = [], 1
            while i < len(toks):
                x = toks[i]
                if x in ('-I', '-D', '-U', '-include', '-isystem', '-iquote', '-x') and i + 1 < len(toks):
                    flags += [x, toks[i + 1]]; i += 2; continue
                if x.startswith(('-I', '-D', '-U', '-std=', '-finput-charset', '-include', '-isystem', '-iquote')):
                    flags.append(x)
                i += 1
            units.append((toks[0], flags, src))
        return units

    def deps_from_compiler(self, min_units):
        \"\"\"The tree as the compiler sees it: gcc -MM per compile line (eight at a time). The .d files are not read: the build cache carries the producer
        root's .d files into every root that fetches, and a .d is rewritten only by a local compile of its unit, so on a cache-using root it names the
        headers of that root's last local compile (step 7, 2026-10-31: 45 of 308 named headers deleted weeks ago).\"\"\"
        units = self.compile_lines()
        if len(units) < min_units:
            print('REFUSE(2): make -B -n build-all lists %d compile lines in %s, fewer than %d: not a SCRIP root, or the Makefile is broken' % (len(units), self.root, min_units), file=sys.stderr)
            sys.exit(2)
        def one(u):
            cc, flags, src = u
            r = subprocess.run([cc, '-MM'] + flags + [src], cwd=self.root, capture_output=True, text=True)
            return src, r.returncode, r.stdout, r.stderr
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            results = list(ex.map(one, units))
        failed = [(s, e.strip().splitlines()[:1]) for s, rc, o, e in results if rc != 0]
        if failed:
            print('REFUSE(2): %d of %d units do not preprocess (gcc -MM): %s' % (len(failed), len(results), '; '.join('%s: %s' % (self.rel(s) or s, (e or [''])[0][:120]) for s, e in failed[:3])), file=sys.stderr)
            sys.exit(2)
        for src, rc, o, e in results:
            s, deps = self.parse_d(o)
            if s:
                self.unit_deps[s].update(deps)

    def read_d(self, path):
        return self.parse_d(read(path))

    def parse_d(self, text):
        text = text.replace('\\\\\\n', ' ')
"""
assert t.count(old2) == 1, t.count(old2); t = t.replace(old2, new2)
old3 = "import argparse, collections, os, re, sys"
assert t.count(old3) == 1, 'import line'; t = t.replace(old3, "import argparse, collections, concurrent.futures, os, re, shlex, subprocess, sys")
old4 = "    ap.add_argument('--obj')\n"
new4 = "    ap.add_argument('--obj', help='read the .d files under this directory and out/ instead of asking the compiler (the fixtures); implies --from-d')\n    ap.add_argument('--from-d', action='store_true', help='read the .d files under the objdir and out/ (the old reader); the default asks make -B -n build-all and gcc -MM')\n"
assert t.count(old4) == 1; t = t.replace(old4, new4)
old5 = "    t = Tree(root, a.obj or default_obj(root), a.min_units)"
new5 = "    t = Tree(root, a.obj or default_obj(root), a.min_units, from_d=a.from_d or a.obj is not None)"
assert t.count(old5) == 1; t = t.replace(old5, new5)
old6 = "#   util_header_fanin.py --unused          per unit the direct includes none of whose declarations the unit names, then \"summary unused=N\"\n"
new6 = old6 + "#   util_header_fanin.py --from-d          read the .d files under the objdir and out/ instead of asking the compiler (the fixtures pass --obj, which implies it); the\n#                                          default runs make -B -n build-all and gcc -MM per unit: a cache-using root's .d files are the producer's and stale (step 7)\n"
assert t.count(old6) == 1; t = t.replace(old6, new6)
open(p, 'w').write(t); print('  util_header_fanin.py: the dependency lists come from the compiler; --from-d and --obj keep the .d reader')
g = H + 'test_gate_no_header_reaches_more_units_than_its_users.sh'; t = open(g).read()
old7 = """if [ "$ok9" = 1 ]; then echo "  ok   ARM 9:"""
new7 = """ok10=1
cm="$T/cm"; mkdir -p "$cm/src" "$cm/out"
printf '#ifndef A_H\\n#define A_H\\nint a_fn(int);\\n#endif\\n' > "$cm/src/a.h"
printf '#ifndef DEAD_H\\n#define DEAD_H\\nint dead_fn(int);\\n#endif\\n' > "$cm/src/dead.h"
printf '#include "a.h"\\nint a(void) { return a_fn(1); }\\n' > "$cm/src/a.c"
printf '#include "a.h"\\nint b(void) { return a_fn(2); }\\n' > "$cm/src/b.c"
printf 'build-all: a.o b.o\\na.o: src/a.c\\n\\tgcc -I src -c src/a.c -o a.o\\nb.o: src/b.c\\n\\tgcc -I src -c src/b.c -o b.o\\n' > "$cm/Makefile"
printf 'a.o: src/a.c src/a.h src/dead.h\\n' > "$cm/out/a.d"
printf 'b.o: src/b.c src/a.h src/dead.h\\n' > "$cm/out/b.d"
cfan() { python3 -I "$FAN" --root "$cm" --min-units 1 --base-file "$T/empty_base.tsv" --inline-file "$T/empty_inline.tsv" --baseline-file "$cm/baseline.tsv" "$@"; }
cfan 2>&1 | awk -F'\\t' '$7 == "dead.h" { f = 1 } END { exit f }' || { ok10=0; echo "         the stale .d files under out/ were read: dead.h has a fan-in though no unit includes it"; }
cfan 2>&1 | awk -F'\\t' '$7 == "a.h" && $1 == 2 { f = 1 } END { exit !f }' || { ok10=0; echo "         a.h does not read fan-in 2 from the compiler's own dependency lists (make -B -n build-all, gcc -MM)"; }
cfan --from-d --obj "$cm/out" 2>&1 | awk -F'\\t' '$7 == "dead.h" && $1 == 2 { f = 1 } END { exit !f }' || { ok10=0; echo "         the .d reader does not read the planted stale .d: the control is no control"; }
if [ "$ok10" = 1 ]; then echo "  ok   ARM 10: the dependency lists come from the compiler (make -B -n build-all, gcc -MM per unit), and a stale .d under out/ naming a dead header is not read; the .d reader (--from-d) still reads it"
else echo "  RED  ARM 10: the instrument reads the .d files, which the build cache carries from the producer's root"; fail=1; fi
if [ "$ok9" = 1 ]; then echo "  ok   ARM 9:"""
assert t.count(old7) == 1; t = t.replace(old7, new7)
old8 = "# DECLARED RULING (reporting) at step 1a; BLOCKING since step 7 (2026-10-31, the cto: every arm read 0 and the baseline was lowered to that tree)."
new8 = "# DECLARED RULING (reporting) at step 1a; BLOCKING since step 7 (2026-10-31, the cto: every arm read 0 and the baseline was lowered to that tree). THE DEPENDENCY LISTS COME FROM THE COMPILER (ARM 10, the same night): make -B -n build-all names the units and their flags, gcc -MM answers each unit's includes; the .d files are not read, because the build cache carries the producer root's .d files and a cache-using root's are as old as its last local compile of each unit (45 of 308 named deleted headers)."
assert t.count(old8) == 1; t = t.replace(old8, new8)
open(g, 'w').write(t); print('  the gate: ARM 10 (the stale .d control) and the header note')
