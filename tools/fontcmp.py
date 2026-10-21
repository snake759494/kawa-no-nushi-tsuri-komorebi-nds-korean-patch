from PIL import Image,ImageFont,ImageDraw
import sys
sys.path.insert(0,'tools')
d=open('ext/common.arc','rb').read()
def orig(i):
  o=0x2064+i*128; im=Image.new('L',(16,16),255)
  for t in range(4):
    for y in range(8):
      for x in range(8):
        v=(d[o+t*32+y*4+x//2]>>(4*(x&1)))&15
        im.putpixel(((t&1)*8+x,(t>>1)*8+y),[255,0,110,190][v] if v<4 else 128)
  return im
txt='川のぬし釣りこもれびの谷'
def ttf(path,size,s,dy=0):
  f=ImageFont.truetype(path,size); out=[]
  for ch in s:
    im=Image.new('L',(16,16),255); dr=ImageDraw.Draw(im); dr.text((0,dy),ch,font=f,fill=0); 
    q=im.point(lambda v:0 if v<64 else 110 if v<128 else 190 if v<200 else 255)
    out.append(q)
  return out
from PIL import BdfFontFile
import io
def bdf(path,s):
  # 간이 BDF 렌더
  g={};cur=None;bm=[];inb=False
  for line in open(path,encoding='utf8',errors='ignore'):
    p=line.split()
    if not p: continue
    if p[0]=='ENCODING': cur=int(p[1])
    elif p[0]=='BBX': bbx=list(map(int,p[1:]))
    elif p[0]=='BITMAP': inb=True; bm=[]
    elif p[0]=='ENDCHAR': inb=False; g[cur]=(bbx,bm)
    elif inb: bm.append(int(p[0],16))
  out=[]
  for ch in s:
    im=Image.new('L',(16,16),255)
    if ord(ch) in g:
      (w,h,ox,oy),bm=g[ord(ch)]; nb=(w+7)//8*8
      for y,row in enumerate(bm):
        for x in range(w):
          if row>>(nb-1-x)&1: im.putpixel((x+ox,y+(11-h-oy)),0)
    out.append(im)
  return out
rows=[('orig',[orig(i) for i in range(0,20)])]
k='강의 낚시꾼 숲속 골짜기 시냇물 노래'
F='../'
rows.append(('galmuri11',bdf('fonts/Galmuri11.bdf',k)))
for name,fn,sz,dy in [('NSN-bRg12','NanumSquareNeo-bRg.ttf',12,-1),('NSN-cBd12','NanumSquareNeo-cBd.ttf',12,-1),('NSN-bRg11','NanumSquareNeo-bRg.ttf',11,0),('SH-M12','SeoulHangangM.ttf',12,-2),('SH-B12','SeoulHangangB.ttf',12,-2)]:
  rows.append((name,ttf(F+fn,sz,k,dy)))
S=4
out=Image.new('L',(80+20*17*S,len(rows)*17*S),255); dr=ImageDraw.Draw(out)
for r,(n,gl) in enumerate(rows):
  dr.text((0,r*17*S+20),n,fill=0)
  for i,g in enumerate(gl): out.paste(g.resize((16*S,16*S),0),(80+i*17*S,r*17*S))
out.save('fontcmp.png')
