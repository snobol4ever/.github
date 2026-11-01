S='/tmp/claude-1000/-home-claude-cto/25cbd82c-ea4e-46bc-9ee6-3c52fc5dcc1f/scratchpad'
p='/home/claude_cto/.github/ARCH-HEADER-SPLIT.md'; t=open(p).read()
ab=open(S+'/page-3-2.txt').read().strip('\n')
# 1. the as-built paragraph after 3.2's design paragraph
i=t.index('**3.2 emit.h'); j=t.index('\n\n', i)
t=t[:j]+'\n\n'+ab+t[j:]
# 2. the emit.h row of section 4
k=t.index('| `src/emitter/emit.h` |'); e=t.index('\n', k)
row=t[k:e]; cells=row.split(' | ')
cells[3]=cells[3]+' -- AS BUILT 2026-10-31 (the cto): ten families as the census ruled them (section 3.2 as built); emit_sm.h, bb_walk_states.h and bb_pl_call_state.h not created, their contents dead; emit.h 57 lines, fan-in 2, users 3'
t=t[:k]+' | '.join(cells)+t[e:]
# 3. the preamble's row
k=t.index('| `src/templates/bb/bb_template_common.h` |'); e=t.index('\n', k)
row=t[k:e]; cells=row.split(' | ')
cells[3]='DELETED by step 3 (2026-10-31, the cto): re-cut to four includes and three prototypes it was an umbrella the ruling gate read as unused in 120 templates; every template includes emitter/emit_state.h (the _ and g_emit it names) and emitter/emit_str.h where it names IF or FOR, the latter admitted to the base set in the preamble\'s place; the zls_ prototypes were frame_layout.h\'s, GZ_CELL_OFF had no user, CSET_CHAIN_MAX is emit_knobs.h\'s (the plan here was: ' + cells[3] + ')'
t=t[:k]+' | '.join(cells)+t[e:]
# 4. the roll-out row 3's last cell
k=t.index('\n| 3 | emit.h'); e=t.index('\n', k+1)
row=t[k+1:e]; cells=row.split(' | ')
cells[-1]=cells[-1].replace(' |', '').rstrip()+'; AS BUILT: emit.h fan-in 2 (users 3), emit_state.h and emit_str.h base, the preamble deleted, 297 of 297 objects identical, landed [SCRIP_HASH] |'
t=t[:k+1]+' | '.join(cells)+t[e:]
open(p,'w').write(t); print('page: 3.2 as built, the emit.h and preamble rows, the roll-out row 3')
