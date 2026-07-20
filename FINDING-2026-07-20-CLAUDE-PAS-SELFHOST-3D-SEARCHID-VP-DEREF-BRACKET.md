# FINDING 2026-07-20 — PAS-SELFHOST-3d: the var-decl "stall" is NOT in vardeclaration; it is a pointer-field deref after searchid's var-param writeback

**Author:** Claude (session 2026-07-20). **Status:** BRACKETED, NO CODE LANDED. **Repro:** `program t; var i:integer; begin i:=5 end.` → SCRIP-pcom `--run` emits 40-byte `prr` (`l 3` / `ent 1 l 4` / `ent 2 l 5`), rc=0, no error, then stops.

## The bracket (MONITOR-FIRST milestone instrumentation of pcom under SCRIP)

Instrumented copy: `/tmp/p4boot/pcom_inst.pas` (writeln('@@...') milestones into the listing `output`). Trace of the FAILING input ends here:

```
@@BLK-ENTER ... @@VD-OUTER-DONE sy=31   <- vardeclaration + decl loop COMPLETE
@@BLK-DECL-END sy=31 eof=0              <- decl loop exits cleanly, sy=beginsy(31)
@@BODY-STMT-LOOP-TOP sy=0              <- enters body statement loop, sy=ident(0)
@@STMT-ENTER sy=0
@@ST-IDENT-PRE-SID
@@SID-ENTER id=[i       ]
@@SID-LEVEL disx=1 rootnil=0
@@SID-NODE name=[i       ] cmp_eq=1 cmp_lt=0   <- searchid FINDS i (goto 1 taken)
@@SID-EXIT
@@ST-IDENT-POST-SID-NODEREF            <- fires: writeln with NO lcp deref works
@@ST-NIL=0                             <- lcp is NON-NIL after searchid
@@ST-NAME=                             <- lcp^.name reads EMPTY (should be "i       ")
[STOP]                                 <- lcp^.klass deref STALLS (no @@ST-KLASS)
```

## What this proves (and corrects in the LIVE CURSOR)

1. **The "var-declaration stall" name is WRONG.** `vardeclaration`, `typ`, and the entire `block` declaration loop run to completion. So do PAS-SELFHOST-3d's prior guesses about `while`/`repeat`/`case` mis-termination in the decl section.
2. The stall is in pcom's `statement()` -> `ident:` case, at the FIRST field dereference of the pointer `searchid` wrote back through its `var fcp: ctp` parameter:
   ```pascal
   ident: begin searchid([vars,field,func,proc],lcp); {returns lcp -> i's entry}
            ... lcp^.klass ...   {<- STALLS here}
   ```
3. **Same pointer reads differently in two scopes.** INSIDE searchid, `lcp^.name` reads `"i       "` correctly (the `@@SID-NODE` print). In the CALLER, the SAME returned pointer reads `lcp^.name` = EMPTY and `lcp^.klass` = STALL. Pointer VALUE survives (`@@ST-NIL=0`), so it is a FIELD-LAYOUT / field-access divergence across scopes, not a null/lost pointer.

## What is NOT the bug (isolation probes, all PASS under SCRIP --run)

- `/tmp/p4boot/probe_vptr.pas` — var-param pointer writeback + variant-tag read, plain global pointer. PASS (klass=2, DONE).
- `/tmp/p4boot/probe_disp.pas` — adds the `display[disx].fname` array-of-record source + BST-shaped loop + `goto`-equivalent. PASS.

So the minimal shapes work; the pcom failure needs the FULL `identifier` record layout (`name: alpha; llink,rlink: ctp; idtype: stp; next: ctp; case klass: idclass of ...` — pcom.pas:142-156), a `packed record` with a nested multi-level variant, deeper than the probes reproduced. The `klass` variant TAG field sits after name(8) + 4 pointers.

## Hypothesis for the fix (next session)

SCRIP's per-scope record-field resolution (the `g_pas_recvars` / field-index registry, `__pas_field_*` / `__pas_deref` runtime, and the variant-tag `klass` handling) computes a different field offset / decode for `ctp^.name`/`ctp^.klass` in the `statement`/`body` scope than in `searchid`'s scope — OR `enterid` stored a re-encoded record whose field boundaries the caller's deref misreads. Reads of `.name` (offset 0) partially work (empty, not garbage); `.klass` (the variant tag, deep offset) stalls -> likely an out-of-range field index into the SOH-encoded record producing a bad control-flow (Byrd-box omega to program end, the documented IR_SUCCEED/IR_FAIL invisibility hazard) rather than a crash.

## NEXT STEP (sanctioned: RULES.md two-step gdb hit-count)

1. Build with the record probe growing toward pcom's real `identifier` layout (add the multi-level `case klass` variant + `packed` + alpha `name`) until a MINIMAL standalone probe reproduces the empty-name / klass-stall. That collapses the bracket to a corpus-committable repro.
2. gdb: break on the emitted `lcp^.klass` deref site (the `__pas_deref`/field-index runtime sink), hit-count spin to the statement-time call, single-step to the instruction that reads the wrong offset / routes omega. Fix there.
3. Re-run instrumented pcom; the trace must pass `@@ST-IDENT-KLASS=` and reach `@@STMT-EXIT` / `retp`.

## Env
- Symlinks `/home/claude/{SCRIP,corpus,.github}` -> `/home/claude/work/*`. `scrip` built. `libscrip_rt.so` + fpc were building in background (mode-3 `--run` needs neither; used for the bracket).
- Repro inputs: `/tmp/p4boot/l_var1.pas` (fails), `l_empty.pas` (self-hosts, 130-byte prr).
- NO CODE LANDED, NO COMMIT, NO PUSH. No credential needed yet.

## Additional negative probes (all PASS under SCRIP --run — the bug needs pcom-scale context)
- `probe3.pas` — pcom-FAITHFUL `identifier` record: packed, alfa name, full multi-level nested variant (`proc,func: (case pfdeckind ... case pfkind ...)`). PASS (vp klass=2).
- `probe4.pas` — same pointer deref'd in THREE scopes (searchit/reader/main) after `display[disx].fname` BST-shaped retrieval + var-param writeback. PASS.
- `probe5.pas` — node fields set in SEPARATE passes after `new` (klass set, then a `while nxt<>nil do with nxt^` offset-assignment loop mutating vaddr — the exact vardeclaration shape), then var-param writeback + klass read. PASS.

CONCLUSION: every isolated shape works. The pcom failure needs the FULL environment the probes can't cheaply reconstruct: the real unbalanced BST built by `enterid` (which does `fcp^.llink:=nil; fcp^.rlink:=nil` AFTER insertion — pcom.pas:551), the `display[]`/`top`/`level` globals, and pcom scale. GDB on the live pcom deref (two-step hit-count on the `lcp^.klass` field-deref sink) is the converging next tool, not more probes.

## PRECISE next-session start
1. `scrip --run /tmp/p4boot/pcom_inst.pas < /tmp/p4boot/l_var1.pas` reproduces the trace above (instrumented pcom preserved-in-spirit; recreate from pcom.pas + the @@ markers if the sandbox evaporated — marker list is in this doc's trace).
2. `apt-get install -y gdb`; break on the field-deref runtime sink (`__pas_deref` / the `klass` variant-tag field-index path in `by_name_dispatch.c` / `zeta_storage.c`), condition/ignore-count to the statement-time `searchid`-returned `lcp^.klass` read, single-step to the instruction that reads the wrong offset or routes omega.
3. The tell: `lcp^.name` (offset 0) reads EMPTY (not garbage) and `lcp^.klass` (variant tag, deeper offset) routes omega-to-program-end — consistent with an out-of-range field index into the SOH-encoded record, or a per-scope record-type binding that decodes `ctp^` with wrong field boundaries in `body`/`statement` vs `searchid`.
