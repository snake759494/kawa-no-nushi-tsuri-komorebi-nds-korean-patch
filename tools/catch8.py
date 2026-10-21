import sys,os,struct
sys.path.insert(0,'tools')
from desmume.emulator import DeSmuME
from desmume.controls import Keys,keymask
import emusrv_dump
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
e=DeSmuME(); e.volume_set(0); e.open(os.path.abspath(sys.argv[1])); e.savestate.load_file(os.path.join(W,'states',sys.argv[2]))
seq=[]
def fr(n):
    for _ in range(n): e.cycle(with_joystick=False)
def key(k):
    m=keymask(getattr(Keys,'KEY_'+k.upper())); e.input.keypad_add_key(m); fr(4); e.input.keypad_rm_key(m)
for k,w in seq:
    if k: key(k)
    fr(w)
found=0
def yellow(im):
    px=im.load(); c=0
    for y in range(85,124,2):
        for x in range(120,256,2):
            r,g,b_=px[x,y][:3]
            if r>220 and g>180 and b_<80: c+=1
    return c
for i in range(2400):
    if i%10==0: key('a')
    e.cycle(with_joystick=False)
    if i%3==0:
        im=e.screenshot()
        if yellow(im)>8:
            emusrv_dump.dump(e,os.path.join(W,'dumps','eff%d'%found)); im.save(os.path.join(W,'shots','eff%d.png'%found)); found+=1
            if found>=4: break
            fr(20)
print('found',found)
e.destroy()
