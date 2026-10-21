import ndspy.rom,sys,collections
r=ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
print(r.name,r.idCode,len(r.arm9),'ov9',len(r.loadArm9Overlays()))
def walk(f,p=''):
    for n in f.files:
        i=f.idOf(n) if hasattr(f,'idOf') else None
        yield p+n
    for n,sub in f.folders: yield from walk(sub,p+n+'/')
fs=list(walk(r.filenames))
ext=collections.Counter(x.rsplit('.',1)[-1] if '.' in x else '' for x in fs)
print(len(fs),ext.most_common(30))
for x in fs:
    print(x,len(r.getFileByName(x)))
