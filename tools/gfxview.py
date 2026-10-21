import sys,os,struct; sys.path.insert(0,'tools')
import ndspy.rom,rln
from PIL import Image
r=ndspy.rom.NintendoDSRom.fromFile("../Kawa no Nushi Tsuri - Komorebi no Tani, Seseragi no Uta (Japan).nds")
os.makedirs('gfxview',exist_ok=True)
def pal(b):
    out=[]
    for i in range(0,len(b),2):
        v=struct.unpack_from('<H',b,i)[0]
        out.append(((v&31)<<3,((v>>5)&31)<<3,((v>>10)&31)<<3))
    return out
def sheet(data,p,cols=32,bpp=4):
    tb=32 if bpp==4 else 64
    n=len(data)//tb; rows=(n+cols-1)//cols
    im=Image.new('RGB',(cols*8,rows*8))
    px=im.load()
    for t in range(n):
        for y in range(8):
            for x in range(8):
                if bpp==4: v=(data[t*32+y*4+x//2]>>(4*(x&1)))&15
                else: v=data[t*64+y*8+x]
                c=p[v] if v<len(p) else (255,0,255)
                if v==0: c=(255,0,255) if bpp==4 else c
                px[(t%cols)*8+x,(t//cols)*8+y]=c
    return im
for fn in sys.argv[1:]:
    d=bytes(r.getFileByName(fn))
    if fn.endswith('.rln'): d=rln.decode(d)
    es=rln.entries(d)
    pals=[e for e in es if e['type'] in (7,8,9,10)]
    for k,e in enumerate(es):
        if e['type'] in (7,8,9,10,16,17,19,13,14,18): continue
        raw=d[e['off']:e['off']+e['size']]
        pe=next((p for p in pals if p['name']==e['name']),pals[0] if pals else None)
        p=pal(d[pe['off']:pe['off']+pe['size']]) if pe else [(i*17,i*17,i*17) for i in range(16)]
        bpp=8 if (pe and pe['size']>=0x200 and e['type'] in (3,4,5,11)) else 4
        im=sheet(raw,p,bpp=bpp)
        im.save('gfxview/%s_%d_%s_t%d.png'%(fn.replace('/','_'),k,e['name'],e['type']))
