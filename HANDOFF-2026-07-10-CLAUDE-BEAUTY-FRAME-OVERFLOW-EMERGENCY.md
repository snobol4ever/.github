# EMERGENCY HANDOFF — 2026-07-10 (Claude) — beauty suite: proc-frame overflow (`[r12+0x7560]` write past a 4 KB frame)

**STATUS: BLOCKED — bug bracketed, NOT fixed. Zero code changes. Nothing to push (SCRIP tree clean at `da22f9dd`; corpus clean; only scratch probes were created and deleted).**
This is an *emergency* handoff purely to preserve a live, well-bracketed bug hunt across the context boundary — not because anything broke. No regression introduced. No commit needed.

## GOAL THIS SESSION
Lon: "get the beauty test suite working." Ran `GOAL-SCRIP-BEAUTY.md`'s own runner against `corpus/programs/snobol4/beauty_suite/*_driver.sno`.

## BASELINE MEASURED (this build, SCRIP `da22f9dd`, corpus `0902dcfc`)
- `scrip` + `libscrip_rt` build clean; oracle `x64/bin/sbl` cloned OK.
- Beauty suite mode-3 (`./scrip --run`): **PASS=1 / FAIL=16** (only `fence_driver` passes). Several fails are hard **segfaults**, not output diffs.
- ⚠ NOTE: `GOAL-SCRIP-BEAUTY.md` is STALE — its "10/18 passing" and its whole S-6..S-13 ladder predate the GZ#5 rewrite and the entire SN4-PAT era. Do not trust its step list; the root cause below is new. The runner command in it is still valid (drop the `SNO_LIB` env var — include dirs are auto-seeded from the driver's own directory by `scrip.c:483`; `SNO_LIB` is optional and irrelevant to the crash).

## THE BUG (bracketed to one instruction; NOT yet root-caused to the emit/slot-assign site)

**Symptom:** emitted proc body writes `mov %rax,0x7560(%r12)` — i.e. `[r12 + 30048]` — but the frame allocated for that proc in `rt.c` is only `max(PROC_FRAME_QWORDS*8 = 4096, p->frame_bytes)` bytes. `p->frame_bytes` for the crashing proc is **0** (confirmed in gdb), so fbytes = 4096. The store at **30048** lands ~26 KB past the end of the frame → SIGSEGV (nondeterministic under ASLR because what sits past the frame varies; **deterministic crash with `setarch -R`**, deterministic-ish without).

**Minimal repro (self-contained, ~10 lines) — reproduces the crash 100% under ASLR-off:**
```
cat > /home/claude/work/corpus/programs/snobol4/beauty_suite/repro.sno << 'EOF'
    TRUE = 1
    FALSE = 0
    UTF = TABLE()
    <121 UTF[CHAR(..)CHAR(..)] = '...' entries — see below>
    UTF_Array = SORT(UTF)
    i = 0
G1  i = i + 1
    $UTF_Array[i, 2] = UTF_Array[i, 1]  :S(G1)
    UTF_Array =
    i =
        DEFINE('foo(name,val)')     :(foo_end)
foo     $name = val                 :(RETURN)
foo_end
        foo('a', 'hello')
        OUTPUT = a
EOF
setarch $(uname -m) -R env SCRIP_NO_SEGV_HANDLER=1 ./scrip --run repro.sno   # → SIGSEGV, deterministic
```
Regenerate the 121 UTF entries with:
```
python3 -c "lines=open('corpus/programs/snobol4/beauty_suite/global.sno').read().splitlines(); \
utf=[l for l in lines if l.strip().startswith('UTF[CHAR')]; print('\n'.join(utf[:121]))"
```

**Bisection facts (all verified this session, not inferred):**
1. `global.sno` alone (no proc call) runs fine. `assign.sno`/a bare `foo` proc alone runs fine.
2. The crash needs BOTH: (a) a large global-init preamble that grows the ζ arena — specifically the `UTF = TABLE()` + `SORT` + the `$UTF_Array[i,2]=...` indirect-assign loop, at **≥121** UTF entries (120 is safe, 121 crashes — a hard cliff), AND (b) a subsequent **indirect assignment inside a DEFINE'd proc** (`$name = val`). `mymin_D` (indirect assign in proc) crashes; `mymin_E` (proc without indirect assign) is fine; `mymin_F` (assign.sno's exact `.dummy`+`$name=EVAL/expr`+NRETURN shape) crashes too.
3. So the trigger is: **the proc's emitted frame uses ζ-slot offsets in the 0x74xx–0x75xx (≈30 KB) range, while its runtime frame allocation is only 4 KB.** The big preamble is what pushes the graph's `jcon_value_region` / slot offsets that high.

**Crash-site disasm (foo's emitted entry, via `gdb -ex 'break rt.c:577' -ex 'x/34i p->fn'`):**
```
push %r12 ; mov %rdi,%r12 ; movabs $g_gva_base,%rax ; mov (%rax),%rbx   ; <- rbx=GVA reload (CSTACK anchor)
push %rbp ; mov %rsp,%rbp ; sub $0x8,%rsp
cmp $0,%esi ; jne <resume>
... (indirect-assign call: rt_nv_set-ish via APPLY/EVAL) ...
0x...3c: mov %rax,0x7560(%r12)      <-- LAND MINE: store 30048 bytes into a 4096-byte frame
```
`p->fn = 0x7ffff7000000`, `p->frame_bytes = 0`, `p->dyn_scope = 1` (so it routes through `rt_call_named_proc`, rt.c:560, alloca/zls2_push path at :573 — NOT `rt_call_proc_descr`).

## WHERE TO LOOK NEXT (the two competing hypotheses — decide FIRST before coding)

The offset 0x7560 and the frame allocation are computed in two different places that have DISAGREED:

- **Emit side:** `g_last_flat_frame_bytes = g_emit_cfg->jcon_value_region` (emit.cpp:1703), where `jcon_value_region = zls_g_region(g)` (scrip_ir.c:248 → zeta_storage.c:338, the ζ-slot region for that graph). Proc slot offsets like 0x74c0/0x74b0/0x7560 come from `ir_drive_slot_assign` writing into that region.
- **Runtime side:** `rt_proc_set_frame_bytes(pname, g_last_flat_frame_bytes)` is called AFTER `emit_chain` for each proc (m3: scrip.c:1385; m4: scrip.c:1159) and is supposed to make `p->frame_bytes` large enough. But gdb shows `p->frame_bytes == 0` for the crashing proc — so **either (H1) `g_last_flat_frame_bytes` was 0/stale when `rt_proc_set_frame_bytes` ran for foo** (region not yet computed, or `g_emit_cfg` pointing at the wrong graph — note emit.cpp:1703 reads `g_emit_cfg` which is set per-proc at scrip.c:1382), **or (H2) the region value is correct but the proc's slot offsets are being assigned from a DIFFERENT (larger, main-graph-sized) region than the one whose size is reported** — i.e. the proc graph inherited the main graph's inflated slot base but reports its own small region.

H2 is the more likely story given the "needs the big main preamble" trigger: the main graph's `jcon_value_region` grew to ~30 KB because of the SORT/indirect-assign loop, and the proc's slots appear to be assigned in the SAME numbering space (hence 0x7560), but `rt_proc_set_frame_bytes` reported the proc's own tiny region (0). **First diagnostic step next session:** in `rt_call_named_proc` (rt.c:560) print `p->frame_bytes` AND the max slot offset the emitted body actually references for `foo`; and at scrip.c:1385 print `pname` + `g_last_flat_frame_bytes` for every proc — confirm whether foo's reported bytes is 0 while its body references 0x7560. That single print pair decides H1 vs H2.

## METHODOLOGY NOTE (RULES.md MONITOR-FIRST)
This is a **crash**, not an oracle divergence, so the 2-way sync-step monitor doesn't directly apply (it brackets *value* divergence between engines). The static bracket above (disasm + bisection cliff at 121 entries + the offset-vs-allocation arithmetic) is already tighter than the monitor would give. Next step is the gdb print-pair above (H1 vs H2), then a targeted single-step, per the RULES.md "step on the land mine" discipline.

## BUILD / RUN CRIB
```
cd /home/claude/work/SCRIP && git config user.name LCherryholmes && git config user.email lcherryh@yahoo.com
bash scripts/install_system_packages.sh
rm -f scrip && make -j4 scrip && make libscrip_rt
# beauty runner (drop SNO_LIB, it's optional):
BEAUTY=/home/claude/work/corpus/programs/snobol4/beauty_suite
for s in "$BEAUTY"/*_driver.sno; do n=$(basename "$s" .sno); r="$BEAUTY/$n.ref"; [ -f "$r" ] || continue
  g=$(timeout 10 ./scrip --run "$s" 2>/dev/null); [ "$g" = "$(cat "$r")" ] && echo "PASS $n" || echo "FAIL $n"; done
```
gdb clean-backtrace hook: prefix with `SCRIP_NO_SEGV_HANDLER=1`; deterministic crash with `setarch $(uname -m) -R`.

## HOUSEKEEPING
- Repos were cloned to **`/home/claude/work/`** (not `/home/claude/`) this session — adjust the PLAN.md clone paths if you clone fresh, or `cd /home/claude/work`.
- SPITBOL oracle at `/home/claude/work/x64/bin/sbl`. It errors "No END statement found" on the beauty drivers because they rely on implicit end — check how the existing `.ref` files were generated (they exist and are the gate; don't regen unless needed).
- BB-CODEGEN DESIGN SET (ARCH-ICON.md, GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md, xa_flat.cpp) WAS read this session — any fix touching the proc prologue/epilogue frame size (xa_flat.cpp `g_frame_active` arms, or the `rt_proc_set_frame_bytes` plumbing) is in scope of those rules; the frame allocation lives in `rt.c` (runtime, not a template) and `scrip.c` (driver), so a pure-plumbing fix there needs no template edit.

## HANDOFF STATUS
**BLOCKED / INCOMPLETE.** No commit, no push (nothing changed). Per RULES.md this is NOT "handoff complete" — it is a preserved bug bracket. `scripts/handoff_status.sh` would print HANDOFF COMPLETE only because the tree is clean (no work to push); that is the trivial-true case, not a completed task. The task (beauty suite green) is UNSTARTED beyond diagnosis.
