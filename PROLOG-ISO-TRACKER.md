# PROLOG-ISO-TRACKER.md — mechanical coverage: SCRIP vs gprolog 1.4.5

**GENERATED — do not hand-edit.** Regenerate: `bash ../harness/scripts/audit_prolog_iso_coverage.sh`
Source of truth: `refs/gprolog-master/src/BipsPl/*.pl` `set_bip_name/2` self-declarations.
Rung: GOAL-PROLOG-BB.md LADDER A → PL-ISO-10. **100% == UNASSIGNED 0 AND core-open 0.**

## Scoreboard

| metric | count |
|--------|-------|
| gprolog public exports (total) | 312 |
| DONE (SCRIP admits) | 297 (95%) |
| RUNG-ASSIGNED | 15 |
| **UNASSIGNED** | **0** |
| core scope | 237 |
| gprolog-ext scope | 75 |
| **core still open** | **5** |

## Per-file coverage

| file | scope | done | total | open |
|------|-------|------|-------|------|
| `stream.pl` | core | 42 | 43 | 1 |
| `os_interf.pl` | gprolog-ext | 29 | 35 | 6 |
| `const_io.pl` | core | 30 | 30 | 0 |
| `char_io.pl` | core | 28 | 28 | 0 |
| `src_rdr.pl` | core | 21 | 22 | 1 |
| `read.pl` | core | 16 | 17 | 1 |
| `atom.pl` | core | 15 | 15 | 0 |
| `dec10io.pl` | core | 12 | 12 | 0 |
| `write.pl` | core | 12 | 12 | 0 |
| `debugger.pl` | gprolog-ext | 9 | 11 | 2 |
| `term_inl.pl` | core | 11 | 11 | 0 |
| `sockets.pl` | gprolog-ext | 8 | 8 | 0 |
| `assert.pl` | core | 6 | 6 | 0 |
| `file.pl` | gprolog-ext | 5 | 6 | 1 |
| `flag.pl` | core | 6 | 6 | 0 |
| `sort.pl` | core | 6 | 6 | 0 |
| `stat.pl` | gprolog-ext | 5 | 6 | 1 |
| `pretty.pl` | core | 5 | 5 | 0 |
| `consult.pl` | core | 3 | 4 | 1 |
| `le_interf.pl` | gprolog-ext | 4 | 4 | 0 |
| `random.pl` | gprolog-ext | 4 | 4 | 0 |
| `arith_inl.pl` | core | 2 | 3 | 1 |
| `call.pl` | core | 3 | 3 | 0 |
| `control.pl` | core | 3 | 3 | 0 |
| `print.pl` | core | 3 | 3 | 0 |
| `format.pl` | core | 2 | 2 | 0 |
| `oper.pl` | core | 2 | 2 | 0 |
| `pred.pl` | core | 2 | 2 | 0 |
| `expand.pl` | core | 1 | 1 | 0 |
| `pl_error.pl` | core | 1 | 1 | 0 |
| `t.pl` | gprolog-ext | 1 | 1 | 0 |

## UNASSIGNED — no rung owns these (must reach 0)  (0)

*(none)*

## RUNG-ASSIGNED — owned, not yet landed  (15)

| predicate | file | scope | home |
|-----------|------|-------|------|
| `current_evaluable/1` | `arith_inl.pl` | core | PL-ISO-12 |
| `write_default_include_file/1` | `consult.pl` | core | PL-ISO-13 |
| `trace/0` | `debugger.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `wam_debug/0` | `debugger.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `prolog_file_suffix/1` | `file.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `delete_directory/2` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `delete_file/2` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `fork_prolog/1` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `select/5` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `shell/0` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `unlink/2` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `read_line_to_chars/2` | `read.pl` | core | PL-ISO-7a |
| `sr_read_term/3` | `src_rdr.pl` | core | PL-ISO-7b |
| `statistics/0` | `stat.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `set_stream_alias/2` | `stream.pl` | core | PL-ISO-7b |

## DONE — admitted by SCRIP  (297)

| predicate | file | scope | home |
|-----------|------|-------|------|
| `evaluable_property/2` | `arith_inl.pl` | core |  |
| `succ/2` | `arith_inl.pl` | core |  |
| `abolish/1` | `assert.pl` | core |  |
| `asserta/1` | `assert.pl` | core |  |
| `assertz/1` | `assert.pl` | core |  |
| `clause/2` | `assert.pl` | core |  |
| `retract/1` | `assert.pl` | core |  |
| `retractall/1` | `assert.pl` | core |  |
| `atom_chars/2` | `atom.pl` | core |  |
| `atom_codes/2` | `atom.pl` | core |  |
| `atom_concat/3` | `atom.pl` | core |  |
| `atom_length/2` | `atom.pl` | core |  |
| `atom_property/2` | `atom.pl` | core |  |
| `char_code/2` | `atom.pl` | core |  |
| `current_atom/1` | `atom.pl` | core |  |
| `lower_upper/2` | `atom.pl` | core |  |
| `name/2` | `atom.pl` | core |  |
| `new_atom/1` | `atom.pl` | core |  |
| `new_atom/2` | `atom.pl` | core |  |
| `number_atom/2` | `atom.pl` | core |  |
| `number_chars/2` | `atom.pl` | core |  |
| `number_codes/2` | `atom.pl` | core |  |
| `sub_atom/5` | `atom.pl` | core |  |
| `call_det/2` | `call.pl` | core |  |
| `call_nth/2` | `call.pl` | core |  |
| `countall/2` | `call.pl` | core |  |
| `get_byte/1` | `char_io.pl` | core |  |
| `get_byte/2` | `char_io.pl` | core |  |
| `get_char/1` | `char_io.pl` | core |  |
| `get_char/2` | `char_io.pl` | core |  |
| `get_code/1` | `char_io.pl` | core |  |
| `get_code/2` | `char_io.pl` | core |  |
| `get_key/1` | `char_io.pl` | core |  |
| `get_key/2` | `char_io.pl` | core |  |
| `get_key_no_echo/1` | `char_io.pl` | core |  |
| `get_key_no_echo/2` | `char_io.pl` | core |  |
| `peek_byte/1` | `char_io.pl` | core |  |
| `peek_byte/2` | `char_io.pl` | core |  |
| `peek_char/1` | `char_io.pl` | core |  |
| `peek_char/2` | `char_io.pl` | core |  |
| `peek_code/1` | `char_io.pl` | core |  |
| `peek_code/2` | `char_io.pl` | core |  |
| `put_byte/1` | `char_io.pl` | core |  |
| `put_byte/2` | `char_io.pl` | core |  |
| `put_char/1` | `char_io.pl` | core |  |
| `put_char/2` | `char_io.pl` | core |  |
| `put_code/1` | `char_io.pl` | core |  |
| `put_code/2` | `char_io.pl` | core |  |
| `unget_byte/1` | `char_io.pl` | core |  |
| `unget_byte/2` | `char_io.pl` | core |  |
| `unget_char/1` | `char_io.pl` | core |  |
| `unget_char/2` | `char_io.pl` | core |  |
| `unget_code/1` | `char_io.pl` | core |  |
| `unget_code/2` | `char_io.pl` | core |  |
| `display_to_atom/2` | `const_io.pl` | core |  |
| `display_to_chars/2` | `const_io.pl` | core |  |
| `display_to_codes/2` | `const_io.pl` | core |  |
| `format_to_atom/3` | `const_io.pl` | core |  |
| `format_to_chars/3` | `const_io.pl` | core |  |
| `format_to_codes/3` | `const_io.pl` | core |  |
| `print_to_atom/2` | `const_io.pl` | core |  |
| `print_to_chars/2` | `const_io.pl` | core |  |
| `print_to_codes/2` | `const_io.pl` | core |  |
| `read_from_atom/2` | `const_io.pl` | core |  |
| `read_from_chars/2` | `const_io.pl` | core |  |
| `read_from_codes/2` | `const_io.pl` | core |  |
| `read_term_from_atom/3` | `const_io.pl` | core |  |
| `read_term_from_chars/3` | `const_io.pl` | core |  |
| `read_term_from_codes/3` | `const_io.pl` | core |  |
| `read_token_from_atom/2` | `const_io.pl` | core |  |
| `read_token_from_chars/2` | `const_io.pl` | core |  |
| `read_token_from_codes/2` | `const_io.pl` | core |  |
| `write_canonical_to_atom/2` | `const_io.pl` | core |  |
| `write_canonical_to_chars/2` | `const_io.pl` | core |  |
| `write_canonical_to_codes/2` | `const_io.pl` | core |  |
| `write_term_to_atom/3` | `const_io.pl` | core |  |
| `write_term_to_chars/3` | `const_io.pl` | core |  |
| `write_term_to_codes/3` | `const_io.pl` | core |  |
| `write_to_atom/2` | `const_io.pl` | core |  |
| `write_to_chars/2` | `const_io.pl` | core |  |
| `write_to_codes/2` | `const_io.pl` | core |  |
| `writeq_to_atom/2` | `const_io.pl` | core |  |
| `writeq_to_chars/2` | `const_io.pl` | core |  |
| `writeq_to_codes/2` | `const_io.pl` | core |  |
| `listing/0` | `consult.pl` | core |  |
| `listing/1` | `consult.pl` | core |  |
| `load/1` | `consult.pl` | core |  |
| `between/3` | `control.pl` | core |  |
| `for/3` | `control.pl` | core |  |
| `halt/1` | `control.pl` | core |  |
| `debug/0` | `debugger.pl` | gprolog-ext |  |
| `debugging/0` | `debugger.pl` | gprolog-ext |  |
| `leash/1` | `debugger.pl` | gprolog-ext |  |
| `nodebug/0` | `debugger.pl` | gprolog-ext |  |
| `nospy/1` | `debugger.pl` | gprolog-ext |  |
| `nospyall/0` | `debugger.pl` | gprolog-ext |  |
| `notrace/0` | `debugger.pl` | gprolog-ext |  |
| `spy/1` | `debugger.pl` | gprolog-ext |  |
| `spypoint_condition/3` | `debugger.pl` | gprolog-ext |  |
| `append/1` | `dec10io.pl` | core |  |
| `get/1` | `dec10io.pl` | core |  |
| `get0/1` | `dec10io.pl` | core |  |
| `put/1` | `dec10io.pl` | core |  |
| `see/1` | `dec10io.pl` | core |  |
| `seeing/1` | `dec10io.pl` | core |  |
| `seen/0` | `dec10io.pl` | core |  |
| `skip/1` | `dec10io.pl` | core |  |
| `tab/1` | `dec10io.pl` | core |  |
| `tell/1` | `dec10io.pl` | core |  |
| `telling/1` | `dec10io.pl` | core |  |
| `told/0` | `dec10io.pl` | core |  |
| `expand_term/2` | `expand.pl` | core |  |
| `absolute_file_name/2` | `file.pl` | gprolog-ext |  |
| `decompose_file_name/4` | `file.pl` | gprolog-ext |  |
| `is_absolute_file_name/1` | `file.pl` | gprolog-ext |  |
| `is_relative_file_name/1` | `file.pl` | gprolog-ext |  |
| `prolog_file_name/2` | `file.pl` | gprolog-ext |  |
| `argument_counter/1` | `flag.pl` | core |  |
| `argument_list/1` | `flag.pl` | core |  |
| `argument_value/2` | `flag.pl` | core |  |
| `current_prolog_flag/2` | `flag.pl` | core |  |
| `environ/2` | `flag.pl` | core |  |
| `set_prolog_flag/2` | `flag.pl` | core |  |
| `format/2` | `format.pl` | core |  |
| `format/3` | `format.pl` | core |  |
| `add_linedit_completion/1` | `le_interf.pl` | gprolog-ext |  |
| `find_linedit_completion/2` | `le_interf.pl` | gprolog-ext |  |
| `get_linedit_prompt/1` | `le_interf.pl` | gprolog-ext |  |
| `set_linedit_prompt/1` | `le_interf.pl` | gprolog-ext |  |
| `current_op/3` | `oper.pl` | core |  |
| `op/3` | `oper.pl` | core |  |
| `architecture/1` | `os_interf.pl` | gprolog-ext |  |
| `change_directory/1` | `os_interf.pl` | gprolog-ext |  |
| `copy_file/2` | `os_interf.pl` | gprolog-ext |  |
| `create_pipe/2` | `os_interf.pl` | gprolog-ext |  |
| `date_time/1` | `os_interf.pl` | gprolog-ext |  |
| `directory_files/2` | `os_interf.pl` | gprolog-ext |  |
| `exec/4` | `os_interf.pl` | gprolog-ext |  |
| `exec/5` | `os_interf.pl` | gprolog-ext |  |
| `file_exists/1` | `os_interf.pl` | gprolog-ext |  |
| `file_permission/2` | `os_interf.pl` | gprolog-ext |  |
| `file_property/2` | `os_interf.pl` | gprolog-ext |  |
| `host_name/1` | `os_interf.pl` | gprolog-ext |  |
| `make_directory/1` | `os_interf.pl` | gprolog-ext |  |
| `os_version/1` | `os_interf.pl` | gprolog-ext |  |
| `popen/3` | `os_interf.pl` | gprolog-ext |  |
| `prolog_pid/1` | `os_interf.pl` | gprolog-ext |  |
| `rename_file/2` | `os_interf.pl` | gprolog-ext |  |
| `send_signal/2` | `os_interf.pl` | gprolog-ext |  |
| `shell/1` | `os_interf.pl` | gprolog-ext |  |
| `shell/2` | `os_interf.pl` | gprolog-ext |  |
| `sleep/1` | `os_interf.pl` | gprolog-ext |  |
| `spawn/2` | `os_interf.pl` | gprolog-ext |  |
| `spawn/3` | `os_interf.pl` | gprolog-ext |  |
| `system/1` | `os_interf.pl` | gprolog-ext |  |
| `system/2` | `os_interf.pl` | gprolog-ext |  |
| `temporary_file/3` | `os_interf.pl` | gprolog-ext |  |
| `temporary_name/2` | `os_interf.pl` | gprolog-ext |  |
| `wait/2` | `os_interf.pl` | gprolog-ext |  |
| `working_directory/1` | `os_interf.pl` | gprolog-ext |  |
| `syntax_error_info/4` | `pl_error.pl` | core |  |
| `current_predicate/1` | `pred.pl` | core |  |
| `predicate_property/2` | `pred.pl` | core |  |
| `bind_variables/2` | `pretty.pl` | core |  |
| `name_query_vars/2` | `pretty.pl` | core |  |
| `name_singleton_vars/1` | `pretty.pl` | core |  |
| `numbervars/1` | `pretty.pl` | core |  |
| `numbervars/3` | `pretty.pl` | core |  |
| `get_print_stream/1` | `print.pl` | core |  |
| `print/1` | `print.pl` | core |  |
| `print/2` | `print.pl` | core |  |
| `get_seed/1` | `random.pl` | gprolog-ext |  |
| `random/1` | `random.pl` | gprolog-ext |  |
| `random/3` | `random.pl` | gprolog-ext |  |
| `set_seed/1` | `random.pl` | gprolog-ext |  |
| `char_conversion/2` | `read.pl` | core |  |
| `current_char_conversion/2` | `read.pl` | core |  |
| `last_read_start_line_column/2` | `read.pl` | core |  |
| `read/1` | `read.pl` | core |  |
| `read/2` | `read.pl` | core |  |
| `read_atom/1` | `read.pl` | core |  |
| `read_atom/2` | `read.pl` | core |  |
| `read_integer/1` | `read.pl` | core |  |
| `read_integer/2` | `read.pl` | core |  |
| `read_line_to_codes/2` | `read.pl` | core |  |
| `read_number/1` | `read.pl` | core |  |
| `read_number/2` | `read.pl` | core |  |
| `read_term/2` | `read.pl` | core |  |
| `read_term/3` | `read.pl` | core |  |
| `read_token/1` | `read.pl` | core |  |
| `read_token/2` | `read.pl` | core |  |
| `hostname_address/2` | `sockets.pl` | gprolog-ext |  |
| `socket/2` | `sockets.pl` | gprolog-ext |  |
| `socket_accept/3` | `sockets.pl` | gprolog-ext |  |
| `socket_accept/4` | `sockets.pl` | gprolog-ext |  |
| `socket_bind/2` | `sockets.pl` | gprolog-ext |  |
| `socket_close/1` | `sockets.pl` | gprolog-ext |  |
| `socket_connect/4` | `sockets.pl` | gprolog-ext |  |
| `socket_listen/2` | `sockets.pl` | gprolog-ext |  |
| `keysort/1` | `sort.pl` | core |  |
| `keysort/2` | `sort.pl` | core |  |
| `msort/1` | `sort.pl` | core |  |
| `msort/2` | `sort.pl` | core |  |
| `sort/1` | `sort.pl` | core |  |
| `sort/2` | `sort.pl` | core |  |
| `sr_change_options/2` | `src_rdr.pl` | core |  |
| `sr_close/1` | `src_rdr.pl` | core |  |
| `sr_current_descriptor/1` | `src_rdr.pl` | core |  |
| `sr_error_from_exception/2` | `src_rdr.pl` | core |  |
| `sr_get_error_counters/3` | `src_rdr.pl` | core |  |
| `sr_get_file_name/2` | `src_rdr.pl` | core |  |
| `sr_get_include_list/2` | `src_rdr.pl` | core |  |
| `sr_get_include_stream_list/2` | `src_rdr.pl` | core |  |
| `sr_get_module/3` | `src_rdr.pl` | core |  |
| `sr_get_position/3` | `src_rdr.pl` | core |  |
| `sr_get_size_counters/3` | `src_rdr.pl` | core |  |
| `sr_get_stream/2` | `src_rdr.pl` | core |  |
| `sr_new_pass/1` | `src_rdr.pl` | core |  |
| `sr_open/3` | `src_rdr.pl` | core |  |
| `sr_set_error_counters/3` | `src_rdr.pl` | core |  |
| `sr_write_error/2` | `src_rdr.pl` | core |  |
| `sr_write_error/4` | `src_rdr.pl` | core |  |
| `sr_write_error/6` | `src_rdr.pl` | core |  |
| `sr_write_message/4` | `src_rdr.pl` | core |  |
| `sr_write_message/6` | `src_rdr.pl` | core |  |
| `sr_write_message/8` | `src_rdr.pl` | core |  |
| `cpu_time/1` | `stat.pl` | gprolog-ext |  |
| `real_time/1` | `stat.pl` | gprolog-ext |  |
| `statistics/2` | `stat.pl` | gprolog-ext |  |
| `system_time/1` | `stat.pl` | gprolog-ext |  |
| `user_time/1` | `stat.pl` | gprolog-ext |  |
| `add_stream_alias/2` | `stream.pl` | core |  |
| `add_stream_mirror/2` | `stream.pl` | core |  |
| `at_end_of_stream/0` | `stream.pl` | core |  |
| `at_end_of_stream/1` | `stream.pl` | core |  |
| `character_count/2` | `stream.pl` | core |  |
| `close/1` | `stream.pl` | core |  |
| `close/2` | `stream.pl` | core |  |
| `close_input_atom_stream/1` | `stream.pl` | core |  |
| `close_input_chars_stream/1` | `stream.pl` | core |  |
| `close_input_codes_stream/1` | `stream.pl` | core |  |
| `close_output_atom_stream/2` | `stream.pl` | core |  |
| `close_output_chars_stream/2` | `stream.pl` | core |  |
| `close_output_codes_stream/2` | `stream.pl` | core |  |
| `current_alias/2` | `stream.pl` | core |  |
| `current_input/1` | `stream.pl` | core |  |
| `current_mirror/2` | `stream.pl` | core |  |
| `current_output/1` | `stream.pl` | core |  |
| `current_stream/1` | `stream.pl` | core |  |
| `flush_output/0` | `stream.pl` | core |  |
| `flush_output/1` | `stream.pl` | core |  |
| `line_count/2` | `stream.pl` | core |  |
| `line_position/2` | `stream.pl` | core |  |
| `open/3` | `stream.pl` | core |  |
| `open/4` | `stream.pl` | core |  |
| `open_input_atom_stream/2` | `stream.pl` | core |  |
| `open_input_chars_stream/2` | `stream.pl` | core |  |
| `open_input_codes_stream/2` | `stream.pl` | core |  |
| `open_output_atom_stream/1` | `stream.pl` | core |  |
| `open_output_chars_stream/1` | `stream.pl` | core |  |
| `open_output_codes_stream/1` | `stream.pl` | core |  |
| `remove_stream_mirror/2` | `stream.pl` | core |  |
| `seek/4` | `stream.pl` | core |  |
| `set_input/1` | `stream.pl` | core |  |
| `set_output/1` | `stream.pl` | core |  |
| `set_stream_buffering/2` | `stream.pl` | core |  |
| `set_stream_eof_action/2` | `stream.pl` | core |  |
| `set_stream_line_column/3` | `stream.pl` | core |  |
| `set_stream_position/2` | `stream.pl` | core |  |
| `set_stream_type/2` | `stream.pl` | core |  |
| `stream_line_column/3` | `stream.pl` | core |  |
| `stream_position/2` | `stream.pl` | core |  |
| `stream_property/2` | `stream.pl` | core |  |
| `setup_call_cleanup/3` | `t.pl` | gprolog-ext |  |
| `acyclic_term/1` | `term_inl.pl` | core |  |
| `copy_term/2` | `term_inl.pl` | core |  |
| `nb_setarg/3` | `term_inl.pl` | core |  |
| `setarg/3` | `term_inl.pl` | core |  |
| `setarg/4` | `term_inl.pl` | core |  |
| `subsumes_term/2` | `term_inl.pl` | core |  |
| `term_hash/2` | `term_inl.pl` | core |  |
| `term_hash/4` | `term_inl.pl` | core |  |
| `term_ref/2` | `term_inl.pl` | core |  |
| `term_variables/2` | `term_inl.pl` | core |  |
| `term_variables/3` | `term_inl.pl` | core |  |
| `display/1` | `write.pl` | core |  |
| `display/2` | `write.pl` | core |  |
| `nl/0` | `write.pl` | core |  |
| `nl/1` | `write.pl` | core |  |
| `write/1` | `write.pl` | core |  |
| `write/2` | `write.pl` | core |  |
| `write_canonical/1` | `write.pl` | core |  |
| `write_canonical/2` | `write.pl` | core |  |
| `write_term/2` | `write.pl` | core |  |
| `write_term/3` | `write.pl` | core |  |
| `writeq/1` | `write.pl` | core |  |
| `writeq/2` | `write.pl` | core |  |

