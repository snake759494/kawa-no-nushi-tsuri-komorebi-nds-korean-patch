"""창 없는 DeSmuME 서버. POST /cmd json 배열. 종료: /close"""
import sys,os,json,struct
from http.server import HTTPServer,BaseHTTPRequestHandler
from desmume.emulator import DeSmuME
from desmume.controls import Keys,keymask
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rom=os.path.abspath(sys.argv[1]); port=int(sys.argv[2])
os.makedirs(os.path.join(W,'shots'),exist_ok=True); os.makedirs(os.path.join(W,'states'),exist_ok=True)
e=DeSmuME(); e.volume_set(0); e.open(rom)
def fr(n):
    for _ in range(n): e.cycle(with_joystick=False)
def oamdump(out):
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
def act(a):
    if a.get('reset'): e.reset()
    if 'load' in a: e.savestate.load_file(os.path.join(W,'states',a['load']))
    m=0
    for k in a.get('keys','').split('+'):
        if k: m|=keymask(getattr(Keys,'KEY_'+k.upper()))
    for _ in range(a.get('rep',1)):
        if m: e.input.keypad_add_key(m)
        if 'touch' in a: e.input.touch_set_pos(*a['touch'])
        fr(a.get('hold',4 if (m or 'touch' in a) else 0))
        if m: e.input.keypad_rm_key(m)
        if 'touch' in a: e.input.touch_release()
        fr(a.get('wait',30))
    if 'shot' in a: e.screenshot().save(os.path.join(W,'shots',a['shot']+'.png'))
    if 'save' in a: e.savestate.save_file(os.path.join(W,'states',a['save']))
    if 'oam' in a: oamdump(os.path.join(W,'dumps',a['oam']))
class H(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def do_POST(self):
        try:
            if self.path=='/close':
                self.send_response(200);self.end_headers();self.wfile.write(b'bye')
                e.destroy(); os._exit(0)
            body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            for a in body: act(a)
            self.send_response(200);self.end_headers();self.wfile.write(b'ok')
        except Exception as ex:
            self.send_response(500);self.end_headers();self.wfile.write(repr(ex).encode())
os.makedirs(os.path.join(W,'dumps'),exist_ok=True)
print('ready',flush=True)
HTTPServer(('127.0.0.1',port),H).serve_forever()
