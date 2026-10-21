"""그림 글자(16x16 셀 행 시트, 4bpp 2x2 타일) 한글 재작성."""
import os
from PIL import Image,ImageDraw,ImageFont
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class BDF:
    def __init__(self,path):
        self.g={};cur=None;inb=False
        for line in open(path,encoding='utf8',errors='ignore'):
            p=line.split()
            if not p: continue
            if p[0]=='ENCODING': cur=int(p[1])
            elif p[0]=='DWIDTH': dw=int(p[1])
            elif p[0]=='BBX': bbx=list(map(int,p[1:]))
            elif p[0]=='FONT_ASCENT': self.asc=int(p[1])
            elif p[0]=='BITMAP': inb=True; bm=[]
            elif p[0]=='ENDCHAR': inb=False; self.g[cur]=(dw,bbx,bm)
            elif inb: bm.append(int(p[0],16))
    def getlength(self,ch): return self.g.get(ord(ch),(4,0,0))[0]
    def getbbox(self,ch): return (0,0,self.getlength(ch),self.asc)
    def draw(self,im,x,y,ch):
        if ord(ch) not in self.g: return
        dw,(w,h,ox,oy),bm=self.g[ord(ch)]; nb=(w+7)//8*8
        for yy,row in enumerate(bm):
            for xx in range(w):
                if row>>(nb-1-xx)&1:
                    X=int(x)+ox+xx; Y=y+self.asc-oy-h+yy
                    if 0<=X<im.width and 0<=Y<im.height: im.putpixel((X,Y),255)
_bdf={}
def ttf(name,size):
    if name.endswith('.bdf'):
        if name not in _bdf: _bdf[name]=BDF(os.path.join(ROOT,'work','fonts',name))
        return _bdf[name]
    return ImageFont.truetype(os.path.join(ROOT,name),size)

def render_mask(text,font,w,h,dx=0,dy=0,spacing=0,center=False):
    """L 모드 잉크 마스크(0..255)."""
    im=Image.new('L',(w*4,h),0); dr=ImageDraw.Draw(im)
    x=0
    widths=[]
    for ch in text:
        bb=font.getbbox(ch); widths.append(font.getlength(ch))
    total=sum(widths)+spacing*(len(text)-1)
    x=(w-total)/2 if center else dx
    for ch,wd in zip(text,widths):
        (font.draw(im,x,dy,ch) if isinstance(font,BDF) else dr.text((x,dy),ch,font=font,fill=255)); x+=wd+spacing
    return im.crop((0,0,w,h)),total

def stylize(mask,fill=1,aa=None,outline=None,th=128,aath=60):
    """마스크 → 팔레트 인덱스 2차원 배열."""
    w,h=mask.size; p=mask.load()
    g=[[0]*w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            v=p[x,y]
            if v>=th: g[y][x]=fill
            elif aa is not None and v>=aath: g[y][x]=aa
    if outline is not None:
        o=[row[:] for row in g]
        for y in range(h):
            for x in range(w):
                if g[y][x]==0:
                    for dy in (-1,0,1):
                        for dx in (-1,0,1):
                            yy,xx=y+dy,x+dx
                            if 0<=yy<h and 0<=xx<w and g[yy][xx] in (fill,aa) and g[yy][xx]!=0:
                                o[y][x]=outline
        g=o
    return g

# 시트 접근(16x16 셀, 셀 내부 2x2 타일)
def get_px(raw,g,x,y):
    t=(y//8)*2+(x//8); o=g*128+t*32+(y%8)*4+(x%8)//2
    return (raw[o]>>(4*(x&1)))&15
def set_px(raw,g,x,y,v):
    t=(y//8)*2+(x//8); o=g*128+t*32+(y%8)*4+(x%8)//2
    sh=4*(x&1); raw[o]=(raw[o]&~(15<<sh))|(v<<sh)

def write_row(raw,row,grid,cells_per_row=16,first_cell=0,ncells=None):
    """grid(h=16, w=16*n)를 시트의 row행 first_cell부터 기록."""
    n=ncells or len(grid[0])//16
    for c in range(n):
        g=row*cells_per_row+first_cell+c
        for y in range(16):
            for x in range(16):
                set_px(raw,g,x,y,grid[y][c*16+x] if c*16+x<len(grid[0]) else 0)

def clear_row(raw,row,cells_per_row=16,n=8):
    for c in range(n):
        for y in range(16):
            for x in range(16): set_px(raw,row*cells_per_row+c,x,y,0)
