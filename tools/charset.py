"""한글 음절 → 글리프 슬롯 배정.
- 0x000~0x395: ARM9 SJIS 표(TBL)와 공유되는 슬롯. SJIS 문자열은 0x38c 미만만 참조 가능.
- 0x396~0x3ef: 표 밖이지만 font12_3 뱅크 안의 빈 슬롯(글리프 인덱스 문자열 전용).
- 번역문에 쓰인 기호·숫자·영문은 원래 슬롯을 유지하고, 나머지 가나·한자 슬롯을 한글로 덮어쓴다.
"""
import sys,json,collections
sys.path.insert(0,'tools')
from common import TBL

# 번역문 일반 문자 → 원래 표의 문자
ASCII={' ':'　','.':'。',',':'、','?':'？','!':'！','~':'～','(':'（',')':'）','/':'／',
       ':':'：','%':'％','-':'－','+':'＋','&':'＆','*':'＊','<':'＜','>':'＞','"':'”',"'":'’',
       '[':'「',']':'」','·':'・'}
for i in range(10): ASCII[str(i)]=chr(0xff10+i)
for i in range(26):
    ASCII[chr(65+i)]=chr(0xff21+i); ASCII[chr(97+i)]=chr(0xff41+i)
# 다시 그리는 기호(일본식 → 한국식)
REDRAW={'。':'.','、':','}
# 항상 보존하는 슬롯(아이콘 등)
ALWAYS_KEEP=set('■〇●◎▽▼△▲＋－÷♯∮ξΘ※○’”．♀♂？！…・ー。、～（）「」０１２３４５６７８９　ｃｍ×♪★☆∀―』『')
SJIS_LIMIT=0x38c
SLOT_END=0x3b4  # 0x3b4~0x3ff는 아이콘 글리프

def norm(ch):
    return ASCII.get(ch,ch)

def is_hangul(ch): return '가'<=ch<='힣'

def build(texts_glyph,texts_sjis,extra_keep=(),aux_only=()):
    """texts_glyph: 글리프 인덱스로 인코딩되는 문자열들, texts_sjis: ARM9 SJIS 문자열들."""
    freq=collections.Counter(); sj=collections.Counter(); other=set()
    for t in texts_glyph:
        for ch in t:
            if is_hangul(ch): freq[ch]+=1
            else: other.add(norm(ch))
    for t in texts_sjis:
        for ch in t:
            if is_hangul(ch): sj[ch]+=1; freq[ch]+=1
            else: other.add(norm(ch))
    keep=set(ch for ch in other if ch in TBL)|ALWAYS_KEEP|set(extra_keep)
    missing=sorted(ch for ch in other if ch not in TBL)
    free_low=[i for i,ch in enumerate(TBL[:SJIS_LIMIT]) if ch not in keep]
    free_hi=[i for i in range(SJIS_LIMIT,SLOT_END) if i>=len(TBL) or TBL[i] not in keep]
    # SJIS에 쓰이는 음절 먼저 낮은 슬롯, 나머지는 빈도순
    aux=[c for c in aux_only if c in freq and c not in sj]
    for c in aux: del freq[c]
    order=sorted(sj,key=lambda c:-sj[c])+sorted((c for c in freq if c not in sj),key=lambda c:-freq[c])
    slots=free_low+free_hi
    if len(order)>len(slots):
        raise SystemExit('글리프 부족: 필요 %d, 가능 %d'%(len(order),len(slots)))
    nsj=len(sj)
    if nsj>len(free_low): raise SystemExit('SJIS 슬롯 부족 %d>%d'%(nsj,len(free_low)))
    cmap={c:slots[i] for i,c in enumerate(order)}
    assert len(aux)<=256
    for i,c in enumerate(sorted(aux)): cmap[c]=0x400+i
    for i,ch in enumerate(TBL):
        if ch in keep and ch not in cmap: cmap[ch]=i
    return cmap,{'aux':len(aux),'hangul':len(order),'sjis_hangul':nsj,'slots':len(slots),'missing':missing,'keep':''.join(sorted(keep))}

def encode_glyph(t,cmap):
    out=[]
    for ch in t:
        n=norm(ch)
        if n not in cmap: raise KeyError('문자 없음 %r in %r'%(ch,t))
        out.append(cmap[n])
    return out

def encode_sjis(t,cmap):
    b=b''
    for ch in t:
        n=norm(ch)
        if n not in cmap: raise KeyError('문자 없음 %r in %r'%(ch,t))
        i=cmap[n]
        if i>=SJIS_LIMIT: raise KeyError('SJIS 범위 밖 %r'%ch)
        b+=TBL[i].encode('cp932')
    return b
