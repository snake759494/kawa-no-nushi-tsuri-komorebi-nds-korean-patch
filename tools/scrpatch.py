"""화면 덤프 기반 그림 글자 패치. 스펙: trans/gfx_patches.json"""
import os,json,collections
import rln,gfxtext,layer
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_cache={}
def files(rom):
    if 'f' not in _cache:
        out=[]
        for i,f in enumerate(rom.files):
            n=rom.filenames.filenameOf(i)
            if not n or not (n.endswith('.arc') or n.endswith('.rln')): continue
            d=bytes(f); d=rln.decode(d) if n.endswith('.rln') else d
            for e in rln.entries(d):
                if e['type'] in (1,2,3,4,6,11): out.append((n,e,d[e['off']:e['off']+e['size']]))
        _cache['f']=out
    return _cache['f']

def get_layer(prefix,lay):
    p=os.path.join(W,'dumps',prefix)
    if lay.startswith('obj'): return layer.obj_layer(p,lay[3])
    return layer.bg_layer(p,lay[2],int(lay[3]))   # 'bgA2'

def sources(rom,loc,v,box,ink=(1,)):
    x0,y0,x1,y1=box
    tiles=set(loc[(x,y)][0]//32*32 for x in range(x0,x1) for y in range(y0,y1) if (x,y) in loc and ((v[loc[(x,y)][0]]>>(4*loc[(x,y)][1]))&15) in ink)
    tiles=[t for t in tiles if len(set(v[t:t+32]))>2]
    res=[]
    for n,e,raw in files(rom):
        votes=collections.Counter()
        for t in tiles:
            k=raw.find(v[t:t+32])
            while k>=0:
                if k%32==0: votes[t-k]+=1
                k=raw.find(v[t:t+32],k+1)
        if votes:
            delta,c=votes.most_common(1)[0]
            if c>=max(1,len(tiles)*0.9): res.append((n,e['name'],e['type'],delta,c,len(tiles)))
    sources.tiles=set(tiles)
    return res

def render_items(loc,v,items,keep,fill,aa,outline,font,center):
    get=lambda X,Y:(v[loc[(X,Y)][0]]>>(4*loc[(X,Y)][1]))&15
    out={}
    for it in items:
        (x0,y0,x1,y1)=it['box']; text=it['text']; size=it.get('size',12)
        for y in range(y0,y1):
            c=collections.Counter(get(x,y) for x in range(x0,x1) if (x,y) in loc and get(x,y) not in keep)
            face=c.most_common(1)[0][0] if c else None
            if face is None: continue
            for x in range(x0,x1):
                if (x,y) in loc: out[(x,y)]=face
        f=gfxtext.ttf(it.get('font',font),size)
        m,_=gfxtext.render_mask(text,f,x1-x0,y1-y0,dx=it.get('dx',1),dy=it.get('dy',0),center=it.get('center',center),spacing=it.get('spacing',0))
        if 'bitmap' in it:   # 공간이 좁아 손으로 찍은 픽셀 글자
            m=m.point(lambda _:0)
            for r,row in enumerate(it['bitmap']):
                for c,ch in enumerate(row):
                    if ch=='#': m.putpixel((c+it.get('dx',0),r+it.get('dy',0)),255)
        g=gfxtext.stylize(m,fill=it.get('fill',fill),aa=it.get('aa',aa),outline=it.get('outline',outline),th=140,aath=70)
        for y in range(y1-y0):
            for x in range(x1-x0):
                if g[y][x] and (x0+x,y0+y) in loc: out[(x0+x,y0+y)]=g[y][x]
    return out

def apply_spec(rom,spec):
    allsrc=[]
    for it in spec['items']:
        sp=dict(spec); sp['items']=[it]
        allsrc+=_apply(rom,sp)
    return allsrc

def _apply(rom,spec):
    loc,v,_=get_layer(spec['dump'],spec['layer'])
    items=spec['items']
    allbox=(min(i['box'][0] for i in items),min(i['box'][1] for i in items),max(i['box'][2] for i in items),max(i['box'][3] for i in items))
    srcs=sources(rom,loc,v,allbox,tuple(spec.get('ink',[spec.get('fill',1)])))
    out=render_items(loc,v,items,tuple(spec.get('keep',[])),spec.get('fill',1),spec.get('aa'),spec.get('outline'),spec.get('font','NanumSquareNeo-eHv.ttf'),spec.get('center',False))
    # 박스 안에서만 쓰이는 타일(다른 칸과 공유되지 않음)은 써도 안전
    users={}
    for (X,Y),(b,h) in loc.items(): users.setdefault(b//32*32,set()).add((X//8,Y//8))
    bx=(allbox[0]//8,allbox[1]//8,(allbox[2]-1)//8,(allbox[3]-1)//8)
    exclusive={t for t,cells in users.items() if all(bx[0]<=cx<=bx[2] and bx[1]<=cy<=bx[3] for cx,cy in cells) and len(cells)==1}
    n=0
    for fn,en,et,delta,c,tot in srcs:
        d=bytes(rom.getFileByName(fn)); comp=fn.endswith('.rln')
        if comp: d=rln.decode(d)
        d=bytearray(d)
        e=[x for x in rln.entries(bytes(d)) if x['name']==en and x['type']==et][0]
        raw=bytearray(d[e['off']:e['off']+e['size']])
        for (X,Y),val in out.items():
            b,h=loc[(X,Y)]; o=b-delta
            if b//32*32 not in sources.tiles and b//32*32 not in exclusive and not spec.get('all_tiles',spec['layer'].startswith('obj')): continue
            if 0<=o<len(raw): raw[o]=(raw[o]&~(15<<(4*h)))|(val<<(4*h))
        d[e['off']:e['off']+e['size']]=raw
        rom.setFileByName(fn,rln.encode(bytes(d)) if comp else bytes(d)); n+=1
    return srcs

def apply_all(rom,stat):
    p=os.path.join(W,'trans','gfx_patches.json')
    if not os.path.exists(p): return
    log=[]
    for spec in json.load(open(p,encoding='utf8')):
        s=apply_spec(rom,spec); log.append((spec['dump'],spec['layer'],[x[:2] for x in s]))
        if not s: print('  출처 없음:',spec['dump'],spec['layer'],spec['items'][0]['text'])
    stat['scr']=log
