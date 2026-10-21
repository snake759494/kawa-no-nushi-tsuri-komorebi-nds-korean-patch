import sys,os
from desmume.emulator import DeSmuME
rom=os.path.abspath(sys.argv[1]); pat=bytes.fromhex(sys.argv[2])
e=DeSmuME(); e.volume_set(0); e.open(rom)
hits=[]
found=None
for f in range(900):
    e.cycle(with_joystick=False)
    if f%10==0:
        ram=bytes(e.memory.unsigned[0x02000000:0x02400000])
        i=ram.find(pat)
        if i>=0:
            found=0x02000000+i; print('frame',f,'at',hex(found)); break
if found:
    def cb(addr,size):
        pc=e.memory.register_arm9.pc
        if len(hits)<20: hits.append((hex(addr),hex(pc)))
    e.memory.register_read(found+8,cb,1)
    for f in range(300): e.cycle(with_joystick=False)
    print(hits)
e.destroy()
