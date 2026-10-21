import json,struct
def dump(e,out):
    M=e.memory.unsigned; res={}
    for eng,oam,vram,pal,dc in [('A',0x07000000,0x06400000,0x05000200,0x04000000),('B',0x07000400,0x06600000,0x05000600,0x04001000)]:
        o=bytes(M[oam:oam+1024]); open(out+'_%s_vram.bin'%eng,'wb').write(bytes(M[vram:vram+0x20000]))
        open(out+'_%s_pal.bin'%eng,'wb').write(bytes(M[pal:pal+512]))
        sp=[]
        for i in range(128):
            a0,a1,a2=struct.unpack_from('<3H',o,i*8)
            if (a0>>8)&3==2: continue
            sp.append(dict(i=i,x=a1&0x1ff,y=a0&0xff,shape=a0>>14,size=a1>>14,tile=a2&0x3ff,pal=a2>>12,bpp8=(a0>>13)&1))
        res[eng]=dict(dispcnt=M.read_long(dc),sprites=sp)
    # BG 레지스터와 VRAM
    bg={}
    for eng,base,vr in [('A',0x04000000,0x06000000),('B',0x04001000,0x06200000)]:
        bg[eng]=dict(dispcnt=M.read_long(base),bgcnt=[M.read_short(base+8+2*i) for i in range(4)])
        open(out+'_%s_bgvram.bin'%eng,'wb').write(bytes(M[vr:vr+0x80000 if eng=='A' else vr+0x20000]))
        open(out+'_%s_bgpal.bin'%eng,'wb').write(bytes(M[0x05000000+(0 if eng=='A' else 0x400):0x05000000+(0x200 if eng=='A' else 0x600)]))
    res['bg']=bg
    json.dump(res,open(out+'.json','w'))
