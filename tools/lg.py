import sys
from PIL import Image
d=open(sys.argv[1],'rb').read()[int(sys.argv[2],0):]
cnt=int(sys.argv[3],0); W=int(sys.argv[4]); H=int(sys.argv[5]); sz=W*H//2
cols=32
im=Image.new('L',(cols*(W+1),((cnt+cols-1)//cols)*(H+1)),128)
for g in range(cnt):
  for y in range(H):
    for x in range(W):
      o=g*sz+(y*W+x)//2
      if o>=len(d): continue
      v=(d[o]>>(4*(x&1)))&15
      im.putpixel(((g%cols)*(W+1)+x,(g//cols)*(H+1)+y),255-min(v,3)*85)
im.resize((im.width*2,im.height*2),0).save(sys.argv[6])
