"""나눔스퀘어 네오 cBd 12px를 원본 글꼴 형식(16x16 셀, 4bpp, 11~12px 안티앨리어싱 3단계)으로 렌더링."""
from PIL import Image,ImageDraw,ImageFont
import os
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONT=os.path.join(ROOT,'NanumSquareNeo-cBd.ttf')
_f=None
def _font():
    global _f
    if _f is None: _f=ImageFont.truetype(FONT,12)
    return _f

def quant(v):
    # v: 잉크 농도 0..255 → 원본 팔레트(1=진함 2=중간 3=옅음 0=투명)
    if v>=170: return 1
    if v>=105: return 2
    if v>=45: return 3
    return 0

def render(ch,dx=0,dy=-1):
    """16x16 값 배열(0..3)."""
    im=Image.new('L',(16,16),0); dr=ImageDraw.Draw(im)
    if ch=='.':
        g=[[0]*16 for _ in range(16)]; g[9][2]=1;g[9][3]=2;g[10][2]=2;g[10][3]=3; return g
    if ch==',':
        g=[[0]*16 for _ in range(16)]; g[9][2]=1;g[9][3]=2;g[10][2]=1;g[11][1]=3; return g
    dr.text((dx,dy),ch,font=_font(),fill=255)
    return [[quant(im.getpixel((x,y))) if x<12 and y<12 else 0 for x in range(16)] for y in range(16)]

def pack(g):
    """16x16 배열 → 128바이트(2x2 타일, 4bpp)."""
    b=bytearray(128)
    for t in range(4):
        for y in range(8):
            for x in range(8):
                v=g[(t>>1)*8+y][(t&1)*8+x]
                o=t*32+y*4+x//2
                b[o]|=v<<(4*(x&1))
    return bytes(b)

def unpack(b):
    g=[[0]*16 for _ in range(16)]
    for t in range(4):
        for y in range(8):
            for x in range(8):
                g[(t>>1)*8+y][(t&1)*8+x]=(b[t*32+y*4+x//2]>>(4*(x&1)))&15
    return g
