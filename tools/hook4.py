import sys,os,collections,json
from desmume.emulator import DeSmuME
from desmume.controls import Keys,keymask
rom=os.path.abspath(sys.argv[1])
e=DeSmuME(); e.volume_set(0); e.open(rom)
hits=collections.Counter()
def cb(addr,size):
    r=e.memory.register_arm9
    if hits: return
    sp=r.sp
    st=[e.memory.unsigned.read_long(sp+4*i) for i in range(40)]
    hits[(hex(addr),hex(r.pc),hex(r.lr),tuple(hex(x) for x in st if 0x2000000<=x<0x2140000))]+=1
base=0x06200000+1088*32
for a in range(base,base+0x200,4): e.memory.register_write(a,cb,4)
def fr(n):
    for _ in range(n): e.cycle(with_joystick=False)
def key(k):
    m=keymask(getattr(Keys,'KEY_'+k)); e.input.keypad_add_key(m); fr(4); e.input.keypad_rm_key(m)
fr(600); key('START'); fr(120); key('A'); fr(120); key('A'); fr(60); key('A'); fr(60)
for k,v in hits.most_common(15): print(k,v)
e.destroy()
