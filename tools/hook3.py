import sys,os
from desmume.emulator import DeSmuME
import ndspy.rom
romp=os.path.abspath(sys.argv[1]); fn=sys.argv[2]
r=ndspy.rom.NintendoDSRom.fromFile(romp); d=bytes(r.getFileByName(fn))
pats=[(o,d[o:o+12]) for o in range(0x40,len(d)-12,len(d)//8)]
e=DeSmuME(); e.volume_set(0); e.open(romp)
for f in range(1500):
    e.cycle(with_joystick=False)
    ram=bytes(e.memory.unsigned[0x02000000:0x02400000])
    for o,p in pats:
        i=ram.find(p)
        if i>=0: print('frame',f,'fileoff',hex(o),'ram',hex(0x2000000+i)); pats.remove((o,p))
    if not pats: break
e.destroy()
