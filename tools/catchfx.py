"""낚시 대결 구간을 프레임 단위로 진행하며 효과 시트(o_pow2l/2r) 스프라이트 배치를 수집."""
import sys,os,struct,json
sys.path.insert(0,'tools')
from desmume.emulator import DeSmuME
from desmume.controls import Keys,keymask
import ndspy.rom,rln
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rom=os.path.abspath(sys.argv[1])
r=ndspy.rom.NintendoDSRom.fromFile(rom)
d=rln.decode(bytes(r.getFileByName('battle/battle_icon.rln')))
E={e['name']:d[e['off']:e['off']+e['size']] for e in rln.entries(d) if e['type']==11}
A=keymask(Keys.KEY_A)
BLK={}
for n,raw in E.items():
    for k in range(16):
        b=raw[k*2048:(k+1)*2048]
        if len(set(b))>2: BLK.setdefault(b,(n,k))
frames={}
st=sys.argv[2]; N=int(sys.argv[3]) if len(sys.argv)>3 else 2400
e=DeSmuME(); e.volume_set(0); e.open(rom); e.savestate.load_file(os.path.join(W,'states',st))
for i in range(N):
    if i%24==0: e.input.keypad_add_key(A)
    if i%24==4: e.input.keypad_rm_key(A)
    e.cycle(with_joystick=False)
    M=e.memory.unsigned
    for eng,oam,vr,dcr in (('A',0x07000000,0x06400000,0x04000000),('B',0x07000400,0x06600000,0x04001000)):
        o=bytes(M[oam:oam+1024]); dc=M.read_long(dcr); bnd=32<<((dc>>20)&3)
        sel=[]
        for j in range(128):
            a0,a1,a2=struct.unpack_from('<3H',o,j*8)
            if (a0>>8)&3==2 or (a0&0xff)>=192 or (a0>>14)!=0 or (a1>>14)!=3: continue
            t=a2&0x3ff; blk=bytes(M[vr+t*bnd:vr+t*bnd+2048])
            if blk in BLK: sel.append((a1&0x1ff,a0&0xff,)+BLK[blk]+(a1>>12&1,a1>>13&1))
        if sel:
            key=str(sorted(sel)); frames[key]=dict(eng=eng,spr=sorted(sel))
e.destroy()
json.dump(list(frames.values()),open(os.path.join(W,'dumps','fx_frames.json'),'w'),indent=0)
print(len(frames))
