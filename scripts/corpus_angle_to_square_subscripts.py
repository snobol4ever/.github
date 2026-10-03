#!/usr/bin/env python3
"""corpus_angle_to_square_subscripts.py [--dry-run | --apply] [--root CORPUS] -- every SNOBOL4 subscript A<I> in the corpus becomes A[I].
Lon 2026-10-02, in-chat to the ceo, verbatim: "Regarding the usage of '<' and '>', remove SCRIP's support for these as array indices.
We do NOT TWO ways to do the same thing. We DO might NEED the angle brackets to implement LAMBDA code syntax." and "THen go change all
corpus programs to not use angle brackets, but instead SQUARE BRACKETS." (ceo CEO-1447). SPITBOL accepts both brackets, so the
conversion cannot change a program's output under the oracle; SCRIP's grammar drops the angle form afterwards (a row).
WHAT IS CONVERTED: in a SNOBOL4 statement, outside string literals ('...' and "..."), a < is a subscript's opening bracket and a > its
closing one -- SNOBOL4 has no other use for them -- EXCEPT in the goto field (after the statement's ':'), where :<C> and :S<C> are the
DIRECT GOTO to a CODE object, which stays. Comment lines (* in column 1), control lines (- in column 1) and everything after a program's
END statement (its data) are left alone; a continuation line (+ or . in column 1) continues its statement's field state. A master
container (tests/*/ALL.sno) holds many programs: after an entry's END its data is left alone until the next entry's banner or one-line ;* tag.
FILES: *.sno, *.inc, *.sbl, and the ```SNOBOL4 fences of *.md, under the corpus. Binary-safe read and write; a file is written only when a
byte changed. Prints one line per changed file (subscripts converted) and the strings that hold a < or > (code that EVAL or CODE may
compile, which the converter does not touch and a human reads).
"""
import os, re, sys
sys.path.insert(0, '/home/claude_ceo/SCRIP/scripts')
from corpus_suite_harness import BANNER_RE, ONE_LINE_TAG_RE
APPLY = '--apply' in sys.argv
ROOT = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else '/home/claude_ceo/corpus'
def convert_lines(lines, container):
    out, n, strings = [], 0, []
    in_goto = False; ended = False
    for idx, line in enumerate(lines):
        if container:
            t0 = line.decode('latin-1')
            if t0[:1] == '*' and BANNER_RE.match(t0):
                # an entry whose first line no statement can begin is DATA held as an entry (gimpel's PHRASES grammar): left alone
                nxt = lines[idx + 1] if idx + 1 < len(lines) else b''
                ended = bool(nxt) and not re.match(rb'[ \t+.*\-A-Za-z0-9]', nxt)
                out.append(line); continue
        if container and ended:
            # a master container: an entry's data after its END is data; the next entry (a banner or a one-line ;* tag) resumes code
            t = line.decode('latin-1')
            if (t[:1] == '*' and BANNER_RE.match(t)) or ONE_LINE_TAG_RE.search(t): ended = False
        if ended or not line or line[:1] in (b'*', b'-') or not re.match(rb'[ \t+.A-Za-z0-9]', line):
            out.append(line); continue   # a line no statement can begin (data such as <GOOD>::= in a container) is left alone
        if line[:1] not in (b'+', b'.'):
            in_goto = False
        if re.match(rb'END(\s|;|$)', line) and not (container and ONE_LINE_TAG_RE.search(line.decode('latin-1'))):
            ended = True; out.append(line); continue
        b = bytearray(line); q = None; i = 0
        label_at = 0 if line[:1] not in (b'+', b'.') else -1   # a statement's first column holds its LABEL, which is a name and stays
        while i < len(b):
            c = b[i]
            if i == label_at:
                label_at = -1
                while i < len(b) and b[i] not in (32, 9, 59): i += 1
                continue
            if q is not None:
                if c == q: q = None
                elif c in (60, 62): strings.append(bytes(line).decode('latin-1').strip()[:160])
            elif c in (39, 34): q = c
            elif c == 59:  # ; a new statement on the same line, whose first byte, if not a blank, starts its label
                in_goto = False; label_at = i + 1
                rest = bytes(b[i + 1:]).lstrip()
                if not container and re.match(rb'END(\s|;|$)', rest): break
                if rest[:1] == b'*': break
            elif c == 58:  # : the goto field
                in_goto = True
            elif c == 60 and not in_goto: b[i] = 91; n += 1
            elif c == 62 and not in_goto: b[i] = 93; n += 1
            i += 1
        out.append(bytes(b))
    return out, n, strings
CODE_LINE = re.compile(rb"\b(SEQ|CODE|EVAL|S1)\(\s*'|^\s*S\s+=\s+'\s+AOPA<|^\s*X\s+=\s+F\s+'\(A<")
def code_strings(lines):
    # the second pass: a string that IS SNOBOL4 code -- Gimpel's SEQ(' ... ') and CODE(' ... ') arguments, and the two strings aopa.inc and
    # tsort.inc assemble and compile -- has its subscript brackets converted too; every other string (output text, HTML, macro data) stays
    out, n = [], 0
    for line in lines:
        if line[:1] in (b'*', b'-') or not CODE_LINE.search(line):
            out.append(line); continue
        b = bytearray(line); q = None; depth = 0
        for i, c in enumerate(b):
            if q is None and c in (39, 34): q = c; depth = 0
            elif q is not None and c == q: q = None
            elif q == 39 and c == 60 and re.match(rb'[A-Za-z0-9_\])]', bytes(b[i - 1:i])): b[i] = 91; n += 1; depth += 1
            elif q == 39 and c == 62 and depth > 0: b[i] = 93; n += 1; depth -= 1
        out.append(bytes(b))
    return out, n
SKIP = ('/packages/pascal/', '/editor_configs/')
def process(path):
    data = open(path, 'rb').read()
    lines = data.split(b'\n')
    container = os.path.basename(path).startswith('ALL.')
    if path.endswith('.md'):
        res, n, strings, fence = [], 0, [], False
        block = []
        for line in lines:
            if not fence and re.match(rb'```(SNOBOL4|Snobol4|snobol4|SCRIP)\s*$', line):
                fence = True; res.append(line); block = []; continue
            if fence and line.startswith(b'```'):
                conv, k, s = convert_lines(block, True); res.extend(conv); n += k; strings += s; fence = False; res.append(line); continue
            if fence: block.append(line)
            else: res.append(line)
        if fence: res.extend(block)
        new = b'\n'.join(res)
    else:
        conv, n, strings = convert_lines(lines, container)
        conv, k = code_strings(conv); n += k
        new = b'\n'.join(conv)
    return data, new, n, strings
total_files = total_n = 0; all_strings = []
for d, dirs, files in os.walk(ROOT):
    dirs[:] = [x for x in dirs if x != '.git']
    for f in sorted(files):
        if not f.endswith(('.sno', '.inc', '.sbl', '.md')): continue
        p = os.path.join(d, f)
        if any(x in p for x in SKIP): continue
        data, new, n, strings = process(p)
        if strings: all_strings += [(p, s) for s in strings]
        if new != data:
            total_files += 1; total_n += n
            print(f'{n:6d}  {os.path.relpath(p, ROOT)}')
            if APPLY: open(p, 'wb').write(new)
print(f'{"APPLIED" if APPLY else "DRY RUN"}: {total_n} brackets in {total_files} files')
seen = set()
print(f'strings holding < or > (left alone, read by a human): {len(all_strings)} lines in {len(set(p for p, s in all_strings))} files')
for p, s in all_strings:
    if (p, s) in seen: continue
    seen.add((p, s))
    if len(seen) <= 40: print(f'   {os.path.relpath(p, ROOT)}: {s}')
