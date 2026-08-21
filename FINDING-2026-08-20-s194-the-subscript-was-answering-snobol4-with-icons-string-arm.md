# FINDING — s194, seat8 (`/home/claude8`, Claude Opus 5), queue row `subscript-silent-accept`

## THE SUBSCRIPT WAS ANSWERING SNOBOL4 WITH ICON'S STRING ARM, AND THE SILENT ACCEPT WAS THE MILD HALF

**One line:** `rt_subscript_var` is shared by every frontend, and its `DT_S`/`DT_SNUL` arm is Icon's
legal substring variable — so a SNOBOL4 subscript on a plain unset variable *failed silently* and a
SNOBOL4 subscript on a **non-null string returned a character**, where SPITBOL raises ERROR 235 for
both. Cured with two faces over one body, selected by a mark the lowerer stamps.

---

## 1. WHAT THE ROW SAID, AND THE HALF IT DID NOT SEE

The brief named four programs (`corpus/programs/snobol4/parser/idx_{simple,multi,nested,in_assign_lhs}`)
where SCRIP produces **nothing and exits 0** while the oracle raises `ERROR 235 -- subscripted operand
is not table or array`. All four reproduce exactly as briefed.

⛔ **THE FALSE ACCEPT IS NOT THE WORST OF IT, AND THE ROW'S FOUR WITNESSES ALL SIT ON THE MILD SIDE
OF THE DEFECT.** Every one of them subscripts an **unset** variable, i.e. the null string, and a null
string has no character to return, so the failure is silent. Give the same variable a value and the
defect changes character completely:

```
        A = 'hello'
        X = A[2]         →  oracle: ERROR 235      SCRIP (before): X = 'e', program runs on
        DATA('P(X,Y)') ; Q = P(1,2) ; Z = Q[1]
                         →  oracle: ERROR 235      SCRIP (before): Z = 1, program runs on
```

That is a **silent wrong answer**, not a silent skip — the same direction, one rung worse. A cure
scoped to "refuse the null string" would have passed the row's original DONE-WHEN and left it.

⭐ **HQ INDEPENDENTLY REACHED THE SAME CONCLUSION AND WIDENED THE ROW'S DONE-WHEN TO IT** (inbox
ruling on `a-subscript-icon-collision`, this row's predecessor ask): *"A DONE-WHEN that can be
satisfied by a wrong fix is a defective DONE-WHEN."* The rule enforced here is the manual's, not the
witnesses': **ARRAY or TABLE or ERROR 235.**

---

## 2. ROOT CAUSE — ONE SHARED ARM, TWO LANGUAGES, OPPOSITE CONTRACTS

`c_rt_subscript_var` (pattern_match.c) derefs the base and dispatches on its datatype. Its arms are:
`DT_A` array · `DT_T` table · `DT_DATA` list/record · **`DT_S`/`DT_SNUL` the substring trap** ·
tail `subscript_get`. The string arm is **Icon's `s[i]`** — a legal substring variable — and Icon's
`L[i]` is the `DT_DATA` arm. SNOBOL4 has neither construct; SPITBOL v3.7 admits exactly two
subscriptable objects (p.89-90 Array referencing, p.94-95 Table referencing) and Appendix D 235 is
what every other operand gets.

So the bug is not a missing message and not a missing table — it is **one function serving two
languages whose contracts disagree on the same operand**, with the permissive contract winning by
default.

⛔ **HQ'S OWN BRIEF WAS WRONG ABOUT THE MESSAGE TABLE AND SAID SO FIRST:** there is no 2xx family in
`rt.c`. `core_err_msgs[]` covers codes 1..39 and every code ≥40 supplies its text at the call site.
The conclusion (missing check) survived; the reason did not.

---

## 3. THE CURE — TWO FACES OVER ONE BODY, SELECTED AT LOWER

Per HQ's ruling (option **(b)**, the `bb_ab_slot_for` ONE-ALLOCATOR-TWO-FACES precedent of s172):

| where | what |
|---|---|
| `src/lower/lower_snobol4.c` | `sx_sub_container_only()` stamps `IR_LIT(sub).sval = "container-only"` on **every** 2-operand `IR_SUBSCRIPT` this lowerer builds — both the TT_IDX rvalue arm and `sx_subscript_lv` (the assignment-target road). Killswitch `SCRIP_SUB_AGG=0` leaves the mark off. |
| `src/templates/bb_subscript.cpp` | reads the mark and swaps **the callee and nothing else** — same four registers, same `DT_FAIL` omega test, same result store, both arms (ZD and legacy) and **both media** (`x86("call", name, ptr)` renders the symbol in TEXT and the baked pointer in BINARY). |
| `src/runtime/pattern_match.c` | `rt_subscript_var_container_only` — deref, test `DT_A`-or-`DT_T`, `kwb_error(235, ...)` otherwise, and on success hand the **original** base to `rt_subscript_var`. |

⛔ **THE STRICT FACE IS SIX LINES AND CONTAINS NO COPY OF THE SUBSCRIPT BODY.** Because it forwards
the original descriptors, every arm below it — including the **RTX veneer's array and table fast
paths** — is reached by exactly the bytes it has always been reached by. There is no second spelling
to keep in step, which is the disease the previous seat8 row (`prototype-spelled-twice`) was about.

⛔ **THE TEST IS AN ALLOW-LIST, NOT A REFUSE-LIST.** `!= DT_A && != DT_T`. A refuse-list would have
to be extended for every datatype SCRIP grows; the manual admits two containers and gives one error
for everything else, so the allow-list is the honest spelling and nothing can slip past it.

⛔ **THE DEREF BEFORE THE TEST IS REQUIRED, NOT DEFENSIVE.** A SNOBOL4 base arrives as the VARREF the
lowerer built (`IR_VAR`, `--dump-ir`); only `rt_deref` can say what it holds. It is idempotent here.

⛔ **CHAINED SUBSCRIPTS PASS FOR A MEASURED REASON.** `A[1,2]` lowers to **two** 2-operand
`IR_SUBSCRIPT`s (`--dump-ir`, and the emitted `.s` carries two `rt_subscript_var` calls, not one
`subscript_get2`), so the second one's base is the NAMETRAP the first returned — it derefs to the
**row array**, answers `DT_A`, and passes. Placing the test after the deref is what makes that work.

⛔ **OUT-OF-BOUNDS STILL FAILS AND MUST NEVER BECOME AN ERROR.** Manual p.90 makes looping until an
array reference fails the idiomatic traversal. The bounds test stays inside the `DT_A` arm, *below*
this gate. The gate is about the operand's TYPE only.

⛔ **`kwb_error`, NOT `core_runtime_error`** — the OPSYN rung measured this one row earlier:
`core_runtime_error`'s conversion arm needs a pushed `jmp_buf` that only the EVAL boundary supplies,
so it would print-and-exit where a program that set `&ERRLIMIT` expects statement failure. At the
default `&ERRLIMIT` of 0 `kwb_error` calls it anyway, so the default arm terminates exactly as the
oracle does.

⛔ **NAMES CARRY NO LANGUAGE**, per HQ: the mark says what the subscript *does*, and `.sc` (Snocone)
and `.reb` (Rebus) ride this lowerer and inherit the rule **because they inherit SPITBOL's aggregate
rule with it** — not because of who they are. `test_gate_emit_no_lang.sh` green.

---

## 4. THE FOURTH-ROAD CENSUS HQ DEMANDED — ONLY ONE ROAD IS LIVE

HQ required a census of the three spellings of the read path before curing any one of them.

| road | verdict | receipt |
|---|---|---|
| `subscript_get` via `bb_idx_get.cpp` | **DEAD** | `IR_IDX` is not in `IR.h`; `emit.cpp` has no dispatch for it; its sole producer is `lower_snobol4.gz5-parked-41b53078.c`, which the Makefile does not build |
| `c_rt_subscript_var` via `bb_subscript.cpp` | **THE LIVE ROAD** — cured | every SNOBOL4/Snocone/Rebus subscript, both modes |
| hand asm `rtx_icnsub.S:149` | **NOT A PARALLEL ROAD — DOWNSTREAM** | reached only *after* the container test passed, so its `.Lsub_string` and `DT_DATA` arms are unreachable from SNOBOL4 by construction |

Corroborated by sweeping every checked-in `.s` outside `programs/lon`: `rt_subscript_var` **38**
files, `subscript_get` **0**, and `subscript_get2` + `rt_section_var` appear in **6** files that are
**all `benchmarks/icon`**.

---

## 5. RECEIPTS (pristine `make`, RT_OPT `-O0`, one build, arms selected by the killswitch)

**Oracle-pinned probes, byte-identical to `sbl -bf` in BOTH modes:**
- `corpus/probe/subscript/sub_container_only.sno` — the **11-face census**: null string, string,
  integer, real, pattern, name, expression, code, data-object → **235**; array and table → accepted.
- `corpus/probe/subscript/sub_shapes.sno` — the four witness shapes (rvalue, multi, nested, **lvalue**)
  plus the same three shapes on real arrays as the positive control.

⭐ **BOTH PROBES ARE PROVEN LIVE, NOT INERT** — the s193 `leafsib` lesson applied in the same session
it was written: under `SCRIP_SUB_AGG=0` the census **diverges on every line** (and the old code did
not even fail consistently — a REAL operand hit `Error 3 Erroneous array or table reference`).

**Icon hard gate:** `corpus/probe/subscript/icn_string_subscript.icn` — string subscript, string-subscript
**assignment**, list read/write, table read — green both modes. `test_smoke_icon` 14/14 both modes;
`test_gate_icn_semicolon_required` all three locks; `test_gate_icn_no_stack` 0. ⛔ Its `.ref` is
SCRIP-pinned and **says so in the file**: this seat has `icont` but not `iconx`.

**Boards, one build, A/B by killswitch (post-rebase onto seat3 `40a5b01a` + seat4 `apply-snodef-m4`):**

| | treatment | control (`SCRIP_SUB_AGG=0`) |
|---|---|---|
| corpus m3 | 338 / 2 | 339 / 1 |
| corpus m4 | 337 / 2 SKIP 1 | 337 / 2 SKIP 1 — **identical by name** |
| crosscheck m3 / m4 / DIVERGE | 319/1 · 318/1 · 0 | **identical by name** |

Gates green: `emit_no_lang`, BOTH-MEDIUM ratchet **0/0**, `icn_semicolon_required`, `icn_no_stack`.
Smokes: icon 14/14, rebus 4/0, snocone 4/1 (**the 1 is pre-existing — identical in both arms**).

**RULES step-4 regen, all six, attributed file-by-file by recompiling each mover under both arms:**
**25 movers are this rung's** and every one is an array/table/subscript program (`array_sum`,
`table_access`, `091_array_create_access`, `1110_array_1d`, `1113_table`, snocone `A05_table`,
`calculator`, `json`, `treebank`, …); **21 are standing drift** the regen swept up. The whole of this
rung's emission delta, in every one of the 25, is the callee name:
`call rt_subscript_var@PLT` → `call rt_subscript_var_container_only@PLT`.

---

## 6. ⛔ THE ONE RED THIS LEAVES — `demo_treebank` m3 — IS A DIFFERENT BUG, AND TWO SEATS FOUND IT INDEPENDENTLY

The sole corpus mover is `demo_treebank` in m3. Root-caused, and it is **not** the subscript rung:

SPITBOL's `( e1, e2, ..., en )` is **Alternative Evaluation** (manual v3.7 p.99): elements evaluated
left to right, value is the **first that succeeds**, later elements evaluated **only** on failure,
the whole thing fails only if all fail. Oracle-pinned every line in
`corpus/probe/vlist/vlist_expr_alternation.sno` (checked in **RED with a live-oracle ref**).

`treebank.sno` grows its backing array with `a = ARRAY('0:' (IDENT(a(x)) 0, size * 2 - 1))`. Once the
list is non-empty, element 1 fails, the statement fails, the array never grows, and **every element
subscript lands on a null base** — which the old permissive subscript turned into a silent FAIL.
`treebank.ref` is only `matched bytes=327`, so the program went **GREEN while building an empty tree**.

⭐ **SEAT3 REACHED THE IDENTICAL CONCLUSION ONE SESSION EARLIER** (s193, row `treebank-allocating`,
board 02:38: *"treebank.sno m3 prints its PINNED 'matched bytes=327' while building an EMPTY TREE —
the .ref is true of a program that does no work"*). Two seats, two roads in, one cause. Seat3 landed
the lowering **default OFF** (`SCRIP_VLIST_ALT=1`) because the ζ-spine retreat contract reads every
ω as "leave the statement", and asked row `vlist-alt-zeta-depth` for the partner.

⛔ **MEASURED ON THIS TREE, ALL FOUR ARMS — TREEBANK CANNOT BE GREEN UNTIL BOTH LAND:**

| arm | treebank m3 |
|---|---|
| default (container-only on, VLIST off) | `Error 235` — honest |
| `SCRIP_VLIST_ALT=1` | **SIGSEGV, core dumped** |
| `SCRIP_SUB_AGG=0` (control) | `matched bytes=327` — the false green |
| `SCRIP_VLIST_ALT=1 SCRIP_SUB_AGG=0` | **SIGSEGV, core dumped** |

So this rung did not break treebank; it **stopped treebank lying**. Its m4 arm was already red in
**both** arms before this rung. Disposition asked of HQ (`q-subscript-silent-accept`); recommendation
was **land it** — reverting restores a false green in the dangerous direction, and the real repair is
seat3's `vlist-alt-zeta-depth`, not a permissive subscript.

---

## 7. ADJACENT, NOT FIXED, NAMED SO IT IS NOT RE-DERIVED

- ⛔ **`g_core_err_stmt` NEVER ADVANCES.** Every runtime error in this tree reports **`in statement 0`**
  — 235 and pre-existing 164 alike (`OUTPUT='one'; OUTPUT='two'; PROTOTYPE('abc')` → `Error 164 in
  statement 0`). The oracle names the real statement. Not this row; worth a row.
- **`DATATYPE` of a program-defined object answers upper-case:** SCRIP `LIST`, oracle `list`
  (measured on the treebank list library). Not this row.

---

## 8. ⭐ THE GENERALISABLE PART

**When one runtime helper serves two languages, the arm that is *legal in the other language* is
invisible to every test the first language owns.** The four witnesses in this row all subscripted an
unset variable, so the shared Icon string arm returned nothing and the defect read as "silence" —
the whole class looked like a missing error message. It was a **wrong arm**, and one line of source
(`A = 'hello'` instead of leaving `A` unset) turned a silent skip into a wrong answer. When a cure
lands in a shared helper, sweep the **datatype space of the operand**, not the witness set: the
11-face census is the whole reason this cure is right rather than merely green.

---

**Tree:** SCRIP (this rung) · corpus `probe/subscript/`, `probe/vlist/`, 25 `.s` · `.github` this file.
**No new global variable. No new opcode. No template medium branch. Killswitch `SCRIP_SUB_AGG=0`
reverts verbatim by stopping the lowerer stamping, so the selector falls back by construction.**
