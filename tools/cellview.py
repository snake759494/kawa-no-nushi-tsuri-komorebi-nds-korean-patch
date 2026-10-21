import sys,os,struct; sys.path.insert(0,'tools')
import ndspy.rom,rln
from PIL import Image
r=ndspy.rom.NintendoDSRom.fromFile("../Kawa no Nushi Tsuri - Komorebi no Tani, Seseragi no Uta (Japan).nds")
fn,ename=sys.argv[1],sys.argv[2]
d=bytes(r.getFileByName(fn)); d=rln.decode(d) if fn.endswith('.rln') else d
e=[x for x in rln.entries(d) if x['name']==ename and x['type'] in (2,6,1,3,4)][0]
raw=d[e['off']:e['off']+e['size']]
# 16x16 셀(2x2 타일 연속)을 가로 16개로
n=len(raw)//128; cols=16
im=Image.new('L',(cols*17,((n+cols-1)//cols)*17),128)
for g in range(n):
  for t in range(4):
    for y in range(8):
      for x in range(8):
        v=(raw[g*128+t*32+y*4+x//2]>>(4*(x&1)))&15
        im.putpixel(((g%cols)*17+(t&1)*8+x,(g//cols)*17+(t>>1)*8+y),255-v*16)
bb=Image.eval(im,lambda v:255-v).getbbox()
im.resize((im.width*3,im.height*3),0).save(sys.argv[-1])
