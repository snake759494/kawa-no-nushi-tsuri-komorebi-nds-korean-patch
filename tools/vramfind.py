import sys,os; sys.path.insert(0,'tools')
from desmume.emulator import DeSmuME
import ndspy.rom,rln
romp=os.path.abspath(sys.argv[1])
e=DeSmuME(); e.volume_set(0); e.open(romp)
e.savestate.load_file(sys.argv[2])
for _ in range(10): e.cycle(with_joystick=False)
vr={}
for base in (0x06000000,0x06200000,0x06400000,0x06600000):
    vr[base]=bytes(e.memory.unsigned[base:base+0x20000])
e.destroy()
r=ndspy.rom.NintendoDSRom.fromFile(romp)
hits={}
for i,f in enumerate(r.files):
    n=r.filenames.filenameOf(i)
    if not n or not (n.endswith('.arc') or n.endswith('.rln')): continue
    d=bytes(f); d=rln.decode(d) if n.endswith('.rln') else d
    for en in rln.entries(d):
        raw=d[en['off']:en['off']+en['size']]
        for k in range(0,len(raw)-64,512):
            chunk=raw[k:k+64]
            if chunk.count(0)>40: continue
            for base,v in vr.items():
                j=v.find(chunk)
                if j>=0: hits.setdefault((n,en['name'],en['type']),set()).add(hex(base+j))
for k,v in hits.items(): print(k,sorted(v)[:4],len(v))
