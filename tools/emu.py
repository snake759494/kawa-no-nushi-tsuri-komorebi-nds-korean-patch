# 창 없는 DeSmuME 코어. 사용: emu.py rom script.json  (actions 목록)
import sys,json,os
from desmume.emulator import DeSmuME
from desmume.controls import Keys,keymask
rom=os.path.abspath(sys.argv[1]); acts=json.load(open(sys.argv[2],encoding='utf8'))
os.makedirs('shots',exist_ok=True)
e=DeSmuME(); e.volume_set(0); e.open(rom)
def fr(n):
  for _ in range(n): e.cycle(with_joystick=False)
for a in acts:
  if 'load' in a: e.savestate.load_file(a['load'])
  m=0
  for k in a.get('keys','').split('+'):
    if k: m|=keymask(getattr(Keys,'KEY_'+k.upper()))
  rep=a.get('rep',1)
  for _ in range(rep):
    if m: e.input.keypad_add_key(m)
    if 'touch' in a: e.input.touch_set_pos(*a['touch'])
    fr(a.get('hold',4 if (m or 'touch' in a) else 0))
    if m: e.input.keypad_rm_key(m)
    if 'touch' in a: e.input.touch_release()
    fr(a.get('wait',30))
  if 'shot' in a: e.screenshot().save('shots/'+a['shot']+'.png')
  if 'save' in a: e.savestate.save_file(a['save'])
  if 'dump' in a:
    open(a['dump'],'wb').write(bytes(e.memory.unsigned[0x02000000:0x02400000]))
e.destroy()
