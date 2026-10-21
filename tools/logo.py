"""타이틀 로고(type0 8bpp 선형 비트맵) 한글 재작성. 위쪽 장식은 유지하고 글자판을 다시 그린다."""
import struct,os
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import type0
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F=lambda n,s: ImageFont.truetype(os.path.join(ROOT,n),s)

def text_layer(size,text,font,xy,fill_top,fill_bot,inner,outer,inner_w,outer_w,shadow=None,sh_off=(0,2)):
    """RGBA 레이어에 그라데이션 글자 + 2중 테두리 + 그림자."""
    W,H=size
    mask=Image.new('L',size,0); ImageDraw.Draw(mask).text(xy,text,font=font,fill=255)
    mask=mask.point(lambda v:255 if v>=110 else 0)
    def grow(m,r):
        return m.filter(ImageFilter.MaxFilter(r*2+1)) if r>0 else m
    m_in=grow(mask,inner_w); m_out=grow(m_in,outer_w)
    out=Image.new('RGBA',size,(0,0,0,0))
    if shadow:
        sh=m_out.transform(size,Image.AFFINE,(1,0,-sh_off[0],0,1,-sh_off[1]))
        out.paste(Image.new('RGBA',size,shadow),(0,0),sh)
    out.paste(Image.new('RGBA',size,outer),(0,0),m_out)
    out.paste(Image.new('RGBA',size,inner),(0,0),m_in)
    bb=mask.getbbox() or (0,0,W,H)
    grad=Image.new('RGBA',size)
    gd=ImageDraw.Draw(grad)
    for y in range(H):
        t=min(1,max(0,(y-bb[1])/max(1,bb[3]-bb[1])))
        c=tuple(int(fill_top[i]*(1-t)+fill_bot[i]*t) for i in range(3))+(255,)
        gd.line([(0,y),(W,y)],fill=c)
    out.paste(grad,(0,0),mask)
    return out

def quantize(img,pal,keep):
    """RGBA → 팔레트 인덱스(투명=keep 픽셀 유지)."""
    W,H=img.size; px=img.load(); res=[row[:] for row in keep]
    cache={}
    for y in range(H):
        for x in range(W):
            r,g,b,a=px[x,y]
            if a<128: continue
            k=(r>>3,g>>3,b>>3)
            if k not in cache:
                best=min(range(1,len(pal)),key=lambda i:(pal[i][0]-r)**2+(pal[i][1]-g)**2+(pal[i][2]-b)**2)
                cache[k]=best
            res[y][x]=cache[k]
    return res

def build(b,scale,keep_top,lines):
    """b: 원본 type0 데이터, keep_top: 이 y 미만은 원본 유지(장식), lines: [(text,font,y,style)]"""
    w,h,bpp,npx,po=type0.info(b)
    pal=type0.pal(b[po:po+512])
    raw=b[4:4+npx]
    grid=[[raw[y*w+x] if y<keep_top else 0 for x in range(w)] for y in range(h)]
    layer=Image.new('RGBA',(w,h),(0,0,0,0))
    for text,font,y,st in lines:
        tw=font.getlength(text)
        l=text_layer((w,h),text,font,((w-tw)/2,y),**st)
        layer=Image.alpha_composite(layer,l)
    grid=quantize(layer,pal,grid)
    out=bytearray(b)
    out[4:4+npx]=bytes(v for row in grid for v in row)
    return bytes(out),layer
