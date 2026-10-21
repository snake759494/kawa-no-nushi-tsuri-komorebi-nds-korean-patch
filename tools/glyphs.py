import sys
from PIL import Image
d=open(sys.argv[1],'rb').read()[int(sys.argv[2],0):]
cnt=int(sys.argv[3],0); per=int(sys.argv[4]) if len(sys.argv)>5 else 32
cols=32
im=Image.new('L',(cols*17,((cnt+cols-1)//cols)*17),128)
for g in range(cnt):
  for t in range(4):
    for y in range(8):
      for x in range(8):
        o=g*128+t*32+y*4+x//2
        if o>=len(d): continue
        v=(d[o]>>(4*(x&1)))&15
        im.putpixel(((g%cols)*17+(t&1)*8+x,(g//cols)*17+(t>>1)*8+y),255-min(v,3)*85)
im.resize((im.width*2,im.height*2),0).save(sys.argv[-1])
