import sys,os,collections
from desmume.emulator import DeSmuME
from desmume.controls import Keys,keymask
rom=os.path.abspath(sys.argv[1])
e=DeSmuME(); e.volume_set(0); e.open(rom)
seen=[]
def mk(name):
    def cb(addr,size):
        r=e.memory.register_arm9
        vals=[r.r0,r.r1,r.r2,r.r3]
        info=[]
        for v in vals:
            if 0x2000000<=v<0x2400000:
                raw=bytes(e.memory.unsigned[v-0x20:v+0x10])
                info.append(raw.hex())
        seen.append((name,[hex(x) for x in vals],info))
    return cb
for a in [0x2096b28,0x2096bac,0x2096c28,0x2096cc8,0x2096ce8,0x20975ec]:
    e.memory.register_exec(a,mk(hex(a)))
def fr(n):
    for _ in range(n): e.cycle(with_joystick=False)
def key(k):
    m=keymask(getattr(Keys,'KEY_'+k)); e.input.keypad_add_key(m); fr(4); e.input.keypad_rm_key(m)
fr(600); n0=len(seen); key('START'); fr(120); key('A'); fr(120); key('A'); fr(60); key('A'); fr(60)
for s in seen[n0:]: print(s[0],s[1]); [print('   ',x) for x in s[2]]
e.destroy()
