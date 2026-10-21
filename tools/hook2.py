import sys,os,collections
from desmume.emulator import DeSmuME
rom=os.path.abspath(sys.argv[1]); addrs=[int(x,16) for x in sys.argv[2:]]
e=DeSmuME(); e.volume_set(0); e.open(rom)
hits=collections.Counter()
def cb(addr,size):
    r=e.memory.register_arm9
    hits[(hex(addr),hex(r.pc),hex(r.lr))]+=1
for a in addrs: e.memory.register_write(a,cb,4)
for f in range(1500): e.cycle(with_joystick=False)
for k,v in hits.most_common(30): print(k,v)
e.destroy()
