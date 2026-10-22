"""공용 UI 그림 시트(big_map.arc pt_04 등, 타입 3 4bpp, 가로 32타일 2D) 라벨 한글화.
라벨마다 배경(행별 다수색)·글자색·외곽선색을 원본에서 판별해 다시 그린다.
같은 시트를 공유하는 사본은 라벨 영역 타일이 기준과 바이트 단위로 같을 때만 고친다."""
import collections
import rln,gfxtext

# (x0,y0,x1,y1, 텍스트, 글꼴크기 또는 'g9')
LABELS=[
 (0,16,40,32,'네',13),
 (0,36,64,48,'소지 포인트','g9'),
 (0,50,88,64,'소지/필요/',11),
 (24,71,56,81,'종류','g9'),
 (24,81,56,91,'포인트','g9'),
 (48,88,64,104,'위',12),
 (40,130,96,143,'아니요',12),
 (0,142,32,155,'뒤로',11),
 (128,150,176,163,'대회 시작',11),
 (104,188,144,200,'카드',11),
 (160,182,184,194,'능력',11),
 (160,198,184,210,'종족',11),
 (24,210,120,222,'낚시 대회 결과 발표',11),
 (128,210,160,222,'카드',11),
 (0,226,48,238,'HP 포인트',10),
 (72,226,112,238,'종류',11),
 (0,242,32,254,'카드',11),
 (72,242,96,254,'능력',11),
 (112,242,144,254,'성장도',11),
]

def gp(raw,x,y):
    t=(y//8)*32+x//8; return (raw[t*32+(y%8)*4+(x%8)//2]>>(4*(x&1)))&15
def sp(raw,x,y,v):
    t=(y//8)*32+x//8; o=t*32+(y%8)*4+(x%8)//2; s=4*(x&1); raw[o]=(raw[o]&~(15<<s))|(v<<s)

ROWMODE={'뒤로','대회 시작','도구','종족','칭호','HP 포인트'}
def style(raw,x0,y0,x1,y1,rowmode=False):
    """배경=행별 다수색, 글자 채움=배경과 안 닿는 내부 다수색, 외곽선=배경과 닿는 글자색."""
    bg={}
    # 박스에서 가장 자주 나오는 세로 열 패턴 = 글자 없는 배경 열(가로로 균일한 줄무늬·단색 배경)
    cols=collections.Counter(tuple(gp(raw,x,y) for y in range(y0,y1)) for x in range(x0,x1))
    col,cnt=cols.most_common(1)[0]
    if cnt>=2 and not rowmode:
        for i,y in enumerate(range(y0,y1)): bg[y]=col[i]
    else:
        for y in range(y0,y1): bg[y]=collections.Counter(gp(raw,x,y) for x in range(x0,x1)).most_common(1)[0][0]
    inner=collections.Counter(); edge=collections.Counter()
    for y in range(y0,y1):
        for x in range(x0,x1):
            v=gp(raw,x,y)
            if v==bg[y]: continue
            nb=[gp(raw,xx,yy) for xx,yy in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)) if x0<=xx<x1 and y0<=yy<y1]
            if any(n==bg.get(yy) for n,(xx,yy) in zip(nb,[(x-1,y),(x+1,y),(x,y-1),(x,y+1)])): edge[v]+=1
            else: inner[v]+=1
    fill=(inner or edge).most_common(1)[0][0]
    out=None
    if edge:
        e=[v for v,_ in edge.most_common() if v!=fill]
        if e and edge[e[0]]>edge.get(fill,0)*0.5: out=e[0]
    return bg,fill,out

def draw(raw,lab):
    x0,y0,x1,y1,text,size=lab
    bg,fill,out=style(raw,x0,y0,x1,y1,text in ROWMODE or (text=='카드' and x0==128))
    for y in range(y0,y1):
        for x in range(x0,x1): sp(raw,x,y,bg[y])
    f=gfxtext.ttf('Galmuri9.bdf',9) if size=='g9' else gfxtext.ttf('NanumSquareNeo-eHv.ttf',size)
    W,H=x1-x0,y1-y0
    m,tw=gfxtext.render_mask(text,f,W,H,center=True,dy=(-2 if size=='g9' and H<=10 else 0 if size=='g9' else max(0,(H-size)//2)))
    g=gfxtext.stylize(m,fill=fill,outline=out,th=120)
    for y in range(H):
        for x in range(W):
            if g[y][x]: sp(raw,x0+x,y0+y,g[y][x])

def boxbytes(raw,lab):
    x0,y0,x1,y1=lab[:4]
    return b''.join(raw[((y//8)*32+x//8)*32:((y//8)*32+x//8)*32+32] for y in range(y0-y0%8,y1,8) for x in range(x0-x0%8,x1,8))

def patch(rom,stat):
    ref=None
    d0=bytes(rom.getFileByName('big_map.arc'))
    ref=[d0[e['off']:e['off']+e['size']] for e in rln.entries(d0) if e['name']=='pt_04' and e['type']==3][0]
    refbox=[boxbytes(ref,l) for l in LABELS]
    n=0
    for i,f in enumerate(rom.files):
        fn=rom.filenames.filenameOf(i)
        if not fn or not (fn.endswith('.arc') or fn.endswith('.rln')): continue
        d=bytes(f); comp=fn.endswith('.rln')
        if comp: d=rln.decode(d)
        d=bytearray(d); ch=False
        for e in rln.entries(bytes(d)):
            if e['type'] not in (3,4) or e['size']!=0x8000: continue
            raw=bytearray(d[e['off']:e['off']+e['size']])
            hit=0
            for lab,rb in zip(LABELS,refbox):
                if boxbytes(raw,lab)==rb: draw(raw,lab); hit+=1
            if hit:
                d[e['off']:e['off']+e['size']]=raw; ch=True; n+=hit
        if ch: rom.setFileByName(fn,rln.encode(bytes(d)) if comp else bytes(d))
    stat['uisheet']=n
