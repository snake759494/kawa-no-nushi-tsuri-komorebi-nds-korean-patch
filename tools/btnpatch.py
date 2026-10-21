"""OAM 기준 덤프의 '한 묶음 스프라이트'(막대/버튼) 배치를 빌려 같은 시트의 다른 묶음을 재구성·패치."""
import os,json,copy
import rln
from objcomp import compose
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Ref:
    def __init__(self,prefix,eng,sel):
        self.prefix=prefix; self.eng=eng
        self.d=json.load(open(os.path.join(W,prefix+'.json')))
        self.v=open(os.path.join(W,prefix+'_%s_vram.bin'%eng),'rb').read()
        dc=self.d[eng]['dispcnt']; self.bnd=32<<((dc>>20)&3)
        self.sp=sorted([s for s in self.d[eng]['sprites'] if sel(s)],key=lambda s:(s['y'],s['x']))
        t0=self.sp[0]['tile']; self.rel=[(s['tile']-t0)*self.bnd for s in self.sp]
        self.size=self.rel[-1]+512
        self.blk=self.v[t0*self.bnd:t0*self.bnd+self.size]
    def find(self,raw):
        keys=[(k,self.blk[k:k+32]) for k in (0,128,self.size-512+96,self.size-512+224)]
        res=[]
        for o in range(0,len(raw)-self.size+1,128):
            if all(raw[o+k:o+k+32]==t for k,t in keys):
                if not res or o-res[-1]>=self.size: res.append(o)
        return res
    def layout(self,raw,off,base=0x8000):
        vv=bytearray(len(self.v)); vv[base:base+len(raw)]=raw
        sp=[]
        for s,r in zip(self.sp,self.rel):
            s=dict(s); s['tile']=(base+off+r)//self.bnd; sp.append(s)
        dd=copy.deepcopy(self.d); dd[self.eng]['sprites']=sp
        tmp=os.path.join(W,'dumps','_btn')
        json.dump(dd,open(tmp+'.json','w')); open(tmp+'_%s_vram.bin'%self.eng,'wb').write(bytes(vv))
        open(tmp+'_%s_pal.bin'%self.eng,'wb').write(open(os.path.join(W,self.prefix+'_%s_pal.bin'%self.eng),'rb').read())
        img,loc=compose(tmp,self.eng)
        return img,loc,bytes(vv),base

def patch(rom,fn,en,ref,texts,box,size=12,etype=6,offsets=None):
    import scrpatch
    d=bytes(rom.getFileByName(fn)); comp=fn.endswith('.rln')
    if comp: d=rln.decode(d)
    d=bytearray(d)
    e=[x for x in rln.entries(bytes(d)) if x['name']==en and x['type']==etype][0]
    raw=bytearray(d[e['off']:e['off']+e['size']]); orig=bytes(raw)
    groups=offsets if offsets is not None else ref.find(orig)
    for off,text in zip(groups,texts):
        if text is None: continue
        img,loc,vv,base=ref.layout(orig,off)
        out=scrpatch.render_items(loc,vv,[{'box':list(box),'text':text,'size':size,'center':True}],(1,9,12),1,9,12,'NanumSquareNeo-eHv.ttf',True)
        for (X,Y),val in out.items():
            b,h=loc[(X,Y)]; o=b-base
            if off<=o<off+ref.size: raw[o]=(raw[o]&~(15<<(4*h)))|(val<<(4*h))
    d[e['off']:e['off']+e['size']]=raw
    rom.setFileByName(fn,rln.encode(bytes(d)) if comp else bytes(d))
    return groups
