#!/usr/bin/env python3
# hdr6b1.py -- headers step 6 B1 (ARCH-HEADER-SPLIT section 4 row driver_private.h, section 5 row 6; CEO-2032; the cto 2026-10-31):
# driver_private.h is split BY DEFINING UNIT, measured with nm over the built objects: a prototype goes to the interface header of the
# unit that defines it (driver_globals.h, driver_data.h, driver_label.h, driver_call.h, driver_hooks.h; real_str is already in string_ops.h,
# try_call_builtin_by_name joins by_name_dispatch.h, ir_print_node joins ir/ast.h), a variable with its definer, a record with the
# functions that take it; a prototype nothing defines is deleted; the two inline bodies nothing calls are deleted (R3). Every includer
# replaces its one include by the new headers it names plus only those old passengers it names, in the old relative order (R5: a
# static inline is emitted where its header is first reached).     hdr6b1.py <SCRIP root> [--apply]
import os, re, sys, subprocess, glob, collections
R = os.path.abspath(sys.argv[1]); SRC = R + '/src/'; APPLY = '--apply' in sys.argv
HS = os.path.abspath(os.path.join(R, '..', 'harness', 'scripts')); sys.path.insert(0, HS); import util_header_fanin as F
def rd(p): return open(p, errors='surrogateescape').read()
def wr(p, t): open(p, 'w', errors='surrogateescape').write(t)
WORD = re.compile(r'[A-Za-z_\u0080-￿][A-Za-z_0-9\u0080-￿]*')
def toks(text): return set(WORD.findall(F.strip_strings(F.strip_comments(text))))
INCDIRS = ['', 'ir/', 'lower/', 'emitter/', 'runtime/core/', 'runtime/builtins/', 'runtime/', 'runtime/rt/', 'parsers/snobol4/', 'parsers/raku/', 'optimizer/', 'templates/bb/', 'templates/xa/', 'templates/x86/']
def resolve(includer_rel, inc):
    own = os.path.normpath(os.path.join(os.path.dirname(includer_rel), inc))
    if os.path.isfile(SRC + own): return own
    for d in INCDIRS:
        c = os.path.normpath(d + inc)
        if os.path.isfile(SRC + c): return c
    return None
H = 'driver/driver_private.h'; L = rd(SRC + H).split('\n')
# --- 1. the items -----------------------------------------------------------------------------------------------------------------------------------------
items = []   # (kind, name, [lines])  kind: inc sys ext proto macro block inline other
i = 0
while i < len(L):
    s = L[i].strip()
    if s.startswith('#include'):
        m = re.match(r'#include\s+([<"])([^>"]+)[>"]', s); items.append(('sys' if m.group(1) == '<' else 'inc', m.group(2), [L[i]]))
    elif s.startswith('typedef struct') and s.endswith('{'):
        j = i
        while not re.match(r'^\}\s*\w+\s*;', L[j].strip()): j += 1
        items.append(('block', re.match(r'^\}\s*(\w+)\s*;', L[j].strip()).group(1), L[i:j + 1])); i = j
    elif s.startswith('static inline'):
        j = i; depth = L[i].count('{') - L[i].count('}')
        while depth > 0: j += 1; depth += L[j].count('{') - L[j].count('}')
        items.append(('inline', re.search(r'\b(\w+)\s*\(', s).group(1), L[i:j + 1])); i = j
    elif s.startswith('typedef struct {') and s.endswith(';'):
        items.append(('block', re.search(r'\}\s*(\w+)\s*;$', s).group(1), [L[i]]))
    elif s.startswith('#define'):
        items.append(('macro', re.match(r'#define\s+(\w+)', s).group(1), [L[i]]))
    elif s.startswith('extern') and '(' not in s:
        items.append(('ext', re.search(r'\b(\w+)\s*(?:\[[^\]]*\])?\s*;$', s).group(1), [L[i]]))
    elif s.endswith(';') and '(' in s and not s.startswith('#'):
        items.append(('proto', re.search(r'\b(\w+)\s*\(', s).group(1), [L[i]]))
    else:
        items.append(('other', s, [L[i]]))
    i += 1
# --- 2. the definers ---------------------------------------------------------------------------------------------------------------------------------------
objdir = '/tmp/si_objs' + R.replace('/', '-')
objs = sorted(glob.glob(R + '/out/rt_pic-*/*.o')) + glob.glob(objdir + '/scrip_driver.o')
assert objs, 'no objects under ' + R
nmout = subprocess.run(['nm', '-A', '--defined-only'] + objs, capture_output=True, text=True).stdout
definer = {}
for ln in nmout.split('\n'):
    m = re.match(r'^(\S+?\.o):[0-9a-f]* ([TtDdBbRr]) (\S+)$', ln)
    if m: definer.setdefault(m.group(3), os.path.basename(m.group(1))[:-2])
NEW = {'driver_globals': 'driver/driver_globals.h', 'driver_data': 'driver/driver_data.h', 'driver_label': 'driver/driver_label.h', 'driver_call': 'driver/driver_call.h', 'driver_hooks': 'driver/driver_hooks.h'}
EXISTING = {'string_ops': 'runtime/string_ops.h', 'by_name_dispatch': 'runtime/by_name_dispatch.h', 'ast_print': 'ir/ast.h'}
BLOCK_HOME = {'fh_slot_t': 'driver/driver_globals.h', 'InitSlot': 'driver/driver_call.h', 'InitEnt': 'driver/driver_call.h', 'DatType': 'driver/driver_data.h'}
MACRO_HOME = {'g_fh': 'driver/driver_globals.h', 'FH_N': 'driver/driver_globals.h', 'init_tab': 'driver/driver_call.h'}
dest = collections.OrderedDict((h, []) for h in NEW.values()); appended = collections.defaultdict(list); deleted = []; carried = []
src_tokens = {}
def used_anywhere(name):
    for f in glob.glob(SRC + '**/*', recursive=True):
        if f.endswith(('.c', '.cpp', '.h', '.inc')) and f != SRC + H:
            if f not in src_tokens: src_tokens[f] = toks(rd(f))
            if name in src_tokens[f]: return True
    return False
first_pos = {}
for k, (kind, name, ls) in enumerate(items):
    if kind in ('inc', 'sys'): carried.append((k, kind, name)); continue
    if kind == 'other': continue
    home = None
    if kind in ('proto', 'ext'):
        d = definer.get(name)
        if d in NEW: home = NEW[d]
        elif d in EXISTING:
            ex = EXISTING[d]
            if name in toks(rd(SRC + ex)): deleted.append((name, 'already declared in ' + ex))
            else: appended[ex].append(ls[0].replace('extern ', '', 1)); first_pos.setdefault(ex, k)
            continue
        elif d is None: deleted.append((name, 'defined nowhere')); continue
        else: raise SystemExit('unmapped definer %s for %s' % (d, name))
    elif kind == 'block': home = BLOCK_HOME[name]
    elif kind == 'macro':
        if name == os.path.basename(H).upper().replace('.', '_'): continue
        if name in MACRO_HOME: home = MACRO_HOME[name]
        elif not used_anywhere(name): deleted.append((name, 'a macro nothing uses')); continue
        else: raise SystemExit('macro %s is used and has no home' % name)
    elif kind == 'inline':
        if used_anywhere(name): raise SystemExit('inline %s is used; it must be compiled, not deleted' % name)
        deleted.append((name, 'an inline body nothing calls (R3)')); continue
    dest[home].append((name, ls)); first_pos.setdefault(home, k)
# --- 3. the new headers ------------------------------------------------------------------------------------------------------------------------------------
TYPE_HDR = [('FILE', '<stdio.h>'), ('size_t', '<stddef.h>'), ('int64_t', '<stdint.h>'), ('cv_t', '"ir/ct_vec.h"'), ('DESCR_t', '"ir/descr.h"'), ('tree_t', '"ir/ast.h"'), ('Match', '"runtime/re.h"')]
def header_text(path, body_lines):
    g = os.path.basename(path).upper().replace('.', '_'); t = toks('\n'.join(body_lines))
    incs = ['#include %s' % h for ty, h in TYPE_HDR if ty in t]
    return '\n'.join(['#ifndef ' + g, '#define ' + g] + incs + body_lines + ['#endif', ''])
new_text = {h: header_text(h, [l for _, ls in its for l in ls]) for h, its in dest.items() if its}
new_ids = {h: {n for n, _ in its} for h, its in dest.items() if its}
for ex, protos in appended.items():
    t = rd(SRC + ex); k = t.rstrip('\n').rfind('#endif'); assert k > 0, ex
    extra = ''
    if 'FILE' in toks('\n'.join(protos)) and '#include <stdio.h>' not in t: extra = '#include <stdio.h>\n'
    body = t[:k] + '\n'.join(protos) + '\n' + t[k:]
    if extra:
        m = re.search(r'^#define \w+_H\n', body, re.M); body = body[:m.end()] + extra + body[m.end():]
    new_text[ex] = body; new_ids[ex] = {re.search(r'\b(\w+)\s*\(', p).group(1) for p in protos}
# --- 4. the units -------------------------------------------------------------------------------------------------------------------------------------------
SYS_IDS = {'stdio.h': 'FILE printf fprintf sprintf snprintf fopen fclose fputs fputc fgets fread fwrite fflush stdin stdout stderr puts putchar getc fgetc getchar ungetc fseek ftell rewind setvbuf perror vfprintf vsnprintf vprintf fdopen fileno tmpfile remove rename EOF BUFSIZ',
           'stdlib.h': 'exit abort atoi atol atoll strtol strtoul strtoll strtoull strtod qsort bsearch getenv setenv abs labs llabs EXIT_FAILURE EXIT_SUCCESS system div ldiv atexit mkstemp realpath',
           'string.h': 'strlen strcmp strncmp strcpy strncpy strcat strncat memcpy memmove memset memcmp strchr strrchr strstr strdup strndup strtok memchr strerror strcasecmp strncasecmp strspn strcspn strpbrk',
           'ctype.h': 'isalpha isdigit isalnum isspace isupper islower toupper tolower isxdigit ispunct isprint iscntrl isgraph',
           'setjmp.h': 'jmp_buf setjmp longjmp sigjmp_buf sigsetjmp siglongjmp', 'time.h': 'time_t time clock clock_t localtime gmtime strftime mktime timespec clock_gettime CLOCKS_PER_SEC difftime CLOCK_MONOTONIC CLOCK_REALTIME nanosleep ctime'}
SYS_IDS = {k: set(v.split()) for k, v in SYS_IDS.items()}
pass_ids = {}
for k, kind, name in carried:
    if kind == 'inc':
        p = resolve(H, name)
        if p is None: raise SystemExit('passenger %s does not resolve' % name)
        if p not in pass_ids: pass_ids[p] = (k, F.scan_header(rd(SRC + p))[0], name)
INCRX = r'^[ \t]*#[ \t]*include[ \t]+"(?:[^"]*/)?driver_private\.h"[^\n]*\n'
units = sorted(f[len(SRC):] for f in glob.glob(SRC + '**/*', recursive=True) if f.endswith(('.c', '.cpp')) and re.search(INCRX, rd(f), re.M))
plan = {}
for u in units:
    text = rd(SRC + u); tu = toks(text)
    have = set()
    for m in re.finditer(r'^\s*#\s*include\s+"([^"]+)"', text, re.M):
        p = resolve(u, m.group(1))
        if p: have.add(p)
    lines = []   # (position, include line)
    for k, kind, name in carried:
        if kind == 'sys':
            if name in SYS_IDS and (SYS_IDS[name] & tu) and ('#include <%s>' % name) not in text: lines.append((k, '#include <%s>' % name))
        else:
            p = resolve(H, name); k0, ids, _ = pass_ids[p]
            if k == k0 and p not in have and (ids & tu): lines.append((k, '#include "%s"' % p))
    for h, ids in new_ids.items():
        if (ids & tu) and h not in have and not any(l == '#include "%s"' % h for _, l in lines): lines.append((first_pos[h], '#include "%s"' % h))
    lines.sort()
    plan[u] = [l for _, l in lines]
print('driver_private.h: %d lines, %d items; new headers: %s' % (len(L), len(items), ', '.join('%s %d' % (os.path.basename(h), len(its)) for h, its in dest.items())))
print('  appended to existing headers: %s' % ('; '.join('%s += %s' % (ex, ', '.join(re.search(r"\b(\w+)\s*\(", p).group(1) for p in ps)) for ex, ps in appended.items()) or 'none'))
print('  deleted: %s' % '; '.join('%s (%s)' % d for d in deleted))
print('  passengers: %d distinct' % len(pass_ids))
for u in units: print('  %-36s -> %s' % (u, ' '.join(l.replace('#include ', '') for l in plan[u])))
if APPLY:
    for h, t in new_text.items(): wr(SRC + h, t)
    for u in units:
        text = rd(SRC + u)
        text = re.sub(INCRX, lambda m: ''.join(l + '\n' for l in plan[u]), text, count=1, flags=re.M)
        wr(SRC + u, text)
    os.remove(SRC + H); print('APPLIED: %d headers written, %d units rewritten, driver_private.h deleted' % (len(new_text), len(units)))
else: print('(dry run; --apply writes)')
