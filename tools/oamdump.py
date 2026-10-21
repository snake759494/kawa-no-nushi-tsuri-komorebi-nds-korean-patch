"""상태 파일에서 OAM/OBJ VRAM/팔레트/DISPCNT 덤프 → json+bin."""
import sys,os,json,struct
from desmume.emulator import DeSmuME
rom,st,out=os.path.abspath(sys.argv[1]),sys.argv[2],sys.argv[3]
e=DeSmuME(); e.volume_set(0); e.open(rom); e.savestate.load_file(st)
for _ in range(3): e.cycle(with_joystick=False)
M=e.memory.unsigned
res={}
for eng,oam,vram,pal,dc in [('A',0x07000000,0x06400000,0x05000200,0x04000000),('B',0x07000400,0x06600000,0x05000600,0x04001000)]:
    o=bytes(M[oam:oam+1024]); v=bytes(M[vram:vram+0x20000]); p=bytes(M[pal:pal+512])
    dispcnt=M.read_long(dc)
    open(out+'_%s_vram.bin'%eng,'wb').write(v); open(out+'_%s_pal.bin'%eng,'wb').write(p)
    sprites=[]
    for i in range(128):
        a0,a1,a2=struct.unpack_from('<3H',o,i*8)
        if (a0>>8)&3==2: continue  # 숨김
        shape=a0>>14; size=a1>>14; y=a0&0xff; x=a1&0x1ff
        sprites.append(dict(i=i,x=x,y=y,shape=shape,size=size,tile=a2&0x3ff,pal=a2>>12,bpp8=(a0>>13)&1,hf=(a1>>12)&1,vf=(a1>>13)&1,aff=(a0>>8)&1))
    res[eng]=dict(dispcnt=dispcnt,sprites=sprites)
json.dump(res,open(out+'.json','w'),indent=0)
e.destroy()
