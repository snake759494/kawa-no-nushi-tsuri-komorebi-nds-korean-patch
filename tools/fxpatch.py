"""낚시 대결 효과음 글자(battle_icon.rln o_pow2l/o_pow2r, 64x64 4bpp 1D 스프라이트) 한글화."""
import rln,gfxtext
from PIL import Image,ImageDraw,ImageFilter
L=[('꾸',(14,8,44,32))]
SPR={
 0:[('꾸',(14,8,44,32))],
 1:[('꾸',(14,8,44,30)),('욱',(14,30,44,48))],
 2:[('꾸',(14,8,44,28)),('욱',(14,28,44,46)),('!',(14,46,44,58))],
 3:[('꾸',(16,30,52,63))],5:[('꾸',(16,30,52,63))],7:[('꾸',(16,30,52,63))],
 6:[('욱',(14,0,42,26))],
 8:[('욱',(14,0,42,24)),('!',(14,24,42,34))],
 9:[('끄',(6,10,58,58))],
 11:[('끄',(6,12,58,63))],13:[('끄',(6,12,58,63))],
 12:[('윽',(6,0,50,32))],
 14:[('윽',(6,0,50,34)),('!',(6,34,50,56))],
}
def setpx(raw,k,x,y,v):
    t=(y//8)*8+x//8; b=k*2048+t*32+(y%8)*4+x//2; s=4*(x&1)
    raw[b]=(raw[b]&~(15<<s))|(v<<s)
def glyph(ch,w,h):
    """박스에 맞춘 굵은 글자 마스크(채움) + 외곽선 마스크."""
    size=h+4
    while True:
        f=gfxtext.ttf('NanumSquareNeo-eHv.ttf',size)
        bb=f.getbbox(ch)
        if (bb[2]-bb[0])<=w-2 and (bb[3]-bb[1])<=h-2 or size<8: break
        size-=1
    im=Image.new('L',(w,h),0); dr=ImageDraw.Draw(im)
    dr.text(((w-(bb[2]-bb[0]))/2-bb[0],(h-(bb[3]-bb[1]))/2-bb[1]),ch,font=f,fill=255)
    fill=im.point(lambda v:255 if v>=110 else 0)
    out=fill.filter(ImageFilter.MaxFilter(3))
    return fill,out,im
def patch(rom):
    fn='battle/battle_icon.rln'
    d=bytearray(rln.decode(bytes(rom.getFileByName(fn))))
    for e in rln.entries(bytes(d)):
        if e['name'] not in ('o_pow2l','o_pow2r') or e['type']!=11: continue
        raw=bytearray(d[e['off']:e['off']+e['size']])
        for k,items in SPR.items():
            for y in range(64):
                for x in range(64): setpx(raw,k,x,y,0)
            for ch,(x0,y0,x1,y1) in items:
                fill,out,aa=glyph(ch,x1-x0,y1-y0)
                for y in range(y1-y0):
                    for x in range(x1-x0):
                        if fill.getpixel((x,y)): v=3 if aa.getpixel((x,y))>=200 else 2
                        elif out.getpixel((x,y)): v=1
                        else: continue
                        setpx(raw,k,x0+x,y0+y,v)
        d[e['off']:e['off']+e['size']]=raw
    rom.setFileByName(fn,rln.encode(bytes(d)))
