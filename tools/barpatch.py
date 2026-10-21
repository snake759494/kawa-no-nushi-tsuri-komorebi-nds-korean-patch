"""타이틀 메뉴 막대(pt_10_1t)의 OAM 배치를 빌려 같은 구조의 막대 시트(pt_10_2t/3t 등)를 재구성·패치."""
import os,json,struct,copy
import rln,gfxtext
from objcomp import compose
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF='oam_title'
BND=128   # 원본 ROM 타이틀 화면 덤프(엔진 B)

def _ref():
    d=json.load(open(os.path.join(W,REF+'.json')))
    v=open(os.path.join(W,REF+'_B_vram.bin'),'rb').read()
    bar=[s for s in d['B']['sprites'] if s['y']==64 and s['size']==2]
    bar.sort(key=lambda s:s['x'])
    return d,v,bar

def find_bars(raw,ref_raw):
    """타이틀 막대(ref 항목 오프셋 0)의 왼쪽·오른쪽 끝 프레임 타일로 막대 시작 탐색."""
    keys=[(k,ref_raw[k:k+32]) for k in (0,128,6*512+96,6*512+224)]
    res=[]
    for o in range(0,len(raw)-3584+1,128):
        if all(raw[o+k:o+k+32]==t for k,t in keys):
            if not res or o-res[-1]>=3584: res.append(o)
    return res

def layout(raw,bar_off,base_unit_off):
    """bar_off(항목 내 바이트)에 있는 막대를 타이틀 막대 위치에 합성 → (이미지, loc)."""
    d,v,bar=_ref()
    vv=bytearray(v); base=base_unit_off
    vv[base:base+len(raw)]=raw
    sp=[]
    for i,s in enumerate(bar):
        s=dict(s); s['tile']=(base+bar_off)//BND+i*(512//BND); sp.append(s)
    dd=copy.deepcopy(d); dd['B']['sprites']=sp
    tmp=os.path.join(W,'dumps','_bar')
    json.dump(dd,open(tmp+'.json','w')); open(tmp+'_B_vram.bin','wb').write(bytes(vv))
    open(tmp+'_B_pal.bin','wb').write(open(os.path.join(W,REF+'_B_pal.bin'),'rb').read())
    return compose(tmp,'B')

def entry_base(raw):
    """타이틀 덤프 VRAM에서 pt_10_1t가 놓인 위치(바이트)."""
    _,v,_=_ref()
    for k in range(0,len(raw)-256,32):
        c=raw[k:k+256]
        if len(set(c))>6:
            j=v.find(c)
            if j>=0: return j-k

BAR_TEXTS={
 ('map/pt_10.rln','pt_10_1t'):['처음부터','이어서 하기','Wi-Fi 설정','낚시 대회 열기','낚시 대회 참가','친구 코드','낚시 대회 안내','이름 변경'],
 ('map/pt_10.rln','pt_10_2t'):['DS 무선 통신','Wi-Fi 통신','친구 코드 등록','친구 코드 확인','랜덤','친구와','네','아니요'],
 ('map/pt_10.rln','pt_10_3t'):['낚시 대회','누구와도','돌아가기','그만두기','이제 됐어요','받기','설명 한 번 더 듣기','친구 리스트'],
 ('map/title0.arc','tit_obj'):['처음부터','이어서 하기','Wi-Fi 설정','낚시 대회 열기'],
}
def patch_all(rom):
    import scrpatch
    d0=rln.decode(bytes(rom.getFileByName('map/pt_10.rln')))
    ref=[d0[e['off']:e['off']+e['size']] for e in rln.entries(d0) if e['name']=='pt_10_1t'][0]
    base=0x8f00
    for (fn,en),texts in BAR_TEXTS.items():
        d=bytes(rom.getFileByName(fn)); comp=fn.endswith('.rln')
        if comp: d=rln.decode(d)
        d=bytearray(d)
        e=[x for x in rln.entries(bytes(d)) if x['name']==en and x['type']==6][0]
        raw=bytearray(d[e['off']:e['off']+e['size']]); orig=bytes(raw)
        bars=find_bars(orig,ref)
        for off,text in zip(bars,texts):
            img,loc=layout(orig,off,base)
            vv=open(os.path.join(W,'dumps','_bar_B_vram.bin'),'rb').read()
            out=scrpatch.render_items(loc,vv,[{'box':[22,67,228,84],'text':text,'size':12}],(1,9,12),1,9,12,'NanumSquareNeo-eHv.ttf',False)
            for (X,Y),val in out.items():
                b,h=loc[(X,Y)]; o=b-base
                if off<=o<off+3584: raw[o]=(raw[o]&~(15<<(4*h)))|(val<<(4*h))
        d[e['off']:e['off']+e['size']]=raw
        rom.setFileByName(fn,rln.encode(bytes(d)) if comp else bytes(d))
