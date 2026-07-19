# FINDING 2026-07-19 — JCON compiler under SCRIP: links + runs; five fixes landed; two runtime pipeline blockers pinned with micro-repros

Session goal (Lon): jtran (JCON's translator, Icon source) self-hosting under SCRIP, then 4-way perf
(iconx / JCON-JVM / SCRIP m3 / m4). Re-derive all counts fresh. SCRIP `b6363a50`, corpus `+rung14`.

## Landed (full narrative in SCRIP b6363a50's message)
1. **XA_BB_EMIT_PAIR_MAX 32→1024 + loud guard** — 17-arm DISJUNCTION overflow wrote a label ptr over
   `pair_n` → SEGV at HEAD (regression vs the 2026-07-18 finding's rc=0). Round-2 Q_MAX disease, 2nd wardrobe.
2. **The 183-undefined-labels + 1-bomb were ONE surface** — 177 `bb_assign_local` bomb sites (the "1"
   counted the deduped `.rodata` string) emitting rt_bomb with NO α/β. All `__case_result` assigns with
   control-node rhs (130 RETURN / 44 SUSPEND / 3 GOTO). Diagnosis instrument added: `SCRIP_DRIVE_DIAG=1`
   (zero-text-emission per drive + ASSIGN staging census; emit_io.c byte counter + emit_text_count()).
3. **TT_CASE gets the slice-3 `icn_arm_result` filter** (both arm-result pushes) — same latent disease
   lower_alt/lower_if had.
4. **`emit_chain_operand_refs` mangle site caught red-handed** (gdb: bp on ir_operand_push by child ptr):
   the stack-sim backfill wiped+repushed operands, handing RETURN as a value operand — undoing lower's
   authored zero-operand form. Fix (language-blind): RETURN/SUSPEND/CORET/COFAIL reset the sim stack like
   ar<0; control transfer is never a value.
5. **Pre-existing semantics**: `case … { N: return e }` rewired RETURN's exit edge into the case (f(1)
   returned the FALLTHROUGH). Wiring-kind arm now keeps its own edge. Locked: corpus
   `rung14_case_return_arm` (m3 diff-exact; m4 byte-identical output verified pre-lock).
6. **proc/1 implemented** + proc()'s user branch returned an entry_pc-keyed DESCR that misresolves to
   'main' under stackless (all entry_pcs identical → procval_name's table scan hits row 0). Now returns
   canonical `rt_proc_value(name)`.

## Board after (fresh, this sandbox)
Icon rungs **FAIL 9→7** (scan2 + var now PASS; zero regressions; FAIL set ⊂ cursor's). Smokes icon
14/14×2, prolog 5/5×2, sno 7/7. Gates no_stack/one_reg/semicolon = 0. jtran merge: **0 bombs, LINKS**
(4.4MB /tmp/jtran.bin) under `SCRIP_BETA_ELIDE_OFF=1`.

## Blocker A — β-elision scan gap (elision rung owner)
`xchain680_n282_β` (m4 ld undefined; m3 twin `bb_emit_end unresolved forward ref`): an IR_ASSIGN's β is
the landing of an emit-time ω-CHASE/φ-redirect (BP-9(ii) re-resolution can land a DIFFERENT node's β
than the verbatim wire `flat_beta_used_scan` mirrors). One instance in ~420K lines. The hatch
`SCRIP_BETA_ELIDE_OFF=1` is the sanctioned same-build baseline — use it for all jcon-compiler builds
until the scan learns the chase. Candidate fix shapes: (a) replicate chase logic in the scan (drift
risk, violates write-once), (b) flip bused[j] when the chase selects betas[j] with j>i and accept the
j<i residue loudly, (c) never elide β of nodes that can be φ/chase landings (ASSIGN class?).

## Blocker B — coexpr pipeline, TWO mode-split repros (the jtran shape)
jtran = `while L[1] {… c := create fn(c,args)}; while @c` — stages pull `@\c`, yield by `suspend`.
- **m4: create-through-proc()-descriptor loses the pump.** `/tmp/p8.icn` (10 lines): `fn:=proc("hi2");
  c:=create fn(c,["z"]); write("pump: ",@c)` → m3 prints `pump: val:z`; **m4 prints nothing for that
  line** (first @ fails silently), A/B/C frame intact, rc=0. Plain `create (1 to 3)` pumps fine both
  modes (p4; &features precedent) — the delta is the COMPUTED-DESCR callee inside the spawned coexpr
  under m4. Suspect: the in-thread by-name/native-fn resolution path m4-side (rt_call_proc_descr /
  slab-per-thread); the pre-fix symptom `[GZ-10] rt_call_proc_descr: 'main' has no stackless slab`
  points the same direction.
- **m3: full 15-module pipeline spins ~116M EMPTY lines** to timeout on
  `preproc hello_t.icn : stdout` (rc=124). Preprocessor is PROVEN CORRECT in isolation (m4 probe
  /tmp/tpp.icn + module: first yield `#line 0 "hello_t.icn"`). So per-line logic is right; the spin is
  in the m3 pipeline/transmission or a scan loop under the coexpr (a generator yielding "" forever
  instead of failing at EOF). MONITOR-FIRST applies once a comparable oracle trace exists; next session
  bracket with the instrumented main `/tmp/jm2.icn` pattern (stage-by-stage counters).

## Repro pack (rebuild these paths from this finding; /tmp dies with the sandbox)
- Merge: 15 modules in ORDER (2026-07-18 finding) + `SCRIP_BETA_ELIDE_OFF=1`; link `-L out -lscrip_rt`.
- p8 (m4 coexpr-descr), jm2 (instrumented main), tpp (isolated preprocessor probe) — bodies in the
  session transcript / trivially re-derivable from the shapes above.

## Not reached (next session)
Self-host run + byte-compare vs iconx-jtran; 4-way bench. Arizona icont/iconx BUILT this sandbox
(`/home/claude/icon-master`, make Configure name=linux && make Icont — clean). JCON JVM not built
(needs default-jdk-headless; jcont bashism + cwd traps in GOAL-ICON-BB §BENCHMARK MAP).
