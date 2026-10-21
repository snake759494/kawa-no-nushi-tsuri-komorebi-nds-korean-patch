"""ARM9 글리프 인덱스 데이터와 그림 글자 패치."""
import struct,os,sys
import rln,charset,gfxtext,type0,logo
from PIL import Image

# ---------- 화자 이름(0x270f 종료, 14바이트 고정 칸) ----------
SPEAKERS=['렌','마나토','아야하','누리카베','갓파','네코마타','꼬마도깨비','가마이타치','고다마','누에',
          '팥씻기','사사라','장고','마쓰리','히로','사치','윤나','야스','미유키','카즈','나나요','마사','가오리']
SPEAKER_TABLE=0x1317fc
CONTEST=[(0x11f068,4,'수 승부'),(0x11f076,6,'크기 승부!')]

# ---------- 이름 입력 키보드 ----------
PAGE_A='가거고구그기나너노누느니다더도두드디라러로루르리마머모무므미바버보부브비사서소수스시아어오우으이자저조주즈지차처초추츠치카커코쿠크키타터토투트티파퍼포푸프피하허호후흐히야여요유와위'
POOL_B=('강건경곤광규근길김남년단달대덕동득래련령류린림만명문민박범별병상석선설성세솔송수순승신실심안양연영예완용운원윤은을의인일임재정종준지진찬창철청태하한해향형혜호홍화환훈희'
        '곰꽃나래누리다솜별빛봄샘슬아름여름울진찬해솔')
SYMBOLS='ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ０１２３４５６７８９？！☆★・♪．ー×（）～'
KNOWN=set()
def pages():
    a=list(PAGE_A); assert len(a)==90,len(a)
    if KNOWN:
        spare=[ch for ch in '여요유와위얀연예오우은을인일임장전정제조중진채천최태하한해현호화효훈휘희' if ch in KNOWN and ch not in a]
        for i,ch in enumerate(a):
            if ch not in KNOWN and spare: a[i]=spare.pop(0)
    b=[]
    for pref in (True,False):
        for ch in POOL_B:
            if len(b)==90: break
            if ch in a or ch in b: continue
            if pref and ch not in KNOWN: continue
            b.append(ch)
    for ch in sorted(KNOWN):
        if len(b)==90: break
        if '가'<=ch<='힣' and ch not in a and ch not in b: b.append(ch)
    assert len(b)==90,len(b)
    c=list(SYMBOLS)+['　']*(90-len(SYMBOLS))
    return a,b,c
KB_TABLE={'a':0x120178,'b':0x120250,'c':0x120328}

def texts():
    """글리프 인덱스로 쓰이는 추가 문자열(문자 배정에 포함)."""
    a,b,c=pages()
    return SPEAKERS+[t for _,_,t in CONTEST]+[''.join(a),''.join(b)]

def keep_symbols():
    return set(SYMBOLS)

def wstr(arm9,off,cap,text,cmap):
    g=[cmap[charset.norm(ch)] for ch in text]
    assert len(g)<=cap,(text,cap)
    b=struct.pack('<%dH'%len(g),*g)+struct.pack('<H',0x270f)
    b+=b'\0'*(cap*2+2-len(b))
    arm9[off:off+len(b)]=b

def patch_arm9(rom,cmap):
    d=bytearray(rom.arm9)
    for i,name in enumerate(SPEAKERS):
        p=struct.unpack_from('<I',d,SPEAKER_TABLE+4*i)[0]-0x2000000
        wstr(d,p,6,name,cmap)
    for off,cap,t in CONTEST: wstr(d,off,cap,t,cmap)
    a,b,c=pages()
    for key,chars in (('a',a),('b',b),('c',c)):
        base=KB_TABLE[key]
        for row in range(18):
            g=[cmap[charset.norm(ch)] if ch!='　' else cmap['　'] for ch in chars[row*5:row*5+5]]
            struct.pack_into('<5HH',d,base+row*12,*g,0x270f)
    rom.arm9=bytes(d)

# ---------- 키보드 그림(pt_11_a/b/c, type4 4bpp 2D) ----------
def bg_px(raw,x,y):
    t=(y//8)*32+(x//8); return (raw[t*32+(y%8)*4+(x%8)//2]>>(4*(x&1)))&15
def bg_set(raw,x,y,v):
    t=(y//8)*32+(x//8); o=t*32+(y%8)*4+(x%8)//2; s=4*(x&1)
    raw[o]=(raw[o]&~(15<<s))|(v<<s)

KB_FONT=('NanumSquareNeo-dEb.ttf',12)
def draw_kb(raw,chars):
    font=gfxtext.ttf(*KB_FONT)
    for i,ch in enumerate(chars):
        vr,blk=divmod(i,15); blk,col=divmod(blk,5)
        # 표 행 순서: 표 행 r → 화면 행 r//3, 블록 r%3
    for row in range(18):
        vr,blk=divmod(row,3)
        x0=[4,88,171][blk]; y0=144+vr*16
        for k in range(5):
            ch=chars[row*5+k]; cx=x0+16*k
            for y in range(y0,y0+12):
                for x in range(cx,cx+14): bg_set(raw,x,y,12)
            if ch=='　': continue
            m,_=gfxtext.render_mask(ch,font,14,13,dx=0,dy=-1)
            for y in range(13):
                for x in range(14):
                    v=m.getpixel((x,y))
                    c=8 if v>=150 else 9 if v>=90 else 10 if v>=40 else None
                    if c and y0+y<y0+13: bg_set(raw,cx+x,y0+y,c)

def label(raw,box,text,size=13,dx=2,dy=0):
    """배경 c 위 라벨(はい/いいえ 형식)."""
    x0,y0,x1,y1=box
    for y in range(y0,y1):
        for x in range(x0,x1): bg_set(raw,x,y,12)
    font=gfxtext.ttf('NanumSquareNeo-eHv.ttf',size)
    m,_=gfxtext.render_mask(text,font,x1-x0,y1-y0,dx=dx,dy=dy)
    g=[[0]*(x1-x0) for _ in range(y1-y0)]
    for y in range(y1-y0):
        for x in range(x1-x0):
            v=m.getpixel((x,y)); g[y][x]=1 if v>=140 else 9 if v>=70 else 0
    for y in range(y1-y0):
        for x in range(x1-x0):
            if g[y][x]: bg_set(raw,x0+x,y0+y,g[y][x])
            elif y>0 and x>0 and g[y-1][x-1]: bg_set(raw,x0+x,y0+y,10)

def button(raw,box,text,size=11):
    """줄무늬 버튼 면 위 라벨: 면을 행별 우세 색으로 복원 후 채움1/외곽c."""
    x0,y0,x1,y1=box
    import collections
    for y in range(y0,y1):
        c=collections.Counter(bg_px(raw,x,y) for x in range(x0,x1) if bg_px(raw,x,y) not in (1,9,12))
        face=c.most_common(1)[0][0] if c else 5
        for x in range(x0,x1): bg_set(raw,x,y,face)
    font=gfxtext.ttf('NanumSquareNeo-eHv.ttf',size)
    W,H=x1-x0,y1-y0
    m,_=gfxtext.render_mask(text,font,W,H,center=True,dy=0)
    g=gfxtext.stylize(m,fill=1,outline=12,th=110)
    for y in range(H):
        for x in range(W):
            if g[y][x]: bg_set(raw,x0+x,y0+y,g[y][x])

BUTTONS=['기본','받침','기호','지움','결정']
def patch_keyboard(rom):
    a,b,c=pages()
    for key,chars in (('a',a),('b',b),('c',c)):
        fn='map/pt_11_%s.rln'%key
        d=bytearray(rln.decode(bytes(rom.getFileByName(fn))))
        e=rln.entries(d)[0]; raw=bytearray(d[e['off']:e['off']+e['size']])
        draw_kb(raw,chars)
        label(raw,(1,9,40,23),'네')
        label(raw,(1,105,56,119),'아니요')
        for i,t in enumerate(BUTTONS):
            button(raw,(32*i+4,85,32*i+28,95),t)
        d[e['off']:e['off']+e['size']]=raw
        rom.setFileByName(fn,rln.encode(bytes(d)))

def apply(rom,cmap,stat):
    patch_arm9(rom,cmap)
    patch_keyboard(rom)
    import gfxpatch
    gfxpatch.apply(rom,stat)
