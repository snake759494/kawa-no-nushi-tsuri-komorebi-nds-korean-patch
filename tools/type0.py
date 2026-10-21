import struct
from PIL import Image
def info(b):
    bpp=8 if b[1]==0xff else 4
    w=256 if b[0]==0 else b[0]   # 0 = 256
    h=struct.unpack_from('<H',b,2)[0]
    if h==0: h=256
    npx=w*h*bpp//8
    pal_off=4+npx
    return w,h,bpp,npx,pal_off
def pal(b):
    return [(((v&31)<<3),((v>>5)&31)<<3,((v>>10)&31)<<3) for v in struct.unpack('<%dH'%(len(b)//2),b)]
def render(b,tiled=True):
    w,h,bpp,npx,po=info(b)
    p=pal(b[po:])
    raw=b[4:4+npx]
    im=Image.new('RGB',(w,h)); px=im.load()
    for i in range(w*h):
        v=raw[i] if bpp==8 else (raw[i//2]>>(4*(i&1)))&15
        if tiled:
            t=i//64; q=i%64; x=(t%(w//8))*8+q%8; y=(t//(w//8))*8+q//8
        else: x,y=i%w,i//w
        px[x,y]=p[v] if v<len(p) else (255,0,255)
    return im
