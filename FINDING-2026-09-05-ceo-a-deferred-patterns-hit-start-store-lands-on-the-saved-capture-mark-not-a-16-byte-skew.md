# FINDING 2026-09-05 (ceo): the gimpel SNOREAD/READ/FASTBAL crashes were a deferred pattern's hit-start store landing on the saved capture mark -- not a 16-byte calling-convention skew

Written 2026-09-05 09:54 CDT. Row `bb-define-16b-stack-skew-corrupts-exit-jump-target` (ceo under QUARTET round 2, closed under FLEET-8). Landed SCRIP `bc336dfb3`, corpus `a3dc7a375`.

## CLAIM
The row's GOAL named a 16-byte skew between a DEFINE'd function's entry write and its exit reads. Measured at the instruction level, the entry and exit ports use matching offsets and the function's spine is balanced; the crash is inside the match end's success path. A REPLACEMENT statement whose pattern is a pattern-valued VARIABLE carrying a capture (`P = 'b' . F` then `B P = 'X'`) dies in both modes; the same variable without replacement, and the same capture written inline, are clean.

## MECHANISM (ASM-DIFF-FIRST, then one watchpoint)
- The deferred-pattern box's success landing emits `lea rcx,[g_scan_hit_start]; mov rax,[rcx]; mov dword ptr [rsp+160], eax` unless `emit_match_owns_startd()` holds. That predicate counted only statement-frame-hosted starts and ignored the RBP-frame regime (`emit_match_rbp()`, on by default), under which the begin box always keeps the start delta at `[rbp-40]`.
- At that landing rsp sits inside the live match frame, and `rsp+160` is exactly `[rbp-8]`: the pushed r12, the cas pointer the match end passes to `c_rt_match_end_all` as the deferred-capture mark. A dword store of hit start 0 turns the mark `0x7fffee1ff030` into `0x7fff00000000`; `rt_dcap_pump` walks entries from there (SIGSEGV in C), or a thunk entry jumps there (the SNOREAD witness's RIP=0x7fff00000000 that read as "a garbage jump target").
- Cure (emit.cpp): a match owns its start delta whenever it has an RBP frame. Second collision cured in the same commit: the match end's replacement arm wrote repl_start (dword) into `[rbp-48]`, the begin box's own qword slot; it now lives in the unused upper dword of the start-delta qword (`[rbp-36]`).

## EVIDENCE
- Ablation ladder of twelve witnesses (match / replacement / pattern variable / capture into the result variable / into a global / RETURN vs fall-through / inline vs deferred / a pattern built by a DEFINE'd function) -- all match `sbl -bf` in both modes after the cure; four of them are the gate `test_gate_sno_deferred_replacement_keeps_its_capture_mark.sh` (corpus `dcap_repl_*.sno` + oracle-cut refs, refs re-cut live; RED 8 of 8 arms on origin `0a1a94239`, GREEN after). In `make test` after the runtime-DEFINE gate.
- gimpel: 79/126 both modes, zero crashes (was 59/126) -- READ and FASTBAL drivers green; SNOREAD no longer crashes but diverges after its second extracted statement (transfer to undefined label ERROR: `IDENT(SNO_BUFFER)` fails where the oracle's buffer is null) -> successor row `snobol4-snoread-buffer-not-consumed-after-a-deferred-replacement-in-a-function` (hq_C).
- SNOBOL4 master m3 1777/0/0 · m4 1777/0/0; `break_len_array_replace_1` turned green (promoted in all marker places, with the two entries promoted yesterday whose ALL.xfail blocks were still standing). Snocone smoke 5/5. Icon master board 599/601 both modes (held).
- A side defect found while running testpgms by hand in the package directory: `OUTPUT('TITLE',6,'(14H1THIS IS HAND ,110A1)')` made SCRIP create a FILE named by the FORTRAN format string -> row `snobol4-output-third-argument-is-a-format-not-a-file-name` (hq_P). Never run a suite program by hand in its package directory; the runner's scratch cwd exists for this reason.

## LESSON FOR THE STANDARD
A crash whose faulting address "looks like garbage" is a value with a story: `0x7fff00000000` is a pointer with its low dword zeroed, i.e. a dword store on a qword slot. Read the value before theorising a frame skew. The mechanism a row's GOAL asserts is a hypothesis until the faulting instruction is read.
