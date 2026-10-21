"""그림 글자 시트 패치(제목·지명·로고·튜토리얼)."""
import rln,gfxtext,type0,logo

G_TITLE=['저장 데이터','이름 입력','이름 확인','어망','메뉴','도구','아이템','카드 폴더','카드','부탁 메모','통신','친구 코드','Wi-Fi 통신','조과 기록']
MP_NAME=['연못','계류','폭포','맑은 시내','상류 폭포','늪','지하 호수','산꼭대기 호수','우리 집','아침','낮','밤']
MAP_NAME_OLD=['폭포','맑은 시내','늪','상류 폭포','지하 호수','산꼭대기 호수']

STYLE_A=dict(fill=1,aa=2,outline=4)      # menu_common 계열
STYLE_B=dict(fill=1,aa=None,outline=15)  # g_title.arc / map_name.arc

def sheet_rows(raw,rows,style):
    font=gfxtext.ttf('NanumSquareNeo-eHv.ttf',12)
    for i,t in enumerate(rows):
        gfxtext.clear_row(raw,i)
        m,_=gfxtext.render_mask(t,font,128,16,dx=1,dy=1)
        g=gfxtext.stylize(m,**style)
        gfxtext.write_row(raw,i,g)

def patch_entries(rom,fn,ename,rows,style):
    d=bytes(rom.getFileByName(fn)); comp=fn.endswith('.rln')
    if comp: d=rln.decode(d)
    d=bytearray(d); n=0
    for e in rln.entries(bytes(d)):
        if e['name']==ename and e['type']==2:
            raw=bytearray(d[e['off']:e['off']+e['size']])
            sheet_rows(raw,rows,style); d[e['off']:e['off']+e['size']]=raw; n+=1
    if n: rom.setFileByName(fn,rln.encode(bytes(d)) if comp else bytes(d))
    return n

LOGO_MAIN=dict(fill_top=(255,60,40),fill_bot=(255,230,40),inner=(255,255,255),outer=(30,60,200),inner_w=2,outer_w=3,shadow=(20,140,90),sh_off=(0,3))
LOGO_SUB=dict(fill_top=(255,255,255),fill_bot=(220,240,255),inner=(40,80,220),outer=(40,80,220),inner_w=1,outer_w=1,shadow=(30,150,200),sh_off=(0,2))
def patch_logo(rom,fn,big):
    d=bytearray(rln.decode(bytes(rom.getFileByName(fn))))
    e=rln.entries(bytes(d))[0]; b=bytes(d[e['off']:e['off']+e['size']])
    F=logo.F
    if big:
        lines=[('강의 낚시꾼',F('NanumSquareNeo-eHv.ttf',34),36,LOGO_MAIN),('나무 그늘 골짜기 · 시냇물의 노래',F('NanumSquareNeo-eHv.ttf',14),84,LOGO_SUB)]
        keep=31
    else:
        m=dict(LOGO_MAIN,inner_w=1,outer_w=2,sh_off=(0,2)); s=dict(LOGO_SUB,inner_w=0,outer_w=1,sh_off=(0,1))
        lines=[('강의 낚시꾼',F('NanumSquareNeo-eHv.ttf',20),18,m),('나무 그늘 골짜기 · 시냇물의 노래',F('NanumSquareNeo-eHv.ttf',9),46,s)]
        keep=17
    nb,_=logo.build(b,1,keep,lines)
    d[e['off']:e['off']+e['size']]=nb
    rom.setFileByName(fn,rln.encode(bytes(d)))

TUTORIAL=['주인공의 체력 게이지','낚싯줄 긴장 게이지','릴 감기 아이콘','여기를 터치해 돌리기','화살표 아이콘','여기를 터치']
def _blocks(b):
    w,h,bpp,npx,po=type0.info(b)
    def blk(x,y):
        out=bytearray(32)
        for yy in range(8):
            for xx in range(8):
                i=(y+yy)*w+x+xx; v=(b[4+i//2]>>(4*(i&1)))&15
                out[yy*4+xx//2]|=v<<(4*(xx&1))
        return bytes(out)
    return w,h,blk

def patch_tutorial(rom):
    fn='battle/b_tutorial.rln'
    d=bytearray(rln.decode(bytes(rom.getFileByName(fn))))
    es=rln.entries(bytes(d))
    e0=[e for e in es if e['type']==0][0]; e6=[e for e in es if e['type']==6][0]
    w,h,blk=_blocks(bytes(d[e0['off']:e0['off']+e0['size']]))
    src={}
    for y in range(0,h,8):
        for x in range(0,w,8): src.setdefault(blk(x,y),(x,y))
    raw6=bytes(d[e6['off']:e6['off']+e6['size']])
    tmap=[]
    for t in range(len(raw6)//32):
        tb=raw6[t*32:t*32+32]
        tmap.append(None if len(set(tb))<=1 else src.get(tb))
    for e in rln.entries(bytes(d)):
        if e['type']!=0: continue
        b=bytearray(d[e['off']:e['off']+e['size']])
        w,h,bpp,npx,po=type0.info(b)
        def gp(x,y):
            i=y*w+x; return (b[4+i//2]>>(4*(i&1)))&15
        def sp(x,y,v):
            i=y*w+x; o=4+i//2; s=4*(i&1); b[o]=(b[o]&~(15<<s))|(v<<s)
        # 각 행: 안쪽 테두리(5) 사이의 글자(1,2,3)를 면(4)으로 지움
        rows=[]
        for y in range(h):
            xs=[x for x in range(w) if gp(x,y)==5]
            if len(xs)>=2 and xs[-1]-xs[0]>40:
                inner=[gp(x,y) for x in range(xs[0]+1,xs[-1])]
                if inner.count(4)>len(inner)*0.15:
                    for x in range(xs[0]+1,xs[-1]):
                        if gp(x,y) in (1,2,3): sp(x,y,4)
                    rows.append((y,xs[0]+1,xs[-1]))
        groups=[]
        for y,x0,x1 in rows:
            if groups and y==groups[-1][-1][0]+1: groups[-1].append((y,x0,x1))
            else: groups.append([(y,x0,x1)])
        groups=[g for g in groups if len(g)>=8]
        font=gfxtext.ttf('NanumSquareNeo-dEb.ttf',11)
        for k,(g,t) in enumerate(zip(groups,TUTORIAL)):
            y0=g[0][0]; y1=g[-1][0]+1; x0=max(r[1] for r in g)+1; x1=min(r[2] for r in g)-1
            W_=x1-x0; H_=y1-y0
            m,tw=gfxtext.render_mask(t,font,W_,H_,center=True,dy=(H_-12)//2)
            for y in range(H_):
                for x in range(W_):
                    v=m.getpixel((x,y))
                    if v>=140: sp(x0+x,y0+y,1)
                    elif v>=70: sp(x0+x,y0+y,3)
        d[e['off']:e['off']+e['size']]=b
    w,h,blk=_blocks(bytes(d[e0['off']:e0['off']+e0['size']]))
    new6=bytearray(raw6)
    for t,pos in enumerate(tmap):
        if pos: new6[t*32:t*32+32]=blk(*pos)
    d[e6['off']:e6['off']+e6['size']]=new6
    rom.setFileByName(fn,rln.encode(bytes(d)))

def sheet_box(raw,row,box,text,face,fill=1,aa=None,outline=None,font='NanumSquareNeo-dEb.ttf',size=11,center=True,dy=0):
    x0,y0,x1,y1=box
    P=lambda x,y,v:gfxtext.set_px(raw,row*16+x//16,x%16,y,v)
    for y in range(y0,y1):
        for x in range(x0,x1): P(x,y,face)
    f=gfxtext.ttf(font,size)
    m,_=gfxtext.render_mask(text,f,x1-x0,y1-y0,center=center,dy=dy)
    g=gfxtext.stylize(m,fill=fill,aa=aa,outline=outline,th=140,aath=70)
    for y in range(y1-y0):
        for x in range(x1-x0):
            if g[y][x]: P(x0+x,y0+y,g[y][x])

def patch_sheet(rom,fn,ename,ops):
    d=bytes(rom.getFileByName(fn)); comp=fn.endswith('.rln')
    if comp: d=rln.decode(d)
    d=bytearray(d)
    for e in rln.entries(bytes(d)):
        if e['name']==ename and e['type']==2:
            raw=bytearray(d[e['off']:e['off']+e['size']])
            for op in ops: sheet_box(raw,**op)
            d[e['off']:e['off']+e['size']]=raw
    rom.setFileByName(fn,rln.encode(bytes(d)) if comp else bytes(d))

def apply(rom,stat):
    patch_sheet(rom,'map/pt_18.rln','pt18obj2',[dict(row=0,box=(14,3,160,15),text='주인을 찾아서',face=7,aa=9,center=False),dict(row=1,box=(14,3,160,15),text='낚시 수행',face=7,aa=9,center=False)])
    patch_sheet(rom,'map/pt_19.rln','pt19obja',[dict(row=0,box=(2,2,31,15),text='미끼',face=0,aa=9,outline=12),dict(row=0,box=(31,2,63,15),text='루어',face=0,aa=9,outline=12),dict(row=0,box=(63,2,99,15),text='플라이',face=0,aa=9,outline=12,size=10)])
    for fn in ['menu_common.arc','menu_common2.arc','map/pt_04.rln','map/pt_04_2.rln','map/pt_17.rln','map/pt_21.rln','map/pt_29.rln','map/pt_34.rln']:
        patch_sheet(rom,fn,'mp_namea',[dict(row=r,box=(24,2,38,14),text='위',face=11,aa=10,size=10) for r in (12,13,14,15)])
    n=0
    for fn in ['menu_common.arc','menu_common2.arc','map/pt_17.rln','map/pt_21.rln','map/pt_34.rln']:
        n+=patch_entries(rom,fn,'g_titlea',G_TITLE,STYLE_A)
    for fn in ['menu_common.arc','menu_common2.arc','map/pt_04.rln','map/pt_04_2.rln','map/pt_17.rln','map/pt_21.rln','map/pt_29.rln','map/pt_34.rln']:
        n+=patch_entries(rom,fn,'mp_namea',MP_NAME,STYLE_A)
    n+=patch_entries(rom,'g_title.arc','g_title',G_TITLE[:13],STYLE_B)
    n+=patch_entries(rom,'map_name.arc','mp_name',MAP_NAME_OLD,STYLE_B)
    patch_logo(rom,'map/title1_0.rln',True)
    patch_logo(rom,'map/title1_1.rln',False)
    patch_tutorial(rom)
    import sprpatch
    import barpatch
    barpatch.patch_all(rom)
    import btnpatch,gridpatch
    ref=btnpatch.Ref('oam_menu','B',lambda s_:s_['y']==24 and s_['x'] in (24,56,88))
    btnpatch.patch(rom,'map/pt_18.rln','pt18obj',ref,['낚시 도구','아이템','어망','카드 폴더','조과 기록','부탁 메모','친구 코드','저장'],(25,29,110,48),offsets=[i*0x1000 for i in range(8)])
    for fn,en in (('map/pt_27.rln','pt27objt'),('map/pt_36.rln','pt36objt')):
        gridpatch.patch(rom,fn,en,[dict(first=0,count=6,box=(8,2,184,18),text='마릿수 승부!'),dict(first=8,count=6,box=(8,2,184,18),text='크기 승부!')])
    for fn in ('menu_common.arc','menu_common2.arc'):
        gridpatch.patch(rom,fn,'obj_01a',[dict(first=1,count=1,box=(3,2,30,12),text='메뉴',font='Galmuri9.bdf',aa=None,keep=(1,9,12)),dict(first=2,count=1,box=(3,2,30,12),text='그만',font='Galmuri9.bdf',aa=None,keep=(1,9,12))])
    import scrpatch
    scrpatch.apply_all(rom,stat)
    stat['gfx_sheets']=n
