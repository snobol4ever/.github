# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `asm-backend` B-223 — M-ASM-RUNG8
**HEAD:** `be4a978` B-222
**Milestone:** M-ASM-RUNG8 ❌
**Invariants:** 100/106 C (6 pre-existing) · 26/26 ASM

**⚠ CRITICAL NEXT ACTION — Session B-223:**

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase origin asm-backend
apt-get install -y libgc-dev nasm && make -C src
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh    # 100/106 (6 pre-existing)
CORPUS=$CORPUS bash test/crosscheck/run_crosscheck_asm.sh # 26/26

# Sprint M-ASM-RUNG8: rung8/ — REPLACE/SIZE/DUPL 3/3 PASS via ASM backend
ls /home/claude/snobol4corpus/crosscheck/strings/
CORPUS=$CORPUS bash test/crosscheck/run_crosscheck_asm_rung.sh \
  /home/claude/snobol4corpus/crosscheck/strings rung8
```

**Sprint B-220 — JVM Greek labels (65 sites in emit_byrd_jvm.c):**

Every Byrd port label in generated JVM output must carry a Greek suffix.

| Old | Port | New |
|---|---|---|
| `Jn%d_lit_ok` | γ | `Jn%d_lit_γ` |
| `Jn%d_seq_mid` | γ→α | `Jn%d_seq_γ` |
| `Jn%d_alt_right` | β | `Jn%d_alt_β` |
| `Jn%d_nam_ok` | γ | `Jn%d_nam_γ` |
| `Jn%d_dol_ok` | γ | `Jn%d_dol_γ` |
| `Jn%d_arb_loop` | β | `Jn%d_arb_β` |
| `Jn%d_arb_decr` | β inc | `Jn%d_arb_βinc` |
| `Jn%d_arb_retry` | β retry | `Jn%d_arb_βr` |
| `Jn%d_arb_commit` | γ | `Jn%d_arb_γ` |
| `Jpat%d_success` | stmt γ | `Jpat%d_γ` |
| `Jpat%d_fail` | stmt ω | `Jpat%d_ω` |
| `Jpat%d_retry` | scan β | `Jpat%d_β` |
| `Jpat%d_tok` / `Jpat%d_tfail` | tree γ/ω | `Jpat%d_tγ` / `Jpat%d_tω` |
| `Jfn%d_return` / `Jfn%d_freturn` | fn γ/ω | `Jfn%d_γ` / `Jfn%d_ω` |

**Sprint B-221 — NET Greek labels (22 sites in emit_byrd_net.c):**

| Old | Port | New |
|---|---|---|
| `Nn%d_nam_ok` | γ | `Nn%d_nam_γ` |
| `Nn%d_dol_ok` | γ | `Nn%d_dol_γ` |
| `Nn%d_arb_loop` | β | `Nn%d_arb_β` |
| `Nn%d_arb_done` | γ | `Nn%d_arb_γ` |
| `Npat%d_tok` | stmt γ | `Npat%d_γ` |
| `Npat%d_fail` | stmt ω | `Npat%d_ω` |
| `Npat%d_retry` | scan β | `Npat%d_β` |
| `Nfn%d_return` / `Nfn%d_freturn` | fn γ/ω | `Nfn%d_γ` / `Nfn%d_ω` |

**Sprint B-222 — Local variable alignment across all four emit_pat_node functions:**

Goal: same concept = same name in all four backends. Names should be readable English words, not abbreviations. `i`, `j`, `k` are fine for loop counters.

**emit_pat_node parameters — canon names:**

| Concept | C | ASM | JVM | NET | Canon |
|---|---|---|---|---|---|
| stmt pointer | `s` | `stmt` | `s` | `s` | `s` — ASM rename `stmt→s` |
| subject (string name / slot) | `subj` | `subj` | `loc_subj` | `loc_subj` | `subj` (C/ASM pass name; JVM/NET pass slot index — different types, same word) |
| subject length | `subj_len` | `subj_len_sym` | `loc_len` | `loc_len` | `subj_len` — ASM rename `subj_len_sym→subj_len`; JVM/NET rename `loc_len→subj_len` |
| cursor | `cursor` | `cursor` | `loc_cursor` | `loc_cursor` | `cursor` — JVM/NET rename `loc_cursor→cursor` |
| capture slot allocator | (depth) | — | `p_cap_local` | `p_next_int` / `p_next_str` | `cap_slot` — JVM rename `p_cap_local→cap_slot`; NET rename `p_next_int→cap_slot`, drop `p_next_str` |

**emit_pat_node local variables — canon names per node type:**

| Concept | C | JVM | NET | Canon |
|---|---|---|---|---|
| literal string value | `s` | `s` | `s` | `s` ✅ |
| literal string length | `slen` | `slen` | `slen` | `slen` ✅ |
| uid for this node | `u` (in emit_stmt) / implicit | `uid` | `uid` | `uid` — C rename `u→uid` in emit_stmt |
| capture-before cursor | — | `loc_before` | `loc_before` | `cursor_before` — both rename `loc_before→cursor_before` |
| variable name string | `varname` | `varname` | `varname` | `varname` ✅ |
| escaped name buffer | `nameesc` | `nameesc` | — | `nameesc` ✅ |
| gamma label buffer | `alpha_lbl` etc (C uses Label type) | `lbl_inner_ok` / `lbl_ok` | `lbl_ok` | `gamma_lbl` — align JVM/NET to descriptive names: `gamma_lbl`, `omega_lbl`, `retry_lbl`, `success_lbl`, `fail_lbl` |
| alt right-branch label | — | `lbl_try_right` | varies | `right_lbl` |
| arb loop label | — | `lbl_arb_loop` | `lbl_loop` | `loop_lbl` |
| arb done label | — | `lbl_arb_done` | `lbl_done` | `done_lbl` |
| proto buffer | `pbuf` | `pbuf` | `pbuf` | `pbuf` ✅ |
| proto string | `proto` | `proto` | `proto` | `proto` ✅ |
| entry label string | `el` | `el` | `el` | `entry_lbl` — all rename `el→entry_lbl` |
| end label string | from goto | from goto | `gl` | `end_lbl` — NET rename `gl→end_lbl` |

**DO NOT mark M-EMITTER-NAMING ✅ until B-220 + B-221 + B-222 all complete.**

---

## Last Session Summary

**Session B-223 — M-ASM-RUNG8 ✅ complete:**
- Root cause: &ALPHABET is a 256-byte binary string with NUL at index 0; NUL-terminated char* representation broke REPLACE/SIZE.
- Fix: added `uint32_t slen` to DESCR_t padding (struct stays 16 bytes, zero ABI change); `BSTRVAL(s,len)` macro; `descr_slen()` helper.
- NV_SET_fn("ALPHABET") now uses BSTRVAL(alphabet,256). _b_SIZE uses slen for binary strings. REPLACE_fn uses descr_slen() + binary_mode preserves NUL bytes for positional alignment.
- 810_replace 3/3, 811_size 3/3, 812_dupl 3/3. Invariants: 100/106 C + 26/26 ASM hold. HEAD `1d0a983`.

## Active Milestones (next 5)

| ID | Status | Notes |
|----|--------|-------|
| M-ASM-RUNG11 | ❌ 2/7 | ITEM lvalue emitter fix + PROTOTYPE/VALUE verify — B-212 |
| M-ASM-LIBRARY | ❌ | Gates on RUNG11 |
| M-SC-CORPUS-R2 | ❌ | do_procedure body emission fix (sc_cf.c) — F-211 |
| M-JVM-CROSSCHECK | ❌ | 89/92 (J-208 progress) |
| M-NET-R1 | ❌ | 74/82 NET — ARB backtrack SEQ-omega bug (N-205 WIP) |

Full milestone history → [PLAN.md](PLAN.md)

---

## Concurrent Sessions

| Session | Branch | Focus |
|---------|--------|-------|
| B-212 | `asm-backend` | M-ASM-RUNG11 |
| F-210 | `main` | M-SC-CORPUS-R2 |
| J-208 | `jvm-backend` | M-JVM-CROSSCHECK (89/92) |
| N-206 | `net-backend` | M-NET-CROSSCHECK — 102/110; ARRAY/TABLE/DATA + roman next |
| D-156 | `net-perf-analysis` | M-NET-PERF |

Per RULES.md: `git pull --rebase` before every push. Update only your row in PLAN.md NOW table.
