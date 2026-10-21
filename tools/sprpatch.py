"""OAM 덤프(원본 ROM 기준)로 합성한 스프라이트 화면 위에 한글을 그려 원본 타일 항목에 되돌려 쓴다."""
import os,collections
import rln,gfxtext
from objcomp import compose
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_entry(rom,fn,ename,etype=6):
    d=bytes(rom.getFileByName(fn)); comp=fn.endswith('.rln')
    if comp: d=rln.decode(d)
    d=bytearray(d)
    e=[x for x in rln.entries(bytes(d)) if x['name']==ename and x['type']==etype][0]
    return d,e,comp

def find_vram(vram,raw):
    for k in range(0,len(raw)-64,32):
        c=raw[k:k+64]
        if len(set(c))>4:
            j=vram.find(c)
            if j>=0 and j%32==k%32: return j-k
    return None

def draw(fn_rom,prefix,eng,fn,ename,items,etype=6,center=False,font='NanumSquareNeo-eHv.ttf',fill=1,aa=9,outline=12,keep=(1,9,12)):
    rom=fn_rom
    d,e,comp=load_entry(rom,fn,ename,etype)
    raw=bytearray(d[e['off']:e['off']+e['size']])
    vram=open(os.path.join(W,prefix+'_%s_vram.bin'%eng),'rb').read()
    orig=bytes(raw)
    _,loc=compose(os.path.join(W,prefix),eng)
    import collections as _c
    votes=_c.Counter(); tmap={}
    for base,sz in compose.blocks:
        blk=vram[base:base+sz]
        if len(set(blk))<=2: continue
        ks=[]; k=orig.find(blk)
        while k>=0:
            if k%32==0: ks.append(k)
            k=orig.find(blk,k+1)
        if len(ks)==1: votes[base-ks[0]]+=1
    for base,sz in compose.blocks:
        blk=vram[base:base+sz]
        # 이 블록과 일치하는 후보 기준 중 가장 많이 득표한 기준 사용
        for delta,_n in votes.most_common():
            k=base-delta
            if 0<=k<=len(orig)-sz and orig[k:k+sz]==blk:
                for t in range(0,sz,32): tmap[base+t]=k+t
                break
    def toff(b):
        return tmap.get(b//32*32,-1)
    def get(X,Y):
        b,h=loc[(X,Y)]; return (vram[b]>>(4*h))&15
    out={}
    for (x0,y0,x1,y1),text,size in items:
        for y in range(y0,y1):
            c=collections.Counter(get(x,y) for x in range(x0,x1) if (x,y) in loc and get(x,y) not in keep)
            face=c.most_common(1)[0][0] if c else 0
            for x in range(x0,x1):
                if (x,y) in loc: out[(x,y)]=face
        f=gfxtext.ttf(font,size)
        m,_=gfxtext.render_mask(text,f,x1-x0,y1-y0,dx=1,dy=0,center=center)
        g=gfxtext.stylize(m,fill=fill,aa=aa,outline=outline,th=140,aath=70)
        for y in range(y1-y0):
            for x in range(x1-x0):
                if g[y][x] and (x0+x,y0+y) in loc: out[(x0+x,y0+y)]=g[y][x]
    n=0
    for (X,Y),v in out.items():
        b,h=loc[(X,Y)]; t=toff(b)
        o=t+(b%32) if t>=0 else -1
        if 0<=o<len(raw):
            raw[o]=(raw[o]&~(15<<(4*h)))|(v<<(4*h)); n+=1
    d[e['off']:e['off']+e['size']]=raw
    rom.setFileByName(fn,rln.encode(bytes(d)) if comp else bytes(d))
    return n
