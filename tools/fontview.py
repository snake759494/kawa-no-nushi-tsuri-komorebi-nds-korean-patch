import sys
from PIL import Image
d=open(sys.argv[1],'rb').read()[int(sys.argv[2],0):]
tw=int(sys.argv[3]) # tiles per row
n=len(d)//32
rows=(n+tw-1)//tw
im=Image.new('L',(tw*8,rows*8))
for t in range(n):
  for y in range(8):
    for x in range(8):
      b=d[t*32+y*4+x//2]; v=(b>>(4*(x&1)))&15
      im.putpixel(((t%tw)*8+x,(t//tw)*8+y),255-v*60 if v<5 else 0)
im=im.resize((im.width*2,im.height*2),0); im.save(sys.argv[4])
