"""저장 상태부터 자동 진행하며 주기적으로 화면·상태를 남긴다. 사용: play.py rom state prefix frames [touch]"""
import sys,os
sys.path.insert(0,'tools')
from desmume.emulator import DeSmuME
from desmume.controls import Keys,keymask
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rom,st,pre,N=os.path.abspath(sys.argv[1]),sys.argv[2],sys.argv[3],int(sys.argv[4])
e=DeSmuME(); e.volume_set(0); e.open(rom); e.savestate.load_file(os.path.join(W,'states',st))
A=keymask(Keys.KEY_A)
for i in range(N):
    if i%24==0: e.input.keypad_add_key(A)
    if i%24==4: e.input.keypad_rm_key(A)
    if len(sys.argv)>5 and i%48==10: e.input.touch_set_pos(128,150)
    if len(sys.argv)>5 and i%48==14: e.input.touch_release()
    e.cycle(with_joystick=False)
    if i%240==0:
        k=i//240
        e.screenshot().save(os.path.join(W,'shots','%s_%03d.png'%(pre,k)))
        e.savestate.save_file(os.path.join(W,'states','%s_%03d.dst'%(pre,k)))
e.destroy()
