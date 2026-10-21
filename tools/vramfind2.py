import sys,os,collections; sys.path.insert(0,'tools')
from desmume.emulator import DeSmuME
import ndspy.rom,rln
romp=os.path.abspath(sys.argv[1])
e=DeSmuME(); e.volume_set(0); e.open(romp); e.savestate.load_file(sys.argv[2])
for _ in range(10): e.cycle(with_joystick=False)
v=bytes(e.memory.unsigned[0x06200000:0x06220000])+bytes(e.memory.unsigned[0x06600000:0x06620000])
e.destroy()
tiles=set(v[i:i+32] for i in range(0,len(v),32) if v[i:i+32].count(0)<20)
r=ndspy.rom.NintendoDSRom.fromFile(romp); hits=collections.Counter()
for i,f in enumerate(r.files):
    n=r.filenames.filenameOf(i)
    if not n or not (n.endswith('.arc') or n.endswith('.rln')): continue
    d=bytes(f); d=rln.decode(d) if n.endswith('.rln') else d
    for en in rln.entries(d):
        raw=d[en['off']:en['off']+en['size']]
        for k in range(0,len(raw)-31,32):
            if raw[k:k+32] in tiles: hits[(n,en['name'],en['type'])]+=1
for k,c in hits.most_common(25): print(k,c)
