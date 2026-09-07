import json,hashlib
from pathlib import Path
p=Path('music-findings');old=json.loads((p/'resynthesis-results.json').read_text());b=json.loads((p/'boundary-results.json').read_text())
rows=[]
for i,n in enumerate(old['notes']):
 rows.append({'id':f'P{i+1:02d}','midi_pitch_candidate':n['midi_pitch'],'observed_presence_start_s':n['start_s'],'observed_presence_end_s':n['end_s'],'attack_time_s':None,'release_time_s':None,'instrument':None,'status':'pitch_presence_only','reason':'Contour agreement does not establish physical attack or release. Intervals must not be automatically converted to notes separated by rests.'})
revision={'schema':'sound-lab.pitch-presence.v1','source_sha256':old['source_sha256'],'scope_seconds':[615,630],'previous_candidate_midi_status':'diagnostic_render_only_not_transcription','pitch_regions':rows,'f_component_gap_evidence':b['analysis'],'unresolved':['fundamental octave','source/instrument attribution','attack and release times','possible reattacks under sustained spectral energy'],'next_valid_use':'Use presence regions as search constraints for original-audio verification; do not export a performance MIDI from these alone.'}
(p/'pitch-presence-revision.json').write_text(json.dumps(revision,indent=2)+'\n')
assert len(rows)==16 and all(x['attack_time_s'] is None and x['release_time_s'] is None for x in rows)
# Plot measured component against earlier candidate's explicit sound/silence.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(11,3.6))
a=b['analysis'][1];bins=a['half_second_bins']
ax.plot([r['start_s']-615+.25 for r in bins],[r['f_component_db'] for r in bins],color='#155f87',marker='.',label='Original: 335-362 Hz component (0.5 s median)')
for n in old['notes']:
 if n['midi_pitch']==65:ax.axvspan(n['start_s']-615,n['end_s']-615,color='#d68622',alpha=.3)
ax.axvspan(-1,-.5,color='#d68622',alpha=.3,label='Earlier candidate: F4 active')
ax.set(xlim=(0,15),xlabel='Seconds after 10:15',ylabel='STFT band amplitude (dB)',title='Metamorphoses: candidate gaps do not establish rests')
ax.legend(loc='lower left',fontsize=8);ax.grid(alpha=.15);fig.tight_layout();fig.savefig(p/'f-component-presence.png',dpi=180)
print('16 annotations revised; graph generated')
