"""OAM 덤프로 스프라이트 합성 + 각 픽셀의 VRAM 바이트 위치 맵."""
import json,struct
from PIL import Image
SIZES={0:[(8,8),(16,16),(32,32),(64,64)],1:[(16,8),(32,8),(32,16),(64,32)],2:[(8,16),(8,32),(16,32),(32,64)]}
def compose(prefix,eng,sel=None,boundary=None):
    d=json.load(open(prefix+'.json'))[eng]; v=open(prefix+'_%s_vram.bin'%eng,'rb').read()
    p=open(prefix+'_%s_pal.bin'%eng,'rb').read()
    pal=[[(((c&31)<<3),((c>>5)&31)<<3,((c>>10)&31)<<3) for c in struct.unpack_from('<16H',p,k*32)] for k in range(16)]
    dc=d['dispcnt']; one_d=(dc>>4)&1; bnd=32<<((dc>>20)&3) if boundary is None else boundary
    im=Image.new('RGB',(256,192),(255,0,255)); loc={}; blocks=[]
    for s in d['sprites']:
        if sel and not sel(s): continue
        w,h=SIZES[s['shape']][s['size']]
        base=s['tile']*bnd
        blocks.append((base,w*h//2))
        for ty in range(h//8):
            for tx in range(w//8):
                toff=base+((ty*(w//8)+tx)*32 if one_d else (ty*32+tx)*32)
                for y in range(8):
                    for x in range(8):
                        b=toff+y*4+x//2; val=(v[b]>>(4*(x&1)))&15
                        X=(s['x']+tx*8+x)&511; Y=(s['y']+ty*8+y)&255
                        if X<256 and Y<192 and val:
                            im.putpixel((X,Y),pal[s['pal']][val]); loc[(X,Y)]=(b,x&1)
    compose.blocks=blocks
    return im,loc
