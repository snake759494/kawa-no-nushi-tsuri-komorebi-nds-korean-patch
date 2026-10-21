import ndspy.rom,sys,os
r=ndspy.rom.NintendoDSRom.fromFile(sys.argv[1]); os.makedirs('work/ext',exist_ok=True)
for n in sys.argv[2:]:
    open('work/ext/'+n.replace('/','_'),'wb').write(r.getFileByName(n))
open('work/ext/arm9.bin','wb').write(r.arm9)
for i,o in enumerate(r.loadArm9Overlays().values()): pass
import ndspy.codeCompression as cc
open('work/ext/arm9.dec','wb').write(cc.decompress(r.arm9) if True else r.arm9)
print(len(r.arm9Overlays if hasattr(r,'arm9Overlays') else []), r.arm9OverlayTable[:10])
