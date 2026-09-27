# FINDING 2026-09-27 hq_snocone -- does only tree_t cross from each SCRIP parser to the lower stage? A link-level audit of the seven frontends

**Lon's word, in-chat to hq_snocone, verbatim:** "So you know, check all other SCRIP parsers to verify. No information but tree_t get passed to the lower stage. Verify this is true for Raku." -- then -- "Ensure that only the tree_t gets sent/used by parser stage to the lower stage. All global structures needed at runtime, are built in the lower stage. Pass that on to the HQ-RAKU."

**Tree:** SCRIP origin `eed4e2996`, the objects actually linked: `make`'s own `RT_PIC_SRCS` (251 sources; the 17 hand-written `.s`/`.S` runtime files have no C object and were not scanned) plus `scrip_driver.o`.

**Method (the script below):** `nm` over every linked object. Per language: (A) every global a parser object DEFINES that any object outside that parser references; (B) every DATA global defined elsewhere that the parser references AND a lowerer references or defines; (C) every symbol DEFINED in a lowerer that the parser references (a parser writing into lowering); (D) every function in a third module that both the parser and a lowerer call (a registry would show here). Every hit was then read in source. Plus: `tree_t` (src/ir/ast.h) has no pointer field -- kind, a sval/ival/dval union, children, line, slen -- so the only smuggling route is a cast into sval, checked for Raku.

## VERDICT BY LANGUAGE

| language | holds? | what crosses |
|---|---|---|
| Raku | **YES** | `raku_compile` -> `tree_t **` only; the driver hands `lower_raku_stage2` only that tree. No shared data global (B=0), no call into a lowerer (C=0), no `RkItem`-family symbol outside `rk_*.c`, sval holds interned strings only. The lowerer calls one parser function, `rk_seq_is_logical_and` (lower_raku.c:692, 1311), a pure predicate on the node's own fields (TT_SEQ, n==2, v.ival==1). Flags ride in tree fields (slen bit 1 bareword, bit 2 array name). No runtime object references a Raku parser symbol. |
| Snocone | **YES** | `snocone_compile` -> tree only. |
| Rebus | **YES** | `rebus_compile` -> tree only (rebus_lower.c, in the parser directory, translates Rebus into the SNOBOL4-family tree inside the parse stage). |
| Icon | **YES** | `icon_compile` -> tree only; the driver's `icn_prune_unreachable_procs` is a tree-to-tree pass. NOTE: `icon_runtime.c` (cset_union/inter/diff/canonical, rt_icn_cset_member[_n]) is RUNTIME code filed under src/parsers/icon, called by the runtime and by bb_scan_* templates -- code misfiled, not a parse structure. |
| SNOBOL4 | **YES** for parser -> lower | `sno_parse_ast` -> tree; `stmt_to_ast` (driver/stmt_ast.c) turns the parser's STMT_t records into tree_t using the lexer's include ranges -- inside tree construction. Lowerers read only tree attributes (`stmt_attr_*`) and `stmt_src_get_file()`, the input path the DRIVER sets. NOTE for clause 2: `sno_end_lineno` (parser) is read by the driver to position INPUT after END at run time (scrip.c:1348) -- a parse fact reaching the runtime beside the tree; the END node's line could carry it. |
| **Prolog** | **NO** | (1) the dynamic-predicate set: `prolog_compile` -> `prolog_lower(PlProgram*)` (src/parsers/prolog/prolog_lower.c, `pld_mark_scan`) calls `pl_dyn_mark`, which writes `g_stage2.pl_dyn_name[] / pl_dyn_arity[] / pl_dyn_n` (lower_prolog.c:57-63, silently capped at 64); lower_prolog.c reads it back at 817, 2027-2028, 2050-2052, 2166-2167, 2187 ($db_decl goals, standing_cells). (2) lower_prolog.c:1790-1794 calls `pl_prelude_defines` (prolog_parse.c:1364), which RE-PARSES the whole prelude source on every query. (3) the parser's USER-OPERATOR table (`prolog_op_user_count/get`) and ATOM table (`prolog_atom_count/name`) are read by the driver and emitted straight into mode-4 assembly (scrip.c:556, 1631-1633), and are runtime structures built by the parser (unification.c, by_name_dispatch.c, bb_call*.cpp, bb_lit_scalar.cpp reference `prolog_atom_*`, `ATOM_DOT`, `ATOM_NIL`, `prolog_op_table_*`) -- clause 2. (4) the parse stage runs through two structures of its own, PlProgram then CODE_t, before `code_to_ast`. |
| **Pascal** | **NO** | `pas_is_nrec_idx(e)` (pascal.y:1184) answers whether a node's ADDRESS is in the parser's side table `g_pas_nrec_marks[]`; lower_pascal.c:380 and 626 ask it -- the nested-record-index fact lives beside the tree, keyed by pointer identity. (`g_trace_budget` read by the parser is a trace switch, not parse data.) |

## THE SCRIPT (`python3 audit_parser_boundary.py rt_pic_srcs.txt`; the list from `make -s -f Makefile -f <(printf 'p:\n\t@echo $(RT_PIC_SRCS)\n') p | tr ' ' '\n'`)

```python
#!/usr/bin/env python3
"""Link-level audit: what crosses from each SCRIP parser to anything else, by nm over the objects actually linked."""
import subprocess, os, sys, collections, re
ROOT = '/home/claude_snocone/SCRIP'
OBJ = ROOT + '/out/rt_pic-f65f143e2f'
srcs = [l.strip() for l in open(sys.argv[1]) if l.strip()]
objs = {}
for s in srcs:
    b = os.path.basename(s); b = re.sub(r'\.(c|cpp|cc)$', '', b)
    o = os.path.join(OBJ, b + '.o')
    if not os.path.exists(o): print('MISSING OBJECT for', s); continue
    if o in objs.values(): print('DUPLICATE BASENAME', s)
    objs[s] = o
objs[ROOT + '/src/driver/scrip.c'] = '/tmp/si_objs-home-claude_snocone-SCRIP/scrip_driver.o'
def nm(o, flag):
    out = subprocess.run(['nm', flag, o], capture_output=True, text=True).stdout
    r = {}
    for line in out.splitlines():
        p = line.split()
        if flag == '-u' and len(p) >= 2: r[p[-1]] = 'U'
        elif flag == '--defined-only' and len(p) >= 3 and p[1] in 'TDBRCVWG': r[p[2]] = p[1]
    return r
defs = {s: nm(o, '--defined-only') for s, o in objs.items()}
undf = {s: nm(o, '-u') for s, o in objs.items()}
definer = {}
for s, d in defs.items():
    for sym, t in d.items(): definer.setdefault(sym, []).append((s, t))
def group(s):
    m = re.search(r'/src/parsers/([a-z0-9]+)/', s)
    if m: return 'parser:' + m.group(1)
    m = re.search(r'/src/lower/', s)
    if m: return 'lower'
    return 'other:' + s.split('/src/')[1].split('/')[0]
LANGS = ['snobol4', 'snocone', 'icon', 'prolog', 'rebus', 'raku', 'pascal']
DATA = set('DBRCVG')
for L in LANGS:
    P = [s for s in objs if group(s) == 'parser:' + L]
    print('=' * 100); print('LANGUAGE %s: %d linked parser object(s): %s' % (L, len(P), ' '.join(os.path.basename(s) for s in P)))
    out_refs = collections.defaultdict(list)
    for s in objs:
        if s in P: continue
        for sym in undf[s]:
            for (ds, t) in definer.get(sym, []):
                if ds in P: out_refs[(sym, t, os.path.basename(ds))].append(os.path.basename(s) + '[' + group(s) + ']')
    print('(A) symbols this parser DEFINES that are referenced OUTSIDE it: %d' % len(out_refs))
    for (sym, t, ds), users in sorted(out_refs.items(), key=lambda x: (x[0][1] not in DATA, x[0][0])):
        kind = 'DATA' if t in DATA else 'code'
        print('   %-4s %-44s def %-22s <- %s' % (kind, sym, ds, ', '.join(sorted(set(users)))[:230]))
    shared = collections.defaultdict(set)
    for s in P:
        for sym in undf[s]:
            for (ds, t) in definer.get(sym, []):
                if ds not in P and t in DATA:
                    lowers = [os.path.basename(x) for x in objs if group(x) == 'lower' and sym in undf[x]] + [os.path.basename(x) for x in objs if group(x) == 'lower' and sym in defs[x]]
                    if lowers: shared[(sym, t, os.path.basename(ds))] |= set(lowers)
    print('(B) DATA globals defined elsewhere that this parser references AND a lowerer references or defines: %d' % len(shared))
    for (sym, t, ds), lows in sorted(shared.items()):
        print('   DATA %-44s def %-22s  lowerers: %s' % (sym, ds, ', '.join(sorted(lows))))
print('=' * 100)
for L in LANGS:
    P = [s for s in objs if group(s) == 'parser:' + L]
    lows = [s for s in objs if group(s) == 'lower']
    c = sorted({(sym, os.path.basename(ds), t) for s in P for sym in undf[s] for (ds, t) in definer.get(sym, []) if ds in lows})
    print('(C) %-8s parser references symbols DEFINED in a lowerer: %d  %s' % (L, len(c), '; '.join('%s(%s,%s)' % x for x in c)))
    d = collections.defaultdict(set)
    for s in P:
        for sym in undf[s]:
            for (ds, t) in definer.get(sym, []):
                if ds in P or ds in lows or t in DATA: continue
                for x in lows:
                    if sym in undf[x]: d[(sym, os.path.basename(ds))].add(os.path.basename(x))
    print('(D) %-8s code defined in a third module, called by this parser AND a lowerer: %d' % (L, len(d)))
    for (sym, ds), xs in sorted(d.items()):
        print('      %-40s def %-24s lowerers: %s' % (sym, ds, ', '.join(sorted(xs))))
```
