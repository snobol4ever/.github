# Session Handoff — 2026-07-10

## Context window at handoff: ~80%

---

## What was accomplished this session

### Commits (newest first)

**48e7d7d3** `ICN: member(t,k) returns value not key; GC visitor handles list frame_elems raw array`
- `by_name_dispatch.c`: `member(t,k)` was returning `kd` (the lookup key); Icon semantics return the stored **value**. Fixed to `table_get(tbl, ks)`. Recovers `rung13_table_member`.
- `gc_heap.c`: `rt_gc_visit_descr` DT_DATA branch crashed on list records that smuggle a raw `DESCR_t*` as `frame_elems` (`.u->type = 0x64` garbage → SIGSEGV). Fixed by detecting `frame_elems` layout by field name and walking elements directly. Fixes geddump crash on GC cycle.

**241c5867** `BENCH-F3: bare string-relop with generator operand re-pumps on compare-fail`
- `lower_icon.c`: relop ω→right-β re-pump wire guarded `ival 5..10` (numeric relops BINOP_LT..NE only). String relops `BINOP_SLT..SNE` (12..17) never got the edge → `"x" == !L` / `"x" == (a|b|c)` only tried first alternative. Guard is now the `is_relop` predicate (both families, canonical: `irgen.icn ir_binary` funcs-set opfn failLabel = right.ir.resume).
- Verified: 5 repros HIT m3+m4; exhaustion still MISSes; all gates green; rung FAIL-set byte-identical pre/post (fix was ladder-neutral, no new regressions).

---

## Repo state

| Binary | Built | Clean |
|--------|-------|-------|
| `SCRIP/scrip` | ✓ 2026-07-10 | ✓ |
| `SCRIP/out/libscrip_rt.so` | ✓ 2026-07-10 | ✓ |

| Suite | Result |
|-------|--------|
| Icon smoke m3+m4 | 12/12 both modes |
| Prolog smoke m3+m4 | 5/5 both modes |
| SNOBOL4 smoke | 7/7 |
| All 6 icon/emit gates | GREEN |
| Icon rung ladder | 229 PASS / 24 FAIL / 35 XFAIL (rung13 recovered) |

Installed: `gdb` (apt-get, session-local).

---

## Clones in place

```
/home/claude/.github/          ← snobol4ever/.github (PLAN.md, GOAL-ICON-BB.md etc.)
/home/claude/SCRIP/            ← snobol4ever/SCRIP
/home/claude/corpus/           ← snobol4ever/corpus
/home/claude/icon-master/      ← gtownsend/icon (built: bin/icont + bin/iconx)
/home/claude/SCRIP/refs/icon-master → /home/claude/icon-master
/home/claude/SCRIP/refs/jcon-master/tran/irgen.icn → corpus copy
```

---

## Open FAIL list (24 remaining after this session)

```
rung36_jcon_args       rung36_jcon_coerce    rung36_jcon_endetab
rung36_jcon_fncs1      rung36_jcon_genqueen  rung36_jcon_htprep
rung36_jcon_kwds       rung36_jcon_mffsol    rung36_jcon_mindfa
rung36_jcon_parse      rung36_jcon_prepro    rung36_jcon_recogn
rung36_jcon_scan       rung36_jcon_scan1     rung36_jcon_scan2
rung36_jcon_string     rung36_jcon_string1   rung36_jcon_substring
rung36_jcon_table      rung36_jcon_var
rung37_keywords        rung37_neg_pos        rung37_proc_lookup
rung37_scan_alt
```

### Diagnosed this session (not yet fixed)

**rung37_scan_alt** — `("ab"|"cd"|"ef") ? move(1)` only fires body for first subject. EVERY alternation in scan position: external β should advance to next subject after body exhaustion; currently the alternation collapses after first. Root: `bb_gen_scan` β-wire does not thread back to alternation's next-subject edge.

**rung37_neg_pos** — rc=134 (SIGABRT); negative/pos scan position semantics; also `subj_mut` lvalue swap of `&pos` ↔ local incorrect.

**rung36_jcon_*** (20 tests) — bulk rung36 failures span: scan, string ops, table ops, coercion, args, keyword semantics. Likely shared root causes; investigate `rung36_jcon_scan` first as it's a simpler single-feature test.

**rung37_keywords** — `&fail`, `&null`, `&subject`, `&pos` keyword semantics under various contexts.

**rung37_proc_lookup** — procedure-value lookup / first-class procedure semantics.

### geddump (benchmark, not a rung test)

Crash fixed (GC SEGV). Now **times out** >120s. Suspected root: scan_stmt loop over large GEDCOM file is O(n²) — string concatenation re-allocation pattern common in Icon programs that build large strings incrementally. Need to profile; likely `str_concat` or `every … || …` pattern.

---

## Next session recommended entry

1. Read `PLAN.md` + `RULES.md` + `GOAL-ICON-BB.md` (mandatory per session-start sequence).
2. Run `bash scripts/test_smoke_icon.sh` + `bash scripts/test_smoke_prolog.sh` to confirm clean baseline.
3. Attack **rung37_scan_alt** — alternation-in-scan-position β threading. Read `src/templates/bb_gen_scan.cpp` + `src/templates/bb_match_alternate.cpp` + canonical `irgen.icn ir_a_Binop` / `ir_a_Scan` before touching.
4. Then **rung36_jcon_scan** to open the bulk rung36 block.
5. **Do not touch geddump timeout** until scan_alt is clean — they may share a scan-position performance root.

---

## Session authors
LCherryholmes · Claude Sonnet 4.6
