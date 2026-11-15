const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(process.argv[2],'utf8');
const code=source.split('\n').find(l=>l.startsWith('lanes.forEach(l=>{l.el.addEventListener'));
assert(code);
function fixture(){let serial=0;const timers=new Map(),handlers={},calls=[];const button={addEventListener:(n,f)=>handlers[n]=f,setPointerCapture:()=>{},hasPointerCapture:()=>true,releasePointerCapture:()=>{}};
const lane={el:{addEventListener:()=>{}},stopButton:button,buffer:{fixture:true}};
vm.runInNewContext(code,{lanes:[lane],trackTap:()=>{},setTimeout:f=>{timers.set(++serial,f);return serial},clearTimeout:id=>timers.delete(id),clearLane:l=>{l.buffer=null;calls.push('clear')},stopLane:()=>calls.push('stop')});
return {timers,calls,lane,event:(type,id)=>handlers[type]?.({type,pointerId:id}),flush:()=>{for(const [id,f] of [...timers]){timers.delete(id);f()}}};}
let f=fixture();f.event('pointerdown',1);f.event('pointerdown',2);f.event('pointerup',2);f.event('pointerup',1);const pending=f.timers.size;f.flush();const orphan=f.calls.includes('clear');
if(process.argv.includes('--original')){assert(orphan);console.log(JSON.stringify({original_orphan_clear:orphan,pending_after_both_up:pending}));process.exit();}
assert(!orphan);assert(f.lane.buffer);assert.equal(pending,0);
const cases=['both_up_no_clear'];
for(const end of ['pointercancel','lostpointercapture']){f=fixture();f.event('pointerdown',1);f.event('pointerdown',2);f.event(end,1);f.flush();assert.deepEqual(f.calls,[]);assert(f.lane.buffer);cases.push(end+'_no_clear');}
f=fixture();f.event('pointerdown',1);f.event('pointerup',1);f.flush();assert.deepEqual(f.calls,['stop']);cases.push('single_tap_stop');
f=fixture();f.event('pointerdown',1);f.flush();f.event('pointerup',1);assert.deepEqual(f.calls,['clear']);cases.push('single_hold_clear_once');
f=fixture();f.event('pointerdown',1);f.event('pointerdown',2);f.event('pointerup',2);f.flush();assert.deepEqual(f.calls,['clear']);f.event('pointerup',1);cases.push('second_pointer_cannot_release_owner');
f=fixture();f.event('pointerdown',1);f.event('pointercancel',1);f.event('pointerdown',2);f.event('pointerup',2);f.flush();assert.deepEqual(f.calls,['stop']);cases.push('cancel_then_new_pointer');
console.log(JSON.stringify({cases,passed:cases.length,audio:false,real_data_touched:false}));
