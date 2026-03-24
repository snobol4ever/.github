# FRONTEND-ICON.md — Tiny-ICON Frontend (L3)

Tiny-ICON is a frontend for snobol4x targeting the x64 ASM backend.
SNOBOL4 and Icon share a bloodline — Griswold invented both.
The Byrd Box IR is the bridge: same four ports (α/β/γ/ω), new Icon frontend
feeding the same TINY pipeline. Goal-directed generators map directly to Byrd boxes.

**Session trigger phrase:** `"I'm playing with ICON"`
**Session prefix:** `I` (e.g. I-1, I-2, I-3)
**Backend:** x64 ASM only — same NASM/ELF64 pipeline as SNOBOL4
**Location:** `src/frontend/icon/` in snobol4x

*Session state → this file §NOW. Backend → BACKEND-X64.md.*

---

## §NOW — Session State

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **ICON frontend** | `main` I-10 — SESSIONS_ARCHIVE pruned; fixes documented, not yet applied | `54031a5` I-7 | M-ICON-CORPUS-R3 |

### Next session checklist (I-11)

```bash
git clone https://github.com/snobol4ever/snobol4x
git clone https://github.com/snobol4ever/.github
# Read FRONTEND-ICON.md §NOW — two exact patches below, apply both
# Rebuild icon_driver, test t01_gen → must output 1\n2\n3\n4
# Write R3 corpus (5 tests), run full suite, fire M-ICON-CORPUS-R3
```

**M-ICON-CORPUS-R3 spec:** user procedures with return; user-defined generators with suspend.
rung03_suspend already has t01_gen (upto/4). R3 adds t01_return through t05_gen_compose.

### I-9 findings — exact patches for icon_emit.c (apply first thing I-10)

**Fix 1 — `left_is_value` (~line 598 of icon_emit.c):**

Replace:
```c
IcnNode *left_child = n->children[0];
int left_is_value = (left_child->kind == ICN_VAR || left_child->kind == ICN_INT ||
                     left_child->kind == ICN_STR || left_child->kind == ICN_CALL);
```
With:
```c
IcnNode *left_child = n->children[0];
int left_call_is_gen = 0;
if (left_child->kind == ICN_CALL && left_child->nchildren >= 1) {
    const char *fn = left_child->children[0]->val.sval;
    for (int k = 0; k < user_proc_count; k++)
        if (strcmp(user_procs[k], fn) == 0) { left_call_is_gen = user_proc_is_gen[k]; break; }
}
int left_is_value = (left_child->kind == ICN_VAR || left_child->kind == ICN_INT ||
                     left_child->kind == ICN_STR ||
                     (left_child->kind == ICN_CALL && !left_call_is_gen));
```

**Fix 2 — rsp save/restore in `emit_call` is_gen docall block (~line 498):**

In the `if(is_gen){` docall block, declare a `saved_rsp` BSS slot and save/restore around the jmp trampoline. The β resume path also needs a save before jumping back in. Full patch:

```c
if(is_gen){
    char after_call[64]; snprintf(after_call,sizeof after_call,"icon_%d_after_call",id);
    char caller_ret[80]; snprintf(caller_ret,sizeof caller_ret,"icn_%s_caller_ret",fname);
    char saved_rsp[64]; snprintf(saved_rsp,sizeof saved_rsp,"icn_%d_saved_rsp",id);
    bss_declare(saved_rsp);
    E(em,"    mov     byte [rel icn_suspended], 0\n");
    E(em,"    mov     [rel %s], rsp\n", saved_rsp);
    E(em,"    lea     rax, [rel %s]\n", after_call);
    E(em,"    mov     [rel %s], rax\n", caller_ret);
    E(em,"    jmp     icn_%s\n", fname);
    Ldef(em,after_call);
    E(em,"    mov     rsp, [rel %s]\n", saved_rsp);   // ← restore before icn_failed check
    // ... rest unchanged (movzx icn_failed, etc.)
```

And in the β path (`Ldef(em,b)` / `if(is_gen)` block, ~line 485), reconstruct the saved_rsp name from `id` and save before jumping:

```c
/* β: resume if suspended */
Ldef(em,b);
if(is_gen){
    char saved_rsp_b[64]; snprintf(saved_rsp_b,sizeof saved_rsp_b,"icn_%d_saved_rsp",id);
    E(em,"    ; call β — resume if suspended, fail otherwise\n");
    E(em,"    movzx   rax, byte [rel icn_suspended]\n");
    E(em,"    test    rax, rax\n");
    E(em,"    jz      %s\n", ports.fail);
    E(em,"    mov     [rel %s], rsp\n", saved_rsp_b);  // ← save before resuming
    E(em,"    mov     byte [rel icn_suspended], 0\n");
    E(em,"    jmp     [rel icn_suspend_resume]\n");
```

**Key insight:** The `saved_rsp_b` in the β block and `saved_rsp` in the docall block use the same BSS slot name (`icn_%d_saved_rsp` with the same `id`). The β save updates it so that after the next yield→`after_call`, `mov rsp, [saved_rsp]` restores correctly again. Both must use the same `id` — which they do since `id` is the node ID assigned to this ICN_CALL.

---



## Why Icon fits the Byrd Box model

Icon's goal-directed evaluation: every expression either succeeds (generating
zero or more values) or fails. Expressions suspend and resume like generators.
This maps exactly to α (proceed) / β (resume) / γ (succeed) / ω (fail).

JCON (Townsend + Proebsting, 1999) proved this: Icon → JVM via Byrd Box IR.
Proebsting's 1996 paper gives the exact four-port templates for every Icon
operator. Those templates are our emitter spec.

---

## Design Decisions

### Backend: x64 ASM (not C, not JVM)

The x64 ASM backend already has full arithmetic (`E_ADD/SUB/MPY/DIV`),
string ops (`CAT2_*` macros), function calls (`APPLY_FN_N`), and the
complete Byrd box macro library. Icon's expression evaluation maps directly
onto existing machinery. No new backend needed.

JCON source is kept as structural reference (especially `irgen.icn` for
four-port wiring patterns) but is not built or run.

### Explicit semicolons — no auto-insertion

Icon's standard lexer inserts semicolons automatically on newlines.
We reject this. Every expression sequence requires an explicit `;`.
This is a deliberate deviation: simpler lexer, explicit structure,
no hanging-continuation ambiguity. Icon source in the corpus is patched
to use explicit semicolons.

### Shared IR — reuse everything with exact semantics

| Icon concept | Shared IR node | Notes |
|---|---|---|
| Integer literal | `E_ILIT` | exact reuse |
| Real literal | `E_FLIT` | exact reuse |
| String literal | `E_QLIT` | exact reuse |
| Cset literal | `E_QLIT` + DT_CS tag | cset = typed string |
| Variable | `E_VART` | exact reuse |
| `+` `-` `*` `/` `%` `^` | `E_ADD/SUB/MPY/DIV/EXPOP` | exact reuse |
| Unary `-` | `E_MNS` | exact reuse |
| `\|\|` string concat | `E_CONC` | exact reuse |
| Function call | `E_FNC` | exact reuse |
| `upto(cs)` | `BREAK` Byrd box | semantic match |
| `many(cs)` | `SPAN` Byrd box | semantic match |
| cset membership | `ANY` Byrd box | semantic match |
| `\|` value alternation | new `E_ICN_ALT` | NOT `E_OR` (that is pattern alt) |
| `to` generator | new `E_TO` node | paper §4.4 template |
| `every`/`do` | new `E_EVERY` node | drives generator to exhaustion |
| `if`/`then`/`else` | new `E_ICN_IF` node | paper §4.5 indirect goto |
| `suspend` | new `E_SUSPEND` node | β port of enclosing call |
| `?` string scan | new `E_SCAN` node | explicit cursor threading |

New nodes added to `sno2c.h` `EKind` enum. SNOBOL4 frontend unaffected.

### `bounded` flag — deferred optimization

JCON threads a `bounded` flag through every IR node: when an expression
is in a "value needed" context (assignment RHS, argument), the resume/fail
ports are omitted entirely. This is the highest-value optimization but is
deferred until after correctness. All four ports emitted unconditionally
for now.

---

## Milestone Table

| ID | Trigger | Depends on | Status |
|----|---------|-----------|--------|
| **M-ICON-ORACLE** | `icont` + `iconx` built from icon-master; `every write(1 to 5);` → `1\n2\n3\n4\n5` confirmed; `icon-master/bin/icont` and `iconx` committed to path | — | ✅ `d364a14` |
| **M-ICON-LEX** | `icon_lex.c` tokenizes all Tier 0 tokens; `icon_lex_test.c` 100% pass | M-ICON-ORACLE | ✅ 108/108 I-2 |
| **M-ICON-PARSE-LIT** | Parser produces correct AST for all Proebsting §2 paper examples | M-ICON-LEX | ✅ 21/21 I-2 |
| **M-ICON-EMIT-LIT** | Byrd box for `ICN_INT` matches paper §4.1 exactly | M-ICON-PARSE-LIT | ✅ I-2 |
| **M-ICON-EMIT-TO** | `to` generator; `every write(1 to 5);` → `1..5` | M-ICON-EMIT-LIT | ✅ I-2 |
| **M-ICON-EMIT-ARITH** | `+` `*` `-` `/` binary ops via existing `E_ADD/MPY/SUB/DIV` | M-ICON-EMIT-TO | ✅ I-2 |
| **M-ICON-EMIT-REL** | `<` `>` `=` `~=` relational with goal-directed retry | M-ICON-EMIT-ARITH | ✅ I-2 |
| **M-ICON-EMIT-IF** | `if`/`then`/`else` with indirect goto `gate` temp (paper §4.5) | M-ICON-EMIT-REL | ✅ I-2 |
| **M-ICON-EMIT-EVERY** | `every E do E` drives generator to exhaustion | M-ICON-EMIT-IF | ✅ I-2 |
| **M-ICON-CORPUS-R1** | Rung 1: all paper examples pass; oracle = `icont`+`iconx` from icon-master | M-ICON-EMIT-EVERY | ✅ 6/6 I-2 |
| **M-ICON-PROC** | `procedure`/`end`, `local`, `return`, `fail`, call expressions | M-ICON-CORPUS-R1 | ✅ `d736059` I-6 |
| **M-ICON-SUSPEND** | `suspend E` inside procedure = user-defined generator | M-ICON-PROC | ✅ `d736059` I-6 |
| **M-ICON-CORPUS-R2** | Rung 2: arithmetic generators, relational filtering | M-ICON-SUSPEND | ✅ `54031a5` I-7 |
| **M-ICON-CORPUS-R3** | Rung 3: user procedures with return; user-defined generators | M-ICON-CORPUS-R2 | ❌ |
| **M-ICON-STRING** | `ICN_STR`, `\|\|` concat via `CAT2_*` macros | M-ICON-CORPUS-R3 | ❌ |
| **M-ICON-SCAN** | `E ? E` string scanning; explicit cursor threading | M-ICON-STRING | ❌ |
| **M-ICON-CSET** | Cset literals; `upto`→`BREAK`, `many`→`SPAN`, membership→`ANY` | M-ICON-SCAN | ❌ |
| **M-ICON-CORPUS-R4** | Rung 4: string operations and scanning | M-ICON-CSET | ❌ |

---


## Session Bootstrap (every I-session)

```bash
git clone https://github.com/snobol4ever/snobol4x
git clone https://github.com/snobol4ever/.github
bash /home/claude/snobol4x/setup.sh
# Reference material already present from session planning:
# /home/claude/jcon-master/   — JCON source (irgen.icn, ir.icn)
# /home/claude/icon-master/   — Icon reference impl (icont oracle)
```

Read FRONTEND-ICON.md §NOW for current milestone. Start at first ❌.

---

## Reference

- Proebsting 1996 paper: "Simple Translation of Goal-Directed Evaluation" — four-port templates §4.1–4.5
- JCON source: `jcon-master/tran/` — `ir.icn` (IR vocab), `irgen.icn` (wiring patterns)
- Icon reference impl: `icon-master/src/icont/` — `tparse.c`, `tcode.c`
- Prolog frontend (structural template): `src/frontend/prolog/`
- ASM macro library: `src/runtime/asm/snobol4_asm.mac`
- MISC.md §JCON — lessons learned from JCON study

---

---

## JCON + icon-master Analysis

Full pre-coding reference (irgen.icn four-port patterns, ir.icn IR vocab, tcode.c AST names,
ByrdBox golden C reference, deltas vs plan, rung 1 runtime requirements) →
**[JCON-ANALYSIS.md](JCON-ANALYSIS.md)**

