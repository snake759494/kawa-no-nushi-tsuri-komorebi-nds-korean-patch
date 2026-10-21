"""한국어 ROM 빌드: python -X utf8 tools/build.py
원본 ROM은 읽기만 하고, 결과는 원본과 같은 폴더의 '... (Korean).nds'로 저장."""
import sys,os,re,json,struct,glob,collections,hashlib
sys.path.insert(0,'tools')
import ndspy.rom
from common import TBL,dec
from disasm import parse
import charset,font
from arcmsg import read as arc_read

W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT=os.path.dirname(W)
SRC=os.path.join(ROOT,'Kawa no Nushi Tsuri - Komorebi no Tani, Seseragi no Uta (Japan).nds')
DST=os.path.join(ROOT,'Kawa no Nushi Tsuri - Komorebi no Tani, Seseragi no Uta (Korean).nds')
TOK=re.compile(r'\{([0-9a-f]{4})\}')

def load_tsv(pattern):
    m={}
    for fn in sorted(glob.glob(os.path.join(W,'trans',pattern))):
        for line in open(fn,encoding='utf8').read().splitlines():
            if not line.strip() or line.startswith('#'): continue
            k,v=line.split('\t',1)
            m[k]=v
    return m

def split_tokens(t):
    """'{8001}' 토큰과 일반 문자 목록."""
    out=[];p=0
    for m in TOK.finditer(t):
        out+=list(t[p:m.start()]); out.append(int(m.group(1),16)); p=m.end()
    out+=list(t[p:])
    return out

def enc_glyph(t,cmap):
    return [x if isinstance(x,int) else charset.encode_glyph(x,cmap)[0] for x in split_tokens(t)]

# ---------------- 번역 로드 ----------------
def load_all():
    ja=[l.split('\t',2) for l in open(os.path.join(W,'trans','ja_all.txt'),encoding='utf8').read().splitlines()]
    ko=load_tsv('ko_[0-9][0-9].tsv')
    fix=load_tsv('fix_script.tsv') if os.path.exists(os.path.join(W,'trans','fix_script.tsv')) else {}
    ko.update(fix)
    script={}
    for i,s,t in ja:
        if i in ko: script[t]=ko[i]
    arc=load_tsv('ko_arc.tsv'); arc.update(load_tsv('fix_arc.tsv')); arm9=load_tsv('ko_arm9.tsv')
    return script,arc,arm9

def post(t):
    """번역문 공통 후처리."""
    t=t.replace('너굴','타누').replace('다누','타누')
    t=t.replace('・・・','…').replace('...','…').replace('。','.').replace('、',',')
    return t

# ---------------- 스크립트 ----------------
JUMP={0x0a:20,0x0b:20,0x0c:20,0x0d:20,0x0e:20,0x0f:20,0x12:4,0x13:4}
def rebuild_script(b,tr,cmap,stat):
    hdr,ins=parse(b)
    newins=[];omap={}
    pos=12
    for p,w,r in ins:
        omap[p]=pos
        op=w&0xff
        if op in (0x16,0x1f):
            ln=struct.unpack_from('<I',r,4)[0]
            ws=struct.unpack('<%dH'%(ln//2),r[8:8+ln]); e=ws.index(0x8000)
            ja=dec(ws[:e])
            if ja in tr:
                words=enc_glyph(post(tr[ja]),cmap); stat['tr']+=1
            else:
                words=list(ws[:e])
                if re.search('[぀-ヿ一-鿿]',ja): stat['miss'].append(ja)
            words.append(0x8000)
            if len(words)%2: words.append(0)
            body=struct.pack('<%dH'%len(words),*words)
            r=struct.pack('<II',w,len(body))+body
        newins.append((p,w,bytearray(r)));pos+=len(r)
    omap['end']=pos
    for p,w,r in newins:
        op=w&0xff
        if op in JUMP:
            k=JUMP[op]; v=struct.unpack_from('<I',r,k)[0]
            struct.pack_into('<I',r,k,omap[v+12]-12)
    code=b''.join(bytes(r) for _,_,r in newins)
    return b'[SCR103]'+struct.pack('<I',len(code))+code

def build_scripts(data,tr,cmap,stat):
    n=struct.unpack_from('<I',data,0)[0]
    scs=[data[o:o+s] for o,s in (struct.unpack_from('<2I',data,4+8*i) for i in range(n))]
    out=[rebuild_script(b,tr,cmap,stat) for b in scs]
    tab=b'';body=b'';off=4+8*n
    for s in out:
        tab+=struct.pack('<II',off+len(body),len(s)); body+=s
        while len(body)%4: body+=b'\0'
    return struct.pack('<I',n)+tab+body

# ---------------- arc 메시지 ----------------
def build_arc(name,orig,tr,cmap,stat):
    hdr,ss=arc_read_bytes(orig)
    words_all=[];offs=[]
    for i,s in enumerate(ss):
        key='%s:%d'%(name,i)
        tail=[]
        if 0xffff in s: k=s.index(0xffff); tail=[0xffff]; s=s[:k]
        if key in tr:
            w=enc_glyph(post(tr[key]),cmap); stat['tr']+=1
        else:
            w=s; stat['miss'].append(key)
        offs.append(len(words_all)); words_all+=w+tail
    n=len(ss)
    body=struct.pack('<I',n)+struct.pack('<%dI'%n,*offs)+struct.pack('<%dH'%len(words_all),*words_all)
    while len(body)%32: body+=b'\0'
    h=bytearray(hdr); struct.pack_into('<I',h,0xc,len(body))
    return bytes(h)+body

def arc_read_bytes(h):
    n=struct.unpack_from('<I',h,0x20)[0]; offs=list(struct.unpack_from('<%dI'%n,h,0x24)); base=0x24+4*n
    tot=(len(h)-base)//2; ws=struct.unpack_from('<%dH'%tot,h,base)
    return h[:0x20],[list(ws[offs[i]:(offs[i+1] if i+1<n else tot)]) for i in range(n)]

# ---------------- 폰트 ----------------
FONT_BANKS=[0x2064,0xa084,0x120a4,0x1a0c4]  # common.arc 안 font12_0..3 데이터 시작
def build_font(common,cmap):
    c=bytearray(common)
    for ch,idx in cmap.items():
        orig=TBL[idx] if idx<len(TBL) else None
        if orig==ch and ch not in charset.REDRAW: continue
        draw=charset.REDRAW.get(ch,ch)
        g=font.render(draw)
        if idx>=0x400:
            AUX[0x20+(idx-0x400)*128:0x20+(idx-0x400)*128+128]=font.pack(g); continue
        o=FONT_BANKS[idx>>8]+(idx&0xff)*128
        c[o:o+128]=font.pack(g)
    return bytes(c)
AUX=None

# ---------------- ARM9 SJIS 문자열 ----------------
def build_arm9(arm9,tr,cmap,stat):
    d=bytearray(arm9)
    refs=collections.defaultdict(list)
    for i in range(0,len(d)-3,4):
        v=struct.unpack_from('<I',d,i)[0]
        if 0x211f000<=v<0x2140000: refs[v-0x2000000].append(i)
    items=[]
    for k,v in tr.items():
        o=int(k,16); e=d.index(b'\0',o)
        items.append((o,e-o,charset.encode_sjis(post(v),cmap)))
    # 원래 문자열 공간(종료 0 포함, 다음 문자열 전까지)을 빈 공간으로
    items.sort()
    free=[]
    starts=[x[0] for x in items]+[len(d)]
    for j,(o,l,new) in enumerate(items):
        end=o+l+1
        while end<starts[j+1] and d[end]==0: end+=1
        free.append([o,end])
        d[o:end]=b'\0'*(end-o)
    placed={}
    # 원래 자리에 들어가면 그대로, 아니면 빈 공간 할당
    pending=[]
    for (o,l,new),(fo,fe) in zip(items,free):
        if len(new)+1<=fe-fo:
            d[o:o+len(new)]=new; placed[o]=o
            free[free.index([fo,fe])]=[o+len(new)+1,fe]
        else: pending.append((o,new))
    pending.sort(key=lambda x:-len(x[1]))
    for o,new in pending:
        for f in free:
            a=(f[0]+1)&~1
            if f[1]-a>=len(new)+1:
                d[a:a+len(new)]=new; d[a+len(new)]=0; placed[o]=a; f[0]=a+len(new)+1; break
        else: raise SystemExit('ARM9 문자열 공간 부족: %x'%o)
    moved=0
    for o,a in placed.items():
        if o!=a:
            for r in refs[o]: struct.pack_into('<I',d,r,0x2000000+a); moved+=1
    stat['arm9_moved']=moved
    return bytes(d)

def main():
    rom=ndspy.rom.NintendoDSRom.fromFile(SRC)
    script_tr,arc_tr,arm9_tr=load_all()
    gtexts=[post(t) for t in script_tr.values()]+[post(t) for t in arc_tr.values()]
    stexts=[post(t) for t in arm9_tr.values()]
    import extra
    extra.KNOWN=set(''.join(gtexts))
    S=set(''.join(post(t) for t in script_tr.values()))|set(''.join(stexts))|set(''.join(extra.texts()))
    A=set(''.join(post(t) for k,t in arc_tr.items() if k.startswith('card')))
    S|=set(''.join(post(t) for k,t in arc_tr.items() if not k.startswith('card')))
    cmap,info=charset.build([TOK.sub('',t) for t in gtexts]+extra.texts(),stexts,extra.keep_symbols(),aux_only=sorted(A-S))
    print('문자:',info)
    stat={'tr':0,'miss':[]}
    rom.setFileByName('script_data.bin',build_scripts(rom.getFileByName('script_data.bin'),script_tr,cmap,stat))
    for n in ['item_help_word','work_memo_sysmes','card_explanation']:
        rom.setFileByName(n+'.arc',build_arc(n,rom.getFileByName(n+'.arc'),arc_tr,cmap,stat))
    global AUX
    AUX=bytearray(rom.getFileByName('fon12_0s.arc'))
    rom.setFileByName('common.arc',build_font(rom.getFileByName('common.arc'),cmap))
    rom.setFileByName('fon12_0s.arc',bytes(AUX))
    rom.arm9=build_arm9(rom.arm9,arm9_tr,cmap,stat)
    extra.apply(rom,cmap,stat)
    print('번역 적용',stat['tr'],'미번역',len(stat['miss']),'ARM9 포인터 이동',stat.get('arm9_moved'))
    for m in stat['miss'][:20]: print('  미번역:',m[:60])
    json.dump({k:v for k,v in cmap.items()},open(os.path.join(W,'cmap.json'),'w',encoding='utf8'),ensure_ascii=False)
    rom.saveToFile(DST)
    print('저장',DST,hashlib.sha256(open(DST,'rb').read()).hexdigest())

if __name__=='__main__': main()
