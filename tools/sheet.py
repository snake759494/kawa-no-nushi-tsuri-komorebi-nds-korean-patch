import sys
from PIL import Image,ImageDraw
d=open(sys.argv[1],'rb').read()[int(sys.argv[2],0):]
start=int(sys.argv[3],0); cnt=int(sys.argv[4],0); cols=32; S=3
im=Image.new('L',(40+cols*17*S,((cnt+cols-1)//cols)*17*S),255); dr=ImageDraw.Draw(im)
for g in range(cnt):
  gi=start+g
  X=40+(g%cols)*17*S; Y=(g//cols)*17*S
  if g%cols==0: dr.text((0,Y+15),hex(gi),fill=0)
  dr.rectangle((X-1,Y-1,X+16*S,Y+16*S),outline=180)
  for t in range(4):
    for y in range(8):
      for x in range(8):
        o=gi*128+t*32+y*4+x//2
        if o>=len(d): continue
        v=(d[o]>>(4*(x&1)))&15
        if v: dr.rectangle((X+((t&1)*8+x)*S,Y+((t>>1)*8+y)*S,X+((t&1)*8+x)*S+S-1,Y+((t>>1)*8+y)*S+S-1),fill=255-min(v,3)*85)
im.save(sys.argv[5])
